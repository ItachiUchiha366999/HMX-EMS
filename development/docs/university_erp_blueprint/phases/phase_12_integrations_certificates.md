# Phase 12: Integrations & Certificate Generation

## Overview
This phase implements external system integrations (payment gateways, SMS, biometric, DigiLocker) and comprehensive certificate generation system for various university documents.

**Duration**: 4-5 weeks
**Priority**: High
**Dependencies**: Phase 1-8 (Core modules complete)

---

## Part A: Payment Gateway Integration

### 1. Payment Gateway Settings (DocType)

```json
{
  "name": "Payment Gateway Settings",
  "module": "University ERP",
  "doctype": "DocType",
  "is_single": 1,
  "fields": [
    {
      "fieldname": "gateway_section",
      "fieldtype": "Section Break",
      "label": "Gateway Configuration"
    },
    {
      "fieldname": "default_gateway",
      "fieldtype": "Select",
      "label": "Default Payment Gateway",
      "options": "\nRazorpay\nPayU\nPaytm\nCCAvenue\nStripe",
      "reqd": 1
    },
    {
      "fieldname": "environment",
      "fieldtype": "Select",
      "label": "Environment",
      "options": "Sandbox\nProduction",
      "default": "Sandbox"
    },
    {
      "fieldname": "razorpay_section",
      "fieldtype": "Section Break",
      "label": "Razorpay Settings",
      "depends_on": "eval:doc.default_gateway=='Razorpay'"
    },
    {
      "fieldname": "razorpay_key_id",
      "fieldtype": "Data",
      "label": "Razorpay Key ID"
    },
    {
      "fieldname": "razorpay_key_secret",
      "fieldtype": "Password",
      "label": "Razorpay Key Secret"
    },
    {
      "fieldname": "razorpay_webhook_secret",
      "fieldtype": "Password",
      "label": "Webhook Secret"
    },
    {
      "fieldname": "payu_section",
      "fieldtype": "Section Break",
      "label": "PayU Settings",
      "depends_on": "eval:doc.default_gateway=='PayU'"
    },
    {
      "fieldname": "payu_merchant_key",
      "fieldtype": "Data",
      "label": "PayU Merchant Key"
    },
    {
      "fieldname": "payu_merchant_salt",
      "fieldtype": "Password",
      "label": "PayU Merchant Salt"
    },
    {
      "fieldname": "payu_auth_header",
      "fieldtype": "Password",
      "label": "PayU Auth Header"
    },
    {
      "fieldname": "callback_section",
      "fieldtype": "Section Break",
      "label": "Callback URLs"
    },
    {
      "fieldname": "success_url",
      "fieldtype": "Data",
      "label": "Success Redirect URL"
    },
    {
      "fieldname": "failure_url",
      "fieldtype": "Data",
      "label": "Failure Redirect URL"
    },
    {
      "fieldname": "webhook_url",
      "fieldtype": "Data",
      "label": "Webhook URL",
      "read_only": 1
    }
  ]
}
```

### 2. Payment Transaction (DocType)

```json
{
  "name": "Payment Transaction",
  "module": "University ERP",
  "doctype": "DocType",
  "autoname": "naming_series:",
  "naming_series": "PAY-.YYYY.-.#####",
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
      "fieldname": "reference_doctype",
      "fieldtype": "Link",
      "label": "Reference DocType",
      "options": "DocType"
    },
    {
      "fieldname": "reference_name",
      "fieldtype": "Dynamic Link",
      "label": "Reference Document",
      "options": "reference_doctype"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "transaction_date",
      "fieldtype": "Datetime",
      "label": "Transaction Date",
      "default": "Now"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Initiated\nPending\nSuccess\nFailed\nRefunded\nCancelled",
      "default": "Initiated"
    },
    {
      "fieldname": "payment_section",
      "fieldtype": "Section Break",
      "label": "Payment Details"
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
      "fieldname": "payment_gateway",
      "fieldtype": "Select",
      "label": "Payment Gateway",
      "options": "Razorpay\nPayU\nPaytm\nCCAvenue\nStripe"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
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
      "fieldname": "gateway_signature",
      "fieldtype": "Data",
      "label": "Gateway Signature",
      "hidden": 1
    },
    {
      "fieldname": "payment_method",
      "fieldtype": "Select",
      "label": "Payment Method",
      "options": "\nCard\nNetBanking\nUPI\nWallet\nEMI"
    },
    {
      "fieldname": "response_section",
      "fieldtype": "Section Break",
      "label": "Gateway Response"
    },
    {
      "fieldname": "gateway_response",
      "fieldtype": "Code",
      "label": "Full Response",
      "options": "JSON"
    },
    {
      "fieldname": "error_message",
      "fieldtype": "Small Text",
      "label": "Error Message"
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
    },
    {
      "fieldname": "refund_reason",
      "fieldtype": "Small Text",
      "label": "Refund Reason"
    }
  ]
}
```

### 3. Payment Gateway Controller

