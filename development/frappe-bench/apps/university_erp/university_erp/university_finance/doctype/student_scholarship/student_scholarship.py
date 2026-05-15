# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

"""Student Scholarship controller — wires the Approved / Disbursed workflow
states to the student's Fees doc + portal Fees & Payments view.

Workflow states (verified on prod):
    Draft → Under Verification → Approved → Disbursed
                              ↘ Rejected
                                Cancelled

Side effects per state:
    Approved   — write `Fees.custom_scholarship_amount = discount_amount`,
                 set `Fees.custom_net_amount = grand_total - scholarship`.
                 Outstanding stays untouched — this is a *pending* credit.
    Disbursed  — create a submitted Payment Entry (Receive) referencing the
                 Fees doc; the standard Frappe Education hook reduces
                 `Fees.outstanding_amount` automatically. Idempotent.
    Cancelled  — reverse: cancel the linked Payment Entry, clear the scholarship
                 amount on the Fees doc.

Patterns reused:
    - `fee_refund.py:create_payment_entry` for account resolution
    - `record_offline_payment` for the Payment Entry shape (with references)
    - `student_applicant.py:on_update` idempotency pattern
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class StudentScholarship(Document):
    # Map workflow_state to the doctype's `status` Select so reports/portal that
    # key off `status` keep working without schema change.
    WORKFLOW_TO_STATUS = {
        "Draft": "Active",
        "Under Verification": "Active",
        "Approved": "Active",
        "Disbursed": "Active",
        "Rejected": "Cancelled",
        "Cancelled": "Cancelled",
    }

    def validate(self):
        self.sync_status_with_workflow()
        self.compute_discount_amount()
        self.default_validity_dates()

    def sync_status_with_workflow(self):
        ws = getattr(self, "workflow_state", None)
        target = self.WORKFLOW_TO_STATUS.get(ws)
        if target and self.status != target:
            self.status = target

    def compute_discount_amount(self):
        """If percentage is set but absolute amount isn't, derive ₹ from the
        student's most-recent Fees row. Cap at max_benefit_amount."""
        if flt(self.discount_amount) > 0:
            # Already explicit — only enforce the cap.
            if flt(self.max_benefit_amount) and flt(self.discount_amount) > flt(self.max_benefit_amount):
                self.discount_amount = self.max_benefit_amount
            return

        if flt(self.discount_percentage) <= 0:
            return

        target_fees = self._target_fees_name()
        if not target_fees:
            return  # nothing to derive against; demo seed sets discount_amount explicitly

        grand_total = flt(frappe.db.get_value("Fees", target_fees, "grand_total"))
        derived = grand_total * flt(self.discount_percentage) / 100.0
        if flt(self.max_benefit_amount):
            derived = min(derived, flt(self.max_benefit_amount))
        self.discount_amount = round(derived, 2)

    def default_validity_dates(self):
        if not self.valid_from:
            self.valid_from = nowdate()
        if not self.valid_till:
            today = getdate(nowdate())
            # 31-March of the next year if today is past March, else this year
            year = today.year + 1 if today.month >= 4 else today.year
            self.valid_till = getdate(f"{year}-03-31")

    # ------------------------------------------------------------------
    # Fees-doc linkage
    # ------------------------------------------------------------------

    def _target_fees_name(self):
        """Pick the Fees row this scholarship credits.

        Strategy:
        1. Most recent submitted Fees for this student where
           custom_scholarship_amount is 0 — so we don't double-apply.
        2. Else, the most recent submitted Fees regardless.
        """
        candidate = frappe.db.sql("""
            SELECT name FROM `tabFees`
            WHERE student = %s AND docstatus = 1
              AND COALESCE(custom_scholarship_amount, 0) = 0
            ORDER BY posting_date DESC, creation DESC
            LIMIT 1
        """, self.student)
        if candidate:
            return candidate[0][0]
        candidate = frappe.db.sql("""
            SELECT name FROM `tabFees`
            WHERE student = %s AND docstatus = 1
            ORDER BY posting_date DESC, creation DESC
            LIMIT 1
        """, self.student)
        return candidate[0][0] if candidate else None

    # ------------------------------------------------------------------
    # Workflow-driven side effects
    # ------------------------------------------------------------------

    def on_update(self):
        self._dispatch_workflow_side_effects()

    def on_update_after_submit(self):
        # Fires when a submitted doc's workflow_state moves between
        # docstatus=1 states (Approved → Disbursed). on_update doesn't always
        # run in that path because Frappe uses db_set under the hood.
        self._dispatch_workflow_side_effects()

    def _dispatch_workflow_side_effects(self):
        ws = getattr(self, "workflow_state", None)
        if ws == "Approved":
            self._apply_pending_credit()
        elif ws == "Disbursed":
            self._disburse()
        elif ws in ("Cancelled", "Rejected"):
            self._reverse()

    def _apply_pending_credit(self):
        """Mark the scholarship as a pending credit on the Fees doc.
        Display-only — does NOT reduce outstanding_amount yet.
        Idempotent."""
        fees_name = self._target_fees_name()
        if not fees_name:
            return  # No fees yet; will apply on next save when one exists

        existing = flt(frappe.db.get_value("Fees", fees_name, "custom_scholarship_amount"))
        if existing >= flt(self.discount_amount):
            return  # already applied, idempotent

        grand_total = flt(frappe.db.get_value("Fees", fees_name, "grand_total"))
        scholarship = flt(self.discount_amount)
        net = max(grand_total - scholarship, 0)

        frappe.db.set_value("Fees", fees_name, {
            "custom_scholarship_amount": scholarship,
            "custom_net_amount": net,
        }, update_modified=False)

    def _disburse(self):
        """Create a submitted Payment Entry that actually moves the money.
        Idempotent via `total_benefit_given`."""
        if flt(self.total_benefit_given) >= flt(self.discount_amount) > 0:
            return  # already disbursed

        fees_name = self._target_fees_name()
        if not fees_name:
            frappe.log_error(
                title=f"Scholarship {self.name} — no Fees to disburse against",
                message=f"Student {self.student} has no submitted Fees row.",
            )
            return

        # Make sure Fees outstanding > 0 so we don't allocate against zero
        outstanding = flt(frappe.db.get_value("Fees", fees_name, "outstanding_amount"))
        if outstanding <= 0:
            # Refresh: in case someone overpaid earlier, scholarship still tracks it on paper
            frappe.db.set_value("Student Scholarship", self.name, "total_benefit_given",
                                self.discount_amount, update_modified=False)
            return

        amount_to_apply = min(flt(self.discount_amount), outstanding)
        company, cash_account, receivable = self._resolve_accounts()
        if not (company and cash_account and receivable):
            frappe.log_error(
                title=f"Scholarship {self.name} — accounts not configured",
                message="University Accounts Settings missing fee_collection_account / receivable account.",
            )
            return

        student_name = frappe.db.get_value("Student", self.student, "student_name") or self.student

        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "posting_date": nowdate(),
            "company": company,
            "party_type": "Student",
            "party": self.student,
            "party_name": student_name,
            "paid_from": receivable,
            "paid_to": cash_account,
            "paid_amount": amount_to_apply,
            "received_amount": amount_to_apply,
            "source_exchange_rate": 1,
            "target_exchange_rate": 1,
            "mode_of_payment": self._pick_mode_of_payment(),
            "reference_no": self.name,
            "reference_date": nowdate(),
            "remarks": (
                f"Scholarship Credit — {self.scholarship_type or 'Scholarship'} "
                f"({self.name}) applied to fee {fees_name}"
            ),
            "references": [{
                "reference_doctype": "Fees",
                "reference_name": fees_name,
                "total_amount": flt(frappe.db.get_value("Fees", fees_name, "grand_total")),
                "outstanding_amount": outstanding,
                "allocated_amount": amount_to_apply,
            }],
        })
        pe.flags.ignore_permissions = True
        pe.flags.ignore_mandatory = True
        pe.insert(ignore_permissions=True)
        try:
            pe.submit()
        except Exception as e:
            frappe.log_error(message=str(e), title=f"Scholarship PE submit failed for {self.name}")
            return

        # Manually decrement outstanding (Education app's hook can be flaky on edited PEs)
        new_outstanding = max(outstanding - amount_to_apply, 0)
        frappe.db.set_value("Fees", fees_name, "outstanding_amount", new_outstanding,
                            update_modified=False)

        # Bookkeeping on the scholarship row
        frappe.db.set_value("Student Scholarship", self.name, {
            "total_benefit_given": amount_to_apply,
        }, update_modified=False)

        frappe.msgprint(
            _("Scholarship disbursed: ₹{0} credited to {1} via Payment Entry {2}").format(
                amount_to_apply, fees_name, pe.name
            ),
            indicator="green", alert=True,
        )

    def _reverse(self):
        """Reverse the side effects on Cancel / Reject."""
        fees_name = self._target_fees_name()
        if fees_name:
            # Clear pending credit
            frappe.db.set_value("Fees", fees_name, {
                "custom_scholarship_amount": 0,
                "custom_net_amount": frappe.db.get_value("Fees", fees_name, "grand_total"),
            }, update_modified=False)

        # Cancel the disbursement PE if it exists
        if self.total_benefit_given:
            pes = frappe.db.sql("""
                SELECT name FROM `tabPayment Entry`
                WHERE reference_no = %s AND docstatus = 1
            """, self.name)
            for (pe_name,) in pes:
                try:
                    pe = frappe.get_doc("Payment Entry", pe_name)
                    pe.cancel()
                except Exception as e:
                    frappe.log_error(message=str(e), title=f"Scholarship PE cancel failed for {pe_name}")
            frappe.db.set_value("Student Scholarship", self.name, "total_benefit_given", 0,
                                update_modified=False)

    def on_cancel(self):
        self._reverse()

    # ------------------------------------------------------------------
    # Account / mode-of-payment helpers (mirror of fee_refund.py)
    # ------------------------------------------------------------------

    def _resolve_accounts(self):
        """Return (company, cash_account, receivable_account) — falling back
        gracefully if University Accounts Settings isn't fully configured."""
        company = None
        cash_account = None
        try:
            settings = frappe.get_single("University Accounts Settings")
            company = settings.company
            cash_account = settings.fee_collection_account
        except Exception:
            pass

        if not company:
            company = frappe.db.get_value("Company", {}, "name")
        if not company:
            return None, None, None

        if not cash_account:
            cash_account = (
                frappe.db.get_value("Account",
                    {"company": company, "account_type": "Cash", "is_group": 0}, "name")
                or frappe.db.get_value("Account",
                    {"company": company, "account_type": "Bank", "is_group": 0}, "name")
            )

        receivable = frappe.db.get_value(
            "Account",
            {"company": company, "account_type": "Receivable", "is_group": 0},
            "name",
        )
        return company, cash_account, receivable

    def _pick_mode_of_payment(self):
        for c in ("Bank Transfer", "Cash", "UPI"):
            if frappe.db.exists("Mode of Payment", c):
                return c
        return frappe.db.get_value("Mode of Payment", {}, "name") or "Cash"
