# Phase 15: Communication & Notification System

## Overview
This phase implements a comprehensive communication system including SMS integration, WhatsApp Business API, push notifications, email automation, in-app notifications, and a digital notice board system.

**Duration**: 4-5 weeks
**Priority**: High (Required for User Experience)
**Dependencies**: Phase 1 (Foundation), Phase 13 (Portals)

---

## Part A: SMS Gateway Integration

### 1. SMS Settings DocType

```json
{
    "doctype": "DocType",
    "name": "SMS Settings",
    "module": "University ERP",
    "issingle": 1,
    "fields": [
        {
            "fieldname": "enabled",
            "fieldtype": "Check",
            "label": "SMS Enabled",
            "default": 0
        },
        {
            "fieldname": "provider",
            "fieldtype": "Select",
            "label": "SMS Provider",
            "options": "\nTwilio\nMSG91\nTextLocal\nAWS SNS\nCustom",
            "reqd": 1
        },
        {
            "fieldname": "api_credentials_section",
            "fieldtype": "Section Break",
            "label": "API Credentials"
        },
        {
            "fieldname": "api_key",
            "fieldtype": "Data",
            "label": "API Key"
        },
        {
            "fieldname": "api_secret",
            "fieldtype": "Password",
            "label": "API Secret"
        },
        {
            "fieldname": "auth_token",
            "fieldtype": "Password",
            "label": "Auth Token",
            "depends_on": "eval:doc.provider=='Twilio'"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "account_sid",
            "fieldtype": "Data",
            "label": "Account SID",
            "depends_on": "eval:doc.provider=='Twilio'"
        },
        {
            "fieldname": "sender_id",
            "fieldtype": "Data",
            "label": "Sender ID",
            "description": "Registered sender ID for SMS"
        },
        {
            "fieldname": "sender_number",
            "fieldtype": "Data",
            "label": "Sender Phone Number",
            "depends_on": "eval:doc.provider=='Twilio'"
        },
        {
            "fieldname": "settings_section",
            "fieldtype": "Section Break",
            "label": "Settings"
        },
        {
            "fieldname": "route",
            "fieldtype": "Select",
            "label": "Route",
            "options": "Transactional\nPromotional",
            "default": "Transactional"
        },
        {
            "fieldname": "dlt_entity_id",
            "fieldtype": "Data",
            "label": "DLT Entity ID",
            "description": "Required for Indian SMS regulations"
        },
        {
            "fieldname": "default_country_code",
            "fieldtype": "Data",
            "label": "Default Country Code",
            "default": "+91"
        },
        {
            "fieldname": "column_break_2",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "rate_limit",
            "fieldtype": "Int",
            "label": "Rate Limit (per minute)",
            "default": 100
        },
        {
            "fieldname": "retry_count",
            "fieldtype": "Int",
            "label": "Retry Count",
            "default": 3
        },
        {
            "fieldname": "test_mode",
            "fieldtype": "Check",
            "label": "Test Mode",
            "description": "Log SMS but don't send"
        },
        {
            "fieldname": "custom_api_section",
            "fieldtype": "Section Break",
            "label": "Custom API Settings",
            "depends_on": "eval:doc.provider=='Custom'"
        },
        {
            "fieldname": "api_url",
            "fieldtype": "Data",
            "label": "API URL"
        },
        {
            "fieldname": "request_method",
            "fieldtype": "Select",
            "label": "Request Method",
            "options": "GET\nPOST",
            "default": "POST"
        },
        {
            "fieldname": "request_template",
            "fieldtype": "Code",
            "label": "Request Template (JSON)",
            "options": "JSON"
        }
    ]
}
```

### 2. SMS Gateway Manager

```python
# sms_gateway.py

import frappe
from frappe import _
import requests
import json


class SMSGateway:
    """Unified SMS gateway interface"""

    def __init__(self):
        self.settings = frappe.get_single("SMS Settings")
        if not self.settings.enabled:
            frappe.throw(_("SMS service is not enabled"))

        self.provider = self.settings.provider

    def send(self, phone_number, message, template_id=None):
        """Send SMS to a phone number"""
        # Normalize phone number
        phone = self.normalize_phone(phone_number)

        if self.settings.test_mode:
            return self.log_test_sms(phone, message)

        # Route to appropriate provider
        providers = {
            "Twilio": self._send_twilio,
            "MSG91": self._send_msg91,
            "TextLocal": self._send_textlocal,
            "AWS SNS": self._send_aws_sns,
            "Custom": self._send_custom
        }

        sender = providers.get(self.provider)
        if not sender:
            frappe.throw(_(f"Unknown SMS provider: {self.provider}"))

        result = sender(phone, message, template_id)
        self.log_sms(phone, message, result)

        return result

    def send_bulk(self, recipients, message, template_id=None):
        """Send SMS to multiple recipients"""
        results = []
        for recipient in recipients:
            phone = recipient.get("phone") if isinstance(recipient, dict) else recipient
            try:
                result = self.send(phone, message, template_id)
                results.append({"phone": phone, "success": True, "result": result})
            except Exception as e:
                results.append({"phone": phone, "success": False, "error": str(e)})

        return results

    def normalize_phone(self, phone):
        """Normalize phone number with country code"""
        phone = str(phone).strip()

        # Remove any non-numeric characters except +
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')

        # Add country code if not present
        if not phone.startswith('+'):
            if phone.startswith('0'):
                phone = phone[1:]
            phone = self.settings.default_country_code + phone

        return phone

    def _send_twilio(self, phone, message, template_id):
        """Send via Twilio"""
        from twilio.rest import Client

        client = Client(
            self.settings.account_sid,
            self.settings.get_password("auth_token")
        )

        response = client.messages.create(
            body=message,
            from_=self.settings.sender_number,
            to=phone
        )

        return {
            "message_id": response.sid,
            "status": response.status,
            "provider": "Twilio"
        }

    def _send_msg91(self, phone, message, template_id):
        """Send via MSG91"""
        url = "https://api.msg91.com/api/v5/flow/"

        headers = {
            "authkey": self.settings.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "template_id": template_id or self.settings.dlt_entity_id,
            "sender": self.settings.sender_id,
            "short_url": "0",
            "mobiles": phone.replace("+", ""),
            "VAR1": message
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if response.status_code != 200:
            frappe.throw(_(f"MSG91 error: {result.get('message', 'Unknown error')}"))

        return {
            "message_id": result.get("request_id"),
            "status": "sent",
            "provider": "MSG91"
        }

    def _send_textlocal(self, phone, message, template_id):
        """Send via TextLocal"""
        url = "https://api.textlocal.in/send/"

        params = {
            "apikey": self.settings.api_key,
            "numbers": phone.replace("+91", ""),
            "message": message,
            "sender": self.settings.sender_id
        }

        response = requests.post(url, data=params)
        result = response.json()

        if result.get("status") != "success":
            frappe.throw(_(f"TextLocal error: {result.get('errors', 'Unknown error')}"))

        return {
            "message_id": result.get("batch_id"),
            "status": "sent",
            "provider": "TextLocal"
        }

    def _send_aws_sns(self, phone, message, template_id):
        """Send via AWS SNS"""
        import boto3

        client = boto3.client(
            'sns',
            aws_access_key_id=self.settings.api_key,
            aws_secret_access_key=self.settings.get_password("api_secret"),
            region_name='ap-south-1'
        )

        response = client.publish(
            PhoneNumber=phone,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': self.settings.sender_id
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )

        return {
            "message_id": response.get("MessageId"),
            "status": "sent",
            "provider": "AWS SNS"
        }

    def _send_custom(self, phone, message, template_id):
        """Send via custom API"""
        url = self.settings.api_url

        # Parse template and substitute values
        template = json.loads(self.settings.request_template or "{}")
        template = self._substitute_values(template, phone, message, template_id)

        if self.settings.request_method == "POST":
            response = requests.post(url, json=template, headers={
                "Authorization": f"Bearer {self.settings.api_key}"
            })
        else:
            response = requests.get(url, params=template, headers={
                "Authorization": f"Bearer {self.settings.api_key}"
            })

        return {
            "message_id": response.text[:50],
            "status": "sent" if response.status_code == 200 else "failed",
            "provider": "Custom"
        }

    def _substitute_values(self, template, phone, message, template_id):
        """Substitute values in template"""
        if isinstance(template, dict):
            return {k: self._substitute_values(v, phone, message, template_id) for k, v in template.items()}
        elif isinstance(template, str):
            return template.replace("{{phone}}", phone).replace("{{message}}", message).replace("{{template_id}}", template_id or "")
        return template

    def log_sms(self, phone, message, result):
        """Log SMS in database"""
        frappe.get_doc({
            "doctype": "SMS Log",
            "phone_number": phone,
            "message": message[:500],
            "provider": self.provider,
            "message_id": result.get("message_id"),
            "status": result.get("status"),
            "sent_at": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)

    def log_test_sms(self, phone, message):
        """Log test SMS without sending"""
        frappe.get_doc({
            "doctype": "SMS Log",
            "phone_number": phone,
            "message": message[:500],
            "provider": "Test Mode",
            "status": "test",
            "sent_at": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)

        return {
            "message_id": f"test_{frappe.generate_hash(length=8)}",
            "status": "test",
            "provider": "Test Mode"
        }


# SMS Log DocType
SMS_LOG_DOCTYPE = {
    "doctype": "DocType",
    "name": "SMS Log",
    "module": "University ERP",
    "fields": [
        {"fieldname": "phone_number", "fieldtype": "Data", "label": "Phone Number"},
        {"fieldname": "message", "fieldtype": "Small Text", "label": "Message"},
        {"fieldname": "provider", "fieldtype": "Data", "label": "Provider"},
        {"fieldname": "message_id", "fieldtype": "Data", "label": "Message ID"},
        {"fieldname": "status", "fieldtype": "Data", "label": "Status"},
        {"fieldname": "sent_at", "fieldtype": "Datetime", "label": "Sent At"},
        {"fieldname": "delivery_status", "fieldtype": "Data", "label": "Delivery Status"},
        {"fieldname": "error_message", "fieldtype": "Small Text", "label": "Error Message"}
    ]
}
```

