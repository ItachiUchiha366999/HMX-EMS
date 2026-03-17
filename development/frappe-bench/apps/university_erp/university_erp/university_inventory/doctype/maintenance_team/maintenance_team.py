# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MaintenanceTeam(Document):
    """Maintenance Team - Team of employees for asset maintenance"""

    def validate(self):
        """Validate maintenance team"""
        self.validate_team_lead()
        self.validate_members()

    def validate_team_lead(self):
        """Ensure team lead is active if set"""
        if self.team_lead:
            employee = frappe.get_doc("Employee", self.team_lead)
            if employee.status != "Active":
                frappe.throw(_("Team Lead {0} is not an active employee").format(
                    self.team_lead
                ))

    def validate_members(self):
        """Validate team members"""
        employees = []
        for member in self.members:
            if member.employee in employees:
                frappe.throw(_("Duplicate employee {0} in team members").format(
                    member.employee
                ))
            employees.append(member.employee)

    def get_team_members(self):
        """Get list of team member employees"""
        return [member.employee for member in self.members]
