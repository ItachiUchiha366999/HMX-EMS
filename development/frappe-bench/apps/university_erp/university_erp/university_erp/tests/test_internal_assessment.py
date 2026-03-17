"""
Tests for Internal Assessment Module

Tests covering assessment creation, score recording, and CO attainment.
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestInternalAssessment(FrappeTestCase):
    """Test cases for Internal Assessment DocType"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.test_course = cls.create_test_course()
        cls.test_academic_year = cls.create_test_academic_year()
        cls.test_academic_term = cls.create_test_academic_term()
        cls.test_students = cls.create_test_students()

    @classmethod
    def create_test_course(cls):
        """Create a test course"""
        if not frappe.db.exists("Course", "_Test Course IA"):
            course = frappe.new_doc("Course")
            course.course_code = "TCIA001"
            course.course_name = "_Test Course IA"
            course.insert(ignore_permissions=True)
            return course.name
        return "_Test Course IA"

    @classmethod
    def create_test_academic_year(cls):
        """Create a test academic year"""
        if not frappe.db.exists("Academic Year", "_Test Year 2024"):
            year = frappe.new_doc("Academic Year")
            year.academic_year_name = "_Test Year 2024"
            year.year_start_date = "2024-01-01"
            year.year_end_date = "2024-12-31"
            year.insert(ignore_permissions=True)
            return year.name
        return "_Test Year 2024"

    @classmethod
    def create_test_academic_term(cls):
        """Create a test academic term"""
        if not frappe.db.exists("Academic Term", "_Test Term Sem1"):
            term = frappe.new_doc("Academic Term")
            term.academic_year = cls.test_academic_year
            term.term_name = "_Test Term Sem1"
            term.term_start_date = "2024-01-01"
            term.term_end_date = "2024-06-30"
            term.insert(ignore_permissions=True)
            return term.name
        return "_Test Term Sem1"

    @classmethod
    def create_test_students(cls):
        """Create test students"""
        students = []
        for i in range(3):
            name = f"_Test Student IA {i+1}"
            if not frappe.db.exists("Student", name):
                student = frappe.new_doc("Student")
                student.student_name = name
                student.roll_number = f"TESTIA{i+1:03d}"
                student.insert(ignore_permissions=True)
                students.append(student.name)
            else:
                students.append(name)
        return students

    def test_create_internal_assessment(self):
        """Test creating internal assessment"""
        assessment = frappe.new_doc("Internal Assessment")
        assessment.assessment_name = "_Test Assignment 1"
        assessment.assessment_type = "Assignment"
        assessment.course = self.test_course
        assessment.academic_year = self.test_academic_year
        assessment.academic_term = self.test_academic_term
        assessment.assessment_date = today()
        assessment.maximum_marks = 20
        assessment.passing_marks = 8
        assessment.status = "Draft"

        assessment.insert(ignore_permissions=True)

        self.assertTrue(assessment.name)
        self.assertEqual(assessment.maximum_marks, 20)

        # Cleanup
        assessment.delete()

    def test_add_assessment_criteria(self):
        """Test adding assessment criteria"""
        assessment = frappe.new_doc("Internal Assessment")
        assessment.assessment_name = "_Test Quiz with Criteria"
        assessment.assessment_type = "Quiz"
        assessment.course = self.test_course
        assessment.academic_year = self.test_academic_year
        assessment.academic_term = self.test_academic_term
        assessment.assessment_date = today()
        assessment.maximum_marks = 20

        assessment.append("criteria", {
            "criteria_name": "Concept Understanding",
            "max_marks": 10,
            "weightage": 50
        })
        assessment.append("criteria", {
            "criteria_name": "Problem Solving",
            "max_marks": 10,
            "weightage": 50
        })

        assessment.insert(ignore_permissions=True)

        self.assertEqual(len(assessment.criteria), 2)

        # Cleanup
        assessment.delete()

    def test_record_student_scores(self):
        """Test recording student scores"""
        assessment = frappe.new_doc("Internal Assessment")
        assessment.assessment_name = "_Test Assessment Scoring"
        assessment.assessment_type = "Quiz"
        assessment.course = self.test_course
        assessment.academic_year = self.test_academic_year
        assessment.academic_term = self.test_academic_term
        assessment.assessment_date = today()
        assessment.maximum_marks = 20
        assessment.passing_marks = 8

        # Add students
        for student in self.test_students:
            assessment.append("scores", {
                "student": student
            })

        assessment.insert(ignore_permissions=True)

        # Record scores
        assessment.record_score(self.test_students[0], 18, remarks="Excellent")
        assessment.record_score(self.test_students[1], 12, remarks="Good")
        assessment.record_score(self.test_students[2], 6, remarks="Needs improvement")

        assessment.reload()

        # Check summary calculation
        self.assertEqual(assessment.evaluated_count, 3)
        self.assertEqual(assessment.passed_count, 2)  # 18 and 12 pass
        self.assertEqual(assessment.highest_marks, 18)
        self.assertEqual(assessment.lowest_marks, 6)

        # Cleanup
        assessment.delete()

    def test_bulk_upload_scores(self):
        """Test bulk score upload"""
        assessment = frappe.new_doc("Internal Assessment")
        assessment.assessment_name = "_Test Bulk Upload"
        assessment.assessment_type = "Assignment"
        assessment.course = self.test_course
        assessment.academic_year = self.test_academic_year
        assessment.academic_term = self.test_academic_term
        assessment.assessment_date = today()
        assessment.maximum_marks = 100

        for student in self.test_students:
            assessment.append("scores", {"student": student})

        assessment.insert(ignore_permissions=True)

        # Bulk upload
        scores_data = [
            {"student": self.test_students[0], "marks": 85},
            {"student": self.test_students[1], "marks": 70},
            {"student": self.test_students[2], "marks": 55}
        ]

        result = assessment.bulk_upload_scores(scores_data)

        self.assertEqual(result["updated"], 3)

        # Cleanup
        assessment.delete()