### 3. SMS Templates

```python
# sms_templates.py

import frappe
from frappe import _


class SMSTemplateManager:
    """Manage SMS templates with DLT compliance"""

    # Pre-defined templates
    TEMPLATES = {
        "attendance_alert": {
            "name": "Attendance Alert",
            "message": "Dear Parent, Your ward {student_name} was marked {status} on {date} for {course}. -University",
            "category": "Attendance",
            "dlt_template_id": ""
        },
        "fee_reminder": {
            "name": "Fee Reminder",
            "message": "Dear {student_name}, Your fee of Rs.{amount} is due on {due_date}. Please pay to avoid late fee. -University",
            "category": "Fee",
            "dlt_template_id": ""
        },
        "exam_schedule": {
            "name": "Exam Schedule",
            "message": "Dear {student_name}, Your {exam_name} exam is scheduled on {date} at {time} in {room}. -University",
            "category": "Examination",
            "dlt_template_id": ""
        },
        "result_published": {
            "name": "Result Published",
            "message": "Dear {student_name}, Results for {exam_name} have been published. Login to portal to view. -University",
            "category": "Result",
            "dlt_template_id": ""
        },
        "otp_verification": {
            "name": "OTP Verification",
            "message": "Your OTP for University Portal is {otp}. Valid for 10 minutes. Do not share. -University",
            "category": "Security",
            "dlt_template_id": ""
        },
        "admission_status": {
            "name": "Admission Status",
            "message": "Dear {applicant_name}, Your admission application status: {status}. Login to portal for details. -University",
            "category": "Admission",
            "dlt_template_id": ""
        },
        "library_due": {
            "name": "Library Due Reminder",
            "message": "Dear {student_name}, Book '{book_title}' is due on {due_date}. Please return to avoid fine. -University",
            "category": "Library",
            "dlt_template_id": ""
        },
        "hostel_visitor": {
            "name": "Hostel Visitor Alert",
            "message": "Dear {student_name}, Visitor {visitor_name} is here to meet you at hostel reception. -University",
            "category": "Hostel",
            "dlt_template_id": ""
        },
        "emergency_alert": {
            "name": "Emergency Alert",
            "message": "URGENT: {message} Please take necessary action immediately. -University",
            "category": "Emergency",
            "dlt_template_id": ""
        },
        "payment_confirmation": {
            "name": "Payment Confirmation",
            "message": "Dear {student_name}, Payment of Rs.{amount} received. Receipt: {receipt_no}. Thank you. -University",
            "category": "Fee",
            "dlt_template_id": ""
        }
    }

    @staticmethod
    def get_template(template_key):
        """Get SMS template by key"""
        template = frappe.db.get_value(
            "SMS Template",
            {"template_key": template_key, "enabled": 1},
            ["message", "dlt_template_id"],
            as_dict=True
        )

        if not template:
            # Fall back to default
            default = SMSTemplateManager.TEMPLATES.get(template_key)
            if default:
                return default
            frappe.throw(_(f"SMS template not found: {template_key}"))

        return template

    @staticmethod
    def render_template(template_key, context):
        """Render SMS template with context"""
        template = SMSTemplateManager.get_template(template_key)
        message = template.get("message", "")

        # Substitute variables
        for key, value in context.items():
            message = message.replace(f"{{{key}}}", str(value))

        return message, template.get("dlt_template_id")


# SMS Template DocType
SMS_TEMPLATE_DOCTYPE = {
    "doctype": "DocType",
    "name": "SMS Template",
    "module": "University ERP",
    "fields": [
        {"fieldname": "template_name", "fieldtype": "Data", "label": "Template Name", "reqd": 1},
        {"fieldname": "template_key", "fieldtype": "Data", "label": "Template Key", "reqd": 1, "unique": 1},
        {"fieldname": "category", "fieldtype": "Select", "label": "Category",
         "options": "Attendance\nFee\nExamination\nResult\nAdmission\nLibrary\nHostel\nEmergency\nSecurity\nGeneral"},
        {"fieldname": "message", "fieldtype": "Small Text", "label": "Message Template", "reqd": 1},
        {"fieldname": "dlt_template_id", "fieldtype": "Data", "label": "DLT Template ID"},
        {"fieldname": "enabled", "fieldtype": "Check", "label": "Enabled", "default": 1},
        {"fieldname": "variables", "fieldtype": "Small Text", "label": "Available Variables", "read_only": 1}
    ]
}
```

---

## Part B: WhatsApp Business Integration

### 1. WhatsApp Settings DocType

```json
{
    "doctype": "DocType",
    "name": "WhatsApp Settings",
    "module": "University ERP",
    "issingle": 1,
    "fields": [
        {
            "fieldname": "enabled",
            "fieldtype": "Check",
            "label": "WhatsApp Enabled"
        },
        {
            "fieldname": "provider",
            "fieldtype": "Select",
            "label": "Provider",
            "options": "\nMeta Business API\nTwilio WhatsApp\nGupshup\nWATI"
        },
        {
            "fieldname": "api_section",
            "fieldtype": "Section Break",
            "label": "API Configuration"
        },
        {
            "fieldname": "phone_number_id",
            "fieldtype": "Data",
            "label": "Phone Number ID"
        },
        {
            "fieldname": "business_account_id",
            "fieldtype": "Data",
            "label": "Business Account ID"
        },
        {
            "fieldname": "access_token",
            "fieldtype": "Password",
            "label": "Access Token"
        },
        {
            "fieldname": "column_break_api",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "api_version",
            "fieldtype": "Data",
            "label": "API Version",
            "default": "v17.0"
        },
        {
            "fieldname": "webhook_verify_token",
            "fieldtype": "Data",
            "label": "Webhook Verify Token"
        },
        {
            "fieldname": "templates_section",
            "fieldtype": "Section Break",
            "label": "Message Templates"
        },
        {
            "fieldname": "approved_templates",
            "fieldtype": "Table",
            "label": "Approved Templates",
            "options": "WhatsApp Template"
        }
    ]
}
```

