# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock


class TestEmergencyAlert(FrappeTestCase):
    """Test cases for Emergency Alert"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_alert = None

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if cls.test_alert and frappe.db.exists("Emergency Alert", cls.test_alert.name):
            # Delete acknowledgments first
            frappe.db.delete("Emergency Acknowledgment", {"emergency_alert": cls.test_alert.name})
            frappe.delete_doc("Emergency Alert", cls.test_alert.name, force=True)

    def test_create_emergency_alert(self):
        """Test creating an emergency alert"""
        alert = frappe.get_doc({
            "doctype": "Emergency Alert",
            "alert_type": "Fire",
            "severity": "High",
            "status": "Draft",
            "title": "Test Fire Alert",
            "message": "This is a test fire alert.",
            "instructions": "Please evacuate immediately.",
            "target_audience": "All"
        })
        alert.insert(ignore_permissions=True)

        self.__class__.test_alert = alert

        self.assertIsNotNone(alert.name)
        self.assertEqual(alert.status, "Draft")

    def test_broadcast_alert(self):
        """Test broadcasting an alert"""
        if not self.test_alert:
            self.test_create_emergency_alert()

        # Mock the broadcast method to avoid actual sends
        with patch.object(self.test_alert, 'send_notifications'):
            result = self.test_alert.broadcast()

            # After broadcast, status should be Active
            self.test_alert.reload()
            self.assertEqual(self.test_alert.status, "Active")

    def test_resolve_alert(self):
        """Test resolving an alert"""
        if not self.test_alert:
            self.test_create_emergency_alert()

        # Set to Active first
        self.test_alert.status = "Active"
        self.test_alert.save(ignore_permissions=True)

        with patch.object(self.test_alert, 'send_all_clear'):
            result = self.test_alert.resolve()

            self.test_alert.reload()
            self.assertEqual(self.test_alert.status, "Resolved")

    def test_cancel_alert(self):
        """Test cancelling an alert"""
        # Create new alert for cancel test
        alert = frappe.get_doc({
            "doctype": "Emergency Alert",
            "alert_type": "Other",
            "severity": "Low",
            "status": "Draft",
            "title": "Cancel Test",
            "message": "Test message"
        })
        alert.insert(ignore_permissions=True)

        alert.cancel_alert()

        alert.reload()
        self.assertEqual(alert.status, "Cancelled")

        # Cleanup
        frappe.delete_doc("Emergency Alert", alert.name, force=True)

    def test_get_recipients_all(self):
        """Test getting recipients for 'All' audience"""
        if not self.test_alert:
            self.test_create_emergency_alert()

        self.test_alert.target_audience = "All"
        recipients = self.test_alert.get_recipients()

        self.assertIsInstance(recipients, list)

    def test_calculate_acknowledgment_rate(self):
        """Test acknowledgment rate calculation"""
        if not self.test_alert:
            self.test_create_emergency_alert()

        self.test_alert.total_recipients = 100
        self.test_alert.acknowledgments_received = 75

        self.test_alert.calculate_acknowledgment_rate()

        self.assertEqual(self.test_alert.acknowledgment_rate, 75.0)


class TestEmergencyAcknowledgment(FrappeTestCase):
    """Test cases for Emergency Acknowledgment"""

    def test_create_acknowledgment(self):
        """Test creating an acknowledgment"""
        # Create test alert first
        alert = frappe.get_doc({
            "doctype": "Emergency Alert",
            "alert_type": "Medical Emergency",
            "severity": "High",
            "status": "Active",
            "title": "Ack Test Alert",
            "message": "Test message"
        })
        alert.insert(ignore_permissions=True)

        # Create acknowledgment
        ack = frappe.get_doc({
            "doctype": "Emergency Acknowledgment",
            "emergency_alert": alert.name,
            "user": "Administrator",
            "status": "Safe"
        })
        ack.insert(ignore_permissions=True)

        self.assertIsNotNone(ack.name)
        self.assertIsNotNone(ack.acknowledged_at)

        # Cleanup
        frappe.delete_doc("Emergency Acknowledgment", ack.name, force=True)
        frappe.delete_doc("Emergency Alert", alert.name, force=True)


class TestEmergencyBroadcast(FrappeTestCase):
    """Test cases for Emergency Broadcast module"""

    def test_quick_broadcast(self):
        """Test quick broadcast function"""
        from university_erp.university_erp.emergency_broadcast import quick_broadcast

        with patch('university_erp.university_erp.emergency_broadcast.EmergencyBroadcast') as MockBroadcast:
            mock_instance = MagicMock()
            MockBroadcast.return_value = mock_instance

            result = quick_broadcast(
                alert_type="Fire",
                title="Quick Test",
                message="Test message"
            )

            # Should create an alert
            self.assertIsNotNone(result)

    def test_send_fire_alert(self):
        """Test fire alert quick function"""
        from university_erp.university_erp.emergency_broadcast import send_fire_alert

        with patch('university_erp.university_erp.emergency_broadcast.quick_broadcast') as mock_broadcast:
            mock_broadcast.return_value = {"alert": "test123"}

            result = send_fire_alert(
                location="Building A",
                message="Fire detected"
            )

            mock_broadcast.assert_called_once()

    def test_send_lockdown_alert(self):
        """Test lockdown alert quick function"""
        from university_erp.university_erp.emergency_broadcast import send_lockdown_alert

        with patch('university_erp.university_erp.emergency_broadcast.quick_broadcast') as mock_broadcast:
            mock_broadcast.return_value = {"alert": "test123"}

            result = send_lockdown_alert(
                reason="Security threat",
                instructions="Stay in place"
            )

            mock_broadcast.assert_called_once()


class TestEmergencyAlertAPI(FrappeTestCase):
    """Test cases for Emergency Alert API endpoints"""

    def test_get_active_alerts(self):
        """Test get_active_alerts API"""
        from university_erp.university_erp.doctype.emergency_alert.emergency_alert import get_active_alerts

        result = get_active_alerts()

        self.assertIsInstance(result, list)

    def test_get_emergency_contacts(self):
        """Test get_emergency_contacts API"""
        from university_erp.university_erp.doctype.emergency_alert.emergency_alert import get_emergency_contacts

        result = get_emergency_contacts()

        self.assertIsInstance(result, dict)
        self.assertIn("police", result)
        self.assertIn("fire", result)
        self.assertIn("ambulance", result)

    def test_acknowledge_alert(self):
        """Test acknowledge API"""
        from university_erp.university_erp.doctype.emergency_alert.emergency_alert import acknowledge

        # Create test alert
        alert = frappe.get_doc({
            "doctype": "Emergency Alert",
            "alert_type": "Other",
            "severity": "Low",
            "status": "Active",
            "title": "Ack API Test",
            "message": "Test"
        })
        alert.insert(ignore_permissions=True)

        result = acknowledge(
            alert_name=alert.name,
            status="Safe"
        )

        self.assertTrue(result.get("success"))

        # Cleanup
        frappe.db.delete("Emergency Acknowledgment", {"emergency_alert": alert.name})
        frappe.delete_doc("Emergency Alert", alert.name, force=True)
