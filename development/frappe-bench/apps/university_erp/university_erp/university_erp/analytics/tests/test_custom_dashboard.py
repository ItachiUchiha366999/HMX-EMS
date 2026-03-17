# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest


class TestCustomDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test dashboard
        if not frappe.db.exists("Custom Dashboard", "Test Dashboard"):
            cls.test_dashboard = frappe.get_doc({
                "doctype": "Custom Dashboard",
                "dashboard_name": "Test Dashboard",
                "dashboard_type": "Academic",
                "description": "Test dashboard for unit testing",
                "is_public": 1,
                "is_active": 1,
                "layout_type": "Grid",
                "columns": 3,
                "refresh_interval": "5 minutes",
                "enable_date_filter": 1,
                "default_date_range": "This Month"
            })
            cls.test_dashboard.insert(ignore_permissions=True)
        else:
            cls.test_dashboard = frappe.get_doc("Custom Dashboard", "Test Dashboard")

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if frappe.db.exists("Custom Dashboard", "Test Dashboard"):
            frappe.delete_doc("Custom Dashboard", "Test Dashboard", force=True)
        frappe.db.commit()

    def test_dashboard_creation(self):
        """Test dashboard creation"""
        self.assertTrue(frappe.db.exists("Custom Dashboard", "Test Dashboard"))
        self.assertEqual(self.test_dashboard.dashboard_type, "Academic")
        self.assertEqual(self.test_dashboard.columns, 3)

    def test_dashboard_public_access(self):
        """Test public dashboard access"""
        self.assertTrue(self.test_dashboard.has_access())

    def test_column_validation(self):
        """Test column validation"""
        dashboard = frappe.get_doc({
            "doctype": "Custom Dashboard",
            "dashboard_name": "Test Invalid Columns",
            "dashboard_type": "Custom",
            "columns": 15  # Invalid - max is 12
        })

        with self.assertRaises(frappe.ValidationError):
            dashboard.insert()

    def test_dashboard_with_widgets(self):
        """Test dashboard with widgets"""
        if frappe.db.exists("Custom Dashboard", "Test Widget Dashboard"):
            frappe.delete_doc("Custom Dashboard", "Test Widget Dashboard", force=True)

        dashboard = frappe.get_doc({
            "doctype": "Custom Dashboard",
            "dashboard_name": "Test Widget Dashboard",
            "dashboard_type": "Custom",
            "is_active": 1,
            "columns": 3,
            "widgets": [
                {
                    "widget_title": "Test Widget",
                    "widget_type": "Number Card",
                    "data_source": "Static",
                    "position_row": 1,
                    "position_col": 1,
                    "width": 1,
                    "height": 1
                }
            ]
        })
        dashboard.insert(ignore_permissions=True)

        self.assertEqual(len(dashboard.widgets), 1)
        self.assertEqual(dashboard.widgets[0].widget_title, "Test Widget")

        # Clean up
        dashboard.delete()

    def test_view_count_increment(self):
        """Test view count increment"""
        initial_count = self.test_dashboard.view_count or 0
        self.test_dashboard.increment_view_count()

        # Reload to get updated value
        self.test_dashboard.reload()
        self.assertEqual(self.test_dashboard.view_count, initial_count + 1)


class TestScheduledReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Check if a standard report exists to use
        cls.report_name = "General Ledger"
        if not frappe.db.exists("Report", cls.report_name):
            cls.report_name = None

    def test_scheduled_report_creation(self):
        """Test scheduled report creation"""
        if not self.report_name:
            self.skipTest("No standard report available for testing")

        if frappe.db.exists("Scheduled Report", "Test Scheduled Report"):
            frappe.delete_doc("Scheduled Report", "Test Scheduled Report", force=True)

        scheduled_report = frappe.get_doc({
            "doctype": "Scheduled Report",
            "report_name": "Test Scheduled Report",
            "report": self.report_name,
            "is_enabled": 1,
            "frequency": "Monthly",
            "day_of_month": 1,
            "time_of_day": "08:00",
            "output_format": "PDF",
            "delivery_method": "Email",
            "recipients": [
                {"email": "test@example.com"}
            ]
        })
        scheduled_report.insert(ignore_permissions=True)

        self.assertIsNotNone(scheduled_report.next_run)

        # Clean up
        scheduled_report.delete()

    def test_scheduled_report_validation(self):
        """Test scheduled report validation"""
        if not self.report_name:
            self.skipTest("No standard report available for testing")

        # Missing day_of_month for monthly report
        scheduled_report = frappe.get_doc({
            "doctype": "Scheduled Report",
            "report_name": "Test Invalid Report",
            "report": self.report_name,
            "frequency": "Monthly",
            "time_of_day": "08:00",
            # day_of_month missing
        })

        with self.assertRaises(frappe.ValidationError):
            scheduled_report.insert()

    def test_email_delivery_requires_recipients(self):
        """Test email delivery requires recipients"""
        if not self.report_name:
            self.skipTest("No standard report available for testing")

        scheduled_report = frappe.get_doc({
            "doctype": "Scheduled Report",
            "report_name": "Test No Recipients",
            "report": self.report_name,
            "frequency": "Daily",
            "time_of_day": "08:00",
            "delivery_method": "Email",
            # recipients missing
        })

        with self.assertRaises(frappe.ValidationError):
            scheduled_report.insert()


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCustomDashboard))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestScheduledReport))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
