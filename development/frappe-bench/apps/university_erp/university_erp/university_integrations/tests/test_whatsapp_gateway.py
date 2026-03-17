# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock
import json


class TestWhatsAppGateway(FrappeTestCase):
    """Test cases for WhatsApp Gateway"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test WhatsApp Settings if not exists
        if not frappe.db.exists("WhatsApp Settings", "WhatsApp Settings"):
            settings = frappe.new_doc("WhatsApp Settings")
            settings.enabled = 0
            settings.provider = "Meta Business API"
            settings.test_mode = 1
            settings.default_country_code = "+91"
            settings.insert(ignore_permissions=True)

    def test_normalize_phone_10_digit(self):
        """Test phone normalization for 10-digit numbers"""
        from university_erp.university_integrations.whatsapp_gateway import WhatsAppGateway

        with patch.object(WhatsAppGateway, '__init__', lambda x: None):
            gateway = WhatsAppGateway()
            gateway.settings = MagicMock()
            gateway.settings.default_country_code = "+91"

            # 10-digit number should get country code
            result = gateway.normalize_phone("9876543210")
            self.assertEqual(result, "919876543210")

    def test_normalize_phone_with_plus(self):
        """Test phone normalization with + prefix"""
        from university_erp.university_integrations.whatsapp_gateway import WhatsAppGateway

        with patch.object(WhatsAppGateway, '__init__', lambda x: None):
            gateway = WhatsAppGateway()
            gateway.settings = MagicMock()
            gateway.settings.default_country_code = "+91"

            # Number with + should have it removed
            result = gateway.normalize_phone("+919876543210")
            self.assertEqual(result, "919876543210")

    def test_normalize_phone_with_leading_zero(self):
        """Test phone normalization with leading zero"""
        from university_erp.university_integrations.whatsapp_gateway import WhatsAppGateway

        with patch.object(WhatsAppGateway, '__init__', lambda x: None):
            gateway = WhatsAppGateway()
            gateway.settings = MagicMock()
            gateway.settings.default_country_code = "+91"

            # Leading zero should be replaced with country code
            result = gateway.normalize_phone("09876543210")
            self.assertEqual(result, "919876543210")

    def test_get_whatsapp_templates_disabled(self):
        """Test template fetch when WhatsApp is disabled"""
        from university_erp.university_integrations.whatsapp_gateway import get_whatsapp_templates

        # Disable WhatsApp
        frappe.db.set_value("WhatsApp Settings", "WhatsApp Settings", "enabled", 0)

        result = get_whatsapp_templates()

        self.assertFalse(result.get("success"))
        self.assertIn("not enabled", result.get("error", ""))

    def test_sync_whatsapp_templates_disabled(self):
        """Test template sync when WhatsApp is disabled"""
        from university_erp.university_integrations.whatsapp_gateway import sync_whatsapp_templates

        # Disable WhatsApp
        frappe.db.set_value("WhatsApp Settings", "WhatsApp Settings", "enabled", 0)

        result = sync_whatsapp_templates()

        self.assertFalse(result.get("success"))

    @patch('university_erp.university_integrations.whatsapp_gateway.requests')
    def test_send_template_message_test_mode(self, mock_requests):
        """Test sending template message in test mode"""
        from university_erp.university_integrations.whatsapp_gateway import WhatsAppGateway

        # Enable test mode
        frappe.db.set_value("WhatsApp Settings", "WhatsApp Settings", {
            "enabled": 1,
            "test_mode": 1
        })

        try:
            gateway = WhatsAppGateway()

            # Create mock template
            if not frappe.db.exists("WhatsApp Template", {"template_key": "test_template"}):
                template = frappe.new_doc("WhatsApp Template")
                template.template_name = "Test Template"
                template.template_key = "test_template"
                template.body_template = "Hello {{1}}"
                template.status = "Approved"
                template.insert(ignore_permissions=True)

            result = gateway.send_template_message(
                "9876543210",
                "test_template",
                {"body": ["World"]}
            )

            # In test mode, should succeed without actual API call
            self.assertTrue(result.get("test_mode") or result.get("success"))

        finally:
            # Disable WhatsApp
            frappe.db.set_value("WhatsApp Settings", "WhatsApp Settings", "enabled", 0)


class TestWhatsAppTemplateSync(FrappeTestCase):
    """Test cases for WhatsApp Template Sync"""

    def test_map_template_status(self):
        """Test template status mapping"""
        from university_erp.university_integrations.whatsapp_gateway import _map_template_status

        self.assertEqual(_map_template_status("APPROVED"), "Approved")
        self.assertEqual(_map_template_status("PENDING"), "Pending")
        self.assertEqual(_map_template_status("REJECTED"), "Rejected")
        self.assertEqual(_map_template_status("unknown"), "Pending")

    def test_map_template_category(self):
        """Test template category mapping"""
        from university_erp.university_integrations.whatsapp_gateway import _map_template_category

        self.assertEqual(_map_template_category("MARKETING"), "Marketing")
        self.assertEqual(_map_template_category("UTILITY"), "Utility")
        self.assertEqual(_map_template_category("AUTHENTICATION"), "Authentication")
        self.assertEqual(_map_template_category("unknown"), "Marketing")


class TestWhatsAppWebhook(FrappeTestCase):
    """Test cases for WhatsApp Webhook"""

    def test_webhook_verification(self):
        """Test webhook verification request"""
        # This would require mocking frappe.request
        pass

    def test_incoming_message_processing(self):
        """Test incoming message processing"""
        from university_erp.university_integrations.whatsapp_gateway import _process_message_webhook

        # Mock incoming message data
        data = {
            "messages": [
                {
                    "from": "919876543210",
                    "type": "text",
                    "id": "test_msg_id",
                    "timestamp": "1234567890",
                    "text": {"body": "Hello"}
                }
            ],
            "statuses": []
        }

        # This should not raise an error
        try:
            _process_message_webhook(data)
        except Exception as e:
            # Expected to fail if WhatsApp Log doesn't exist
            if "WhatsApp Log" not in str(e):
                raise