```python
# payment_gateway.py

import frappe
from frappe import _
import razorpay
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
        self.client = razorpay.Client(
            auth=(
                self.settings.razorpay_key_id,
                self.settings.get_password("razorpay_key_secret")
            )
        )

    def create_order(self, amount, student, reference_doctype=None, reference_name=None):
        """Create Razorpay order"""
        try:
            # Amount in paise
            amount_paise = int(amount * 100)

            order_data = {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"rcpt_{frappe.utils.random_string(10)}",
                "notes": {
                    "student": student,
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

            return {
                "success": True,
                "order_id": order["id"],
                "transaction": transaction.name,
                "key_id": self.settings.razorpay_key_id,
                "amount": amount_paise,
                "currency": "INR"
            }

        except Exception as e:
            frappe.log_error(f"Razorpay order creation failed: {str(e)}")
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
                transaction.save(ignore_permissions=True)

                # Trigger post-payment actions
                self._on_payment_success(transaction)

                return {"success": True, "transaction": transaction.name}
            else:
                return {"success": False, "error": "Signature verification failed"}

        except Exception as e:
            frappe.log_error(f"Payment verification failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_payment_method(self, payment_id):
        """Get payment method from Razorpay"""
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment.get("method", "").capitalize()
        except:
            return ""

    def _on_payment_success(self, transaction):
        """Handle post-payment actions"""
        if transaction.reference_doctype == "Fees":
            # Update fee payment status
            fee = frappe.get_doc("Fees", transaction.reference_name)
            fee.outstanding_amount -= transaction.amount
            if fee.outstanding_amount <= 0:
                fee.outstanding_amount = 0
                fee.docstatus = 1  # Submit
            fee.save(ignore_permissions=True)

    def process_refund(self, transaction_name, amount=None, reason=None):
        """Process refund through Razorpay"""
        try:
            transaction = frappe.get_doc("Payment Transaction", transaction_name)

            if transaction.status != "Success":
                return {"success": False, "error": "Can only refund successful payments"}

            refund_amount = amount or transaction.amount
            refund_amount_paise = int(refund_amount * 100)

            refund = self.client.payment.refund(
                transaction.gateway_payment_id,
                {
                    "amount": refund_amount_paise,
                    "notes": {"reason": reason or "Requested by admin"}
                }
            )

            transaction.status = "Refunded"
            transaction.refund_id = refund["id"]
            transaction.refund_amount = refund_amount
            transaction.refund_date = frappe.utils.now_datetime()
            transaction.refund_reason = reason
            transaction.save(ignore_permissions=True)

            return {"success": True, "refund_id": refund["id"]}

        except Exception as e:
            frappe.log_error(f"Refund failed: {str(e)}")
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
                f"{student_doc.first_name}|{student_doc.student_email_id}|||||||||||"
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

            return {
                "success": True,
                "payment_url": f"{self.base_url}/_payment",
                "params": {
                    "key": self.merchant_key,
                    "txnid": txnid,
                    "amount": amount,
                    "productinfo": "Fee Payment",
                    "firstname": student_doc.first_name,
                    "email": student_doc.student_email_id,
                    "phone": student_doc.student_mobile_number or "",
                    "surl": self.settings.success_url,
                    "furl": self.settings.failure_url,
                    "hash": hash_value
                },
                "transaction": transaction.name
            }

        except Exception as e:
            frappe.log_error(f"PayU order creation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def verify_payment(self, payment_data):
        """Verify PayU payment response"""
        try:
            txnid = payment_data.get("txnid")
            status = payment_data.get("status")
            amount = payment_data.get("amount")
            received_hash = payment_data.get("hash")

            # Verify reverse hash
            hash_string = (
                f"{self.merchant_salt}|{status}|||||||||||"
                f"{payment_data.get('email')}|{payment_data.get('firstname')}|"
                f"{payment_data.get('productinfo')}|{amount}|{txnid}|{self.merchant_key}"
            )
            calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest()

            if received_hash == calculated_hash and status == "success":
                transaction = frappe.get_doc(
                    "Payment Transaction",
                    {"gateway_order_id": txnid}
                )
                transaction.gateway_payment_id = payment_data.get("mihpayid")
                transaction.status = "Success"
                transaction.payment_method = payment_data.get("mode", "").capitalize()
                transaction.gateway_response = json.dumps(payment_data)
                transaction.save(ignore_permissions=True)

                return {"success": True, "transaction": transaction.name}
            else:
                return {"success": False, "error": "Payment verification failed"}

        except Exception as e:
            frappe.log_error(f"PayU verification failed: {str(e)}")
            return {"success": False, "error": str(e)}


# API Endpoints

@frappe.whitelist()
def initiate_payment(amount, student, gateway=None, reference_doctype=None, reference_name=None):
    """Initiate payment through configured gateway"""
    settings = frappe.get_single("Payment Gateway Settings")
    gateway = gateway or settings.default_gateway

    if gateway == "Razorpay":
        handler = RazorpayGateway()
    elif gateway == "PayU":
        handler = PayUGateway()
    else:
        return {"success": False, "error": f"Unsupported gateway: {gateway}"}

    return handler.create_order(
        float(amount),
        student,
        reference_doctype,
        reference_name
    )


@frappe.whitelist(allow_guest=True)
def payment_callback():
    """Handle payment gateway callbacks"""
    data = frappe.form_dict

    # Determine gateway from data
    if "razorpay_order_id" in data:
        handler = RazorpayGateway()
    elif "mihpayid" in data:
        handler = PayUGateway()
    else:
        frappe.throw(_("Unknown payment gateway"))

    result = handler.verify_payment(data)

    if result.get("success"):
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = (
            frappe.get_single("Payment Gateway Settings").success_url
            + f"?transaction={result.get('transaction')}"
        )
    else:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = (
            frappe.get_single("Payment Gateway Settings").failure_url
            + f"?error={result.get('error')}"
        )


@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """Handle Razorpay webhooks"""
    try:
        payload = frappe.request.get_data()
        signature = frappe.request.headers.get("X-Razorpay-Signature")

        settings = frappe.get_single("Payment Gateway Settings")
        secret = settings.get_password("razorpay_webhook_secret")

        # Verify webhook signature
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if signature != expected_signature:
            frappe.throw(_("Invalid webhook signature"))

        event = json.loads(payload)
        event_type = event.get("event")

        if event_type == "payment.captured":
            # Payment successful
            payment = event["payload"]["payment"]["entity"]
            order_id = payment.get("order_id")

            transaction = frappe.get_doc(
                "Payment Transaction",
                {"gateway_order_id": order_id}
            )

            if transaction.status != "Success":
                transaction.gateway_payment_id = payment["id"]
                transaction.status = "Success"
                transaction.save(ignore_permissions=True)

        elif event_type == "refund.created":
            # Refund processed
            refund = event["payload"]["refund"]["entity"]
            payment_id = refund.get("payment_id")

            transaction = frappe.get_doc(
                "Payment Transaction",
                {"gateway_payment_id": payment_id}
            )
            transaction.status = "Refunded"
            transaction.refund_id = refund["id"]
            transaction.refund_amount = refund["amount"] / 100
            transaction.save(ignore_permissions=True)

        return {"status": "ok"}

    except Exception as e:
        frappe.log_error(f"Webhook processing failed: {str(e)}")
        return {"status": "error", "message": str(e)}
```

---

## Part B: SMS Gateway Integration

### 1. SMS Settings (DocType)

```json
{
  "name": "SMS Settings",
  "module": "University ERP",
  "doctype": "DocType",
  "is_single": 1,
  "fields": [
    {
      "fieldname": "sms_gateway",
      "fieldtype": "Select",
      "label": "SMS Gateway",
      "options": "\nMSG91\nTwilio\nTextLocal\nFast2SMS",
      "reqd": 1
    },
    {
      "fieldname": "sender_id",
      "fieldtype": "Data",
      "label": "Sender ID",
      "description": "6 character alphanumeric sender ID"
    },
    {
      "fieldname": "msg91_section",
      "fieldtype": "Section Break",
      "label": "MSG91 Settings",
      "depends_on": "eval:doc.sms_gateway=='MSG91'"
    },
    {
      "fieldname": "msg91_auth_key",
      "fieldtype": "Password",
      "label": "MSG91 Auth Key"
    },
    {
      "fieldname": "msg91_template_id",
      "fieldtype": "Data",
      "label": "Default Template ID"
    },
    {
      "fieldname": "twilio_section",
      "fieldtype": "Section Break",
      "label": "Twilio Settings",
      "depends_on": "eval:doc.sms_gateway=='Twilio'"
    },
    {
      "fieldname": "twilio_account_sid",
      "fieldtype": "Data",
      "label": "Twilio Account SID"
    },
    {
      "fieldname": "twilio_auth_token",
      "fieldtype": "Password",
      "label": "Twilio Auth Token"
    },
    {
      "fieldname": "twilio_phone_number",
      "fieldtype": "Data",
      "label": "Twilio Phone Number"
    },
    {
      "fieldname": "templates_section",
      "fieldtype": "Section Break",
      "label": "SMS Templates"
    },
    {
      "fieldname": "sms_templates",
      "fieldtype": "Table",
      "label": "Templates",
      "options": "SMS Template"
    }
  ]
}
```

### 2. SMS Template (Child DocType)

```json
{
  "name": "SMS Template",
  "module": "University ERP",
  "doctype": "DocType",
  "istable": 1,
  "fields": [
    {
      "fieldname": "template_name",
      "fieldtype": "Data",
      "label": "Template Name",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "template_id",
      "fieldtype": "Data",
      "label": "DLT Template ID",
      "in_list_view": 1
    },
    {
      "fieldname": "event_trigger",
      "fieldtype": "Select",
      "label": "Event Trigger",
      "options": "\nFee Due Reminder\nFee Payment Confirmation\nAttendance Alert\nExam Schedule\nResult Declaration\nAdmission Status\nHostel Allotment\nCustom",
      "in_list_view": 1
    },
    {
      "fieldname": "message_template",
      "fieldtype": "Text",
      "label": "Message Template"
    }
  ]
}
```

### 3. SMS Log (DocType)

```json
{
  "name": "SMS Log",
  "module": "University ERP",
  "doctype": "DocType",
  "autoname": "naming_series:",
  "naming_series": "SMS-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "recipient",
      "fieldtype": "Data",
      "label": "Recipient Number",
      "reqd": 1
    },
    {
      "fieldname": "recipient_name",
      "fieldtype": "Data",
      "label": "Recipient Name"
    },
    {
      "fieldname": "message",
      "fieldtype": "Text",
      "label": "Message",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "sent_on",
      "fieldtype": "Datetime",
      "label": "Sent On",
      "default": "Now"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Queued\nSent\nDelivered\nFailed",
      "default": "Queued"
    },
    {
      "fieldname": "gateway_response",
      "fieldtype": "Code",
      "label": "Gateway Response",
      "options": "JSON"
    },
    {
      "fieldname": "error_message",
      "fieldtype": "Small Text",
      "label": "Error Message"
    }
  ]
}
```

