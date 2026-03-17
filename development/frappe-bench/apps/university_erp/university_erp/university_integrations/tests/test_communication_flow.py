# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Integration tests for end-to-end communication flows
"""

import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock


class TestUnifiedCommunicationFlow(FrappeTestCase):
    """Test cases for unified communication flow"""

    def test_unified_send_basic(self):
        """Test basic unified send"""
        from university_erp.university_erp.unified_communication import unified_send

        result = unified_send(
            recipient="Administrator",
            title="Test Unified",
            message="Test message",
            channels=["in_app"]
        )

        self.assertTrue(result.get("success"))
        self.assertIn("in_app", result.get("channels", {}))

        # Cleanup
        frappe.db.delete("User Notification", {"title": "Test Unified"})

    def test_unified_send_with_fallback(self):
        """Test unified send with fallback on failure"""
        from university_erp.university_erp.unified_communication import unified_send

        # Try multiple channels - in_app should succeed even if others fail
        result = unified_send(
            recipient="Administrator",
            title="Test Fallback",
            message="Test message",
            channels=["sms", "email", "in_app"],
            fallback_on_failure=True
        )

        self.assertTrue(result.get("success"))

        # Cleanup
        frappe.db.delete("User Notification", {"title": "Test Fallback"})

    def test_unified_send_respects_preferences(self):
        """Test that unified send respects user preferences"""
        from university_erp.university_erp.unified_communication import unified_send

        # Create preference that disables all
        try:
            pref = frappe.get_doc("Notification Preference", {"user": "Administrator"})
        except frappe.DoesNotExistError:
            pref = frappe.new_doc("Notification Preference")
            pref.user = "Administrator"

        pref.enabled = 0
        pref.save(ignore_permissions=True)

        result = unified_send(
            recipient="Administrator",
            title="Test Preferences",
            message="Test message",
            respect_preferences=True
        )

        # Should fail because notifications are disabled
        self.assertFalse(result.get("success"))

        # Re-enable
        pref.enabled = 1
        pref.save(ignore_permissions=True)

    def test_unified_send_deduplication(self):
        """Test message deduplication"""
        from university_erp.university_erp.unified_communication import unified_send

        # Send first message
        result1 = unified_send(
            recipient="Administrator",
            title="Dedup Test",
            message="Same message",
            channels=["in_app"],
            deduplicate=True
        )

        # Send duplicate immediately
        result2 = unified_send(
            recipient="Administrator",
            title="Dedup Test",
            message="Same message",
            channels=["in_app"],
            deduplicate=True
        )

        # Second should be blocked
        self.assertTrue(result2.get("deduplicated"))

        # Cleanup
        frappe.db.delete("User Notification", {"title": "Dedup Test"})


class TestSMSQueueFlow(FrappeTestCase):
    """Test cases for SMS queue flow"""

    def test_schedule_sms_flow(self):
        """Test SMS scheduling flow"""
        from university_erp.university_integrations.doctype.sms_queue.sms_queue import schedule_sms

        result = schedule_sms(
            mobile_number="9876543210",
            message="Test SMS",
            priority="Normal"
        )

        self.assertTrue(result.get("success"))
        self.assertIsNotNone(result.get("queue_id"))

        # Cleanup
        if result.get("queue_id"):
            frappe.delete_doc("SMS Queue", result.get("queue_id"), force=True)

    def test_bulk_sms_flow(self):
        """Test bulk SMS scheduling"""
        from university_erp.university_integrations.doctype.sms_queue.sms_queue import schedule_bulk_sms

        recipients = [
            {"mobile_number": "9876543210", "name": "User 1"},
            {"mobile_number": "9876543211", "name": "User 2"},
            {"mobile_number": "9876543212", "name": "User 3"}
        ]

        result = schedule_bulk_sms(
            recipients=recipients,
            message="Hello {name}, this is a test",
            priority="Normal"
        )

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("queued_count"), 3)

        # Cleanup
        if result.get("batch_id"):
            frappe.db.delete("SMS Queue", {"batch_id": result.get("batch_id")})


class TestEmailQueueFlow(FrappeTestCase):
    """Test cases for email queue flow"""

    def test_queue_email_flow(self):
        """Test email queueing flow"""
        from university_erp.university_integrations.doctype.email_queue_extended.email_queue_extended import queue_email

        result = queue_email(
            recipient="test@example.com",
            subject="Test Email",
            message="<p>This is a test email</p>",
            priority="Normal"
        )

        self.assertTrue(result.get("success"))
        self.assertIsNotNone(result.get("queue_id"))

        # Cleanup
        if result.get("queue_id"):
            frappe.delete_doc("Email Queue Extended", result.get("queue_id"), force=True)

    def test_priority_email_flow(self):
        """Test priority email queueing"""
        from university_erp.university_integrations.doctype.email_queue_extended.email_queue_extended import queue_email

        result = queue_email(
            recipient="test@example.com",
            subject="Urgent Email",
            message="This is urgent",
            priority="Urgent"
        )

        self.assertTrue(result.get("success"))

        # Verify priority
        if result.get("queue_id"):
            doc = frappe.get_doc("Email Queue Extended", result.get("queue_id"))
            self.assertEqual(doc.priority, "Urgent")

            # Cleanup
            frappe.delete_doc("Email Queue Extended", result.get("queue_id"), force=True)


class TestNotificationTemplateFlow(FrappeTestCase):
    """Test cases for notification template flow"""

    def test_notification_service_send(self):
        """Test NotificationService send flow"""
        from university_erp.university_erp.notification_service import NotificationService

        # This test would require a Notification Template to exist
        # Skip if template doesn't exist
        if not frappe.db.exists("Notification Template", "test_template"):
            return

        result = NotificationService.send_notification(
            recipients=["Administrator"],
            template_name="test_template",
            context={"name": "Test User"},
            channels=["email"]
        )

        self.assertIsInstance(result, list)


class TestEmergencyBroadcastFlow(FrappeTestCase):
    """Test cases for emergency broadcast flow"""

    def test_full_emergency_flow(self):
        """Test complete emergency broadcast flow"""
        # Create alert
        alert = frappe.get_doc({
            "doctype": "Emergency Alert",
            "alert_type": "Fire",
            "severity": "Critical",
            "status": "Draft",
            "title": "Flow Test Fire Alert",
            "message": "This is a test",
            "instructions": "Evacuate",
            "target_audience": "All",
            "send_push": 0,
            "send_sms": 0,
            "send_whatsapp": 0,
            "send_email": 0
        })
        alert.insert(ignore_permissions=True)

        # Broadcast
        with patch.object(alert, 'send_notifications'):
            alert.broadcast()

        alert.reload()
        self.assertEqual(alert.status, "Active")

        # Acknowledge
        ack = frappe.get_doc({
            "doctype": "Emergency Acknowledgment",
            "emergency_alert": alert.name,
            "user": "Administrator",
            "status": "Safe"
        })
        ack.insert(ignore_permissions=True)

        # Resolve
        with patch.object(alert, 'send_all_clear'):
            alert.resolve()

        alert.reload()
        self.assertEqual(alert.status, "Resolved")

        # Cleanup
        frappe.delete_doc("Emergency Acknowledgment", ack.name, force=True)
        frappe.delete_doc("Emergency Alert", alert.name, force=True)


class TestCommunicationAnalyticsFlow(FrappeTestCase):
    """Test cases for communication analytics"""

    def test_report_execution(self):
        """Test communication analytics report execution"""
        from university_erp.university_erp.report.communication_analytics.communication_analytics import execute

        filters = {
            "report_type": "summary",
            "from_date": frappe.utils.add_days(frappe.utils.nowdate(), -30),
            "to_date": frappe.utils.nowdate()
        }

        columns, data, _, chart, summary = execute(filters)

        self.assertIsInstance(columns, list)
        self.assertIsInstance(data, list)
        self.assertIsInstance(summary, list)

    def test_daily_report(self):
        """Test daily report generation"""
        from university_erp.university_erp.report.communication_analytics.communication_analytics import execute

        filters = {
            "report_type": "daily",
            "from_date": frappe.utils.add_days(frappe.utils.nowdate(), -7),
            "to_date": frappe.utils.nowdate()
        }

        columns, data, _, _, _ = execute(filters)

        self.assertIsInstance(columns, list)
        # Should have date column
        self.assertTrue(any(c.get("fieldname") == "date" for c in columns))