### 2. WhatsApp Gateway

```python
# whatsapp_gateway.py

import frappe
from frappe import _
import requests
import json


class WhatsAppGateway:
    """WhatsApp Business API Gateway"""

    def __init__(self):
        self.settings = frappe.get_single("WhatsApp Settings")
        if not self.settings.enabled:
            frappe.throw(_("WhatsApp service is not enabled"))

        self.base_url = f"https://graph.facebook.com/{self.settings.api_version}"

    def send_template_message(self, phone_number, template_name, template_params=None, language="en"):
        """Send WhatsApp template message"""
        phone = self.normalize_phone(phone_number)

        url = f"{self.base_url}/{self.settings.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('access_token')}",
            "Content-Type": "application/json"
        }

        # Build template components
        components = []
        if template_params:
            body_params = [{"type": "text", "text": str(p)} for p in template_params.get("body", [])]
            if body_params:
                components.append({
                    "type": "body",
                    "parameters": body_params
                })

            header_params = template_params.get("header", [])
            if header_params:
                components.append({
                    "type": "header",
                    "parameters": [{"type": "text", "text": str(p)} for p in header_params]
                })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if response.status_code != 200:
            error = result.get("error", {}).get("message", "Unknown error")
            frappe.throw(_(f"WhatsApp error: {error}"))

        self.log_message(phone, template_name, result)

        return {
            "message_id": result.get("messages", [{}])[0].get("id"),
            "status": "sent"
        }

    def send_text_message(self, phone_number, message):
        """Send plain text message (only to users who messaged in last 24h)"""
        phone = self.normalize_phone(phone_number)

        url = f"{self.base_url}/{self.settings.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('access_token')}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if response.status_code != 200:
            error = result.get("error", {}).get("message", "Unknown error")
            frappe.throw(_(f"WhatsApp error: {error}"))

        self.log_message(phone, "text_message", result, message)

        return {
            "message_id": result.get("messages", [{}])[0].get("id"),
            "status": "sent"
        }

    def send_document(self, phone_number, document_url, caption=None, filename=None):
        """Send document via WhatsApp"""
        phone = self.normalize_phone(phone_number)

        url = f"{self.base_url}/{self.settings.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('access_token')}",
            "Content-Type": "application/json"
        }

        document_payload = {"link": document_url}
        if caption:
            document_payload["caption"] = caption
        if filename:
            document_payload["filename"] = filename

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "document",
            "document": document_payload
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        return {
            "message_id": result.get("messages", [{}])[0].get("id"),
            "status": "sent"
        }

    def send_image(self, phone_number, image_url, caption=None):
        """Send image via WhatsApp"""
        phone = self.normalize_phone(phone_number)

        url = f"{self.base_url}/{self.settings.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('access_token')}",
            "Content-Type": "application/json"
        }

        image_payload = {"link": image_url}
        if caption:
            image_payload["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "image",
            "image": image_payload
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        return {
            "message_id": result.get("messages", [{}])[0].get("id"),
            "status": "sent"
        }

    def normalize_phone(self, phone):
        """Normalize phone number for WhatsApp"""
        phone = str(phone).strip()
        phone = ''.join(c for c in phone if c.isdigit())

        # WhatsApp requires number without + but with country code
        if phone.startswith('0'):
            phone = '91' + phone[1:]
        elif not phone.startswith('91') and len(phone) == 10:
            phone = '91' + phone

        return phone

    def log_message(self, phone, template, result, message=None):
        """Log WhatsApp message"""
        frappe.get_doc({
            "doctype": "WhatsApp Log",
            "phone_number": phone,
            "template_name": template,
            "message": message,
            "message_id": result.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "sent_at": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():
    """Handle WhatsApp webhook callbacks"""
    settings = frappe.get_single("WhatsApp Settings")

    # Webhook verification
    if frappe.request.method == "GET":
        mode = frappe.request.args.get("hub.mode")
        token = frappe.request.args.get("hub.verify_token")
        challenge = frappe.request.args.get("hub.challenge")

        if mode == "subscribe" and token == settings.webhook_verify_token:
            return challenge
        return "Forbidden", 403

    # Handle incoming messages
    if frappe.request.method == "POST":
        data = frappe.request.get_json()

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    process_incoming_message(change.get("value", {}))

        return {"status": "ok"}


def process_incoming_message(data):
    """Process incoming WhatsApp message"""
    messages = data.get("messages", [])

    for message in messages:
        phone = message.get("from")
        message_type = message.get("type")
        message_id = message.get("id")

        # Log incoming message
        frappe.get_doc({
            "doctype": "WhatsApp Log",
            "phone_number": phone,
            "message_id": message_id,
            "direction": "Incoming",
            "message_type": message_type,
            "message": message.get("text", {}).get("body") if message_type == "text" else "",
            "received_at": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)

        # Auto-reply or route to support
        handle_incoming_message(phone, message)


def handle_incoming_message(phone, message):
    """Handle incoming message with auto-reply or routing"""
    message_text = message.get("text", {}).get("body", "").lower()

    # Simple keyword-based auto-reply
    auto_replies = {
        "fee": "Your current fee status will be sent shortly. Please wait.",
        "result": "To check results, please visit the student portal.",
        "attendance": "Your attendance report will be sent shortly.",
        "help": "Available commands: fee, result, attendance, timetable, contact"
    }

    for keyword, reply in auto_replies.items():
        if keyword in message_text:
            gateway = WhatsAppGateway()
            gateway.send_text_message(phone, reply)
            return

    # Default reply
    gateway = WhatsAppGateway()
    gateway.send_text_message(
        phone,
        "Thank you for your message. Please visit student portal or contact administration for assistance."
    )
```

---

## Part C: Push Notifications

### 1. Push Notification Settings

```json
{
    "doctype": "DocType",
    "name": "Push Notification Settings",
    "module": "University ERP",
    "issingle": 1,
    "fields": [
        {
            "fieldname": "enabled",
            "fieldtype": "Check",
            "label": "Push Notifications Enabled"
        },
        {
            "fieldname": "provider",
            "fieldtype": "Select",
            "label": "Provider",
            "options": "\nFirebase Cloud Messaging\nOneSignal\nPusher"
        },
        {
            "fieldname": "firebase_section",
            "fieldtype": "Section Break",
            "label": "Firebase Configuration",
            "depends_on": "eval:doc.provider=='Firebase Cloud Messaging'"
        },
        {
            "fieldname": "firebase_project_id",
            "fieldtype": "Data",
            "label": "Firebase Project ID"
        },
        {
            "fieldname": "firebase_server_key",
            "fieldtype": "Password",
            "label": "Server Key"
        },
        {
            "fieldname": "firebase_service_account",
            "fieldtype": "Code",
            "label": "Service Account JSON",
            "options": "JSON"
        },
        {
            "fieldname": "onesignal_section",
            "fieldtype": "Section Break",
            "label": "OneSignal Configuration",
            "depends_on": "eval:doc.provider=='OneSignal'"
        },
        {
            "fieldname": "onesignal_app_id",
            "fieldtype": "Data",
            "label": "OneSignal App ID"
        },
        {
            "fieldname": "onesignal_api_key",
            "fieldtype": "Password",
            "label": "OneSignal API Key"
        },
        {
            "fieldname": "web_push_section",
            "fieldtype": "Section Break",
            "label": "Web Push Configuration"
        },
        {
            "fieldname": "vapid_public_key",
            "fieldtype": "Data",
            "label": "VAPID Public Key"
        },
        {
            "fieldname": "vapid_private_key",
            "fieldtype": "Password",
            "label": "VAPID Private Key"
        }
    ]
}
```

