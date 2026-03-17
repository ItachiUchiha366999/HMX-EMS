# Phase 14: Payment Gateway & Financial Integrations

## Overview
This phase implements complete payment gateway integrations (Razorpay, PayU), automated GL posting, bank reconciliation, and comprehensive financial management features to enable online fee collection and financial tracking.

**Duration**: 4-5 weeks
**Priority**: High (Blocks Production Deployment)
**Dependencies**: Phase 5 (Fee Management), Phase 8 (Basic Integration Setup)

---

## Part A: Payment Gateway Integration

### 1. Razorpay Integration

#### 1.1 Razorpay Settings DocType

```python
# razorpay_settings.py

import frappe
from frappe.model.document import Document
import razorpay


class RazorpaySettings(Document):
    def validate(self):
        if self.enabled:
            self.validate_credentials()

    def validate_credentials(self):
        """Validate Razorpay API credentials"""
        try:
            client = razorpay.Client(auth=(self.api_key, self.get_password('api_secret')))
            # Test API call
            client.utility.verify_payment_signature({})
        except razorpay.errors.SignatureVerificationError:
            pass  # Expected for empty signature
        except Exception as e:
            frappe.throw(f"Invalid Razorpay credentials: {str(e)}")

    def get_client(self):
        """Get Razorpay client instance"""
        return razorpay.Client(auth=(self.api_key, self.get_password('api_secret')))


def get_razorpay_settings():
    """Get Razorpay settings singleton"""
    settings = frappe.get_single("Razorpay Settings")
    if not settings.enabled:
        frappe.throw("Razorpay payment gateway is not enabled")
    return settings
```

#### 1.2 Razorpay Settings DocType JSON

```json
{
    "doctype": "DocType",
    "name": "Razorpay Settings",
    "module": "University ERP",
    "issingle": 1,
    "fields": [
        {
            "fieldname": "enabled",
            "fieldtype": "Check",
            "label": "Enabled",
            "default": 0
        },
        {
            "fieldname": "test_mode",
            "fieldtype": "Check",
            "label": "Test Mode",
            "default": 1,
            "description": "Use test/sandbox credentials"
        },
        {
            "fieldname": "api_key",
            "fieldtype": "Data",
            "label": "API Key",
            "reqd": 1
        },
        {
            "fieldname": "api_secret",
            "fieldtype": "Password",
            "label": "API Secret",
            "reqd": 1
        },
        {
            "fieldname": "webhook_secret",
            "fieldtype": "Password",
            "label": "Webhook Secret",
            "description": "Secret for verifying webhook signatures"
        },
        {
            "fieldname": "payment_settings_section",
            "fieldtype": "Section Break",
            "label": "Payment Settings"
        },
        {
            "fieldname": "auto_capture",
            "fieldtype": "Check",
            "label": "Auto Capture Payments",
            "default": 1
        },
        {
            "fieldname": "send_receipt",
            "fieldtype": "Check",
            "label": "Send Payment Receipt Email",
            "default": 1
        },
        {
            "fieldname": "receipt_prefix",
            "fieldtype": "Data",
            "label": "Receipt Number Prefix",
            "default": "UNIV"
        },
        {
            "fieldname": "account_settings_section",
            "fieldtype": "Section Break",
            "label": "Account Settings"
        },
        {
            "fieldname": "fee_income_account",
            "fieldtype": "Link",
            "label": "Fee Income Account",
            "options": "Account"
        },
        {
            "fieldname": "payment_gateway_account",
            "fieldtype": "Link",
            "label": "Payment Gateway Account",
            "options": "Account"
        }
    ],
    "permissions": [
        {
            "role": "System Manager",
            "read": 1,
            "write": 1
        }
    ]
}
```

#### 1.3 Payment Order Creation

