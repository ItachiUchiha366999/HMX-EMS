# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class InventoryItem(Document):
    """Inventory Item - Master item for stock management"""

    def autoname(self):
        """Generate item code after naming series"""
        if self.naming_series:
            from frappe.model.naming import make_autoname
            self.name = make_autoname(self.naming_series, doc=self)
            self.item_code = self.name

    def validate(self):
        """Validate the inventory item"""
        self.validate_reorder_settings()
        self.set_defaults_from_group()

    def validate_reorder_settings(self):
        """Validate reorder level and quantity"""
        if self.reorder_level and not self.reorder_quantity:
            frappe.throw(_("Reorder Quantity is required when Reorder Level is set"))

        if self.minimum_stock_level and self.reorder_level:
            if flt(self.minimum_stock_level) > flt(self.reorder_level):
                frappe.throw(
                    _("Minimum Stock Level cannot be greater than Reorder Level")
                )

    def set_defaults_from_group(self):
        """Set default values from item group if not specified"""
        if self.item_group:
            from university_erp.university_erp.doctype.inventory_item_group.inventory_item_group import (
                get_item_group_defaults
            )
            defaults = get_item_group_defaults(self.item_group)

            if not self.expense_account and defaults.get("expense_account"):
                self.expense_account = defaults["expense_account"]

            if not self.default_warehouse and defaults.get("warehouse"):
                self.default_warehouse = defaults["warehouse"]

    def before_save(self):
        """Actions before saving"""
        self.update_stock_info()

    def update_stock_info(self):
        """Update current stock and value from stock ledger"""
        stock = self.get_stock_balance()
        self.current_stock = flt(stock.get("qty", 0))
        self.total_stock_value = flt(stock.get("value", 0))

        if self.current_stock > 0:
            self.valuation_rate = flt(self.total_stock_value / self.current_stock, 2)

    def get_stock_balance(self, warehouse=None):
        """Get current stock balance"""
        filters = {"item_code": self.item_code or self.name}
        warehouse_condition = ""
        if warehouse:
            filters["warehouse"] = warehouse
            warehouse_condition = "AND warehouse = %(warehouse)s"

        stock = frappe.db.sql("""
            SELECT
                SUM(actual_qty) as qty,
                SUM(stock_value) as value
            FROM `tabStock Ledger Entry`
            WHERE item_code = %(item_code)s
            {warehouse_condition}
            AND is_cancelled = 0
        """.format(warehouse_condition=warehouse_condition), filters, as_dict=True)

        return {
            "qty": flt(stock[0].qty) if stock else 0,
            "value": flt(stock[0].value) if stock else 0
        }

    def on_trash(self):
        """Validate before deletion"""
        if frappe.db.exists("Stock Ledger Entry", {"item_code": self.name}):
            frappe.throw(
                _("Cannot delete item {0} as it has stock transactions").format(self.name)
            )


@frappe.whitelist()
def get_item_details(item_code, warehouse=None):
    """Get item details for forms"""
    item = frappe.get_cached_doc("Inventory Item", item_code)

    details = {
        "item_name": item.item_name,
        "item_group": item.item_group,
        "unit_of_measure": item.unit_of_measure,
        "uom": item.unit_of_measure,
        "description": item.description,
        "standard_rate": item.standard_rate,
        "last_purchase_rate": item.last_purchase_rate,
        "valuation_rate": item.valuation_rate,
        "default_warehouse": item.default_warehouse,
        "expense_account": item.expense_account,
        "is_active": item.is_active
    }

    # Add stock balance if warehouse specified
    if warehouse:
        stock = item.get_stock_balance(warehouse)
        details["actual_qty"] = stock.get("qty", 0)
        details["stock_value"] = stock.get("value", 0)

    return details


@frappe.whitelist()
def get_items_below_reorder_level():
    """Get all items below reorder level"""
    items = frappe.get_all(
        "Inventory Item",
        filters={
            "is_active": 1,
            "maintain_stock": 1,
            "reorder_level": [">", 0]
        },
        fields=[
            "name", "item_code", "item_name", "item_group",
            "current_stock", "reorder_level", "reorder_quantity",
            "minimum_stock_level", "default_warehouse", "default_supplier"
        ]
    )

    low_stock_items = []
    for item in items:
        if flt(item.current_stock) <= flt(item.reorder_level):
            item["stock_status"] = "Critical" if flt(item.current_stock) <= flt(item.minimum_stock_level) else "Low"
            item["qty_to_order"] = flt(item.reorder_quantity) or (flt(item.reorder_level) - flt(item.current_stock))
            low_stock_items.append(item)

    return low_stock_items


@frappe.whitelist()
def update_item_stock_info(item_code):
    """Update stock info for an item"""
    item = frappe.get_doc("Inventory Item", item_code)
    item.update_stock_info()
    item.save(ignore_permissions=True)
    return item.current_stock
