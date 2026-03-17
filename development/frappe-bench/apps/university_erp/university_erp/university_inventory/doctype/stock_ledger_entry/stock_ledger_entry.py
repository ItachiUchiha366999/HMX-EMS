# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class StockLedgerEntry(Document):
    """Stock Ledger Entry - Records all stock movements"""

    def validate(self):
        """Validate stock ledger entry"""
        self.validate_item()
        self.validate_warehouse()

    def validate_item(self):
        """Validate item exists and is active"""
        if not frappe.db.exists("Inventory Item", self.item_code):
            frappe.throw(_("Item {0} does not exist").format(self.item_code))

    def validate_warehouse(self):
        """Validate warehouse exists and is active"""
        if not frappe.db.exists("Warehouse", self.warehouse):
            frappe.throw(_("Warehouse {0} does not exist").format(self.warehouse))

        if frappe.db.get_value("Warehouse", self.warehouse, "is_active") == 0:
            frappe.throw(_("Warehouse {0} is not active").format(self.warehouse))

    def update_qty_after_transaction(self):
        """Calculate and update qty after transaction"""
        previous_qty = self.get_previous_qty()
        self.qty_after_transaction = flt(previous_qty) + flt(self.actual_qty)

        # Calculate stock value difference
        if self.actual_qty > 0:
            self.stock_value_difference = flt(self.actual_qty) * flt(self.incoming_rate or self.valuation_rate)
        else:
            self.stock_value_difference = flt(self.actual_qty) * flt(self.outgoing_rate or self.valuation_rate)

    def get_previous_qty(self):
        """Get quantity before this transaction"""
        previous_sle = frappe.db.sql("""
            SELECT qty_after_transaction
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s AND warehouse = %s
            AND is_cancelled = 0
            AND (
                posting_date < %s OR
                (posting_date = %s AND posting_time < %s) OR
                (posting_date = %s AND posting_time = %s AND creation < %s)
            )
            ORDER BY posting_date DESC, posting_time DESC, creation DESC
            LIMIT 1
        """, (
            self.item_code, self.warehouse,
            self.posting_date,
            self.posting_date, self.posting_time,
            self.posting_date, self.posting_time, self.creation
        ))

        return flt(previous_sle[0][0]) if previous_sle else 0


def get_stock_balance(item_code, warehouse=None, posting_date=None, posting_time=None):
    """Get stock balance for item"""
    conditions = ["item_code = %(item_code)s", "is_cancelled = 0"]
    values = {"item_code": item_code}

    if warehouse:
        conditions.append("warehouse = %(warehouse)s")
        values["warehouse"] = warehouse

    if posting_date:
        conditions.append("posting_date <= %(posting_date)s")
        values["posting_date"] = posting_date

    result = frappe.db.sql("""
        SELECT
            SUM(actual_qty) as qty,
            SUM(stock_value) as value
        FROM `tabStock Ledger Entry`
        WHERE {conditions}
    """.format(conditions=" AND ".join(conditions)), values, as_dict=True)

    return {
        "qty": flt(result[0].qty) if result else 0,
        "value": flt(result[0].value) if result else 0
    }


def get_stock_ledger_entries(item_code=None, warehouse=None, from_date=None, to_date=None, limit=None):
    """Get stock ledger entries"""
    conditions = ["is_cancelled = 0"]
    values = {}

    if item_code:
        conditions.append("item_code = %(item_code)s")
        values["item_code"] = item_code

    if warehouse:
        conditions.append("warehouse = %(warehouse)s")
        values["warehouse"] = warehouse

    if from_date:
        conditions.append("posting_date >= %(from_date)s")
        values["from_date"] = from_date

    if to_date:
        conditions.append("posting_date <= %(to_date)s")
        values["to_date"] = to_date

    limit_clause = f"LIMIT {limit}" if limit else ""

    return frappe.db.sql("""
        SELECT
            name, item_code, warehouse, posting_date, posting_time,
            voucher_type, voucher_no, actual_qty, qty_after_transaction,
            incoming_rate, outgoing_rate, valuation_rate, stock_value,
            batch_no, serial_no
        FROM `tabStock Ledger Entry`
        WHERE {conditions}
        ORDER BY posting_date DESC, posting_time DESC, creation DESC
        {limit_clause}
    """.format(conditions=" AND ".join(conditions), limit_clause=limit_clause), values, as_dict=True)


@frappe.whitelist()
def get_item_stock_by_warehouse(item_code):
    """Get stock by warehouse for an item"""
    return frappe.db.sql("""
        SELECT
            warehouse,
            SUM(actual_qty) as qty,
            SUM(stock_value) as value
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s AND is_cancelled = 0
        GROUP BY warehouse
        HAVING SUM(actual_qty) > 0
    """, item_code, as_dict=True)