### 4. SMS Gateway Controller

```python
# sms_gateway.py

import frappe
from frappe import _
import requests
import json


class SMSGateway:
    """Base SMS gateway handler"""

    def __init__(self):
        self.settings = frappe.get_single("SMS Settings")

    def send_sms(self, recipient, message, template_id=None):
        """Send SMS - to be implemented by subclass"""
        raise NotImplementedError

    def send_bulk_sms(self, recipients, message, template_id=None):
        """Send bulk SMS"""
        results = []
        for recipient in recipients:
            result = self.send_sms(recipient, message, template_id)
            results.append(result)
        return results


class MSG91Gateway(SMSGateway):
    """MSG91 SMS gateway implementation"""

    def __init__(self):
        super().__init__()
        self.auth_key = self.settings.get_password("msg91_auth_key")
        self.sender_id = self.settings.sender_id
        self.base_url = "https://control.msg91.com/api/v5"

    def send_sms(self, recipient, message, template_id=None):
        """Send SMS via MSG91"""
        try:
            # Normalize phone number
            recipient = self._normalize_phone(recipient)
            template_id = template_id or self.settings.msg91_template_id

            url = f"{self.base_url}/flow/"
            headers = {
                "authkey": self.auth_key,
                "Content-Type": "application/json"
            }

            payload = {
                "template_id": template_id,
                "sender": self.sender_id,
                "short_url": "0",
                "mobiles": recipient,
                "VAR1": message  # Variable in template
            }

            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            # Log SMS
            log = frappe.get_doc({
                "doctype": "SMS Log",
                "recipient": recipient,
                "message": message,
                "status": "Sent" if response_data.get("type") == "success" else "Failed",
                "gateway_response": json.dumps(response_data),
                "error_message": response_data.get("message") if response_data.get("type") != "success" else None
            })
            log.insert(ignore_permissions=True)

            return {
                "success": response_data.get("type") == "success",
                "log": log.name,
                "response": response_data
            }

        except Exception as e:
            frappe.log_error(f"MSG91 SMS failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _normalize_phone(self, phone):
        """Normalize phone number to 91XXXXXXXXXX format"""
        phone = str(phone).strip()
        phone = ''.join(filter(str.isdigit, phone))

        if len(phone) == 10:
            phone = "91" + phone
        elif phone.startswith("0"):
            phone = "91" + phone[1:]

        return phone


class TwilioGateway(SMSGateway):
    """Twilio SMS gateway implementation"""

    def __init__(self):
        super().__init__()
        from twilio.rest import Client

        self.client = Client(
            self.settings.twilio_account_sid,
            self.settings.get_password("twilio_auth_token")
        )
        self.from_number = self.settings.twilio_phone_number

    def send_sms(self, recipient, message, template_id=None):
        """Send SMS via Twilio"""
        try:
            # Normalize phone number
            if not recipient.startswith("+"):
                recipient = "+91" + recipient[-10:]

            sms = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=recipient
            )

            # Log SMS
            log = frappe.get_doc({
                "doctype": "SMS Log",
                "recipient": recipient,
                "message": message,
                "status": "Sent" if sms.status in ["queued", "sent"] else "Failed",
                "gateway_response": json.dumps({
                    "sid": sms.sid,
                    "status": sms.status
                })
            })
            log.insert(ignore_permissions=True)

            return {
                "success": True,
                "sid": sms.sid,
                "log": log.name
            }

        except Exception as e:
            frappe.log_error(f"Twilio SMS failed: {str(e)}")
            return {"success": False, "error": str(e)}


# Utility Functions

def get_sms_gateway():
    """Get configured SMS gateway instance"""
    settings = frappe.get_single("SMS Settings")

    if settings.sms_gateway == "MSG91":
        return MSG91Gateway()
    elif settings.sms_gateway == "Twilio":
        return TwilioGateway()
    else:
        frappe.throw(_("SMS gateway not configured"))


@frappe.whitelist()
def send_sms(recipient, message, template_id=None):
    """Send SMS to a recipient"""
    gateway = get_sms_gateway()
    return gateway.send_sms(recipient, message, template_id)


@frappe.whitelist()
def send_bulk_sms(recipients, message, template_id=None):
    """Send SMS to multiple recipients"""
    if isinstance(recipients, str):
        recipients = json.loads(recipients)

    gateway = get_sms_gateway()
    return gateway.send_bulk_sms(recipients, message, template_id)


def send_templated_sms(event_trigger, recipient, variables):
    """Send SMS using predefined template"""
    settings = frappe.get_single("SMS Settings")

    template = None
    for t in settings.sms_templates:
        if t.event_trigger == event_trigger:
            template = t
            break

    if not template:
        frappe.log_error(f"SMS template not found for event: {event_trigger}")
        return {"success": False, "error": "Template not found"}

    # Replace variables in template
    message = template.message_template
    for key, value in variables.items():
        message = message.replace(f"{{{{{key}}}}}", str(value))

    gateway = get_sms_gateway()
    return gateway.send_sms(recipient, message, template.template_id)


# Event Handlers

def on_fee_due(fee):
    """Send fee due reminder SMS"""
    student = frappe.get_doc("Student", fee.student)
    if student.student_mobile_number:
        send_templated_sms(
            "Fee Due Reminder",
            student.student_mobile_number,
            {
                "student_name": student.student_name,
                "amount": fee.outstanding_amount,
                "due_date": fee.due_date
            }
        )


def on_payment_success(transaction):
    """Send payment confirmation SMS"""
    student = frappe.get_doc("Student", transaction.student)
    if student.student_mobile_number:
        send_templated_sms(
            "Fee Payment Confirmation",
            student.student_mobile_number,
            {
                "student_name": student.student_name,
                "amount": transaction.amount,
                "transaction_id": transaction.name
            }
        )


def send_attendance_alert(student, date, subject, status):
    """Send attendance alert to student/parent"""
    student_doc = frappe.get_doc("Student", student)

    # Send to student
    if student_doc.student_mobile_number:
        send_templated_sms(
            "Attendance Alert",
            student_doc.student_mobile_number,
            {
                "student_name": student_doc.student_name,
                "date": date,
                "subject": subject,
                "status": status
            }
        )

    # Send to guardian
    guardians = frappe.get_all(
        "Student Guardian",
        filters={"parent": student},
        fields=["guardian_name", "guardian_mobile"]
    )

    for guardian in guardians:
        if guardian.guardian_mobile:
            send_templated_sms(
                "Attendance Alert",
                guardian.guardian_mobile,
                {
                    "student_name": student_doc.student_name,
                    "date": date,
                    "subject": subject,
                    "status": status
                }
            )
```

---

## Part C: Biometric Integration

### 1. Biometric Device (DocType)

