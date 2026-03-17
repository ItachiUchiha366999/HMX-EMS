# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet


class SupplierGroup(NestedSet):
    """Supplier Group - Hierarchical categorization of suppliers"""

    nsm_parent_field = "parent_supplier_group"

    def on_update(self):
        NestedSet.on_update(self)

    def on_trash(self):
        NestedSet.on_trash(self, allow_root_deletion=True)


@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False, **filters):
    if is_root:
        parent = ""

    return frappe.get_all(
        "Supplier Group",
        filters={"parent_supplier_group": parent or ""},
        fields=["name as value", "is_group as expandable", "supplier_group_name"],
        order_by="supplier_group_name asc"
    )
