"""Offline / counter payment recorder for student fees.

Used by the registrar / cashier to record an offline payment (cash, cheque,
bank transfer, UPI) against a student's Fees document. Creates a submitted
Payment Entry that the student portal Fees page will then display under
Payment History, and the receipt download will work against.
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_payment_quote(fee_name):
    """Return outstanding, pending_scholarship and student-residual for a Fees doc.

    Used by the desk-side `Record Offline Payment` dialog to default the
    Amount field to what the student can actually pay (i.e. excluding the
    slice reserved for an approved-but-not-yet-disbursed scholarship).
    """
    fees = frappe.db.get_value(
        "Fees", fee_name,
        ["student", "grand_total", "outstanding_amount"],
        as_dict=True,
    ) or {}
    if not fees:
        frappe.throw(_("Fees {0} not found").format(fee_name))

    pending_scholarship = float(frappe.db.sql("""
        SELECT COALESCE(SUM(discount_amount), 0)
        FROM `tabStudent Scholarship`
        WHERE student = %s AND workflow_state = 'Approved'
    """, fees.student)[0][0] or 0)

    outstanding = float(fees.outstanding_amount or 0)
    residual = max(outstanding - pending_scholarship, 0)
    return {
        "fee_name": fee_name,
        "grand_total": float(fees.grand_total or 0),
        "outstanding_amount": outstanding,
        "pending_scholarship_amount": pending_scholarship,
        "student_residual": residual,
    }


@frappe.whitelist()
def list_outstanding_fees(student=None):
    """For the cashier: list fees rows with outstanding > 0.
    If `student` is omitted, returns ALL outstanding fees site-wide.
    """
    cond = "f.outstanding_amount > 0 AND f.docstatus = 1"
    args = []
    if student:
        cond += " AND f.student = %s"
        args.append(student)

    return frappe.db.sql(f"""
        SELECT f.name, f.student, f.student_name, f.program, f.academic_term,
               f.grand_total, f.outstanding_amount, f.due_date
        FROM `tabFees` f
        WHERE {cond}
        ORDER BY f.due_date ASC
        LIMIT 100
    """, args, as_dict=True)


@frappe.whitelist()
def record_offline_payment(fee_name, amount, mode_of_payment, reference_no=None, reference_date=None):
    """Create + submit a Payment Entry for the given Fees doc.

    Permissions: caller must have `University Finance` (or be System Manager).
    """
    roles = frappe.get_roles(frappe.session.user)
    if not ({"University Finance", "System Manager", "Administrator"} & set(roles)):
        frappe.throw(_("You don't have permission to record payments. Need 'University Finance' role."),
                     frappe.PermissionError)

    fees = frappe.get_doc("Fees", fee_name)
    if fees.docstatus != 1:
        frappe.throw(_("Fees record must be submitted before recording a payment"))

    amount = float(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be greater than zero"))

    # Compute the student's actual residual share after any approved-but-not-yet-disbursed
    # scholarship. The cashier cannot accept more than this — the scholarship slice
    # is reserved for the funding body and will be settled when the scholarship moves
    # to Disbursed.
    pending_scholarship = float(frappe.db.sql("""
        SELECT COALESCE(SUM(discount_amount), 0)
        FROM `tabStudent Scholarship`
        WHERE student = %s AND workflow_state = 'Approved'
    """, fees.student)[0][0] or 0)

    outstanding = float(fees.outstanding_amount or 0)
    residual = max(outstanding - pending_scholarship, 0)

    if amount > outstanding:
        frappe.throw(_("Amount ₹{0:,.0f} exceeds outstanding ₹{1:,.0f}").format(amount, outstanding))

    if pending_scholarship > 0 and amount > residual:
        frappe.throw(
            _("Cannot accept ₹{0:,.0f} — ₹{1:,.0f} is reserved for an approved scholarship "
              "pending disbursement. Maximum the student can pay now is ₹{2:,.0f}.").format(
                amount, pending_scholarship, residual
            )
        )

    company = frappe.db.get_value("Company", {}, "name")

    # Pick paid_to (cash / bank) account — match by Mode of Payment
    paid_to = _account_for_mode(mode_of_payment, company)
    if not paid_to:
        frappe.throw(_("No active asset account configured for {0}").format(mode_of_payment))

    # paid_from = the Receivable account on the Fees doc (or fall back to default)
    paid_from = getattr(fees, "receivable_account", None) \
        or frappe.db.get_value("Account",
            {"company": company, "account_type": "Receivable", "is_group": 0},
            "name")
    if not paid_from:
        frappe.throw(_("No Receivable account configured for company {0}").format(company))

    pe = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "posting_date": frappe.utils.nowdate(),
        "company": company,
        "mode_of_payment": mode_of_payment,
        "party_type": "Student",
        "party": fees.student,
        "party_name": fees.student_name,
        "paid_from": paid_from,
        "paid_to": paid_to,
        "paid_amount": amount,
        "received_amount": amount,
        "reference_no": reference_no or f"OFFLINE-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}",
        "reference_date": reference_date or frappe.utils.nowdate(),
        "references": [{
            "reference_doctype": "Fees",
            "reference_name": fees.name,
            "total_amount": fees.grand_total,
            "outstanding_amount": fees.outstanding_amount,
            "allocated_amount": amount,
        }],
    })
    pe.flags.ignore_permissions = True
    pe.flags.ignore_mandatory = True
    pe.insert(ignore_permissions=True)
    pe.submit()

    # Refresh outstanding on the Fees doc — Frappe Education sometimes lags here
    new_outstanding = max((fees.outstanding_amount or 0) - amount, 0)
    fees.db_set("outstanding_amount", new_outstanding, update_modified=False)

    return {
        "payment_entry": pe.name,
        "amount": amount,
        "mode": mode_of_payment,
        "reference_no": pe.reference_no,
        "fee_name": fees.name,
        "remaining_outstanding": new_outstanding,
        "fully_paid": new_outstanding == 0,
    }


def _account_for_mode(mode, company):
    """Pick the best asset account for the given Mode of Payment."""
    # 1. Look at the Mode of Payment Account child table
    rows = frappe.db.sql("""
        SELECT default_account
        FROM `tabMode of Payment Account`
        WHERE parent=%s AND company=%s
        LIMIT 1
    """, (mode, company))
    if rows and rows[0][0]:
        return rows[0][0]

    # 2. Fall back by mode keyword
    if "Cash" in mode:
        return frappe.db.get_value("Account",
            {"company": company, "account_type": "Cash", "is_group": 0}, "name")
    return frappe.db.get_value("Account",
        {"company": company, "account_type": "Bank", "is_group": 0}, "name") \
        or frappe.db.get_value("Account",
            {"company": company, "account_type": "Cash", "is_group": 0}, "name")