```json
{
  "name": "Biometric Device",
  "module": "University ERP",
  "doctype": "DocType",
  "autoname": "naming_series:",
  "naming_series": "BIO-.####",
  "fields": [
    {
      "fieldname": "device_name",
      "fieldtype": "Data",
      "label": "Device Name",
      "reqd": 1
    },
    {
      "fieldname": "device_type",
      "fieldtype": "Select",
      "label": "Device Type",
      "options": "ZKTeco\nESSL\nBioMax\nMantra\nOther",
      "reqd": 1
    },
    {
      "fieldname": "serial_number",
      "fieldtype": "Data",
      "label": "Serial Number"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "location",
      "fieldtype": "Data",
      "label": "Installation Location"
    },
    {
      "fieldname": "department",
      "fieldtype": "Link",
      "label": "Department",
      "options": "Department"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Active\nInactive\nMaintenance",
      "default": "Active"
    },
    {
      "fieldname": "connection_section",
      "fieldtype": "Section Break",
      "label": "Connection Settings"
    },
    {
      "fieldname": "ip_address",
      "fieldtype": "Data",
      "label": "IP Address",
      "reqd": 1
    },
    {
      "fieldname": "port",
      "fieldtype": "Int",
      "label": "Port",
      "default": 4370
    },
    {
      "fieldname": "communication_password",
      "fieldtype": "Password",
      "label": "Communication Password"
    },
    {
      "fieldname": "sync_section",
      "fieldtype": "Section Break",
      "label": "Sync Settings"
    },
    {
      "fieldname": "last_sync",
      "fieldtype": "Datetime",
      "label": "Last Sync"
    },
    {
      "fieldname": "auto_sync",
      "fieldtype": "Check",
      "label": "Enable Auto Sync"
    },
    {
      "fieldname": "sync_interval",
      "fieldtype": "Int",
      "label": "Sync Interval (minutes)",
      "default": 15,
      "depends_on": "auto_sync"
    }
  ]
}
```

### 2. Biometric Attendance Log (DocType)

```json
{
  "name": "Biometric Attendance Log",
  "module": "University ERP",
  "doctype": "DocType",
  "autoname": "naming_series:",
  "naming_series": "BAL-.YYYY.-.#####",
  "fields": [
    {
      "fieldname": "device",
      "fieldtype": "Link",
      "label": "Device",
      "options": "Biometric Device",
      "reqd": 1
    },
    {
      "fieldname": "user_id",
      "fieldtype": "Data",
      "label": "Biometric User ID",
      "reqd": 1
    },
    {
      "fieldname": "punch_time",
      "fieldtype": "Datetime",
      "label": "Punch Time",
      "reqd": 1
    },
    {
      "fieldname": "punch_type",
      "fieldtype": "Select",
      "label": "Punch Type",
      "options": "Check In\nCheck Out\nBreak Start\nBreak End"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "employee",
      "fieldtype": "Link",
      "label": "Employee",
      "options": "Employee"
    },
    {
      "fieldname": "student",
      "fieldtype": "Link",
      "label": "Student",
      "options": "Student"
    },
    {
      "fieldname": "processed",
      "fieldtype": "Check",
      "label": "Processed",
      "default": 0
    },
    {
      "fieldname": "attendance_record",
      "fieldtype": "Dynamic Link",
      "label": "Attendance Record",
      "options": "attendance_doctype"
    },
    {
      "fieldname": "attendance_doctype",
      "fieldtype": "Link",
      "label": "Attendance DocType",
      "options": "DocType",
      "hidden": 1
    }
  ]
}
```

### 3. Biometric Controller

```python
# biometric_integration.py

import frappe
from frappe import _
from datetime import datetime, timedelta
import socket


class BiometricDevice:
    """Base biometric device handler"""

    def __init__(self, device_name):
        self.device = frappe.get_doc("Biometric Device", device_name)

    def connect(self):
        """Establish connection to device"""
        raise NotImplementedError

    def disconnect(self):
        """Close connection"""
        raise NotImplementedError

    def get_attendance(self, start_date=None, end_date=None):
        """Fetch attendance logs from device"""
        raise NotImplementedError

    def sync_users(self, users):
        """Sync user data to device"""
        raise NotImplementedError


class ZKTecoDevice(BiometricDevice):
    """ZKTeco device integration using pyzk library"""

    def __init__(self, device_name):
        super().__init__(device_name)
        from zk import ZK

        self.zk = ZK(
            self.device.ip_address,
            port=self.device.port,
            timeout=5,
            password=self.device.get_password("communication_password") or 0
        )
        self.conn = None

    def connect(self):
        """Connect to ZKTeco device"""
        try:
            self.conn = self.zk.connect()
            return True
        except Exception as e:
            frappe.log_error(f"ZKTeco connection failed: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from device"""
        if self.conn:
            self.conn.disconnect()

    def get_attendance(self, start_date=None, end_date=None):
        """Get attendance logs from ZKTeco device"""
        if not self.connect():
            return []

        try:
            attendance = self.conn.get_attendance()
            logs = []

            for record in attendance:
                punch_time = record.timestamp

                # Filter by date range if specified
                if start_date and punch_time.date() < start_date:
                    continue
                if end_date and punch_time.date() > end_date:
                    continue

                logs.append({
                    "user_id": str(record.user_id),
                    "punch_time": punch_time,
                    "punch_type": self._get_punch_type(record.punch)
                })

            # Update last sync time
            self.device.last_sync = frappe.utils.now_datetime()
            self.device.save(ignore_permissions=True)

            return logs

        finally:
            self.disconnect()

    def _get_punch_type(self, punch_code):
        """Convert punch code to type"""
        mapping = {
            0: "Check In",
            1: "Check Out",
            2: "Break Start",
            3: "Break End"
        }
        return mapping.get(punch_code, "Check In")

    def sync_users(self, users):
        """Sync users to device"""
        if not self.connect():
            return False

        try:
            for user in users:
                self.conn.set_user(
                    uid=user["uid"],
                    name=user["name"],
                    privilege=user.get("privilege", 0),
                    password=user.get("password", ""),
                    group_id=user.get("group_id", ""),
                    user_id=user["user_id"]
                )
            return True
        except Exception as e:
            frappe.log_error(f"User sync failed: {str(e)}")
            return False
        finally:
            self.disconnect()

    def clear_attendance(self):
        """Clear attendance logs from device"""
        if not self.connect():
            return False

        try:
            self.conn.clear_attendance()
            return True
        finally:
            self.disconnect()


def get_biometric_device(device_name):
    """Get appropriate device handler"""
    device = frappe.get_doc("Biometric Device", device_name)

    if device.device_type == "ZKTeco":
        return ZKTecoDevice(device_name)
    elif device.device_type == "ESSL":
        return ESSLDevice(device_name)
    else:
        frappe.throw(_("Unsupported device type: {0}").format(device.device_type))


@frappe.whitelist()
def sync_attendance(device_name, start_date=None, end_date=None):
    """Sync attendance from biometric device"""
    device_handler = get_biometric_device(device_name)
    logs = device_handler.get_attendance(
        start_date=frappe.utils.getdate(start_date) if start_date else None,
        end_date=frappe.utils.getdate(end_date) if end_date else None
    )

    created = 0
    for log in logs:
        # Check if already exists
        existing = frappe.db.exists("Biometric Attendance Log", {
            "device": device_name,
            "user_id": log["user_id"],
            "punch_time": log["punch_time"]
        })

        if not existing:
            bio_log = frappe.get_doc({
                "doctype": "Biometric Attendance Log",
                "device": device_name,
                "user_id": log["user_id"],
                "punch_time": log["punch_time"],
                "punch_type": log["punch_type"]
            })

            # Try to match with employee or student
            bio_log.employee = get_employee_by_biometric_id(log["user_id"])
            bio_log.student = get_student_by_biometric_id(log["user_id"])

            bio_log.insert(ignore_permissions=True)
            created += 1

    frappe.db.commit()
    return {"synced": created, "total": len(logs)}


def get_employee_by_biometric_id(biometric_id):
    """Get employee linked to biometric ID"""
    return frappe.db.get_value(
        "Employee",
        {"custom_biometric_id": biometric_id},
        "name"
    )


def get_student_by_biometric_id(biometric_id):
    """Get student linked to biometric ID"""
    return frappe.db.get_value(
        "Student",
        {"custom_biometric_id": biometric_id},
        "name"
    )


@frappe.whitelist()
def process_attendance_logs(from_date=None, to_date=None):
    """Process biometric logs into attendance records"""
    filters = {"processed": 0}

    if from_date:
        filters["punch_time"] = [">=", from_date]
    if to_date:
        filters["punch_time"] = ["<=", to_date + " 23:59:59"]

    logs = frappe.get_all(
        "Biometric Attendance Log",
        filters=filters,
        fields=["name", "employee", "student", "punch_time", "punch_type"],
        order_by="punch_time"
    )

    processed = 0

    # Group by employee/student and date
    grouped = {}
    for log in logs:
        key = (log.employee or log.student, log.punch_time.date())
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(log)

    for (person, date), person_logs in grouped.items():
        if not person:
            continue

        # Sort by time
        person_logs.sort(key=lambda x: x.punch_time)

        check_in = None
        check_out = None

        for log in person_logs:
            if log.punch_type == "Check In" and not check_in:
                check_in = log.punch_time
            elif log.punch_type == "Check Out":
                check_out = log.punch_time

        # Create/update attendance
        if person_logs[0].employee:
            create_employee_attendance(
                person_logs[0].employee,
                date,
                check_in,
                check_out,
                person_logs
            )

        processed += len(person_logs)

    return {"processed": processed}


def create_employee_attendance(employee, date, check_in, check_out, logs):
    """Create attendance record for employee"""
    from frappe.utils import get_datetime

    # Check existing
    existing = frappe.db.exists("Attendance", {
        "employee": employee,
        "attendance_date": date
    })

    if existing:
        attendance = frappe.get_doc("Attendance", existing)
    else:
        attendance = frappe.get_doc({
            "doctype": "Attendance",
            "employee": employee,
            "attendance_date": date,
            "company": frappe.db.get_value("Employee", employee, "company")
        })

    # Calculate working hours
    if check_in and check_out:
        working_hours = (check_out - check_in).total_seconds() / 3600
        attendance.working_hours = round(working_hours, 2)
        attendance.status = "Present"
    elif check_in:
        attendance.status = "Half Day"

    attendance.save(ignore_permissions=True)

    # Mark logs as processed
    for log in logs:
        frappe.db.set_value(
            "Biometric Attendance Log",
            log.name,
            {
                "processed": 1,
                "attendance_doctype": "Attendance",
                "attendance_record": attendance.name
            }
        )


# Scheduled Tasks

def scheduled_sync_all_devices():
    """Sync all active biometric devices"""
    devices = frappe.get_all(
        "Biometric Device",
        filters={"status": "Active", "auto_sync": 1},
        pluck="name"
    )

    for device in devices:
        try:
            sync_attendance(device)
        except Exception as e:
            frappe.log_error(f"Auto sync failed for {device}: {str(e)}")
```

