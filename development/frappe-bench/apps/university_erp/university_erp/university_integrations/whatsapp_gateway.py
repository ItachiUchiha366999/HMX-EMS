# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
WhatsApp Business API Gateway
Supports: Meta Business API, Twilio WhatsApp, Gupshup, WATI
"""

import frappe
from frappe import _
import requests
import json
import re


class WhatsAppGateway:
    """Unified WhatsApp gateway interface"""

    def __init__(self):
        self.settings = frappe.get_single("WhatsApp Settings")

        if not self.settings.enabled:
            frappe.throw(_("WhatsApp integration is not enabled"))

        self.provider = self.settings.provider

    def send_template_message(self, phone_number, template_key, params=None, language="en"):
        """
        Send WhatsApp template message

        Args:
            phone_number: Recipient phone number
            template_key: Template key from WhatsApp Template doctype
            params: Dict with 'header', 'body', 'buttons' lists
            language: Language code (default: en)

        Returns:
            dict with success, message_id, log
        """
        phone = self.normalize_phone(phone_number)

        if self.settings.test_mode:
            return self._log_test_message(phone, "template", template_name=template_key)

        self.settings.check_rate_limit()

        # Get template
        template = frappe.get_doc("WhatsApp Template", template_key)
        template_data = template.get_template_for_sending(params)

        # Route to provider
        providers = {
            "Meta Business API": self._send_meta_template,
            "Twilio WhatsApp": self._send_twilio_template,
            "Gupshup": self._send_gupshup_template,
            "WATI": self._send_wati_template
        }

        sender = providers.get(self.provider)
        if not sender:
            frappe.throw(_(f"Unknown WhatsApp provider: {self.provider}"))

        result = sender(phone, template_data)

        # Log message
        log = self._create_log(
            phone_number=phone,
            message_type="template",
            template_name=template_key,
            template_params=json.dumps(params) if params else None,
            message_id=result.get("message_id"),
            status="Sent" if result.get("success") else "Failed",
            error_message=result.get("error"),
            raw_response=json.dumps(result.get("raw_response")) if result.get("raw_response") else None
        )

        if result.get("success"):
            self.settings.increment_message_count()

        return {
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "log": log.name,
            "error": result.get("error")
        }

    def send_text_message(self, phone_number, message):
        """
        Send plain text message (only works within 24-hour window)

        Args:
            phone_number: Recipient phone number
            message: Text message content

        Returns:
            dict with success, message_id, log
        """
        phone = self.normalize_phone(phone_number)

        if self.settings.test_mode:
            return self._log_test_message(phone, "text", message_content=message)

        self.settings.check_rate_limit()

        providers = {
            "Meta Business API": self._send_meta_text,
            "Twilio WhatsApp": self._send_twilio_text,
            "Gupshup": self._send_gupshup_text,
            "WATI": self._send_wati_text
        }

        sender = providers.get(self.provider)
        if not sender:
            frappe.throw(_(f"Unknown WhatsApp provider: {self.provider}"))

        result = sender(phone, message)

        log = self._create_log(
            phone_number=phone,
            message_type="text",
            message_content=message,
            message_id=result.get("message_id"),
            status="Sent" if result.get("success") else "Failed",
            error_message=result.get("error")
        )

        if result.get("success"):
            self.settings.increment_message_count()

        return {
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "log": log.name
        }

    def send_media_message(self, phone_number, media_type, media_url, caption=None):
        """
        Send media message (image, document, video)

        Args:
            phone_number: Recipient phone number
            media_type: Type of media (image, document, video)
            media_url: URL of the media
            caption: Optional caption

        Returns:
            dict with success, message_id, log
        """
        phone = self.normalize_phone(phone_number)

        if self.settings.test_mode:
            return self._log_test_message(phone, media_type, media_url=media_url, message_content=caption)

        self.settings.check_rate_limit()

        if self.provider == "Meta Business API":
            result = self._send_meta_media(phone, media_type, media_url, caption)
        elif self.provider == "Twilio WhatsApp":
            result = self._send_twilio_media(phone, media_url, caption)
        else:
            return {"success": False, "error": f"Media messages not supported for {self.provider}"}

        log = self._create_log(
            phone_number=phone,
            message_type=media_type,
            media_url=media_url,
            message_content=caption,
            message_id=result.get("message_id"),
            status="Sent" if result.get("success") else "Failed",
            error_message=result.get("error")
        )

        if result.get("success"):
            self.settings.increment_message_count()

        return {
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "log": log.name
        }

    def normalize_phone(self, phone):
        """Normalize phone number for WhatsApp API"""
        phone = str(phone).strip()
        # Remove all non-numeric characters except +
        phone = re.sub(r'[^0-9+]', '', phone)

        # Remove leading +
        if phone.startswith('+'):
            phone = phone[1:]

        # Add country code if missing
        if len(phone) == 10:
            country_code = self.settings.default_country_code.replace('+', '')
            phone = country_code + phone
        elif phone.startswith('0'):
            country_code = self.settings.default_country_code.replace('+', '')
            phone = country_code + phone[1:]

        return phone

    # ========== Meta Business API ==========

    def _send_meta_template(self, phone, template_data):
        """Send template message via Meta Business API"""
        url = f"https://graph.facebook.com/{self.settings.api_version}/{self.settings.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('access_token')}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "template",
            "template": template_data
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if response.status_code == 200:
                message_id = result.get("messages", [{}])[0].get("id")
                return {"success": True, "message_id": message_id, "raw_response": result}
            else:
                error = result.get("error", {}).get("message", "Unknown error")
                return {"success": False, "error": error, "raw_response": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_meta_text(self, phone, message):
        """Send text message via Meta Business API"""
        url = f"https://graph.facebook.com/{self.settings.api_version}/{self.settings.phone_number_id}/messages"

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

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if response.status_code == 200:
                message_id = result.get("messages", [{}])[0].get("id")
                return {"success": True, "message_id": message_id}
            else:
                error = result.get("error", {}).get("message", "Unknown error")
                return {"success": False, "error": error}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_meta_media(self, phone, media_type, media_url, caption):
        """Send media message via Meta Business API"""
        url = f"https://graph.facebook.com/{self.settings.api_version}/{self.settings.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('access_token')}",
            "Content-Type": "application/json"
        }

        media_payload = {"link": media_url}
        if caption:
            media_payload["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": media_type,
            media_type: media_payload
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if response.status_code == 200:
                message_id = result.get("messages", [{}])[0].get("id")
                return {"success": True, "message_id": message_id}
            else:
                error = result.get("error", {}).get("message", "Unknown error")
                return {"success": False, "error": error}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Twilio WhatsApp ==========

    def _send_twilio_template(self, phone, template_data):
        """Send template message via Twilio (content templates)"""
        try:
            from twilio.rest import Client

            client = Client(
                self.settings.twilio_account_sid,
                self.settings.get_password("twilio_auth_token")
            )

            # Twilio uses content SIDs for templates
            message = client.messages.create(
                from_=self.settings.twilio_whatsapp_number,
                to=f"whatsapp:+{phone}",
                content_sid=template_data.get("name"),
                content_variables=json.dumps({"1": "value"})  # Simplified
            )

            return {
                "success": message.status in ["queued", "sent"],
                "message_id": message.sid
            }

        except ImportError:
            return {"success": False, "error": "Twilio library not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_twilio_text(self, phone, message):
        """Send text message via Twilio WhatsApp"""
        try:
            from twilio.rest import Client

            client = Client(
                self.settings.twilio_account_sid,
                self.settings.get_password("twilio_auth_token")
            )

            msg = client.messages.create(
                from_=self.settings.twilio_whatsapp_number,
                to=f"whatsapp:+{phone}",
                body=message
            )

            return {
                "success": msg.status in ["queued", "sent"],
                "message_id": msg.sid
            }

        except ImportError:
            return {"success": False, "error": "Twilio library not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_twilio_media(self, phone, media_url, caption):
        """Send media message via Twilio WhatsApp"""
        try:
            from twilio.rest import Client

            client = Client(
                self.settings.twilio_account_sid,
                self.settings.get_password("twilio_auth_token")
            )

            msg = client.messages.create(
                from_=self.settings.twilio_whatsapp_number,
                to=f"whatsapp:+{phone}",
                body=caption or "",
                media_url=[media_url]
            )

            return {
                "success": msg.status in ["queued", "sent"],
                "message_id": msg.sid
            }

        except ImportError:
            return {"success": False, "error": "Twilio library not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Gupshup ==========

    def _send_gupshup_template(self, phone, template_data):
        """Send template message via Gupshup"""
        url = "https://api.gupshup.io/sm/api/v1/template/msg"

        headers = {
            "apikey": self.settings.get_password("gupshup_api_key"),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "channel": "whatsapp",
            "source": self.settings.gupshup_source_number,
            "destination": phone,
            "src.name": self.settings.gupshup_app_name,
            "template": json.dumps({
                "id": template_data.get("name"),
                "params": template_data.get("components", [])
            })
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            result = response.json()

            if result.get("status") == "submitted":
                return {"success": True, "message_id": result.get("messageId")}
            else:
                return {"success": False, "error": result.get("message", "Unknown error")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_gupshup_text(self, phone, message):
        """Send text message via Gupshup"""
        url = "https://api.gupshup.io/sm/api/v1/msg"

        headers = {
            "apikey": self.settings.get_password("gupshup_api_key"),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "channel": "whatsapp",
            "source": self.settings.gupshup_source_number,
            "destination": phone,
            "src.name": self.settings.gupshup_app_name,
            "message": json.dumps({"type": "text", "text": message})
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            result = response.json()

            if result.get("status") == "submitted":
                return {"success": True, "message_id": result.get("messageId")}
            else:
                return {"success": False, "error": result.get("message", "Unknown error")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== WATI ==========

    def _send_wati_template(self, phone, template_data):
        """Send template message via WATI"""
        url = f"{self.settings.wati_api_endpoint}/api/v1/sendTemplateMessage"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('wati_api_token')}",
            "Content-Type": "application/json"
        }

        # Extract parameters from template_data
        params = []
        for component in template_data.get("components", []):
            if component.get("type") == "body":
                for param in component.get("parameters", []):
                    params.append({"name": f"param{len(params)+1}", "value": param.get("text", "")})

        payload = {
            "whatsappNumber": phone,
            "templateName": template_data.get("name"),
            "broadcastName": "API_Broadcast",
            "parameters": params
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if result.get("result"):
                return {"success": True, "message_id": result.get("messageId")}
            else:
                return {"success": False, "error": result.get("info", "Unknown error")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_wati_text(self, phone, message):
        """Send text message via WATI"""
        url = f"{self.settings.wati_api_endpoint}/api/v1/sendSessionMessage/{phone}"

        headers = {
            "Authorization": f"Bearer {self.settings.get_password('wati_api_token')}",
            "Content-Type": "application/json"
        }

        payload = {"messageText": message}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if result.get("result"):
                return {"success": True, "message_id": result.get("messageId")}
            else:
                return {"success": False, "error": result.get("info", "Unknown error")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Logging ==========

    def _create_log(self, **kwargs):
        """Create WhatsApp log entry"""
        from university_erp.university_integrations.doctype.whatsapp_log.whatsapp_log import create_whatsapp_log
        return create_whatsapp_log(**kwargs)

    def _log_test_message(self, phone, message_type, **kwargs):
        """Log test message without sending"""
        log = self._create_log(
            phone_number=phone,
            message_type=message_type,
            status="Test",
            **kwargs
        )

        return {
            "success": True,
            "message_id": f"test_{frappe.generate_hash(length=8)}",
            "log": log.name,
            "test_mode": True
        }


# ========== Factory Function ==========

def get_whatsapp_gateway():
    """Get configured WhatsApp gateway instance"""
    return WhatsAppGateway()


# ========== API Endpoints ==========

@frappe.whitelist()
def send_whatsapp_template(phone_number, template_key, params=None):
    """Send WhatsApp template message - API endpoint"""
    if isinstance(params, str):
        params = json.loads(params)

    gateway = get_whatsapp_gateway()
    return gateway.send_template_message(phone_number, template_key, params)


@frappe.whitelist()
def send_whatsapp_message(phone_number, message):
    """Send WhatsApp text message - API endpoint"""
    gateway = get_whatsapp_gateway()
    return gateway.send_text_message(phone_number, message)


@frappe.whitelist()
def send_whatsapp_media(phone_number, media_type, media_url, caption=None):
    """Send WhatsApp media message - API endpoint"""
    gateway = get_whatsapp_gateway()
    return gateway.send_media_message(phone_number, media_type, media_url, caption)


# ========== Webhook Handler ==========

@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():
    """
    Handle WhatsApp webhook callbacks from Meta Business API

    Handles:
    - Webhook verification (GET requests)
    - Incoming messages (POST requests)
    - Message status updates (POST requests)
    """
    settings = frappe.get_single("WhatsApp Settings")

    # Webhook verification (GET request)
    if frappe.request.method == "GET":
        mode = frappe.request.args.get("hub.mode")
        token = frappe.request.args.get("hub.verify_token")
        challenge = frappe.request.args.get("hub.challenge")

        if mode == "subscribe" and token == settings.webhook_verify_token:
            frappe.response["message"] = challenge
            return challenge

        frappe.response["http_status_code"] = 403
        return "Forbidden"

    # Handle incoming webhooks (POST request)
    if frappe.request.method == "POST":
        try:
            data = frappe.request.get_json(force=True)

            # Update last webhook received
            frappe.db.set_value(
                "WhatsApp Settings", "WhatsApp Settings",
                "last_webhook_received", frappe.utils.now_datetime()
            )

            # Process webhook entries
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        _process_message_webhook(change.get("value", {}))

            frappe.db.commit()
            return {"status": "ok"}

        except Exception as e:
            frappe.log_error(f"WhatsApp webhook error: {str(e)}", "WhatsApp Webhook")
            return {"status": "error", "message": str(e)}

    return {"status": "method_not_allowed"}


def _process_message_webhook(data):
    """Process message webhook data"""
    from university_erp.university_integrations.doctype.whatsapp_log.whatsapp_log import (
        create_whatsapp_log, update_message_status
    )

    # Handle incoming messages
    messages = data.get("messages", [])
    for message in messages:
        phone = message.get("from")
        message_type = message.get("type")
        message_id = message.get("id")
        timestamp = message.get("timestamp")

        # Extract message content
        content = ""
        if message_type == "text":
            content = message.get("text", {}).get("body", "")
        elif message_type == "image":
            content = "[Image]"
        elif message_type == "document":
            content = "[Document]"

        # Log incoming message
        create_whatsapp_log(
            phone_number=phone,
            message_type=message_type,
            direction="Incoming",
            message_id=message_id,
            message_content=content,
            status="Received"
        )

        # Process auto-reply if configured
        _handle_incoming_message(phone, message)

    # Handle status updates
    statuses = data.get("statuses", [])
    for status in statuses:
        message_id = status.get("id")
        status_value = status.get("status")
        timestamp = status.get("timestamp")

        update_message_status(message_id, status_value, timestamp)


def _handle_incoming_message(phone, message):
    """Handle incoming message with auto-reply logic"""
    message_type = message.get("type")

    if message_type != "text":
        return

    text = message.get("text", {}).get("body", "").lower().strip()

    # Simple keyword-based auto-replies
    auto_replies = {
        "fee": "Your fee status will be sent shortly. Please check the student portal for details.",
        "result": "To check your results, please visit the student portal at {portal_url}.",
        "attendance": "Your attendance information is available on the student portal.",
        "help": "Available commands: fee, result, attendance, timetable, contact\nFor assistance, contact the administration office.",
        "hi": "Hello! Welcome to University ERP. How can I help you today?\n\nType 'help' for available commands.",
        "hello": "Hello! Welcome to University ERP. How can I help you today?\n\nType 'help' for available commands."
    }

    for keyword, reply in auto_replies.items():
        if keyword in text:
            try:
                gateway = WhatsAppGateway()
                portal_url = frappe.utils.get_url("/student-portal")
                reply = reply.replace("{portal_url}", portal_url)
                gateway.send_text_message(phone, reply)
            except Exception as e:
                frappe.log_error(f"Auto-reply failed: {str(e)}", "WhatsApp Auto-Reply")
            return

    # Default reply for unrecognized messages
    try:
        gateway = WhatsAppGateway()
        default_reply = (
            "Thank you for your message. For assistance, please visit the student portal "
            "or contact the administration office.\n\nType 'help' for available commands."
        )
        gateway.send_text_message(phone, default_reply)
    except Exception:
        pass


# ========== Scheduled Tasks ==========

def reset_daily_counters():
    """Reset daily message counters - called by scheduler"""
    frappe.db.set_value(
        "WhatsApp Settings", "WhatsApp Settings",
        "messages_sent_today", 0
    )
    frappe.db.commit()


# ========== Template Sync Functions ==========

@frappe.whitelist()
def get_whatsapp_templates():
    """
    Fetch all approved templates from WhatsApp Business API

    Returns:
        dict: List of templates with status and metadata
    """
    settings = frappe.get_single("WhatsApp Settings")

    if not settings.enabled:
        return {"success": False, "error": "WhatsApp integration is not enabled"}

    if settings.provider == "Meta Business API":
        return _get_meta_templates(settings)
    elif settings.provider == "Gupshup":
        return _get_gupshup_templates(settings)
    elif settings.provider == "WATI":
        return _get_wati_templates(settings)
    elif settings.provider == "Twilio WhatsApp":
        return _get_twilio_templates(settings)
    else:
        return {"success": False, "error": f"Template sync not supported for {settings.provider}"}


def _get_meta_templates(settings):
    """Fetch templates from Meta Business API"""
    url = f"https://graph.facebook.com/{settings.api_version}/{settings.waba_id}/message_templates"

    headers = {
        "Authorization": f"Bearer {settings.get_password('access_token')}",
        "Content-Type": "application/json"
    }

    params = {
        "limit": 100,
        "fields": "name,status,language,category,components,quality_score"
    }

    try:
        templates = []
        while url:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            result = response.json()

            if response.status_code != 200:
                error = result.get("error", {}).get("message", "Unknown error")
                return {"success": False, "error": error}

            templates.extend(result.get("data", []))

            # Handle pagination
            paging = result.get("paging", {})
            url = paging.get("next")
            params = None  # Next URL includes params

        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_gupshup_templates(settings):
    """Fetch templates from Gupshup"""
    url = "https://api.gupshup.io/sm/api/v1/template/list"

    headers = {
        "apikey": settings.get_password("gupshup_api_key"),
        "Content-Type": "application/json"
    }

    params = {
        "appName": settings.gupshup_app_name
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        result = response.json()

        if result.get("status") == "success":
            templates = result.get("templates", [])
            # Normalize format
            normalized = []
            for t in templates:
                normalized.append({
                    "name": t.get("elementName"),
                    "status": t.get("status", "").upper(),
                    "language": t.get("languageCode", "en"),
                    "category": t.get("templateType", "MARKETING"),
                    "components": t.get("data", ""),
                    "quality_score": None
                })
            return {"success": True, "templates": normalized, "count": len(normalized)}
        else:
            return {"success": False, "error": result.get("message", "Unknown error")}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_wati_templates(settings):
    """Fetch templates from WATI"""
    url = f"{settings.wati_api_endpoint}/api/v1/getMessageTemplates"

    headers = {
        "Authorization": f"Bearer {settings.get_password('wati_api_token')}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        result = response.json()

        if result.get("result"):
            templates = result.get("messageTemplates", [])
            # Normalize format
            normalized = []
            for t in templates:
                normalized.append({
                    "name": t.get("elementName"),
                    "status": t.get("status", "").upper(),
                    "language": t.get("language", "en"),
                    "category": t.get("category", "MARKETING"),
                    "components": t.get("bodyOriginal", ""),
                    "quality_score": None
                })
            return {"success": True, "templates": normalized, "count": len(normalized)}
        else:
            return {"success": False, "error": result.get("info", "Unknown error")}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_twilio_templates(settings):
    """Fetch templates from Twilio Content API"""
    try:
        from twilio.rest import Client

        client = Client(
            settings.twilio_account_sid,
            settings.get_password("twilio_auth_token")
        )

        # Fetch content templates
        content_list = client.content.v1.contents.list(limit=100)

        templates = []
        for content in content_list:
            templates.append({
                "name": content.friendly_name,
                "status": "APPROVED",  # Twilio approved templates are available
                "language": content.language or "en",
                "category": "MARKETING",
                "components": json.dumps(content.types) if content.types else "",
                "quality_score": None,
                "content_sid": content.sid
            })

        return {"success": True, "templates": templates, "count": len(templates)}

    except ImportError:
        return {"success": False, "error": "Twilio library not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def sync_whatsapp_templates():
    """
    Sync templates from WhatsApp Business API to local WhatsApp Template doctype

    Creates new templates and updates existing ones with latest status

    Returns:
        dict: Sync summary with created, updated, and error counts
    """
    # Fetch templates from provider
    result = get_whatsapp_templates()

    if not result.get("success"):
        return result

    templates = result.get("templates", [])

    created = 0
    updated = 0
    errors = []

    for template in templates:
        try:
            template_name = template.get("name")
            existing = frappe.db.exists("WhatsApp Template", {"template_name": template_name})

            if existing:
                # Update existing template
                doc = frappe.get_doc("WhatsApp Template", existing)
                doc.status = _map_template_status(template.get("status"))
                doc.quality_score = template.get("quality_score")
                doc.last_synced = frappe.utils.now()
                doc.save(ignore_permissions=True)
                updated += 1
            else:
                # Create new template
                doc = frappe.new_doc("WhatsApp Template")
                doc.template_name = template_name
                doc.template_key = template_name.lower().replace(" ", "_")
                doc.language = template.get("language", "en")
                doc.category = _map_template_category(template.get("category"))
                doc.status = _map_template_status(template.get("status"))
                doc.quality_score = template.get("quality_score")
                doc.last_synced = frappe.utils.now()

                # Parse components if available
                components = template.get("components")
                if isinstance(components, list):
                    for comp in components:
                        if comp.get("type") == "HEADER":
                            doc.header_type = comp.get("format", "TEXT").lower()
                            if comp.get("text"):
                                doc.header_text = comp.get("text")
                        elif comp.get("type") == "BODY":
                            doc.body_template = comp.get("text", "")
                        elif comp.get("type") == "FOOTER":
                            doc.footer_text = comp.get("text", "")
                        elif comp.get("type") == "BUTTONS":
                            for btn in comp.get("buttons", []):
                                doc.append("buttons", {
                                    "button_type": btn.get("type", "QUICK_REPLY"),
                                    "button_text": btn.get("text", ""),
                                    "button_url": btn.get("url", ""),
                                    "phone_number": btn.get("phone_number", "")
                                })
                elif isinstance(components, str) and components:
                    # String format (from Gupshup/WATI)
                    doc.body_template = components

                doc.insert(ignore_permissions=True)
                created += 1

        except Exception as e:
            errors.append({
                "template": template.get("name"),
                "error": str(e)
            })
            frappe.log_error(
                f"Template sync failed for {template.get('name')}: {str(e)}",
                "WhatsApp Template Sync"
            )

    frappe.db.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "total": len(templates),
        "errors": errors
    }


def _map_template_status(status):
    """Map provider status to local status"""
    status_map = {
        "APPROVED": "Approved",
        "PENDING": "Pending",
        "REJECTED": "Rejected",
        "PAUSED": "Paused",
        "DISABLED": "Disabled"
    }
    return status_map.get(str(status).upper(), "Pending")


def _map_template_category(category):
    """Map provider category to local category"""
    category_map = {
        "MARKETING": "Marketing",
        "UTILITY": "Utility",
        "AUTHENTICATION": "Authentication",
        "TRANSACTIONAL": "Utility"
    }
    return category_map.get(str(category).upper(), "Marketing")


@frappe.whitelist()
def create_whatsapp_template_on_provider(template_name):
    """
    Submit a new template to WhatsApp Business API for approval

    Args:
        template_name: Name of local WhatsApp Template document

    Returns:
        dict: Submission result with template ID if successful
    """
    settings = frappe.get_single("WhatsApp Settings")

    if not settings.enabled:
        return {"success": False, "error": "WhatsApp integration is not enabled"}

    template = frappe.get_doc("WhatsApp Template", template_name)

    if settings.provider == "Meta Business API":
        return _create_meta_template(settings, template)
    else:
        return {"success": False, "error": f"Template creation not supported for {settings.provider}"}


def _create_meta_template(settings, template):
    """Create template on Meta Business API"""
    url = f"https://graph.facebook.com/{settings.api_version}/{settings.waba_id}/message_templates"

    headers = {
        "Authorization": f"Bearer {settings.get_password('access_token')}",
        "Content-Type": "application/json"
    }

    # Build components
    components = []

    # Header
    if template.header_type and template.header_type != "none":
        header_comp = {"type": "HEADER", "format": template.header_type.upper()}
        if template.header_type == "text" and template.header_text:
            header_comp["text"] = template.header_text
        elif template.header_type in ["image", "document", "video"]:
            header_comp["example"] = {"header_handle": [template.get("header_media_example") or ""]}
        components.append(header_comp)

    # Body (required)
    body_comp = {"type": "BODY", "text": template.body_template}

    # Extract body parameters
    import re
    params = re.findall(r'\{\{(\d+)\}\}', template.body_template)
    if params:
        examples = []
        for i in range(len(params)):
            examples.append(f"Example{i+1}")
        body_comp["example"] = {"body_text": [examples]}

    components.append(body_comp)

    # Footer
    if template.footer_text:
        components.append({"type": "FOOTER", "text": template.footer_text})

    # Buttons
    if template.buttons:
        buttons = []
        for btn in template.buttons:
            button = {"type": btn.button_type.upper(), "text": btn.button_text}
            if btn.button_type.upper() == "URL" and btn.button_url:
                button["url"] = btn.button_url
            elif btn.button_type.upper() == "PHONE_NUMBER" and btn.phone_number:
                button["phone_number"] = btn.phone_number
            buttons.append(button)
        components.append({"type": "BUTTONS", "buttons": buttons})

    payload = {
        "name": template.template_key,
        "language": template.language or "en",
        "category": _reverse_map_category(template.category),
        "components": components
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        if response.status_code == 200:
            # Update local template with provider ID
            template.provider_template_id = result.get("id")
            template.status = "Pending"
            template.save(ignore_permissions=True)

            return {
                "success": True,
                "template_id": result.get("id"),
                "status": result.get("status")
            }
        else:
            error = result.get("error", {}).get("message", "Unknown error")
            return {"success": False, "error": error, "details": result}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _reverse_map_category(category):
    """Map local category back to provider format"""
    category_map = {
        "Marketing": "MARKETING",
        "Utility": "UTILITY",
        "Authentication": "AUTHENTICATION"
    }
    return category_map.get(category, "MARKETING")