### 2. Push Notification Manager

```python
# push_notification.py

import frappe
from frappe import _
import json
import requests


class PushNotificationManager:
    """Manage push notifications across platforms"""

    def __init__(self):
        self.settings = frappe.get_single("Push Notification Settings")
        if not self.settings.enabled:
            frappe.throw(_("Push notifications are not enabled"))

    def send_to_user(self, user, title, body, data=None, image=None):
        """Send push notification to a user"""
        # Get user's device tokens
        tokens = self.get_user_tokens(user)

        if not tokens:
            return {"success": False, "error": "No device tokens found"}

        results = []
        for token in tokens:
            result = self.send_to_token(token.token, title, body, data, image, token.platform)
            results.append(result)

        return {"success": True, "results": results}

    def send_to_topic(self, topic, title, body, data=None, image=None):
        """Send push notification to a topic"""
        if self.settings.provider == "Firebase Cloud Messaging":
            return self._send_fcm_topic(topic, title, body, data, image)
        elif self.settings.provider == "OneSignal":
            return self._send_onesignal_segment(topic, title, body, data, image)

    def send_to_token(self, token, title, body, data=None, image=None, platform="android"):
        """Send push notification to specific token"""
        if self.settings.provider == "Firebase Cloud Messaging":
            return self._send_fcm(token, title, body, data, image, platform)
        elif self.settings.provider == "OneSignal":
            return self._send_onesignal(token, title, body, data, image)

    def _send_fcm(self, token, title, body, data, image, platform):
        """Send via Firebase Cloud Messaging"""
        url = "https://fcm.googleapis.com/fcm/send"

        headers = {
            "Authorization": f"key={self.settings.get_password('firebase_server_key')}",
            "Content-Type": "application/json"
        }

        notification = {
            "title": title,
            "body": body
        }

        if image:
            notification["image"] = image

        payload = {
            "to": token,
            "notification": notification,
            "data": data or {}
        }

        # Platform-specific options
        if platform == "ios":
            payload["apns"] = {
                "payload": {
                    "aps": {
                        "sound": "default",
                        "badge": 1
                    }
                }
            }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        self.log_notification(token, title, body, result)

        return {
            "success": result.get("success", 0) > 0,
            "message_id": result.get("results", [{}])[0].get("message_id")
        }

    def _send_fcm_topic(self, topic, title, body, data, image):
        """Send FCM notification to topic"""
        url = "https://fcm.googleapis.com/fcm/send"

        headers = {
            "Authorization": f"key={self.settings.get_password('firebase_server_key')}",
            "Content-Type": "application/json"
        }

        notification = {"title": title, "body": body}
        if image:
            notification["image"] = image

        payload = {
            "to": f"/topics/{topic}",
            "notification": notification,
            "data": data or {}
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def _send_onesignal(self, token, title, body, data, image):
        """Send via OneSignal"""
        url = "https://onesignal.com/api/v1/notifications"

        headers = {
            "Authorization": f"Basic {self.settings.get_password('onesignal_api_key')}",
            "Content-Type": "application/json"
        }

        payload = {
            "app_id": self.settings.onesignal_app_id,
            "include_player_ids": [token],
            "headings": {"en": title},
            "contents": {"en": body},
            "data": data or {}
        }

        if image:
            payload["big_picture"] = image

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def _send_onesignal_segment(self, segment, title, body, data, image):
        """Send OneSignal notification to segment"""
        url = "https://onesignal.com/api/v1/notifications"

        headers = {
            "Authorization": f"Basic {self.settings.get_password('onesignal_api_key')}",
            "Content-Type": "application/json"
        }

        payload = {
            "app_id": self.settings.onesignal_app_id,
            "included_segments": [segment],
            "headings": {"en": title},
            "contents": {"en": body},
            "data": data or {}
        }

        if image:
            payload["big_picture"] = image

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def get_user_tokens(self, user):
        """Get device tokens for a user"""
        return frappe.get_all(
            "User Device Token",
            filters={"user": user, "active": 1},
            fields=["token", "platform", "device_id"]
        )

    def log_notification(self, token, title, body, result):
        """Log push notification"""
        frappe.get_doc({
            "doctype": "Push Notification Log",
            "token": token[:50],
            "title": title,
            "body": body[:500],
            "result": json.dumps(result),
            "sent_at": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)


# User Device Token DocType
USER_DEVICE_TOKEN_DOCTYPE = {
    "doctype": "DocType",
    "name": "User Device Token",
    "module": "University ERP",
    "fields": [
        {"fieldname": "user", "fieldtype": "Link", "label": "User", "options": "User", "reqd": 1},
        {"fieldname": "token", "fieldtype": "Data", "label": "Device Token", "reqd": 1},
        {"fieldname": "platform", "fieldtype": "Select", "label": "Platform", "options": "android\nios\nweb"},
        {"fieldname": "device_id", "fieldtype": "Data", "label": "Device ID"},
        {"fieldname": "device_name", "fieldtype": "Data", "label": "Device Name"},
        {"fieldname": "active", "fieldtype": "Check", "label": "Active", "default": 1},
        {"fieldname": "last_used", "fieldtype": "Datetime", "label": "Last Used"}
    ]
}


@frappe.whitelist()
def register_device_token(token, platform, device_id=None, device_name=None):
    """Register device token for push notifications"""
    user = frappe.session.user

    # Check if token exists
    existing = frappe.db.get_value(
        "User Device Token",
        {"user": user, "token": token},
        "name"
    )

    if existing:
        # Update existing
        frappe.db.set_value("User Device Token", existing, {
            "active": 1,
            "last_used": frappe.utils.now_datetime()
        })
    else:
        # Create new
        frappe.get_doc({
            "doctype": "User Device Token",
            "user": user,
            "token": token,
            "platform": platform,
            "device_id": device_id,
            "device_name": device_name,
            "active": 1,
            "last_used": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)

    return {"success": True}


@frappe.whitelist()
def unregister_device_token(token):
    """Unregister device token"""
    frappe.db.set_value(
        "User Device Token",
        {"user": frappe.session.user, "token": token},
        "active", 0
    )
    return {"success": True}
```

---

## Part D: In-App Notification System

### 1. Notification Center