---

## Part D: DigiLocker Integration

### 1. DigiLocker Settings (DocType)

```json
{
  "name": "DigiLocker Settings",
  "module": "University ERP",
  "doctype": "DocType",
  "is_single": 1,
  "fields": [
    {
      "fieldname": "enabled",
      "fieldtype": "Check",
      "label": "Enable DigiLocker Integration"
    },
    {
      "fieldname": "client_id",
      "fieldtype": "Data",
      "label": "Client ID"
    },
    {
      "fieldname": "client_secret",
      "fieldtype": "Password",
      "label": "Client Secret"
    },
    {
      "fieldname": "hmac_key",
      "fieldtype": "Password",
      "label": "HMAC Key"
    },
    {
      "fieldname": "environment",
      "fieldtype": "Select",
      "label": "Environment",
      "options": "Sandbox\nProduction",
      "default": "Sandbox"
    },
    {
      "fieldname": "issuer_section",
      "fieldtype": "Section Break",
      "label": "Issuer Details"
    },
    {
      "fieldname": "org_id",
      "fieldtype": "Data",
      "label": "Organization ID"
    },
    {
      "fieldname": "issuer_id",
      "fieldtype": "Data",
      "label": "Issuer ID"
    },
    {
      "fieldname": "doc_types_section",
      "fieldtype": "Section Break",
      "label": "Document Types"
    },
    {
      "fieldname": "document_types",
      "fieldtype": "Table",
      "label": "Document Types",
      "options": "DigiLocker Document Type"
    }
  ]
}
```

### 2. DigiLocker Document Type (Child DocType)

```json
{
  "name": "DigiLocker Document Type",
  "module": "University ERP",
  "doctype": "DocType",
  "istable": 1,
  "fields": [
    {
      "fieldname": "document_type",
      "fieldtype": "Data",
      "label": "Document Type",
      "in_list_view": 1
    },
    {
      "fieldname": "doc_type_code",
      "fieldtype": "Data",
      "label": "Doc Type Code",
      "in_list_view": 1
    },
    {
      "fieldname": "uri_format",
      "fieldtype": "Data",
      "label": "URI Format"
    }
  ]
}
```

### 3. DigiLocker Controller

```python
# digilocker_integration.py

import frappe
from frappe import _
import requests
import hashlib
import hmac
import base64
import json
from datetime import datetime


class DigiLockerClient:
    """DigiLocker API integration client"""

    def __init__(self):
        self.settings = frappe.get_single("DigiLocker Settings")

        if not self.settings.enabled:
            frappe.throw(_("DigiLocker integration is not enabled"))

        self.base_url = (
            "https://api.digitallocker.gov.in"
            if self.settings.environment == "Production"
            else "https://apisetu.gov.in/stg"
        )

        self.client_id = self.settings.client_id
        self.client_secret = self.settings.get_password("client_secret")
        self.hmac_key = self.settings.get_password("hmac_key")

    def _generate_hmac(self, data):
        """Generate HMAC signature for request"""
        message = json.dumps(data, separators=(',', ':'))
        signature = hmac.new(
            self.hmac_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _get_headers(self, hmac_signature=None):
        """Get API request headers"""
        headers = {
            "Content-Type": "application/json",
            "x-digilocker-hmac": hmac_signature or ""
        }
        return headers

    def issue_document(self, doc_type, doc_data, student):
        """Issue document to DigiLocker"""
        try:
            # Get document type configuration
            doc_config = None
            for dt in self.settings.document_types:
                if dt.document_type == doc_type:
                    doc_config = dt
                    break

            if not doc_config:
                return {"success": False, "error": f"Document type {doc_type} not configured"}

            student_doc = frappe.get_doc("Student", student)

            # Prepare document data
            payload = {
                "orgId": self.settings.org_id,
                "issuerId": self.settings.issuer_id,
                "docType": doc_config.doc_type_code,
                "docData": doc_data,
                "recipientId": student_doc.custom_aadhaar_number,  # Aadhaar linked
                "issueDate": datetime.now().strftime("%Y-%m-%d")
            }

            hmac_signature = self._generate_hmac(payload)

            response = requests.post(
                f"{self.base_url}/issuedoc/1/issue",
                headers=self._get_headers(hmac_signature),
                json=payload
            )

            if response.status_code == 200:
                result = response.json()

                # Log issued document
                frappe.get_doc({
                    "doctype": "DigiLocker Issued Document",
                    "student": student,
                    "document_type": doc_type,
                    "document_uri": result.get("uri"),
                    "issued_date": frappe.utils.now_datetime()
                }).insert(ignore_permissions=True)

                return {"success": True, "uri": result.get("uri")}
            else:
                return {
                    "success": False,
                    "error": response.text
                }

        except Exception as e:
            frappe.log_error(f"DigiLocker issue failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def verify_document(self, document_uri):
        """Verify document from DigiLocker"""
        try:
            payload = {"uri": document_uri}
            hmac_signature = self._generate_hmac(payload)

            response = requests.post(
                f"{self.base_url}/docverify/1/verify",
                headers=self._get_headers(hmac_signature),
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "verified": result.get("verified", False),
                    "data": result
                }
            else:
                return {"success": False, "error": response.text}

        except Exception as e:
            frappe.log_error(f"DigiLocker verify failed: {str(e)}")
            return {"success": False, "error": str(e)}


@frappe.whitelist()
def issue_certificate_to_digilocker(certificate_type, student, certificate_data):
    """Issue certificate to student's DigiLocker"""
    client = DigiLockerClient()

    if isinstance(certificate_data, str):
        certificate_data = json.loads(certificate_data)

    return client.issue_document(certificate_type, certificate_data, student)


@frappe.whitelist()
def verify_digilocker_document(document_uri):
    """Verify a DigiLocker document"""
    client = DigiLockerClient()
    return client.verify_document(document_uri)
```

