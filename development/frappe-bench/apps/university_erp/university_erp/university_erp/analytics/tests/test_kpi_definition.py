# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import flt


class TestKPIDefinition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test KPI Definition
        if not frappe.db.exists("KPI Definition", "Test Pass Rate"):
            cls.test_kpi = frappe.get_doc({
                "doctype": "KPI Definition",
                "kpi_name": "Test Pass Rate",
                "category": "Academic",
                "description": "Test KPI for unit testing",
                "unit": "%",
                "calculation_method": "Manual Entry",
                "target_value": 80,
                "minimum_acceptable": 60,
                "stretch_target": 90,
                "red_threshold": 60,
                "yellow_threshold": 70,
                "green_threshold": 80,
                "higher_is_better": 1,
                "tracking_frequency": "Monthly",
                "is_active": 1
            })
            cls.test_kpi.insert(ignore_permissions=True)
        else:
            cls.test_kpi = frappe.get_doc("KPI Definition", "Test Pass Rate")

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        # Delete test KPI values first
        frappe.db.delete("KPI Value", {"kpi": "Test Pass Rate"})
        # Delete test KPI definition
        if frappe.db.exists("KPI Definition", "Test Pass Rate"):
            frappe.delete_doc("KPI Definition", "Test Pass Rate", force=True)
        frappe.db.commit()

    def test_kpi_creation(self):
        """Test KPI Definition creation"""
        self.assertTrue(frappe.db.exists("KPI Definition", "Test Pass Rate"))
        self.assertEqual(self.test_kpi.category, "Academic")
        self.assertEqual(self.test_kpi.target_value, 80)

    def test_kpi_code_generation(self):
        """Test automatic KPI code generation"""
        self.assertIsNotNone(self.test_kpi.kpi_code)
        self.assertTrue(self.test_kpi.kpi_code.startswith("ACA"))

    def test_get_status_green(self):
        """Test status calculation for green threshold"""
        status = self.test_kpi.get_status(85)
        self.assertEqual(status, "Green")

    def test_get_status_yellow(self):
        """Test status calculation for yellow threshold"""
        status = self.test_kpi.get_status(75)
        self.assertEqual(status, "Yellow")

    def test_get_status_red(self):
        """Test status calculation for red threshold"""
        status = self.test_kpi.get_status(55)
        self.assertEqual(status, "Red")

    def test_get_variance_positive(self):
        """Test variance calculation for above target"""
        variance = self.test_kpi.get_variance(88)
        self.assertEqual(variance, 10)  # 10% above target

    def test_get_variance_negative(self):
        """Test variance calculation for below target"""
        variance = self.test_kpi.get_variance(72)
        self.assertEqual(variance, -10)  # 10% below target

    def test_threshold_validation_higher_is_better(self):
        """Test threshold validation for higher_is_better KPIs"""
        # Create a KPI with invalid thresholds
        kpi = frappe.get_doc({
            "doctype": "KPI Definition",
            "kpi_name": "Test Invalid Thresholds",
            "category": "Academic",
            "calculation_method": "Manual Entry",
            "higher_is_better": 1,
            "red_threshold": 80,  # Higher than yellow - invalid
            "yellow_threshold": 70,
            "green_threshold": 60  # Lower than yellow - invalid
        })

        with self.assertRaises(frappe.ValidationError):
            kpi.insert()

    def test_calculation_method_validation(self):
        """Test calculation method validation"""
        kpi = frappe.get_doc({
            "doctype": "KPI Definition",
            "kpi_name": "Test SQL KPI",
            "category": "Academic",
            "calculation_method": "SQL Query",
            # Missing sql_query - should fail validation
        })

        with self.assertRaises(frappe.ValidationError):
            kpi.insert()


class TestKPIValue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test KPI Definition
        if not frappe.db.exists("KPI Definition", "Test Value KPI"):
            cls.test_kpi = frappe.get_doc({
                "doctype": "KPI Definition",
                "kpi_name": "Test Value KPI",
                "category": "Financial",
                "calculation_method": "Manual Entry",
                "target_value": 100,
                "red_threshold": 70,
                "yellow_threshold": 85,
                "green_threshold": 95,
                "higher_is_better": 1,
                "tracking_frequency": "Monthly",
                "is_active": 1
            })
            cls.test_kpi.insert(ignore_permissions=True)
        else:
            cls.test_kpi = frappe.get_doc("KPI Definition", "Test Value KPI")

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        frappe.db.delete("KPI Value", {"kpi": "Test Value KPI"})
        if frappe.db.exists("KPI Definition", "Test Value KPI"):
            frappe.delete_doc("KPI Definition", "Test Value KPI", force=True)
        frappe.db.commit()

    def test_kpi_value_creation(self):
        """Test KPI Value creation"""
        from frappe.utils import today, add_days, get_first_day, get_last_day

        today_date = frappe.utils.getdate(today())

        kpi_value = frappe.get_doc({
            "doctype": "KPI Value",
            "kpi": "Test Value KPI",
            "period_type": "Monthly",
            "period_start": get_first_day(today_date),
            "period_end": get_last_day(today_date),
            "value": 92
        })
        kpi_value.insert(ignore_permissions=True)

        self.assertIsNotNone(kpi_value.name)
        self.assertEqual(kpi_value.value, 92)
        self.assertEqual(kpi_value.status, "Yellow")  # 92 is between 85 and 95

        # Clean up
        kpi_value.delete()

    def test_kpi_value_variance_calculation(self):
        """Test automatic variance calculation"""
        from frappe.utils import today, get_first_day, get_last_day

        today_date = frappe.utils.getdate(today())

        kpi_value = frappe.get_doc({
            "doctype": "KPI Value",
            "kpi": "Test Value KPI",
            "period_type": "Monthly",
            "period_start": get_first_day(today_date),
            "period_end": get_last_day(today_date),
            "value": 110
        })
        kpi_value.insert(ignore_permissions=True)

        self.assertEqual(kpi_value.variance, 10)  # 10% above target
        self.assertEqual(kpi_value.status, "Green")

        # Clean up
        kpi_value.delete()

    def test_kpi_value_date_validation(self):
        """Test period date validation"""
        from frappe.utils import today, add_days

        today_date = frappe.utils.getdate(today())

        kpi_value = frappe.get_doc({
            "doctype": "KPI Value",
            "kpi": "Test Value KPI",
            "period_type": "Monthly",
            "period_start": add_days(today_date, 10),  # Start after end - invalid
            "period_end": today_date,
            "value": 90
        })

        with self.assertRaises(frappe.ValidationError):
            kpi_value.insert()


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestKPIDefinition))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestKPIValue))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
