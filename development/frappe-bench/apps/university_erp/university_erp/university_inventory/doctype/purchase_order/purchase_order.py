# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PurchaseOrder(Document):
    """Purchase Order - Main purchasing document"""

    def validate(self):
        """Validate purchase order"""
        self.validate_items()
        self.set_item_details()
        self.set_warehouse()
        self.calculate_totals()
        self.calculate_taxes()
        self.set_status()

    def validate_items(self):
        """Validate items"""
        if not self.items:
            frappe.throw(_("Please add items to the purchase order"))

        for item in self.items:
            if flt(item.qty) <= 0:
                frappe.throw(_("Quantity must be greater than 0 for item {0}").format(item.item_code))

            if flt(item.rate) <= 0:
                frappe.throw(_("Rate must be greater than 0 for item {0}").format(item.item_code))

    def set_item_details(self):
        """Set item details from item master"""
        for item in self.items:
            item_doc = frappe.get_cached_doc("Inventory Item", item.item_code)
            item.item_name = item_doc.item_name
            item.uom = item_doc.unit_of_measure
            item.amount = flt(item.qty) * flt(item.rate)

    def set_warehouse(self):
        """Set warehouse for items"""
        for item in self.items:
            if not item.warehouse and self.set_warehouse:
                item.warehouse = self.set_warehouse

    def calculate_totals(self):
        """Calculate totals"""
        self.total_qty = sum(flt(item.qty) for item in self.items)
        self.total = sum(flt(item.amount) for item in self.items)

    def calculate_taxes(self):
        """Calculate taxes and grand total"""
        self.total_taxes_and_charges = 0
        net_total = flt(self.total) - flt(self.discount_amount)
        cumulative_total = net_total

        for tax in self.taxes:
            if tax.charge_type == "Actual":
                tax.tax_amount = flt(tax.rate)
            elif tax.charge_type == "On Net Total":
                tax.tax_amount = net_total * flt(tax.rate) / 100
            elif tax.charge_type == "On Previous Row Amount":
                ref_tax = self.get_tax_by_row_id(tax.row_id)
                tax.tax_amount = flt(ref_tax.tax_amount) * flt(tax.rate) / 100 if ref_tax else 0
            elif tax.charge_type == "On Previous Row Total":
                ref_tax = self.get_tax_by_row_id(tax.row_id)
                tax.tax_amount = flt(ref_tax.total) * flt(tax.rate) / 100 if ref_tax else 0

            if tax.add_deduct_tax == "Deduct":
                cumulative_total -= flt(tax.tax_amount)
                self.total_taxes_and_charges -= flt(tax.tax_amount)
            else:
                cumulative_total += flt(tax.tax_amount)
                self.total_taxes_and_charges += flt(tax.tax_amount)

            tax.total = cumulative_total

        self.grand_total = flt(self.total) - flt(self.discount_amount) + flt(self.total_taxes_and_charges)
        self.rounded_total = round(self.grand_total)

    def get_tax_by_row_id(self, row_id):
        """Get tax row by row id"""
        for idx, tax in enumerate(self.taxes):
            if str(idx + 1) == str(row_id):
                return tax
        return None

    def set_status(self):
        """Set status based on received and billed quantities"""
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            total_qty = sum(flt(item.qty) for item in self.items)
            received_qty = sum(flt(item.received_qty) for item in self.items)
            billed_qty = sum(flt(item.billed_qty) for item in self.items)

            if received_qty >= total_qty and billed_qty >= total_qty:
                self.status = "Completed"
            elif received_qty >= total_qty:
                self.status = "To Bill"
            elif billed_qty >= total_qty:
                self.status = "To Receive"
            else:
                self.status = "To Receive and Bill"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        """On submit actions"""
        self.set_status()
        self.update_material_request()

    def on_cancel(self):
        """On cancel actions"""
        self.status = "Cancelled"
        # Reverse material request updates if needed

    def update_material_request(self):
        """Update ordered quantity in material request"""
        for item in self.items:
            if item.material_request and item.material_request_item:
                mr_item = frappe.get_doc("Material Request Item", item.material_request_item)
                mr_item.ordered_qty = flt(mr_item.ordered_qty) + flt(item.qty)
                mr_item.db_set("ordered_qty", mr_item.ordered_qty)

                # Update material request status
                mr = frappe.get_doc("Material Request", item.material_request)
                mr.update_status()

    def update_status_after_receipt(self):
        """Update status after items are received"""
        self.set_status()
        self.db_set("status", self.status)

        # Update last purchase rate on items
        for item in self.items:
            if flt(item.received_qty) > 0:
                frappe.db.set_value("Inventory Item", item.item_code, "last_purchase_rate", item.rate)


@frappe.whitelist()
def make_stock_entry(source_name):
    """Create Stock Entry (Material Receipt) from Purchase Order"""
    po = frappe.get_doc("Purchase Order", source_name)

    if po.status in ["Completed", "Cancelled", "Closed"]:
        frappe.throw(_("Cannot create receipt for {0} Purchase Order").format(po.status))

    se = frappe.new_doc("Stock Entry")
    se.entry_type = "Material Receipt"
    se.purchase_order = po.name
    se.to_warehouse = po.set_warehouse

    for item in po.items:
        pending_qty = flt(item.qty) - flt(item.received_qty)
        if pending_qty > 0:
            se.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": pending_qty,
                "uom": item.uom,
                "rate": item.rate,
                "t_warehouse": item.warehouse or po.set_warehouse
            })

    return se


@frappe.whitelist()
def close_or_unclose_purchase_order(name, status):
    """Close or unclose purchase order"""
    po = frappe.get_doc("Purchase Order", name)

    if status == "Closed":
        if po.status not in ["To Receive and Bill", "To Bill", "To Receive"]:
            frappe.throw(_("Purchase Order can only be closed when status is To Receive/To Bill"))
        po.db_set("status", "Closed")
    else:
        po.set_status()
        po.db_set("status", po.status)

    return po.status