```python
# notification_center.py

import frappe
from frappe import _
from frappe.utils import now_datetime, add_days


class NotificationCenter:
    """Central notification management system"""

    NOTIFICATION_TYPES = {
        "info": {"icon": "info-circle", "color": "blue"},
        "success": {"icon": "check-circle", "color": "green"},
        "warning": {"icon": "exclamation-triangle", "color": "orange"},
        "error": {"icon": "times-circle", "color": "red"},
        "announcement": {"icon": "bullhorn", "color": "purple"}
    }

    @staticmethod
    def send(user, title, message, notification_type="info", link=None, category=None, expires_in_days=30):
        """Send notification to a user"""
        notification = frappe.get_doc({
            "doctype": "User Notification",
            "user": user,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "link": link,
            "category": category or "General",
            "read": 0,
            "expires_on": add_days(now_datetime(), expires_in_days)
        })
        notification.insert(ignore_permissions=True)

        # Real-time notification via Socket.IO
        frappe.publish_realtime(
            event="new_notification",
            message={
                "notification": notification.name,
                "title": title,
                "message": message,
                "type": notification_type
            },
            user=user
        )

        return notification.name

    @staticmethod
    def send_to_role(role, title, message, notification_type="info", link=None, category=None):
        """Send notification to all users with a role"""
        users = frappe.get_all(
            "Has Role",
            filters={"role": role, "parenttype": "User"},
            pluck="parent"
        )

        notifications = []
        for user in users:
            if user != "Administrator":
                notif = NotificationCenter.send(user, title, message, notification_type, link, category)
                notifications.append(notif)

        return notifications

    @staticmethod
    def send_to_students(program=None, batch=None, title=None, message=None, notification_type="info", link=None):
        """Send notification to students"""
        filters = {}
        if program:
            filters["program"] = program
        if batch:
            filters["batch"] = batch

        students = frappe.get_all("Student", filters=filters, fields=["user"])

        notifications = []
        for student in students:
            if student.user:
                notif = NotificationCenter.send(student.user, title, message, notification_type, link, "Academic")
                notifications.append(notif)

        return notifications

    @staticmethod
    def get_user_notifications(user, limit=50, unread_only=False, category=None):
        """Get notifications for a user"""
        filters = {
            "user": user,
            "expires_on": [">=", now_datetime()]
        }

        if unread_only:
            filters["read"] = 0

        if category:
            filters["category"] = category

        notifications = frappe.get_all(
            "User Notification",
            filters=filters,
            fields=["name", "title", "message", "notification_type", "link", "category", "read", "creation"],
            order_by="creation desc",
            limit=limit
        )

        return notifications

    @staticmethod
    def mark_as_read(notification_name):
        """Mark notification as read"""
        frappe.db.set_value("User Notification", notification_name, "read", 1)
        return {"success": True}

    @staticmethod
    def mark_all_read(user):
        """Mark all notifications as read for user"""
        frappe.db.sql("""
            UPDATE `tabUser Notification`
            SET `read` = 1
            WHERE user = %s AND `read` = 0
        """, user)
        return {"success": True}

    @staticmethod
    def get_unread_count(user):
        """Get unread notification count"""
        return frappe.db.count(
            "User Notification",
            filters={
                "user": user,
                "read": 0,
                "expires_on": [">=", now_datetime()]
            }
        )

    @staticmethod
    def delete_old_notifications(days=90):
        """Delete notifications older than specified days"""
        cutoff_date = add_days(now_datetime(), -days)
        frappe.db.sql("""
            DELETE FROM `tabUser Notification`
            WHERE creation < %s
        """, cutoff_date)


# User Notification DocType
USER_NOTIFICATION_DOCTYPE = {
    "doctype": "DocType",
    "name": "User Notification",
    "module": "University ERP",
    "fields": [
        {"fieldname": "user", "fieldtype": "Link", "label": "User", "options": "User", "reqd": 1},
        {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
        {"fieldname": "message", "fieldtype": "Small Text", "label": "Message"},
        {"fieldname": "notification_type", "fieldtype": "Select", "label": "Type",
         "options": "info\nsuccess\nwarning\nerror\nannouncement"},
        {"fieldname": "link", "fieldtype": "Data", "label": "Link"},
        {"fieldname": "category", "fieldtype": "Select", "label": "Category",
         "options": "General\nAcademic\nFee\nExamination\nLibrary\nHostel\nPlacement\nEmergency"},
        {"fieldname": "read", "fieldtype": "Check", "label": "Read"},
        {"fieldname": "expires_on", "fieldtype": "Datetime", "label": "Expires On"}
    ],
    "permissions": [
        {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "All", "read": 1, "if_owner": 1}
    ]
}


# API endpoints
@frappe.whitelist()
def get_notifications(limit=50, unread_only=False, category=None):
    """Get current user's notifications"""
    return NotificationCenter.get_user_notifications(
        frappe.session.user,
        limit=int(limit),
        unread_only=bool(unread_only),
        category=category
    )


@frappe.whitelist()
def mark_notification_read(notification):
    """Mark notification as read"""
    return NotificationCenter.mark_as_read(notification)


@frappe.whitelist()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    return NotificationCenter.mark_all_read(frappe.session.user)


@frappe.whitelist()
def get_unread_count():
    """Get unread notification count"""
    return NotificationCenter.get_unread_count(frappe.session.user)
```

---

## Part E: Email Automation

### 1. Email Automation Rules

```python
# email_automation.py

import frappe
from frappe import _
from frappe.utils import add_days, today, now_datetime


class EmailAutomation:
    """Automated email sending based on triggers"""

    @staticmethod
    def send_welcome_email(student):
        """Send welcome email to new student"""
        template = frappe.db.get_single_value("University Settings", "student_welcome_email_template")

        if not template:
            return

        student_doc = frappe.get_doc("Student", student)

        if not student_doc.student_email_id:
            return

        frappe.sendmail(
            recipients=[student_doc.student_email_id],
            subject="Welcome to University",
            template=template,
            args={
                "student": student_doc,
                "portal_link": frappe.utils.get_url("/student_portal")
            },
            reference_doctype="Student",
            reference_name=student
        )

    @staticmethod
    def send_fee_reminder(days_before_due=7):
        """Send fee reminder emails"""
        due_date = add_days(today(), days_before_due)

        pending_fees = frappe.get_all(
            "Fees",
            filters={
                "docstatus": 1,
                "outstanding_amount": [">", 0],
                "due_date": due_date
            },
            fields=["name", "student", "student_name", "grand_total", "outstanding_amount", "due_date"]
        )

        for fee in pending_fees:
            student = frappe.get_doc("Student", fee.student)

            if not student.student_email_id:
                continue

            frappe.sendmail(
                recipients=[student.student_email_id],
                subject=f"Fee Payment Reminder - Due on {fee.due_date}",
                template="fee_reminder",
                args={
                    "student": student,
                    "fee": fee,
                    "payment_link": frappe.utils.get_url(f"/student_portal/fees?pay={fee.name}")
                },
                reference_doctype="Fees",
                reference_name=fee.name
            )

    @staticmethod
    def send_attendance_report_to_parents():
        """Send weekly attendance report to parents"""
        from_date = add_days(today(), -7)

        # Get students with low attendance
        students_with_low_attendance = frappe.db.sql("""
            SELECT
                s.name as student,
                s.student_name,
                sg.guardian,
                sg.guardian_name,
                g.email_address as guardian_email,
                COUNT(CASE WHEN sa.status = 'Present' THEN 1 END) * 100.0 / COUNT(*) as attendance_percentage
            FROM `tabStudent` s
            JOIN `tabStudent Guardian` sg ON sg.parent = s.name
            JOIN `tabGuardian` g ON g.name = sg.guardian
            JOIN `tabStudent Attendance` sa ON sa.student = s.name
            WHERE sa.date >= %s
            GROUP BY s.name, sg.guardian
            HAVING attendance_percentage < 75
        """, from_date, as_dict=True)

        for record in students_with_low_attendance:
            if not record.guardian_email:
                continue

            frappe.sendmail(
                recipients=[record.guardian_email],
                subject=f"Weekly Attendance Report - {record.student_name}",
                template="attendance_report_parent",
                args={
                    "student_name": record.student_name,
                    "guardian_name": record.guardian_name,
                    "attendance_percentage": round(record.attendance_percentage, 2),
                    "from_date": from_date,
                    "to_date": today()
                }
            )

    @staticmethod
    def send_exam_reminder(days_before=3):
        """Send exam reminder to students"""
        exam_date = add_days(today(), days_before)

        exams = frappe.get_all(
            "Exam Schedule",
            filters={
                "exam_date": exam_date,
                "docstatus": 1
            },
            fields=["name", "course", "exam_date", "start_time", "room"]
        )

        for exam in exams:
            # Get enrolled students
            students = frappe.db.sql("""
                SELECT DISTINCT s.name, s.student_name, s.student_email_id
                FROM `tabStudent` s
                JOIN `tabCourse Registration` cr ON cr.student = s.name
                WHERE cr.course = %s AND cr.docstatus = 1
            """, exam.course, as_dict=True)

            for student in students:
                if not student.student_email_id:
                    continue

                frappe.sendmail(
                    recipients=[student.student_email_id],
                    subject=f"Exam Reminder: {exam.course} on {exam.exam_date}",
                    template="exam_reminder",
                    args={
                        "student": student,
                        "exam": exam
                    }
                )

    @staticmethod
    def send_result_notification(assessment_plan):
        """Notify students when results are published"""
        results = frappe.get_all(
            "Assessment Result",
            filters={
                "assessment_plan": assessment_plan,
                "docstatus": 1
            },
            fields=["student", "student_name", "total_score", "grade"]
        )

        for result in results:
            student = frappe.get_doc("Student", result.student)

            if not student.student_email_id:
                continue

            frappe.sendmail(
                recipients=[student.student_email_id],
                subject="Your Exam Results Are Available",
                template="result_notification",
                args={
                    "student": student,
                    "result": result,
                    "portal_link": frappe.utils.get_url("/student_portal/results")
                }
            )


# Scheduled jobs
def send_daily_fee_reminders():
    """Scheduled job to send fee reminders"""
    EmailAutomation.send_fee_reminder(days_before_due=7)
    EmailAutomation.send_fee_reminder(days_before_due=3)
    EmailAutomation.send_fee_reminder(days_before_due=1)


def send_weekly_attendance_reports():
    """Scheduled job to send weekly attendance reports"""
    EmailAutomation.send_attendance_report_to_parents()


def send_exam_reminders():
    """Scheduled job to send exam reminders"""
    EmailAutomation.send_exam_reminder(days_before=3)
    EmailAutomation.send_exam_reminder(days_before=1)
```

