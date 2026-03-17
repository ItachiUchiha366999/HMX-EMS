# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Payment Gateway Integration Module
Supports: Razorpay, PayU, Paytm, CCAvenue, Stripe
"""

import frappe
from frappe import _
import hashlib
import hmac
import json


class PaymentGateway:
    """Base payment gateway handler"""

    def __init__(self):
        self.settings = frappe.get_single("Payment Gateway Settings")

    def create_order(self, amount, student, reference_doctype=None, reference_name=None):
        """Create payment order - to be implemented by subclass"""
        raise NotImplementedError

    def verify_payment(self, payment_data):
        """Verify payment signature - to be implemented by subclass"""
        raise NotImplementedError

    def process_refund(self, transaction, amount=None, reason=None):
        """Process refund - to be implemented by subclass"""
        raise NotImplementedError


class RazorpayGateway(PaymentGateway):
    """Razorpay payment gateway implementation"""

    def __init__(self):
        super().__init__()
        self.client = self.settings.get_razorpay_client()

    def create_order(self, amount, student, reference_doctype=None, reference_name=None):
        """Create Razorpay order"""
        try:
            # Amount in paise
            amount_paise = int(float(amount) * 100)

            # Get student details
            student_doc = frappe.get_doc("Student", student)

            order_data = {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"rcpt_{frappe.utils.random_string(10)}",
                "notes": {
                    "student": student,
                    "student_name": student_doc.student_name,
                    "reference_doctype": reference_doctype or "",
                    "reference_name": reference_name or ""
                }
            }

            order = self.client.order.create(data=order_data)

            # Create transaction record
            transaction = frappe.get_doc({
                "doctype": "Payment Transaction",
                "student": student,
                "amount": amount,
                "payment_gateway": "Razorpay",
                "gateway_order_id": order["id"],
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "status": "Initiated"
            })
            transaction.insert(ignore_permissions=True)
            frappe.db.commit()

            return {
                "success": True,
                "order_id": order["id"],
                "transaction": transaction.name,
                "key_id": self.settings.razorpay_key_id,
                "amount": amount_paise,
                "currency": "INR",
                "name": student_doc.student_name,
                "email": student_doc.student_email_id or "",
                "contact": student_doc.student_mobile_number or ""
            }

        except Exception as e:
            frappe.log_error(f"Razorpay order creation failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}

    def verify_payment(self, payment_data):
        """Verify Razorpay payment signature"""
        try:
            order_id = payment_data.get("razorpay_order_id")
            payment_id = payment_data.get("razorpay_payment_id")
            signature = payment_data.get("razorpay_signature")

            # Verify signature
            secret = self.settings.get_password("razorpay_key_secret")
            message = f"{order_id}|{payment_id}"

            expected_signature = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            if signature == expected_signature:
                # Update transaction
                transaction = frappe.get_doc(
                    "Payment Transaction",
                    {"gateway_order_id": order_id}
                )
                transaction.gateway_payment_id = payment_id
                transaction.gateway_signature = signature
                transaction.status = "Success"
                transaction.payment_method = self._get_payment_method(payment_id)
                transaction.gateway_response = json.dumps(payment_data)
                transaction.save(ignore_permissions=True)
                frappe.db.commit()

                return {"success": True, "transaction": transaction.name}
            else:
                # Update transaction as failed
                transaction = frappe.get_doc(
                    "Payment Transaction",
                    {"gateway_order_id": order_id}
                )
                transaction.status = "Failed"
                transaction.error_message = "Signature verification failed"
                transaction.save(ignore_permissions=True)
                frappe.db.commit()

                return {"success": False, "error": "Signature verification failed"}

        except Exception as e:
            frappe.log_error(f"Payment verification failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}

    def _get_payment_method(self, payment_id):
        """Get payment method from Razorpay"""
        try:
            payment = self.client.payment.fetch(payment_id)
            method = payment.get("method", "")
            method_mapping = {
                "card": "Card",
                "netbanking": "NetBanking",
                "upi": "UPI",
                "wallet": "Wallet",
                "emi": "EMI",
                "bank_transfer": "Bank Transfer"
            }
            return method_mapping.get(method, method.capitalize())
        except Exception:
            return ""

    def process_refund(self, transaction_name, amount=None, reason=None):
        """Process refund through Razorpay"""
        try:
            transaction = frappe.get_doc("Payment Transaction", transaction_name)

            if transaction.status != "Success":
                return {"success": False, "error": "Can only refund successful payments"}

            refund_amount = float(amount) if amount else transaction.amount
            refund_amount_paise = int(refund_amount * 100)

            refund = self.client.payment.refund(
                transaction.gateway_payment_id,
                {
                    "amount": refund_amount_paise,
                    "notes": {"reason": reason or "Requested by admin"}
                }
            )

            # Determine if partial or full refund
            if refund_amount < transaction.amount:
                transaction.status = "Partially Refunded"
            else:
                transaction.status = "Refunded"

            transaction.refund_id = refund["id"]
            transaction.refund_amount = refund_amount
            transaction.refund_date = frappe.utils.now_datetime()
            transaction.refund_reason = reason
            transaction.refund_status = "Processed"
            transaction.save(ignore_permissions=True)
            frappe.db.commit()

            return {"success": True, "refund_id": refund["id"]}

        except Exception as e:
            frappe.log_error(f"Refund failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}


class PayUGateway(PaymentGateway):
    """PayU payment gateway implementation"""

    def __init__(self):
        super().__init__()
        self.merchant_key = self.settings.payu_merchant_key
        self.merchant_salt = self.settings.get_password("payu_merchant_salt")
        self.base_url = (
            "https://secure.payu.in" if self.settings.environment == "Production"
            else "https://sandboxsecure.payu.in"
        )

    def create_order(self, amount, student, reference_doctype=None, reference_name=None):
        """Create PayU payment request"""
        try:
            student_doc = frappe.get_doc("Student", student)
            txnid = f"TXN{frappe.utils.random_string(12)}"

            # Create hash
            hash_string = (
                f"{self.merchant_key}|{txnid}|{amount}|Fee Payment|"
                f"{student_doc.first_name or student_doc.student_name.split()[0]}|"
                f"{student_doc.student_email_id or ''}|||||||||||"
                f"{self.merchant_salt}"
            )
            hash_value = hashlib.sha512(hash_string.encode()).hexdigest()

            # Create transaction record
            transaction = frappe.get_doc({
                "doctype": "Payment Transaction",
                "student": student,
                "amount": amount,
                "payment_gateway": "PayU",
                "gateway_order_id": txnid,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "status": "Initiated"
            })
            transaction.insert(ignore_permissions=True)
            frappe.db.commit()

            return {
                "success": True,
                "payment_url": f"{self.base_url}/_payment",
                "params": {
                    "key": self.merchant_key,
                    "txnid": txnid,
                    "amount": str(amount),
                    "productinfo": "Fee Payment",
                    "firstname": student_doc.first_name or student_doc.student_name.split()[0],
                    "email": student_doc.student_email_id or "",
                    "phone": student_doc.student_mobile_number or "",
                    "surl": self.settings.success_url,
                    "furl": self.settings.failure_url,
                    "hash": hash_value
                },
                "transaction": transaction.name
            }

        except Exception as e:
            frappe.log_error(f"PayU order creation failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}

    def verify_payment(self, payment_data):
        """Verify PayU payment response"""
        try:
            txnid = payment_data.get("txnid")
            status = payment_data.get("status")
            amount = payment_data.get("amount")
            received_hash = payment_data.get("hash")

            # Verify reverse hash
            additional_charges = payment_data.get("additionalCharges", "")
            if additional_charges:
                hash_string = f"{additional_charges}|{self.merchant_salt}|{status}|||||||||||"
            else:
                hash_string = f"{self.merchant_salt}|{status}|||||||||||"

            hash_string += (
                f"{payment_data.get('email', '')}|"
                f"{payment_data.get('firstname', '')}|"
                f"{payment_data.get('productinfo', '')}|"
                f"{amount}|{txnid}|{self.merchant_key}"
            )
            calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest()

            transaction = frappe.get_doc(
                "Payment Transaction",
                {"gateway_order_id": txnid}
            )

            if received_hash == calculated_hash and status == "success":
                transaction.gateway_payment_id = payment_data.get("mihpayid")
                transaction.status = "Success"
                transaction.payment_method = payment_data.get("mode", "").capitalize()
                transaction.gateway_response = json.dumps(payment_data)
                transaction.save(ignore_permissions=True)
                frappe.db.commit()

                return {"success": True, "transaction": transaction.name}
            else:
                transaction.status = "Failed"
                transaction.error_message = payment_data.get("error_Message", "Verification failed")
                transaction.gateway_response = json.dumps(payment_data)
                transaction.save(ignore_permissions=True)
                frappe.db.commit()

                return {"success": False, "error": "Payment verification failed"}

        except Exception as e:
            frappe.log_error(f"PayU verification failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}


class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation"""

    def __init__(self):
        super().__init__()
        self.stripe = self.settings.get_stripe_client()

    def create_order(self, amount, student, reference_doctype=None, reference_name=None):
        """Create Stripe checkout session"""
        try:
            student_doc = frappe.get_doc("Student", student)

            # Amount in paise (smallest currency unit)
            amount_paise = int(float(amount) * 100)

            # Create checkout session
            session = self.stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": "Fee Payment",
                            "description": f"Payment for {student_doc.student_name}"
                        },
                        "unit_amount": amount_paise
                    },
                    "quantity": 1
                }],
                mode="payment",
                success_url=self.settings.success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=self.settings.cancel_url or self.settings.failure_url,
                customer_email=student_doc.student_email_id,
                metadata={
                    "student": student,
                    "reference_doctype": reference_doctype or "",
                    "reference_name": reference_name or ""
                }
            )

            # Create transaction record
            transaction = frappe.get_doc({
                "doctype": "Payment Transaction",
                "student": student,
                "amount": amount,
                "payment_gateway": "Stripe",
                "gateway_order_id": session.id,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "status": "Initiated"
            })
            transaction.insert(ignore_permissions=True)
            frappe.db.commit()

            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url,
                "transaction": transaction.name
            }

        except Exception as e:
            frappe.log_error(f"Stripe session creation failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}

    def verify_payment(self, session_id):
        """Verify Stripe payment by session ID"""
        try:
            session = self.stripe.checkout.Session.retrieve(session_id)

            transaction = frappe.get_doc(
                "Payment Transaction",
                {"gateway_order_id": session_id}
            )

            if session.payment_status == "paid":
                transaction.gateway_payment_id = session.payment_intent
                transaction.status = "Success"
                transaction.payment_method = "Card"
                transaction.gateway_response = json.dumps({
                    "session_id": session.id,
                    "payment_intent": session.payment_intent,
                    "payment_status": session.payment_status
                })
                transaction.save(ignore_permissions=True)
                frappe.db.commit()

                return {"success": True, "transaction": transaction.name}
            else:
                transaction.status = "Failed"
                transaction.error_message = f"Payment status: {session.payment_status}"
                transaction.save(ignore_permissions=True)
                frappe.db.commit()

                return {"success": False, "error": "Payment not completed"}

        except Exception as e:
            frappe.log_error(f"Stripe verification failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}


# Factory function
def get_payment_gateway(gateway=None):
    """Get appropriate payment gateway instance"""
    settings = frappe.get_single("Payment Gateway Settings")
    gateway = gateway or settings.default_gateway

    if gateway == "Razorpay":
        return RazorpayGateway()
    elif gateway == "PayU":
        return PayUGateway()
    elif gateway == "Stripe":
        return StripeGateway()
    else:
        frappe.throw(_("Unsupported gateway: {0}").format(gateway))


# API Endpoints

@frappe.whitelist()
def initiate_payment(amount, student, gateway=None, reference_doctype=None, reference_name=None):
    """Initiate payment through configured gateway"""
    handler = get_payment_gateway(gateway)
    return handler.create_order(
        float(amount),
        student,
        reference_doctype,
        reference_name
    )


@frappe.whitelist()
def verify_payment(payment_data, gateway=None):
    """Verify payment from gateway"""
    if isinstance(payment_data, str):
        payment_data = json.loads(payment_data)

    handler = get_payment_gateway(gateway)
    return handler.verify_payment(payment_data)


@frappe.whitelist()
def process_refund(transaction_name, amount=None, reason=None):
    """Process refund for a transaction"""
    transaction = frappe.get_doc("Payment Transaction", transaction_name)
    handler = get_payment_gateway(transaction.payment_gateway)
    return handler.process_refund(transaction_name, amount, reason)


@frappe.whitelist(allow_guest=True)
def payment_callback():
    """Handle payment gateway callbacks"""
    data = dict(frappe.form_dict)

    try:
        # Determine gateway from data
        if "razorpay_order_id" in data:
            handler = RazorpayGateway()
            result = handler.verify_payment(data)
        elif "mihpayid" in data:
            handler = PayUGateway()
            result = handler.verify_payment(data)
        elif "session_id" in data:
            handler = StripeGateway()
            result = handler.verify_payment(data.get("session_id"))
        else:
            frappe.throw(_("Unknown payment gateway"))
            return

        settings = frappe.get_single("Payment Gateway Settings")

        if result.get("success"):
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = (
                settings.success_url + f"?transaction={result.get('transaction')}"
            )
        else:
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = (
                settings.failure_url + f"?error={result.get('error')}"
            )

    except Exception as e:
        frappe.log_error(f"Payment callback failed: {str(e)}", "Payment Gateway")
        settings = frappe.get_single("Payment Gateway Settings")
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = settings.failure_url + f"?error={str(e)}"


@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """Handle Razorpay webhooks"""
    try:
        payload = frappe.request.get_data()
        signature = frappe.request.headers.get("X-Razorpay-Signature")

        settings = frappe.get_single("Payment Gateway Settings")
        secret = settings.get_password("razorpay_webhook_secret")

        if not secret:
            return {"status": "error", "message": "Webhook secret not configured"}

        # Verify webhook signature
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if signature != expected_signature:
            frappe.log_error("Invalid webhook signature", "Razorpay Webhook")
            return {"status": "error", "message": "Invalid signature"}

        event = json.loads(payload)
        event_type = event.get("event")

        if event_type == "payment.captured":
            # Payment successful
            payment = event["payload"]["payment"]["entity"]
            order_id = payment.get("order_id")

            if order_id:
                transaction = frappe.db.get_value(
                    "Payment Transaction",
                    {"gateway_order_id": order_id},
                    "name"
                )

                if transaction:
                    txn = frappe.get_doc("Payment Transaction", transaction)
                    if txn.status != "Success":
                        txn.gateway_payment_id = payment["id"]
                        txn.status = "Success"
                        txn.payment_method = payment.get("method", "").capitalize()
                        txn.save(ignore_permissions=True)
                        frappe.db.commit()

        elif event_type == "payment.failed":
            # Payment failed
            payment = event["payload"]["payment"]["entity"]
            order_id = payment.get("order_id")

            if order_id:
                transaction = frappe.db.get_value(
                    "Payment Transaction",
                    {"gateway_order_id": order_id},
                    "name"
                )

                if transaction:
                    txn = frappe.get_doc("Payment Transaction", transaction)
                    if txn.status not in ["Success", "Refunded"]:
                        txn.status = "Failed"
                        txn.error_message = payment.get("error_description", "Payment failed")
                        txn.save(ignore_permissions=True)
                        frappe.db.commit()

        elif event_type == "refund.created":
            # Refund processed
            refund = event["payload"]["refund"]["entity"]
            payment_id = refund.get("payment_id")

            if payment_id:
                transaction = frappe.db.get_value(
                    "Payment Transaction",
                    {"gateway_payment_id": payment_id},
                    "name"
                )

                if transaction:
                    txn = frappe.get_doc("Payment Transaction", transaction)
                    txn.refund_id = refund["id"]
                    txn.refund_amount = refund["amount"] / 100  # Convert paise to rupees
                    txn.refund_date = frappe.utils.now_datetime()
                    txn.refund_status = "Processed"

                    if txn.refund_amount >= txn.amount:
                        txn.status = "Refunded"
                    else:
                        txn.status = "Partially Refunded"

                    txn.save(ignore_permissions=True)
                    frappe.db.commit()

        return {"status": "ok"}

    except Exception as e:
        frappe.log_error(f"Webhook processing failed: {str(e)}", "Razorpay Webhook")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_payment_status(transaction_name):
    """Get payment status for a transaction"""
    transaction = frappe.get_doc("Payment Transaction", transaction_name)

    return {
        "status": transaction.status,
        "amount": transaction.amount,
        "payment_gateway": transaction.payment_gateway,
        "gateway_payment_id": transaction.gateway_payment_id,
        "transaction_date": transaction.transaction_date,
        "error_message": transaction.error_message
    }
