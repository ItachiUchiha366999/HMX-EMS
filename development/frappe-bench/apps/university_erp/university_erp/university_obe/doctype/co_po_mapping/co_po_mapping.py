# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class COPOMapping(Document):
    def validate(self):
        self.validate_course_program()
        self.validate_mappings()
        self.calculate_statistics()

    def before_submit(self):
        self.status = "Approved"
        if not self.approval_date:
            self.approval_date = frappe.utils.today()

    def on_cancel(self):
        self.status = "Cancelled"

    def validate_course_program(self):
        """Validate that course belongs to the selected program"""
        # Check if course is in program's course list
        program_courses = frappe.get_all(
            "Program Course",
            filters={"parent": self.program},
            pluck="course"
        )
        if self.course not in program_courses:
            frappe.msgprint(
                _("Note: Course {0} may not be directly linked to Program {1}").format(
                    self.course, self.program
                ),
                indicator="orange"
            )

    def validate_mappings(self):
        """Validate mapping entries"""
        if not self.mapping_table:
            frappe.throw(_("Please add at least one CO-PO mapping entry"))

        # Check for duplicate CO-PO pairs
        seen = set()
        for row in self.mapping_table:
            key = (row.course_outcome, row.program_outcome)
            if key in seen:
                frappe.throw(
                    _("Duplicate mapping found: {0} to {1}").format(
                        row.co_code or row.course_outcome,
                        row.po_code or row.program_outcome
                    )
                )
            seen.add(key)

    def calculate_statistics(self):
        """Calculate mapping statistics"""
        if not self.mapping_table:
            return

        total = 0
        strong = 0
        moderate = 0
        weak = 0
        none = 0
        total_correlation = 0

        for row in self.mapping_table:
            level = self.get_correlation_number(row.correlation_level)
            total += 1

            if level == 3:
                strong += 1
            elif level == 2:
                moderate += 1
            elif level == 1:
                weak += 1
            else:
                none += 1

            total_correlation += level

        self.total_mappings = total
        self.strong_correlations = strong
        self.moderate_correlations = moderate
        self.weak_correlations = weak
        self.no_correlations = none
        self.avg_correlation = round(total_correlation / total, 2) if total > 0 else 0

    def get_correlation_number(self, correlation_level):
        """Extract numeric correlation level from select value"""
        if not correlation_level:
            return 0
        # Handle formats like "3 - High" or just "3"
        try:
            return int(str(correlation_level).split(" ")[0])
        except (ValueError, IndexError):
            return 0


@frappe.whitelist()
def generate_mapping_matrix(course, program):
    """Generate empty CO-PO mapping matrix for a course and program"""
    # Get all COs for the course
    cos = frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "co_number", "co_code", "co_statement"],
        order_by="co_number"
    )

    # Get all POs for the program
    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": program, "status": "Active"},
        fields=["name", "po_number", "po_code", "po_title", "is_pso"],
        order_by="is_pso, po_number"
    )

    if not cos:
        frappe.throw(_("No active Course Outcomes found for course {0}").format(course))

    if not pos:
        frappe.throw(_("No active Program Outcomes found for program {0}").format(program))

    # Generate mapping entries (CO x PO matrix)
    mapping_entries = []
    for co in cos:
        for po in pos:
            mapping_entries.append({
                "course_outcome": co.name,
                "co_code": co.co_code,
                "co_statement": co.co_statement,
                "program_outcome": po.name,
                "po_code": po.po_code,
                "po_title": po.po_title,
                "correlation_level": "0 - No Correlation"
            })

    return {
        "course_outcomes": cos,
        "program_outcomes": pos,
        "mapping_entries": mapping_entries
    }


