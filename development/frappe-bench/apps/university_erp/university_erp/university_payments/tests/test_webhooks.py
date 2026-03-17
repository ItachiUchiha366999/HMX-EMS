"""
Test cases for Webhook handlers

Tests the Razorpay and PayU webhook handling functionality.
"""
import frappe
import unittest
import json
import hmac
import hashlib
from unittest.mock import patch, MagicMock
from frappe.tests.utils import FrappeTestCase


class TestRazorpayWebhook(FrappeTestCase):
    """Test Razorpay webhook handler"""

    def test_signature_verification(self):
        """Test Razorpay webhook signature verification"""
        from university_erp.university_payments.webhooks.razorpay_webhook import verify_webhook_signature

        webhook_secret = "test_webhook_secret"
        payload = '{"event": "payment.captured", "payload": {"payment": {"entity": {"id": "pay_123"}}}}'

        # Generate valid signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Test valid signature
        is_valid = verify_webhook_signature(payload, expected_signature, webhook_secret)
        self.assertTrue(is_valid)

        # Test invalid signature
        is_valid = verify_webhook_signature(payload, "invalid_signature", webhook_secret)
        self.assertFalse(is_valid)

    def test_payment_captured_event_parsing(self):
        """Test parsing of payment.captured event"""
        from university_erp.university_payments.webhooks.razorpay_webhook import parse_payment_event

        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_123",
                        "order_id": "order_456",
                        "amount": 1000000,  # In paise
                        "status": "captured",
                        "method": "upi"
                    }
                }
            }
        }

        result = parse_payment_event(payload)
        self.assertEqual(result["payment_id"], "pay_123")
        self.assertEqual(result["order_id"], "order_456")
        self.assertEqual(result["amount"], 10000)  # Converted to rupees
        self.assertEqual(result["status"], "captured")

    def test_payment_failed_event_parsing(self):
        """Test parsing of payment.failed event"""
        from university_erp.university_payments.webhooks.razorpay_webhook import parse_payment_event

        payload = {
            "event": "payment.failed",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_123",
                        "order_id": "order_456",
                        "amount": 1000000,
                        "status": "failed",
                        "error_code": "BAD_REQUEST_ERROR",
                        "error_description": "Payment failed due to insufficient funds"
                    }
                }
            }
        }

        result = parse_payment_event(payload)
        self.assertEqual(result["status"], "failed")
        self.assertIn("error_code", result)

    def test_refund_event_parsing(self):
        """Test parsing of refund.created event"""
        from university_erp.university_payments.webhooks.razorpay_webhook import parse_refund_event

        payload = {
            "event": "refund.created",
            "payload": {
                "refund": {
                    "entity": {
                        "id": "rfnd_123",
                        "payment_id": "pay_456",
                        "amount": 500000,
                        "status": "processed"
                    }
                }
            }
        }

        result = parse_refund_event(payload)
        self.assertEqual(result["refund_id"], "rfnd_123")
        self.assertEqual(result["payment_id"], "pay_456")
        self.assertEqual(result["amount"], 5000)

    def test_webhook_log_creation(self):
        """Test that webhook events are logged"""
        webhook_log = frappe.get_doc({
            "doctype": "Webhook Log",
            "payment_gateway": "Razorpay",
            "event_type": "payment.captured",
            "payload": '{"test": "data"}',
            "status": "Received"
        })

        # Should not raise any errors
        webhook_log.validate()