---

## Part F: Digital Notice Board

### 1. Notice Board DocType

```json
{
    "doctype": "DocType",
    "name": "Notice Board",
    "module": "University ERP",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "title",
            "fieldtype": "Data",
            "label": "Title",
            "reqd": 1
        },
        {
            "fieldname": "notice_type",
            "fieldtype": "Select",
            "label": "Notice Type",
            "options": "General\nAcademic\nExamination\nAdmission\nPlacement\nHostel\nLibrary\nSports\nCultural\nEmergency",
            "reqd": 1
        },
        {
            "fieldname": "priority",
            "fieldtype": "Select",
            "label": "Priority",
            "options": "Low\nMedium\nHigh\nUrgent",
            "default": "Medium"
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "publish_date",
            "fieldtype": "Date",
            "label": "Publish Date",
            "reqd": 1,
            "default": "Today"
        },
        {
            "fieldname": "expiry_date",
            "fieldtype": "Date",
            "label": "Expiry Date"
        },
        {
            "fieldname": "is_pinned",
            "fieldtype": "Check",
            "label": "Pin to Top"
        },
        {
            "fieldname": "content_section",
            "fieldtype": "Section Break",
            "label": "Content"
        },
        {
            "fieldname": "content",
            "fieldtype": "Text Editor",
            "label": "Notice Content",
            "reqd": 1
        },
        {
            "fieldname": "attachment",
            "fieldtype": "Attach",
            "label": "Attachment"
        },
        {
            "fieldname": "target_audience_section",
            "fieldtype": "Section Break",
            "label": "Target Audience"
        },
        {
            "fieldname": "audience_type",
            "fieldtype": "Select",
            "label": "Audience Type",
            "options": "All\nStudents Only\nFaculty Only\nStaff Only\nParents Only\nSpecific Programs\nSpecific Departments",
            "default": "All"
        },
        {
            "fieldname": "target_programs",
            "fieldtype": "Table MultiSelect",
            "label": "Target Programs",
            "options": "Notice Target Program",
            "depends_on": "eval:doc.audience_type=='Specific Programs'"
        },
        {
            "fieldname": "target_departments",
            "fieldtype": "Table MultiSelect",
            "label": "Target Departments",
            "options": "Notice Target Department",
            "depends_on": "eval:doc.audience_type=='Specific Departments'"
        },
        {
            "fieldname": "notification_section",
            "fieldtype": "Section Break",
            "label": "Notifications"
        },
        {
            "fieldname": "send_email",
            "fieldtype": "Check",
            "label": "Send Email Notification"
        },
        {
            "fieldname": "send_sms",
            "fieldtype": "Check",
            "label": "Send SMS Notification"
        },
        {
            "fieldname": "send_push",
            "fieldtype": "Check",
            "label": "Send Push Notification"
        },
        {
            "fieldname": "send_whatsapp",
            "fieldtype": "Check",
            "label": "Send WhatsApp Notification"
        }
    ],
    "permissions": [
        {
            "role": "System Manager",
            "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1
        },
        {
            "role": "Academic Admin",
            "read": 1, "write": 1, "create": 1, "submit": 1
        },
        {
            "role": "Student",
            "read": 1
        },
        {
            "role": "Faculty",
            "read": 1
        }
    ]
}
```

### 2. Notice Board Manager

