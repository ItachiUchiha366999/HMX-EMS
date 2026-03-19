# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

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
        {"fieldname": "route", "label": _("Route"), "fieldtype": "Link", "options": "Transport Route", "width": 150},
        {"fieldname": "student_count", "label": _("Students"), "fieldtype": "Int", "width": 80},
        {"fieldname": "total_fare", "label": _("Total Billed"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "collected", "label": _("Collected"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "outstanding", "label": _("Outstanding"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "collection_rate", "label": _("Collection %"), "fieldtype": "Percent", "width": 100}
    ]


def get_data(filters):
    conditions = ["ta.status = 'Active'", "ta.docstatus = 1"]
    values = []

    if filters.get("academic_year"):
        conditions.append("ta.academic_year = %s")
        values.append(filters.get("academic_year"))

    if filters.get("route"):
        conditions.append("ta.route = %s")
        values.append(filters.get("route"))

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql("""
        SELECT
            ta.route,
            tr.route_name,
            COUNT(ta.name) as student_count,
            SUM(ta.total_fare) as total_fare
        FROM `tabTransport Allocation` ta
        JOIN `tabTransport Route` tr ON ta.route = tr.name
        WHERE {where_clause}
        GROUP BY ta.route
        ORDER BY tr.route_name
    """.format(where_clause=where_clause), values, as_dict=True)

    # Calculate collection for each route
    for row in data:
        # Get fee payments for this route's allocations
        collected = frappe.db.sql("""
            SELECT COALESCE(SUM(f.grand_total - f.outstanding_amount), 0) as collected
            FROM `tabFees` f
            JOIN `tabTransport Allocation` ta ON f.name = ta.fee_reference
            WHERE ta.route = %s
            AND ta.status = 'Active'
            AND ta.docstatus = 1
            AND f.docstatus = 1
        """, (row.route,))[0][0] or 0

        row["collected"] = collected
        row["outstanding"] = (row.total_fare or 0) - collected
        row["collection_rate"] = round(
            collected / row.total_fare * 100, 2
        ) if row.total_fare else 0

    return data


def get_chart(data):
    if not data:
        return None

    labels = [d.route_name or d.route for d in data]
    collected = [d.collected or 0 for d in data]
    outstanding = [d.outstanding or 0 for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Collected"), "values": collected},
                {"name": _("Outstanding"), "values": outstanding}
            ]
        },
        "type": "bar",
        "colors": ["#98d85b", "#fc4f51"],
        "barOptions": {"stacked": 1}
    }


def get_summary(data):
    if not data:
        return []

    total_billed = sum(d.total_fare or 0 for d in data)
    total_collected = sum(d.collected or 0 for d in data)
    total_outstanding = sum(d.outstanding or 0 for d in data)
    avg_collection = (total_collected / total_billed * 100) if total_billed else 0

    return [
        {"value": total_billed, "label": _("Total Billed"), "datatype": "Currency"},
        {"value": total_collected, "label": _("Total Collected"), "datatype": "Currency", "indicator": "green"},
        {"value": total_outstanding, "label": _("Total Outstanding"), "datatype": "Currency", "indicator": "red" if total_outstanding > 0 else "green"},
        {"value": round(avg_collection, 2), "label": _("Collection Rate"), "datatype": "Percent"}
    ]
