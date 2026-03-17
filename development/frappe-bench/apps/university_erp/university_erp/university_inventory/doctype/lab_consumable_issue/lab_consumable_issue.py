# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class LabConsumableIssue(Document):
    """Lab Consumable Issue - Issue consumables from lab stores"""

    def validate(self):
        """Validate consumable issue"""
        self.validate_items()
        self.set_item_details()
        self.calculate_totals()

    def validate_items(self):
        """Validate items"""
        if not self.items:
            frappe.throw(_("Please add items to issue"))

        for item in self.items:
            if flt(item.qty) <= 0:
                frappe.throw(_("Quantity must be greater than 0 for item {0}").format(
                    item.item_code
                ))

    def set_item_details(self):
        """Set item details and calculate amounts"""
        for item in self.items:
            item_doc = frappe.get_cached_doc("Inventory Item", item.item_code)
            item.item_name = item_doc.item_name
            item.uom = item_doc.unit_of_measure

            # Get rate from item master if not set
            if not item.rate:
                item.rate = item_doc.valuation_rate or item_doc.standard_rate or 0

            item.amount = flt(item.qty) * flt(item.rate)

    def calculate_totals(self):
        """Calculate totals"""
        self.total_qty = sum(flt(item.qty) for item in self.items)
        self.total_value = sum(flt(item.amount) for item in self.items)

    def on_submit(self):
        """Create stock entry for material issue"""
        self.create_stock_entry()

    def on_cancel(self):
        """Cancel related stock entry"""
        self.cancel_stock_entry()

    def create_stock_entry(self):
        """Create stock entry for material issue"""
        # Get default warehouse from lab
        lab = frappe.get_doc("University Laboratory", self.lab)
        default_warehouse = None

        # Try to find lab store warehouse
        warehouses = frappe.get_all(
            "Warehouse",
            filters={"warehouse_type": "Lab Store", "is_group": 0},
            fields=["name"]
        )
        if warehouses:
            default_warehouse = warehouses[0].name

        se = frappe.new_doc("Stock Entry")
        se.entry_type = "Material Issue"
        se.posting_date = self.issue_date
        se.reference_doctype = self.doctype
        se.reference_name = self.name

        for item in self.items:
            warehouse = item.warehouse or default_warehouse
            if not warehouse:
                frappe.throw(_("Please set warehouse for item {0}").format(item.item_code))

            se.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.rate,
                "s_warehouse": warehouse
            })

        se.insert()
        se.submit()

        frappe.msgprint(_("Stock Entry {0} created").format(se.name))

    def cancel_stock_entry(self):
        """Cancel related stock entry"""
        stock_entries = frappe.get_all(
            "Stock Entry",
            filters={
                "reference_doctype": self.doctype,
                "reference_name": self.name,
                "docstatus": 1
            }
        )

        for se in stock_entries:
            doc = frappe.get_doc("Stock Entry", se.name)
            doc.cancel()


@frappe.whitelist()
def get_lab_consumable_summary(lab, from_date, to_date):
    """Get consumable usage summary for a lab"""
    return frappe.db.sql("""
        SELECT
            lci.item_code,
            lci.item_name,
            SUM(lci.qty) as total_qty,
            SUM(lci.amount) as total_value
        FROM `tabLab Consumable Issue Item` lci
        INNER JOIN `tabLab Consumable Issue` lc ON lc.name = lci.parent
        WHERE lc.lab = %s
        AND lc.issue_date BETWEEN %s AND %s
        AND lc.docstatus = 1
        GROUP BY lci.item_code
        ORDER BY total_qty DESC
    """, (lab, from_date, to_date), as_dict=True)
