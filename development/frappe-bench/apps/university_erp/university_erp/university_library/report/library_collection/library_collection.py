# Copyright (c) 2026, University ERP and contributors
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "category", "label": _("Category"), "fieldtype": "Link", "options": "Library Category", "width": 150},
        {"fieldname": "total_titles", "label": _("Total Titles"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_copies", "label": _("Total Copies"), "fieldtype": "Int", "width": 100},
        {"fieldname": "available", "label": _("Available"), "fieldtype": "Int", "width": 100},
        {"fieldname": "issued", "label": _("Issued"), "fieldtype": "Int", "width": 80},
        {"fieldname": "total_value", "label": _("Total Value"), "fieldtype": "Currency", "width": 120}
    ]


def get_data(filters):
    conditions = []
    values = []

    if filters.get("category"):
        conditions.append("category = %s")
        values.append(filters.get("category"))

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    return frappe.db.sql("""
        SELECT
            category,
            COUNT(*) as total_titles,
            SUM(total_copies) as total_copies,
            SUM(available_copies) as available,
            SUM(issued_copies) as issued,
            SUM(price * total_copies) as total_value
        FROM `tabLibrary Article`
        {where_clause}
        GROUP BY category
        ORDER BY total_titles DESC
    """.format(where_clause=where_clause), values, as_dict=True)


def get_chart(data):
    if not data:
        return None

    return {
        "data": {
            "labels": [d.category for d in data],
            "datasets": [{"values": [d.total_titles for d in data]}]
        },
        "type": "pie"
    }


def get_summary(data):
    if not data:
        return []

    return [
        {"value": sum(d.total_titles for d in data), "label": _("Total Titles"), "datatype": "Int"},
        {"value": sum(d.total_copies for d in data), "label": _("Total Copies"), "datatype": "Int"},
        {"value": sum(d.available for d in data), "label": _("Available"), "datatype": "Int"},
        {"value": sum(d.total_value or 0 for d in data), "label": _("Total Value"), "datatype": "Currency"}
    ]