```python
# notice_board.py

import frappe
from frappe import _
from frappe.utils import today, now_datetime


class NoticeBoardManager:
    """Manage notice board operations"""

    @staticmethod
    def get_notices(user=None, notice_type=None, limit=20):
        """Get active notices for user"""
        filters = {
            "docstatus": 1,
            "publish_date": ["<=", today()],
        }

        # Add expiry filter
        or_filters = [
            ["expiry_date", "is", "not set"],
            ["expiry_date", ">=", today()]
        ]

        if notice_type:
            filters["notice_type"] = notice_type

        notices = frappe.get_all(
            "Notice Board",
            filters=filters,
            or_filters=or_filters,
            fields=[
                "name", "title", "notice_type", "priority", "publish_date",
                "content", "attachment", "is_pinned", "audience_type"
            ],
            order_by="is_pinned desc, priority desc, publish_date desc",
            limit=limit
        )

        # Filter by audience if user specified
        if user:
            notices = [n for n in notices if NoticeBoardManager.is_notice_for_user(n, user)]

        return notices

    @staticmethod
    def is_notice_for_user(notice, user):
        """Check if notice is applicable to user"""
        if notice.audience_type == "All":
            return True

        roles = frappe.get_roles(user)

        if notice.audience_type == "Students Only" and "Student" in roles:
            return True
        if notice.audience_type == "Faculty Only" and "Faculty" in roles:
            return True
        if notice.audience_type == "Staff Only" and "Employee" in roles:
            return True
        if notice.audience_type == "Parents Only" and "Guardian" in roles:
            return True

        # Check specific programs
        if notice.audience_type == "Specific Programs":
            student = frappe.db.get_value("Student", {"user": user}, "name")
            if student:
                student_program = frappe.db.get_value(
                    "Program Enrollment",
                    {"student": student, "docstatus": 1},
                    "program"
                )
                target_programs = frappe.get_all(
                    "Notice Target Program",
                    filters={"parent": notice.name},
                    pluck="program"
                )
                if student_program in target_programs:
                    return True

        return False

    @staticmethod
    def publish_notice(notice_name):
        """Publish notice and send notifications"""
        notice = frappe.get_doc("Notice Board", notice_name)

        if notice.docstatus != 1:
            frappe.throw(_("Notice must be submitted before publishing"))

        # Get target users
        users = NoticeBoardManager.get_target_users(notice)

        # Send notifications based on settings
        if notice.send_email:
            NoticeBoardManager.send_email_notifications(notice, users)

        if notice.send_sms:
            NoticeBoardManager.send_sms_notifications(notice, users)

        if notice.send_push:
            NoticeBoardManager.send_push_notifications(notice, users)

        if notice.send_whatsapp:
            NoticeBoardManager.send_whatsapp_notifications(notice, users)

        # Create in-app notifications
        for user in users:
            NotificationCenter.send(
                user=user.get("user"),
                title=f"New Notice: {notice.title}",
                message=notice.title,
                notification_type="announcement",
                link=f"/notice-board/{notice.name}",
                category=notice.notice_type
            )

        return {"success": True, "users_notified": len(users)}

    @staticmethod
    def get_target_users(notice):
        """Get list of target users for notice"""
        users = []

        if notice.audience_type == "All":
            users = frappe.get_all("User", filters={"enabled": 1}, fields=["name as user", "email", "mobile_no"])

        elif notice.audience_type == "Students Only":
            students = frappe.get_all(
                "Student",
                filters={"enabled": 1},
                fields=["user", "student_email_id as email", "phone as mobile_no"]
            )
            users = [s for s in students if s.user]

        elif notice.audience_type == "Faculty Only":
            faculty = frappe.db.sql("""
                SELECT u.name as user, u.email, e.cell_number as mobile_no
                FROM `tabUser` u
                JOIN `tabEmployee` e ON e.user_id = u.name
                WHERE u.enabled = 1 AND e.department LIKE '%%Faculty%%'
            """, as_dict=True)
            users = faculty

        elif notice.audience_type == "Specific Programs":
            target_programs = frappe.get_all(
                "Notice Target Program",
                filters={"parent": notice.name},
                pluck="program"
            )

            students = frappe.db.sql("""
                SELECT DISTINCT s.user, s.student_email_id as email, s.phone as mobile_no
                FROM `tabStudent` s
                JOIN `tabProgram Enrollment` pe ON pe.student = s.name
                WHERE pe.program IN %s AND pe.docstatus = 1 AND s.user IS NOT NULL
            """, (target_programs,), as_dict=True)
            users = students

        return users

    @staticmethod
    def send_email_notifications(notice, users):
        """Send email notifications"""
        emails = [u.email for u in users if u.get("email")]

        if not emails:
            return

        frappe.sendmail(
            recipients=emails,
            subject=f"Notice: {notice.title}",
            template="notice_board_notification",
            args={
                "notice": notice,
                "link": frappe.utils.get_url(f"/notice-board/{notice.name}")
            },
            reference_doctype="Notice Board",
            reference_name=notice.name
        )

    @staticmethod
    def send_sms_notifications(notice, users):
        """Send SMS notifications"""
        sms_gateway = SMSGateway()

        message = f"New Notice: {notice.title}. Visit portal for details. -University"

        for user in users:
            if user.get("mobile_no"):
                try:
                    sms_gateway.send(user.mobile_no, message)
                except Exception:
                    pass

    @staticmethod
    def send_push_notifications(notice, users):
        """Send push notifications"""
        push_manager = PushNotificationManager()

        for user in users:
            try:
                push_manager.send_to_user(
                    user=user.get("user"),
                    title=f"New Notice: {notice.notice_type}",
                    body=notice.title,
                    data={
                        "type": "notice",
                        "notice_id": notice.name
                    }
                )
            except Exception:
                pass

    @staticmethod
    def send_whatsapp_notifications(notice, users):
        """Send WhatsApp notifications"""
        try:
            whatsapp = WhatsAppGateway()

            for user in users:
                if user.get("mobile_no"):
                    whatsapp.send_template_message(
                        phone_number=user.mobile_no,
                        template_name="notice_alert",
                        template_params={
                            "body": [notice.title, notice.notice_type]
                        }
                    )
        except Exception:
            pass


# Portal API
@frappe.whitelist()
def get_notices(notice_type=None, limit=20):
    """Get notices for current user"""
    return NoticeBoardManager.get_notices(
        user=frappe.session.user,
        notice_type=notice_type,
        limit=int(limit)
    )


@frappe.whitelist()
def get_notice_detail(notice_name):
    """Get notice details"""
    notice = frappe.get_doc("Notice Board", notice_name)

    if notice.docstatus != 1:
        frappe.throw(_("Notice not found"))

    if not NoticeBoardManager.is_notice_for_user(notice.as_dict(), frappe.session.user):
        frappe.throw(_("You don't have permission to view this notice"))

    return notice.as_dict()
```

---

## Part G: Emergency Broadcast System

### 1. Emergency Alert

```python
# emergency_broadcast.py

import frappe
from frappe import _
from frappe.utils import now_datetime


class EmergencyBroadcast:
    """Emergency notification broadcast system"""

    ALERT_LEVELS = {
        "info": {"priority": 1, "color": "blue"},
        "warning": {"priority": 2, "color": "orange"},
        "critical": {"priority": 3, "color": "red"},
        "emergency": {"priority": 4, "color": "darkred"}
    }

    @staticmethod
    def broadcast(title, message, alert_level="warning", target_audience="all"):
        """Broadcast emergency alert"""

        # Create alert record
        alert = frappe.get_doc({
            "doctype": "Emergency Alert",
            "title": title,
            "message": message,
            "alert_level": alert_level,
            "target_audience": target_audience,
            "broadcast_time": now_datetime(),
            "status": "Broadcasting"
        })
        alert.insert(ignore_permissions=True)

        # Get target users
        if target_audience == "all":
            users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
        elif target_audience == "students":
            users = frappe.get_all("Student", filters={"enabled": 1}, pluck="user")
        elif target_audience == "faculty":
            users = frappe.db.sql("""
                SELECT user_id FROM `tabEmployee`
                WHERE department LIKE '%%Faculty%%' AND status = 'Active'
            """, pluck=True)
        else:
            users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")

        users = [u for u in users if u]

        # Send through all channels simultaneously
        EmergencyBroadcast._send_all_channels(alert, users, title, message)

        # Update status
        alert.status = "Sent"
        alert.users_reached = len(users)
        alert.save(ignore_permissions=True)

        return {
            "alert_id": alert.name,
            "users_notified": len(users)
        }

    @staticmethod
    def _send_all_channels(alert, users, title, message):
        """Send through all available channels"""
        # Real-time notification
        frappe.publish_realtime(
            event="emergency_alert",
            message={
                "alert_id": alert.name,
                "title": title,
                "message": message,
                "level": alert.alert_level
            },
            user=users
        )

        # In-app notifications
        for user in users:
            NotificationCenter.send(
                user=user,
                title=f"EMERGENCY: {title}",
                message=message,
                notification_type="error",
                category="Emergency"
            )

        # Push notifications
        try:
            push_manager = PushNotificationManager()
            push_manager.send_to_topic(
                "emergency",
                f"EMERGENCY: {title}",
                message,
                {"type": "emergency", "alert_id": alert.name}
            )
        except Exception:
            pass

        # SMS (background job for large lists)
        frappe.enqueue(
            EmergencyBroadcast._send_emergency_sms,
            users=users,
            title=title,
            message=message,
            queue="short"
        )

    @staticmethod
    def _send_emergency_sms(users, title, message):
        """Send emergency SMS in background"""
        try:
            sms_gateway = SMSGateway()

            # Get phone numbers
            phones = []
            for user in users:
                phone = frappe.db.get_value("User", user, "mobile_no")
                if not phone:
                    # Try student phone
                    phone = frappe.db.get_value("Student", {"user": user}, "phone")
                if phone:
                    phones.append(phone)

            sms_message = f"EMERGENCY: {title}. {message[:100]}... -University"

            for phone in phones:
                try:
                    sms_gateway.send(phone, sms_message)
                except Exception:
                    continue

        except Exception as e:
            frappe.log_error(f"Emergency SMS error: {str(e)}", "Emergency Broadcast")


# Emergency Alert DocType
EMERGENCY_ALERT_DOCTYPE = {
    "doctype": "DocType",
    "name": "Emergency Alert",
    "module": "University ERP",
    "fields": [
        {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
        {"fieldname": "message", "fieldtype": "Small Text", "label": "Message", "reqd": 1},
        {"fieldname": "alert_level", "fieldtype": "Select", "label": "Alert Level",
         "options": "info\nwarning\ncritical\nemergency"},
        {"fieldname": "target_audience", "fieldtype": "Select", "label": "Target Audience",
         "options": "all\nstudents\nfaculty\nstaff"},
        {"fieldname": "broadcast_time", "fieldtype": "Datetime", "label": "Broadcast Time"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status",
         "options": "Draft\nBroadcasting\nSent\nCancelled"},
        {"fieldname": "users_reached", "fieldtype": "Int", "label": "Users Reached"}
    ]
}


@frappe.whitelist()
def send_emergency_alert(title, message, alert_level="warning", target_audience="all"):
    """API to send emergency alert"""
    # Only allow authorized users
    if not frappe.has_permission("Emergency Alert", "create"):
        frappe.throw(_("You don't have permission to send emergency alerts"))

    return EmergencyBroadcast.broadcast(title, message, alert_level, target_audience)
```

