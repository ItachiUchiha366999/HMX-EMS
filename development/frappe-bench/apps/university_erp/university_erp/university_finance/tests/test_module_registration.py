import frappe
from frappe.tests.utils import FrappeTestCase


class TestModuleRegistration(FrappeTestCase):
    """Smoke tests for University Finance module registration."""

    def test_module_def_exists(self):
        """Module Def record exists for University Finance."""
        self.assertTrue(
            frappe.db.exists("Module Def", "University Finance"),
            "Module Def 'University Finance' not found in database"
        )

    def test_gl_entry_owned_by_university_finance(self):
        """GL Entry doctype is owned by University Finance module."""
        module = frappe.db.get_value("DocType", "GL Entry", "module")
        self.assertEqual(module, "University Finance")

    def test_payment_entry_owned_by_university_finance(self):
        """Payment Entry doctype is owned by University Finance module."""
        module = frappe.db.get_value("DocType", "Payment Entry", "module")
        self.assertEqual(module, "University Finance")

    def test_journal_entry_owned_by_university_finance(self):
        """Journal Entry doctype is owned by University Finance module."""
        module = frappe.db.get_value("DocType", "Journal Entry", "module")
        self.assertEqual(module, "University Finance")

    def test_account_owned_by_university_finance(self):
        """Account doctype is owned by University Finance module."""
        module = frappe.db.get_value("DocType", "Account", "module")
        self.assertEqual(module, "University Finance")

    def test_general_ledger_import(self):
        """general_ledger.py can be imported from university_finance."""
        from university_erp.university_finance.general_ledger import make_gl_entries
        self.assertTrue(callable(make_gl_entries))

    def test_utils_import(self):
        """utils.py can be imported from university_finance."""
        from university_erp.university_finance.utils import get_fiscal_year
        self.assertTrue(callable(get_fiscal_year))

    def test_compat_shim_import(self):
        """_erpnext_compat.py can be imported and provides expected functions."""
        from university_erp.university_finance._erpnext_compat import (
            get_default_company, get_company_currency, get_default_cost_center
        )
        self.assertTrue(callable(get_default_company))
        self.assertTrue(callable(get_company_currency))
        self.assertTrue(callable(get_default_cost_center))

    def test_gl_entry_data_preserved(self):
        """Existing GL Entry data is still accessible after fork."""
        count = frappe.db.count("GL Entry")
        # Just verify the table is accessible, count >= 0
        self.assertGreaterEqual(count, 0)
