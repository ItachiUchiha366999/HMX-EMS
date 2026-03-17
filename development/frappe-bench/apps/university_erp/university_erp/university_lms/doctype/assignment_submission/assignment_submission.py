# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class AssignmentSubmission(Document):
    def validate(self):
        self.validate_submission()
        self.check_late_submission()
        self.calculate_final_marks()

    def validate_submission(self):
        """Validate submission against assignment rules"""
        assignment = frappe.get_doc("LMS Assignment", self.assignment)

        # Check if assignment accepts submissions
        if not assignment.is_available():
            frappe.throw(_("This assignment is not yet available for submission"))

        if not assignment.accepts_late_submission():
            frappe.throw(_("This assignment no longer accepts submissions"))

        # Check submission type requirements
        if assignment.submission_type == "File Upload" and not self.submission_files:
            frappe.throw(_("File upload is required for this assignment"))

        if assignment.submission_type == "Online Text" and not self.submission_text:
            frappe.throw(_("Online text submission is required for this assignment"))

        # Check max attempts
        existing_attempts = frappe.db.count("Assignment Submission", {
            "assignment": self.assignment,
            "student": self.student,
            "name": ["!=", self.name or ""]
        })

        if existing_attempts >= assignment.max_attempts:
            frappe.throw(_("Maximum submission attempts ({0}) reached").format(assignment.max_attempts))

        self.attempt_number = existing_attempts + 1

    def check_late_submission(self):
        """Check if submission is late and calculate penalty"""
        assignment = frappe.get_doc("LMS Assignment", self.assignment)

        submission_time = get_datetime(self.submission_date or now_datetime())
        due_date = get_datetime(assignment.due_date)

        if submission_time > due_date:
            self.is_late = 1
            if assignment.late_submission_allowed and assignment.late_penalty_percent:
                self.late_penalty = assignment.late_penalty_percent
        else:
            self.is_late = 0
            self.late_penalty = 0

    def calculate_final_marks(self):
        """Calculate final marks after late penalty"""
        if self.marks_obtained is not None:
            penalty_amount = (self.marks_obtained * (self.late_penalty or 0)) / 100
            self.final_marks = max(0, self.marks_obtained - penalty_amount)
        else:
            self.final_marks = None

    def after_insert(self):
        """Update assignment statistics"""
        assignment = frappe.get_doc("LMS Assignment", self.assignment)
        assignment.update_statistics()

    def on_update(self):
        """Update assignment statistics when graded"""
        if self.has_value_changed("status") and self.status == "Graded":
            assignment = frappe.get_doc("LMS Assignment", self.assignment)
            assignment.update_statistics()


@frappe.whitelist()
def submit_assignment(assignment, student, submission_text=None, files=None, comments=None):
    """Submit an assignment"""
    # Check if submission already exists
    existing = frappe.db.exists("Assignment Submission", {
        "assignment": assignment,
        "student": student,
        "status": ["!=", "Resubmission Required"]
    })

    if existing:
        frappe.throw(_("You have already submitted this assignment"))

    submission = frappe.get_doc({
        "doctype": "Assignment Submission",
        "assignment": assignment,
        "student": student,
        "submission_text": submission_text,
        "student_comments": comments,
        "submission_date": now_datetime()
    })

    # Add files if provided
    if files:
        for file_data in files:
            submission.append("submission_files", {
                "file": file_data.get("file"),
                "file_name": file_data.get("file_name"),
                "file_size": file_data.get("file_size"),
                "uploaded_on": now_datetime()
            })

    submission.insert()

    return {
        "message": _("Assignment submitted successfully"),
        "submission": submission.name
    }


@frappe.whitelist()
def grade_submission(submission_name, marks_obtained, feedback=None, rubric_scores=None):
    """Grade an assignment submission"""
    submission = frappe.get_doc("Assignment Submission", submission_name)

    submission.marks_obtained = marks_obtained
    submission.feedback = feedback
    submission.status = "Graded"
    submission.graded_by = frappe.session.user
    submission.graded_on = now_datetime()

    # Update rubric scores if provided
    if rubric_scores:
        submission.rubric_scores = []
        for score in rubric_scores:
            submission.append("rubric_scores", {
                "criterion": score.get("criterion"),
                "max_points": score.get("max_points"),
                "points_awarded": score.get("points_awarded"),
                "feedback": score.get("feedback")
            })

    submission.save()

    return {
        "message": _("Submission graded successfully"),
        "final_marks": submission.final_marks
    }
