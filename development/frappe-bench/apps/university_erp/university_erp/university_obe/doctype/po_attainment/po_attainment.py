# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class POAttainment(Document):
    def validate(self):
        self.validate_weights()
        self.calculate_direct_attainment()
        self.calculate_indirect_attainment()
        self.calculate_final_attainment()
        self.calculate_overall_summary()
        self.calculate_compliance_scores()
        self.status = "Calculated"

    def before_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"

    def validate_weights(self):
        """Ensure direct + indirect weights = 100%"""
        total_weight = (self.direct_weight or 80) + (self.indirect_weight or 20)
        if abs(total_weight - 100) > 0.01:
            frappe.throw(_("Direct weight and Indirect weight must sum to 100%"))

    def calculate_direct_attainment(self):
        """Calculate direct PO attainment from CO attainments"""
        if not self.direct_po_attainment:
            return

        for row in self.direct_po_attainment:
            # Calculate attainment level from weighted attainment
            if row.weighted_attainment:
                row.attainment_level = row.weighted_attainment
                row.attainment_percent = self.level_to_percent(row.weighted_attainment)

        # Calculate average
        levels = [row.attainment_level for row in self.direct_po_attainment if row.attainment_level]
        self.avg_direct_attainment = sum(levels) / len(levels) if levels else 0

    def calculate_indirect_attainment(self):
        """Calculate indirect PO attainment from surveys"""
        if not self.indirect_po_attainment:
            return

        for row in self.indirect_po_attainment:
            if row.avg_rating and row.avg_rating > 0:
                row.attainment_percent = (row.avg_rating / 5) * 100
                row.attainment_level = self.get_attainment_level(row.attainment_percent)

        # Calculate average
        levels = [row.attainment_level for row in self.indirect_po_attainment if row.attainment_level]
        self.avg_indirect_attainment = sum(levels) / len(levels) if levels else 0

    def calculate_final_attainment(self):
        """Calculate final weighted PO attainment"""
        if not self.final_po_attainment:
            return

        # Build lookup for direct attainment by PO
        direct_by_po = {}
        for row in self.direct_po_attainment or []:
            direct_by_po[row.program_outcome] = row.attainment_level or 0

        # Build lookup for indirect attainment by PO
        indirect_by_po = {}
        for row in self.indirect_po_attainment or []:
            po = row.program_outcome
            if po not in indirect_by_po:
                indirect_by_po[po] = []
            indirect_by_po[po].append(row.attainment_level or 0)

        # Calculate final for each PO
        for row in self.final_po_attainment:
            po = row.program_outcome

            # Direct attainment
            row.direct_attainment = direct_by_po.get(po, 0)

            # Indirect attainment (average if multiple surveys)
            if po in indirect_by_po and indirect_by_po[po]:
                row.indirect_attainment = sum(indirect_by_po[po]) / len(indirect_by_po[po])
            else:
                row.indirect_attainment = 0

            # Calculate weighted final
            direct_weight = (row.direct_weight or self.direct_weight or 80) / 100
            indirect_weight = (row.indirect_weight or self.indirect_weight or 20) / 100

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
        """Calculate overall PO/PSO attainment summary"""
        if not self.final_po_attainment:
            return

        pos = [row for row in self.final_po_attainment if not row.is_pso]
        psos = [row for row in self.final_po_attainment if row.is_pso]

        # PO statistics
        self.total_pos = len(pos)
        self.pos_achieved = sum(1 for row in pos if row.achieved)

        # PSO statistics
        self.total_psos = len(psos)
        self.psos_achieved = sum(1 for row in psos if row.achieved)

        # Overall attainment
        all_entries = self.final_po_attainment
        if all_entries:
            total_attainment = sum(row.final_attainment for row in all_entries)
            self.overall_attainment = round(total_attainment / len(all_entries), 2) if all_entries else 0

    def calculate_compliance_scores(self):
        """Calculate NBA and NAAC compliance scores"""
        if not self.final_po_attainment:
            return

        # NBA compliance: based on PO1-PO12 achievement (12 Graduate Attributes)
        pos = [row for row in self.final_po_attainment if not row.is_pso]
        if pos:
            achieved = sum(1 for row in pos if row.achieved)
            self.nba_compliance_score = round((achieved / len(pos)) * 100, 2)

        # NAAC compliance: based on overall attainment level
        # Level 3 (70%+) = 100%, Level 2 (60-70%) = 75%, Level 1 (50-60%) = 50%
        if self.overall_attainment >= 2.5:
            self.naac_compliance_score = 100
        elif self.overall_attainment >= 2:
            self.naac_compliance_score = 75
        elif self.overall_attainment >= 1.5:
            self.naac_compliance_score = 50
        else:
            self.naac_compliance_score = 25

    def get_attainment_level(self, percentage):
        """Convert percentage to attainment level (0-3)"""
        if percentage >= 70:
            return 3
        elif percentage >= 60:
            return 2
        elif percentage >= 50:
            return 1
        else:
            return 0

    def level_to_percent(self, level):
        """Convert attainment level to approximate percentage"""
        if level >= 3:
            return 85
        elif level >= 2:
            return 65
        elif level >= 1:
            return 55
        else:
            return 0


