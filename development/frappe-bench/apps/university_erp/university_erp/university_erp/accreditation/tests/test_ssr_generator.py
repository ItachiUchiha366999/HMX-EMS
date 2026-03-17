# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import today, getdate


class TestSSRGenerator(unittest.TestCase):
    """Tests for SSR (Self Study Report) Generator"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        # Create test accreditation cycle for SSR generation
        if not frappe.db.exists("Accreditation Cycle", "Test SSR Cycle"):
            cls.test_cycle = frappe.get_doc({
                "doctype": "Accreditation Cycle",
                "cycle_name": "Test SSR Cycle",
                "accreditation_type": "NAAC",
                "start_date": today(),
                "end_date": frappe.utils.add_months(today(), 12),
                "status": "Data Collection"
            })
            cls.test_cycle.insert(ignore_permissions=True)
        else:
            cls.test_cycle = frappe.get_doc("Accreditation Cycle", "Test SSR Cycle")

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if frappe.db.exists("Accreditation Cycle", "Test SSR Cycle"):
            frappe.delete_doc("Accreditation Cycle", "Test SSR Cycle", force=True)
        frappe.db.commit()

    def test_generator_initialization(self):
        """Test SSR generator initialization"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        self.assertIsNotNone(generator)
        self.assertEqual(generator.accreditation_cycle, "Test SSR Cycle")

    def test_generate_ssr_html(self):
        """Test SSR generation in HTML format"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator.generate_ssr(output_format="html")

        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        # Should contain HTML tags
        self.assertIn("<", result)

    def test_executive_summary_generation(self):
        """Test executive summary generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator._generate_executive_summary()

        self.assertIsInstance(result, dict)
        self.assertIn("institution_name", result)
        self.assertIn("accreditation_type", result)

    def test_institutional_profile_generation(self):
        """Test institutional profile generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator._generate_institutional_profile()

        self.assertIsInstance(result, dict)
        self.assertIn("basic_info", result)

    def test_all_criteria_generation(self):
        """Test all criteria generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator._generate_all_criteria()

        self.assertIsInstance(result, dict)
        # Should have all 7 criteria
        self.assertEqual(len(result), 7)
        self.assertIn("criterion_1", result)
        self.assertIn("criterion_7", result)

    def test_criterion_generation(self):
        """Test individual criterion generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")

        # Test each criterion
        for i in range(1, 8):
            result = generator._generate_criterion(i)
            self.assertIsInstance(result, dict)
            self.assertIn("criterion_number", result)
            self.assertIn("criterion_name", result)
            self.assertIn("metrics", result)

    def test_dvv_clarifications_section(self):
        """Test DVV clarifications section generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator._generate_dvv_clarifications()

        self.assertIsInstance(result, dict)

    def test_supporting_documents_section(self):
        """Test supporting documents section generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator._generate_supporting_documents()

        self.assertIsInstance(result, dict)

    def test_swoc_analysis_generation(self):
        """Test SWOC analysis generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator._generate_swoc_analysis()

        self.assertIsInstance(result, dict)
        self.assertIn("strengths", result)
        self.assertIn("weaknesses", result)
        self.assertIn("opportunities", result)
        self.assertIn("challenges", result)

    def test_best_practices_generation(self):
        """Test best practices section generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test SSR Cycle")
        result = generator._generate_best_practices()

        self.assertIsInstance(result, dict)
        self.assertIn("practices", result)


class TestSSRExport(unittest.TestCase):
    """Tests for SSR export functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        if not frappe.db.exists("Accreditation Cycle", "Test Export Cycle"):
            cls.test_cycle = frappe.get_doc({
                "doctype": "Accreditation Cycle",
                "cycle_name": "Test Export Cycle",
                "accreditation_type": "NAAC",
                "start_date": today(),
                "end_date": frappe.utils.add_months(today(), 12),
                "status": "Data Collection"
            })
            cls.test_cycle.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if frappe.db.exists("Accreditation Cycle", "Test Export Cycle"):
            frappe.delete_doc("Accreditation Cycle", "Test Export Cycle", force=True)
        frappe.db.commit()

    def test_html_export(self):
        """Test HTML export"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test Export Cycle")
        result = generator.generate_ssr(output_format="html")

        self.assertIsNotNone(result)
        self.assertIn("<html", result.lower())

    def test_json_export(self):
        """Test JSON export"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test Export Cycle")
        result = generator.generate_ssr(output_format="json")

        self.assertIsNotNone(result)
        # Should be valid JSON string
        import json
        try:
            parsed = json.loads(result)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("Invalid JSON output")

    def test_table_of_contents_generation(self):
        """Test table of contents generation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        generator = SSRGenerator(accreditation_cycle="Test Export Cycle")
        toc = generator._generate_table_of_contents()

        self.assertIsInstance(toc, list)
        # Should have sections for all criteria plus intro sections
        self.assertGreater(len(toc), 7)


class TestSSRValidation(unittest.TestCase):
    """Tests for SSR validation functionality"""

    def test_completeness_check(self):
        """Test SSR completeness check"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        # Create temporary test cycle
        if frappe.db.exists("Accreditation Cycle", "Test Completeness Cycle"):
            frappe.delete_doc("Accreditation Cycle", "Test Completeness Cycle", force=True)

        test_cycle = frappe.get_doc({
            "doctype": "Accreditation Cycle",
            "cycle_name": "Test Completeness Cycle",
            "accreditation_type": "NAAC",
            "start_date": today(),
            "end_date": frappe.utils.add_months(today(), 12),
            "status": "Data Collection"
        })
        test_cycle.insert(ignore_permissions=True)

        try:
            generator = SSRGenerator(accreditation_cycle="Test Completeness Cycle")
            is_complete, missing = generator.check_completeness()

            self.assertIsInstance(is_complete, bool)
            self.assertIsInstance(missing, list)
        finally:
            frappe.delete_doc("Accreditation Cycle", "Test Completeness Cycle", force=True)

    def test_data_validation(self):
        """Test SSR data validation"""
        from university_erp.university_erp.accreditation.ssr_generator import SSRGenerator

        # Create temporary test cycle
        if frappe.db.exists("Accreditation Cycle", "Test Validation Cycle"):
            frappe.delete_doc("Accreditation Cycle", "Test Validation Cycle", force=True)

        test_cycle = frappe.get_doc({
            "doctype": "Accreditation Cycle",
            "cycle_name": "Test Validation Cycle",
            "accreditation_type": "NAAC",
            "start_date": today(),
            "end_date": frappe.utils.add_months(today(), 12),
            "status": "Data Collection"
        })
        test_cycle.insert(ignore_permissions=True)

        try:
            generator = SSRGenerator(accreditation_cycle="Test Validation Cycle")
            is_valid, errors = generator.validate_ssr_data()

            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(errors, list)
        finally:
            frappe.delete_doc("Accreditation Cycle", "Test Validation Cycle", force=True)


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSSRGenerator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSSRExport))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSSRValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
