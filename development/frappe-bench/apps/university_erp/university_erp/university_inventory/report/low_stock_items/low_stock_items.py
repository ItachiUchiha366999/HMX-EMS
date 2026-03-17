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
            "width": 180
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
            "fieldname": "current_stock",
            "label": _("Current Stock"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "reorder_level",
            "label": _("Reorder Level"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "reorder_qty",
            "label": _("Reorder Qty"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "shortage",
            "label": _("Shortage"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "default_supplier",
            "label": _("Default Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 120
        },
        {
            "fieldname": "last_purchase_rate",
            "label": _("Last Purchase Rate"),
            "fieldtype": "Currency",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            ii.name as item_code,
            ii.item_name,
            ii.item_group,
            COALESCE(sle.warehouse, ii.default_warehouse) as warehouse,
            COALESCE(SUM(sle.actual_qty), 0) as current_stock,
            ii.reorder_level,
            ii.reorder_quantity as reorder_qty,
            ii.default_supplier,
            ii.last_purchase_rate
        FROM `tabInventory Item` ii
        LEFT JOIN `tabStock Ledger Entry` sle ON sle.item_code = ii.name AND sle.is_cancelled = 0
        WHERE ii.maintain_stock = 1
        AND ii.is_active = 1
        AND ii.reorder_level > 0
        {conditions}
        GROUP BY ii.name, COALESCE(sle.warehouse, ii.default_warehouse)
        HAVING COALESCE(SUM(sle.actual_qty), 0) <= ii.reorder_level
        ORDER BY (ii.reorder_level - COALESCE(SUM(sle.actual_qty), 0)) DESC
    """.format(conditions=conditions), {
        "item_group": filters.get("item_group"),
        "warehouse": filters.get("warehouse")
    }, as_dict=True)

    # Calculate shortage
    for row in data:
        row["shortage"] = flt(row["reorder_level"]) - flt(row["current_stock"])

    return data


def get_conditions(filters):
    conditions = []

    if filters.get("item_group"):
        conditions.append("AND ii.item_group = %(item_group)s")

    if filters.get("warehouse"):
        conditions.append("AND sle.warehouse = %(warehouse)s")

    return " ".join(conditions)
