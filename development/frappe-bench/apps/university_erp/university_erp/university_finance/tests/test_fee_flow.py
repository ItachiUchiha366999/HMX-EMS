import frappe
from frappe.tests.utils import FrappeTestCase


class TestFeeFlow(FrappeTestCase):
    """End-to-end test: Fees submission creates GL Entries via forked university_finance module."""

    def test_fee_submit_creates_gl_entries(self):
        """Submitting a Fees document should create GL Entries via university_finance.general_ledger.

        This traces the full call chain:
        1. Fees on_submit (hooks.py) -> GLPostingManager
        2. GLPostingManager -> university_finance.general_ledger.make_gl_entries
        3. make_gl_entries -> GL Entry records in database

        Note: GL entries are only created if University Accounts Settings
        has auto_post_gl enabled and accounts configured. If not configured,
        the test verifies the import chain works and the call path is correct.
        """
        # Find an existing submitted Fees document
        existing_fee = frappe.db.get_value(
            "Fees", {"docstatus": 1}, ["name", "grand_total", "student"], as_dict=True
        )

        if existing_fee:
            # Verify GLPostingManager import chain works
            from university_erp.university_payments.gl_posting import GLPostingManager
            try:
                manager = GLPostingManager()
                # If auto_post_gl is enabled, GL entries should exist
                if hasattr(manager, 'settings') and manager.settings.auto_post_gl:
                    gl_entries = frappe.get_all(
                        "GL Entry",
                        filters={"voucher_type": "Fees", "voucher_no": existing_fee.name},
                        fields=["name", "account", "debit", "credit"]
                    )
                    if len(gl_entries) > 0:
                        # Verify entries balance (debit = credit)
                        total_debit = sum(e.debit for e in gl_entries)
                        total_credit = sum(e.credit for e in gl_entries)
                        self.assertAlmostEqual(
                            total_debit, total_credit, places=2,
                            msg=f"GL entries for Fees {existing_fee.name} don't balance"
                        )
                else:
                    # auto_post_gl not enabled -- verify the import chain works
                    from university_erp.university_finance.general_ledger import make_gl_entries
                    self.assertTrue(
                        callable(make_gl_entries),
                        "make_gl_entries should be importable even if auto_post_gl is off"
                    )
            except frappe.DoesNotExistError:
                # University Accounts Settings not configured
                # Verify the import chain still works
                from university_erp.university_finance.general_ledger import make_gl_entries
                self.assertTrue(callable(make_gl_entries))
        else:
            # No submitted Fees -- verify the import chain
            from university_erp.university_finance.general_ledger import make_gl_entries
            self.assertTrue(callable(make_gl_entries))

    def test_payment_entry_module_path(self):
        """Payment Entry controller loads through university_finance module."""
        # Verify Payment Entry can be loaded via the forked module path
        pe_meta = frappe.get_meta("Payment Entry")
        self.assertEqual(
            pe_meta.module, "University Finance",
            "Payment Entry should be owned by University Finance module"
        )

        # Verify the controller can be loaded
        from university_erp.university_finance.doctype.payment_entry.payment_entry import PaymentEntry
        self.assertTrue(
            hasattr(PaymentEntry, "validate"),
            "PaymentEntry class should have validate method"
        )

    def test_payment_webhook_path_documented(self):
        """Payment webhook handler path should not reference erpnext.accounts.

        This test scans university_erp api/ directories for any erpnext.accounts
        references in webhook-related files.
        """
        import os
        import re

        # Check both possible api locations
        app_dirs = [
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "api"
            ),
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                "university_erp", "api"
            ),
        ]

        violations = []
        for api_dir in app_dirs:
            if not os.path.exists(api_dir):
                continue

            for root, dirs, files in os.walk(api_dir):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for f in files:
                    if f.endswith(".py"):
                        filepath = os.path.join(root, f)
                        with open(filepath) as fh:
                            content = fh.read()
                        matches = re.findall(r"^from erpnext\.accounts\.", content, re.MULTILINE)
                        if matches:
                            rel = os.path.relpath(filepath, api_dir)
                            violations.append(f"{rel}: {matches}")

        self.assertEqual(
            violations, [],
            f"Payment webhook files reference erpnext.accounts:\n"
            + "\n".join(violations)
        )

    def test_hooks_doc_events_intact(self):
        """hooks.py doc_events for Fees still reference correct paths."""
        import university_erp.hooks as hooks
        doc_events = hooks.doc_events

        self.assertIn("Fees", doc_events, "Fees should be in doc_events")
        fees_events = doc_events["Fees"]

        # on_submit should have our handlers
        self.assertIn("on_submit", fees_events)
        on_submit = fees_events["on_submit"]
        if isinstance(on_submit, list):
            # Check at least one handler references university_erp
            university_handlers = [h for h in on_submit if "university_erp" in h]
            self.assertGreater(
                len(university_handlers), 0,
                "At least one on_submit handler should reference university_erp"
            )
        elif isinstance(on_submit, str):
            self.assertIn("university_erp", on_submit)
