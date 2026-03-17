# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock


class TestNotificationCenter(FrappeTestCase):
    """Test cases for Notification Center"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = "Administrator"

    def test_send_notification(self):
        """Test sending a notification"""
        from university_erp.university_erp.notification_center import NotificationCenter

        result = NotificationCenter.send(
            user=self.test_user,
            title="Test Notification",
            message="This is a test notification",
            notification_type="info",
            category="General"
        )

        self.assertIsNotNone(result)
        self.assertTrue(frappe.db.exists("User Notification", result))

        # Cleanup
        frappe.delete_doc("User Notification", result, force=True)

    def test_get_unread_count(self):
        """Test getting unread notification count"""
        from university_erp.university_erp.notification_center import NotificationCenter

        # Create a test notification
        notification = NotificationCenter.send(
            user=self.test_user,
            title="Test Count",
            message="Test message"
        )

        count = NotificationCenter.get_unread_count(self.test_user)

        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 1)

        # Cleanup
        if notification:
            frappe.delete_doc("User Notification", notification, force=True)

    def test_mark_as_read(self):
        """Test marking notification as read"""
        from university_erp.university_erp.notification_center import NotificationCenter

        # Create a test notification
        notification = NotificationCenter.send(
            user=self.test_user,
            title="Test Read",
            message="Test message"
        )

        # Mark as read
        NotificationCenter.mark_as_read(notification)

        # Verify
        doc = frappe.get_doc("User Notification", notification)
        self.assertEqual(doc.read, 1)
        self.assertIsNotNone(doc.read_at)

        # Cleanup
        frappe.delete_doc("User Notification", notification, force=True)

    def test_mark_all_read(self):
        """Test marking all notifications as read"""
        from university_erp.university_erp.notification_center import NotificationCenter

        # Create test notifications
        notifications = []
        for i in range(3):
            n = NotificationCenter.send(
                user=self.test_user,
                title=f"Test {i}",
                message="Test message"
            )
            notifications.append(n)

        # Mark all as read
        count = NotificationCenter.mark_all_read(self.test_user)

        self.assertGreaterEqual(count, 3)

        # Cleanup
        for n in notifications:
            if n:
                frappe.delete_doc("User Notification", n, force=True)

    def test_get_user_notifications(self):
        """Test getting user notifications with filters"""
        from university_erp.university_erp.notification_center import NotificationCenter

        # Create test notifications
        notification = NotificationCenter.send(
            user=self.test_user,
            title="Test List",
            message="Test message",
            category="Fee"
        )

        result = NotificationCenter.get_user_notifications(
            user=self.test_user,
            category="Fee",
            limit=10
        )

        self.assertIsInstance(result, list)

        # Cleanup
        if notification:
            frappe.delete_doc("User Notification", notification, force=True)

    def test_send_to_role(self):
        """Test sending notification to a role"""
        from university_erp.university_erp.notification_center import NotificationCenter

        # Send to System Manager role
        count = NotificationCenter.send_to_role(
            role="System Manager",
            title="Role Test",
            message="Test message for role"
        )

        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 1)

        # Cleanup - delete notifications with this title
        frappe.db.delete("User Notification", {"title": "Role Test"})

    def test_delete_notification(self):
        """Test deleting a notification"""
        from university_erp.university_erp.notification_center import NotificationCenter

        # Create test notification
        notification = NotificationCenter.send(
            user=self.test_user,
            title="Test Delete",
            message="Test message"
        )

        # Delete it
        result = NotificationCenter.delete_notification(notification, self.test_user)

        self.assertTrue(result)
        self.assertFalse(frappe.db.exists("User Notification", notification))


class TestNotificationCenterAPI(FrappeTestCase):
    """Test cases for Notification Center API"""

    def test_get_notifications_api(self):
        """Test get_notifications API endpoint"""
        from university_erp.university_erp.notification_center import get_notifications

        result = get_notifications(limit=10)

        self.assertIsInstance(result, list)

    def test_get_unread_count_api(self):
        """Test get_unread_count API endpoint"""
        from university_erp.university_erp.notification_center import get_unread_count

        result = get_unread_count()

        self.assertIsInstance(result, int)

    def test_mark_notification_read_api(self):
        """Test mark_notification_read API endpoint"""
        from university_erp.university_erp.notification_center import (
            NotificationCenter, mark_notification_read
        )

        # Create notification
        notification = NotificationCenter.send(
            user="Administrator",
            title="API Test",
            message="Test"
        )

        # Mark as read via API
        result = mark_notification_read(notification)

        self.assertTrue(result)

        # Cleanup
        if notification:
            frappe.delete_doc("User Notification", notification, force=True)


class TestNotificationPreferences(FrappeTestCase):
    """Test cases for notification preferences"""

    def test_should_send_notification(self):
        """Test preference checking"""
        from university_erp.university_erp.doctype.notification_preference.notification_preference import (
            should_send_notification
        )

        # This function should return True by default
        result = should_send_notification("Administrator", "fee", "email")

        self.assertIsInstance(result, bool)

    def test_get_user_preferences(self):
        """Test getting user preferences"""
        # Create or get preferences
        user = "Administrator"

        try:
            pref = frappe.get_doc("Notification Preference", {"user": user})
        except frappe.DoesNotExistError:
            pref = frappe.new_doc("Notification Preference")
            pref.user = user
            pref.enabled = 1
            pref.email_enabled = 1
            pref.insert(ignore_permissions=True)

        self.assertTrue(pref.enabled)
