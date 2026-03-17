# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, flt


class AccreditationCycle(Document):
    def validate(self):
        self.validate_dates()
        self.validate_scope()
        self.calculate_progress()

    def validate_dates(self):
        """Validate date fields"""
        if self.data_period_start and self.data_period_end:
            if getdate(self.data_period_start) > getdate(self.data_period_end):
                frappe.throw(_("Data Period Start cannot be after Data Period End"))

        if self.valid_from and self.valid_until:
            if getdate(self.valid_from) > getdate(self.valid_until):
                frappe.throw(_("Valid From cannot be after Valid Until"))

    def validate_scope(self):
        """Validate scope type and related fields"""
        if self.scope_type == "Program Level" and not self.programs:
            frappe.throw(_("Please select at least one Program for Program Level scope"))

        if self.scope_type == "Department Level" and not self.departments:
            frappe.throw(_("Please select at least one Department for Department Level scope"))

    def before_save(self):
        """Set up default criteria for NAAC if not set"""
        if self.accreditation_body == "NAAC" and not self.criteria:
            self.setup_naac_criteria()

    def setup_naac_criteria(self):
        """Set up 7 NAAC criteria"""
        naac_criteria = [
            {"criterion_number": "1", "criterion_name": "Curricular Aspects", "weightage": 100, "max_score": 100},
            {"criterion_number": "2", "criterion_name": "Teaching-Learning and Evaluation", "weightage": 200, "max_score": 200},
            {"criterion_number": "3", "criterion_name": "Research, Innovations and Extension", "weightage": 150, "max_score": 150},
            {"criterion_number": "4", "criterion_name": "Infrastructure and Learning Resources", "weightage": 100, "max_score": 100},
            {"criterion_number": "5", "criterion_name": "Student Support and Progression", "weightage": 100, "max_score": 100},
            {"criterion_number": "6", "criterion_name": "Governance, Leadership and Management", "weightage": 100, "max_score": 100},
            {"criterion_number": "7", "criterion_name": "Institutional Values and Best Practices", "weightage": 100, "max_score": 100}
        ]

        for criterion in naac_criteria:
            self.append("criteria", criterion)

    def calculate_progress(self):
        """Calculate overall progress based on criteria status"""
        if not self.criteria:
            self.overall_progress = 0
            return

        total_criteria = len(self.criteria)
        completed = 0

        for criterion in self.criteria:
            if criterion.data_status == "Completed":
                completed += 0.8
            elif criterion.data_status == "Verified":
                completed += 1
            elif criterion.data_status == "In Progress":
                completed += 0.5

        self.overall_progress = (completed / total_criteria) * 100 if total_criteria > 0 else 0

    def get_criterion_summary(self):
        """Get summary of all criteria"""
        summary = {
            "total": len(self.criteria),
            "not_started": 0,
            "in_progress": 0,
            "completed": 0,
            "verified": 0,
            "total_score": 0,
            "max_score": 0
        }

        for criterion in self.criteria:
            if criterion.data_status == "Not Started":
                summary["not_started"] += 1
            elif criterion.data_status == "In Progress":
                summary["in_progress"] += 1
            elif criterion.data_status == "Completed":
                summary["completed"] += 1
            elif criterion.data_status == "Verified":
                summary["verified"] += 1

            summary["total_score"] += flt(criterion.score)
            summary["max_score"] += flt(criterion.max_score)

        return summary


@frappe.whitelist()
def get_accreditation_progress(accreditation_cycle):
    """Get progress details for an accreditation cycle"""
    cycle = frappe.get_doc("Accreditation Cycle", accreditation_cycle)
    return cycle.get_criterion_summary()
