# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProgramEducationalObjective(Document):
    def validate(self):
        self.validate_unique_peo_number()

    def validate_unique_peo_number(self):
        """Ensure PEO number is unique within the program"""
        existing = frappe.db.exists(
            "Program Educational Objective",
            {
                "program": self.program,
                "peo_number": self.peo_number,
                "name": ("!=", self.name),
                "status": ("!=", "Archived")
            }
        )
        if existing:
            frappe.throw(f"PEO {self.peo_number} already exists for program {self.program}")


@frappe.whitelist()
def get_program_peos(program):
    """Get all PEOs for a program"""
    return frappe.get_all(
        "Program Educational Objective",
        filters={"program": program, "status": "Active"},
        fields=["name", "peo_number", "peo_statement", "bloom_level", "industry_relevance"],
        order_by="peo_number"
    )
