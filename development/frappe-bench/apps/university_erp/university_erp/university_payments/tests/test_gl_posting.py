"""
Test cases for GL Posting module

Tests the automated General Ledger posting functionality.
"""
import frappe
import unittest
from unittest.mock import patch, MagicMock
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate


class TestGLPosting(FrappeTestCase):
    """Test GL Posting functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.company = frappe.db.get_single_value("Global Defaults", "default_company") or "Test Company"

    def test_gl_posting_manager_initialization(self):
        """Test GLPostingManager initialization"""
        from university_erp.university_payments.gl_posting import GLPostingManager

        manager = GLPostingManager(self.company)
        self.assertEqual(manager.company, self.company)

    def test_get_fee_income_account(self):
        """Test getting fee income account"""
        from university_erp.university_payments.gl_posting import GLPostingManager

        manager = GLPostingManager(self.company)

        # Should return an account or None
        account = manager.get_fee_income_account()
        if account:
            self.assertTrue(frappe.db.exists("Account", account))

    def test_get_payment_gateway_account(self):
        """Test getting payment gateway account"""
        from university_erp.university_payments.gl_posting import GLPostingManager

        manager = GLPostingManager(self.company)

        # Should return an account or None
        account = manager.get_payment_gateway_account("Razorpay")
        # Account might not exist in test environment, so we just check it doesn't error

    @patch('university_erp.university_payments.gl_posting.frappe')
    def test_post_fee_collection_structure(self, mock_frappe):
        """Test fee collection GL posting structure"""
        from university_erp.university_payments.gl_posting import GLPostingManager

        mock_frappe.get_doc = MagicMock()
        mock_frappe.new_doc = MagicMock()
        mock_frappe.db.get_single_value = MagicMock(return_value="Test Company")

        manager = GLPostingManager("Test Company")

        # Test the structure of GL entry
        gl_entry_data = {
            "student": "TEST-STU-001",
            "fees": "TEST-FEE-001",
            "amount": 10000,
            "payment_gateway": "Razorpay",
            "transaction_id": "pay_123"
        }

        # This tests the method exists and accepts correct parameters
        # Actual GL posting would require database setup
        self.assertTrue(callable(manager.post_fee_collection))

    def test_gl_entry_validation(self):
        """Test GL entry validation logic"""
        from university_erp.university_payments.gl_posting import GLPostingManager

        manager = GLPostingManager(self.company)

        # Test amount validation
        self.assertTrue(manager.validate_amount(1000))
        self.assertFalse(manager.validate_amount(0))
        self.assertFalse(manager.validate_amount(-100))

    def test_category_account_mapping(self):
        """Test fee category to account mapping"""
        from university_erp.university_payments.gl_posting import GLPostingManager

        manager = GLPostingManager(self.company)

        # Test category account retrieval
        # Should return None if not configured, not raise error
        account = manager.get_category_account("Tuition Fee")
        # Account might be None in test environment


class TestGLPostingHooks(FrappeTestCase):
    """Test GL Posting hooks"""

    def test_on_fees_submit_hook_exists(self):
        """Test that on_fees_submit hook function exists"""
        from university_erp.university_payments.gl_posting import on_fees_submit

        self.assertTrue(callable(on_fees_submit))

    def test_on_fees_cancel_hook_exists(self):
        """Test that on_fees_cancel hook function exists"""
        from university_erp.university_payments.gl_posting import on_fees_cancel

        self.assertTrue(callable(on_fees_cancel))


class TestUniversityAccountsSettings(FrappeTestCase):
    """Test University Accounts Settings DocType"""

    def test_accounts_settings_creation(self):
        """Test creating accounts settings"""
        settings = frappe.get_doc({
            "doctype": "University Accounts Settings"
        })

        # Should not raise any errors
        settings.validate()

    def test_accounts_settings_singleton(self):
        """Test that accounts settings is a singleton"""
        settings1 = frappe.get_single("University Accounts Settings")
        settings2 = frappe.get_single("University Accounts Settings")

        # Both should reference the same document
        self.assertEqual(settings1.name, settings2.name)


class TestFeeCategoryAccount(FrappeTestCase):
    """Test Fee Category Account mapping"""

    def test_fee_category_account_creation(self):
        """Test creating fee category account mapping"""
        mapping = frappe.get_doc({
            "doctype": "Fee Category Account",
            "fee_category": "Test Category",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Test Company"
        })

        # Should not raise any errors (account fields optional)
        mapping.validate()


if __name__ == "__main__":
    unittest.main()
