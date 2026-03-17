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
            "fieldname": "item_group",
            "label": _("Item Group"),
            "fieldtype": "Link",
            "options": "Inventory Item Group",
            "width": 120
        },
        {
            "fieldname": "warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        {
            "fieldname": "opening_qty",
            "label": _("Opening Qty"),
            "fieldtype": "Float",
            "width": 100
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
            "fieldname": "reorder_level",
            "label": _("Reorder Level"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "stock_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    # Get stock movements
    data = frappe.db.sql("""
        SELECT
            sle.item_code,
            ii.item_name,
            ii.item_group,
            sle.warehouse,
            SUM(CASE WHEN sle.posting_date < %(from_date)s THEN sle.actual_qty ELSE 0 END) as opening_qty,
            SUM(CASE WHEN sle.posting_date >= %(from_date)s AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) as in_qty,
            SUM(CASE WHEN sle.posting_date >= %(from_date)s AND sle.actual_qty < 0 THEN ABS(sle.actual_qty) ELSE 0 END) as out_qty,
            SUM(sle.actual_qty) as balance_qty,
            AVG(sle.valuation_rate) as valuation_rate,
            ii.reorder_level
        FROM `tabStock Ledger Entry` sle
        INNER JOIN `tabInventory Item` ii ON ii.name = sle.item_code
        WHERE sle.is_cancelled = 0
        AND sle.posting_date <= %(to_date)s
        {conditions}
        GROUP BY sle.item_code, sle.warehouse
        ORDER BY ii.item_name, sle.warehouse
    """.format(conditions=conditions), {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "item_code": filters.get("item_code"),
        "item_group": filters.get("item_group"),
        "warehouse": filters.get("warehouse")
    }, as_dict=True)

    # Calculate balance value and status
    for row in data:
        row["balance_value"] = flt(row["balance_qty"]) * flt(row["valuation_rate"])

        if flt(row["balance_qty"]) <= 0:
            row["stock_status"] = "Out of Stock"
        elif row["reorder_level"] and flt(row["balance_qty"]) <= flt(row["reorder_level"]):
            row["stock_status"] = "Low Stock"
        else:
            row["stock_status"] = "In Stock"

    return data


def get_conditions(filters):
    conditions = []

    if filters.get("item_code"):
        conditions.append("AND sle.item_code = %(item_code)s")

    if filters.get("item_group"):
        conditions.append("AND ii.item_group = %(item_group)s")

    if filters.get("warehouse"):
        conditions.append("AND sle.warehouse = %(warehouse)s")

    return " ".join(conditions)
