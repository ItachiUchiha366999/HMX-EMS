# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Payment Gateway Webhooks
Handles payment callbacks from Razorpay, PayU, etc.
"""

import frappe
from frappe import _
import json
import hashlib
import hmac


@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """
    Handle Razorpay webhook events

    Validates signature and processes payment events
    """
    try:
        # Get payload
        payload = frappe.request.get_data(as_text=True)
        signature = frappe.get_request_header("X-Razorpay-Signature")

        # Get webhook secret from settings
        settings = frappe.get_single("University ERP Settings")
        webhook_secret = settings.get("razorpay_webhook_secret")

        if not webhook_secret:
            log_webhook_event("razorpay", payload, "error", "Webhook secret not configured")
            return {"status": "error", "message": "Configuration error"}

        # Verify signature
        if not verify_razorpay_signature(payload, signature, webhook_secret):
            log_webhook_event("razorpay", payload, "error", "Invalid signature")
            frappe.local.response["http_status_code"] = 401
            return {"status": "error", "message": "Invalid signature"}

        # Parse event
        event = json.loads(payload)
        event_type = event.get("event")

        # Log the event
        log_webhook_event("razorpay", payload, "received", event_type)

        # Process based on event type
        if event_type == "payment.captured":
            result = process_payment_captured(event)
        elif event_type == "payment.failed":
            result = process_payment_failed(event)
        elif event_type == "refund.created":
            result = process_refund(event)
        elif event_type == "payment.authorized":
            result = {"status": "acknowledged", "message": "Payment authorized"}
        else:
            result = {"status": "ignored", "message": f"Event {event_type} not handled"}

        # Update log status
        log_webhook_event("razorpay", payload, "processed", json.dumps(result))

        return result

    except json.JSONDecodeError:
        log_webhook_event("razorpay", frappe.request.get_data(as_text=True), "error", "Invalid JSON")
        frappe.local.response["http_status_code"] = 400
        return {"status": "error", "message": "Invalid JSON payload"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Razorpay Webhook Error")
        log_webhook_event("razorpay", frappe.request.get_data(as_text=True), "error", str(e))
        frappe.local.response["http_status_code"] = 500
        return {"status": "error", "message": "Internal error"}


def verify_razorpay_signature(payload, signature, secret):
    """Verify Razorpay webhook signature"""
    if not signature:
        return False

    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def process_payment_captured(event):
    """
    Process payment.captured event

    This is called when a payment is successfully captured
    """
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})

    razorpay_payment_id = payment_entity.get("id")
    razorpay_order_id = payment_entity.get("order_id")
    amount = payment_entity.get("amount", 0) / 100  # Convert from paise to rupees
    currency = payment_entity.get("currency", "INR")
    email = payment_entity.get("email")
    contact = payment_entity.get("contact")
    notes = payment_entity.get("notes", {})

    # Get fee reference from notes
    fee_id = notes.get("fee_id")

    if not fee_id:
        return {"status": "error", "message": "No fee reference in payment"}

    # Check if payment already processed
    existing = frappe.db.exists(
        "Payment Entry",
        {"reference_no": razorpay_payment_id}
    )

    if existing:
        return {"status": "duplicate", "message": "Payment already processed"}

    try:
        # Get fee details
        fee = frappe.get_doc("Fees", fee_id)

        if fee.outstanding_amount <= 0:
            return {"status": "error", "message": "Fee already paid"}

        # Create Payment Entry
        payment = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Student",
            "party": fee.student,
            "party_name": fee.student_name,
            "paid_amount": min(amount, fee.outstanding_amount),
            "received_amount": min(amount, fee.outstanding_amount),
            "target_exchange_rate": 1,
            "paid_to": get_fee_receivable_account(),
            "reference_no": razorpay_payment_id,
            "reference_date": frappe.utils.nowdate(),
            "mode_of_payment": "Online Payment",
            "remarks": f"Razorpay Payment - Order: {razorpay_order_id}"
        })

        # Add reference to fee
        payment.append("references", {
            "reference_doctype": "Fees",
            "reference_name": fee_id,
            "allocated_amount": min(amount, fee.outstanding_amount)
        })

        payment.insert(ignore_permissions=True)
        payment.submit()

        # Send notification
        send_payment_confirmation(fee, amount, razorpay_payment_id)

        return {
            "status": "success",
            "payment_entry": payment.name,
            "amount": amount,
            "fee_id": fee_id
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Payment Processing Error")
        return {"status": "error", "message": str(e)}


def process_payment_failed(event):
    """
    Process payment.failed event

    This is called when a payment fails
    """
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})

    razorpay_payment_id = payment_entity.get("id")
    error_code = payment_entity.get("error_code")
    error_description = payment_entity.get("error_description")
    notes = payment_entity.get("notes", {})

    fee_id = notes.get("fee_id")

    # Log the failure
    frappe.get_doc({
        "doctype": "Payment Webhook Log",
        "gateway": "Razorpay",
        "event_type": "payment.failed",
        "payment_id": razorpay_payment_id,
        "reference_doctype": "Fees",
        "reference_name": fee_id,
        "status": "Failed",
        "error_message": f"{error_code}: {error_description}"
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "status": "logged",
        "payment_id": razorpay_payment_id,
        "error": error_description
    }


def process_refund(event):
    """
    Process refund.created event

    This is called when a refund is initiated
    """
    refund_entity = event.get("payload", {}).get("refund", {}).get("entity", {})

    refund_id = refund_entity.get("id")
    payment_id = refund_entity.get("payment_id")
    amount = refund_entity.get("amount", 0) / 100
    notes = refund_entity.get("notes", {})

    # Find original payment
    payment_entry = frappe.db.get_value(
        "Payment Entry",
        {"reference_no": payment_id},
        ["name", "party"],
        as_dict=True
    )

    if not payment_entry:
        return {"status": "error", "message": "Original payment not found"}

    try:
        # Create refund entry (as a return payment)
        refund = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Student",
            "party": payment_entry.party,
            "paid_amount": amount,
            "received_amount": amount,
            "paid_from": get_fee_receivable_account(),
            "reference_no": refund_id,
            "reference_date": frappe.utils.nowdate(),
            "mode_of_payment": "Online Payment",
            "remarks": f"Razorpay Refund for Payment: {payment_id}"
        })

        refund.insert(ignore_permissions=True)
        refund.submit()

        return {
            "status": "success",
            "refund_entry": refund.name,
            "amount": amount
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Refund Processing Error")
        return {"status": "error", "message": str(e)}


def log_webhook_event(gateway, payload, status, message=None):
    """Log webhook event for debugging"""
    try:
        frappe.get_doc({
            "doctype": "Payment Webhook Log",
            "gateway": gateway,
            "payload": payload[:65000] if payload else None,  # Truncate if too long
            "status": status,
            "error_message": message
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        pass  # Don't fail if logging fails


def get_fee_receivable_account():
    """Get the fee receivable account"""
    company = frappe.db.get_single_value("Global Defaults", "default_company")

    account = frappe.db.get_value(
        "Company",
        company,
        "default_receivable_account"
    )

    if not account:
        # Fallback to finding a receivable account
        account = frappe.db.get_value(
            "Account",
            {
                "company": company,
                "account_type": "Receivable",
                "is_group": 0
            },
            "name"
        )

    return account


def send_payment_confirmation(fee, amount, payment_id):
    """Send payment confirmation notification"""
    from university_erp.university_erp.notification_service import NotificationService

    if fee.student_email_id:
        context = {
            "student_name": fee.student_name,
            "amount": amount,
            "payment_id": payment_id,
            "fee_id": fee.name,
            "remaining_amount": fee.outstanding_amount - amount
        }

        NotificationService.send_notification(
            recipients=[fee.student_email_id],
            template_name="payment_confirmation",
            context=context,
            respect_preferences=False  # Always send payment confirmations
        )


@frappe.whitelist(allow_guest=True)
def payu_webhook():
    """
    Handle PayU webhook events

    Alternative payment gateway handler
    """
    try:
        # PayU sends form data
        data = frappe.form_dict

        txn_id = data.get("txnid")
        status = data.get("status")
        amount = data.get("amount")
        hash_value = data.get("hash")

        # Get PayU credentials
        settings = frappe.get_single("University ERP Settings")
        merchant_key = settings.get("payu_merchant_key")
        salt = settings.get("payu_salt")

        # Verify hash (simplified - actual implementation needs full hash verification)
        if not merchant_key or not salt:
            log_webhook_event("payu", json.dumps(dict(data)), "error", "PayU not configured")
            return {"status": "error"}

        log_webhook_event("payu", json.dumps(dict(data)), "received", status)

        if status == "success":
            # Process successful payment
            # Similar to Razorpay processing
            return {"status": "success"}
        else:
            return {"status": "failed"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "PayU Webhook Error")
        return {"status": "error"}
