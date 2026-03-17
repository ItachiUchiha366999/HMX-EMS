# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, date_diff


class ResearchProject(Document):
    def validate(self):
        self.validate_dates()

    def validate_dates(self):
        """Validate project dates"""
        if self.start_date and self.expected_end_date:
            if getdate(self.start_date) > getdate(self.expected_end_date):
                frappe.throw(_("Expected End Date cannot be before Start Date"))

        if self.start_date and self.actual_end_date:
            if getdate(self.start_date) > getdate(self.actual_end_date):
                frappe.throw(_("Actual End Date cannot be before Start Date"))

    def calculate_progress(self):
        """Calculate project progress percentage"""
        if not self.start_date or not self.expected_end_date:
            return 0

        total_days = date_diff(self.expected_end_date, self.start_date)
        if total_days <= 0:
            return 0

        elapsed_days = date_diff(frappe.utils.today(), self.start_date)
        progress = min(100, max(0, (elapsed_days / total_days) * 100))

        return round(progress, 2)


@frappe.whitelist()
def get_active_projects(principal_investigator=None, department=None, project_type=None):
    """Get active research projects"""
    filters = {"status": ["in", ["Proposed", "Approved", "Ongoing"]]}

    if principal_investigator:
        filters["principal_investigator"] = principal_investigator

    if department:
        filters["department"] = department

    if project_type:
        filters["project_type"] = project_type

    projects = frappe.get_all("Research Project",
        filters=filters,
        fields=["name", "project_title", "project_type", "principal_investigator",
                "pi_name", "status", "sanctioned_amount", "start_date", "expected_end_date"]
    )

    return projects
