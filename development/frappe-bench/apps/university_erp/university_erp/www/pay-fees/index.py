"""
Pay Fees Page Controller

Handles the fee payment page that allows students to pay their fees online.
"""
import frappe
from frappe import _


def get_context(context):
    """Get context for pay-fees page"""
    context.no_cache = 1

    # Get fee reference from URL
    fees_name = frappe.form_dict.get("fees") or frappe.form_dict.get("name")

    if not fees_name:
        context.error = _("No fee reference provided. Please use a valid payment link.")
        return context

    # Check if user is logged in
    if frappe.session.user == "Guest":
        # Redirect to login with return URL
        frappe.local.flags.redirect_location = f"/login?redirect-to=/pay-fees?fees={fees_name}"
        raise frappe.Redirect

    try:
        # Get fee document
        fees = frappe.get_doc("Fees", fees_name)

        # Verify the logged-in user has permission to pay this fee
        if not has_payment_permission(fees):
            context.error = _("You don't have permission to pay this fee.")
            return context

        # Check if fee is already fully paid
        if fees.outstanding_amount <= 0:
            context.fees = fees
            return context

        # Get payment gateway settings
        razorpay_enabled = is_razorpay_enabled()
        payu_enabled = is_payu_enabled()

        if not razorpay_enabled and not payu_enabled:
            context.error = _("Online payment is currently unavailable. Please contact administration.")
            return context

        # Set context variables
        context.fees = fees
        context.razorpay_enabled = razorpay_enabled
        context.payu_enabled = payu_enabled

    except frappe.DoesNotExistError:
        context.error = _("Fee record not found. Please check the payment link.")
    except Exception as e:
        frappe.log_error(f"Pay Fees Error: {str(e)}", "Pay Fees Page")
        context.error = _("An error occurred. Please try again later.")

    return context


def has_payment_permission(fees):
    """Check if current user can pay this fee"""
    # System Manager and Accounts Manager can pay any fee
    if "System Manager" in frappe.get_roles() or "Accounts Manager" in frappe.get_roles():
        return True

    # Check if user is the student
    student = frappe.db.get_value("Student", fees.student, ["user", "student_email_id"], as_dict=True)
    if student:
        if student.user == frappe.session.user:
            return True
        if student.student_email_id == frappe.session.user:
            return True

    # Check if user is a guardian of the student
    guardian_student = frappe.db.get_all(
        "Student Guardian",
        filters={"parent": fees.student},
        fields=["guardian"]
    )
    for gs in guardian_student:
        guardian_email = frappe.db.get_value("Guardian", gs.guardian, "email_address")
        if guardian_email == frappe.session.user:
            return True

    return False


def is_razorpay_enabled():
    """Check if Razorpay is enabled"""
    try:
        settings = frappe.get_single("Razorpay Settings")
        return settings.enabled and settings.api_key
    except Exception:
        return False


def is_payu_enabled():
    """Check if PayU is enabled"""
    try:
        settings = frappe.get_single("PayU Settings")
        return settings.enabled and settings.merchant_key
    except Exception:
        return False