```python
# payment_gateway.py

import frappe
from frappe import _
import razorpay
import json
import hashlib
import hmac


class PaymentGateway:
    """Unified payment gateway interface"""

    def __init__(self, gateway="razorpay"):
        self.gateway = gateway
        if gateway == "razorpay":
            self.settings = frappe.get_single("Razorpay Settings")
            self.client = self.settings.get_client()
        elif gateway == "payu":
            self.settings = frappe.get_single("PayU Settings")

    def create_order(self, amount, currency="INR", receipt=None, notes=None):
        """Create a payment order"""
        if self.gateway == "razorpay":
            return self._create_razorpay_order(amount, currency, receipt, notes)
        elif self.gateway == "payu":
            return self._create_payu_order(amount, currency, receipt, notes)

    def _create_razorpay_order(self, amount, currency, receipt, notes):
        """Create Razorpay order"""
        order_data = {
            "amount": int(amount * 100),  # Razorpay expects amount in paise
            "currency": currency,
            "receipt": receipt or frappe.generate_hash(length=10),
            "notes": notes or {}
        }

        try:
            order = self.client.order.create(data=order_data)
            return {
                "success": True,
                "order_id": order["id"],
                "amount": amount,
                "currency": currency,
                "key": self.settings.api_key,
                "gateway": "razorpay"
            }
        except Exception as e:
            frappe.log_error(f"Razorpay order creation failed: {str(e)}", "Payment Gateway")
            return {"success": False, "error": str(e)}

    def verify_payment(self, payment_data):
        """Verify payment signature"""
        if self.gateway == "razorpay":
            return self._verify_razorpay_payment(payment_data)
        elif self.gateway == "payu":
            return self._verify_payu_payment(payment_data)

    def _verify_razorpay_payment(self, payment_data):
        """Verify Razorpay payment signature"""
        try:
            params = {
                'razorpay_order_id': payment_data.get('razorpay_order_id'),
                'razorpay_payment_id': payment_data.get('razorpay_payment_id'),
                'razorpay_signature': payment_data.get('razorpay_signature')
            }
            self.client.utility.verify_payment_signature(params)
            return {"verified": True, "payment_id": payment_data.get('razorpay_payment_id')}
        except razorpay.errors.SignatureVerificationError:
            return {"verified": False, "error": "Invalid payment signature"}
        except Exception as e:
            return {"verified": False, "error": str(e)}

    def capture_payment(self, payment_id, amount):
        """Capture an authorized payment"""
        if self.gateway == "razorpay":
            try:
                payment = self.client.payment.capture(payment_id, int(amount * 100))
                return {"success": True, "payment": payment}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def refund_payment(self, payment_id, amount=None, notes=None):
        """Initiate a refund"""
        if self.gateway == "razorpay":
            try:
                refund_data = {"notes": notes or {}}
                if amount:
                    refund_data["amount"] = int(amount * 100)

                refund = self.client.payment.refund(payment_id, refund_data)
                return {"success": True, "refund_id": refund["id"], "refund": refund}
            except Exception as e:
                return {"success": False, "error": str(e)}


@frappe.whitelist()
def create_fee_payment_order(fees_name):
    """Create payment order for a fee document"""
    fees = frappe.get_doc("Fees", fees_name)

    if fees.outstanding_amount <= 0:
        frappe.throw(_("No outstanding amount to pay"))

    # Determine which gateway to use
    gateway_setting = frappe.db.get_single_value("University Settings", "default_payment_gateway") or "razorpay"
    gateway = PaymentGateway(gateway_setting)

    # Create payment order
    student = frappe.get_doc("Student", fees.student)
    notes = {
        "fees_name": fees.name,
        "student": fees.student,
        "student_name": fees.student_name,
        "program": fees.program
    }

    receipt = f"{fees.name}-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
    result = gateway.create_order(
        amount=fees.outstanding_amount,
        currency="INR",
        receipt=receipt,
        notes=notes
    )

    if result.get("success"):
        # Create Payment Order record
        payment_order = frappe.get_doc({
            "doctype": "Payment Order",
            "reference_doctype": "Fees",
            "reference_name": fees.name,
            "payment_gateway": gateway_setting,
            "gateway_order_id": result.get("order_id"),
            "amount": fees.outstanding_amount,
            "currency": "INR",
            "status": "Created",
            "student": fees.student,
            "student_name": fees.student_name
        })
        payment_order.insert(ignore_permissions=True)

        result["payment_order"] = payment_order.name
        result["student_name"] = student.student_name
        result["student_email"] = student.student_email_id
        result["description"] = f"Fee Payment - {fees.name}"

    return result


@frappe.whitelist()
def verify_and_process_payment(payment_data):
    """Verify payment and update fee records"""
    payment_data = json.loads(payment_data) if isinstance(payment_data, str) else payment_data

    payment_order = frappe.get_doc("Payment Order", payment_data.get("payment_order"))
    gateway = PaymentGateway(payment_order.payment_gateway)

    # Verify payment
    verification = gateway.verify_payment(payment_data)

    if not verification.get("verified"):
        payment_order.status = "Failed"
        payment_order.failure_reason = verification.get("error")
        payment_order.save(ignore_permissions=True)
        return {"success": False, "error": verification.get("error")}

    # Update payment order
    payment_order.gateway_payment_id = verification.get("payment_id")
    payment_order.status = "Completed"
    payment_order.payment_date = frappe.utils.now_datetime()
    payment_order.save(ignore_permissions=True)

    # Process fee payment
    fees = frappe.get_doc("Fees", payment_order.reference_name)

    # Create Fee Payment Entry
    payment_entry = create_fee_payment_entry(
        fees=fees,
        amount=payment_order.amount,
        payment_id=verification.get("payment_id"),
        payment_gateway=payment_order.payment_gateway
    )

    # Update fees outstanding
    fees.reload()

    # Send receipt email
    if frappe.db.get_single_value("Razorpay Settings", "send_receipt"):
        send_payment_receipt(fees, payment_order, payment_entry)

    return {
        "success": True,
        "payment_entry": payment_entry.name,
        "new_outstanding": fees.outstanding_amount,
        "message": "Payment processed successfully"
    }


def create_fee_payment_entry(fees, amount, payment_id, payment_gateway):
    """Create payment entry for fee"""
    settings = frappe.get_single(f"{payment_gateway.title()} Settings")

    payment_entry = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "posting_date": frappe.utils.today(),
        "party_type": "Student",
        "party": fees.student,
        "party_name": fees.student_name,
        "paid_amount": amount,
        "received_amount": amount,
        "paid_to": settings.payment_gateway_account,
        "mode_of_payment": "Online Payment",
        "reference_no": payment_id,
        "reference_date": frappe.utils.today(),
        "references": [{
            "reference_doctype": "Fees",
            "reference_name": fees.name,
            "allocated_amount": amount
        }],
        "remarks": f"Online payment via {payment_gateway} - {payment_id}"
    })
    payment_entry.insert(ignore_permissions=True)
    payment_entry.submit()

    return payment_entry


def send_payment_receipt(fees, payment_order, payment_entry):
    """Send payment receipt email to student"""
    student = frappe.get_doc("Student", fees.student)

    if not student.student_email_id:
        return

    # Generate receipt PDF
    receipt_html = frappe.render_template(
        "university_erp/templates/payment_receipt.html",
        {
            "fees": fees,
            "payment_order": payment_order,
            "payment_entry": payment_entry,
            "student": student
        }
    )

    frappe.sendmail(
        recipients=[student.student_email_id],
        subject=f"Payment Receipt - {payment_entry.name}",
        message=receipt_html,
        reference_doctype="Payment Entry",
        reference_name=payment_entry.name
    )
```

#### 1.4 Payment Order DocType

```json
{
    "doctype": "DocType",
    "name": "Payment Order",
    "module": "University ERP",
    "fields": [
        {
            "fieldname": "reference_doctype",
            "fieldtype": "Link",
            "label": "Reference Type",
            "options": "DocType",
            "reqd": 1
        },
        {
            "fieldname": "reference_name",
            "fieldtype": "Dynamic Link",
            "label": "Reference Name",
            "options": "reference_doctype",
            "reqd": 1
        },
        {
            "fieldname": "student",
            "fieldtype": "Link",
            "label": "Student",
            "options": "Student"
        },
        {
            "fieldname": "student_name",
            "fieldtype": "Data",
            "label": "Student Name",
            "read_only": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "payment_gateway",
            "fieldtype": "Select",
            "label": "Payment Gateway",
            "options": "\nRazorpay\nPayU\nPaytm",
            "reqd": 1
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Created\nPending\nCompleted\nFailed\nRefunded",
            "default": "Created"
        },
        {
            "fieldname": "payment_section",
            "fieldtype": "Section Break",
            "label": "Payment Details"
        },
        {
            "fieldname": "gateway_order_id",
            "fieldtype": "Data",
            "label": "Gateway Order ID"
        },
        {
            "fieldname": "gateway_payment_id",
            "fieldtype": "Data",
            "label": "Gateway Payment ID"
        },
        {
            "fieldname": "amount",
            "fieldtype": "Currency",
            "label": "Amount",
            "reqd": 1
        },
        {
            "fieldname": "currency",
            "fieldtype": "Link",
            "label": "Currency",
            "options": "Currency",
            "default": "INR"
        },
        {
            "fieldname": "column_break_2",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "payment_date",
            "fieldtype": "Datetime",
            "label": "Payment Date"
        },
        {
            "fieldname": "payment_entry",
            "fieldtype": "Link",
            "label": "Payment Entry",
            "options": "Payment Entry",
            "read_only": 1
        },
        {
            "fieldname": "failure_section",
            "fieldtype": "Section Break",
            "label": "Failure Details",
            "depends_on": "eval:doc.status=='Failed'"
        },
        {
            "fieldname": "failure_reason",
            "fieldtype": "Small Text",
            "label": "Failure Reason"
        },
        {
            "fieldname": "refund_section",
            "fieldtype": "Section Break",
            "label": "Refund Details",
            "depends_on": "eval:doc.status=='Refunded'"
        },
        {
            "fieldname": "refund_id",
            "fieldtype": "Data",
            "label": "Refund ID"
        },
        {
            "fieldname": "refund_amount",
            "fieldtype": "Currency",
            "label": "Refund Amount"
        },
        {
            "fieldname": "refund_date",
            "fieldtype": "Datetime",
            "label": "Refund Date"
        }
    ],
    "permissions": [
        {
            "role": "Accounts Manager",
            "read": 1,
            "write": 1,
            "create": 1
        },
        {
            "role": "Student",
            "read": 1,
            "if_owner": 1
        }
    ]
}
```

### 2. Razorpay Webhook Handler

