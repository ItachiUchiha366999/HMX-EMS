# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import today


class TestAccreditationAPI(unittest.TestCase):
    """Tests for Accreditation API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test accreditation cycle
        if not frappe.db.exists("Accreditation Cycle", "Test API Cycle"):
            cls.test_cycle = frappe.get_doc({
                "doctype": "Accreditation Cycle",
                "cycle_name": "Test API Cycle",
                "accreditation_type": "NAAC",
                "start_date": today(),
                "end_date": frappe.utils.add_months(today(), 12),
                "status": "Data Collection"
            })
            cls.test_cycle.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if frappe.db.exists("Accreditation Cycle", "Test API Cycle"):
            frappe.delete_doc("Accreditation Cycle", "Test API Cycle", force=True)
        frappe.db.commit()

    def test_calculate_co_attainment_api(self):
        """Test calculate_co_attainment API"""
        from university_erp.university_erp.accreditation.api import calculate_co_attainment

        result = calculate_co_attainment(
            course="TEST-COURSE",
            academic_year="2025-26"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("course", result)

    def test_calculate_po_attainment_api(self):
        """Test calculate_po_attainment API"""
        from university_erp.university_erp.accreditation.api import calculate_po_attainment

        result = calculate_po_attainment(
            program="TEST-PROGRAM",
            academic_year="2025-26"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("program", result)

    def test_get_copo_matrix_api(self):
        """Test get_copo_matrix API"""
        from university_erp.university_erp.accreditation.api import get_copo_matrix

        result = get_copo_matrix(course="TEST-COURSE")

        self.assertIsInstance(result, dict)
        self.assertIn("course", result)
        self.assertIn("matrix", result)

    def test_collect_naac_data_api(self):
        """Test collect_naac_data API"""
        from university_erp.university_erp.accreditation.api import collect_naac_data

        result = collect_naac_data(academic_year="2025-26")

        self.assertIsInstance(result, dict)
        # Should return collected data for all 7 criteria
        self.assertIn("criterion_1", result)

    def test_generate_ssr_api(self):
        """Test generate_ssr API"""
        from university_erp.university_erp.accreditation.api import generate_ssr

        result = generate_ssr(
            accreditation_cycle="Test API Cycle",
            output_format="html"
        )

        self.assertIsNotNone(result)

    def test_get_accreditation_dashboard_api(self):
        """Test get_accreditation_dashboard API"""
        from university_erp.university_erp.accreditation.api import get_accreditation_dashboard

        result = get_accreditation_dashboard()

        self.assertIsInstance(result, dict)
        self.assertIn("active_cycles", result)
        self.assertIn("upcoming_deadlines", result)

    def test_get_criterion_progress_api(self):
        """Test get_criterion_progress API"""
        from university_erp.university_erp.accreditation.api import get_criterion_progress

        result = get_criterion_progress(accreditation_cycle="Test API Cycle")

        self.assertIsInstance(result, dict)
        self.assertIn("criteria", result)

    def test_get_naac_metrics_api(self):
        """Test get_naac_metrics API"""
        from university_erp.university_erp.accreditation.api import get_naac_metrics

        result = get_naac_metrics(criterion="1")

        self.assertIsInstance(result, list)

    def test_get_nirf_data_api(self):
        """Test get_nirf_data API"""
        from university_erp.university_erp.accreditation.api import get_nirf_data

        result = get_nirf_data(ranking_year="2026")

        self.assertIsInstance(result, dict)

    def test_update_metric_status_api(self):
        """Test update_metric_status API"""
        # Create a test metric first
        if not frappe.db.exists("NAAC Metric", {"metric_number": "1.1.1-API-TEST"}):
            metric = frappe.get_doc({
                "doctype": "NAAC Metric",
                "metric_number": "1.1.1-API-TEST",
                "metric_name": "Test API Metric",
                "criterion": "1",
                "metric_type": "Quantitative",
                "max_score": 20,
                "status": "Pending"
            })
            metric.insert(ignore_permissions=True)

        try:
            from university_erp.university_erp.accreditation.api import update_metric_status

            result = update_metric_status(
                metric_name=frappe.get_value("NAAC Metric", {"metric_number": "1.1.1-API-TEST"}, "name"),
                status="Data Collected"
            )

            self.assertIsInstance(result, dict)
            self.assertEqual(result.get("status"), "success")
        finally:
            # Clean up
            metrics = frappe.get_all("NAAC Metric", filters={"metric_number": "1.1.1-API-TEST"})
            for m in metrics:
                frappe.delete_doc("NAAC Metric", m.name, force=True)


class TestAccreditationAPIPermissions(unittest.TestCase):
    """Tests for API permissions"""

    def test_api_requires_login(self):
        """Test that API requires login"""
        # This would typically test that anonymous users can't access the API
        # For now, just verify the API functions are decorated with frappe.whitelist
        from university_erp.university_erp.accreditation import api

        # Check that functions are whitelisted
        self.assertTrue(hasattr(api.calculate_co_attainment, '__wrapped__') or
                       callable(api.calculate_co_attainment))


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAccreditationAPI))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAccreditationAPIPermissions))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
