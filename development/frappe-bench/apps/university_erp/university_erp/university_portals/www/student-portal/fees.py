# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, nowdate


def get_context(context):
    """Student fees page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.pending_fees = get_pending_fees(student.name)
    context.payment_history = get_payment_history(student.name)
    context.fee_summary = get_fee_summary(student.name)

    return context


def get_pending_fees(student):
    """Get all pending fee schedules"""
    fees = frappe.db.sql("""
        SELECT
            fs.name,
            fs.fee_structure,
            fs.academic_year,
            fs.academic_term,
            fs.due_date,
            fs.total_amount,
            fs.paid_amount,
            fs.outstanding_amount,
            CASE
                WHEN fs.due_date < %s THEN 'Overdue'
                WHEN fs.due_date = %s THEN 'Due Today'
                ELSE 'Upcoming'
            END as status
        FROM `tabFee Schedule` fs
        WHERE fs.student = %s
        AND fs.outstanding_amount > 0
        AND fs.docstatus = 1
        ORDER BY fs.due_date ASC
    """, (nowdate(), nowdate(), student), as_dict=1)

    return fees


def get_payment_history(student):
    """Get payment history"""
    payments = frappe.db.sql("""
        SELECT
            pe.name,
            pe.posting_date,
            pe.paid_amount,
            pe.mode_of_payment,
            pe.reference_no,
            fs.fee_structure,
            fs.academic_year,
            fs.academic_term
        FROM `tabPayment Entry` pe
        JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
        JOIN `tabFee Schedule` fs ON fs.name = per.reference_name
        WHERE fs.student = %s
        AND pe.docstatus = 1
        AND per.reference_doctype = 'Fee Schedule'
        ORDER BY pe.posting_date DESC
        LIMIT 20
    """, student, as_dict=1)

    return payments


def get_fee_summary(student):
    """Get fee summary statistics"""
    summary = frappe.db.sql("""
        SELECT
            COALESCE(SUM(total_amount), 0) as total_fees,
            COALESCE(SUM(paid_amount), 0) as total_paid,
            COALESCE(SUM(outstanding_amount), 0) as total_pending,
            COUNT(*) as total_schedules,
            SUM(CASE WHEN outstanding_amount = 0 THEN 1 ELSE 0 END) as paid_schedules
        FROM `tabFee Schedule`
        WHERE student = %s
        AND docstatus = 1
    """, student, as_dict=1)

    return summary[0] if summary else {}


@frappe.whitelist()
def initiate_fee_payment(fee_schedule):
    """Initiate payment for a fee schedule"""
    frappe.has_permission("Fee Schedule", "read", throw=True)

    fee = frappe.get_doc("Fee Schedule", fee_schedule)

    # Get current student
    student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    if fee.student != student:
        frappe.throw(_("You can only pay your own fees"), frappe.PermissionError)

    if fee.outstanding_amount <= 0:
        frappe.throw(_("No outstanding amount for this fee schedule"))

    # Create payment request or redirect to payment gateway
    # This would integrate with the payment gateway configured in the system
    payment_url = frappe.utils.get_url(f"/api/method/university_erp.university_portals.api.portal_api.create_payment_request?fee_schedule={fee_schedule}")

    return {
        "success": True,
        "payment_url": payment_url,
        "amount": fee.outstanding_amount
    }
