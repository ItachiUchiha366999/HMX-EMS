# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, nowdate, now_datetime


class PurchaseReceipt(Document):
    def validate(self):
        self.validate_items()
        self.set_item_details()
        self.calculate_accepted_qty()
        self.calculate_totals()
        self.calculate_taxes()
        self.set_status()

    def validate_items(self):
        """Validate items in the receipt"""
        if not self.items:
            frappe.throw(_("Please add items to receive"))

        for item in self.items:
            if not item.item_code:
                frappe.throw(_("Row {0}: Item Code is required").format(item.idx))

            if flt(item.qty) <= 0:
                frappe.throw(_("Row {0}: Qty must be greater than 0").format(item.idx))

            if not item.warehouse:
                if self.set_warehouse:
                    item.warehouse = self.set_warehouse
                else:
                    frappe.throw(_("Row {0}: Accepted Warehouse is required").format(item.idx))

            # Validate rejected qty
            if flt(item.rejected_qty) > 0 and not item.rejected_warehouse:
                if self.rejected_warehouse:
                    item.rejected_warehouse = self.rejected_warehouse
                else:
                    frappe.throw(
                        _("Row {0}: Rejected Warehouse is required for rejected items").format(item.idx)
                    )

    def set_item_details(self):
        """Set item details from item master"""
        for item in self.items:
            if item.item_code:
                item_doc = frappe.get_cached_doc("Inventory Item", item.item_code)
                if not item.item_name:
                    item.item_name = item_doc.item_name
                if not item.uom:
                    item.uom = item_doc.unit_of_measure
                if not item.stock_uom:
                    item.stock_uom = item_doc.unit_of_measure

    def calculate_accepted_qty(self):
        """Calculate accepted qty = received qty - rejected qty"""
        for item in self.items:
            item.received_qty = flt(item.qty)
            item.accepted_qty = flt(item.qty) - flt(item.rejected_qty)

            if flt(item.accepted_qty) < 0:
                frappe.throw(
                    _("Row {0}: Rejected Qty cannot be greater than Received Qty").format(item.idx)
                )

    def calculate_totals(self):
        """Calculate item amounts and totals"""
        self.total_qty = 0
        self.total_rejected_qty = 0
        self.total = 0

        for item in self.items:
            item.amount = flt(item.accepted_qty) * flt(item.rate)
            self.total_qty += flt(item.accepted_qty)
            self.total_rejected_qty += flt(item.rejected_qty)
            self.total += flt(item.amount)

    def calculate_taxes(self):
        """Calculate taxes and grand total"""
        self.total_taxes_and_charges = 0

        if self.taxes:
            cumulative_total = flt(self.total)

            for tax in self.taxes:
                if tax.charge_type == "Actual":
                    tax.tax_amount = flt(tax.rate)
                elif tax.charge_type == "On Net Total":
                    tax.tax_amount = flt(self.total) * flt(tax.rate) / 100
                elif tax.charge_type == "On Previous Row Amount":
                    ref_row = self.taxes[cint(tax.row_id) - 1] if tax.row_id else None
                    if ref_row:
                        tax.tax_amount = flt(ref_row.tax_amount) * flt(tax.rate) / 100
                elif tax.charge_type == "On Previous Row Total":
                    ref_row = self.taxes[cint(tax.row_id) - 1] if tax.row_id else None
                    if ref_row:
                        tax.tax_amount = flt(ref_row.total) * flt(tax.rate) / 100

                if tax.add_deduct_tax == "Deduct":
                    cumulative_total -= flt(tax.tax_amount)
                    self.total_taxes_and_charges -= flt(tax.tax_amount)
                else:
                    cumulative_total += flt(tax.tax_amount)
                    self.total_taxes_and_charges += flt(tax.tax_amount)

                tax.total = cumulative_total

        self.grand_total = flt(self.total) + flt(self.total_taxes_and_charges)
        self.rounded_total = round(self.grand_total)

    def set_status(self, update=False, status=None):
        """Set document status"""
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            if self.is_return:
                self.status = "Completed"
            else:
                # Check if all items are billed
                self.status = "To Bill"  # Simplified - can be enhanced with billing check
        elif self.docstatus == 2:
            self.status = "Cancelled"

        if update:
            self.db_set("status", self.status)

    def on_submit(self):
        """Actions on submit"""
        self.update_purchase_order()
        self.create_stock_entries()
        self.update_status()

    def on_cancel(self):
        """Actions on cancel"""
        self.update_purchase_order(cancel=True)
        self.cancel_stock_entries()
        self.set_status(update=True)

    def update_purchase_order(self, cancel=False):
        """Update received qty in linked purchase order"""
        if not self.purchase_order:
            return

        po = frappe.get_doc("Purchase Order", self.purchase_order)

        for item in self.items:
            if item.purchase_order_item:
                for po_item in po.items:
                    if po_item.name == item.purchase_order_item:
                        if cancel:
                            po_item.received_qty = flt(po_item.received_qty) - flt(item.accepted_qty)
                        else:
                            po_item.received_qty = flt(po_item.received_qty) + flt(item.accepted_qty)
                        po_item.db_update()

        po.update_status()

    def create_stock_entries(self):
        """Create stock ledger entries for received items"""
        for item in self.items:
            # Create entry for accepted qty
            if flt(item.accepted_qty) > 0:
                self.create_stock_ledger_entry(
                    item_code=item.item_code,
                    warehouse=item.warehouse,
                    qty=item.accepted_qty,
                    rate=item.rate,
                    batch_no=item.batch_no,
                    serial_no=item.serial_no
                )

            # Create entry for rejected qty
            if flt(item.rejected_qty) > 0 and item.rejected_warehouse:
                self.create_stock_ledger_entry(
                    item_code=item.item_code,
                    warehouse=item.rejected_warehouse,
                    qty=item.rejected_qty,
                    rate=item.rate,
                    batch_no=item.batch_no,
                    serial_no=item.serial_no
                )

    def create_stock_ledger_entry(self, item_code, warehouse, qty, rate, batch_no=None, serial_no=None):
        """Create a stock ledger entry"""
        sle = frappe.new_doc("Stock Ledger Entry")
        sle.item_code = item_code
        sle.warehouse = warehouse
        sle.posting_date = self.posting_date
        sle.posting_time = self.posting_time
        sle.voucher_type = self.doctype
        sle.voucher_no = self.name
        sle.actual_qty = flt(qty)
        sle.incoming_rate = flt(rate)
        sle.valuation_rate = flt(rate)
        sle.batch_no = batch_no
        sle.serial_no = serial_no

        # Calculate qty after transaction
        current_qty = get_current_stock(item_code, warehouse)
        sle.qty_after_transaction = flt(current_qty) + flt(qty)
        sle.stock_value = flt(sle.qty_after_transaction) * flt(rate)
        sle.stock_value_difference = flt(qty) * flt(rate)

        sle.insert(ignore_permissions=True)
        sle.submit()

    def cancel_stock_entries(self):
        """Cancel stock ledger entries"""
        sles = frappe.get_all(
            "Stock Ledger Entry",
            filters={"voucher_type": self.doctype, "voucher_no": self.name, "docstatus": 1},
            pluck="name"
        )

        for sle_name in sles:
            sle = frappe.get_doc("Stock Ledger Entry", sle_name)
            sle.cancel()

    def update_status(self):
        """Update status after submit"""
        self.set_status(update=True)


