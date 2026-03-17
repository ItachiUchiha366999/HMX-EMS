"""
Tests for Question Bank Module

Tests covering question creation, validation, and statistics.
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestQuestionBank(FrappeTestCase):
    """Test cases for Question Bank DocType"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.test_course = cls.create_test_course()

    @classmethod
    def create_test_course(cls):
        """Create a test course"""
        if not frappe.db.exists("Course", "_Test Course QB"):
            course = frappe.new_doc("Course")
            course.course_code = "TCQ001"
            course.course_name = "_Test Course QB"
            course.insert(ignore_permissions=True)
            return course.name
        return "_Test Course QB"

    def test_create_mcq_question(self):
        """Test creating MCQ question with options"""
        question = frappe.new_doc("Question Bank")
        question.question_text = "What is 2 + 2?"
        question.question_type = "Multiple Choice (MCQ)"
        question.course = self.test_course
        question.difficulty_level = "Easy"
        question.blooms_taxonomy = "Remember (L1)"
        question.marks = 1

        # Add options
        question.append("options", {
            "option_label": "A",
            "option_text": "3",
            "is_correct": 0
        })
        question.append("options", {
            "option_label": "B",
            "option_text": "4",
            "is_correct": 1
        })
        question.append("options", {
            "option_label": "C",
            "option_text": "5",
            "is_correct": 0
        })
        question.append("options", {
            "option_label": "D",
            "option_text": "6",
            "is_correct": 0
        })

        question.insert(ignore_permissions=True)

        self.assertTrue(question.name)
        self.assertEqual(len(question.options), 4)

        # Cleanup
        question.delete()

    def test_mcq_must_have_correct_answer(self):
        """Test that MCQ questions must have exactly one correct option"""
        question = frappe.new_doc("Question Bank")
        question.question_text = "Test question without correct answer"
        question.question_type = "Multiple Choice (MCQ)"
        question.course = self.test_course
        question.difficulty_level = "Easy"
        question.blooms_taxonomy = "Remember (L1)"
        question.marks = 1

        # Add options without correct answer
        question.append("options", {
            "option_label": "A",
            "option_text": "Option 1",
            "is_correct": 0
        })
        question.append("options", {
            "option_label": "B",
            "option_text": "Option 2",
            "is_correct": 0
        })

        with self.assertRaises(frappe.ValidationError):
            question.insert(ignore_permissions=True)

    def test_create_short_answer_question(self):
        """Test creating short answer question"""
        question = frappe.new_doc("Question Bank")
        question.question_text = "Define photosynthesis in one sentence."
        question.question_type = "Short Answer"
        question.course = self.test_course
        question.difficulty_level = "Medium"
        question.blooms_taxonomy = "Understand (L2)"
        question.marks = 2
        question.correct_answer = "Photosynthesis is the process by which plants convert light energy into chemical energy."

        question.insert(ignore_permissions=True)

        self.assertTrue(question.name)
        self.assertEqual(question.question_type, "Short Answer")

        # Cleanup
        question.delete()

    def test_question_status_workflow(self):
        """Test question status transitions"""
        question = frappe.new_doc("Question Bank")
        question.question_text = "Test status workflow question"
        question.question_type = "Short Answer"
        question.course = self.test_course
        question.difficulty_level = "Easy"
        question.blooms_taxonomy = "Remember (L1)"
        question.marks = 1
        question.insert(ignore_permissions=True)

        # Initial status should be Draft
        self.assertEqual(question.status, "Draft")

        # Submit for review
        question.submit_for_review()
        question.reload()
        self.assertEqual(question.status, "Pending Review")

        # Cleanup
        question.delete()

    def test_negative_marking_configuration(self):
        """Test negative marking settings"""
        question = frappe.new_doc("Question Bank")
        question.question_text = "Test negative marking question"
        question.question_type = "Multiple Choice (MCQ)"
        question.course = self.test_course
        question.difficulty_level = "Hard"
        question.blooms_taxonomy = "Apply (L3)"
        question.marks = 4
        question.negative_marking = 1
        question.negative_marks = 1

        question.append("options", {
            "option_label": "A",
            "option_text": "Correct",
            "is_correct": 1
        })
        question.append("options", {
            "option_label": "B",
            "option_text": "Wrong",
            "is_correct": 0
        })

        question.insert(ignore_permissions=True)

        self.assertTrue(question.negative_marking)
        self.assertEqual(question.negative_marks, 1)

        # Cleanup
        question.delete()


class TestQuestionPaperGenerator(FrappeTestCase):
    """Test cases for Question Paper Generator"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.test_course = cls.create_test_course()
        cls.create_test_questions()

    @classmethod
    def create_test_course(cls):
        """Create a test course"""
        if not frappe.db.exists("Course", "_Test Course QPG"):
            course = frappe.new_doc("Course")
            course.course_code = "TCQPG001"
            course.course_name = "_Test Course QPG"
            course.insert(ignore_permissions=True)
            return course.name
        return "_Test Course QPG"

    @classmethod
    def create_test_questions(cls):
        """Create test questions for paper generation"""
        cls.questions = []

        for i in range(10):
            difficulty = ["Easy", "Medium", "Hard"][i % 3]
            q = frappe.new_doc("Question Bank")
            q.question_text = f"Test Question {i+1} for paper generation"
            q.question_type = "Multiple Choice (MCQ)"
            q.course = cls.test_course
            q.difficulty_level = difficulty
            q.blooms_taxonomy = "Remember (L1)"
            q.marks = 2
            q.status = "Approved"

            q.append("options", {"option_label": "A", "option_text": "Opt A", "is_correct": 1})
            q.append("options", {"option_label": "B", "option_text": "Opt B", "is_correct": 0})
            q.append("options", {"option_label": "C", "option_text": "Opt C", "is_correct": 0})
            q.append("options", {"option_label": "D", "option_text": "Opt D", "is_correct": 0})

            q.insert(ignore_permissions=True)
            cls.questions.append(q.name)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        for q_name in cls.questions:
            frappe.delete_doc("Question Bank", q_name, force=True)
        super().tearDownClass()

    def test_create_question_paper_template(self):
        """Test creating question paper template"""
        template = frappe.new_doc("Question Paper Template")
        template.template_name = "_Test Template"
        template.course = self.test_course
        template.total_marks = 20
        template.duration_minutes = 60
        template.total_questions = 10

        template.append("sections", {
            "section_name": "Section A",
            "section_type": "MCQ",
            "number_of_questions": 10,
            "marks_per_question": 2,
            "total_marks": 20
        })

        template.insert(ignore_permissions=True)

        self.assertTrue(template.name)
        self.assertEqual(template.total_marks, 20)

        # Cleanup
        template.delete()


if __name__ == "__main__":
    unittest.main()