class TestAssessmentRubric(FrappeTestCase):
    """Test cases for Assessment Rubric DocType"""

    def test_create_rubric(self):
        """Test creating assessment rubric"""
        rubric = frappe.new_doc("Assessment Rubric")
        rubric.rubric_name = "_Test Rubric"
        rubric.assessment_type = "Assignment"
        rubric.level_1_label = "Excellent"
        rubric.level_1_min_percentage = 90
        rubric.level_2_label = "Good"
        rubric.level_2_min_percentage = 75
        rubric.level_3_label = "Satisfactory"
        rubric.level_3_min_percentage = 60
        rubric.level_4_label = "Needs Improvement"
        rubric.level_4_min_percentage = 40
        rubric.level_5_label = "Unsatisfactory"
        rubric.level_5_min_percentage = 0

        rubric.insert(ignore_permissions=True)

        self.assertTrue(rubric.name)

        # Test level lookup
        level = rubric.get_level_for_percentage(85)
        self.assertEqual(level["label"], "Good")

        level = rubric.get_level_for_percentage(95)
        self.assertEqual(level["label"], "Excellent")

        # Cleanup
        rubric.delete()

    def test_rubric_percentage_validation(self):
        """Test that rubric percentages must be in descending order"""
        rubric = frappe.new_doc("Assessment Rubric")
        rubric.rubric_name = "_Test Invalid Rubric"
        rubric.assessment_type = "Quiz"
        rubric.level_1_label = "Best"
        rubric.level_1_min_percentage = 50  # Lower than level 2
        rubric.level_2_label = "Good"
        rubric.level_2_min_percentage = 75  # Higher than level 1
        rubric.level_3_min_percentage = 60
        rubric.level_4_min_percentage = 40
        rubric.level_5_min_percentage = 0

        with self.assertRaises(frappe.ValidationError):
            rubric.insert(ignore_permissions=True)


if __name__ == "__main__":
    unittest.main()
