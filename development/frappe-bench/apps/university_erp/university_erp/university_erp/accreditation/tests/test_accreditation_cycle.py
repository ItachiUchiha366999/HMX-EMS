# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import today, add_days, add_months, getdate


class TestAccreditationCycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test accreditation cycle
        if not frappe.db.exists("Accreditation Cycle", "Test NAAC Cycle 2026"):
            cls.test_cycle = frappe.get_doc({
                "doctype": "Accreditation Cycle",
                "cycle_name": "Test NAAC Cycle 2026",
                "accreditation_type": "NAAC",
                "cycle_number": 1,
                "start_date": today(),
                "end_date": add_months(today(), 12),
                "status": "Preparation",
                "accreditation_level": "Institutional",
                "scope": "Full Institution"
            })
            cls.test_cycle.insert(ignore_permissions=True)
        else:
            cls.test_cycle = frappe.get_doc("Accreditation Cycle", "Test NAAC Cycle 2026")

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if frappe.db.exists("Accreditation Cycle", "Test NAAC Cycle 2026"):
            frappe.delete_doc("Accreditation Cycle", "Test NAAC Cycle 2026", force=True)
        frappe.db.commit()

    def test_accreditation_cycle_creation(self):
        """Test accreditation cycle creation"""
        self.assertTrue(frappe.db.exists("Accreditation Cycle", "Test NAAC Cycle 2026"))
        self.assertEqual(self.test_cycle.accreditation_type, "NAAC")
        self.assertEqual(self.test_cycle.status, "Preparation")

    def test_date_validation(self):
        """Test that end date must be after start date"""
        cycle = frappe.get_doc({
            "doctype": "Accreditation Cycle",
            "cycle_name": "Test Invalid Dates",
            "accreditation_type": "NAAC",
            "start_date": today(),
            "end_date": add_days(today(), -10),  # End date before start
            "status": "Preparation"
        })

        with self.assertRaises(frappe.ValidationError):
            cycle.insert()

    def test_setup_naac_criteria(self):
        """Test NAAC criteria setup"""
        # Create a new cycle to test criteria setup
        if frappe.db.exists("Accreditation Cycle", "Test Criteria Setup"):
            frappe.delete_doc("Accreditation Cycle", "Test Criteria Setup", force=True)

        cycle = frappe.get_doc({
            "doctype": "Accreditation Cycle",
            "cycle_name": "Test Criteria Setup",
            "accreditation_type": "NAAC",
            "start_date": today(),
            "end_date": add_months(today(), 12),
            "status": "Preparation"
        })
        cycle.insert(ignore_permissions=True)
        cycle.setup_naac_criteria()
        cycle.reload()

        # Should have 7 NAAC criteria
        self.assertEqual(len(cycle.criteria), 7)

        # Verify first criterion is Curricular Aspects
        criterion_names = [c.criterion_name for c in cycle.criteria]
        self.assertIn("Curricular Aspects", criterion_names)
        self.assertIn("Teaching-Learning and Evaluation", criterion_names)

        # Clean up
        frappe.delete_doc("Accreditation Cycle", "Test Criteria Setup", force=True)

    def test_progress_calculation(self):
        """Test progress calculation"""
        # Create cycle with criteria
        if frappe.db.exists("Accreditation Cycle", "Test Progress Calc"):
            frappe.delete_doc("Accreditation Cycle", "Test Progress Calc", force=True)

        cycle = frappe.get_doc({
            "doctype": "Accreditation Cycle",
            "cycle_name": "Test Progress Calc",
            "accreditation_type": "NAAC",
            "start_date": today(),
            "end_date": add_months(today(), 12),
            "status": "Preparation",
            "criteria": [
                {
                    "criterion_number": "1",
                    "criterion_name": "Curricular Aspects",
                    "weightage": 100,
                    "max_score": 100,
                    "status": "Completed",
                    "completion_percentage": 100
                },
                {
                    "criterion_number": "2",
                    "criterion_name": "Teaching-Learning",
                    "weightage": 100,
                    "max_score": 100,
                    "status": "In Progress",
                    "completion_percentage": 50
                }
            ]
        })
        cycle.insert(ignore_permissions=True)

        # Progress should be calculated
        self.assertIsNotNone(cycle.overall_progress)
        self.assertGreater(cycle.overall_progress, 0)

        # Clean up
        frappe.delete_doc("Accreditation Cycle", "Test Progress Calc", force=True)

    def test_status_transitions(self):
        """Test valid status transitions"""
        if frappe.db.exists("Accreditation Cycle", "Test Status Trans"):
            frappe.delete_doc("Accreditation Cycle", "Test Status Trans", force=True)

        cycle = frappe.get_doc({
            "doctype": "Accreditation Cycle",
            "cycle_name": "Test Status Trans",
            "accreditation_type": "NAAC",
            "start_date": today(),
            "end_date": add_months(today(), 12),
            "status": "Preparation"
        })
        cycle.insert(ignore_permissions=True)

        # Test valid transition
        cycle.status = "Data Collection"
        cycle.save()
        self.assertEqual(cycle.status, "Data Collection")

        # Clean up
        frappe.delete_doc("Accreditation Cycle", "Test Status Trans", force=True)

    def test_criterion_summary(self):
        """Test criterion summary method"""
        if frappe.db.exists("Accreditation Cycle", "Test Criterion Summary"):
            frappe.delete_doc("Accreditation Cycle", "Test Criterion Summary", force=True)

        cycle = frappe.get_doc({
            "doctype": "Accreditation Cycle",
            "cycle_name": "Test Criterion Summary",
            "accreditation_type": "NAAC",
            "start_date": today(),
            "end_date": add_months(today(), 12),
            "status": "Preparation"
        })
        cycle.insert(ignore_permissions=True)
        cycle.setup_naac_criteria()
        cycle.reload()

        summary = cycle.get_criterion_summary()

        self.assertIn("criteria", summary)
        self.assertIn("total_weightage", summary)
        self.assertIn("total_score", summary)
        self.assertEqual(len(summary["criteria"]), 7)

        # Clean up
        frappe.delete_doc("Accreditation Cycle", "Test Criterion Summary", force=True)