---

## Part E: Certificate Generation System

### 1. Certificate Template (DocType)

```json
{
  "name": "Certificate Template",
  "module": "University ERP",
  "doctype": "DocType",
  "autoname": "field:template_name",
  "fields": [
    {
      "fieldname": "template_name",
      "fieldtype": "Data",
      "label": "Template Name",
      "reqd": 1,
      "unique": 1
    },
    {
      "fieldname": "certificate_type",
      "fieldtype": "Select",
      "label": "Certificate Type",
      "options": "Bonafide Certificate\nCharacter Certificate\nMigration Certificate\nTransfer Certificate\nDegree Certificate\nProvisional Certificate\nConduct Certificate\nStudy Certificate\nNo Dues Certificate\nMedium of Instruction Certificate\nCustom",
      "reqd": 1
    },
    {
      "fieldname": "description",
      "fieldtype": "Small Text",
      "label": "Description"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "is_active",
      "fieldtype": "Check",
      "label": "Is Active",
      "default": 1
    },
    {
      "fieldname": "requires_approval",
      "fieldtype": "Check",
      "label": "Requires Approval"
    },
    {
      "fieldname": "approver_role",
      "fieldtype": "Link",
      "label": "Approver Role",
      "options": "Role",
      "depends_on": "requires_approval"
    },
    {
      "fieldname": "template_section",
      "fieldtype": "Section Break",
      "label": "Template Content"
    },
    {
      "fieldname": "html_template",
      "fieldtype": "Code",
      "label": "HTML Template",
      "options": "HTML"
    },
    {
      "fieldname": "styling_section",
      "fieldtype": "Section Break",
      "label": "Styling"
    },
    {
      "fieldname": "page_size",
      "fieldtype": "Select",
      "label": "Page Size",
      "options": "A4\nLetter\nLegal",
      "default": "A4"
    },
    {
      "fieldname": "orientation",
      "fieldtype": "Select",
      "label": "Orientation",
      "options": "Portrait\nLandscape",
      "default": "Portrait"
    },
    {
      "fieldname": "header_image",
      "fieldtype": "Attach Image",
      "label": "Header Image"
    },
    {
      "fieldname": "footer_image",
      "fieldtype": "Attach Image",
      "label": "Footer Image"
    },
    {
      "fieldname": "watermark_image",
      "fieldtype": "Attach Image",
      "label": "Watermark Image"
    },
    {
      "fieldname": "css_styles",
      "fieldtype": "Code",
      "label": "Custom CSS",
      "options": "CSS"
    }
  ]
}
```

### 2. Certificate Request (DocType)

```json
{
  "name": "Certificate Request",
  "module": "University ERP",
  "doctype": "DocType",
  "autoname": "naming_series:",
  "naming_series": "CERT-.YYYY.-.#####",
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
      "fieldname": "program",
      "fieldtype": "Link",
      "label": "Program",
      "options": "Program",
      "fetch_from": "student.program"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "certificate_template",
      "fieldtype": "Link",
      "label": "Certificate Template",
      "options": "Certificate Template",
      "reqd": 1
    },
    {
      "fieldname": "request_date",
      "fieldtype": "Date",
      "label": "Request Date",
      "default": "Today",
      "reqd": 1
    },
    {
      "fieldname": "purpose",
      "fieldtype": "Small Text",
      "label": "Purpose"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "Pending\nApproved\nRejected\nGenerated\nIssued",
      "default": "Pending"
    },
    {
      "fieldname": "details_section",
      "fieldtype": "Section Break",
      "label": "Certificate Details"
    },
    {
      "fieldname": "additional_fields",
      "fieldtype": "Table",
      "label": "Additional Fields",
      "options": "Certificate Field"
    },
    {
      "fieldname": "approval_section",
      "fieldtype": "Section Break",
      "label": "Approval"
    },
    {
      "fieldname": "approved_by",
      "fieldtype": "Link",
      "label": "Approved By",
      "options": "User",
      "read_only": 1
    },
    {
      "fieldname": "approval_date",
      "fieldtype": "Date",
      "label": "Approval Date",
      "read_only": 1
    },
    {
      "fieldname": "rejection_reason",
      "fieldtype": "Small Text",
      "label": "Rejection Reason",
      "depends_on": "eval:doc.status=='Rejected'"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "certificate_number",
      "fieldtype": "Data",
      "label": "Certificate Number",
      "read_only": 1
    },
    {
      "fieldname": "issue_date",
      "fieldtype": "Date",
      "label": "Issue Date",
      "read_only": 1
    },
    {
      "fieldname": "generated_pdf",
      "fieldtype": "Attach",
      "label": "Generated PDF",
      "read_only": 1
    },
    {
      "fieldname": "verification_section",
      "fieldtype": "Section Break",
      "label": "Verification"
    },
    {
      "fieldname": "verification_code",
      "fieldtype": "Data",
      "label": "Verification Code",
      "read_only": 1
    },
    {
      "fieldname": "qr_code",
      "fieldtype": "Attach Image",
      "label": "QR Code",
      "read_only": 1
    }
  ]
}
```

### 3. Certificate Field (Child DocType)

```json
{
  "name": "Certificate Field",
  "module": "University ERP",
  "doctype": "DocType",
  "istable": 1,
  "fields": [
    {
      "fieldname": "field_name",
      "fieldtype": "Data",
      "label": "Field Name",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "field_value",
      "fieldtype": "Data",
      "label": "Field Value",
      "in_list_view": 1
    }
  ]
}
```

### 4. Certificate Generator Controller

