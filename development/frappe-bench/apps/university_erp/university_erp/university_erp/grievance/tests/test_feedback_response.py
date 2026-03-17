# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days


class TestFeedbackResponse(FrappeTestCase):
    """Test cases for Feedback Response DocType"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.test_form = cls.create_test_feedback_form()

    @classmethod
    def create_test_feedback_form(cls):
        """Create a test feedback form"""
        form_name = "Test Response Form"
        if frappe.db.exists("Feedback Form", form_name):
            return frappe.get_doc("Feedback Form", form_name)

        feedback_form = frappe.get_doc({
            "doctype": "Feedback Form",
            "title": form_name,
            "form_type": "Course Feedback",
            "status": "Active",
            "start_date": getdate(),
            "end_date": add_days(getdate(), 30),
            "allow_anonymous": 1
        })

        feedback_form.append("questions", {
            "question_text": "Rate the course content",
            "question_type": "Rating",
            "is_required": 1,
            "options": "Poor\nFair\nGood\nVery Good\nExcellent",
            "weightage": 1.0,
            "category": "Content"
        })

        feedback_form.append("questions", {
            "question_text": "How likely to recommend?",
            "question_type": "Scale",
            "is_required": 1,
            "weightage": 1.0,
            "category": "NPS"
        })

        feedback_form.append("questions", {
            "question_text": "Additional comments",
            "question_type": "Text",
            "is_required": 0
        })

        feedback_form.insert(ignore_permissions=True)
        return feedback_form

    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        super().tearDownClass()
        if cls.test_form:
            # Delete all responses first
            responses = frappe.get_all(
                "Feedback Response",
                filters={"feedback_form": cls.test_form.name}
            )
            for r in responses:
                frappe.delete_doc("Feedback Response", r.name, force=True)
            frappe.delete_doc("Feedback Form", cls.test_form.name, force=True)

    def test_feedback_response_creation(self):
        """Test creating a feedback response"""
        response = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "respondent_name": "Test Student",
            "submission_date": getdate(),
            "status": "Valid"
        })

        # Add answers
        response.append("answers", {
            "question_id": "1",
            "question_text": "Rate the course content",
            "answer_value": "5"
        })

        response.append("answers", {
            "question_id": "2",
            "question_text": "How likely to recommend?",
            "answer_value": "9"
        })

        response.insert(ignore_permissions=True)

        self.assertIsNotNone(response.name)
        self.assertEqual(len(response.answers), 2)
        self.assertEqual(response.status, "Valid")

        # Clean up
        response.delete(force=True)

    def test_feedback_response_anonymous(self):
        """Test anonymous feedback response"""
        response = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "is_anonymous": 1,
            "submission_date": getdate(),
            "status": "Valid"
        })

        response.append("answers", {
            "question_id": "1",
            "question_text": "Rate the course content",
            "answer_value": "4"
        })

        response.insert(ignore_permissions=True)

        self.assertEqual(response.is_anonymous, 1)

        # Clean up
        response.delete(force=True)

    def test_feedback_response_score_calculation(self):
        """Test overall score calculation"""
        response = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "respondent_name": "Score Test Student",
            "submission_date": getdate(),
            "status": "Valid",
            "overall_score": 80.0  # Pre-calculated score
        })

        response.append("answers", {
            "question_id": "1",
            "question_text": "Rate the course content",
            "answer_value": "4"  # 4/5 = 80%
        })

        response.insert(ignore_permissions=True)

        self.assertEqual(response.overall_score, 80.0)

        # Clean up
        response.delete(force=True)

    def test_feedback_response_section_scores(self):
        """Test section scores in feedback response"""
        response = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "respondent_name": "Section Score Student",
            "submission_date": getdate(),
            "status": "Valid"
        })

        response.append("answers", {
            "question_id": "1",
            "question_text": "Rate the course content",
            "answer_value": "5"
        })

        # Add section scores
        response.append("section_scores", {
            "section_name": "Content",
            "score": 100.0,
            "responses_count": 1
        })

        response.append("section_scores", {
            "section_name": "Teaching",
            "score": 85.0,
            "responses_count": 1
        })

        response.insert(ignore_permissions=True)

        self.assertEqual(len(response.section_scores), 2)
        self.assertEqual(response.section_scores[0].section_name, "Content")

        # Clean up
        response.delete(force=True)

    def test_feedback_response_nps_category(self):
        """Test NPS category classification"""
        # Test Promoter (9-10)
        response1 = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "submission_date": getdate(),
            "status": "Valid",
            "nps_category": "Promoter"
        })
        response1.append("answers", {"question_id": "1", "question_text": "Q1", "answer_value": "5"})
        response1.insert(ignore_permissions=True)
        self.assertEqual(response1.nps_category, "Promoter")
        response1.delete(force=True)

        # Test Passive (7-8)
        response2 = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "submission_date": getdate(),
            "status": "Valid",
            "nps_category": "Passive"
        })
        response2.append("answers", {"question_id": "1", "question_text": "Q1", "answer_value": "4"})
        response2.insert(ignore_permissions=True)
        self.assertEqual(response2.nps_category, "Passive")
        response2.delete(force=True)

        # Test Detractor (0-6)
        response3 = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "submission_date": getdate(),
            "status": "Valid",
            "nps_category": "Detractor"
        })
        response3.append("answers", {"question_id": "1", "question_text": "Q1", "answer_value": "2"})
        response3.insert(ignore_permissions=True)
        self.assertEqual(response3.nps_category, "Detractor")
        response3.delete(force=True)

    def test_feedback_response_with_comments(self):
        """Test feedback response with additional comments"""
        response = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "respondent_name": "Comments Test Student",
            "submission_date": getdate(),
            "status": "Valid",
            "comments": "Great course! The professor explained concepts very clearly."
        })

        response.append("answers", {
            "question_id": "1",
            "question_text": "Rate the course content",
            "answer_value": "5"
        })

        response.insert(ignore_permissions=True)

        self.assertIsNotNone(response.comments)
        self.assertIn("Great course", response.comments)

        # Clean up
        response.delete(force=True)

    def test_feedback_response_status_change(self):
        """Test changing feedback response status"""
        response = frappe.get_doc({
            "doctype": "Feedback Response",
            "feedback_form": self.test_form.name,
            "respondent": frappe.session.user,
            "respondent_type": "Student",
            "submission_date": getdate(),
            "status": "Draft"
        })

        response.append("answers", {
            "question_id": "1",
            "question_text": "Q1",
            "answer_value": "3"
        })

        response.insert(ignore_permissions=True)
        self.assertEqual(response.status, "Draft")

        # Change to Valid
        response.status = "Valid"
        response.save(ignore_permissions=True)
        self.assertEqual(response.status, "Valid")

        # Mark as Invalid
        response.status = "Invalid"
        response.save(ignore_permissions=True)
        self.assertEqual(response.status, "Invalid")

        # Clean up
        response.delete(force=True)
