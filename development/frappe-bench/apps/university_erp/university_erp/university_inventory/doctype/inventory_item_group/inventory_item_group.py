# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet


class InventoryItemGroup(NestedSet):
    """Inventory Item Group - Hierarchical categorization of inventory items"""

    nsm_parent_field = "parent_inventory_item_group"

    def validate(self):
        """Validate the item group"""
        self.validate_parent()

    def validate_parent(self):
        """Validate parent group settings"""
        if self.parent_inventory_item_group:
            parent = frappe.get_doc("Inventory Item Group", self.parent_inventory_item_group)
            if not parent.is_group:
                frappe.throw(
                    _("Parent {0} must be a group").format(self.parent_inventory_item_group)
                )

    def on_update(self):
        """Handle tree structure updates"""
        NestedSet.on_update(self)
        self.validate_one_root()

    def on_trash(self):
        """Validate before deletion"""
        NestedSet.on_trash(self, allow_root_deletion=True)
        self.validate_no_items()
        self.validate_no_children()

    def validate_no_items(self):
        """Check if group has items"""
        if frappe.db.exists("Inventory Item", {"item_group": self.name}):
            frappe.throw(
                _("Cannot delete {0} as it has linked items").format(self.name)
            )

    def validate_no_children(self):
        """Check if group has children"""
        if frappe.db.exists("Inventory Item Group", {"parent_inventory_item_group": self.name}):
            frappe.throw(
                _("Cannot delete {0} as it has child groups").format(self.name)
            )


def get_item_group_defaults(item_group):
    """Get default expense account and warehouse from item group hierarchy"""
    defaults = {
        "expense_account": None,
        "warehouse": None
    }

    current_group = item_group

    while current_group:
        group_doc = frappe.get_cached_doc("Inventory Item Group", current_group)

        if not defaults["expense_account"] and group_doc.default_expense_account:
            defaults["expense_account"] = group_doc.default_expense_account

        if not defaults["warehouse"] and group_doc.default_warehouse:
            defaults["warehouse"] = group_doc.default_warehouse

        if defaults["expense_account"] and defaults["warehouse"]:
            break

        current_group = group_doc.parent_inventory_item_group

    return defaults


@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False, **filters):
    """Return children of parent for tree view"""
    if is_root:
        parent = ""

    item_groups = frappe.get_all(
        "Inventory Item Group",
        filters={"parent_inventory_item_group": parent or ""},
        fields=["name as value", "is_group as expandable", "group_name"],
        order_by="group_name asc"
    )

    return item_groups


@frappe.whitelist()
def add_node():
    """Add a new node to the tree"""
    from frappe.desk.treeview import make_tree_args

    args = make_tree_args(**frappe.form_dict)

    if args.get("is_root"):
        args["parent_inventory_item_group"] = None

    doc = frappe.get_doc(args)
    doc.insert()

    return doc.name
