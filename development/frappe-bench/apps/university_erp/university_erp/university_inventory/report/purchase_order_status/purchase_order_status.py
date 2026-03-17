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
            "fieldname": "name",
            "label": _("PO Number"),
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 140
        },
        {
            "fieldname": "supplier",
            "label": _("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 120
        },
        {
            "fieldname": "supplier_name",
            "label": _("Supplier Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "transaction_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "grand_total",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "total_qty",
            "label": _("Total Qty"),
            "fieldtype": "Float",
            "width": 90
        },
        {
            "fieldname": "received_qty",
            "label": _("Received Qty"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "received_percent",
            "label": _("Received %"),
            "fieldtype": "Percent",
            "width": 90
        },
        {
            "fieldname": "billed_qty",
            "label": _("Billed Qty"),
            "fieldtype": "Float",
            "width": 90
        },
        {
            "fieldname": "billed_percent",
            "label": _("Billed %"),
            "fieldtype": "Percent",
            "width": 80
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "delivery_date",
            "label": _("Required By"),
            "fieldtype": "Date",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            po.name,
            po.supplier,
            po.supplier_name,
            po.transaction_date,
            po.grand_total,
            po.total_qty,
            po.status,
            po.delivery_date,
            COALESCE(SUM(poi.received_qty), 0) as received_qty,
            COALESCE(SUM(poi.billed_qty), 0) as billed_qty
        FROM `tabPurchase Order` po
        LEFT JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
        WHERE po.docstatus = 1
        {conditions}
        GROUP BY po.name
        ORDER BY po.transaction_date DESC
    """.format(conditions=conditions), {
        "supplier": filters.get("supplier"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "status": filters.get("status")
    }, as_dict=True)

    # Calculate percentages
    for row in data:
        if flt(row["total_qty"]) > 0:
            row["received_percent"] = (flt(row["received_qty"]) / flt(row["total_qty"])) * 100
            row["billed_percent"] = (flt(row["billed_qty"]) / flt(row["total_qty"])) * 100
        else:
            row["received_percent"] = 0
            row["billed_percent"] = 0

    return data


def get_conditions(filters):
    conditions = []

    if filters.get("supplier"):
        conditions.append("AND po.supplier = %(supplier)s")

    if filters.get("from_date"):
        conditions.append("AND po.transaction_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("AND po.transaction_date <= %(to_date)s")

    if filters.get("status"):
        conditions.append("AND po.status = %(status)s")

    return " ".join(conditions)
