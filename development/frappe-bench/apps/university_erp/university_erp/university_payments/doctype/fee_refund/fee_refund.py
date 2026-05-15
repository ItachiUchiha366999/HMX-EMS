# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class FeeRefund(Document):
    # Map the workflow_state Frappe sets during transitions onto the doctype's
    # `status` Select field so the two stay in lock-step. Without this the
    # `before_submit` guard ("Only Approved refunds can be submitted") fails on
    # the Process Refund transition because status was left at its initial value.
    WORKFLOW_TO_STATUS = {
        "Pending": "Draft",
        "Pending Approval": "Pending Approval",
        "Approved": "Approved",
        "Processed": "Processed",
        "Rejected": "Rejected",
        "Cancelled": "Cancelled",
    }

    def validate(self):
        self.sync_status_with_workflow()
        self.validate_refund_amount()
        self.calculate_net_refund()

    def sync_status_with_workflow(self):
        """Keep `status` aligned with `workflow_state` on every save."""
        ws = getattr(self, "workflow_state", None)
        target = self.WORKFLOW_TO_STATUS.get(ws)
        if target and self.status != target:
            self.status = target

    def validate_refund_amount(self):
        """Validate refund amount against paid amount.

        The Education app's `Fees` doctype doesn't have a `paid_amount` column;
        it stores `grand_total` and `outstanding_amount` and the paid amount is
        derived. Compute it explicitly here.
        """
        if not self.fees:
            return  # nothing to validate against
        fees = frappe.db.get_value(
            "Fees", self.fees, ["grand_total", "outstanding_amount"], as_dict=True,
        ) or {}
        paid_amount = flt(fees.get("grand_total")) - flt(fees.get("outstanding_amount"))

        if flt(self.refund_amount) > paid_amount:
            frappe.throw(_("Refund amount cannot exceed paid amount of {0}").format(
                frappe.format_value(paid_amount, {"fieldtype": "Currency"})
            ))

        if flt(self.refund_amount) <= 0:
            frappe.throw(_("Refund amount must be greater than zero"))

        # Check for existing refunds against the same Fees row
        existing_refunds = frappe.db.sql("""
            SELECT SUM(net_refund) as total_refunded
            FROM `tabFee Refund`
            WHERE fees = %s AND docstatus = 1 AND name != %s
        """, (self.fees, self.name), as_dict=True)

        total_refunded = flt(existing_refunds[0].total_refunded) if existing_refunds else 0

        if (total_refunded + flt(self.refund_amount)) > paid_amount:
            frappe.throw(_(
                "Total refund amount ({0}) cannot exceed paid amount ({1}). Already refunded: {2}"
            ).format(
                frappe.format_value(total_refunded + flt(self.refund_amount), {"fieldtype": "Currency"}),
                frappe.format_value(paid_amount, {"fieldtype": "Currency"}),
                frappe.format_value(total_refunded, {"fieldtype": "Currency"})
            ))

    def calculate_net_refund(self):
        """Calculate net refund after deductions"""
        self.net_refund = flt(self.refund_amount) - flt(self.deduction_amount)
        if self.net_refund < 0:
            frappe.throw(_("Net refund cannot be negative"))

    def before_submit(self):
        """Validate before submission"""
        if self.status not in ["Approved", "Processed"]:
            frappe.throw(_("Only Approved refunds can be submitted"))

    def on_submit(self):
        """Create the refund Payment Entry on submit.

        The doctype's `status` is sync'd from `workflow_state` in `validate`, so
        by the time `on_submit` fires the status has already moved past 'Approved'
        to 'Processed'. We accept either as the trigger so the refund Payment
        Entry actually gets created.
        """
        if self.status in ("Approved", "Processed") and not self.payment_entry:
            self.create_payment_entry()
            self.update_fees_status()

    def on_cancel(self):
        """Handle cancellation"""
        if self.payment_entry:
            pe = frappe.get_doc("Payment Entry", self.payment_entry)
            if pe.docstatus == 1:
                pe.cancel()

    def create_payment_entry(self):
        """Create the refund Payment Entry (Pay type, party=Student) so it
        shows on the student's portal Payment History and reduces the Fees
        outstanding back upward.

        Resolution order for accounts:
        1. `University Accounts Settings.fee_collection_account` if configured
        2. Otherwise pick a reasonable Cash / Bank account for the company
        3. Otherwise throw with a useful message
        """
        try:
            settings = frappe.get_single("University Accounts Settings")
            company = settings.company
            cash_account = settings.fee_collection_account
        except Exception:
            settings = None
            company = None
            cash_account = None

        if not company:
            company = frappe.db.get_value("Company", {}, "name")
        if not company:
            frappe.throw(_("No Company configured — cannot create refund Payment Entry"))

        if not cash_account:
            cash_account = (
                frappe.db.get_value("Account",
                    {"company": company, "account_type": "Cash", "is_group": 0}, "name")
                or frappe.db.get_value("Account",
                    {"company": company, "account_type": "Bank", "is_group": 0}, "name")
            )
        if not cash_account:
            frappe.throw(_("No Cash/Bank account found for company {0}").format(company))

        # paid_from is the asset account (cash) that's being depleted.
        # paid_to is the party receivable account (reduces what the student is owed).
        receivable = frappe.db.get_value(
            "Account",
            {"company": company, "account_type": "Receivable", "is_group": 0},
            "name",
        )
        if not receivable:
            frappe.throw(_("No Receivable account found for company {0}").format(company))

        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "posting_date": self.refund_date,
            "company": company,
            "party_type": "Student",
            "party": self.student,
            "party_name": self.student_name,
            "paid_from": cash_account,
            "paid_to": receivable,
            "paid_amount": self.net_refund,
            "received_amount": self.net_refund,
            "source_exchange_rate": 1,
            "target_exchange_rate": 1,
            "mode_of_payment": self.get_mode_of_payment(),
            "reference_no": self.name,
            "reference_date": self.refund_date,
            "remarks": f"Fee refund {self.name} — {self.refund_reason} — fee {self.fees}",
            "references": [{
                "reference_doctype": "Fees",
                "reference_name": self.fees,
                "total_amount": self.net_refund,
                "outstanding_amount": 0,
                "allocated_amount": self.net_refund,
            }],
        })

        if self.payment_mode == "Bank Transfer" and self.bank_account:
            payment_entry.remarks += (
                f"\nBank: {self.bank_name}, A/C: {self.bank_account}, IFSC: {self.ifsc_code}"
            )

        payment_entry.flags.ignore_permissions = True
        payment_entry.flags.ignore_mandatory = True
        payment_entry.insert(ignore_permissions=True)
        try:
            payment_entry.submit()
        except Exception as e:
            frappe.log_error(message=str(e), title=f"Refund PE submit failed for {self.name}")

        self.db_set("payment_entry", payment_entry.name, update_modified=False)
        self.db_set("processed_date", frappe.utils.today(), update_modified=False)

    def get_mode_of_payment(self):
        """Map the Fee Refund's payment_mode to a Mode of Payment master that
        actually exists on this site. Falls back to any available mode if the
        first choice is missing.
        """
        candidates = {
            "Bank Transfer": ["Bank Transfer", "Bank Draft", "Wire Transfer"],
            "Cheque": ["Cheque"],
            "Cash": ["Cash"],
            "Online Refund": ["UPI", "Credit Card", "Bank Transfer"],
            "UPI": ["UPI"],
        }.get(self.payment_mode, ["Cash"])
        for c in candidates:
            if frappe.db.exists("Mode of Payment", c):
                return c
        # last resort — any active Mode of Payment on the site
        any_mop = frappe.db.get_value("Mode of Payment", {"enabled": 1}, "name") \
            or frappe.db.get_value("Mode of Payment", {}, "name")
        return any_mop or "Cash"

    def update_fees_status(self):
        """If the cumulative refunds equal or exceed the paid portion of the
        Fees doc, mark the Fees status as 'Refunded'. Education app's Fees has
        no `paid_amount` column, so derive from grand_total - outstanding_amount.
        """
        fees = frappe.db.get_value(
            "Fees", self.fees,
            ["grand_total", "outstanding_amount"], as_dict=True,
        ) or {}
        paid_amount = flt(fees.get("grand_total")) - flt(fees.get("outstanding_amount"))

        total_refunded = frappe.db.sql("""
            SELECT SUM(net_refund) as total
            FROM `tabFee Refund`
            WHERE fees = %s AND docstatus = 1
        """, self.fees, as_dict=True)[0].total or 0

        # Bump the Fees outstanding_amount back upward by the refund amount —
        # this is what the student portal's pending_fees query reads.
        new_outstanding = flt(fees.get("outstanding_amount")) + flt(self.net_refund)
        new_outstanding = min(new_outstanding, flt(fees.get("grand_total")))
        frappe.db.set_value("Fees", self.fees, "outstanding_amount",
                            new_outstanding, update_modified=False)

        if flt(total_refunded) >= paid_amount:
            frappe.db.set_value("Fees", self.fees, "status", "Refunded",
                                update_modified=False)