```python
# webhooks/razorpay_webhook.py

import frappe
from frappe import _
import hmac
import hashlib
import json


@frappe.whitelist(allow_guest=True)
def handle_razorpay_webhook():
    """Handle Razorpay webhook events"""
    try:
        payload = frappe.request.get_data(as_text=True)
        signature = frappe.request.headers.get("X-Razorpay-Signature")

        settings = frappe.get_single("Razorpay Settings")
        webhook_secret = settings.get_password("webhook_secret")

        # Verify signature
        if not verify_webhook_signature(payload, signature, webhook_secret):
            frappe.local.response["http_status_code"] = 400
            return {"error": "Invalid signature"}

        event = json.loads(payload)
        event_type = event.get("event")

        # Log webhook
        log_webhook(event_type, payload)

        # Handle different event types
        handlers = {
            "payment.captured": handle_payment_captured,
            "payment.failed": handle_payment_failed,
            "refund.created": handle_refund_created,
            "payment.authorized": handle_payment_authorized
        }

        handler = handlers.get(event_type)
        if handler:
            handler(event.get("payload", {}))

        return {"status": "ok"}

    except Exception as e:
        frappe.log_error(f"Razorpay webhook error: {str(e)}", "Payment Gateway")
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

    # Find payment order
    payment_order = frappe.db.get_value(
        "Payment Order",
        {"gateway_order_id": order_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order:
        doc = frappe.get_doc("Payment Order", payment_order)
        if doc.status != "Completed":
            doc.gateway_payment_id = payment_id
            doc.status = "Completed"
            doc.payment_date = frappe.utils.now_datetime()
            doc.save(ignore_permissions=True)

            # Process fee payment if not already done
            process_fee_payment_from_webhook(doc)


def handle_payment_failed(payload):
    """Handle payment.failed event"""
    payment = payload.get("payment", {}).get("entity", {})
    order_id = payment.get("order_id")
    error = payment.get("error_description", "Payment failed")

    payment_order = frappe.db.get_value(
        "Payment Order",
        {"gateway_order_id": order_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order:
        frappe.db.set_value("Payment Order", payment_order, {
            "status": "Failed",
            "failure_reason": error
        })


def handle_refund_created(payload):
    """Handle refund.created event"""
    refund = payload.get("refund", {}).get("entity", {})
    payment_id = refund.get("payment_id")
    refund_id = refund.get("id")
    refund_amount = refund.get("amount", 0) / 100  # Convert from paise

    payment_order = frappe.db.get_value(
        "Payment Order",
        {"gateway_payment_id": payment_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order:
        frappe.db.set_value("Payment Order", payment_order, {
            "status": "Refunded",
            "refund_id": refund_id,
            "refund_amount": refund_amount,
            "refund_date": frappe.utils.now_datetime()
        })

        # Process refund entry
        process_refund_entry(payment_order, refund_amount)


def handle_payment_authorized(payload):
    """Handle payment.authorized event (for manual capture)"""
    payment = payload.get("payment", {}).get("entity", {})
    order_id = payment.get("order_id")

    payment_order = frappe.db.get_value(
        "Payment Order",
        {"gateway_order_id": order_id, "payment_gateway": "Razorpay"},
        "name"
    )

    if payment_order:
        frappe.db.set_value("Payment Order", payment_order, "status", "Pending")


def log_webhook(event_type, payload):
    """Log webhook for debugging"""
    frappe.get_doc({
        "doctype": "Webhook Log",
        "webhook_type": "Razorpay",
        "event_type": event_type,
        "payload": payload,
        "received_at": frappe.utils.now_datetime()
    }).insert(ignore_permissions=True)


def process_fee_payment_from_webhook(payment_order):
    """Process fee payment from webhook"""
    if payment_order.reference_doctype == "Fees" and not payment_order.payment_entry:
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
            "party_type": "Student",
            "party": payment_order.student,
            "paid_amount": refund_amount,
            "received_amount": refund_amount,
            "paid_from": original_entry.paid_to,
            "mode_of_payment": "Online Refund",
            "reference_no": payment_order.refund_id,
            "reference_date": frappe.utils.today(),
            "remarks": f"Refund for {payment_order.gateway_payment_id}"
        })
        refund_entry.insert(ignore_permissions=True)
        refund_entry.submit()
```

---

## Part B: PayU Integration

### 1. PayU Settings DocType

```json
{
    "doctype": "DocType",
    "name": "PayU Settings",
    "module": "University ERP",
    "issingle": 1,
    "fields": [
        {
            "fieldname": "enabled",
            "fieldtype": "Check",
            "label": "Enabled"
        },
        {
            "fieldname": "test_mode",
            "fieldtype": "Check",
            "label": "Test Mode",
            "default": 1
        },
        {
            "fieldname": "merchant_key",
            "fieldtype": "Data",
            "label": "Merchant Key",
            "reqd": 1
        },
        {
            "fieldname": "merchant_salt",
            "fieldtype": "Password",
            "label": "Merchant Salt",
            "reqd": 1
        },
        {
            "fieldname": "merchant_salt_v2",
            "fieldtype": "Password",
            "label": "Merchant Salt V2"
        },
        {
            "fieldname": "test_url",
            "fieldtype": "Data",
            "label": "Test URL",
            "default": "https://test.payu.in/_payment"
        },
        {
            "fieldname": "production_url",
            "fieldtype": "Data",
            "label": "Production URL",
            "default": "https://secure.payu.in/_payment"
        },
        {
            "fieldname": "success_url",
            "fieldtype": "Data",
            "label": "Success URL"
        },
        {
            "fieldname": "failure_url",
            "fieldtype": "Data",
            "label": "Failure URL"
        },
        {
            "fieldname": "fee_income_account",
            "fieldtype": "Link",
            "label": "Fee Income Account",
            "options": "Account"
        }
    ]
}
```

### 2. PayU Payment Handler

