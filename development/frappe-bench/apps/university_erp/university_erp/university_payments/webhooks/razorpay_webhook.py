# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Razorpay Webhook Handler
Handles payment events from Razorpay
"""

import frappe
from frappe import _
import hmac
import hashlib
import json
import time


@frappe.whitelist(allow_guest=True)
def handle_razorpay_webhook():
    """Handle Razorpay webhook events"""
    start_time = time.time()
    webhook_log_name = None

    try:
        payload = frappe.request.get_data(as_text=True)
        signature = frappe.request.headers.get("X-Razorpay-Signature")

        settings = frappe.get_single("Razorpay Settings")
        webhook_secret = settings.get_webhook_secret()

        # Parse event
        event = json.loads(payload)
        event_type = event.get("event")

        # Log webhook
        webhook_log_name = log_webhook(event_type, payload)

        # Verify signature
        if webhook_secret and not verify_webhook_signature(payload, signature, webhook_secret):
            frappe.local.response["http_status_code"] = 400
            mark_webhook_error(webhook_log_name, "Invalid signature")
            return {"error": "Invalid signature"}

        # Handle different event types
        handlers = {
            "payment.captured": handle_payment_captured,
            "payment.failed": handle_payment_failed,
            "payment.authorized": handle_payment_authorized,
            "refund.created": handle_refund_created,
            "refund.processed": handle_refund_processed,
            "order.paid": handle_order_paid
        }

        handler = handlers.get(event_type)
        if handler:
            handler(event.get("payload", {}))

        # Mark webhook as processed
        processing_time = (time.time() - start_time) * 1000
        mark_webhook_processed(webhook_log_name, {"status": "ok"}, processing_time)

        return {"status": "ok"}

    except json.JSONDecodeError as e:
        frappe.log_error(f"Invalid JSON in webhook: {str(e)}", "Razorpay Webhook")
        frappe.local.response["http_status_code"] = 400
        return {"error": "Invalid JSON"}
    except Exception as e:
        frappe.log_error(f"Razorpay webhook error: {str(e)}", "Razorpay Webhook")
        if webhook_log_name:
            mark_webhook_error(webhook_log_name, str(e))
        frappe.local.response["http_status_code"] = 500
        return {"error": str(e)}


def verify_webhook_signature(payload, signature, secret):
    """Verify Razorpay webhook signature"""
    if not signature or not secret:
        return False

    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


def handle_payment_captured(payload):
    """Handle payment.captured event"""
    payment = payload.get("payment", {}).get("entity", {})
    payment_id = payment.get("id")
    order_id = payment.get("order_id")

    if not order_id:
        return

    # Find payment order
    payment_order_name = frappe.db.get_value(
        "Payment Order",
        {"gateway_order_id": order_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order_name:
        payment_order = frappe.get_doc("Payment Order", payment_order_name)
        if payment_order.status != "Completed":
            payment_order.gateway_payment_id = payment_id
            payment_order.status = "Completed"
            payment_order.payment_date = frappe.utils.now_datetime()
            payment_order.save(ignore_permissions=True)

            # Process fee payment if not already done
            if not payment_order.payment_entry:
                process_fee_payment_from_webhook(payment_order)

            frappe.db.commit()


def handle_payment_failed(payload):
    """Handle payment.failed event"""
    payment = payload.get("payment", {}).get("entity", {})
    order_id = payment.get("order_id")
    error = payment.get("error_description") or payment.get("error_reason") or "Payment failed"

    if not order_id:
        return

    payment_order_name = frappe.db.get_value(
        "Payment Order",
        {"gateway_order_id": order_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order_name:
        frappe.db.set_value("Payment Order", payment_order_name, {
            "status": "Failed",
            "failure_reason": error
        })
        frappe.db.commit()


def handle_payment_authorized(payload):
    """Handle payment.authorized event (for manual capture)"""
    payment = payload.get("payment", {}).get("entity", {})
    order_id = payment.get("order_id")

    if not order_id:
        return

    payment_order_name = frappe.db.get_value(
        "Payment Order",
        {"gateway_order_id": order_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order_name:
        # If auto-capture is enabled, this will be followed by payment.captured
        # Just update status to Pending for manual capture scenarios
        settings = frappe.get_single("Razorpay Settings")
        if not settings.auto_capture:
            frappe.db.set_value("Payment Order", payment_order_name, "status", "Pending")
            frappe.db.commit()


def handle_order_paid(payload):
    """Handle order.paid event"""
    order = payload.get("order", {}).get("entity", {})
    order_id = order.get("id")

    if not order_id:
        return

    payment_order_name = frappe.db.get_value(
        "Payment Order",
        {"gateway_order_id": order_id, "payment_gateway": "Razorpay", "status": ["!=", "Completed"]},
        "name"
    )

    if payment_order_name:
        payment_order = frappe.get_doc("Payment Order", payment_order_name)
        if payment_order.status != "Completed":
            # Get payment ID from order
            payments = order.get("payments", {})
            if payments.get("items"):
                payment_id = payments["items"][0].get("id")
                payment_order.gateway_payment_id = payment_id

            payment_order.status = "Completed"
            payment_order.payment_date = frappe.utils.now_datetime()
            payment_order.save(ignore_permissions=True)

            if not payment_order.payment_entry:
                process_fee_payment_from_webhook(payment_order)

            frappe.db.commit()


def handle_refund_created(payload):
    """Handle refund.created event"""
    refund = payload.get("refund", {}).get("entity", {})
    payment_id = refund.get("payment_id")
    refund_id = refund.get("id")
    refund_amount = (refund.get("amount", 0) or 0) / 100  # Convert from paise

    if not payment_id:
        return

    payment_order_name = frappe.db.get_value(
        "Payment Order",
        {"gateway_payment_id": payment_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order_name:
        frappe.db.set_value("Payment Order", payment_order_name, {
            "status": "Refunded",
            "refund_id": refund_id,
            "refund_amount": refund_amount,
            "refund_date": frappe.utils.now_datetime()
        })

        # Process refund entry
        process_refund_entry(payment_order_name, refund_amount)
        frappe.db.commit()


def handle_refund_processed(payload):
    """Handle refund.processed event"""
    # Similar to refund.created but confirms refund is complete
    handle_refund_created(payload)


def log_webhook(event_type, payload):
    """Log webhook for debugging"""
    from university_erp.university_payments.doctype.webhook_log.webhook_log import log_webhook as create_log
    return create_log("Razorpay", event_type, payload)


def mark_webhook_processed(webhook_log_name, response, processing_time):
    """Mark webhook as processed"""
    if webhook_log_name:
        from university_erp.university_payments.doctype.webhook_log.webhook_log import mark_webhook_processed as mark_processed
        mark_processed(webhook_log_name, response, processing_time)


def mark_webhook_error(webhook_log_name, error_message):
    """Mark webhook with error"""
    if webhook_log_name:
        frappe.db.set_value("Webhook Log", webhook_log_name, "error_message", error_message)
        frappe.db.commit()


def process_fee_payment_from_webhook(payment_order):
    """Process fee payment from webhook"""
    if payment_order.reference_doctype == "Fees" and not payment_order.payment_entry:
        from university_erp.university_payments.payment_gateway import create_fee_payment_entry

        fees = frappe.get_doc("Fees", payment_order.reference_name)
        payment_entry = create_fee_payment_entry(
            fees=fees,
            amount=payment_order.amount,
            payment_id=payment_order.gateway_payment_id,
            payment_gateway=payment_order.payment_gateway
        )
        payment_order.payment_entry = payment_entry.name
        payment_order.save(ignore_permissions=True)


def process_refund_entry(payment_order_name, refund_amount):
    """Create refund entry"""
    payment_order = frappe.get_doc("Payment Order", payment_order_name)

    if payment_order.payment_entry:
        # Create reverse payment entry
        original_entry = frappe.get_doc("Payment Entry", payment_order.payment_entry)

        refund_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "posting_date": frappe.utils.today(),
            "company": original_entry.company,
            "party_type": "Student",
            "party": payment_order.student,
            "party_name": payment_order.student_name,
            "paid_amount": refund_amount,
            "received_amount": refund_amount,
            "target_exchange_rate": 1,
            "paid_from": original_entry.paid_to,
            "mode_of_payment": "Online Refund",
            "reference_no": payment_order.refund_id,
            "reference_date": frappe.utils.today(),
            "remarks": f"Refund for {payment_order.gateway_payment_id} - {payment_order.name}"
        })
        refund_entry.insert(ignore_permissions=True)
        refund_entry.submit()
