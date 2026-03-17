"""
Payment History Page Controller

Shows student's complete payment history with receipt download.
"""
import frappe
from frappe import _
from frappe.utils import flt


def get_context(context):
    """Get context for payment history page"""
    context.no_cache = 1

    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/student-portal/payment-history"
        raise frappe.Redirect

    # Get student linked to current user
    student = get_student_for_user()
    if not student:
        context.error = _("No student record found for your account.")
        return context

    # Get payment entries for student
    payments = frappe.db.sql("""
        SELECT
            pe.name,
            pe.posting_date,
            pe.paid_amount,
            pe.reference_no,
            pe.mode_of_payment,
            pe.docstatus
        FROM `tabPayment Entry` pe
        WHERE pe.party_type = 'Student'
        AND pe.party = %s
        AND pe.docstatus = 1
        AND pe.payment_type = 'Receive'
        ORDER BY pe.posting_date DESC
    """, student.name, as_dict=True)

    # Add status to payments
    for payment in payments:
        payment.status = "Completed"

    context.payments = payments
    context.payment_count = len(payments)
    context.total_paid = sum(flt(p.paid_amount) for p in payments)

    # Get available years for filtering
    context.available_years = sorted(set(p.posting_date.year for p in payments), reverse=True)

    # Get pending fees
    pending_fees = frappe.get_all(
        "Fees",
        filters={
            "student": student.name,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        },
        fields=["name", "due_date", "outstanding_amount", "program"],
        order_by="due_date asc"
    )

    context.pending_fees = pending_fees
    context.pending_amount = sum(flt(f.outstanding_amount) for f in pending_fees)

    return context


def get_student_for_user():
    """Get student record linked to current user"""
    # Try by user link
    student_name = frappe.db.get_value("Student", {"user": frappe.session.user})

    # Try by email
    if not student_name:
        student_name = frappe.db.get_value("Student", {"student_email_id": frappe.session.user})

    if student_name:
        return frappe.get_doc("Student", student_name)

    return None
