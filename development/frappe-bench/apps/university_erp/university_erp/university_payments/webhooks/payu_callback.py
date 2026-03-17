# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
PayU Callback Handler
Handles success and failure callbacks from PayU
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def payu_success():
    """Handle PayU success callback"""
    params = frappe.form_dict

    try:
        settings = frappe.get_single("PayU Settings")

        # Verify hash
        if not settings.verify_response_hash(params):
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = "/fee-payment-failed?error=Invalid+signature"
            return

        txnid = params.get("txnid")
        if not txnid:
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = "/fee-payment-failed?error=Missing+transaction+ID"
            return

        # Find payment order
        payment_order_name = frappe.db.get_value(
            "Payment Order",
            {"gateway_order_id": txnid, "payment_gateway": "PayU"},
            "name"
        )

        if not payment_order_name:
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = f"/fee-payment-failed?error=Payment+order+not+found"
            return

        payment_order = frappe.get_doc("Payment Order", payment_order_name)

        # Check if already processed
        if payment_order.status == "Completed":
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = f"/fee-payment-success?payment={payment_order.payment_entry}"
            return

        # Update payment order
        payment_order.gateway_payment_id = params.get("mihpayid")
        payment_order.status = "Completed"
        payment_order.payment_date = frappe.utils.now_datetime()
        payment_order.save(ignore_permissions=True)

        # Process payment
        from university_erp.university_payments.payment_gateway import create_fee_payment_entry

        fees = frappe.get_doc("Fees", payment_order.reference_name)
        payment_entry = create_fee_payment_entry(
            fees=fees,
            amount=payment_order.amount,
            payment_id=params.get("mihpayid"),
            payment_gateway="PayU"
        )

        payment_order.payment_entry = payment_entry.name
        payment_order.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/fee-payment-success?payment={payment_entry.name}"

    except Exception as e:
        frappe.log_error(f"PayU success callback error: {str(e)}", "PayU Callback")
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/fee-payment-failed?error=Processing+error"


@frappe.whitelist(allow_guest=True)
def payu_failure():
    """Handle PayU failure callback"""
    params = frappe.form_dict

    try:
        txnid = params.get("txnid")
        if txnid:
            payment_order_name = frappe.db.get_value(
                "Payment Order",
                {"gateway_order_id": txnid, "payment_gateway": "PayU"},
                "name"
            )
            if payment_order_name:
                error_message = params.get("error_Message") or params.get("error") or "Payment failed"
                frappe.db.set_value("Payment Order", payment_order_name, {
                    "status": "Failed",
                    "failure_reason": error_message
                })
                frappe.db.commit()

        error = params.get("error_Message") or "Payment failed"
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/fee-payment-failed?error={error.replace(' ', '+')}"

    except Exception as e:
        frappe.log_error(f"PayU failure callback error: {str(e)}", "PayU Callback")
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/fee-payment-failed?error=Unknown+error"


@frappe.whitelist(allow_guest=True)
def payu_cancel():
    """Handle PayU cancel callback"""
    params = frappe.form_dict

    try:
        txnid = params.get("txnid")
        if txnid:
            payment_order_name = frappe.db.get_value(
                "Payment Order",
                {"gateway_order_id": txnid, "payment_gateway": "PayU"},
                "name"
            )
            if payment_order_name:
                frappe.db.set_value("Payment Order", payment_order_name, {
                    "status": "Cancelled",
                    "failure_reason": "Payment cancelled by user"
                })
                frappe.db.commit()

        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/fee-payment-failed?error=Payment+cancelled"

    except Exception as e:
        frappe.log_error(f"PayU cancel callback error: {str(e)}", "PayU Callback")
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/fee-payment-failed?error=Unknown+error"
