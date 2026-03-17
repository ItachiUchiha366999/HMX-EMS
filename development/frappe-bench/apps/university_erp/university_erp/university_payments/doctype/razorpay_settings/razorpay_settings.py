# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class RazorpaySettings(Document):
    def validate(self):
        if self.enabled:
            self.validate_credentials()

    def validate_credentials(self):
        """Validate Razorpay API credentials"""
        if not self.api_key or not self.api_secret:
            frappe.throw(_("API Key and API Secret are required when Razorpay is enabled"))

        # Only validate in production mode if not in test mode
        if not self.test_mode:
            try:
                client = self.get_client()
                # Test API by fetching a non-existent order (will fail but proves auth works)
                client.order.all({"count": 1})
            except Exception as e:
                if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                    frappe.throw(_("Invalid Razorpay credentials: {0}").format(str(e)))

    def get_client(self):
        """Get Razorpay client instance"""
        try:
            import razorpay
        except ImportError:
            frappe.throw(_("razorpay package is not installed. Please run: pip install razorpay"))

        return razorpay.Client(auth=(self.api_key, self.get_password('api_secret')))

    def get_webhook_secret(self):
        """Get webhook secret for signature verification"""
        return self.get_password('webhook_secret') if self.webhook_secret else None


def get_razorpay_settings():
    """Get Razorpay settings singleton"""
    settings = frappe.get_single("Razorpay Settings")
    if not settings.enabled:
        frappe.throw(_("Razorpay payment gateway is not enabled"))
    return settings


def get_razorpay_client():
    """Get Razorpay client from settings"""
    settings = get_razorpay_settings()
    return settings.get_client()
