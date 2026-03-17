# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class COAttainment(Document):
    def validate(self):
        self.validate_weights()
        self.calculate_direct_attainment()
        self.calculate_indirect_attainment()
        self.calculate_final_attainment()
        self.calculate_overall_summary()
        self.status = "Calculated"

    def before_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"

    def validate_weights(self):
        """Ensure direct + indirect weights = 100%"""
        total_weight = (self.direct_weight or 70) + (self.indirect_weight or 30)
        if abs(total_weight - 100) > 0.01:
            frappe.throw(_("Direct weight and Indirect weight must sum to 100%"))

    def calculate_direct_attainment(self):
        """Calculate attainment percentage and level for each direct assessment"""
        for row in self.direct_attainment_table or []:
            if row.total_students and row.total_students > 0:
                row.attainment_percent = (row.students_above_target / row.total_students) * 100
                row.attainment_level = self.get_attainment_level(row.attainment_percent)
            else:
                row.attainment_percent = 0
                row.attainment_level = 0

        # Calculate average direct attainment
        if self.direct_attainment_table:
            levels = [row.attainment_level for row in self.direct_attainment_table if row.attainment_level]
            self.avg_direct_attainment = sum(levels) / len(levels) if levels else 0
        else:
            self.avg_direct_attainment = 0

    def calculate_indirect_attainment(self):
        """Calculate attainment from survey data"""
        for row in self.indirect_attainment_table or []:
            if row.avg_rating and row.avg_rating > 0:
                # Convert 5-point scale to percentage
                row.attainment_percent = (row.avg_rating / 5) * 100
                row.attainment_level = self.get_attainment_level(row.attainment_percent)
            else:
                row.attainment_percent = 0
                row.attainment_level = 0

        # Calculate average indirect attainment
        if self.indirect_attainment_table:
            levels = [row.attainment_level for row in self.indirect_attainment_table if row.attainment_level]
            self.avg_indirect_attainment = sum(levels) / len(levels) if levels else 0
        else:
            self.avg_indirect_attainment = 0

    def calculate_final_attainment(self):
        """Calculate final weighted attainment for each CO"""
        # Group direct attainments by CO
        direct_by_co = {}
        for row in self.direct_attainment_table or []:
            co = row.course_outcome
            if co not in direct_by_co:
                direct_by_co[co] = []
            direct_by_co[co].append(row.attainment_level)

        # Group indirect attainments by CO
        indirect_by_co = {}
        for row in self.indirect_attainment_table or []:
            co = row.course_outcome
            if co not in indirect_by_co:
                indirect_by_co[co] = []
            indirect_by_co[co].append(row.attainment_level)

        # Calculate final for each CO in final table
        for row in self.final_attainment_table or []:
            co = row.course_outcome

            # Average direct attainment for this CO
            if co in direct_by_co and direct_by_co[co]:
                row.direct_attainment = sum(direct_by_co[co]) / len(direct_by_co[co])
            else:
                row.direct_attainment = 0

            # Average indirect attainment for this CO
            if co in indirect_by_co and indirect_by_co[co]:
                row.indirect_attainment = sum(indirect_by_co[co]) / len(indirect_by_co[co])
            else:
                row.indirect_attainment = 0

            # Calculate weighted final
            direct_weight = (row.direct_weight or self.direct_weight or 70) / 100
            indirect_weight = (row.indirect_weight or self.indirect_weight or 30) / 100

            row.final_attainment = (
                row.direct_attainment * direct_weight +
                row.indirect_attainment * indirect_weight
            )

            # Check if target achieved
            target = row.target_attainment or 60
            target_level = self.get_attainment_level(target)
            row.achieved = 1 if row.final_attainment >= target_level else 0
            row.gap = round(target_level - row.final_attainment, 2)

    def calculate_overall_summary(self):
        """Calculate overall CO attainment summary"""
        if not self.final_attainment_table:
            return

        total_cos = len(self.final_attainment_table)
        achieved_cos = sum(1 for row in self.final_attainment_table if row.achieved)
        total_attainment = sum(row.final_attainment for row in self.final_attainment_table)

        self.total_cos = total_cos
        self.cos_achieved = achieved_cos
        self.overall_attainment = round(total_attainment / total_cos, 2) if total_cos > 0 else 0
        self.attainment_percentage = round((achieved_cos / total_cos) * 100, 2) if total_cos > 0 else 0

        # Update total students from first direct assessment if not set
        if not self.total_students and self.direct_attainment_table:
            for row in self.direct_attainment_table:
                if row.total_students:
                    self.total_students = row.total_students
                    break

    def get_attainment_level(self, percentage):
        """Convert percentage to attainment level (0-3)"""
        if percentage >= 70:
            return 3  # High
        elif percentage >= 60:
            return 2  # Medium
        elif percentage >= 50:
            return 1  # Low
        else:
            return 0  # Not achieved


@frappe.whitelist()
def calculate_co_attainment(course, academic_term, student_group=None):
    """Calculate CO attainment from assessment results"""
    # Get all COs for the course
    cos = frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "co_number", "co_code", "co_statement", "target_attainment"]
    )

    if not cos:
        frappe.throw(_("No Course Outcomes found for course {0}").format(course))

    # Get assessment results (if available through Assessment Result DocType)
    # This would integrate with the Examinations module

    return {
        "course": course,
        "academic_term": academic_term,
        "course_outcomes": cos,
        "message": "Use manual entry for attainment data or integrate with Assessment Result"
    }


@frappe.whitelist()
def get_co_attainment_summary(course=None, academic_term=None, academic_year=None):
    """Get CO attainment summary for reporting"""
    filters = {"docstatus": 1}
    if course:
        filters["course"] = course
    if academic_term:
        filters["academic_term"] = academic_term
    if academic_year:
        filters["academic_year"] = academic_year

    attainments = frappe.get_all(
        "CO Attainment",
        filters=filters,
        fields=[
            "name", "course", "course_name", "academic_term",
            "overall_attainment", "cos_achieved", "total_cos",
            "attainment_percentage", "calculation_date"
        ],
        order_by="calculation_date desc"
    )

    return attainments


@frappe.whitelist()
def populate_cos_for_attainment(course):
    """Get COs to populate attainment table"""
    cos = frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "co_code", "co_statement", "target_attainment"],
        order_by="co_number"
    )

    final_entries = []
    for co in cos:
        final_entries.append({
            "course_outcome": co.name,
            "co_code": co.co_code,
            "co_statement": co.co_statement,
            "target_attainment": co.target_attainment or 60,
            "direct_weight": 70,
            "indirect_weight": 30
        })

    return final_entries