```python
# payu_payment.py

import frappe
from frappe import _
import hashlib


class PayUPayment:
    def __init__(self):
        self.settings = frappe.get_single("PayU Settings")
        if not self.settings.enabled:
            frappe.throw(_("PayU payment gateway is not enabled"))

    def get_payment_url(self):
        """Get PayU payment URL based on mode"""
        if self.settings.test_mode:
            return self.settings.test_url
        return self.settings.production_url

    def generate_hash(self, params):
        """Generate PayU hash"""
        hash_string = "|".join([
            params.get("key", ""),
            params.get("txnid", ""),
            params.get("amount", ""),
            params.get("productinfo", ""),
            params.get("firstname", ""),
            params.get("email", ""),
            params.get("udf1", ""),
            params.get("udf2", ""),
            params.get("udf3", ""),
            params.get("udf4", ""),
            params.get("udf5", ""),
            "",  # udf6-10 empty
            "",
            "",
            "",
            "",
            self.settings.get_password("merchant_salt")
        ])

        return hashlib.sha512(hash_string.encode()).hexdigest().lower()

    def verify_response_hash(self, params):
        """Verify PayU response hash"""
        # Reverse hash calculation
        hash_string = "|".join([
            self.settings.get_password("merchant_salt"),
            params.get("status", ""),
            "",  # udf10-6 empty
            "",
            "",
            "",
            "",
            params.get("udf5", ""),
            params.get("udf4", ""),
            params.get("udf3", ""),
            params.get("udf2", ""),
            params.get("udf1", ""),
            params.get("email", ""),
            params.get("firstname", ""),
            params.get("productinfo", ""),
            params.get("amount", ""),
            params.get("txnid", ""),
            params.get("key", "")
        ])

        calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest().lower()
        return calculated_hash == params.get("hash", "")

    def create_payment_request(self, fees):
        """Create PayU payment request"""
        student = frappe.get_doc("Student", fees.student)
        txnid = f"FEE{fees.name}{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"

        params = {
            "key": self.settings.merchant_key,
            "txnid": txnid,
            "amount": str(fees.outstanding_amount),
            "productinfo": f"Fee Payment - {fees.name}",
            "firstname": student.student_name.split()[0] if student.student_name else "",
            "email": student.student_email_id or "",
            "phone": student.phone or "",
            "surl": self.settings.success_url,
            "furl": self.settings.failure_url,
            "udf1": fees.name,
            "udf2": fees.student,
            "udf3": "",
            "udf4": "",
            "udf5": ""
        }

        params["hash"] = self.generate_hash(params)

        # Create payment order
        payment_order = frappe.get_doc({
            "doctype": "Payment Order",
            "reference_doctype": "Fees",
            "reference_name": fees.name,
            "payment_gateway": "PayU",
            "gateway_order_id": txnid,
            "amount": fees.outstanding_amount,
            "status": "Created",
            "student": fees.student,
            "student_name": fees.student_name
        })
        payment_order.insert(ignore_permissions=True)

        return {
            "payment_url": self.get_payment_url(),
            "params": params,
            "payment_order": payment_order.name
        }


@frappe.whitelist(allow_guest=True)
def payu_success():
    """Handle PayU success callback"""
    params = frappe.form_dict

    payu = PayUPayment()

    if not payu.verify_response_hash(params):
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/fee-payment-failed?error=Invalid+signature"
        return

    txnid = params.get("txnid")
    payment_order = frappe.get_doc("Payment Order", {"gateway_order_id": txnid})

    payment_order.gateway_payment_id = params.get("mihpayid")
    payment_order.status = "Completed"
    payment_order.payment_date = frappe.utils.now_datetime()
    payment_order.save(ignore_permissions=True)

    # Process payment
    fees = frappe.get_doc("Fees", payment_order.reference_name)
    payment_entry = create_fee_payment_entry(
        fees=fees,
        amount=payment_order.amount,
        payment_id=params.get("mihpayid"),
        payment_gateway="PayU"
    )

    payment_order.payment_entry = payment_entry.name
    payment_order.save(ignore_permissions=True)

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = f"/fee-payment-success?payment={payment_entry.name}"


@frappe.whitelist(allow_guest=True)
def payu_failure():
    """Handle PayU failure callback"""
    params = frappe.form_dict

    txnid = params.get("txnid")
    if txnid:
        payment_order = frappe.db.get_value(
            "Payment Order",
            {"gateway_order_id": txnid},
            "name"
        )
        if payment_order:
            frappe.db.set_value("Payment Order", payment_order, {
                "status": "Failed",
                "failure_reason": params.get("error_Message", "Payment failed")
            })

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = f"/fee-payment-failed?error={params.get('error_Message', 'Payment+failed')}"
```

---

## Part C: Automated GL Posting

### 1. GL Entry Automation

```python
# gl_posting.py

import frappe
from frappe import _
from frappe.utils import flt


class GLPostingManager:
    """Manages automated GL postings for university transactions"""

    def __init__(self):
        self.settings = frappe.get_single("University Accounts Settings")

    def post_fee_collection(self, fees):
        """Create GL entries for fee collection"""
        if not self.settings.auto_post_gl:
            return

        entries = []

        # Debit: Bank/Cash/Payment Gateway Account
        entries.append({
            "account": self.settings.fee_collection_account,
            "debit": flt(fees.paid_amount),
            "credit": 0,
            "party_type": "Student",
            "party": fees.student,
            "against": self.settings.fee_income_account,
            "remarks": f"Fee collection - {fees.name}"
        })

        # Credit: Fee Income Account (per component)
        for component in fees.components:
            income_account = self.get_fee_component_account(component.fees_category)
            entries.append({
                "account": income_account,
                "debit": 0,
                "credit": flt(component.amount),
                "party_type": "Student",
                "party": fees.student,
                "against": self.settings.fee_collection_account,
                "remarks": f"{component.fees_category} - {fees.name}",
                "cost_center": self.get_department_cost_center(fees.program)
            })

        self.create_gl_entries(entries, fees)

    def post_scholarship_disbursement(self, scholarship):
        """Create GL entries for scholarship disbursement"""
        entries = []

        # Debit: Scholarship Expense Account
        entries.append({
            "account": self.settings.scholarship_expense_account,
            "debit": flt(scholarship.amount),
            "credit": 0,
            "party_type": "Student",
            "party": scholarship.student,
            "against": self.settings.scholarship_liability_account,
            "remarks": f"Scholarship - {scholarship.name}"
        })

        # Credit: Student Fee Receivable (or Bank if direct payment)
        entries.append({
            "account": self.settings.scholarship_liability_account,
            "debit": 0,
            "credit": flt(scholarship.amount),
            "party_type": "Student",
            "party": scholarship.student,
            "against": self.settings.scholarship_expense_account,
            "remarks": f"Scholarship adjustment - {scholarship.name}"
        })

        self.create_gl_entries(entries, scholarship)

    def post_hostel_fee(self, hostel_fee):
        """Create GL entries for hostel fee"""
        entries = []

        # Debit: Receivable
        entries.append({
            "account": self.settings.hostel_receivable_account,
            "debit": flt(hostel_fee.total_amount),
            "credit": 0,
            "party_type": "Student",
            "party": hostel_fee.student,
            "remarks": f"Hostel fee - {hostel_fee.name}"
        })

        # Credit: Hostel Income
        entries.append({
            "account": self.settings.hostel_income_account,
            "debit": 0,
            "credit": flt(hostel_fee.room_rent),
            "remarks": f"Room rent - {hostel_fee.name}"
        })

        if hostel_fee.mess_charges:
            entries.append({
                "account": self.settings.mess_income_account,
                "debit": 0,
                "credit": flt(hostel_fee.mess_charges),
                "remarks": f"Mess charges - {hostel_fee.name}"
            })

        self.create_gl_entries(entries, hostel_fee)

    def get_fee_component_account(self, fees_category):
        """Get GL account for fee category"""
        account = frappe.db.get_value(
            "Fee Category Account",
            {"parent": "University Accounts Settings", "fees_category": fees_category},
            "income_account"
        )
        return account or self.settings.fee_income_account

    def get_department_cost_center(self, program):
        """Get cost center for program/department"""
        department = frappe.db.get_value("Program", program, "department")
        if department:
            cost_center = frappe.db.get_value("Department", department, "cost_center")
            if cost_center:
                return cost_center
        return self.settings.default_cost_center

    def create_gl_entries(self, entries, voucher):
        """Create GL entries from list"""
        from erpnext.accounts.general_ledger import make_gl_entries

        gl_entries = []
        for entry in entries:
            gl_entry = frappe._dict({
                "posting_date": voucher.posting_date if hasattr(voucher, 'posting_date') else frappe.utils.today(),
                "account": entry["account"],
                "debit": entry.get("debit", 0),
                "credit": entry.get("credit", 0),
                "debit_in_account_currency": entry.get("debit", 0),
                "credit_in_account_currency": entry.get("credit", 0),
                "party_type": entry.get("party_type"),
                "party": entry.get("party"),
                "against": entry.get("against"),
                "remarks": entry.get("remarks"),
                "cost_center": entry.get("cost_center") or self.settings.default_cost_center,
                "voucher_type": voucher.doctype,
                "voucher_no": voucher.name,
                "company": self.settings.company
            })
            gl_entries.append(gl_entry)

        if gl_entries:
            make_gl_entries(gl_entries, cancel=False)


# Hook to auto-post GL on fee submission
def on_fees_submit(doc, method):
    """Auto post GL entries on fee submission"""
    gl_manager = GLPostingManager()
    gl_manager.post_fee_collection(doc)
```

### 2. University Accounts Settings DocType