@frappe.whitelist()
def get_co_po_matrix(course=None, program=None, academic_term=None):
    """Get CO-PO mapping matrix with actual correlations"""
    filters = {"docstatus": 1}  # Only submitted mappings
    if course:
        filters["course"] = course
    if program:
        filters["program"] = program
    if academic_term:
        filters["academic_term"] = academic_term

    mappings = frappe.get_all(
        "CO PO Mapping",
        filters=filters,
        fields=["name", "course", "program", "academic_term"]
    )

    if not mappings:
        return {"matrix": [], "cos": [], "pos": []}

    # Get the most recent mapping
    mapping = mappings[0]

    # Get mapping entries
    entries = frappe.get_all(
        "CO PO Mapping Entry",
        filters={"parent": mapping.name},
        fields=["course_outcome", "co_code", "program_outcome", "po_code", "correlation_level"]
    )

    # Build matrix structure
    cos = list(set((e.course_outcome, e.co_code) for e in entries))
    pos = list(set((e.program_outcome, e.po_code) for e in entries))

    # Sort
    cos = sorted(cos, key=lambda x: x[1] if x[1] else "")
    pos = sorted(pos, key=lambda x: x[1] if x[1] else "")

    # Create matrix
    matrix = {}
    for entry in entries:
        co_key = entry.co_code or entry.course_outcome
        po_key = entry.po_code or entry.program_outcome
        if co_key not in matrix:
            matrix[co_key] = {}
        # Extract numeric level
        try:
            level = int(str(entry.correlation_level).split(" ")[0])
        except (ValueError, IndexError):
            level = 0
        matrix[co_key][po_key] = level

    return {
        "mapping_name": mapping.name,
        "course": mapping.course,
        "program": mapping.program,
        "academic_term": mapping.academic_term,
        "cos": [{"name": c[0], "code": c[1]} for c in cos],
        "pos": [{"name": p[0], "code": p[1]} for p in pos],
        "matrix": matrix
    }


@frappe.whitelist()
def get_po_coverage(program, academic_term=None):
    """Get PO coverage across all courses in a program"""
    filters = {"program": program, "docstatus": 1}
    if academic_term:
        filters["academic_term"] = academic_term

    mappings = frappe.get_all(
        "CO PO Mapping",
        filters=filters,
        fields=["name", "course"]
    )

    if not mappings:
        return {"pos": [], "coverage": {}}

    # Get all POs for the program
    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": program, "status": "Active"},
        fields=["name", "po_code", "po_title", "is_pso"],
        order_by="is_pso, po_number"
    )

    # Calculate coverage for each PO
    po_coverage = {}
    for po in pos:
        po_key = po.po_code or po.name
        po_coverage[po_key] = {
            "name": po.name,
            "code": po.po_code,
            "title": po.po_title,
            "is_pso": po.is_pso,
            "courses": [],
            "total_correlations": 0,
            "avg_correlation": 0
        }

    # Process each mapping
    for mapping in mappings:
        entries = frappe.get_all(
            "CO PO Mapping Entry",
            filters={"parent": mapping.name},
            fields=["program_outcome", "po_code", "correlation_level"]
        )

        course_po_levels = {}
        for entry in entries:
            po_key = entry.po_code or entry.program_outcome
            try:
                level = int(str(entry.correlation_level).split(" ")[0])
            except (ValueError, IndexError):
                level = 0

            if po_key not in course_po_levels:
                course_po_levels[po_key] = []
            if level > 0:
                course_po_levels[po_key].append(level)

        # Update coverage
        for po_key, levels in course_po_levels.items():
            if po_key in po_coverage and levels:
                avg_level = sum(levels) / len(levels)
                po_coverage[po_key]["courses"].append({
                    "course": mapping.course,
                    "mapping": mapping.name,
                    "avg_correlation": round(avg_level, 2)
                })
                po_coverage[po_key]["total_correlations"] += len(levels)

    # Calculate overall average for each PO
    for po_key, data in po_coverage.items():
        if data["courses"]:
            total = sum(c["avg_correlation"] for c in data["courses"])
            data["avg_correlation"] = round(total / len(data["courses"]), 2)

    return {
        "program": program,
        "academic_term": academic_term,
        "pos": pos,
        "coverage": po_coverage
    }