class TestNAACMetric(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test NAAC metric
        if not frappe.db.exists("NAAC Metric", {"metric_number": "1.1.1-TEST"}):
            cls.test_metric = frappe.get_doc({
                "doctype": "NAAC Metric",
                "metric_number": "1.1.1-TEST",
                "metric_name": "Test Metric - Curricula Implementation",
                "criterion": "1",
                "description": "Test metric for curriculum implementation",
                "metric_type": "Quantitative",
                "max_score": 20,
                "weightage": 20,
                "data_source": "Manual Entry",
                "year_data": [
                    {"year": "2023-24", "value": 85},
                    {"year": "2024-25", "value": 90}
                ]
            })
            cls.test_metric.insert(ignore_permissions=True)
        else:
            cls.test_metric = frappe.get_doc("NAAC Metric", {"metric_number": "1.1.1-TEST"})

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        metrics = frappe.get_all("NAAC Metric", filters={"metric_number": ["like", "%TEST%"]})
        for m in metrics:
            frappe.delete_doc("NAAC Metric", m.name, force=True)
        frappe.db.commit()

    def test_metric_creation(self):
        """Test NAAC metric creation"""
        self.assertIsNotNone(self.test_metric.name)
        self.assertEqual(self.test_metric.criterion, "1")
        self.assertEqual(self.test_metric.metric_type, "Quantitative")

    def test_metric_number_validation(self):
        """Test metric number format validation"""
        # Valid formats: 1.1.1, 2.3.4, etc.
        metric = frappe.get_doc({
            "doctype": "NAAC Metric",
            "metric_number": "INVALID",  # Invalid format
            "metric_name": "Invalid Metric",
            "criterion": "1",
            "metric_type": "Quantitative",
            "max_score": 20
        })

        with self.assertRaises(frappe.ValidationError):
            metric.insert()

    def test_value_calculation(self):
        """Test value calculation from year data"""
        # Reload to get calculated value
        self.test_metric.reload()

        # Value should be calculated from year_data
        if self.test_metric.year_data:
            self.assertIsNotNone(self.test_metric.calculated_value)

    def test_status_update(self):
        """Test metric status update"""
        if frappe.db.exists("NAAC Metric", {"metric_number": "1.1.2-TEST"}):
            frappe.delete_doc("NAAC Metric", {"metric_number": "1.1.2-TEST"}, force=True)

        metric = frappe.get_doc({
            "doctype": "NAAC Metric",
            "metric_number": "1.1.2-TEST",
            "metric_name": "Test Status Update",
            "criterion": "1",
            "metric_type": "Quantitative",
            "max_score": 20,
            "status": "Pending"
        })
        metric.insert(ignore_permissions=True)

        # Update status
        metric.update_status("Data Collected")
        metric.reload()
        self.assertEqual(metric.status, "Data Collected")

        # Clean up
        frappe.delete_doc("NAAC Metric", metric.name, force=True)

    def test_document_attachment(self):
        """Test document attachment to metric"""
        if frappe.db.exists("NAAC Metric", {"metric_number": "1.1.3-TEST"}):
            frappe.delete_doc("NAAC Metric", {"metric_number": "1.1.3-TEST"}, force=True)

        metric = frappe.get_doc({
            "doctype": "NAAC Metric",
            "metric_number": "1.1.3-TEST",
            "metric_name": "Test Document Attachment",
            "criterion": "1",
            "metric_type": "Quantitative",
            "max_score": 20,
            "documents": [
                {
                    "document_name": "Test Document",
                    "document_type": "PDF",
                    "description": "Test supporting document"
                }
            ]
        })
        metric.insert(ignore_permissions=True)

        self.assertEqual(len(metric.documents), 1)
        self.assertEqual(metric.documents[0].document_name, "Test Document")

        # Clean up
        frappe.delete_doc("NAAC Metric", metric.name, force=True)


class TestNIRFData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test NIRF data
        if not frappe.db.exists("NIRF Data", {"ranking_year": "2026-TEST"}):
            cls.test_nirf = frappe.get_doc({
                "doctype": "NIRF Data",
                "ranking_year": "2026-TEST",
                "category": "University",
                "status": "Draft",
                # TLR Parameters
                "ss_student_strength": 5000,
                "fsr_faculty_ratio": 1.0,
                "fqe_faculty_qualification": 85,
                "fru_financial_resources": 150,
                # RP Parameters
                "pu_publications": 500,
                "qp_quality_publications": 200,
                "ipr_patents": 20,
                "fppp_projects": 50,
                # GO Parameters
                "gue_university_exams": 90,
                "gphd_phd_students": 150,
                "gms_median_salary": 800000,
                # OI Parameters
                "rd_region_diversity": 30,
                "wd_women_diversity": 45,
                "escs_economically_backward": 25,
                "pcs_facilities_disabled": 80,
                # PR Parameters
                "pr_peer_perception": 75
            })
            cls.test_nirf.insert(ignore_permissions=True)
        else:
            cls.test_nirf = frappe.get_doc("NIRF Data", {"ranking_year": "2026-TEST"})

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        nirf_records = frappe.get_all("NIRF Data", filters={"ranking_year": ["like", "%TEST%"]})
        for n in nirf_records:
            frappe.delete_doc("NIRF Data", n.name, force=True)
        frappe.db.commit()

    def test_nirf_data_creation(self):
        """Test NIRF data creation"""
        self.assertIsNotNone(self.test_nirf.name)
        self.assertEqual(self.test_nirf.category, "University")

    def test_score_calculation(self):
        """Test NIRF score calculation"""
        self.test_nirf.reload()

        # TLR score should be calculated (max 30)
        self.assertIsNotNone(self.test_nirf.tlr_score)
        self.assertLessEqual(self.test_nirf.tlr_score, 30)

        # RP score should be calculated (max 30)
        self.assertIsNotNone(self.test_nirf.rp_score)
        self.assertLessEqual(self.test_nirf.rp_score, 30)

        # GO score should be calculated (max 20)
        self.assertIsNotNone(self.test_nirf.go_score)
        self.assertLessEqual(self.test_nirf.go_score, 20)

        # OI score should be calculated (max 10)
        self.assertIsNotNone(self.test_nirf.oi_score)
        self.assertLessEqual(self.test_nirf.oi_score, 10)

        # Total score should be sum of all
        self.assertIsNotNone(self.test_nirf.total_score)
        self.assertLessEqual(self.test_nirf.total_score, 100)

    def test_category_validation(self):
        """Test NIRF category validation"""
        valid_categories = ["Overall", "University", "Engineering", "Management",
                          "Pharmacy", "Medical", "Law"]

        for cat in valid_categories:
            # Should not raise error for valid categories
            nirf = frappe.get_doc({
                "doctype": "NIRF Data",
                "ranking_year": f"2026-CAT-{cat}",
                "category": cat,
                "status": "Draft"
            })
            try:
                nirf.insert(ignore_permissions=True)
                frappe.delete_doc("NIRF Data", nirf.name, force=True)
            except Exception:
                self.fail(f"Valid category {cat} raised exception")

    def test_duplicate_year_category(self):
        """Test that duplicate year-category combination is prevented"""
        # First record already exists from setUpClass
        duplicate = frappe.get_doc({
            "doctype": "NIRF Data",
            "ranking_year": "2026-TEST",  # Same as existing
            "category": "University",  # Same as existing
            "status": "Draft"
        })

        with self.assertRaises(Exception):  # Should raise duplicate error
            duplicate.insert()


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAccreditationCycle))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNAACMetric))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNIRFData))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