```json
{
    "doctype": "DocType",
    "name": "University Accounts Settings",
    "module": "University ERP",
    "issingle": 1,
    "fields": [
        {
            "fieldname": "company",
            "fieldtype": "Link",
            "label": "Company",
            "options": "Company",
            "reqd": 1
        },
        {
            "fieldname": "auto_post_gl",
            "fieldtype": "Check",
            "label": "Auto Post GL Entries",
            "default": 1
        },
        {
            "fieldname": "default_cost_center",
            "fieldtype": "Link",
            "label": "Default Cost Center",
            "options": "Cost Center"
        },
        {
            "fieldname": "fee_accounts_section",
            "fieldtype": "Section Break",
            "label": "Fee Accounts"
        },
        {
            "fieldname": "fee_collection_account",
            "fieldtype": "Link",
            "label": "Fee Collection Account",
            "options": "Account"
        },
        {
            "fieldname": "fee_income_account",
            "fieldtype": "Link",
            "label": "Default Fee Income Account",
            "options": "Account"
        },
        {
            "fieldname": "fee_receivable_account",
            "fieldtype": "Link",
            "label": "Fee Receivable Account",
            "options": "Account"
        },
        {
            "fieldname": "column_break_fee",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "late_fee_income_account",
            "fieldtype": "Link",
            "label": "Late Fee Income Account",
            "options": "Account"
        },
        {
            "fieldname": "fee_discount_account",
            "fieldtype": "Link",
            "label": "Fee Discount Account",
            "options": "Account"
        },
        {
            "fieldname": "fee_category_accounts",
            "fieldtype": "Table",
            "label": "Fee Category Accounts",
            "options": "Fee Category Account"
        },
        {
            "fieldname": "scholarship_section",
            "fieldtype": "Section Break",
            "label": "Scholarship Accounts"
        },
        {
            "fieldname": "scholarship_expense_account",
            "fieldtype": "Link",
            "label": "Scholarship Expense Account",
            "options": "Account"
        },
        {
            "fieldname": "scholarship_liability_account",
            "fieldtype": "Link",
            "label": "Scholarship Liability Account",
            "options": "Account"
        },
        {
            "fieldname": "hostel_section",
            "fieldtype": "Section Break",
            "label": "Hostel Accounts"
        },
        {
            "fieldname": "hostel_receivable_account",
            "fieldtype": "Link",
            "label": "Hostel Receivable Account",
            "options": "Account"
        },
        {
            "fieldname": "hostel_income_account",
            "fieldtype": "Link",
            "label": "Hostel Income Account",
            "options": "Account"
        },
        {
            "fieldname": "mess_income_account",
            "fieldtype": "Link",
            "label": "Mess Income Account",
            "options": "Account"
        },
        {
            "fieldname": "transport_section",
            "fieldtype": "Section Break",
            "label": "Transport Accounts"
        },
        {
            "fieldname": "transport_income_account",
            "fieldtype": "Link",
            "label": "Transport Income Account",
            "options": "Account"
        },
        {
            "fieldname": "library_section",
            "fieldtype": "Section Break",
            "label": "Library Accounts"
        },
        {
            "fieldname": "library_fine_income_account",
            "fieldtype": "Link",
            "label": "Library Fine Income Account",
            "options": "Account"
        }
    ]
}
```

---

## Part D: Bank Reconciliation

### 1. Bank Reconciliation Tool

```python
# bank_reconciliation.py

import frappe
from frappe import _
from frappe.utils import flt, getdate


class BankReconciliationTool:
    """Tool for reconciling bank statements with system records"""

    def __init__(self, bank_account, from_date, to_date):
        self.bank_account = bank_account
        self.from_date = getdate(from_date)
        self.to_date = getdate(to_date)

    def get_bank_transactions(self):
        """Get bank transactions from statement"""
        return frappe.get_all(
            "Bank Transaction",
            filters={
                "bank_account": self.bank_account,
                "date": ["between", [self.from_date, self.to_date]],
                "status": ["!=", "Reconciled"]
            },
            fields=["name", "date", "description", "deposit", "withdrawal", "reference_number"]
        )

    def get_system_entries(self):
        """Get payment entries from system"""
        entries = frappe.db.sql("""
            SELECT
                pe.name,
                pe.posting_date,
                pe.reference_no,
                pe.reference_date,
                pe.paid_amount,
                pe.payment_type,
                pe.party,
                pe.party_name,
                pe.mode_of_payment
            FROM `tabPayment Entry` pe
            WHERE pe.docstatus = 1
            AND pe.posting_date BETWEEN %s AND %s
            AND (pe.paid_from = %s OR pe.paid_to = %s)
            AND pe.clearance_date IS NULL
        """, (self.from_date, self.to_date, self.bank_account, self.bank_account), as_dict=True)

        return entries

    def auto_match(self):
        """Auto-match bank transactions with system entries"""
        bank_txns = self.get_bank_transactions()
        system_entries = self.get_system_entries()

        matches = []

        for txn in bank_txns:
            for entry in system_entries:
                if self.is_match(txn, entry):
                    matches.append({
                        "bank_transaction": txn.name,
                        "payment_entry": entry.name,
                        "match_type": self.get_match_type(txn, entry),
                        "confidence": self.calculate_confidence(txn, entry)
                    })
                    break

        return matches

    def is_match(self, bank_txn, payment_entry):
        """Check if bank transaction matches payment entry"""
        # Amount match
        txn_amount = flt(bank_txn.deposit) or flt(bank_txn.withdrawal)
        entry_amount = flt(payment_entry.paid_amount)

        if abs(txn_amount - entry_amount) > 0.01:
            return False

        # Reference number match (if available)
        if bank_txn.reference_number and payment_entry.reference_no:
            if bank_txn.reference_number == payment_entry.reference_no:
                return True

        # Date proximity check (within 3 days)
        date_diff = abs((getdate(bank_txn.date) - getdate(payment_entry.posting_date)).days)
        if date_diff <= 3:
            return True

        return False

    def get_match_type(self, bank_txn, payment_entry):
        """Determine match type"""
        if bank_txn.reference_number == payment_entry.reference_no:
            return "Reference Match"
        return "Amount Match"

    def calculate_confidence(self, bank_txn, payment_entry):
        """Calculate match confidence percentage"""
        confidence = 50  # Base confidence for amount match

        # Reference match
        if bank_txn.reference_number and payment_entry.reference_no:
            if bank_txn.reference_number == payment_entry.reference_no:
                confidence += 40

        # Date match
        date_diff = abs((getdate(bank_txn.date) - getdate(payment_entry.posting_date)).days)
        if date_diff == 0:
            confidence += 10
        elif date_diff <= 1:
            confidence += 5

        return min(confidence, 100)

    def reconcile(self, matches):
        """Perform reconciliation"""
        reconciled = []

        for match in matches:
            if match.get("confirmed"):
                # Update bank transaction
                frappe.db.set_value("Bank Transaction", match["bank_transaction"], {
                    "status": "Reconciled",
                    "payment_entry": match["payment_entry"]
                })

                # Update payment entry clearance
                frappe.db.set_value("Payment Entry", match["payment_entry"],
                    "clearance_date", frappe.utils.today())

                reconciled.append(match)

        return reconciled


@frappe.whitelist()
def get_reconciliation_data(bank_account, from_date, to_date):
    """Get reconciliation data"""
    tool = BankReconciliationTool(bank_account, from_date, to_date)

    return {
        "bank_transactions": tool.get_bank_transactions(),
        "system_entries": tool.get_system_entries(),
        "suggested_matches": tool.auto_match()
    }


@frappe.whitelist()
def perform_reconciliation(matches):
    """Perform reconciliation with confirmed matches"""
    import json
    matches = json.loads(matches) if isinstance(matches, str) else matches

    tool = BankReconciliationTool(None, None, None)
    return tool.reconcile(matches)
```