```python
# certificate_generator.py

import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
import qrcode
import io
import base64
import hashlib
from jinja2 import Template


class CertificateGenerator:
    """Certificate generation and management"""

    def __init__(self, certificate_request):
        if isinstance(certificate_request, str):
            self.request = frappe.get_doc("Certificate Request", certificate_request)
        else:
            self.request = certificate_request

        self.template = frappe.get_doc(
            "Certificate Template",
            self.request.certificate_template
        )
        self.student = frappe.get_doc("Student", self.request.student)

    def generate(self):
        """Generate certificate PDF"""
        try:
            # Check approval requirement
            if self.template.requires_approval and self.request.status != "Approved":
                frappe.throw(_("Certificate requires approval before generation"))

            # Generate certificate number if not exists
            if not self.request.certificate_number:
                self.request.certificate_number = self._generate_certificate_number()

            # Generate verification code
            if not self.request.verification_code:
                self.request.verification_code = self._generate_verification_code()

            # Generate QR code
            qr_code_path = self._generate_qr_code()

            # Prepare context for template
            context = self._prepare_context()
            context["qr_code"] = qr_code_path

            # Render HTML
            html_content = self._render_template(context)

            # Generate PDF
            pdf_options = {
                "page-size": self.template.page_size,
                "orientation": self.template.orientation,
                "margin-top": "10mm",
                "margin-bottom": "10mm",
                "margin-left": "10mm",
                "margin-right": "10mm"
            }

            pdf_content = get_pdf(html_content, options=pdf_options)

            # Save PDF
            file_name = f"{self.request.name}.pdf"
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "is_private": 0,
                "content": pdf_content,
                "attached_to_doctype": "Certificate Request",
                "attached_to_name": self.request.name
            })
            file_doc.save(ignore_permissions=True)

            # Update request
            self.request.generated_pdf = file_doc.file_url
            self.request.qr_code = qr_code_path
            self.request.status = "Generated"
            self.request.issue_date = frappe.utils.today()
            self.request.save(ignore_permissions=True)

            return {
                "success": True,
                "pdf_url": file_doc.file_url,
                "certificate_number": self.request.certificate_number
            }

        except Exception as e:
            frappe.log_error(f"Certificate generation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _generate_certificate_number(self):
        """Generate unique certificate number"""
        cert_type = self.template.certificate_type[:3].upper()
        year = frappe.utils.nowdate()[:4]

        # Get count for this type and year
        count = frappe.db.count(
            "Certificate Request",
            filters={
                "certificate_template": self.request.certificate_template,
                "certificate_number": ["like", f"{cert_type}/{year}/%"]
            }
        )

        return f"{cert_type}/{year}/{str(count + 1).zfill(5)}"

    def _generate_verification_code(self):
        """Generate verification code for certificate"""
        data = f"{self.request.name}-{self.request.student}-{frappe.utils.now()}"
        hash_code = hashlib.sha256(data.encode()).hexdigest()[:12].upper()
        return hash_code

    def _generate_qr_code(self):
        """Generate QR code for verification"""
        verification_url = frappe.utils.get_url(
            f"/api/method/university_erp.certificates.verify_certificate"
            f"?code={self.request.verification_code}"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(verification_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save to buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Convert to base64
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{qr_base64}"

    def _prepare_context(self):
        """Prepare context dictionary for template rendering"""
        # Get student enrollment details
        enrollment = frappe.get_all(
            "Program Enrollment",
            filters={"student": self.student.name, "docstatus": 1},
            fields=["*"],
            limit=1
        )
        enrollment = enrollment[0] if enrollment else {}

        context = {
            "student": self.student.as_dict(),
            "enrollment": enrollment,
            "certificate_number": self.request.certificate_number,
            "verification_code": self.request.verification_code,
            "issue_date": frappe.utils.format_date(
                self.request.issue_date or frappe.utils.today()
            ),
            "purpose": self.request.purpose,
            "template": self.template.as_dict()
        }

        # Add additional fields
        for field in self.request.additional_fields:
            context[field.field_name] = field.field_value

        # Add program details
        if self.request.program:
            program = frappe.get_doc("Program", self.request.program)
            context["program"] = program.as_dict()

        return context

    def _render_template(self, context):
        """Render HTML template with context"""
        # Base HTML structure
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Times New Roman', serif;
                    margin: 0;
                    padding: 20px;
                }}
                .certificate-container {{
                    position: relative;
                    border: 3px solid #000;
                    padding: 40px;
                    min-height: 700px;
                }}
                .watermark {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    opacity: 0.1;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .content {{
                    line-height: 1.8;
                    text-align: justify;
                }}
                .footer {{
                    margin-top: 50px;
                    display: flex;
                    justify-content: space-between;
                }}
                .signature {{
                    text-align: center;
                    margin-top: 30px;
                }}
                .qr-code {{
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    width: 80px;
                }}
                .verification-code {{
                    font-size: 10px;
                    text-align: center;
                    margin-top: 10px;
                }}
                {self.template.css_styles or ''}
            </style>
        </head>
        <body>
            <div class="certificate-container">
        """

        # Add watermark if configured
        if self.template.watermark_image:
            html += f'<img class="watermark" src="{self.template.watermark_image}" width="300">'

        # Add header if configured
        if self.template.header_image:
            html += f'''
            <div class="header">
                <img src="{self.template.header_image}" width="100%">
            </div>
            '''

        # Render main template content
        template = Template(self.template.html_template or self._get_default_template())
        html += template.render(**context)

        # Add QR code
        html += f'''
            <img class="qr-code" src="{context.get('qr_code', '')}" alt="Verification QR">
            <div class="verification-code">
                Verification Code: {context.get('verification_code', '')}
            </div>
        '''

        # Add footer if configured
        if self.template.footer_image:
            html += f'''
            <div style="position: absolute; bottom: 10px; left: 0; right: 0;">
                <img src="{self.template.footer_image}" width="100%">
            </div>
            '''

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def _get_default_template(self):
        """Get default template based on certificate type"""
        templates = {
            "Bonafide Certificate": """
                <div class="header">
                    <h1>BONAFIDE CERTIFICATE</h1>
                    <p>Certificate No: {{ certificate_number }}</p>
                </div>
                <div class="content">
                    <p>This is to certify that <strong>{{ student.student_name }}</strong>,
                    Son/Daughter of <strong>{{ student.custom_father_name }}</strong>,
                    bearing Roll No. <strong>{{ student.name }}</strong> is a bonafide student of this institution.</p>

                    <p>He/She is currently enrolled in <strong>{{ program.program_name }}</strong> program
                    for the academic year {{ enrollment.academic_year }}.</p>

                    {% if purpose %}
                    <p>This certificate is issued for the purpose of {{ purpose }}.</p>
                    {% endif %}
                </div>
                <div class="footer">
                    <div class="signature">
                        <p>_____________________</p>
                        <p>Principal</p>
                    </div>
                    <div class="signature">
                        <p>_____________________</p>
                        <p>Registrar</p>
                    </div>
                </div>
                <p style="text-align: center; margin-top: 20px;">
                    Date: {{ issue_date }}
                </p>
            """,

            "Character Certificate": """
                <div class="header">
                    <h1>CHARACTER CERTIFICATE</h1>
                    <p>Certificate No: {{ certificate_number }}</p>
                </div>
                <div class="content">
                    <p>This is to certify that <strong>{{ student.student_name }}</strong>,
                    bearing Roll No. <strong>{{ student.name }}</strong>, studied in this institution
                    from {{ enrollment.enrollment_date }} to {{ enrollment.graduation_date or 'present' }}.</p>

                    <p>During his/her stay in this institution, his/her character and conduct
                    have been found to be <strong>GOOD</strong>.</p>

                    <p>He/She bears good moral character and is not involved in any
                    anti-institutional or anti-national activities.</p>
                </div>
                <div class="footer">
                    <div class="signature">
                        <p>_____________________</p>
                        <p>Principal</p>
                    </div>
                </div>
                <p style="text-align: center; margin-top: 20px;">
                    Date: {{ issue_date }}
                </p>
            """,

            "No Dues Certificate": """
                <div class="header">
                    <h1>NO DUES CERTIFICATE</h1>
                    <p>Certificate No: {{ certificate_number }}</p>
                </div>
                <div class="content">
                    <p>This is to certify that <strong>{{ student.student_name }}</strong>,
                    bearing Roll No. <strong>{{ student.name }}</strong>, of <strong>{{ program.program_name }}</strong>
                    has no dues pending against his/her name in the following departments:</p>

                    <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
                        <tr>
                            <td style="border: 1px solid #000; padding: 10px;">Accounts Section</td>
                            <td style="border: 1px solid #000; padding: 10px;">✓ Cleared</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000; padding: 10px;">Library</td>
                            <td style="border: 1px solid #000; padding: 10px;">✓ Cleared</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000; padding: 10px;">Hostel</td>
                            <td style="border: 1px solid #000; padding: 10px;">✓ Cleared</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000; padding: 10px;">Department</td>
                            <td style="border: 1px solid #000; padding: 10px;">✓ Cleared</td>
                        </tr>
                    </table>
                </div>
                <div class="footer">
                    <div class="signature">
                        <p>_____________________</p>
                        <p>Accounts Officer</p>
                    </div>
                    <div class="signature">
                        <p>_____________________</p>
                        <p>Registrar</p>
                    </div>
                </div>
                <p style="text-align: center; margin-top: 20px;">
                    Date: {{ issue_date }}
                </p>
            """
        }

        return templates.get(self.template.certificate_type, templates["Bonafide Certificate"])


# API Endpoints

@frappe.whitelist()
def generate_certificate(certificate_request):
    """Generate certificate PDF"""
    generator = CertificateGenerator(certificate_request)
    return generator.generate()


@frappe.whitelist()
def approve_certificate(certificate_request, approve=True, reason=None):
    """Approve or reject certificate request"""
    request = frappe.get_doc("Certificate Request", certificate_request)

    if approve:
        request.status = "Approved"
        request.approved_by = frappe.session.user
        request.approval_date = frappe.utils.today()
    else:
        request.status = "Rejected"
        request.rejection_reason = reason

    request.save(ignore_permissions=True)

    return {"success": True, "status": request.status}


@frappe.whitelist(allow_guest=True)
def verify_certificate(code):
    """Verify certificate by verification code"""
    request = frappe.db.get_value(
        "Certificate Request",
        {"verification_code": code},
        ["name", "student", "certificate_template", "certificate_number",
         "issue_date", "status"],
        as_dict=True
    )

    if not request:
        return {
            "valid": False,
            "message": "Certificate not found"
        }

    if request.status != "Generated" and request.status != "Issued":
        return {
            "valid": False,
            "message": "Certificate is not valid"
        }

    student = frappe.get_doc("Student", request.student)
    template = frappe.get_doc("Certificate Template", request.certificate_template)

    return {
        "valid": True,
        "certificate_number": request.certificate_number,
        "certificate_type": template.certificate_type,
        "student_name": student.student_name,
        "issue_date": request.issue_date,
        "institution": frappe.db.get_single_value("Education Settings", "institution_name") or "University"
    }


@frappe.whitelist()
def bulk_generate_certificates(template, students, purpose=None):
    """Generate certificates in bulk for multiple students"""
    if isinstance(students, str):
        students = frappe.parse_json(students)

    results = []

    for student in students:
        try:
            # Create certificate request
            request = frappe.get_doc({
                "doctype": "Certificate Request",
                "student": student,
                "certificate_template": template,
                "purpose": purpose,
                "status": "Approved"  # Auto-approve for bulk
            })
            request.insert(ignore_permissions=True)

            # Generate certificate
            generator = CertificateGenerator(request)
            result = generator.generate()

            results.append({
                "student": student,
                "success": result.get("success"),
                "certificate_number": result.get("certificate_number"),
                "error": result.get("error")
            })

        except Exception as e:
            results.append({
                "student": student,
                "success": False,
                "error": str(e)
            })

    return results
```

