# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate, get_datetime


class FeedbackForm(Document):
    """
    Feedback Form DocType for creating surveys and feedback collection forms

    Features:
    - Multiple question types support
    - Target audience filtering
    - Anonymous response support
    - Automatic status management
    - Response statistics
    """

    def validate(self):
        """Validate feedback form"""
        self.validate_dates()
        self.validate_questions()
        self.update_status_from_dates()

    def before_save(self):
        """Actions before saving"""
        self.set_default_thank_you_message()

    def validate_dates(self):
        """Validate start and end dates"""
        if self.start_date and self.end_date:
            start = get_datetime(self.start_date)
            end = get_datetime(self.end_date)

            if end <= start:
                frappe.throw(_("End date must be after start date"))

    def validate_questions(self):
        """Validate that form has questions"""
        if self.status == "Active" and not self.questions:
            frappe.throw(_("Please add at least one question before activating the form"))

    def update_status_from_dates(self):
        """Auto-update status based on dates"""
        if self.status in ["Draft", "Archived"]:
            return

        now = now_datetime()
        start = get_datetime(self.start_date) if self.start_date else None
        end = get_datetime(self.end_date) if self.end_date else None

        if start and end:
            if now < start:
                self.status = "Scheduled"
            elif start <= now <= end:
                if self.status not in ["Paused"]:
                    self.status = "Active"
            elif now > end:
                self.status = "Closed"

    def set_default_thank_you_message(self):
        """Set default thank you message if not provided"""
        if not self.thank_you_message:
            self.thank_you_message = "<p>Thank you for your valuable feedback!</p>"

    @frappe.whitelist()
    def activate_form(self):
        """Activate the feedback form"""
        if not self.questions:
            frappe.throw(_("Please add questions before activating"))

        self.status = "Active"
        self.save()
        return self.status

    @frappe.whitelist()
    def pause_form(self):
        """Pause the feedback form"""
        if self.status != "Active":
            frappe.throw(_("Only active forms can be paused"))

        self.status = "Paused"
        self.save()
        return self.status

    @frappe.whitelist()
    def resume_form(self):
        """Resume a paused feedback form"""
        if self.status != "Paused":
            frappe.throw(_("Only paused forms can be resumed"))

        self.status = "Active"
        self.save()
        return self.status

    @frappe.whitelist()
    def close_form(self):
        """Close the feedback form"""
        self.status = "Closed"
        self.save()
        return self.status

    def update_statistics(self):
        """Update response statistics"""
        self.total_responses = frappe.db.count("Feedback Response", {
            "feedback_form": self.name,
            "status": ["in", ["Submitted", "Valid"]]
        })

        # Calculate response rate
        target_count = self.get_target_count()
        if target_count > 0:
            self.response_rate = (self.total_responses / target_count) * 100
        else:
            self.response_rate = 0

        self.save()

    def get_target_count(self):
        """Get expected number of respondents"""
        if self.target_audience == "Students":
            if self.courses:
                course_list = [c.course for c in self.courses]
                return frappe.db.count("Course Enrollment",
                    filters={"course": ["in", course_list]}
                )
            elif self.programs:
                program_list = [p.program for p in self.programs]
                return frappe.db.count("Program Enrollment",
                    filters={"program": ["in", program_list]}
                )
            else:
                return frappe.db.count("Student", filters={"enabled": 1})
        elif self.target_audience == "Faculty":
            return frappe.db.count("Instructor", filters={"status": "Active"})

        return 0

    def is_accessible_to_student(self, student):
        """Check if a student can access this feedback form"""
        if self.status != "Active":
            return False

        if self.target_audience not in ["Students", "All"]:
            return False

        # Check program filter
        if self.programs:
            program_list = [p.program for p in self.programs]
            student_program = frappe.db.get_value("Student", student, "program")
            if student_program not in program_list:
                return False

        # Check course filter
        if self.courses:
            course_list = [c.course for c in self.courses]
            enrolled_courses = frappe.get_all("Course Enrollment",
                filters={"student": student},
                pluck="course"
            )
            if not any(c in course_list for c in enrolled_courses):
                return False

        return True

    def has_student_responded(self, student):
        """Check if student has already responded"""
        return frappe.db.exists("Feedback Response", {
            "feedback_form": self.name,
            "student": student,
            "status": ["in", ["Submitted", "Valid"]]
        })

    def get_questions_for_display(self, randomize=None):
        """Get questions for display, optionally randomized"""
        questions = list(self.questions)

        if randomize is None:
            randomize = self.randomize_questions

        if randomize:
            import random
            random.shuffle(questions)

        return questions