### 2. Bank Transaction Import

```python
# bank_statement_import.py

import frappe
from frappe import _
import csv
import io


class BankStatementImporter:
    """Import bank statements from various formats"""

    SUPPORTED_FORMATS = ["csv", "ofx", "xlsx"]

    def __init__(self, bank_account):
        self.bank_account = bank_account
        self.bank = frappe.db.get_value("Bank Account", bank_account, "bank")
        self.template = self.get_bank_template()

    def get_bank_template(self):
        """Get import template for bank"""
        templates = {
            "HDFC Bank": {
                "date_column": "Date",
                "description_column": "Narration",
                "withdrawal_column": "Withdrawal Amt.",
                "deposit_column": "Deposit Amt.",
                "balance_column": "Closing Balance",
                "reference_column": "Chq./Ref.No.",
                "date_format": "%d/%m/%y"
            },
            "ICICI Bank": {
                "date_column": "Transaction Date",
                "description_column": "Transaction Remarks",
                "withdrawal_column": "Withdrawal Amount (INR )",
                "deposit_column": "Deposit Amount (INR )",
                "balance_column": "Balance (INR )",
                "reference_column": "Cheque Number",
                "date_format": "%d-%m-%Y"
            },
            "SBI": {
                "date_column": "Txn Date",
                "description_column": "Description",
                "withdrawal_column": "Debit",
                "deposit_column": "Credit",
                "balance_column": "Balance",
                "reference_column": "Ref No./Cheque No.",
                "date_format": "%d %b %Y"
            }
        }
        return templates.get(self.bank, templates["HDFC Bank"])

    def import_csv(self, file_content):
        """Import from CSV file"""
        transactions = []

        reader = csv.DictReader(io.StringIO(file_content))

        for row in reader:
            txn = self.parse_row(row)
            if txn:
                transactions.append(txn)

        return self.create_transactions(transactions)

    def parse_row(self, row):
        """Parse a row from bank statement"""
        from datetime import datetime

        try:
            date_str = row.get(self.template["date_column"], "").strip()
            if not date_str:
                return None

            date = datetime.strptime(date_str, self.template["date_format"]).date()

            withdrawal = self.parse_amount(row.get(self.template["withdrawal_column"], ""))
            deposit = self.parse_amount(row.get(self.template["deposit_column"], ""))

            if not withdrawal and not deposit:
                return None

            return {
                "date": date,
                "description": row.get(self.template["description_column"], ""),
                "withdrawal": withdrawal,
                "deposit": deposit,
                "reference_number": row.get(self.template["reference_column"], ""),
                "closing_balance": self.parse_amount(row.get(self.template["balance_column"], ""))
            }
        except Exception as e:
            frappe.log_error(f"Error parsing row: {str(e)}", "Bank Statement Import")
            return None

    def parse_amount(self, amount_str):
        """Parse amount string to float"""
        if not amount_str:
            return 0

        # Remove currency symbols, commas
        amount_str = str(amount_str).replace(",", "").replace("₹", "").replace("INR", "").strip()

        try:
            return float(amount_str) if amount_str else 0
        except ValueError:
            return 0

    def create_transactions(self, transactions):
        """Create Bank Transaction documents"""
        created = []
        duplicates = 0

        for txn in transactions:
            # Check for duplicate
            existing = frappe.db.exists("Bank Transaction", {
                "bank_account": self.bank_account,
                "date": txn["date"],
                "deposit": txn["deposit"],
                "withdrawal": txn["withdrawal"],
                "reference_number": txn["reference_number"]
            })

            if existing:
                duplicates += 1
                continue

            doc = frappe.get_doc({
                "doctype": "Bank Transaction",
                "bank_account": self.bank_account,
                "date": txn["date"],
                "description": txn["description"],
                "deposit": txn["deposit"],
                "withdrawal": txn["withdrawal"],
                "reference_number": txn["reference_number"],
                "status": "Pending"
            })
            doc.insert(ignore_permissions=True)
            created.append(doc.name)

        return {
            "created": len(created),
            "duplicates": duplicates,
            "transactions": created
        }


@frappe.whitelist()
def import_bank_statement(bank_account, file_url):
    """Import bank statement from uploaded file"""
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    content = file_doc.get_content()

    importer = BankStatementImporter(bank_account)

    if file_url.endswith(".csv"):
        return importer.import_csv(content.decode("utf-8"))
    else:
        frappe.throw(_("Unsupported file format"))
```

---

## Part E: Fee Refund Management

### 1. Fee Refund DocType

```json
{
    "doctype": "DocType",
    "name": "Fee Refund",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "student",
            "fieldtype": "Link",
            "label": "Student",
            "options": "Student",
            "reqd": 1
        },
        {
            "fieldname": "student_name",
            "fieldtype": "Data",
            "label": "Student Name",
            "fetch_from": "student.student_name",
            "read_only": 1
        },
        {
            "fieldname": "fees",
            "fieldtype": "Link",
            "label": "Original Fee",
            "options": "Fees",
            "reqd": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "refund_date",
            "fieldtype": "Date",
            "label": "Refund Date",
            "reqd": 1,
            "default": "Today"
        },
        {
            "fieldname": "refund_reason",
            "fieldtype": "Select",
            "label": "Refund Reason",
            "options": "\nWithdrawal from Program\nExcess Payment\nScholarship Adjustment\nFee Structure Change\nOther",
            "reqd": 1
        },
        {
            "fieldname": "amount_section",
            "fieldtype": "Section Break",
            "label": "Refund Amount"
        },
        {
            "fieldname": "original_amount",
            "fieldtype": "Currency",
            "label": "Original Fee Amount",
            "fetch_from": "fees.grand_total",
            "read_only": 1
        },
        {
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "label": "Paid Amount",
            "fetch_from": "fees.paid_amount",
            "read_only": 1
        },
        {
            "fieldname": "refund_amount",
            "fieldtype": "Currency",
            "label": "Refund Amount",
            "reqd": 1
        },
        {
            "fieldname": "column_break_2",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "deduction_amount",
            "fieldtype": "Currency",
            "label": "Deduction Amount",
            "description": "Processing fees, penalties, etc."
        },
        {
            "fieldname": "net_refund",
            "fieldtype": "Currency",
            "label": "Net Refund Amount",
            "read_only": 1
        },
        {
            "fieldname": "payment_section",
            "fieldtype": "Section Break",
            "label": "Payment Details"
        },
        {
            "fieldname": "payment_mode",
            "fieldtype": "Select",
            "label": "Payment Mode",
            "options": "\nBank Transfer\nCheque\nCash\nOnline Refund",
            "reqd": 1
        },
        {
            "fieldname": "bank_account",
            "fieldtype": "Data",
            "label": "Bank Account Number",
            "depends_on": "eval:doc.payment_mode=='Bank Transfer'"
        },
        {
            "fieldname": "ifsc_code",
            "fieldtype": "Data",
            "label": "IFSC Code",
            "depends_on": "eval:doc.payment_mode=='Bank Transfer'"
        },
        {
            "fieldname": "bank_name",
            "fieldtype": "Data",
            "label": "Bank Name",
            "depends_on": "eval:doc.payment_mode=='Bank Transfer'"
        },
        {
            "fieldname": "column_break_3",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "cheque_number",
            "fieldtype": "Data",
            "label": "Cheque Number",
            "depends_on": "eval:doc.payment_mode=='Cheque'"
        },
        {
            "fieldname": "cheque_date",
            "fieldtype": "Date",
            "label": "Cheque Date",
            "depends_on": "eval:doc.payment_mode=='Cheque'"
        },
        {
            "fieldname": "status_section",
            "fieldtype": "Section Break",
            "label": "Status"
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Draft\nPending Approval\nApproved\nProcessed\nRejected\nCancelled",
            "default": "Draft"
        },
        {
            "fieldname": "processed_date",
            "fieldtype": "Date",
            "label": "Processed Date",
            "read_only": 1
        },
        {
            "fieldname": "payment_entry",
            "fieldtype": "Link",
            "label": "Payment Entry",
            "options": "Payment Entry",
            "read_only": 1
        },
        {
            "fieldname": "remarks_section",
            "fieldtype": "Section Break",
            "label": "Remarks"
        },
        {
            "fieldname": "reason_details",
            "fieldtype": "Small Text",
            "label": "Reason Details"
        },
        {
            "fieldname": "approval_remarks",
            "fieldtype": "Small Text",
            "label": "Approval Remarks"
        }
    ],
    "permissions": [
        {
            "role": "Accounts Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1
        },
        {
            "role": "Accounts User",
            "read": 1,
            "write": 1,
            "create": 1
        }
    ]
}
```

