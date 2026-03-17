# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProgramOutcome(Document):
    def validate(self):
        self.validate_unique_po_number()
        self.set_po_code()
        self.validate_peo_mapping()

    def validate_unique_po_number(self):
        """Ensure PO number is unique within the program"""
        existing = frappe.db.exists(
            "Program Outcome",
            {
                "program": self.program,
                "po_number": self.po_number,
                "name": ("!=", self.name),
                "status": ("!=", "Archived")
            }
        )
        if existing:
            frappe.throw(f"PO {self.po_number} already exists for program {self.program}")

    def set_po_code(self):
        """Set PO code if not provided"""
        if not self.po_code:
            prefix = "PSO" if self.is_pso else "PO"
            self.po_code = f"{prefix}{self.po_number}"

    def validate_peo_mapping(self):
        """Validate PEO mapping entries belong to the same program"""
        for mapping in self.peo_mapping:
            peo_program = frappe.db.get_value("Program Educational Objective", mapping.peo, "program")
            if peo_program != self.program:
                frappe.throw(f"PEO {mapping.peo} does not belong to program {self.program}")


@frappe.whitelist()
def get_program_outcomes(program, include_pso=True):
    """Get all POs for a program"""
    filters = {"program": program, "status": "Active"}
    if not include_pso:
        filters["is_pso"] = 0

    return frappe.get_all(
        "Program Outcome",
        filters=filters,
        fields=[
            "name", "po_number", "po_code", "po_title", "po_statement",
            "is_pso", "nba_attribute", "bloom_level", "target_attainment", "current_attainment"
        ],
        order_by="po_number"
    )


@frappe.whitelist()
def get_nba_graduate_attributes():
    """Get list of NBA Graduate Attributes"""
    return [
        {"value": "Engineering Knowledge", "label": "1. Engineering Knowledge"},
        {"value": "Problem Analysis", "label": "2. Problem Analysis"},
        {"value": "Design/Development of Solutions", "label": "3. Design/Development of Solutions"},
        {"value": "Conduct Investigations", "label": "4. Conduct Investigations"},
        {"value": "Modern Tool Usage", "label": "5. Modern Tool Usage"},
        {"value": "Engineer and Society", "label": "6. Engineer and Society"},
        {"value": "Environment and Sustainability", "label": "7. Environment and Sustainability"},
        {"value": "Ethics", "label": "8. Ethics"},
        {"value": "Individual and Team Work", "label": "9. Individual and Team Work"},
        {"value": "Communication", "label": "10. Communication"},
        {"value": "Project Management and Finance", "label": "11. Project Management and Finance"},
        {"value": "Life-long Learning", "label": "12. Life-long Learning"}
    ]
