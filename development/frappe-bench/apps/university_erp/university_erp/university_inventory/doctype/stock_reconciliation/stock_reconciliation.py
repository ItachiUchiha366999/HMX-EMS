# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, now_datetime


class StockReconciliation(Document):
    def validate(self):
        self.validate_items()
        self.set_current_stock()
        self.calculate_differences()

    def validate_items(self):
        """Validate items in the reconciliation"""
        if not self.items:
            frappe.throw(_("Please add items to reconcile"))

        item_warehouse_combinations = []
        for item in self.items:
            if not item.item_code:
                frappe.throw(_("Row {0}: Item Code is required").format(item.idx))

            if not item.warehouse:
                if self.set_warehouse:
                    item.warehouse = self.set_warehouse
                else:
                    frappe.throw(_("Row {0}: Warehouse is required").format(item.idx))

            # Check for duplicates
            key = (item.item_code, item.warehouse, item.batch_no or "")
            if key in item_warehouse_combinations:
                frappe.throw(
                    _("Row {0}: Duplicate entry for Item {1} in Warehouse {2}").format(
                        item.idx, item.item_code, item.warehouse
                    )
                )
            item_warehouse_combinations.append(key)

    def set_current_stock(self):
        """Set current stock quantity and valuation rate for each item"""
        for item in self.items:
            current_stock = get_stock_balance(
                item.item_code,
                item.warehouse,
                self.posting_date,
                self.posting_time,
                batch_no=item.batch_no
            )
            item.current_qty = flt(current_stock.get("qty", 0))
            item.current_valuation_rate = flt(current_stock.get("valuation_rate", 0))
            item.current_amount = flt(item.current_qty) * flt(item.current_valuation_rate)

    def calculate_differences(self):
        """Calculate quantity and amount differences"""
        total_difference = 0
        for item in self.items:
            # If qty is not set, assume no change
            if item.qty is None:
                item.qty = item.current_qty

            # If valuation_rate is not set, use current rate
            if item.valuation_rate is None or item.valuation_rate == 0:
                item.valuation_rate = item.current_valuation_rate

            # Calculate differences
            item.qty_difference = flt(item.qty) - flt(item.current_qty)
            item.amount = flt(item.qty) * flt(item.valuation_rate)
            item.amount_difference = flt(item.amount) - flt(item.current_amount)

            total_difference += flt(item.amount_difference)

        self.difference_amount = total_difference

    def on_submit(self):
        """Create stock ledger entries on submit"""
        self.create_stock_ledger_entries()

    def on_cancel(self):
        """Reverse stock ledger entries on cancel"""
        self.create_stock_ledger_entries(cancel=True)

    def create_stock_ledger_entries(self, cancel=False):
        """Create stock ledger entries for reconciliation"""
        for item in self.items:
            if flt(item.qty_difference) == 0 and flt(item.amount_difference) == 0:
                continue

            # Create stock ledger entry
            sle = frappe.new_doc("Stock Ledger Entry")
            sle.item_code = item.item_code
            sle.warehouse = item.warehouse
            sle.posting_date = self.posting_date
            sle.posting_time = self.posting_time
            sle.voucher_type = self.doctype
            sle.voucher_no = self.name
            sle.batch_no = item.batch_no
            sle.serial_no = item.serial_no

            if cancel:
                # Reverse the entry
                sle.actual_qty = -flt(item.qty_difference)
                sle.is_cancelled = 1
            else:
                sle.actual_qty = flt(item.qty_difference)

            # Set valuation rate for incoming stock
            if flt(sle.actual_qty) > 0:
                sle.incoming_rate = flt(item.valuation_rate)
            else:
                sle.outgoing_rate = flt(item.valuation_rate)

            sle.valuation_rate = flt(item.valuation_rate)
            sle.qty_after_transaction = flt(item.qty) if not cancel else flt(item.current_qty)
            sle.stock_value = flt(sle.qty_after_transaction) * flt(sle.valuation_rate)
            sle.stock_value_difference = flt(item.amount_difference) if not cancel else -flt(item.amount_difference)

            sle.insert(ignore_permissions=True)
            sle.submit()

    def get_items(self, warehouse=None, item_group=None):
        """Get items for reconciliation based on filters"""
        conditions = []
        values = {}

        if warehouse:
            conditions.append("sle.warehouse = %(warehouse)s")
            values["warehouse"] = warehouse

        if item_group:
            conditions.append("ii.item_group = %(item_group)s")
            values["item_group"] = item_group

        condition_str = " AND ".join(conditions) if conditions else "1=1"

        items = frappe.db.sql("""
            SELECT
                sle.item_code,
                ii.item_name,
                sle.warehouse,
                SUM(sle.actual_qty) as qty,
                AVG(sle.valuation_rate) as valuation_rate
            FROM `tabStock Ledger Entry` sle
            INNER JOIN `tabInventory Item` ii ON ii.name = sle.item_code
            WHERE {conditions}
                AND sle.docstatus < 2
                AND sle.is_cancelled = 0
            GROUP BY sle.item_code, sle.warehouse
            HAVING SUM(sle.actual_qty) != 0
            ORDER BY sle.item_code
        """.format(conditions=condition_str), values, as_dict=True)

        return items


