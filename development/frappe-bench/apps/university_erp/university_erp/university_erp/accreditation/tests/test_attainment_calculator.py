# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import today, getdate


class TestCOPOAttainmentCalculator(unittest.TestCase):
    """Tests for CO-PO Attainment Calculator - integrates with existing university_obe module"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Check if university_obe module exists
        cls.obe_available = frappe.db.exists("DocType", "Course Outcome")

        if cls.obe_available:
            # Create test Course Outcome if not exists
            if not frappe.db.exists("Course Outcome", {"course": "TEST-COURSE", "co_number": "CO1"}):
                try:
                    cls.test_co = frappe.get_doc({
                        "doctype": "Course Outcome",
                        "course": "TEST-COURSE",
                        "co_number": "CO1",
                        "co_statement": "Understand fundamental concepts",
                        "bloom_level": "Understanding",
                        "target_attainment": 60
                    })
                    cls.test_co.insert(ignore_permissions=True)
                except Exception:
                    cls.test_co = None
            else:
                cls.test_co = frappe.get_doc("Course Outcome", {"course": "TEST-COURSE", "co_number": "CO1"})

            # Create test Program Outcome if not exists
            if not frappe.db.exists("Program Outcome", {"program": "TEST-PROGRAM", "po_number": "PO1"}):
                try:
                    cls.test_po = frappe.get_doc({
                        "doctype": "Program Outcome",
                        "program": "TEST-PROGRAM",
                        "po_number": "PO1",
                        "po_statement": "Engineering knowledge application",
                        "target_attainment": 60
                    })
                    cls.test_po.insert(ignore_permissions=True)
                except Exception:
                    cls.test_po = None
            else:
                cls.test_po = frappe.get_doc("Program Outcome", {"program": "TEST-PROGRAM", "po_number": "PO1"})

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if cls.obe_available:
            # Clean up test Course Outcomes
            cos = frappe.get_all("Course Outcome", filters={"course": "TEST-COURSE"})
            for co in cos:
                try:
                    frappe.delete_doc("Course Outcome", co.name, force=True)
                except Exception:
                    pass

            # Clean up test Program Outcomes
            pos = frappe.get_all("Program Outcome", filters={"program": "TEST-PROGRAM"})
            for po in pos:
                try:
                    frappe.delete_doc("Program Outcome", po.name, force=True)
                except Exception:
                    pass

            frappe.db.commit()

    def test_calculator_initialization(self):
        """Test calculator initialization"""
        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        self.assertIsNotNone(calculator)

    def test_direct_attainment_calculation(self):
        """Test direct attainment calculation"""
        if not self.obe_available:
            self.skipTest("university_obe module not available")

        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        result = calculator.calculate_direct_attainment(
            course="TEST-COURSE",
            academic_year="2025-26",
            semester="Odd"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("course", result)
        self.assertIn("cos", result)

    def test_indirect_attainment_calculation(self):
        """Test indirect attainment calculation"""
        if not self.obe_available:
            self.skipTest("university_obe module not available")

        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        result = calculator.calculate_indirect_attainment(
            course="TEST-COURSE",
            academic_year="2025-26"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("course", result)

    def test_overall_attainment_calculation(self):
        """Test overall attainment calculation with weights"""
        if not self.obe_available:
            self.skipTest("university_obe module not available")

        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        result = calculator.calculate_overall_attainment(
            course="TEST-COURSE",
            academic_year="2025-26",
            direct_weight=0.8,
            indirect_weight=0.2
        )

        self.assertIsInstance(result, dict)
        self.assertIn("direct_weight", result)
        self.assertIn("indirect_weight", result)
        self.assertEqual(result["direct_weight"], 0.8)
        self.assertEqual(result["indirect_weight"], 0.2)

    def test_po_attainment_calculation(self):
        """Test PO attainment calculation for a program"""
        if not self.obe_available:
            self.skipTest("university_obe module not available")

        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        result = calculator.calculate_po_attainment(
            program="TEST-PROGRAM",
            academic_year="2025-26"
        )

        self.assertIsInstance(result, dict)
        self.assertIn("program", result)
        self.assertIn("pos", result)

    def test_copo_matrix_generation(self):
        """Test CO-PO mapping matrix generation"""
        if not self.obe_available:
            self.skipTest("university_obe module not available")

        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        result = calculator.get_copo_matrix(course="TEST-COURSE")

        self.assertIsInstance(result, dict)
        self.assertIn("course", result)
        self.assertIn("matrix", result)

    def test_attainment_thresholds(self):
        """Test attainment level classification"""
        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()

        # Test different attainment levels
        level_high = calculator._get_attainment_level(75)
        level_medium = calculator._get_attainment_level(55)
        level_low = calculator._get_attainment_level(35)

        self.assertEqual(level_high, "High")
        self.assertEqual(level_medium, "Medium")
        self.assertEqual(level_low, "Low")

    def test_bloom_level_weights(self):
        """Test Bloom's taxonomy level weights"""
        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()

        # Verify Bloom's level weights
        self.assertEqual(calculator.bloom_weights.get("Remembering"), 1.0)
        self.assertEqual(calculator.bloom_weights.get("Understanding"), 1.2)
        self.assertEqual(calculator.bloom_weights.get("Applying"), 1.4)
        self.assertEqual(calculator.bloom_weights.get("Analyzing"), 1.6)
        self.assertEqual(calculator.bloom_weights.get("Evaluating"), 1.8)
        self.assertEqual(calculator.bloom_weights.get("Creating"), 2.0)


class TestAttainmentReport(unittest.TestCase):
    """Tests for attainment report generation"""

    def test_report_generation(self):
        """Test attainment report generation"""
        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        report = calculator.generate_attainment_report(
            course="TEST-COURSE",
            academic_year="2025-26"
        )

        self.assertIsInstance(report, dict)
        self.assertIn("course", report)
        self.assertIn("generated_at", report)

    def test_batch_attainment_calculation(self):
        """Test batch attainment calculation for multiple courses"""
        from university_erp.university_erp.accreditation.attainment_calculator import COPOAttainmentCalculator

        calculator = COPOAttainmentCalculator()
        courses = ["TEST-COURSE-1", "TEST-COURSE-2"]

        results = calculator.calculate_batch_attainment(
            courses=courses,
            academic_year="2025-26"
        )

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(courses))


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCOPOAttainmentCalculator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAttainmentReport))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
