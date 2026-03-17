"""
External Examiner DocType Controller

Manages external examiners for practical examinations and paper evaluation.
"""

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, today


class ExternalExaminer(Document):
    """
    External Examiner management
    """

    def validate(self):
        self.validate_email()
        self.validate_empanelment()

    def validate_email(self):
        """Validate email uniqueness"""
        if self.email:
            existing = frappe.db.get_value(
                "External Examiner",
                {"email": self.email, "name": ["!=", self.name]}
            )
            if existing:
                frappe.throw(_("External Examiner with email {0} already exists").format(self.email))

    def validate_empanelment(self):
        """Check empanelment validity"""
        if self.empanelment_valid_till:
            if getdate(self.empanelment_valid_till) < getdate(today()):
                self.status = "Inactive"
                frappe.msgprint(_("Empanelment has expired. Status set to Inactive."))

    def update_assignment_stats(self):
        """Update assignment statistics"""
        self.times_assigned = (self.times_assigned or 0) + 1
        self.last_assignment_date = today()
        self.db_set("times_assigned", self.times_assigned)
        self.db_set("last_assignment_date", self.last_assignment_date)

    def update_rating(self, rating: float):
        """
        Update average rating

        Args:
            rating: New rating (1-5)
        """
        if self.average_rating:
            # Calculate weighted average
            total_ratings = self.times_assigned or 1
            current_sum = self.average_rating * (total_ratings - 1)
            self.average_rating = (current_sum + rating) / total_ratings
        else:
            self.average_rating = rating

        self.db_set("average_rating", self.average_rating)


@frappe.whitelist()
def get_available_examiners(specialization: str = None, course: str = None):
    """
    Get available external examiners

    Args:
        specialization: Filter by specialization
        course: Filter by course

    Returns:
        List of available examiners
    """
    filters = {
        "status": "Active"
    }

    if specialization:
        filters["specialization"] = ["like", f"%{specialization}%"]

    examiners = frappe.get_all(
        "External Examiner",
        filters=filters,
        fields=["name", "examiner_name", "organization", "specialization",
                "experience_years", "average_rating", "times_assigned"]
    )

    # Filter by course if provided
    if course:
        course_code = frappe.db.get_value("Course", course, "course_code")
        if course_code:
            examiners = [e for e in examiners
                        if not e.courses_can_evaluate or
                        course_code in (e.courses_can_evaluate or "")]

    return examiners
