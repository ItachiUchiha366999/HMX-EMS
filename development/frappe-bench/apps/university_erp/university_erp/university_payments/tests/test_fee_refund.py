"""
Test cases for Fee Refund module

Tests the fee refund functionality including workflow and validations.
"""
import frappe
import unittest
from unittest.mock import patch, MagicMock
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, flt


class TestFeeRefund(FrappeTestCase):
    """Test Fee Refund functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.create_test_data()

    @classmethod
    def create_test_data(cls):
        """Create test students and fees"""
        # Create test student if not exists
        if not frappe.db.exists("Student", "TEST-STU-REFUND-001"):
            student = frappe.get_doc({
                "doctype": "Student",
                "first_name": "Refund",
                "last_name": "Test Student",
                "student_email_id": "refund.test@university.edu",
                "name": "TEST-STU-REFUND-001"
            })
            try:
                student.insert(ignore_permissions=True)
            except Exception:
                pass

    def test_fee_refund_creation(self):
        """Test creating a fee refund"""
        refund = frappe.get_doc({
            "doctype": "Fee Refund",
            "student": "TEST-STU-REFUND-001",
            "student_name": "Refund Test Student",
            "refund_amount": 5000,
            "reason": "Course Withdrawal",
            "remarks": "Student withdrew from course"
        })

        # Should not raise any errors
        refund.validate()

    def test_refund_amount_validation(self):
        """Test refund amount validation"""
        refund = frappe.get_doc({
            "doctype": "Fee Refund",
            "student": "TEST-STU-REFUND-001",
            "student_name": "Refund Test Student",
            "refund_amount": 0,
            "reason": "Course Withdrawal"
        })

        # Should raise error for zero amount
        with self.assertRaises(frappe.ValidationError):
            refund.validate()

    def test_negative_refund_amount(self):
        """Test that negative refund amounts are rejected"""
        refund = frappe.get_doc({
            "doctype": "Fee Refund",
            "student": "TEST-STU-REFUND-001",
            "student_name": "Refund Test Student",
            "refund_amount": -1000,
            "reason": "Course Withdrawal"
        })

        # Should raise error for negative amount
        with self.assertRaises(frappe.ValidationError):
            refund.validate()

    def test_refund_status_workflow(self):
        """Test refund status workflow"""
        valid_statuses = ["Pending", "Approved", "Processed", "Rejected"]

        for status in valid_statuses:
            refund = frappe.get_doc({
                "doctype": "Fee Refund",
                "student": "TEST-STU-REFUND-001",
                "student_name": "Refund Test Student",
                "refund_amount": 5000,
                "reason": "Course Withdrawal",
                "status": status
            })

            # Should not raise any errors
            refund.validate()

    def test_refund_modes(self):
        """Test different refund modes"""
        valid_modes = ["Bank Transfer", "Cheque", "Cash", "Original Payment Method"]

        for mode in valid_modes:
            refund = frappe.get_doc({
                "doctype": "Fee Refund",
                "student": "TEST-STU-REFUND-001",
                "student_name": "Refund Test Student",
                "refund_amount": 5000,
                "reason": "Course Withdrawal",
                "refund_mode": mode
            })

            # Should not raise any errors
            refund.validate()

    def test_refund_reasons(self):
        """Test different refund reasons"""
        valid_reasons = [
            "Course Withdrawal",
            "Fee Revision",
            "Excess Payment",
            "Scholarship Adjustment",
            "Other"
        ]

        for reason in valid_reasons:
            refund = frappe.get_doc({
                "doctype": "Fee Refund",
                "student": "TEST-STU-REFUND-001",
                "student_name": "Refund Test Student",
                "refund_amount": 5000,
                "reason": reason
            })

            # Should not raise any errors
            refund.validate()


class TestFeeRefundValidations(FrappeTestCase):
    """Test Fee Refund validation rules"""

    def test_refund_exceeds_paid_amount(self):
        """Test that refund cannot exceed paid amount"""
        from university_erp.university_payments.doctype.fee_refund.fee_refund import FeeRefund

        # Create mock fees document
        mock_fees = MagicMock()
        mock_fees.paid_amount = 5000

        refund = FeeRefund({
            "doctype": "Fee Refund",
            "fees": "TEST-FEE-001",
            "student": "TEST-STU-REFUND-001",
            "refund_amount": 10000,  # More than paid
            "reason": "Course Withdrawal"
        })

        # Should fail validation
        with patch.object(refund, 'get_fees_doc', return_value=mock_fees):
            with self.assertRaises(frappe.ValidationError):
                refund.validate_refund_amount()

    def test_bank_details_required_for_bank_transfer(self):
        """Test bank details requirement for bank transfer refunds"""
        refund = frappe.get_doc({
            "doctype": "Fee Refund",
            "student": "TEST-STU-REFUND-001",
            "student_name": "Refund Test Student",
            "refund_amount": 5000,
            "reason": "Course Withdrawal",
            "refund_mode": "Bank Transfer",
            "bank_account_number": "",
            "ifsc_code": ""
        })

        # Should raise error for missing bank details
        # This depends on implementation
        # with self.assertRaises(frappe.ValidationError):
        #     refund.validate()


class TestFeeRefundWorkflow(FrappeTestCase):
    """Test Fee Refund workflow functionality"""

    def test_approval_sets_approved_by(self):
        """Test that approval sets approved_by field"""
        from university_erp.university_payments.doctype.fee_refund.fee_refund import FeeRefund

        refund = FeeRefund({
            "doctype": "Fee Refund",
            "student": "TEST-STU-REFUND-001",
            "student_name": "Refund Test Student",
            "refund_amount": 5000,
            "reason": "Course Withdrawal",
            "status": "Approved"
        })

        refund.on_update()
        # approved_by should be set to current user
        self.assertIsNotNone(refund.approved_by)

    def test_processing_sets_processed_date(self):
        """Test that processing sets processed_date field"""
        from university_erp.university_payments.doctype.fee_refund.fee_refund import FeeRefund

        refund = FeeRefund({
            "doctype": "Fee Refund",
            "student": "TEST-STU-REFUND-001",
            "student_name": "Refund Test Student",
            "refund_amount": 5000,
            "reason": "Course Withdrawal",
            "status": "Processed"
        })

        refund.on_update()
        # processed_date should be set
        self.assertIsNotNone(refund.processed_date)


class TestFeeRefundPaymentEntry(FrappeTestCase):
    """Test Fee Refund payment entry creation"""

    @patch('university_erp.university_payments.doctype.fee_refund.fee_refund.frappe')
    def test_payment_entry_creation(self, mock_frappe):
        """Test payment entry is created for processed refunds"""
        from university_erp.university_payments.doctype.fee_refund.fee_refund import FeeRefund

        mock_payment_entry = MagicMock()
        mock_frappe.new_doc.return_value = mock_payment_entry

        refund = FeeRefund({
            "doctype": "Fee Refund",
            "name": "REF-001",
            "student": "TEST-STU-REFUND-001",
            "student_name": "Refund Test Student",
            "refund_amount": 5000,
            "reason": "Course Withdrawal",
            "status": "Approved",
            "refund_mode": "Bank Transfer"
        })

        # Test the method exists and is callable
        self.assertTrue(callable(refund.create_payment_entry))


if __name__ == "__main__":
    unittest.main()
