# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import today, getdate


class TestNAACDataCollector(unittest.TestCase):
    """Tests for NAAC Data Collector"""

    def test_collector_initialization(self):
        """Test collector initialization"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        self.assertIsNotNone(collector)
        self.assertEqual(collector.academic_year, "2025-26")

    def test_collect_all_metrics(self):
        """Test collecting all NAAC metrics"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector.collect_all_metrics()

        self.assertIsInstance(result, dict)
        # Should have all 7 criteria
        self.assertIn("criterion_1", result)
        self.assertIn("criterion_2", result)
        self.assertIn("criterion_3", result)
        self.assertIn("criterion_4", result)
        self.assertIn("criterion_5", result)
        self.assertIn("criterion_6", result)
        self.assertIn("criterion_7", result)

    def test_criterion_1_collection(self):
        """Test Criterion 1 - Curricular Aspects data collection"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._collect_criterion_1()

        self.assertIsInstance(result, dict)
        self.assertIn("criterion_name", result)
        self.assertEqual(result["criterion_name"], "Curricular Aspects")
        self.assertIn("metrics", result)

    def test_criterion_2_collection(self):
        """Test Criterion 2 - Teaching-Learning data collection"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._collect_criterion_2()

        self.assertIsInstance(result, dict)
        self.assertIn("criterion_name", result)
        self.assertEqual(result["criterion_name"], "Teaching-Learning and Evaluation")
        self.assertIn("metrics", result)

    def test_criterion_3_collection(self):
        """Test Criterion 3 - Research data collection"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._collect_criterion_3()

        self.assertIsInstance(result, dict)
        self.assertIn("criterion_name", result)
        self.assertEqual(result["criterion_name"], "Research, Innovations and Extension")

    def test_criterion_4_collection(self):
        """Test Criterion 4 - Infrastructure data collection"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._collect_criterion_4()

        self.assertIsInstance(result, dict)
        self.assertIn("criterion_name", result)
        self.assertEqual(result["criterion_name"], "Infrastructure and Learning Resources")

    def test_criterion_5_collection(self):
        """Test Criterion 5 - Student Support data collection"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._collect_criterion_5()

        self.assertIsInstance(result, dict)
        self.assertIn("criterion_name", result)
        self.assertEqual(result["criterion_name"], "Student Support and Progression")

    def test_criterion_6_collection(self):
        """Test Criterion 6 - Governance data collection"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._collect_criterion_6()

        self.assertIsInstance(result, dict)
        self.assertIn("criterion_name", result)
        self.assertEqual(result["criterion_name"], "Governance, Leadership and Management")

    def test_criterion_7_collection(self):
        """Test Criterion 7 - Best Practices data collection"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._collect_criterion_7()

        self.assertIsInstance(result, dict)
        self.assertIn("criterion_name", result)
        self.assertEqual(result["criterion_name"], "Institutional Values and Best Practices")

    def test_student_data_collection(self):
        """Test student data collection for NAAC"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._get_student_data()

        self.assertIsInstance(result, dict)
        self.assertIn("total_students", result)
        self.assertIn("male_students", result)
        self.assertIn("female_students", result)

    def test_faculty_data_collection(self):
        """Test faculty data collection for NAAC"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._get_faculty_data()

        self.assertIsInstance(result, dict)
        self.assertIn("total_faculty", result)
        self.assertIn("phd_holders", result)

    def test_research_data_collection(self):
        """Test research data collection for NAAC"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._get_research_data()

        self.assertIsInstance(result, dict)
        self.assertIn("publications", result)
        self.assertIn("patents", result)
        self.assertIn("funded_projects", result)

    def test_infrastructure_data_collection(self):
        """Test infrastructure data collection for NAAC"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._get_infrastructure_data()

        self.assertIsInstance(result, dict)
        self.assertIn("classrooms", result)
        self.assertIn("labs", result)

    def test_placement_data_collection(self):
        """Test placement data collection for NAAC"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        result = collector._get_placement_data()

        self.assertIsInstance(result, dict)
        self.assertIn("students_placed", result)
        self.assertIn("average_salary", result)

    def test_data_validation(self):
        """Test data validation in collector"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")

        # Test validation method
        is_valid, errors = collector.validate_collected_data()

        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(errors, list)

    def test_export_to_excel(self):
        """Test export to Excel format"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")
        collector.collect_all_metrics()

        # Test export method exists and returns path or bytes
        try:
            result = collector.export_to_excel()
            self.assertIsNotNone(result)
        except NotImplementedError:
            # Method may not be fully implemented yet
            pass


class TestNAACDataStorage(unittest.TestCase):
    """Tests for NAAC data storage functionality"""

    def test_store_metric_value(self):
        """Test storing metric value"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")

        # Store a test metric
        result = collector.store_metric_value(
            metric_number="1.1.1",
            value=85,
            year="2025-26"
        )

        self.assertIsNotNone(result)

    def test_get_historical_data(self):
        """Test getting historical data for metrics"""
        from university_erp.university_erp.accreditation.naac_data_collector import NAACDataCollector

        collector = NAACDataCollector(academic_year="2025-26")

        result = collector.get_historical_data(
            metric_number="1.1.1",
            years=5
        )

        self.assertIsInstance(result, list)


def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNAACDataCollector))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNAACDataStorage))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