def get_stock_balance(item_code, warehouse, posting_date=None, posting_time=None, batch_no=None):
    """Get current stock balance for an item in a warehouse"""
    conditions = ["item_code = %(item_code)s", "warehouse = %(warehouse)s", "docstatus < 2", "is_cancelled = 0"]
    values = {"item_code": item_code, "warehouse": warehouse}

    if batch_no:
        conditions.append("batch_no = %(batch_no)s")
        values["batch_no"] = batch_no

    if posting_date:
        conditions.append("posting_date <= %(posting_date)s")
        values["posting_date"] = posting_date

    condition_str = " AND ".join(conditions)

    # Get the latest stock ledger entry
    sle = frappe.db.sql("""
        SELECT
            SUM(actual_qty) as qty,
            AVG(valuation_rate) as valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE {conditions}
    """.format(conditions=condition_str), values, as_dict=True)

    if sle and sle[0]:
        return {
            "qty": flt(sle[0].get("qty", 0)),
            "valuation_rate": flt(sle[0].get("valuation_rate", 0))
        }

    return {"qty": 0, "valuation_rate": 0}


@frappe.whitelist()
def get_items_for_reconciliation(warehouse=None, item_group=None, posting_date=None):
    """API to get items for stock reconciliation"""
    conditions = []
    values = {}

    if warehouse:
        conditions.append("sle.warehouse = %(warehouse)s")
        values["warehouse"] = warehouse

    if item_group:
        conditions.append("ii.item_group = %(item_group)s")
        values["item_group"] = item_group

    if posting_date:
        conditions.append("sle.posting_date <= %(posting_date)s")
        values["posting_date"] = posting_date

    condition_str = " AND ".join(conditions) if conditions else "1=1"

    items = frappe.db.sql("""
        SELECT
            sle.item_code,
            ii.item_name,
            sle.warehouse,
            SUM(sle.actual_qty) as current_qty,
            AVG(sle.valuation_rate) as current_valuation_rate
        FROM `tabStock Ledger Entry` sle
        INNER JOIN `tabInventory Item` ii ON ii.name = sle.item_code
        WHERE {conditions}
            AND sle.docstatus < 2
            AND sle.is_cancelled = 0
        GROUP BY sle.item_code, sle.warehouse
        ORDER BY sle.item_code
    """.format(conditions=condition_str), values, as_dict=True)

    # Calculate current amount
    for item in items:
        item["current_amount"] = flt(item["current_qty"]) * flt(item["current_valuation_rate"])

    return items
