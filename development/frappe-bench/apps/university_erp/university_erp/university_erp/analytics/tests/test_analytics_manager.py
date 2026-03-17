# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import today, add_days, get_first_day, get_last_day, getdate


class TestAnalyticsManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test KPI for analytics testing
        if not frappe.db.exists("KPI Definition", "Test Analytics KPI"):
            cls.test_kpi = frappe.get_doc({
                "doctype": "KPI Definition",
                "kpi_name": "Test Analytics KPI",
                "category": "Academic",
                "calculation_method": "Manual Entry",
                "target_value": 100,
                "red_threshold": 60,
                "yellow_threshold": 80,
                "green_threshold": 90,
                "higher_is_better": 1,
                "tracking_frequency": "Monthly",
                "is_active": 1
            })
            cls.test_kpi.insert(ignore_permissions=True)
        else:
            cls.test_kpi = frappe.get_doc("KPI Definition", "Test Analytics KPI")

        # Create some test KPI values
        today_date = getdate(today())
        for i in range(3):
            month_date = frappe.utils.add_months(today_date, -i)
            month_start = get_first_day(month_date)
            month_end = get_last_day(month_date)

            if not frappe.db.exists("KPI Value", {
                "kpi": "Test Analytics KPI",
                "period_start": month_start
            }):
                kpi_value = frappe.get_doc({
                    "doctype": "KPI Value",
                    "kpi": "Test Analytics KPI",
                    "period_type": "Monthly",
                    "period_start": month_start,
                    "period_end": month_end,
                    "value": 85 + (i * 5)  # 85, 90, 95
                })
                kpi_value.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        frappe.db.delete("KPI Value", {"kpi": "Test Analytics KPI"})
        if frappe.db.exists("KPI Definition", "Test Analytics KPI"):
            frappe.delete_doc("KPI Definition", "Test Analytics KPI", force=True)
        frappe.db.commit()

    def test_calculate_manual_kpi(self):
        """Test calculating manual entry KPI"""
        from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

        manager = AnalyticsManager()
        value = manager.calculate_kpi("Test Analytics KPI")

        # Should return the latest stored value
        self.assertIsNotNone(value)
        self.assertGreaterEqual(value, 85)

    def test_store_kpi_value(self):
        """Test storing KPI value"""
        from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

        manager = AnalyticsManager()
        today_date = getdate(today())

        # Use a unique period to avoid conflicts
        period_start = add_days(today_date, 1)
        period_end = add_days(today_date, 31)

        name = manager.store_kpi_value(
            kpi_name="Test Analytics KPI",
            value=92,
            period_type="Monthly",
            period_start=period_start,
            period_end=period_end
        )

        self.assertIsNotNone(name)

        # Verify the value was stored
        stored = frappe.get_doc("KPI Value", name)
        self.assertEqual(stored.value, 92)
        self.assertEqual(stored.calculation_source, "Auto Calculated")

        # Clean up
        stored.delete()

    def test_get_trend_data(self):
        """Test getting trend data"""
        from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

        manager = AnalyticsManager()
        trend = manager.get_trend_data("Test Analytics KPI", periods=3, period_type="Monthly")

        self.assertIsInstance(trend, list)
        self.assertGreaterEqual(len(trend), 1)

    def test_get_comparison_data(self):
        """Test getting comparison data"""
        from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

        manager = AnalyticsManager()
        today_date = getdate(today())

        current_period = {
            "start": get_first_day(today_date),
            "end": get_last_day(today_date)
        }

        previous_date = frappe.utils.add_months(today_date, -1)
        previous_period = {
            "start": get_first_day(previous_date),
            "end": get_last_day(previous_date)
        }

        comparison = manager.get_comparison_data(
            "Test Analytics KPI",
            current_period,
            previous_period
        )

        self.assertIn("current_value", comparison)
        self.assertIn("previous_value", comparison)
        self.assertIn("change", comparison)
        self.assertIn("change_percent", comparison)


class TestDashboardEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test dashboard
        if not frappe.db.exists("Custom Dashboard", "Test Engine Dashboard"):
            cls.test_dashboard = frappe.get_doc({
                "doctype": "Custom Dashboard",
                "dashboard_name": "Test Engine Dashboard",
                "dashboard_type": "Custom",
                "is_public": 1,
                "is_active": 1,
                "columns": 3
            })
            cls.test_dashboard.insert(ignore_permissions=True)
        else:
            cls.test_dashboard = frappe.get_doc("Custom Dashboard", "Test Engine Dashboard")

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if frappe.db.exists("Custom Dashboard", "Test Engine Dashboard"):
            frappe.delete_doc("Custom Dashboard", "Test Engine Dashboard", force=True)
        frappe.db.commit()

    def test_get_dashboard_data(self):
        """Test getting dashboard data"""
        from university_erp.university_erp.analytics.dashboard_engine import DashboardEngine

        engine = DashboardEngine()
        data = engine.get_dashboard_data("Test Engine Dashboard")

        self.assertIn("dashboard_name", data)
        self.assertIn("widgets", data)
        self.assertEqual(data["dashboard_name"], "Test Engine Dashboard")

    def test_get_available_dashboards(self):
        """Test getting available dashboards"""
        from university_erp.university_erp.analytics.dashboard_engine import DashboardEngine

        engine = DashboardEngine()
        dashboards = engine.get_available_dashboards()

        self.assertIsInstance(dashboards, list)
        # Should include our test dashboard since it's public
        dashboard_names = [d["dashboard_name"] for d in dashboards]
        self.assertIn("Test Engine Dashboard", dashboard_names)


class TestKPICalculationMethods(unittest.TestCase):
    def test_mock_academic_kpis(self):
        """Test academic KPI mock methods"""
        from university_erp.university_erp.analytics.kpis.academic_kpis import (
            student_pass_percentage,
            average_cgpa,
            student_attendance_rate,
            faculty_student_ratio,
            course_completion_rate
        )

        # These should return mock values when real data doesn't exist
        pass_rate = student_pass_percentage()
        self.assertIsInstance(pass_rate, float)
        self.assertGreaterEqual(pass_rate, 0)
        self.assertLessEqual(pass_rate, 100)

        cgpa = average_cgpa()
        self.assertIsInstance(cgpa, float)
        self.assertGreaterEqual(cgpa, 0)

        attendance = student_attendance_rate()
        self.assertIsInstance(attendance, float)

        ratio = faculty_student_ratio()
        self.assertIsInstance(ratio, float)

        completion = course_completion_rate()
        self.assertIsInstance(completion, float)

    def test_mock_financial_kpis(self):
        """Test financial KPI mock methods"""
        from university_erp.university_erp.analytics.kpis.financial_kpis import (
            fee_collection_rate,
            revenue_per_student,
            outstanding_fees_percentage,
            scholarship_utilization
        )

        collection = fee_collection_rate()
        self.assertIsInstance(collection, float)

        revenue = revenue_per_student()
        self.assertIsInstance(revenue, float)

        outstanding = outstanding_fees_percentage()
        self.assertIsInstance(outstanding, float)

        scholarship = scholarship_utilization()
        self.assertIsInstance(scholarship, float)

    def test_mock_admission_kpis(self):
        """Test admission KPI mock methods"""
        from university_erp.university_erp.analytics.kpis.admission_kpis import (
            admission_conversion_rate,
            seat_fill_rate,
            average_application_processing_time,
            application_rejection_rate
        )

        conversion = admission_conversion_rate()
        self.assertIsInstance(conversion, float)

        fill_rate = seat_fill_rate()
        self.assertIsInstance(fill_rate, float)

        processing_time = average_application_processing_time()
        self.assertIsInstance(processing_time, float)

        rejection = application_rejection_rate()
        self.assertIsInstance(rejection, float)


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsManager))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDashboardEngine))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestKPICalculationMethods))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