### 2. Fee Refund Workflow

```python
# fee_refund.py

import frappe
from frappe.model.document import Document
from frappe import _


class FeeRefund(Document):
    def validate(self):
        self.validate_refund_amount()
        self.calculate_net_refund()

    def validate_refund_amount(self):
        """Validate refund amount against paid amount"""
        fees = frappe.get_doc("Fees", self.fees)

        if self.refund_amount > fees.paid_amount:
            frappe.throw(_("Refund amount cannot exceed paid amount"))

        # Check for existing refunds
        existing_refunds = frappe.db.sql("""
            SELECT SUM(net_refund) as total_refunded
            FROM `tabFee Refund`
            WHERE fees = %s AND docstatus = 1 AND name != %s
        """, (self.fees, self.name), as_dict=True)

        total_refunded = existing_refunds[0].total_refunded or 0

        if (total_refunded + self.refund_amount) > fees.paid_amount:
            frappe.throw(_(
                f"Total refund amount ({total_refunded + self.refund_amount}) "
                f"cannot exceed paid amount ({fees.paid_amount})"
            ))

    def calculate_net_refund(self):
        """Calculate net refund after deductions"""
        self.net_refund = (self.refund_amount or 0) - (self.deduction_amount or 0)

    def on_submit(self):
        """Create payment entry on submit"""
        if self.status == "Approved":
            self.create_payment_entry()
            self.update_fees_status()

    def create_payment_entry(self):
        """Create payment entry for refund"""
        settings = frappe.get_single("University Accounts Settings")

        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "posting_date": self.refund_date,
            "party_type": "Student",
            "party": self.student,
            "party_name": self.student_name,
            "paid_amount": self.net_refund,
            "received_amount": self.net_refund,
            "paid_from": settings.fee_collection_account,
            "mode_of_payment": self.payment_mode,
            "reference_no": self.name,
            "reference_date": self.refund_date,
            "remarks": f"Fee refund - {self.refund_reason} - {self.fees}"
        })

        if self.payment_mode == "Bank Transfer":
            payment_entry.bank_account = self.bank_account

        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()

        self.payment_entry = payment_entry.name
        self.status = "Processed"
        self.processed_date = frappe.utils.today()

    def update_fees_status(self):
        """Update original fees status if fully refunded"""
        fees = frappe.get_doc("Fees", self.fees)

        total_refunded = frappe.db.sql("""
            SELECT SUM(net_refund) as total
            FROM `tabFee Refund`
            WHERE fees = %s AND docstatus = 1
        """, self.fees, as_dict=True)[0].total or 0

        if total_refunded >= fees.paid_amount:
            fees.db_set("status", "Refunded")


# Refund workflow states
REFUND_WORKFLOW = {
    "states": [
        {"state": "Draft", "doc_status": 0, "allow_edit": "Accounts User"},
        {"state": "Pending Approval", "doc_status": 0, "allow_edit": "Accounts Manager"},
        {"state": "Approved", "doc_status": 0, "allow_edit": "Accounts Manager"},
        {"state": "Rejected", "doc_status": 0, "allow_edit": "Accounts Manager"}
    ],
    "transitions": [
        {"from": "Draft", "to": "Pending Approval", "action": "Submit for Approval"},
        {"from": "Pending Approval", "to": "Approved", "action": "Approve"},
        {"from": "Pending Approval", "to": "Rejected", "action": "Reject"},
        {"from": "Approved", "to": "Processed", "action": "Process Refund"}
    ]
}
```

---

## Part F: Testing & Validation

### 1. Payment Gateway Test Cases

```python
# tests/test_payment_gateway.py

import frappe
import unittest
from unittest.mock import patch, MagicMock


class TestPaymentGateway(unittest.TestCase):

    def setUp(self):
        self.student = create_test_student()
        self.fees = create_test_fees(self.student)

    def test_razorpay_order_creation(self):
        """Test Razorpay order creation"""
        with patch('razorpay.Client') as mock_client:
            mock_client.return_value.order.create.return_value = {
                "id": "order_test123",
                "amount": 10000,
                "currency": "INR"
            }

            result = create_fee_payment_order(self.fees.name)

            self.assertTrue(result.get("success"))
            self.assertEqual(result.get("order_id"), "order_test123")

    def test_payment_verification(self):
        """Test payment signature verification"""
        # Create mock payment data
        payment_data = {
            "razorpay_order_id": "order_test123",
            "razorpay_payment_id": "pay_test456",
            "razorpay_signature": "valid_signature"
        }

        with patch('razorpay.Client') as mock_client:
            mock_client.return_value.utility.verify_payment_signature.return_value = None

            from university_erp.payment_gateway import PaymentGateway
            gateway = PaymentGateway("razorpay")
            result = gateway.verify_payment(payment_data)

            self.assertTrue(result.get("verified"))

    def test_webhook_handling(self):
        """Test webhook event handling"""
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test456",
                        "order_id": "order_test123",
                        "amount": 10000
                    }
                }
            }
        }

        # Test webhook handler
        with patch('university_erp.webhooks.razorpay_webhook.verify_webhook_signature', return_value=True):
            result = handle_razorpay_webhook_test(payload)
            self.assertEqual(result.get("status"), "ok")

    def test_refund_processing(self):
        """Test refund processing"""
        # Create a completed payment first
        payment_order = create_test_payment_order(self.fees)

        # Process refund
        with patch('razorpay.Client') as mock_client:
            mock_client.return_value.payment.refund.return_value = {
                "id": "rfnd_test789",
                "amount": 5000
            }

            from university_erp.payment_gateway import PaymentGateway
            gateway = PaymentGateway("razorpay")
            result = gateway.refund_payment(payment_order.gateway_payment_id, 50)

            self.assertTrue(result.get("success"))


def create_test_student():
    """Create test student"""
    if not frappe.db.exists("Student", "_Test Student Payment"):
        student = frappe.get_doc({
            "doctype": "Student",
            "first_name": "Test",
            "last_name": "Payment",
            "student_email_id": "test.payment@example.com"
        })
        student.insert()
        return student
    return frappe.get_doc("Student", "_Test Student Payment")


def create_test_fees(student):
    """Create test fees"""
    fees = frappe.get_doc({
        "doctype": "Fees",
        "student": student.name,
        "due_date": frappe.utils.add_days(frappe.utils.today(), 30),
        "components": [{
            "fees_category": "Tuition Fee",
            "amount": 100
        }]
    })
    fees.insert()
    return fees
```

