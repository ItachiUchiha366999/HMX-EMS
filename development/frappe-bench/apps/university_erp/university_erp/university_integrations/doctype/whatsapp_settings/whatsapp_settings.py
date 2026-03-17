# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
WhatsApp Settings DocType Controller
Manages WhatsApp Business API configuration for multiple providers.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url


class WhatsAppSettings(Document):
    def validate(self):
        if self.enabled:
            self.validate_provider_settings()
        self.set_webhook_url()

    def validate_provider_settings(self):
        """Validate that required fields are filled for selected provider"""
        if self.provider == "Meta Business API":
            if not self.phone_number_id:
                frappe.throw(_("Phone Number ID is required for Meta Business API"))
            if not self.access_token:
                frappe.throw(_("Access Token is required for Meta Business API"))

        elif self.provider == "Twilio WhatsApp":
            if not self.twilio_account_sid:
                frappe.throw(_("Twilio Account SID is required"))
            if not self.twilio_auth_token:
                frappe.throw(_("Twilio Auth Token is required"))
            if not self.twilio_whatsapp_number:
                frappe.throw(_("Twilio WhatsApp Number is required"))

        elif self.provider == "Gupshup":
            if not self.gupshup_api_key:
                frappe.throw(_("Gupshup API Key is required"))
            if not self.gupshup_app_name:
                frappe.throw(_("Gupshup App Name is required"))

        elif self.provider == "WATI":
            if not self.wati_api_endpoint:
                frappe.throw(_("WATI API Endpoint is required"))
            if not self.wati_api_token:
                frappe.throw(_("WATI API Token is required"))

    def set_webhook_url(self):
        """Set the webhook URL based on site URL"""
        site_url = get_url()
        self.webhook_url = f"{site_url}/api/method/university_erp.university_integrations.whatsapp_gateway.whatsapp_webhook"

    def get_access_token(self):
        """Get the access token for the configured provider"""
        if self.provider == "Meta Business API":
            return self.get_password("access_token")
        elif self.provider == "Twilio WhatsApp":
            return self.get_password("twilio_auth_token")
        elif self.provider == "Gupshup":
            return self.get_password("gupshup_api_key")
        elif self.provider == "WATI":
            return self.get_password("wati_api_token")
        return None

    def test_connection(self):
        """Test the WhatsApp API connection"""
        if not self.enabled:
            return {"success": False, "error": "WhatsApp integration is not enabled"}

        try:
            if self.provider == "Meta Business API":
                return self._test_meta_connection()
            elif self.provider == "Twilio WhatsApp":
                return self._test_twilio_connection()
            elif self.provider == "Gupshup":
                return self._test_gupshup_connection()
            elif self.provider == "WATI":
                return self._test_wati_connection()
            else:
                return {"success": False, "error": "Provider not configured"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_meta_connection(self):
        """Test Meta Business API connection"""
        import requests

        url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        headers = {
            "Authorization": f"Bearer {self.get_password('access_token')}"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return {"success": True, "message": "Connection successful", "data": response.json()}
        else:
            return {"success": False, "error": response.json().get("error", {}).get("message", "Unknown error")}

    def _test_twilio_connection(self):
        """Test Twilio WhatsApp connection"""
        try:
            from twilio.rest import Client

            client = Client(self.twilio_account_sid, self.get_password("twilio_auth_token"))
            account = client.api.accounts(self.twilio_account_sid).fetch()

            return {"success": True, "message": f"Connected to account: {account.friendly_name}"}

        except ImportError:
            return {"success": False, "error": "Twilio library not installed. Run: pip install twilio"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_gupshup_connection(self):
        """Test Gupshup connection"""
        import requests

        url = "https://api.gupshup.io/sm/api/v1/users"
        headers = {
            "apikey": self.get_password("gupshup_api_key")
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return {"success": True, "message": "Connection successful"}
        else:
            return {"success": False, "error": response.text}

    def _test_wati_connection(self):
        """Test WATI connection"""
        import requests

        url = f"{self.wati_api_endpoint}/api/v1/getContacts"
        headers = {
            "Authorization": f"Bearer {self.get_password('wati_api_token')}"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return {"success": True, "message": "Connection successful"}
        else:
            return {"success": False, "error": response.text}

    def increment_message_count(self):
        """Increment daily message count"""
        frappe.db.set_value(
            "WhatsApp Settings", "WhatsApp Settings",
            "messages_sent_today", self.messages_sent_today + 1
        )

    def check_rate_limit(self):
        """Check if rate limit is exceeded"""
        if self.messages_sent_today >= self.daily_message_limit:
            frappe.throw(_("Daily WhatsApp message limit reached"))
        return True


def get_whatsapp_settings():
    """Get WhatsApp settings singleton"""
    settings = frappe.get_single("WhatsApp Settings")
    if not settings.enabled:
        frappe.throw(_("WhatsApp integration is not enabled"))
    return settings


@frappe.whitelist()
def test_whatsapp_connection():
    """Test WhatsApp connection - API endpoint"""
    settings = frappe.get_single("WhatsApp Settings")
    return settings.test_connection()


def reset_daily_message_count():
    """Reset daily message count - called by scheduler at midnight"""
    frappe.db.set_value("WhatsApp Settings", "WhatsApp Settings", "messages_sent_today", 0)
    frappe.db.commit()
