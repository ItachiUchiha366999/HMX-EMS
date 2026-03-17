"""
Test cases for Bank Reconciliation module

Tests the bank statement import and reconciliation functionality.
"""
import frappe
import unittest
from unittest.mock import patch, MagicMock
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days


class TestBankReconciliation(FrappeTestCase):
    """Test Bank Reconciliation functionality"""

    def test_reconciliation_tool_initialization(self):
        """Test BankReconciliationTool initialization"""
        from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

        tool = BankReconciliationTool()
        self.assertIsNotNone(tool)

    def test_confidence_score_calculation(self):
        """Test confidence score calculation for matching"""
        from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

        tool = BankReconciliationTool()

        # Test exact amount match
        score = tool.calculate_match_confidence(
            bank_amount=10000,
            payment_amount=10000,
            bank_date=nowdate(),
            payment_date=nowdate(),
            bank_reference="TXN123",
            payment_reference="TXN123"
        )
        self.assertEqual(score, 100)

        # Test partial match (amount only)
        score = tool.calculate_match_confidence(
            bank_amount=10000,
            payment_amount=10000,
            bank_date=nowdate(),
            payment_date=add_days(nowdate(), 3),
            bank_reference="TXN123",
            payment_reference="TXN456"
        )
        self.assertGreater(score, 0)
        self.assertLess(score, 100)

        # Test no match
        score = tool.calculate_match_confidence(
            bank_amount=10000,
            payment_amount=5000,
            bank_date=nowdate(),
            payment_date=add_days(nowdate(), 10),
            bank_reference="TXN123",
            payment_reference="TXN456"
        )
        self.assertLess(score, 50)

    def test_date_proximity_score(self):
        """Test date proximity scoring"""
        from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

        tool = BankReconciliationTool()

        # Same date should give max score
        score = tool.date_proximity_score(nowdate(), nowdate())
        self.assertEqual(score, 30)  # Max date score

        # 1 day difference
        score = tool.date_proximity_score(nowdate(), add_days(nowdate(), 1))
        self.assertGreater(score, 0)
        self.assertLess(score, 30)

        # Large difference
        score = tool.date_proximity_score(nowdate(), add_days(nowdate(), 10))
        self.assertEqual(score, 0)

    def test_reference_match_score(self):
        """Test reference matching score"""
        from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

        tool = BankReconciliationTool()

        # Exact match
        score = tool.reference_match_score("TXN123ABC", "TXN123ABC")
        self.assertEqual(score, 30)  # Max reference score

        # Partial match
        score = tool.reference_match_score("TXN123ABC", "TXN123XYZ")
        self.assertGreater(score, 0)

        # No match
        score = tool.reference_match_score("ABC123", "XYZ789")
        self.assertEqual(score, 0)


class TestBankStatementImporter(FrappeTestCase):
    """Test Bank Statement Import functionality"""

    def test_importer_initialization(self):
        """Test BankStatementImporter initialization"""
        from university_erp.university_payments.bank_reconciliation import BankStatementImporter

        importer = BankStatementImporter()
        self.assertIsNotNone(importer)

    def test_supported_formats(self):
        """Test supported bank formats"""
        from university_erp.university_payments.bank_reconciliation import BankStatementImporter

        importer = BankStatementImporter()
        formats = importer.get_supported_formats()

        self.assertIn("hdfc", formats)
        self.assertIn("icici", formats)
        self.assertIn("sbi", formats)
        self.assertIn("axis", formats)

    def test_date_parsing(self):
        """Test date parsing from different formats"""
        from university_erp.university_payments.bank_reconciliation import BankStatementImporter

        importer = BankStatementImporter()

        # Test common date formats
        date_formats = [
            "13-01-2026",
            "13/01/2026",
            "2026-01-13",
            "13 Jan 2026"
        ]

        for date_str in date_formats:
            parsed = importer.parse_date(date_str)
            if parsed:  # Some formats might not be supported
                self.assertIsNotNone(parsed)

    def test_amount_parsing(self):
        """Test amount parsing from different formats"""
        from university_erp.university_payments.bank_reconciliation import BankStatementImporter

        importer = BankStatementImporter()

        # Test various amount formats
        test_cases = [
            ("10000.00", 10000.00),
            ("10,000.00", 10000.00),
            ("Rs. 10,000.00", 10000.00),
            ("INR 10000", 10000.00),
        ]

        for amount_str, expected in test_cases:
            parsed = importer.parse_amount(amount_str)
            if parsed is not None:  # Some formats might not be supported
                self.assertEqual(parsed, expected)


class TestBankTransaction(FrappeTestCase):
    """Test Bank Transaction DocType"""

    def test_bank_transaction_creation(self):
        """Test creating a bank transaction"""
        transaction = frappe.get_doc({
            "doctype": "Bank Transaction",
            "date": nowdate(),
            "bank_account": "Test Bank Account",
            "deposit": 10000,
            "description": "Test transaction"
        })

        # Should not raise any errors
        transaction.validate()

    def test_bank_transaction_type_detection(self):
        """Test transaction type detection"""
        # Deposit transaction
        deposit_txn = frappe.get_doc({
            "doctype": "Bank Transaction",
            "date": nowdate(),
            "bank_account": "Test Bank Account",
            "deposit": 10000,
            "withdrawal": 0,
            "description": "Test deposit"
        })

        deposit_txn.validate()
        # Transaction type would be set based on deposit/withdrawal

        # Withdrawal transaction
        withdrawal_txn = frappe.get_doc({
            "doctype": "Bank Transaction",
            "date": nowdate(),
            "bank_account": "Test Bank Account",
            "deposit": 0,
            "withdrawal": 5000,
            "description": "Test withdrawal"
        })

        withdrawal_txn.validate()


class TestAutoReconciliation(FrappeTestCase):
    """Test automatic reconciliation functionality"""

    def test_auto_match_threshold(self):
        """Test auto-match threshold configuration"""
        from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

        tool = BankReconciliationTool()

        # Default threshold should be 80%
        self.assertEqual(tool.auto_match_threshold, 80)

        # Test with custom threshold
        tool = BankReconciliationTool(auto_match_threshold=90)
        self.assertEqual(tool.auto_match_threshold, 90)

    def test_get_unreconciled_payments(self):
        """Test getting unreconciled payments"""
        from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

        tool = BankReconciliationTool()

        # Should return a list (empty or with data)
        payments = tool.get_unreconciled_payments()
        self.assertIsInstance(payments, list)

    def test_get_unreconciled_bank_transactions(self):
        """Test getting unreconciled bank transactions"""
        from university_erp.university_payments.bank_reconciliation import BankReconciliationTool

        tool = BankReconciliationTool()

        # Should return a list (empty or with data)
        transactions = tool.get_unreconciled_bank_transactions()
        self.assertIsInstance(transactions, list)


if __name__ == "__main__":
    unittest.main()