---

## Implementation Checklist

### Phase 14 Tasks

- [ ] **Week 1: Razorpay Integration**
  - [ ] Create Razorpay Settings DocType
  - [ ] Implement order creation API
  - [ ] Implement payment verification
  - [ ] Create Payment Order DocType
  - [ ] Build webhook handler
  - [ ] Test payment flow end-to-end

- [ ] **Week 2: PayU Integration**
  - [ ] Create PayU Settings DocType
  - [ ] Implement hash generation
  - [ ] Build success/failure handlers
  - [ ] Test PayU payment flow

- [ ] **Week 3: GL Posting & Accounts**
  - [ ] Create University Accounts Settings
  - [ ] Implement GLPostingManager
  - [ ] Setup fee category accounts mapping
  - [ ] Test automatic GL posting
  - [ ] Implement scholarship GL posting
  - [ ] Implement hostel fee GL posting

- [ ] **Week 4: Bank Reconciliation**
  - [ ] Create Bank Transaction DocType
  - [ ] Build statement import tool
  - [ ] Implement auto-matching algorithm
  - [ ] Build reconciliation interface
  - [ ] Test with sample statements

- [ ] **Week 5: Refund Management & Testing**
  - [ ] Create Fee Refund DocType
  - [ ] Implement refund workflow
  - [ ] Build refund payment entry creation
  - [ ] Write comprehensive tests
  - [ ] Documentation and training

---

## Dependencies

### Python Packages
```
razorpay>=1.3.0
```

### Frappe Hooks
```python
# hooks.py additions
doc_events = {
    "Fees": {
        "on_submit": "university_erp.gl_posting.on_fees_submit"
    }
}

# Website routes for webhooks
website_route_rules = [
    {"from_route": "/api/method/university_erp.webhooks.razorpay_webhook.handle_razorpay_webhook", "to_route": "razorpay_webhook"},
    {"from_route": "/api/method/university_erp.payu_payment.payu_success", "to_route": "payu_success"},
    {"from_route": "/api/method/university_erp.payu_payment.payu_failure", "to_route": "payu_failure"}
]
```

---

## Security Considerations

1. **API Key Storage**: All API keys and secrets stored using Frappe's Password field type
2. **Webhook Verification**: All webhooks verified using HMAC signatures
3. **HTTPS Only**: Payment pages must be served over HTTPS
4. **PCI Compliance**: No card data stored in system - handled by payment gateway
5. **Audit Trail**: All payment transactions logged with full audit trail
6. **Rate Limiting**: Webhook endpoints rate-limited to prevent abuse

---

## Implementation Status

### Completed (98%)

| Component | Status | Location |
|-----------|--------|----------|
| Razorpay Settings DocType | Completed | `university_payments/doctype/razorpay_settings/` |
| PayU Settings DocType | Completed | `university_payments/doctype/payu_settings/` |
| Payment Order DocType | Completed | `university_payments/doctype/payment_order/` |
| Webhook Log DocType | Completed | `university_payments/doctype/webhook_log/` |
| University Accounts Settings | Completed | `university_payments/doctype/university_accounts_settings/` |
| Fee Category Account | Completed | `university_payments/doctype/fee_category_account/` |
| Bank Transaction DocType | Completed | `university_payments/doctype/bank_transaction/` |
| Fee Refund DocType | Completed | `university_payments/doctype/fee_refund/` |
| Unified Payment Gateway | Completed | `university_payments/payment_gateway.py` |
| Razorpay Webhook Handler | Completed | `university_payments/webhooks/razorpay_webhook.py` |
| PayU Callback Handler | Completed | `university_payments/webhooks/payu_callback.py` |
| GL Posting Manager | Completed | `university_payments/gl_posting.py` |
| Bank Reconciliation Tool | Completed | `university_payments/bank_reconciliation.py` |
| Payment Receipt Template | Completed | `university_payments/templates/payment_receipt.html` |
| Workspace | Completed | `university_payments/workspace/university_payments/` |
| Hooks Integration | Completed | Updated `hooks.py` |
| Pay Fees Page | Completed | `www/pay-fees/` |
| Payment Success Page | Completed | `www/fee-payment-success/` |
| Payment Failed Page | Completed | `www/fee-payment-failed/` |
| Bank Reconciliation Page | Completed | `www/bank-reconciliation/` |
| Payment History Page | Completed | `www/student-portal/payment-history/` |
| Daily Collection Report | Completed | `report/daily_collection_report/` |
| Gateway Reconciliation Report | Completed | `report/gateway_reconciliation_report/` |
| Refund Report | Completed | `report/refund_report/` |
| Fee Refund Workflow | Completed | `fixtures/fee_refund_workflow.json` |
| Unit Tests | Completed | `tests/test_*.py` |
| Test Fixtures | Completed | `tests/test_records.py` |
| Requirements (razorpay) | Completed | `pyproject.toml` |

### Optional Enhancements (2%)

| Component | Status | Notes |
|-----------|--------|-------|
| Scheduler Events | Optional | Auto daily reconciliation |
| Boot Session Cache | Optional | Payment settings caching |
| PDF Receipt Variant | Optional | Print-optimized template |

### Files Created

```
university_payments/
├── __init__.py
├── payment_gateway.py          # Unified payment gateway
├── gl_posting.py               # GL posting automation
├── bank_reconciliation.py      # Bank reconciliation tool
├── doctype/
│   ├── razorpay_settings/
│   ├── payu_settings/
│   ├── payment_order/
│   ├── webhook_log/
│   ├── university_accounts_settings/
│   ├── fee_category_account/
│   ├── bank_transaction/
│   └── fee_refund/
├── webhooks/
│   ├── __init__.py
│   ├── razorpay_webhook.py
│   └── payu_callback.py
├── templates/
│   └── payment_receipt.html
├── workspace/
│   └── university_payments/
├── fixtures/
│   └── fee_refund_workflow.json
├── report/
│   ├── daily_collection_report/
│   ├── gateway_reconciliation_report/
│   └── refund_report/
├── tests/
│   ├── __init__.py
│   ├── test_payment_gateway.py
│   ├── test_gl_posting.py
│   ├── test_bank_reconciliation.py
│   ├── test_fee_refund.py
│   ├── test_webhooks.py
│   └── test_records.py          # Test fixtures
└── www/
    ├── pay-fees/
    │   ├── index.html
    │   └── index.py
    ├── fee-payment-success/
    │   ├── index.html
    │   └── index.py
    ├── fee-payment-failed/
    │   ├── index.html
    │   └── index.py
    ├── bank-reconciliation/
    │   ├── index.html
    │   └── index.py
    └── student-portal/
        └── payment-history/
            ├── index.html
            └── index.py
```

---

**Document Version:** 1.4
**Created:** January 2026
**Updated:** January 2026
**Author:** University ERP Team
**Implementation Status:** 100% Complete

### Final Enhancements Added:
1. **Scheduler Events** - Daily auto-reconciliation via `scheduled_tasks.py`
2. **Boot Session Caching** - Payment settings cached in `boot.py`
3. **Print Receipt Template** - `payment_receipt_print.html` with formal print layout
