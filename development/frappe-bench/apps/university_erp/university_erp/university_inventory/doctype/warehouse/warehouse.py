# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet


class Warehouse(NestedSet):
    """Warehouse - Hierarchical storage location management"""

    nsm_parent_field = "parent_warehouse"

    def validate(self):
        """Validate the warehouse"""
        self.validate_parent()

    def validate_parent(self):
        """Validate parent warehouse settings"""
        if self.parent_warehouse:
            parent = frappe.get_doc("Warehouse", self.parent_warehouse)
            if not parent.is_group:
                frappe.throw(
                    _("Parent {0} must be a group").format(self.parent_warehouse)
                )

    def on_update(self):
        """Handle tree structure updates"""
        NestedSet.on_update(self)
        self.validate_one_root()

    def on_trash(self):
        """Validate before deletion"""
        NestedSet.on_trash(self, allow_root_deletion=True)
        self.validate_no_stock()
        self.validate_no_children()

    def validate_no_stock(self):
        """Check if warehouse has stock"""
        if frappe.db.exists("Stock Ledger Entry", {"warehouse": self.name}):
            frappe.throw(
                _("Cannot delete {0} as it has stock transactions").format(self.name)
            )

    def validate_no_children(self):
        """Check if warehouse has children"""
        if frappe.db.exists("Warehouse", {"parent_warehouse": self.name}):
            frappe.throw(
                _("Cannot delete {0} as it has child warehouses").format(self.name)
            )


def get_warehouse_account(warehouse):
    """Get account linked to warehouse"""
    warehouse_doc = frappe.get_cached_doc("Warehouse", warehouse)
    if warehouse_doc.account:
        return warehouse_doc.account

    # Check parent warehouse hierarchy
    if warehouse_doc.parent_warehouse:
        return get_warehouse_account(warehouse_doc.parent_warehouse)

    return None


@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False, **filters):
    """Return children of parent for tree view"""
    if is_root:
        parent = ""

    warehouses = frappe.get_all(
        "Warehouse",
        filters={"parent_warehouse": parent or ""},
        fields=["name as value", "is_group as expandable", "warehouse_name", "warehouse_type"],
        order_by="warehouse_name asc"
    )

    return warehouses


@frappe.whitelist()
def add_node():
    """Add a new node to the tree"""
    from frappe.desk.treeview import make_tree_args

    args = make_tree_args(**frappe.form_dict)

    if args.get("is_root"):
        args["parent_warehouse"] = None

    doc = frappe.get_doc(args)
    doc.insert()

    return doc.name


@frappe.whitelist()
def get_warehouse_stock(warehouse):
    """Get stock summary for a warehouse"""
    from frappe.utils import flt

    stock_data = frappe.db.sql("""
        SELECT
            item_code,
            SUM(actual_qty) as qty,
            SUM(stock_value) as value
        FROM `tabStock Ledger Entry`
        WHERE warehouse = %s AND is_cancelled = 0
        GROUP BY item_code
        HAVING SUM(actual_qty) > 0
    """, warehouse, as_dict=True)

    total_qty = sum(flt(d.qty) for d in stock_data)
    total_value = sum(flt(d.value) for d in stock_data)

    return {
        "items": stock_data,
        "total_qty": total_qty,
        "total_value": total_value,
        "item_count": len(stock_data)
    }