---

## Implementation Checklist

### Phase 15 Tasks

- [x] **Week 1: SMS Integration** ✅
  - [x] Create SMS Settings DocType
  - [x] Implement Twilio integration
  - [x] Implement MSG91 integration
  - [x] Create SMS Templates
  - [x] Build SMS Log system
  - [x] Test SMS delivery
  - [x] Create SMS Queue for batch processing
  - [x] Add schedule_sms() and schedule_bulk_sms() functions

- [x] **Week 2: WhatsApp Integration** ✅
  - [x] Create WhatsApp Settings DocType
  - [x] Implement Meta Business API
  - [x] Build webhook handler
  - [x] Create WhatsApp templates
  - [x] Test message delivery

- [x] **Week 3: Push Notifications** ✅
  - [x] Create Push Notification Settings
  - [x] Implement Firebase integration
  - [x] Build device token management
  - [x] Create notification topics
  - [x] Test push delivery

- [x] **Week 4: Notice Board & Email** ✅
  - [x] Create Notice Board DocType
  - [x] Build audience targeting
  - [x] Implement email automation
  - [x] Create scheduled jobs
  - [x] Build emergency broadcast
  - [x] Create Email Queue Extended with retry/bounce handling

- [x] **Week 5: Testing & Integration** ✅
  - [x] Integration testing
  - [x] Unit tests for all modules
  - [x] Documentation
  - [x] Unified Communication Manager with fallback logic
  - [x] Enhanced Notification Preferences (WhatsApp, language)

---

## Scheduled Jobs Configuration

```python
# hooks.py additions

scheduler_events = {
    "daily": [
        "university_erp.email_automation.send_daily_fee_reminders",
        "university_erp.email_automation.send_exam_reminders"
    ],
    "weekly": [
        "university_erp.email_automation.send_weekly_attendance_reports"
    ],
    "cron": {
        "0 6 * * *": [  # Every day at 6 AM
            "university_erp.notification_center.NotificationCenter.delete_old_notifications"
        ]
    }
}
```

---

## Implementation Status

### Completed Components (100%) ✅

#### SMS Gateway Integration ✅
- SMS Settings DocType with multi-provider support (Twilio, MSG91, TextLocal, AWS SNS, Custom)
- SMS Template DocType with DLT compliance
- SMS Log DocType for message tracking
- SMS Gateway Manager (`sms_gateway.py`) with:
  - Multi-provider routing
  - Phone number normalization
  - Test mode support
  - Message logging

#### SMS Queue System ✅ (NEW)
- SMS Queue DocType (`university_integrations/doctype/sms_queue/`)
- Batch processing with priority scheduling (Low/Normal/High/Urgent)
- `schedule_sms()` function for single SMS scheduling
- `schedule_bulk_sms()` function for bulk SMS with personalization
- `process_sms_queue()` scheduled task with rate limiting
- Retry mechanism with configurable max retries
- Batch ID tracking for bulk operations

#### Email Queue Extended ✅ (NEW)
- Email Queue Extended DocType (`university_integrations/doctype/email_queue_extended/`)
- Priority-based email queue (Low/Normal/High/Urgent)
- `queue_email()` function for email scheduling
- Retry mechanism with bounce handling
- Delivery tracking (opened, clicked, bounced)
- `handle_bounce()` for bounce notifications
- `get_email_delivery_stats()` for analytics

#### WhatsApp Business Integration ✅
- WhatsApp Settings DocType with multi-provider support (Meta, Twilio, Gupshup, WATI)
- WhatsApp Template DocType with button support
- WhatsApp Log DocType for message tracking
- WhatsApp Gateway (`whatsapp_gateway.py`) with:
  - Template message sending
  - Text message sending
  - Media message sending
  - Webhook handler for incoming messages
  - Auto-reply functionality

#### Push Notification System ✅
- Push Notification Settings DocType (FCM, OneSignal)
- User Device Token DocType
- Push Notification Log DocType
- Firebase Admin integration (`firebase_admin.py`)
- Push Notification Manager (`push_notification.py`) with:
  - FCM integration
  - OneSignal integration
  - Topic/segment messaging
  - Device token registration API

#### In-App Notification System ✅
- User Notification DocType
- Notification Preference DocType with:
  - Per-channel enable/disable (email, SMS, push, in_app, WhatsApp)
  - Preferred language setting
  - Quiet hours configuration
  - Category-specific preferences
- Notification Center class (`notification_center.py`) with:
  - Real-time delivery via Socket.IO
  - Role-based notifications
  - Student/Faculty targeting
  - Read/unread tracking
  - Scheduled cleanup

#### Notice Board System ✅
- Notice Board DocType (Submittable)
- Notice Target Program child table
- Notice Target Department child table
- Notice View Log DocType for tracking
- Multi-channel notification on submit
- Audience-based filtering
- Email template for notices

#### Emergency Broadcast System ✅
- Emergency Alert DocType with comprehensive fields
- Emergency Acknowledgment DocType
- Emergency Broadcast Manager (`emergency_broadcast.py`) with:
  - Multi-channel broadcasting (SMS, Push, WhatsApp, Email)
  - Quick broadcast functions (fire, lockdown, evacuation)
  - Acknowledgment tracking
  - All-clear notifications
  - Real-time alerts

#### Unified Communication System ✅ (NEW)
- Unified Communication Manager (`unified_communication.py`) with:
  - `unified_send()` entry point for multi-channel notifications
  - Channel priority ordering (in_app → email → push → sms → whatsapp)
  - Smart fallback on channel failure
  - Rate limiting per channel
  - Message deduplication using cache and hash
  - Quiet hours enforcement
  - User preference respect
  - Batch sending support

#### Unit Tests ✅ (NEW)
- `test_whatsapp_gateway.py` - WhatsApp gateway, phone normalization, templates
- `test_push_notification.py` - Firebase admin, device tokens, topics
- `test_notification_center.py` - Notification CRUD, preferences
- `test_notice_board.py` - Notice creation, view logs, API
- `test_emergency_broadcast.py` - Alerts, acknowledgments, broadcast
- `test_communication_flow.py` - End-to-end integration tests

### Files Created

#### DocTypes
- `university_integrations/doctype/sms_queue/sms_queue.json`
- `university_integrations/doctype/sms_queue/sms_queue.py`
- `university_integrations/doctype/email_queue_extended/email_queue_extended.json`
- `university_integrations/doctype/email_queue_extended/email_queue_extended.py`
- `university_erp/doctype/notification_preference/notification_preference.json` (enhanced)

#### Core Modules
- `university_erp/unified_communication.py`
- `university_integrations/firebase_admin.py`
- `university_integrations/push_notification.py`
- `university_integrations/whatsapp_gateway.py`
- `university_erp/notification_center.py`
- `university_erp/emergency_broadcast.py`

#### Test Files
- `university_integrations/tests/test_whatsapp_gateway.py`
- `university_integrations/tests/test_push_notification.py`
- `university_integrations/tests/test_notification_center.py`
- `university_integrations/tests/test_notice_board.py`
- `university_integrations/tests/test_emergency_broadcast.py`
- `university_integrations/tests/test_communication_flow.py`

---

**Document Version:** 2.0
**Created:** January 2026
**Updated:** January 2026 (Phase Complete - 100%)
**Author:** University ERP Team
