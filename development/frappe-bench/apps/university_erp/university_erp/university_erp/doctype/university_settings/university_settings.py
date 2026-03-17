import frappe
from frappe import _
from frappe.model.document import Document


class UniversitySettings(Document):
    """University Settings - Single DocType for university-wide configuration"""

    def validate(self):
        """Validate settings"""
        self.validate_grading_settings()
        self.validate_fee_settings()

    def validate_grading_settings(self):
        """Validate grading settings"""
        if self.passing_grade_points and (self.passing_grade_points < 0 or self.passing_grade_points > 10):
            frappe.throw(_("Passing Grade Points must be between 0 and 10"))

    def validate_fee_settings(self):
        """Validate fee settings"""
        if self.enable_late_fee:
            if not self.late_fee_percentage or self.late_fee_percentage <= 0:
                frappe.throw(_("Late Fee Percentage must be greater than 0"))

            if not self.late_fee_period_days or self.late_fee_period_days <= 0:
                frappe.throw(_("Late Fee Period must be greater than 0 days"))


def get_university_settings():
    """Get University Settings (helper function)"""
    if not frappe.db.exists("University Settings"):
        return None

    return frappe.get_single("University Settings")


def get_enrollment_number_format():
    """Get enrollment number format from settings"""
    settings = get_university_settings()
    if settings and settings.enrollment_number_format:
        return settings.enrollment_number_format
    return "UNI-{YYYY}-{#####}"


def get_application_number_format():
    """Get application number format from settings"""
    settings = get_university_settings()
    if settings and settings.application_number_format:
        return settings.application_number_format
    return "APP-{YYYY}-{#####}"
