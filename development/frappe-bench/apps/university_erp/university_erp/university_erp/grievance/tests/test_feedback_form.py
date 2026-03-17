# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days


class TestFeedbackForm(FrappeTestCase):
    """Test cases for Feedback Form DocType"""

    def test_feedback_form_creation(self):
        """Test creating a feedback form"""
        feedback_form = frappe.get_doc({
            "doctype": "Feedback Form",
            "title": "Test Course Feedback",
            "form_type": "Course Feedback",
            "description": "Test feedback form for unit tests",
            "status": "Draft",
            "start_date": getdate(),
            "end_date": add_days(getdate(), 14),
            "allow_anonymous": 1,
            "is_mandatory": 0
        })

        # Add a section
        feedback_form.append("sections", {
            "section_title": "Teaching Quality",
            "section_description": "Rate the teaching quality"
        })

        # Add questions
        feedback_form.append("questions", {
            "question_text": "How would you rate the course content?",
            "question_type": "Rating",
            "is_required": 1,
            "options": "Poor\nFair\nGood\nVery Good\nExcellent",
            "weightage": 1.0,
            "category": "Content"
        })

        feedback_form.append("questions", {
            "question_text": "How likely are you to recommend this course?",
            "question_type": "Scale",
            "is_required": 1,
            "help_text": "0 = Not at all likely, 10 = Extremely likely",
            "weightage": 1.0,
            "category": "NPS"
        })

        feedback_form.insert(ignore_permissions=True)

        self.assertIsNotNone(feedback_form.name)
        self.assertEqual(feedback_form.status, "Draft")
        self.assertEqual(len(feedback_form.questions), 2)

        # Clean up
        feedback_form.delete(force=True)

    def test_feedback_form_activation(self):
        """Test activating a feedback form"""
        feedback_form = frappe.get_doc({
            "doctype": "Feedback Form",
            "title": "Activation Test Form",
            "form_type": "Faculty Feedback",
            "status": "Draft",
            "start_date": getdate(),
            "end_date": add_days(getdate(), 7)
        })

        feedback_form.append("questions", {
            "question_text": "Test question",
            "question_type": "Rating",
            "is_required": 1
        })

        feedback_form.insert(ignore_permissions=True)

        # Activate the form
        feedback_form.status = "Active"
        feedback_form.save(ignore_permissions=True)

        self.assertEqual(feedback_form.status, "Active")

        # Clean up
        feedback_form.delete(force=True)

    def test_feedback_form_with_filters(self):
        """Test feedback form with program/department filters"""
        feedback_form = frappe.get_doc({
            "doctype": "Feedback Form",
            "title": "Filtered Form Test",
            "form_type": "Course Feedback",
            "status": "Draft",
            "start_date": getdate(),
            "end_date": add_days(getdate(), 14)
        })

        # Add program filter (if Program exists)
        programs = frappe.get_all("Program", limit=1)
        if programs:
            feedback_form.append("program_filters", {
                "program": programs[0].name
            })

        # Add department filter (if Department exists)
        departments = frappe.get_all("Department", limit=1)
        if departments:
            feedback_form.append("department_filters", {
                "department": departments[0].name
            })

        feedback_form.append("questions", {
            "question_text": "Filtered test question",
            "question_type": "Text",
            "is_required": 0
        })

        feedback_form.insert(ignore_permissions=True)

        self.assertIsNotNone(feedback_form.name)

        # Clean up
        feedback_form.delete(force=True)

    def test_feedback_form_question_types(self):
        """Test various question types in feedback form"""
        feedback_form = frappe.get_doc({
            "doctype": "Feedback Form",
            "title": "Question Types Test",
            "form_type": "General Feedback",
            "status": "Draft",
            "start_date": getdate(),
            "end_date": add_days(getdate(), 7)
        })

        # Add different question types
        question_types = [
            {"text": "Rating question", "type": "Rating", "options": "1\n2\n3\n4\n5"},
            {"text": "Scale question", "type": "Scale"},
            {"text": "Text question", "type": "Text"},
            {"text": "Long Text question", "type": "Long Text"},
            {"text": "Yes/No question", "type": "Yes/No"},
            {"text": "Multiple Choice question", "type": "Multiple Choice", "options": "Option A\nOption B\nOption C"}
        ]

        for idx, q in enumerate(question_types):
            feedback_form.append("questions", {
                "question_text": q["text"],
                "question_type": q["type"],
                "options": q.get("options", ""),
                "is_required": 0,
                "weightage": 1.0
            })

        feedback_form.insert(ignore_permissions=True)

        self.assertEqual(len(feedback_form.questions), 6)

        # Clean up
        feedback_form.delete(force=True)

    def test_feedback_form_close(self):
        """Test closing a feedback form"""
        feedback_form = frappe.get_doc({
            "doctype": "Feedback Form",
            "title": "Close Test Form",
            "form_type": "Course Feedback",
            "status": "Active",
            "start_date": add_days(getdate(), -7),
            "end_date": getdate()
        })

        feedback_form.append("questions", {
            "question_text": "Test question",
            "question_type": "Rating",
            "is_required": 1
        })

        feedback_form.insert(ignore_permissions=True)

        # Close the form
        feedback_form.status = "Closed"
        feedback_form.save(ignore_permissions=True)

        self.assertEqual(feedback_form.status, "Closed")

        # Clean up
        feedback_form.delete(force=True)

    def test_feedback_form_statistics_fields(self):
        """Test feedback form statistics fields"""
        feedback_form = frappe.get_doc({
            "doctype": "Feedback Form",
            "title": "Statistics Test Form",
            "form_type": "Faculty Feedback",
            "status": "Draft",
            "start_date": getdate(),
            "end_date": add_days(getdate(), 14),
            "response_count": 0,
            "average_score": 0.0
        })

        feedback_form.append("questions", {
            "question_text": "Stats test question",
            "question_type": "Rating",
            "is_required": 1
        })

        feedback_form.insert(ignore_permissions=True)

        # Update statistics
        feedback_form.response_count = 10
        feedback_form.average_score = 85.5
        feedback_form.save(ignore_permissions=True)

        self.assertEqual(feedback_form.response_count, 10)
        self.assertEqual(feedback_form.average_score, 85.5)

        # Clean up
        feedback_form.delete(force=True)
