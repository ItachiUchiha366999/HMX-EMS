"""
Tests for Online Examination Module

Tests covering exam creation, student attempts, and auto-evaluation.
"""

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_to_date


class TestOnlineExamination(FrappeTestCase):
    """Test cases for Online Examination DocType"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.test_course = cls.create_test_course()
        cls.test_student = cls.create_test_student()

    @classmethod
    def create_test_course(cls):
        """Create a test course"""
        if not frappe.db.exists("Course", "_Test Course OE"):
            course = frappe.new_doc("Course")
            course.course_code = "TCOE001"
            course.course_name = "_Test Course OE"
            course.insert(ignore_permissions=True)
            return course.name
        return "_Test Course OE"

    @classmethod
    def create_test_student(cls):
        """Create a test student"""
        if not frappe.db.exists("Student", "_Test Student OE"):
            student = frappe.new_doc("Student")
            student.student_name = "_Test Student OE"
            student.roll_number = "TEST001"
            student.insert(ignore_permissions=True)
            return student.name
        return "_Test Student OE"

    def test_create_online_examination(self):
        """Test creating online examination"""
        exam = frappe.new_doc("Online Examination")
        exam.examination_name = "_Test Online Exam"
        exam.course = self.test_course
        exam.start_datetime = now_datetime()
        exam.end_datetime = add_to_date(now_datetime(), hours=2)
        exam.duration_minutes = 60
        exam.total_marks = 100
        exam.passing_marks = 40
        exam.max_attempts = 1
        exam.status = "Draft"

        exam.insert(ignore_permissions=True)

        self.assertTrue(exam.name)
        self.assertEqual(exam.duration_minutes, 60)

        # Cleanup
        exam.delete()

    def test_exam_timing_validation(self):
        """Test that end time must be after start time"""
        exam = frappe.new_doc("Online Examination")
        exam.examination_name = "_Test Invalid Timing Exam"
        exam.course = self.test_course
        exam.start_datetime = now_datetime()
        exam.end_datetime = add_to_date(now_datetime(), hours=-1)  # End before start
        exam.duration_minutes = 60
        exam.total_marks = 100

        with self.assertRaises(frappe.ValidationError):
            exam.insert(ignore_permissions=True)

    def test_add_eligible_students(self):
        """Test adding eligible students to exam"""
        exam = frappe.new_doc("Online Examination")
        exam.examination_name = "_Test Exam with Students"
        exam.course = self.test_course
        exam.start_datetime = now_datetime()
        exam.end_datetime = add_to_date(now_datetime(), hours=2)
        exam.duration_minutes = 60
        exam.total_marks = 100

        exam.append("eligible_students", {
            "student": self.test_student
        })

        exam.insert(ignore_permissions=True)

        self.assertEqual(len(exam.eligible_students), 1)
        self.assertEqual(exam.eligible_students[0].student, self.test_student)

        # Cleanup
        exam.delete()

    def test_exam_proctoring_settings(self):
        """Test proctoring configuration"""
        exam = frappe.new_doc("Online Examination")
        exam.examination_name = "_Test Proctored Exam"
        exam.course = self.test_course
        exam.start_datetime = now_datetime()
        exam.end_datetime = add_to_date(now_datetime(), hours=2)
        exam.duration_minutes = 60
        exam.total_marks = 100
        exam.enable_proctoring = 1
        exam.webcam_required = 1
        exam.capture_snapshots = 1
        exam.snapshot_interval_seconds = 30
        exam.max_tab_switches = 3

        exam.insert(ignore_permissions=True)

        self.assertTrue(exam.enable_proctoring)
        self.assertEqual(exam.max_tab_switches, 3)

        # Cleanup
        exam.delete()


class TestStudentExamAttempt(FrappeTestCase):
    """Test cases for Student Exam Attempt DocType"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.test_course = cls.create_test_course()
        cls.test_student = cls.create_test_student()
        cls.test_exam = cls.create_test_exam()

    @classmethod
    def create_test_course(cls):
        """Create a test course"""
        if not frappe.db.exists("Course", "_Test Course SEA"):
            course = frappe.new_doc("Course")
            course.course_code = "TCSEA001"
            course.course_name = "_Test Course SEA"
            course.insert(ignore_permissions=True)
            return course.name
        return "_Test Course SEA"

    @classmethod
    def create_test_student(cls):
        """Create a test student"""
        if not frappe.db.exists("Student", "_Test Student SEA"):
            student = frappe.new_doc("Student")
            student.student_name = "_Test Student SEA"
            student.roll_number = "TESTSEA001"
            student.insert(ignore_permissions=True)
            return student.name
        return "_Test Student SEA"

    @classmethod
    def create_test_exam(cls):
        """Create a test examination"""
        exam_name = "_Test Exam SEA"
        if not frappe.db.exists("Online Examination", exam_name):
            exam = frappe.new_doc("Online Examination")
            exam.examination_name = exam_name
            exam.course = cls.test_course
            exam.start_datetime = now_datetime()
            exam.end_datetime = add_to_date(now_datetime(), hours=24)
            exam.duration_minutes = 60
            exam.total_marks = 100
            exam.max_attempts = 3

            exam.append("eligible_students", {
                "student": cls.test_student
            })

            exam.insert(ignore_permissions=True)
            return exam.name
        return exam_name

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        if frappe.db.exists("Online Examination", cls.test_exam):
            frappe.delete_doc("Online Examination", cls.test_exam, force=True)
        super().tearDownClass()

    def test_create_exam_attempt(self):
        """Test creating exam attempt"""
        attempt = frappe.new_doc("Student Exam Attempt")
        attempt.online_examination = self.test_exam
        attempt.student = self.test_student
        attempt.start_time = now_datetime()
        attempt.status = "In Progress"
        attempt.attempt_number = 1
        attempt.total_questions = 10

        attempt.insert(ignore_permissions=True)

        self.assertTrue(attempt.name)
        self.assertEqual(attempt.status, "In Progress")

        # Cleanup
        attempt.delete()

    def test_save_answer(self):
        """Test saving student answer"""
        attempt = frappe.new_doc("Student Exam Attempt")
        attempt.online_examination = self.test_exam
        attempt.student = self.test_student
        attempt.start_time = now_datetime()
        attempt.status = "In Progress"
        attempt.attempt_number = 1
        attempt.total_questions = 10
        attempt.insert(ignore_permissions=True)

        # Save an answer
        attempt.save_answer("Q1", "Option A", False)
        attempt.reload()

        self.assertEqual(len(attempt.answers), 1)
        self.assertEqual(attempt.answers[0].question, "Q1")

        # Cleanup
        attempt.delete()

    def test_attempt_number_tracking(self):
        """Test that attempt number increments correctly"""
        # First attempt
        attempt1 = frappe.new_doc("Student Exam Attempt")
        attempt1.online_examination = self.test_exam
        attempt1.student = self.test_student
        attempt1.start_time = now_datetime()
        attempt1.status = "Submitted"
        attempt1.attempt_number = 1
        attempt1.insert(ignore_permissions=True)

        # Second attempt
        attempt2 = frappe.new_doc("Student Exam Attempt")
        attempt2.online_examination = self.test_exam
        attempt2.student = self.test_student
        attempt2.start_time = now_datetime()
        attempt2.status = "In Progress"
        attempt2.attempt_number = 2
        attempt2.insert(ignore_permissions=True)

        self.assertEqual(attempt1.attempt_number, 1)
        self.assertEqual(attempt2.attempt_number, 2)

        # Cleanup
        attempt1.delete()
        attempt2.delete()


if __name__ == "__main__":
    unittest.main()