---

## Implementation Checklist

### Week 1-2: Payment Gateway Integration
- [x] Create Payment Gateway Settings DocType
- [x] Create Payment Transaction DocType
- [x] Implement Razorpay integration
- [x] Implement PayU integration
- [x] Implement Stripe integration
- [x] Create webhook handlers (with HMAC signature verification)
- [x] Create payment reports (Payment Transaction Report)

### Week 2-3: SMS Gateway Integration
- [x] Create SMS Settings DocType
- [x] Create SMS Template DocType (Child Table)
- [x] Create SMS Log DocType
- [x] Implement MSG91 integration
- [x] Implement Twilio integration
- [x] Implement TextLocal integration
- [x] Implement Fast2SMS integration
- [x] Create event-triggered SMS handlers
- [x] Create SMS Delivery Report

### Week 3-4: Biometric Integration
- [x] Create Biometric Device DocType
- [x] Create Biometric Attendance Log DocType
- [x] Implement ZKTeco integration (via pyzk)
- [x] Create attendance sync scheduler
- [x] Create attendance processing logic
- [x] Add custom_biometric_id to Employee DocType
- [x] Add custom_biometric_id to Student DocType

### Week 4: DigiLocker Integration
- [x] Create DigiLocker Settings DocType
- [x] Create DigiLocker Document Type (Child Table)
- [x] Create DigiLocker Issued Document DocType
- [x] Implement DigiLocker API client
- [x] Create document issuance workflow
- [x] Create verification endpoint
- [x] Add custom_aadhaar_number to Student DocType
- [x] Add custom_digilocker_id to Student DocType

### Week 4-5: Certificate Generation
- [x] Create Certificate Template DocType
- [x] Create Certificate Field (Child Table)
- [x] Create Certificate Request DocType (Submittable)
- [x] Implement certificate generator
- [x] Create default templates for all types (10+ templates)
- [x] Implement QR code verification
- [x] Create bulk generation feature
- [x] Create Certificate Issuance Report

### Section F: Workspace & Reports
- [x] Create University Integrations Workspace
- [x] Create Payment Transaction Report
- [x] Create SMS Delivery Report
- [x] Create Certificate Issuance Report

---

## Testing Requirements

1. **Payment Gateway Testing**
   - Test sandbox mode for all gateways
   - Verify webhook handling
   - Test refund processing
   - Verify fee status updates

2. **SMS Gateway Testing**
   - Test with valid phone numbers
   - Verify template rendering
   - Test bulk SMS delivery
   - Check delivery status tracking

3. **Biometric Testing**
   - Test device connectivity
   - Verify attendance sync accuracy
   - Test attendance processing
   - Validate working hours calculation

4. **Certificate Testing**
   - Verify PDF generation
   - Test QR code verification
   - Validate certificate numbering
   - Test bulk generation

---

## Security Considerations

1. **API Keys**: Store all API keys and secrets securely using Frappe's Password fieldtype
2. **Webhooks**: Validate all webhook signatures
3. **Payment Data**: Never log sensitive payment information
4. **Certificate Verification**: Use cryptographic verification codes
5. **Access Control**: Implement proper role-based access for all features

---

## Implementation Summary

### Files Created

**DocTypes (14)**:
1. `payment_gateway_settings/` - Single DocType for payment gateway credentials
2. `payment_transaction/` - Standard DocType for transaction tracking
3. `sms_template/` - Child Table for SMS templates with DLT IDs
4. `sms_settings/` - Single DocType for SMS gateway configuration
5. `sms_log/` - Standard DocType for SMS delivery tracking
6. `biometric_device/` - Standard DocType for device configuration
7. `biometric_attendance_log/` - Standard DocType for punch records
8. `digilocker_document_type/` - Child Table for document type codes
9. `digilocker_settings/` - Single DocType for DigiLocker API config
10. `digilocker_issued_document/` - Standard DocType for issued documents
11. `certificate_template/` - Standard DocType for HTML/CSS templates
12. `certificate_field/` - Child Table for dynamic certificate fields
13. `certificate_request/` - Submittable DocType for certificate workflow

**Controllers (5)**:
1. `payment_gateway.py` - Razorpay, PayU, Stripe gateway implementations
2. `sms_gateway.py` - MSG91, Twilio, TextLocal, Fast2SMS implementations
3. `biometric_integration.py` - ZKTeco device integration via pyzk
4. `digilocker_integration.py` - DigiLocker API client
5. `certificate_generator.py` - PDF generation with QR codes

**Reports (3)**:
1. `payment_transaction_report/` - Payment analytics with charts
2. `sms_delivery_report/` - SMS delivery tracking with status
3. `certificate_issuance_report/` - Certificate statistics

**Workspace (1)**:
1. `university_integrations/` - Integration module workspace

**Custom Fields Added**:
- Student: `custom_biometric_id`, `custom_aadhaar_number`, `custom_digilocker_id`
- Employee: `custom_biometric_id`, `custom_biometric_enrolled`, `custom_biometric_enrollment_date`

---

**Document Version**: 2.0
**Created**: Phase 12 Planning
**Completed**: 2026-01-02
**Status**: Implemented
**Module Dependencies**: Fees, Attendance, Student modules
