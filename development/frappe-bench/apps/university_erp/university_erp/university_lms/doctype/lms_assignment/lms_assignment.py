# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class LMSAssignment(Document):
    def validate(self):
        self.validate_dates()
        self.validate_rubric()

    def validate_dates(self):
        """Validate assignment dates"""
        if get_datetime(self.available_from) > get_datetime(self.due_date):
            frappe.throw(_("Due Date cannot be before Available From date"))

        if self.late_submission_allowed and self.late_submission_deadline:
            if get_datetime(self.late_submission_deadline) < get_datetime(self.due_date):
                frappe.throw(_("Late Deadline cannot be before Due Date"))

    def validate_rubric(self):
        """Validate grading rubric total"""
        if self.grading_rubric:
            total_weight = sum(item.weight or 0 for item in self.grading_rubric)
            if total_weight > 0 and abs(total_weight - 100) > 0.01:
                frappe.msgprint(_("Rubric weights should total 100%. Current total: {0}%").format(total_weight))

    def on_submit(self):
        """Notify enrolled students"""
        pass  # Can implement email notification here

    def update_statistics(self):
        """Update assignment statistics"""
        submissions = frappe.get_all("Assignment Submission",
            filters={"assignment": self.name},
            fields=["status", "final_marks"]
        )

        self.total_submissions = len(submissions)
        graded = [s for s in submissions if s.status == "Graded"]
        self.graded_submissions = len(graded)

        if graded:
            self.average_score = sum(s.final_marks or 0 for s in graded) / len(graded)

        self.db_update()

    def is_available(self):
        """Check if assignment is currently available"""
        if self.docstatus != 1:
            return False

        current_time = now_datetime()
        return get_datetime(self.available_from) <= current_time

    def is_past_due(self):
        """Check if assignment is past due date"""
        return now_datetime() > get_datetime(self.due_date)

    def accepts_late_submission(self):
        """Check if assignment still accepts submissions"""
        if not self.is_past_due():
            return True

        if self.late_submission_allowed and self.late_submission_deadline:
            return now_datetime() <= get_datetime(self.late_submission_deadline)

        return False


@frappe.whitelist()
def get_student_assignments(lms_course=None, student=None):
    """Get assignments for a student"""
    filters = {"docstatus": 1}

    if lms_course:
        filters["lms_course"] = lms_course

    assignments = frappe.get_all("LMS Assignment",
        filters=filters,
        fields=["name", "title", "lms_course", "due_date", "max_marks",
                "assignment_type", "available_from"]
    )

    if student:
        for assignment in assignments:
            submission = frappe.db.get_value("Assignment Submission",
                {"assignment": assignment.name, "student": student},
                ["name", "status", "final_marks", "submission_date"], as_dict=True
            )
            assignment["submission"] = submission

    return assignments
