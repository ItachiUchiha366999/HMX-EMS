"""
Fee Payment Success Page Controller

Displays payment confirmation after successful fee payment.
"""
import frappe
from frappe import _


def get_context(context):
    """Get context for payment success page"""
    context.no_cache = 1

    # Get payment reference from URL
    payment_entry_name = frappe.form_dict.get("payment")
    payment_order_name = frappe.form_dict.get("order")

    if not payment_entry_name and not payment_order_name:
        context.error = _("No payment reference provided.")
        return context

    try:
        # Get payment entry
        if payment_entry_name:
            payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
            context.payment_entry = payment_entry

            # Get associated payment order
            payment_order = frappe.db.get_value(
                "Payment Order",
                {"payment_entry": payment_entry_name},
                ["name", "gateway_order_id", "gateway_payment_id", "reference_name"],
                as_dict=True
            )
            if payment_order:
                context.payment_order = payment_order

                # Get fees document
                if payment_order.reference_name:
                    fees = frappe.get_doc("Fees", payment_order.reference_name)
                    context.fees = fees

        elif payment_order_name:
            payment_order = frappe.get_doc("Payment Order", payment_order_name)
            context.payment_order = payment_order

            if payment_order.payment_entry:
                payment_entry = frappe.get_doc("Payment Entry", payment_order.payment_entry)
                context.payment_entry = payment_entry

            if payment_order.reference_name:
                fees = frappe.get_doc("Fees", payment_order.reference_name)
                context.fees = fees

    except frappe.DoesNotExistError:
        context.error = _("Payment record not found.")
    except Exception as e:
        frappe.log_error(f"Payment Success Page Error: {str(e)}", "Payment Success Page")
        context.error = _("An error occurred while loading payment details.")

    return context