def get_current_stock(item_code, warehouse):
    """Get current stock quantity"""
    qty = frappe.db.sql("""
        SELECT SUM(actual_qty) as qty
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s AND warehouse = %s
        AND docstatus < 2 AND is_cancelled = 0
    """, (item_code, warehouse))

    return flt(qty[0][0]) if qty and qty[0][0] else 0


@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
    """Create Purchase Receipt from Purchase Order"""
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("calculate_totals")

    def update_item(source_doc, target_doc, source_parent):
        target_doc.qty = flt(source_doc.qty) - flt(source_doc.received_qty)
        target_doc.received_qty = target_doc.qty
        target_doc.purchase_order = source_parent.name
        target_doc.purchase_order_item = source_doc.name

    doclist = get_mapped_doc(
        "Purchase Order",
        source_name,
        {
            "Purchase Order": {
                "doctype": "Purchase Receipt",
                "field_map": {
                    "name": "purchase_order",
                    "supplier": "supplier",
                    "supplier_name": "supplier_name"
                },
                "validation": {"docstatus": ["=", 1]}
            },
            "Purchase Order Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "name": "purchase_order_item",
                    "parent": "purchase_order",
                    "warehouse": "warehouse",
                    "material_request": "material_request",
                    "material_request_item": "material_request_item"
                },
                "postprocess": update_item,
                "condition": lambda doc: flt(doc.qty) > flt(doc.received_qty)
            }
        },
        target_doc,
        set_missing_values
    )

    return doclist


@frappe.whitelist()
def make_purchase_return(source_name, target_doc=None):
    """Create Purchase Return from Purchase Receipt"""
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.is_return = 1
        target.return_against = source.name
        target.run_method("calculate_totals")

    def update_item(source_doc, target_doc, source_parent):
        target_doc.qty = -1 * flt(source_doc.qty)
        target_doc.received_qty = target_doc.qty
        target_doc.rejected_qty = -1 * flt(source_doc.rejected_qty)

    doclist = get_mapped_doc(
        "Purchase Receipt",
        source_name,
        {
            "Purchase Receipt": {
                "doctype": "Purchase Receipt",
                "validation": {"docstatus": ["=", 1]}
            },
            "Purchase Receipt Item": {
                "doctype": "Purchase Receipt Item",
                "postprocess": update_item
            }
        },
        target_doc,
        set_missing_values
    )

    return doclist
