# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UOM(Document):
    """Unit of Measure DocType for Inventory Management"""

    def validate(self):
        """Validate UOM"""
        # Ensure UOM name is properly formatted
        if self.uom_name:
            self.uom_name = self.uom_name.strip()

    def before_rename(self, old_name, new_name, merge=False):
        """Handle rename to update all references"""
        if merge:
            # Check if new UOM exists and handle merge
            pass


def get_default_uoms():
    """Return list of default UOMs to be created"""
    return [
        {"uom_name": "Nos", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Kg", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Gram", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Ltr", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Ml", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Mtr", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Cm", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Box", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Pack", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Set", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Pair", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Dozen", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Sqm", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Sqft", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Rft", "must_be_whole_number": 0, "enabled": 1},
        {"uom_name": "Ream", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Bottle", "must_be_whole_number": 1, "enabled": 1},
        {"uom_name": "Unit", "must_be_whole_number": 1, "enabled": 1}
    ]


def create_default_uoms():
    """Create default UOMs if they don't exist"""
    for uom_data in get_default_uoms():
        if not frappe.db.exists("UOM", uom_data["uom_name"]):
            uom = frappe.get_doc({
                "doctype": "UOM",
                **uom_data
            })
            uom.insert(ignore_permissions=True)
    frappe.db.commit()
