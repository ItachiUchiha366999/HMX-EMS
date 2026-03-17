# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
SMS Gateway Integration Module
Supports: MSG91, Twilio, TextLocal, Fast2SMS
"""

import frappe
from frappe import _
import requests
import json
import re


class SMSGateway:
    """Base SMS gateway handler"""

    def __init__(self):
        self.settings = frappe.get_single("University SMS Settings")

        if not self.settings.enabled:
            frappe.throw(_("SMS gateway is not enabled"))

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

    def _check_daily_limit(self):
        """Check if daily limit is reached"""
        if self.settings.sms_sent_today >= self.settings.daily_limit:
            frappe.throw(_("Daily SMS limit reached"))

    def _increment_count(self):
        """Increment daily SMS count"""
        frappe.db.set_value(
            "University SMS Settings", "University SMS Settings",
            "sms_sent_today", self.settings.sms_sent_today + 1
        )

    def _normalize_phone(self, phone):
        """Normalize phone number"""
        phone = str(phone).strip()
        phone = re.sub(r'[^0-9+]', '', phone)

        if len(phone) == 10:
            phone = "91" + phone
        elif phone.startswith("0"):
            phone = "91" + phone[1:]
        elif phone.startswith("+"):
            phone = phone[1:]

        return phone

    def _create_log(self, recipient, message, status, response=None, error=None, message_id=None):
        """Create SMS log entry"""
        log = frappe.get_doc({
            "doctype": "SMS Log",
            "recipient": recipient,
            "message": message,
            "sms_gateway": self.settings.sms_gateway,
            "status": status,
            "message_id": message_id,
            "gateway_response": json.dumps(response) if response else None,
            "error_message": error
        })
        log.insert(ignore_permissions=True)
        return log.name


class MSG91Gateway(SMSGateway):
    """MSG91 SMS gateway implementation"""

    def __init__(self):
        super().__init__()
        self.auth_key = self.settings.get_password("msg91_auth_key")
        self.sender_id = self.settings.sender_id
        self.route = self.settings.msg91_route or "4"
        self.base_url = "https://control.msg91.com/api/v5"
        # DLT Compliance settings
        self.dlt_enabled = self.settings.dlt_enabled
        self.dlt_entity_id = self.settings.dlt_entity_id
        self.dlt_template_id = self.settings.dlt_template_id
        self.dlt_header = self.settings.dlt_header

    def send_sms(self, recipient, message, template_id=None, dlt_template_id=None, dlt_header=None):
        """Send SMS via MSG91 with DLT compliance support"""
        try:
            self._check_daily_limit()

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
                "VAR1": message
            }

            # Add DLT compliance parameters if enabled
            if self.dlt_enabled:
                # Use provided DLT template ID or fall back to settings
                effective_dlt_template_id = dlt_template_id or self.dlt_template_id
                effective_dlt_header = dlt_header or self.dlt_header

                if self.dlt_entity_id:
                    payload["DLT_TE_ID"] = self.dlt_entity_id
                if effective_dlt_template_id:
                    payload["DLT_TM_ID"] = effective_dlt_template_id
                if effective_dlt_header:
                    payload["sender"] = effective_dlt_header

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response_data = response.json()

            success = response_data.get("type") == "success"
            status = "Sent" if success else "Failed"

            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status=status,
                response=response_data,
                error=response_data.get("message") if not success else None,
                message_id=response_data.get("request_id")
            )

            if success:
                self._increment_count()

            return {
                "success": success,
                "log": log_name,
                "message_id": response_data.get("request_id"),
                "response": response_data
            }

        except Exception as e:
            frappe.log_error(f"MSG91 SMS failed: {str(e)}", "SMS Gateway")
            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status="Failed",
                error=str(e)
            )
            return {"success": False, "error": str(e), "log": log_name}


class TwilioGateway(SMSGateway):
    """Twilio SMS gateway implementation"""

    def __init__(self):
        super().__init__()
        self.account_sid = self.settings.twilio_account_sid
        self.auth_token = self.settings.get_password("twilio_auth_token")
        self.from_number = self.settings.twilio_phone_number

    def send_sms(self, recipient, message, template_id=None):
        """Send SMS via Twilio"""
        try:
            self._check_daily_limit()

            from twilio.rest import Client

            client = Client(self.account_sid, self.auth_token)

            # Normalize phone number to E.164 format
            if not recipient.startswith("+"):
                recipient = "+91" + self._normalize_phone(recipient)[-10:]

            sms = client.messages.create(
                body=message,
                from_=self.from_number,
                to=recipient
            )

            success = sms.status in ["queued", "sent", "delivered"]
            status = "Sent" if success else "Failed"

            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status=status,
                response={"sid": sms.sid, "status": sms.status},
                message_id=sms.sid
            )

            if success:
                self._increment_count()

            return {
                "success": success,
                "log": log_name,
                "message_id": sms.sid
            }

        except ImportError:
            frappe.throw(_("Twilio library not installed. Run: pip install twilio"))
        except Exception as e:
            frappe.log_error(f"Twilio SMS failed: {str(e)}", "SMS Gateway")
            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status="Failed",
                error=str(e)
            )
            return {"success": False, "error": str(e), "log": log_name}


class TextLocalGateway(SMSGateway):
    """TextLocal SMS gateway implementation"""

    def __init__(self):
        super().__init__()
        self.api_key = self.settings.get_password("textlocal_api_key")
        self.sender = self.settings.textlocal_sender
        self.base_url = "https://api.textlocal.in/send/"

    def send_sms(self, recipient, message, template_id=None):
        """Send SMS via TextLocal"""
        try:
            self._check_daily_limit()

            recipient = self._normalize_phone(recipient)

            params = {
                "apikey": self.api_key,
                "numbers": recipient,
                "message": message,
                "sender": self.sender
            }

            response = requests.post(self.base_url, data=params, timeout=30)
            response_data = response.json()

            success = response_data.get("status") == "success"
            status = "Sent" if success else "Failed"

            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status=status,
                response=response_data,
                error=response_data.get("errors", [{}])[0].get("message") if not success else None
            )

            if success:
                self._increment_count()

            return {
                "success": success,
                "log": log_name,
                "response": response_data
            }

        except Exception as e:
            frappe.log_error(f"TextLocal SMS failed: {str(e)}", "SMS Gateway")
            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status="Failed",
                error=str(e)
            )
            return {"success": False, "error": str(e), "log": log_name}


class Fast2SMSGateway(SMSGateway):
    """Fast2SMS gateway implementation with DLT compliance"""

    def __init__(self):
        super().__init__()
        self.api_key = self.settings.get_password("fast2sms_api_key")
        self.sender_id = self.settings.fast2sms_sender_id
        self.base_url = "https://www.fast2sms.com/dev/bulkV2"
        # DLT Compliance settings
        self.dlt_enabled = self.settings.dlt_enabled
        self.dlt_entity_id = self.settings.dlt_entity_id
        self.dlt_template_id = self.settings.dlt_template_id
        self.dlt_header = self.settings.dlt_header

    def send_sms(self, recipient, message, template_id=None, dlt_template_id=None, dlt_header=None):
        """Send SMS via Fast2SMS with DLT compliance support"""
        try:
            self._check_daily_limit()

            recipient = self._normalize_phone(recipient)[-10:]  # Fast2SMS uses 10 digit

            headers = {
                "authorization": self.api_key,
                "Content-Type": "application/json"
            }

            # Determine effective DLT settings
            effective_dlt_template_id = dlt_template_id or self.dlt_template_id
            effective_sender_id = dlt_header or self.dlt_header or self.sender_id

            payload = {
                "route": "dlt",
                "sender_id": effective_sender_id,
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": recipient
            }

            # Add DLT compliance parameters if enabled
            if self.dlt_enabled:
                if self.dlt_entity_id:
                    payload["entity_id"] = self.dlt_entity_id
                if effective_dlt_template_id:
                    payload["message_id"] = effective_dlt_template_id  # Fast2SMS uses message_id for DLT template

            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response_data = response.json()

            success = response_data.get("return")
            status = "Sent" if success else "Failed"

            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status=status,
                response=response_data,
                error=response_data.get("message") if not success else None,
                message_id=response_data.get("request_id")
            )

            if success:
                self._increment_count()

            return {
                "success": success,
                "log": log_name,
                "response": response_data
            }

        except Exception as e:
            frappe.log_error(f"Fast2SMS failed: {str(e)}", "SMS Gateway")
            log_name = self._create_log(
                recipient=recipient,
                message=message,
                status="Failed",
                error=str(e)
            )
            return {"success": False, "error": str(e), "log": log_name}


# Factory function
def get_sms_gateway():
    """Get configured SMS gateway instance"""
    settings = frappe.get_single("University SMS Settings")

    if not settings.enabled:
        frappe.throw(_("SMS gateway is not enabled"))

    if settings.sms_gateway == "MSG91":
        return MSG91Gateway()
    elif settings.sms_gateway == "Twilio":
        return TwilioGateway()
    elif settings.sms_gateway == "TextLocal":
        return TextLocalGateway()
    elif settings.sms_gateway == "Fast2SMS":
        return Fast2SMSGateway()
    else:
        frappe.throw(_("SMS gateway not configured"))


# API Endpoints

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
    """Send SMS using predefined template with DLT compliance support"""
    try:
        settings = frappe.get_single("University SMS Settings")

        if not settings.enabled:
            return {"success": False, "error": "SMS gateway not enabled"}

        template = settings.get_template(event_trigger)

        if not template:
            frappe.log_error(f"SMS template not found for event: {event_trigger}", "SMS Gateway")
            return {"success": False, "error": "Template not found"}

        # Replace variables in template
        message = template.message_template
        for key, value in variables.items():
            message = message.replace(f"{{{{{key}}}}}", str(value))

        gateway = get_sms_gateway()

        # Pass per-template DLT settings (template_id is also used as DLT template ID)
        # The template can have its own dlt_header that overrides the default
        dlt_template_id = template.template_id  # DLT Template ID from SMS Template
        dlt_header = getattr(template, 'dlt_header', None)  # Per-template DLT header override

        return gateway.send_sms(
            recipient,
            message,
            template_id=template.template_id,
            dlt_template_id=dlt_template_id,
            dlt_header=dlt_header
        )

    except Exception as e:
        frappe.log_error(f"Templated SMS failed: {str(e)}", "SMS Gateway")
        return {"success": False, "error": str(e)}


# Event Handlers

def on_fee_due(fee):
    """Send fee due reminder SMS"""
    try:
        student = frappe.get_doc("Student", fee.student)
        if student.student_mobile_number:
            send_templated_sms(
                "Fee Due Reminder",
                student.student_mobile_number,
                {
                    "student_name": student.student_name,
                    "amount": fee.outstanding_amount,
                    "due_date": frappe.utils.format_date(fee.due_date)
                }
            )
    except Exception as e:
        frappe.log_error(f"Fee due SMS failed: {str(e)}", "SMS Gateway")


def on_payment_success(transaction):
    """Send payment confirmation SMS"""
    try:
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
    except Exception as e:
        frappe.log_error(f"Payment confirmation SMS failed: {str(e)}", "SMS Gateway")


def send_attendance_alert(student, date, subject, status):
    """Send attendance alert to student/parent"""
    try:
        student_doc = frappe.get_doc("Student", student)

        # Send to student
        if student_doc.student_mobile_number:
            send_templated_sms(
                "Attendance Alert",
                student_doc.student_mobile_number,
                {
                    "student_name": student_doc.student_name,
                    "date": frappe.utils.format_date(date),
                    "subject": subject,
                    "status": status
                }
            )

        # Send to guardian
        if hasattr(student_doc, "guardians"):
            for guardian in student_doc.guardians:
                if guardian.guardian_mobile:
                    send_templated_sms(
                        "Attendance Alert",
                        guardian.guardian_mobile,
                        {
                            "student_name": student_doc.student_name,
                            "date": frappe.utils.format_date(date),
                            "subject": subject,
                            "status": status
                        }
                    )
    except Exception as e:
        frappe.log_error(f"Attendance alert SMS failed: {str(e)}", "SMS Gateway")


def send_exam_schedule_sms(student, exam_name, exam_date, subject):
    """Send exam schedule notification"""
    try:
        student_doc = frappe.get_doc("Student", student)
        if student_doc.student_mobile_number:
            send_templated_sms(
                "Exam Schedule",
                student_doc.student_mobile_number,
                {
                    "student_name": student_doc.student_name,
                    "exam_name": exam_name,
                    "exam_date": frappe.utils.format_date(exam_date),
                    "subject": subject
                }
            )
    except Exception as e:
        frappe.log_error(f"Exam schedule SMS failed: {str(e)}", "SMS Gateway")


def send_result_declaration_sms(student, exam_name, result_status):
    """Send result declaration notification"""
    try:
        student_doc = frappe.get_doc("Student", student)
        if student_doc.student_mobile_number:
            send_templated_sms(
                "Result Declaration",
                student_doc.student_mobile_number,
                {
                    "student_name": student_doc.student_name,
                    "exam_name": exam_name,
                    "status": result_status
                }
            )
    except Exception as e:
        frappe.log_error(f"Result declaration SMS failed: {str(e)}", "SMS Gateway")


@frappe.whitelist()
def test_sms_gateway(recipient):
    """Test SMS gateway with a sample message"""
    message = "This is a test message from University ERP SMS Gateway."
    gateway = get_sms_gateway()
    return gateway.send_sms(recipient, message)
