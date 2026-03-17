# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "posting_time",
            "label": _("Time"),
            "fieldtype": "Time",
            "width": 80
        },
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Inventory Item",
            "width": 120
        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        {
            "fieldname": "in_qty",
            "label": _("In Qty"),
            "fieldtype": "Float",
            "width": 80
        },
        {
            "fieldname": "out_qty",
            "label": _("Out Qty"),
            "fieldtype": "Float",
            "width": 80
        },
        {
            "fieldname": "balance_qty",
            "label": _("Balance Qty"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "valuation_rate",
            "label": _("Valuation Rate"),
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "fieldname": "balance_value",
            "label": _("Balance Value"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "voucher_type",
            "label": _("Voucher Type"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No"),
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 140
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            sle.posting_date,
            sle.posting_time,
            sle.item_code,
            ii.item_name,
            sle.warehouse,
            CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END as in_qty,
            CASE WHEN sle.actual_qty < 0 THEN ABS(sle.actual_qty) ELSE 0 END as out_qty,
            sle.qty_after_transaction as balance_qty,
            sle.valuation_rate,
            sle.stock_value as balance_value,
            sle.voucher_type,
            sle.voucher_no
        FROM `tabStock Ledger Entry` sle
        INNER JOIN `tabInventory Item` ii ON ii.name = sle.item_code
        WHERE sle.is_cancelled = 0
        {conditions}
        ORDER BY sle.posting_date, sle.posting_time, sle.name
    """.format(conditions=conditions), {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "item_code": filters.get("item_code"),
        "warehouse": filters.get("warehouse"),
        "voucher_type": filters.get("voucher_type")
    }, as_dict=True)

    return data


def get_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("AND sle.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("AND sle.posting_date <= %(to_date)s")

    if filters.get("item_code"):
        conditions.append("AND sle.item_code = %(item_code)s")

    if filters.get("warehouse"):
        conditions.append("AND sle.warehouse = %(warehouse)s")

    if filters.get("voucher_type"):
        conditions.append("AND sle.voucher_type = %(voucher_type)s")

    return " ".join(conditions)
