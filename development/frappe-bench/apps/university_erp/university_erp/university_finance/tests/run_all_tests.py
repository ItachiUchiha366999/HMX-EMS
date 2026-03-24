"""Run all University Finance tests.

Usage: bench --site university.local execute university_erp.university_finance.tests.run_all_tests.run
"""
import unittest
import sys


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Import all test modules
    from university_erp.university_finance.tests import test_module_registration
    from university_erp.university_finance.tests import test_import_integrity
    from university_erp.university_finance.tests import test_gl_posting
    from university_erp.university_finance.tests import test_fee_flow

    suite.addTests(loader.loadTestsFromModule(test_module_registration))
    suite.addTests(loader.loadTestsFromModule(test_import_integrity))
    suite.addTests(loader.loadTestsFromModule(test_gl_posting))
    suite.addTests(loader.loadTestsFromModule(test_fee_flow))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        sys.exit(1)
