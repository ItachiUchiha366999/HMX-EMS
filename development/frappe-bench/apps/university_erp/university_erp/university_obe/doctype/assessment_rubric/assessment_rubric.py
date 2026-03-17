"""
Assessment Rubric DocType Controller

Defines evaluation rubrics with multiple performance levels
for consistent assessment grading.
"""

import frappe
from frappe.model.document import Document
from frappe import _


class AssessmentRubric(Document):
    """
    Assessment Rubric for standardized evaluation criteria
    """

    def validate(self):
        self.validate_percentages()
        self.set_created_by()

    def validate_percentages(self):
        """Validate that percentage levels are in descending order"""
        levels = [
            (self.level_1_min_percentage, self.level_1_label),
            (self.level_2_min_percentage, self.level_2_label),
            (self.level_3_min_percentage, self.level_3_label),
            (self.level_4_min_percentage, self.level_4_label),
            (self.level_5_min_percentage, self.level_5_label)
        ]

        prev_percentage = 101
        for percentage, label in levels:
            if percentage is not None and percentage >= prev_percentage:
                frappe.throw(_("Percentage levels must be in descending order"))
            prev_percentage = percentage or 0

    def set_created_by(self):
        """Set created_by faculty if not set"""
        if not self.created_by:
            faculty = frappe.db.get_value("Instructor", {"user": frappe.session.user})
            if faculty:
                self.created_by = faculty

    def get_level_for_percentage(self, percentage: float) -> dict:
        """
        Get the rubric level for a given percentage score

        Args:
            percentage: Score percentage

        Returns:
            Dict with level label and description
        """
        levels = [
            (self.level_1_min_percentage, self.level_1_label, self.level_1_description),
            (self.level_2_min_percentage, self.level_2_label, self.level_2_description),
            (self.level_3_min_percentage, self.level_3_label, self.level_3_description),
            (self.level_4_min_percentage, self.level_4_label, self.level_4_description),
            (self.level_5_min_percentage, self.level_5_label, self.level_5_description)
        ]

        for min_pct, label, description in levels:
            if percentage >= (min_pct or 0):
                return {
                    "label": label,
                    "description": description,
                    "min_percentage": min_pct
                }

        return {
            "label": self.level_5_label,
            "description": self.level_5_description,
            "min_percentage": self.level_5_min_percentage
        }


@frappe.whitelist()
def get_rubric_level(rubric_name: str, percentage: float):
    """
    API to get rubric level for a percentage

    Args:
        rubric_name: Rubric document name
        percentage: Score percentage

    Returns:
        Level details
    """
    rubric = frappe.get_doc("Assessment Rubric", rubric_name)
    return rubric.get_level_for_percentage(float(percentage))
