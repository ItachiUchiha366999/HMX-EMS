# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, today


class GrievanceType(Document):
    """Grievance Type DocType for categorizing grievances"""

    def validate(self):
        """Validate grievance type settings"""
        self.validate_escalation_matrix()
        self.validate_sla_days()

    def validate_escalation_matrix(self):
        """Ensure escalation levels are sequential and unique"""
        if not self.escalation_matrix:
            return

        levels = [rule.level for rule in self.escalation_matrix]
        if len(levels) != len(set(levels)):
            frappe.throw(_("Escalation levels must be unique"))

        # Check levels are sequential starting from 2 (level 1 is default assignee)
        sorted_levels = sorted(levels)
        for i, level in enumerate(sorted_levels):
            if level != i + 2:
                frappe.throw(_("Escalation levels must be sequential starting from 2"))

    def validate_sla_days(self):
        """Validate SLA days is positive"""
        if self.sla_days and self.sla_days < 1:
            frappe.throw(_("SLA days must be at least 1"))

    def get_default_sla_date(self):
        """Get expected resolution date based on SLA"""
        return add_days(today(), self.sla_days or 7)

    def get_escalation_assignee(self, level):
        """Get assignee for a specific escalation level"""
        for rule in self.escalation_matrix:
            if rule.level == level:
                return rule.assignee
        return None

    def get_max_escalation_level(self):
        """Get the maximum escalation level defined"""
        if not self.escalation_matrix:
            return 1
        return max(rule.level for rule in self.escalation_matrix)
