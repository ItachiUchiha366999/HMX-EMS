"""
Fee Payment Failed Page Controller

Displays error information when payment fails.
"""
import frappe
from frappe import _


def get_context(context):
    """Get context for payment failed page"""
    context.no_cache = 1

    # Get error details from URL
    error_message = frappe.form_dict.get("error")
    fees_name = frappe.form_dict.get("fees")
    order_id = frappe.form_dict.get("order")

    if error_message:
        # Decode URL-encoded error message
        import urllib.parse
        context.error_message = urllib.parse.unquote(error_message)

    if fees_name:
        context.fees_name = fees_name

    # Try to get fee details if available
    if fees_name:
        try:
            fees = frappe.get_doc("Fees", fees_name)
            context.fees = fees
        except Exception:
            pass

    # Log the failed payment attempt
    if order_id:
        try:
            payment_order = frappe.get_doc("Payment Order", {"gateway_order_id": order_id})
            if payment_order and payment_order.status not in ["Completed", "Failed"]:
                payment_order.status = "Failed"
                payment_order.failure_reason = error_message or "Payment failed"
                payment_order.save(ignore_permissions=True)
                frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to update payment order: {str(e)}", "Payment Failed Page")

    return context
