"""
Test cases for Payment Gateway module

Tests the unified payment gateway functionality for Razorpay and PayU.
"""
import frappe
import unittest
from unittest.mock import patch, MagicMock
from frappe.tests.utils import FrappeTestCase


class TestPaymentGateway(FrappeTestCase):
    """Test Payment Gateway functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.create_test_data()

    @classmethod
    def create_test_data(cls):
        """Create test students, fees, and settings"""
        # Create test student if not exists
        if not frappe.db.exists("Student", "TEST-STU-PAY-001"):
            student = frappe.get_doc({
                "doctype": "Student",
                "first_name": "Test",
                "last_name": "Payment Student",
                "student_email_id": "test.payment@university.edu",
                "name": "TEST-STU-PAY-001"
            })
            student.insert(ignore_permissions=True)

        # Create test fee category if not exists
        if not frappe.db.exists("Fee Category", "Test Tuition Fee"):
            fee_cat = frappe.get_doc({
                "doctype": "Fee Category",
                "category_name": "Test Tuition Fee"
            })
            fee_cat.insert(ignore_permissions=True)

    def test_razorpay_settings_validation(self):
        """Test Razorpay settings validation"""
        settings = frappe.get_doc({
            "doctype": "Razorpay Settings",
            "enabled": 1,
            "api_key": "",
            "api_secret": ""
        })

        # Should fail validation without API keys when enabled
        with self.assertRaises(frappe.ValidationError):
            settings.validate()

    def test_payu_settings_validation(self):
        """Test PayU settings validation"""
        settings = frappe.get_doc({
            "doctype": "PayU Settings",
            "enabled": 1,
            "merchant_key": "",
            "merchant_salt": ""
        })

        # Should fail validation without credentials when enabled
        with self.assertRaises(frappe.ValidationError):
            settings.validate()

    def test_payu_hash_generation(self):
        """Test PayU hash generation"""
        from university_erp.university_payments.doctype.payu_settings.payu_settings import PayUSettings

        settings = PayUSettings({
            "doctype": "PayU Settings",
            "merchant_key": "test_key",
            "merchant_salt": "test_salt"
        })

        # Test hash generation
        params = {
            "key": "test_key",
            "txnid": "TXN123",
            "amount": "1000.00",
            "productinfo": "Test Fee",
            "firstname": "Test",
            "email": "test@test.com"
        }

        hash_value = settings.generate_hash(params)
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 128)  # SHA512 hash length

    def test_payu_response_hash_verification(self):
        """Test PayU response hash verification"""
        from university_erp.university_payments.doctype.payu_settings.payu_settings import PayUSettings

        settings = PayUSettings({
            "doctype": "PayU Settings",
            "merchant_key": "test_key",
            "merchant_salt": "test_salt"
        })

        # Generate hash for verification
        params = {
            "status": "success",
            "email": "test@test.com",
            "firstname": "Test",
            "productinfo": "Test Fee",
            "amount": "1000.00",
            "txnid": "TXN123",
            "key": "test_key"
        }

        # Generate expected hash
        expected_hash = settings.generate_response_hash(params)
        self.assertTrue(settings.verify_response_hash(params, expected_hash))

    @patch('university_erp.university_payments.payment_gateway.frappe')
    def test_payment_order_creation(self, mock_frappe):
        """Test payment order creation"""
        mock_frappe.get_doc = MagicMock()
        mock_frappe.new_doc = MagicMock()

        # This is a basic structural test
        # In production, you'd test against actual database
        from university_erp.university_payments.payment_gateway import PaymentGateway

        gateway = PaymentGateway("razorpay")
        self.assertEqual(gateway.gateway_type, "razorpay")

    def test_amount_validation(self):
        """Test that payment amounts are validated correctly"""
        from university_erp.university_payments.payment_gateway import PaymentGateway

        gateway = PaymentGateway("razorpay")

        # Test valid amount
        self.assertTrue(gateway.validate_amount(1000))
        self.assertTrue(gateway.validate_amount(1.50))

        # Test invalid amounts
        self.assertFalse(gateway.validate_amount(0))
        self.assertFalse(gateway.validate_amount(-100))

    def test_gateway_type_detection(self):
        """Test payment gateway type detection"""
        from university_erp.university_payments.payment_gateway import PaymentGateway

        razorpay_gateway = PaymentGateway("razorpay")
        self.assertEqual(razorpay_gateway.gateway_type, "razorpay")

        payu_gateway = PaymentGateway("payu")
        self.assertEqual(payu_gateway.gateway_type, "payu")

        # Test invalid gateway
        with self.assertRaises(ValueError):
            PaymentGateway("invalid_gateway")


class TestPaymentOrder(FrappeTestCase):
    """Test Payment Order DocType"""

    def test_payment_order_creation(self):
        """Test creating a payment order"""
        payment_order = frappe.get_doc({
            "doctype": "Payment Order",
            "reference_doctype": "Fees",
            "reference_name": "TEST-FEE-001",
            "student": "TEST-STU-PAY-001",
            "payment_gateway": "Razorpay",
            "amount": 10000,
            "status": "Pending"
        })

        # Should not raise any errors
        payment_order.validate()

    def test_payment_order_status_transitions(self):
        """Test valid payment order status transitions"""
        valid_transitions = [
            ("Pending", "Completed"),
            ("Pending", "Failed"),
            ("Completed", "Refunded"),
        ]

        for from_status, to_status in valid_transitions:
            payment_order = frappe.get_doc({
                "doctype": "Payment Order",
                "reference_doctype": "Fees",
                "reference_name": "TEST-FEE-001",
                "student": "TEST-STU-PAY-001",
                "payment_gateway": "Razorpay",
                "amount": 10000,
                "status": from_status
            })

            payment_order.status = to_status
            # Should not raise any errors for valid transitions
            payment_order.validate()


class TestWebhookLog(FrappeTestCase):
    """Test Webhook Log DocType"""

    def test_webhook_log_creation(self):
        """Test creating a webhook log entry"""
        webhook_log = frappe.get_doc({
            "doctype": "Webhook Log",
            "payment_gateway": "Razorpay",
            "event_type": "payment.captured",
            "payload": '{"id": "pay_123", "amount": 10000}',
            "status": "Received"
        })

        # Should not raise any errors
        webhook_log.validate()

    def test_webhook_log_status_update(self):
        """Test webhook log status updates"""
        webhook_log = frappe.get_doc({
            "doctype": "Webhook Log",
            "payment_gateway": "Razorpay",
            "event_type": "payment.captured",
            "payload": '{"id": "pay_123"}',
            "status": "Received"
        })

        webhook_log.status = "Processed"
        webhook_log.validate()
        self.assertEqual(webhook_log.status, "Processed")


if __name__ == "__main__":
    unittest.main()