@frappe.whitelist()
def calculate_po_attainment(program, academic_year):
    """Calculate PO attainment from CO attainments and CO-PO mappings"""
    # Get all POs for the program
    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": program, "status": "Active"},
        fields=["name", "po_number", "po_code", "po_title", "is_pso", "target_attainment"],
        order_by="is_pso, po_number"
    )

    if not pos:
        frappe.throw(_("No Program Outcomes found for program {0}").format(program))

    # Get all courses in the program
    program_courses = frappe.get_all(
        "Program Course",
        filters={"parent": program},
        pluck="course"
    )

    # Get CO attainments for these courses
    co_attainments = frappe.get_all(
        "CO Attainment",
        filters={
            "course": ["in", program_courses],
            "academic_year": academic_year,
            "docstatus": 1
        },
        fields=["name", "course", "overall_attainment"]
    )

    # Get CO-PO mappings
    co_po_mappings = frappe.get_all(
        "CO PO Mapping",
        filters={
            "program": program,
            "docstatus": 1
        },
        fields=["name", "course"]
    )

    # Calculate PO attainment for each PO
    po_attainment_data = []
    for po in pos:
        # Find courses contributing to this PO through CO-PO mapping
        contributing_courses = []
        weighted_sum = 0
        total_weight = 0

        for mapping in co_po_mappings:
            # Get mapping entries for this PO
            entries = frappe.get_all(
                "CO PO Mapping Entry",
                filters={
                    "parent": mapping.name,
                    "program_outcome": po.name
                },
                fields=["correlation_level"]
            )

            for entry in entries:
                try:
                    level = int(str(entry.correlation_level).split(" ")[0])
                except (ValueError, IndexError):
                    level = 0

                if level > 0:
                    # Find corresponding CO attainment
                    for ca in co_attainments:
                        if ca.course == mapping.course:
                            weighted_sum += ca.overall_attainment * level
                            total_weight += level
                            if mapping.course not in contributing_courses:
                                contributing_courses.append(mapping.course)
                            break

        weighted_attainment = weighted_sum / total_weight if total_weight > 0 else 0

        po_attainment_data.append({
            "program_outcome": po.name,
            "po_code": po.po_code,
            "po_title": po.po_title,
            "is_pso": po.is_pso,
            "contributing_courses": len(contributing_courses),
            "weighted_attainment": round(weighted_attainment, 2),
            "target_attainment": po.target_attainment or 60
        })

    return {
        "program": program,
        "academic_year": academic_year,
        "program_outcomes": pos,
        "po_attainment_data": po_attainment_data
    }


@frappe.whitelist()
def get_po_attainment_summary(program=None, academic_year=None):
    """Get PO attainment summary for reporting"""
    filters = {"docstatus": 1}
    if program:
        filters["program"] = program
    if academic_year:
        filters["academic_year"] = academic_year

    attainments = frappe.get_all(
        "PO Attainment",
        filters=filters,
        fields=[
            "name", "program", "program_name", "academic_year",
            "overall_attainment", "pos_achieved", "total_pos",
            "psos_achieved", "total_psos", "nba_compliance_score",
            "naac_compliance_score", "calculation_date"
        ],
        order_by="calculation_date desc"
    )

    return attainments


@frappe.whitelist()
def generate_attainment_report(program, academic_year):
    """Generate comprehensive attainment report for a program"""
    # Get PO attainment
    po_attainment = frappe.get_all(
        "PO Attainment",
        filters={
            "program": program,
            "academic_year": academic_year,
            "docstatus": 1
        },
        fields=["*"]
    )

    if not po_attainment:
        return {"message": "No submitted PO Attainment found for the selected criteria"}

    attainment = po_attainment[0]

    # Get final PO entries
    final_entries = frappe.get_all(
        "PO Final Entry",
        filters={"parent": attainment.name},
        fields=["*"],
        order_by="is_pso, po_code"
    )

    # Get CO attainments for courses in this program
    program_courses = frappe.get_all(
        "Program Course",
        filters={"parent": program},
        pluck="course"
    )

    co_attainments = frappe.get_all(
        "CO Attainment",
        filters={
            "course": ["in", program_courses],
            "academic_year": academic_year,
            "docstatus": 1
        },
        fields=["name", "course", "course_name", "overall_attainment", "cos_achieved", "total_cos"]
    )

    return {
        "program": program,
        "academic_year": academic_year,
        "po_attainment": attainment,
        "final_entries": final_entries,
        "co_attainments": co_attainments,
        "summary": {
            "overall_attainment": attainment.overall_attainment,
            "pos_achieved": attainment.pos_achieved,
            "total_pos": attainment.total_pos,
            "psos_achieved": attainment.psos_achieved,
            "total_psos": attainment.total_psos,
            "nba_compliance": attainment.nba_compliance_score,
            "naac_compliance": attainment.naac_compliance_score
        }
    }