class TestPayUCallback(FrappeTestCase):
    """Test PayU callback handlers"""

    def test_response_hash_verification(self):
        """Test PayU response hash verification"""
        from university_erp.university_payments.webhooks.payu_callback import verify_payu_hash

        merchant_salt = "test_salt"

        response = {
            "status": "success",
            "txnid": "TXN123",
            "amount": "1000.00",
            "productinfo": "Test Fee",
            "firstname": "Test",
            "email": "test@test.com",
            "mihpayid": "PAY123",
            "key": "test_key"
        }

        # Generate expected hash
        hash_string = f"{merchant_salt}|{response['status']}|||||||||||{response['email']}|{response['firstname']}|{response['productinfo']}|{response['amount']}|{response['txnid']}|{response['key']}"
        expected_hash = hashlib.sha512(hash_string.encode()).hexdigest().lower()

        is_valid = verify_payu_hash(response, expected_hash, merchant_salt)
        self.assertTrue(is_valid)

    def test_success_callback_parameters(self):
        """Test success callback parameter extraction"""
        from university_erp.university_payments.webhooks.payu_callback import extract_payment_data

        response = {
            "status": "success",
            "txnid": "TXN123",
            "amount": "1000.00",
            "mihpayid": "PAY123",
            "mode": "UPI",
            "bank_ref_num": "BANK123"
        }

        result = extract_payment_data(response)
        self.assertEqual(result["transaction_id"], "TXN123")
        self.assertEqual(result["amount"], 1000.00)
        self.assertEqual(result["gateway_payment_id"], "PAY123")
        self.assertEqual(result["payment_mode"], "UPI")

    def test_failure_callback_parameters(self):
        """Test failure callback parameter extraction"""
        from university_erp.university_payments.webhooks.payu_callback import extract_payment_data

        response = {
            "status": "failure",
            "txnid": "TXN123",
            "amount": "1000.00",
            "error": "E001",
            "error_Message": "Payment declined by bank"
        }

        result = extract_payment_data(response)
        self.assertEqual(result["status"], "failure")
        self.assertIn("error", result)

    def test_cancel_callback_handling(self):
        """Test cancel callback handling"""
        from university_erp.university_payments.webhooks.payu_callback import handle_cancel

        response = {
            "txnid": "TXN123"
        }

        # Should not raise any errors
        result = handle_cancel(response)
        self.assertIn("status", result)


class TestWebhookIdempotency(FrappeTestCase):
    """Test webhook idempotency handling"""

    def test_duplicate_event_detection(self):
        """Test that duplicate events are detected"""
        from university_erp.university_payments.webhooks.razorpay_webhook import is_duplicate_event

        event_id = "evt_123456"

        # First event should not be duplicate
        is_dup = is_duplicate_event(event_id, "Razorpay")
        self.assertFalse(is_dup)

        # Create a webhook log for this event
        if frappe.db.exists("Webhook Log", {"event_id": event_id}):
            frappe.db.delete("Webhook Log", {"event_id": event_id})

        frappe.get_doc({
            "doctype": "Webhook Log",
            "payment_gateway": "Razorpay",
            "event_type": "payment.captured",
            "event_id": event_id,
            "payload": '{"test": "data"}',
            "status": "Processed"
        }).insert(ignore_permissions=True)

        # Same event should now be detected as duplicate
        is_dup = is_duplicate_event(event_id, "Razorpay")
        self.assertTrue(is_dup)

        # Cleanup
        frappe.db.delete("Webhook Log", {"event_id": event_id})


class TestWebhookErrorHandling(FrappeTestCase):
    """Test webhook error handling"""

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON payload"""
        from university_erp.university_payments.webhooks.razorpay_webhook import parse_webhook_payload

        invalid_json = "not a valid json"

        with self.assertRaises(ValueError):
            parse_webhook_payload(invalid_json)

    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        from university_erp.university_payments.webhooks.razorpay_webhook import validate_payload

        incomplete_payload = {
            "event": "payment.captured"
            # Missing payload field
        }

        with self.assertRaises(ValueError):
            validate_payload(incomplete_payload)

    def test_webhook_retry_logging(self):
        """Test that webhook retries are logged"""
        webhook_log = frappe.get_doc({
            "doctype": "Webhook Log",
            "payment_gateway": "Razorpay",
            "event_type": "payment.captured",
            "payload": '{"test": "data"}',
            "status": "Failed",
            "error_message": "Processing error",
            "retry_count": 1
        })

        webhook_log.validate()
        self.assertEqual(webhook_log.retry_count, 1)


if __name__ == "__main__":
    unittest.main()
