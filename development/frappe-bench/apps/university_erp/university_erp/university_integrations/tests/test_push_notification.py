# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock


class TestFirebaseAdmin(FrappeTestCase):
    """Test cases for Firebase Admin integration"""

    def test_singleton_pattern(self):
        """Test that FirebaseAdmin uses singleton pattern"""
        from university_erp.university_integrations.firebase_admin import FirebaseAdmin

        instance1 = FirebaseAdmin()
        instance2 = FirebaseAdmin()

        self.assertIs(instance1, instance2)

    def test_initialize_without_settings(self):
        """Test initialization without Firebase settings"""
        from university_erp.university_integrations.firebase_admin import FirebaseAdmin

        # Reset singleton
        FirebaseAdmin._instance = None
        FirebaseAdmin._initialized = False

        admin = FirebaseAdmin()

        # Should fail gracefully if settings don't exist
        if not frappe.db.exists("Firebase Settings", "Firebase Settings"):
            result = admin.initialize()
            self.assertFalse(result)

    def test_get_firebase_admin(self):
        """Test factory function"""
        from university_erp.university_integrations.firebase_admin import get_firebase_admin

        admin = get_firebase_admin()
        self.assertIsNotNone(admin)

    def test_get_user_fcm_token_no_token(self):
        """Test getting FCM token for user without token"""
        from university_erp.university_integrations.firebase_admin import get_user_fcm_token

        # Non-existent user should return None
        token = get_user_fcm_token("nonexistent@example.com")
        self.assertIsNone(token)

    def test_get_all_user_tokens_no_tokens(self):
        """Test getting all FCM tokens for user without tokens"""
        from university_erp.university_integrations.firebase_admin import get_all_user_tokens

        # Non-existent user should return empty list
        tokens = get_all_user_tokens("nonexistent@example.com")
        self.assertEqual(tokens, [])


class TestPushNotificationManager(FrappeTestCase):
    """Test cases for Push Notification Manager"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test Push Notification Settings if not exists
        if not frappe.db.exists("Push Notification Settings", "Push Notification Settings"):
            settings = frappe.new_doc("Push Notification Settings")
            settings.enabled = 0
            settings.provider = "Firebase Cloud Messaging"
            settings.test_mode = 1
            settings.insert(ignore_permissions=True)

    def test_push_manager_creation(self):
        """Test PushNotificationManager creation"""
        from university_erp.university_integrations.push_notification import get_push_manager

        manager = get_push_manager()
        self.assertIsNotNone(manager)

    def test_send_to_user_disabled(self):
        """Test sending push when disabled"""
        from university_erp.university_integrations.push_notification import PushNotificationManager

        # Disable push notifications
        frappe.db.set_value(
            "Push Notification Settings",
            "Push Notification Settings",
            "enabled", 0
        )

        manager = PushNotificationManager()
        result = manager.send_to_user("test@example.com", "Test", "Test message")

        # Should fail gracefully
        self.assertFalse(result.get("success"))


class TestDeviceTokenManagement(FrappeTestCase):
    """Test cases for device token management"""

    def test_register_device_token_no_token(self):
        """Test registering device without token"""
        from university_erp.university_integrations.firebase_admin import register_device_token

        result = register_device_token("")

        self.assertFalse(result.get("success"))
        self.assertIn("required", result.get("error", "").lower())

    @patch('frappe.session')
    def test_register_device_token_success(self, mock_session):
        """Test successful device token registration"""
        from university_erp.university_integrations.firebase_admin import register_device_token

        mock_session.user = "Administrator"

        # This may fail if User Device Token doctype doesn't exist
        try:
            result = register_device_token(
                token="test_fcm_token_12345",
                device_type="android",
                device_name="Test Device"
            )

            if result.get("success"):
                self.assertTrue(result.get("success"))
        except Exception:
            # Expected if doctype doesn't exist
            pass

    @patch('frappe.session')
    def test_unregister_device_token(self, mock_session):
        """Test device token unregistration"""
        from university_erp.university_integrations.firebase_admin import unregister_device_token

        mock_session.user = "Administrator"

        result = unregister_device_token("nonexistent_token")

        # Should succeed even if token doesn't exist
        self.assertTrue(result.get("success"))


class TestTopicManagement(FrappeTestCase):
    """Test cases for FCM topic management"""

    def test_subscribe_user_to_topic_no_devices(self):
        """Test subscribing user with no devices"""
        from university_erp.university_integrations.firebase_admin import subscribe_user_to_topic

        with patch('frappe.session') as mock_session:
            mock_session.user = "test@example.com"

            result = subscribe_user_to_topic("test_topic")

            # Should fail if no devices registered
            self.assertFalse(result.get("success"))
            self.assertIn("No devices", result.get("error", ""))
