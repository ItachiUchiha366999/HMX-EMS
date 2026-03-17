# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class MaterialRequest(Document):
    """Material Request - Purchase requisition document"""

    def validate(self):
        """Validate material request"""
        self.validate_items()
        self.set_item_details()
        self.set_warehouse()
        self.set_status()

    def validate_items(self):
        """Validate items"""
        if not self.items:
            frappe.throw(_("Please add items to the material request"))

        for item in self.items:
            if flt(item.qty) <= 0:
                frappe.throw(_("Quantity must be greater than 0 for item {0}").format(item.item_code))

    def set_item_details(self):
        """Set item details from item master"""
        for item in self.items:
            item_doc = frappe.get_cached_doc("Inventory Item", item.item_code)
            item.item_name = item_doc.item_name
            item.uom = item_doc.unit_of_measure

            if not item.rate:
                item.rate = item_doc.standard_rate or 0

            item.amount = flt(item.qty) * flt(item.rate)

    def set_warehouse(self):
        """Set warehouse for items if default is set"""
        for item in self.items:
            if not item.warehouse and self.set_warehouse:
                item.warehouse = self.set_warehouse

    def set_status(self):
        """Set status based on ordered/received quantities"""
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            total_qty = sum(flt(item.qty) for item in self.items)
            ordered_qty = sum(flt(item.ordered_qty) for item in self.items)
            received_qty = sum(flt(item.received_qty) for item in self.items)

            if self.material_request_type == "Purchase":
                if ordered_qty >= total_qty:
                    self.status = "Ordered"
                elif ordered_qty > 0:
                    self.status = "Partially Ordered"
                else:
                    self.status = "Pending"
            elif self.material_request_type in ["Material Transfer", "Material Issue"]:
                if received_qty >= total_qty:
                    self.status = "Transferred" if self.material_request_type == "Material Transfer" else "Issued"
                else:
                    self.status = "Pending"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        """On submit actions"""
        self.status = "Pending"

    def on_cancel(self):
        """On cancel actions"""
        self.status = "Cancelled"

    def update_status(self):
        """Update status after linked documents are created"""
        self.set_status()
        self.db_set("status", self.status)


@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
    """Create Purchase Order from Material Request"""
    mr = frappe.get_doc("Material Request", source_name)

    if mr.material_request_type != "Purchase":
        frappe.throw(_("Material Request type must be Purchase"))

    if mr.status in ["Ordered", "Cancelled"]:
        frappe.throw(_("Cannot create Purchase Order for {0} Material Request").format(mr.status))

    po = frappe.new_doc("Purchase Order")
    po.material_request = mr.name
    po.department = mr.department

    for item in mr.items:
        pending_qty = flt(item.qty) - flt(item.ordered_qty)
        if pending_qty > 0:
            po.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": pending_qty,
                "uom": item.uom,
                "rate": item.rate,
                "warehouse": item.warehouse,
                "schedule_date": item.schedule_date or mr.required_by,
                "material_request": mr.name,
                "material_request_item": item.name
            })

    return po


@frappe.whitelist()
def make_stock_entry(source_name, entry_type=None):
    """Create Stock Entry from Material Request"""
    mr = frappe.get_doc("Material Request", source_name)

    if not entry_type:
        entry_type = "Material Issue" if mr.material_request_type == "Material Issue" else "Material Transfer"

    se = frappe.new_doc("Stock Entry")
    se.entry_type = entry_type
    se.material_request = mr.name

    if mr.material_request_type == "Material Transfer":
        se.from_warehouse = mr.set_from_warehouse
        se.to_warehouse = mr.set_warehouse

    for item in mr.items:
        pending_qty = flt(item.qty) - flt(item.received_qty)
        if pending_qty > 0:
            se_item = {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": pending_qty,
                "uom": item.uom
            }

            if entry_type == "Material Issue":
                se_item["s_warehouse"] = item.warehouse or mr.set_from_warehouse
            elif entry_type == "Material Transfer":
                se_item["s_warehouse"] = mr.set_from_warehouse
                se_item["t_warehouse"] = item.warehouse or mr.set_warehouse

            se.append("items", se_item)

    return se
