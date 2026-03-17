# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, nowtime


class StockEntry(Document):
    """Stock Entry - Stock movement document"""

    def validate(self):
        """Validate stock entry"""
        self.validate_items()
        self.validate_warehouses()
        self.set_item_details()
        self.calculate_totals()

    def validate_items(self):
        """Validate items in stock entry"""
        if not self.items:
            frappe.throw(_("Please add items to the stock entry"))

        for item in self.items:
            if flt(item.qty) <= 0:
                frappe.throw(_("Quantity must be greater than 0 for item {0}").format(item.item_code))

            # Validate item is active
            if frappe.db.get_value("Inventory Item", item.item_code, "is_active") == 0:
                frappe.throw(_("Item {0} is not active").format(item.item_code))

    def validate_warehouses(self):
        """Validate warehouses based on entry type"""
        for item in self.items:
            # Set default warehouses if not specified
            if not item.s_warehouse and self.from_warehouse:
                item.s_warehouse = self.from_warehouse
            if not item.t_warehouse and self.to_warehouse:
                item.t_warehouse = self.to_warehouse

            # Validate based on entry type
            if self.entry_type in ["Material Issue"]:
                if not item.s_warehouse:
                    frappe.throw(
                        _("Source Warehouse is required for Material Issue for item {0}").format(item.item_code)
                    )
            elif self.entry_type in ["Material Receipt", "Opening Stock"]:
                if not item.t_warehouse:
                    frappe.throw(
                        _("Target Warehouse is required for {0} for item {1}").format(self.entry_type, item.item_code)
                    )
            elif self.entry_type == "Material Transfer":
                if not item.s_warehouse or not item.t_warehouse:
                    frappe.throw(
                        _("Both Source and Target Warehouse are required for Material Transfer for item {0}").format(
                            item.item_code
                        )
                    )

    def set_item_details(self):
        """Set item details from item master"""
        for item in self.items:
            item_details = frappe.get_cached_doc("Inventory Item", item.item_code)
            item.item_name = item_details.item_name
            item.uom = item_details.unit_of_measure

            # Set rate from item master if not specified
            if not item.rate:
                item.rate = item_details.valuation_rate or item_details.standard_rate or 0

            # Calculate amount
            item.amount = flt(item.qty) * flt(item.rate)

            # Get actual qty at source warehouse
            if item.s_warehouse:
                item.actual_qty = self.get_actual_qty(item.item_code, item.s_warehouse)

    def get_actual_qty(self, item_code, warehouse):
        """Get actual quantity at warehouse"""
        qty = frappe.db.sql("""
            SELECT SUM(actual_qty) as qty
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s AND warehouse = %s AND is_cancelled = 0
        """, (item_code, warehouse))[0][0] or 0

        return flt(qty)

    def calculate_totals(self):
        """Calculate totals"""
        self.total_qty = sum(flt(item.qty) for item in self.items)
        self.total_amount = sum(flt(item.amount) for item in self.items)

    def on_submit(self):
        """On submit - create stock ledger entries"""
        self.update_stock_ledger()
        self.update_item_stock_info()

    def on_cancel(self):
        """On cancel - reverse stock ledger entries"""
        self.update_stock_ledger(reverse=True)
        self.update_item_stock_info()

    def update_stock_ledger(self, reverse=False):
        """Create or reverse stock ledger entries"""
        for item in self.items:
            # Source warehouse - outward
            if item.s_warehouse:
                self.create_stock_ledger_entry(
                    item,
                    item.s_warehouse,
                    -flt(item.qty) if not reverse else flt(item.qty),
                    is_outward=True
                )

            # Target warehouse - inward
            if item.t_warehouse:
                self.create_stock_ledger_entry(
                    item,
                    item.t_warehouse,
                    flt(item.qty) if not reverse else -flt(item.qty),
                    is_outward=False
                )

    def create_stock_ledger_entry(self, item, warehouse, qty, is_outward=False):
        """Create a stock ledger entry"""
        sle = frappe.get_doc({
            "doctype": "Stock Ledger Entry",
            "item_code": item.item_code,
            "warehouse": warehouse,
            "posting_date": self.posting_date,
            "posting_time": self.posting_time or nowtime(),
            "voucher_type": "Stock Entry",
            "voucher_no": self.name,
            "actual_qty": qty,
            "incoming_rate": flt(item.rate) if not is_outward else 0,
            "outgoing_rate": flt(item.rate) if is_outward else 0,
            "valuation_rate": flt(item.rate),
            "stock_value": flt(qty) * flt(item.rate),
            "batch_no": item.batch_no,
            "serial_no": item.serial_no,
            "is_cancelled": 0
        })
        sle.insert(ignore_permissions=True)

        # Update qty after transaction
        sle.update_qty_after_transaction()
        sle.save(ignore_permissions=True)

    def update_item_stock_info(self):
        """Update stock info on inventory items"""
        item_codes = list(set(item.item_code for item in self.items))
        for item_code in item_codes:
            try:
                item = frappe.get_doc("Inventory Item", item_code)
                item.update_stock_info()
                item.save(ignore_permissions=True)
            except Exception:
                pass


@frappe.whitelist()
def get_items_from_purchase_order(purchase_order):
    """Get pending items from purchase order"""
    po = frappe.get_doc("Purchase Order", purchase_order)

    items = []
    for item in po.items:
        pending_qty = flt(item.qty) - flt(item.received_qty)
        if pending_qty > 0:
            items.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": pending_qty,
                "uom": item.uom,
                "rate": item.rate,
                "amount": pending_qty * flt(item.rate),
                "t_warehouse": item.warehouse
            })

    return items


@frappe.whitelist()
def get_items_from_material_request(material_request):
    """Get pending items from material request"""
    mr = frappe.get_doc("Material Request", material_request)

    items = []
    for item in mr.items:
        pending_qty = flt(item.qty) - flt(item.ordered_qty)
        if pending_qty > 0:
            items.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": pending_qty,
                "uom": item.uom,
                "s_warehouse": item.warehouse if mr.material_request_type == "Material Transfer" else None,
                "t_warehouse": item.warehouse if mr.material_request_type != "Material Transfer" else None
            })

    return items


@frappe.whitelist()
def make_stock_entry(source_doctype, source_name, entry_type):
    """Create stock entry from source document"""
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.entry_type = entry_type

    if source_doctype == "Purchase Order":
        stock_entry.purchase_order = source_name
        items = get_items_from_purchase_order(source_name)
        stock_entry.to_warehouse = frappe.db.get_value("Purchase Order", source_name, "set_warehouse")
    elif source_doctype == "Material Request":
        stock_entry.material_request = source_name
        items = get_items_from_material_request(source_name)
        mr_type = frappe.db.get_value("Material Request", source_name, "material_request_type")
        if mr_type == "Material Transfer":
            stock_entry.entry_type = "Material Transfer"

    for item in items:
        stock_entry.append("items", item)

    return stock_entry
