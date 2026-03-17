# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, nowdate


def get_context(context):
    """Student fees page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "fees"
    context.pending_fees = get_pending_fees(student.name)
    context.payment_history = get_payment_history(student.name)
    context.fee_summary = get_fee_summary(student.name)

    return context


def get_pending_fees(student):
    """Get all pending fees"""
    try:
        # Use Fees doctype which has outstanding_amount
        fees = frappe.db.sql("""
            SELECT
                f.name,
                f.fee_structure,
                f.academic_year,
                f.academic_term,
                f.due_date,
                f.grand_total as total_amount,
                (f.grand_total - f.outstanding_amount) as paid_amount,
                f.outstanding_amount,
                CASE
                    WHEN f.due_date < %s THEN 'Overdue'
                    WHEN f.due_date = %s THEN 'Due Today'
                    ELSE 'Upcoming'
                END as status
            FROM `tabFees` f
            WHERE f.student = %s
            AND f.outstanding_amount > 0
            AND f.docstatus = 1
            ORDER BY f.due_date ASC
        """, (nowdate(), nowdate(), student), as_dict=1)

        return fees
    except Exception:
        return []


def get_payment_history(student):
    """Get payment history"""
    try:
        # Try to get payment entries linked to Fees
        payments = frappe.db.sql("""
            SELECT
                pe.name,
                pe.posting_date,
                pe.paid_amount,
                pe.mode_of_payment,
                pe.reference_no,
                f.fee_structure,
                f.academic_year,
                f.academic_term
            FROM `tabPayment Entry` pe
            JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
            JOIN `tabFees` f ON f.name = per.reference_name
            WHERE f.student = %s
            AND pe.docstatus = 1
            AND per.reference_doctype = 'Fees'
            ORDER BY pe.posting_date DESC
            LIMIT 20
        """, student, as_dict=1)

        return payments
    except Exception:
        return []


def get_fee_summary(student):
    """Get fee summary statistics"""
    try:
        summary = frappe.db.sql("""
            SELECT
                COALESCE(SUM(grand_total), 0) as total_fees,
                COALESCE(SUM(grand_total - outstanding_amount), 0) as total_paid,
                COALESCE(SUM(outstanding_amount), 0) as total_pending,
                COUNT(*) as total_schedules,
                SUM(CASE WHEN outstanding_amount = 0 THEN 1 ELSE 0 END) as paid_schedules
            FROM `tabFees`
            WHERE student = %s
            AND docstatus = 1
        """, student, as_dict=1)

        return summary[0] if summary else {
            "total_fees": 0,
            "total_paid": 0,
            "total_pending": 0,
            "total_schedules": 0,
            "paid_schedules": 0
        }
    except Exception:
        return {
            "total_fees": 0,
            "total_paid": 0,
            "total_pending": 0,
            "total_schedules": 0,
            "paid_schedules": 0
        }


@frappe.whitelist()
def initiate_fee_payment(fee_name):
    """Initiate payment for a fee"""
    try:
        frappe.has_permission("Fees", "read", throw=True)

        fee = frappe.get_doc("Fees", fee_name)

        # Get current student
        student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
        if fee.student != student:
            frappe.throw(_("You can only pay your own fees"), frappe.PermissionError)

        if fee.outstanding_amount <= 0:
            frappe.throw(_("No outstanding amount for this fee"))

        # Create payment request or redirect to payment gateway
        payment_url = frappe.utils.get_url(f"/api/method/university_erp.api.portal_api.create_payment_request?fee_name={fee_name}")

        return {
            "success": True,
            "payment_url": payment_url,
            "amount": fee.outstanding_amount
        }
    except frappe.PermissionError:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
