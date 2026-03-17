# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SurveyTemplate(Document):
    def validate(self):
        self.validate_default_template()

    def validate_default_template(self):
        """Ensure only one default template per survey type"""
        if self.is_default:
            # Clear other defaults for this survey type
            frappe.db.sql("""
                UPDATE `tabSurvey Template`
                SET is_default = 0
                WHERE survey_type = %s AND name != %s AND is_default = 1
            """, (self.survey_type, self.name))


@frappe.whitelist()
def get_survey_templates(survey_type=None, program=None):
    """Get available survey templates"""
    filters = {"is_active": 1}
    if survey_type:
        filters["survey_type"] = survey_type

    templates = frappe.get_all(
        "Survey Template",
        filters=filters,
        fields=["name", "template_name", "survey_type", "program", "is_default"],
        order_by="is_default desc, template_name"
    )

    # Filter by program if specified
    if program:
        templates = [t for t in templates if not t.program or t.program == program]

    return templates