@frappe.whitelist()
def submit_for_approval(refund_name):
    """Submit refund for approval"""
    refund = frappe.get_doc("Fee Refund", refund_name)

    if refund.status != "Draft":
        frappe.throw(_("Only Draft refunds can be submitted for approval"))

    refund.status = "Pending Approval"
    refund.save()

    return {"success": True, "message": _("Refund submitted for approval")}


@frappe.whitelist()
def approve_refund(refund_name, remarks=None):
    """Approve a refund request"""
    refund = frappe.get_doc("Fee Refund", refund_name)

    if refund.status != "Pending Approval":
        frappe.throw(_("Only pending refunds can be approved"))

    refund.status = "Approved"
    refund.approved_by = frappe.session.user
    refund.approved_date = frappe.utils.today()
    if remarks:
        refund.approval_remarks = remarks
    refund.save()

    return {"success": True, "message": _("Refund approved successfully")}


@frappe.whitelist()
def reject_refund(refund_name, remarks=None):
    """Reject a refund request"""
    refund = frappe.get_doc("Fee Refund", refund_name)

    if refund.status not in ["Pending Approval", "Draft"]:
        frappe.throw(_("Only pending or draft refunds can be rejected"))

    refund.status = "Rejected"
    refund.approved_by = frappe.session.user
    refund.approved_date = frappe.utils.today()
    if remarks:
        refund.approval_remarks = remarks
    refund.save()

    return {"success": True, "message": _("Refund rejected")}


@frappe.whitelist()
def get_refund_summary(student=None, from_date=None, to_date=None):
    """Get refund summary"""
    conditions = ["docstatus = 1"]
    values = {}

    if student:
        conditions.append("student = %(student)s")
        values["student"] = student
    if from_date:
        conditions.append("refund_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append("refund_date <= %(to_date)s")
        values["to_date"] = to_date

    where_clause = "WHERE " + " AND ".join(conditions)

    summary = frappe.db.sql("""
        SELECT
            COUNT(*) as total_refunds,
            SUM(refund_amount) as total_refund_amount,
            SUM(deduction_amount) as total_deductions,
            SUM(net_refund) as total_net_refund
        FROM `tabFee Refund`
        {where_clause}
    """.format(where_clause=where_clause), values, as_dict=True)[0]

    return summary
