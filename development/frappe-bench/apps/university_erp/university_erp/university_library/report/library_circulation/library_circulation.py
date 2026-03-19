# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data, filters)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "transaction_date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "issues", "label": _("Issues"), "fieldtype": "Int", "width": 80},
        {"fieldname": "returns", "label": _("Returns"), "fieldtype": "Int", "width": 80},
        {"fieldname": "renewals", "label": _("Renewals"), "fieldtype": "Int", "width": 80},
        {"fieldname": "total", "label": _("Total"), "fieldtype": "Int", "width": 80}
    ]


def get_data(filters):
    conditions = []
    values = []

    if filters.get("from_date"):
        conditions.append("transaction_date >= %s")
        values.append(filters.get("from_date"))

    if filters.get("to_date"):
        conditions.append("transaction_date <= %s")
        values.append(filters.get("to_date"))

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    return frappe.db.sql("""
        SELECT
            transaction_date,
            SUM(CASE WHEN transaction_type = 'Issue' THEN 1 ELSE 0 END) as issues,
            SUM(CASE WHEN transaction_type = 'Return' THEN 1 ELSE 0 END) as returns,
            SUM(CASE WHEN transaction_type = 'Renew' THEN 1 ELSE 0 END) as renewals,
            COUNT(*) as total
        FROM `tabLibrary Transaction`
        {where_clause}
        GROUP BY transaction_date
        ORDER BY transaction_date DESC
    """.format(where_clause=where_clause), values, as_dict=True)


def get_chart(data, filters):
    if not data:
        return None

    labels = [str(d.transaction_date) for d in data[-30:]]  # Last 30 days
    issues = [d.issues for d in data[-30:]]
    returns = [d.returns for d in data[-30:]]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Issues"), "values": issues},
                {"name": _("Returns"), "values": returns}
            ]
        },
        "type": "line",
        "colors": ["#5e64ff", "#98d85b"]
    }


def get_summary(data):
    if not data:
        return []

    total_issues = sum(d.issues for d in data)
    total_returns = sum(d.returns for d in data)
    total_renewals = sum(d.renewals for d in data)

    return [
        {"value": total_issues, "label": _("Total Issues"), "datatype": "Int"},
        {"value": total_returns, "label": _("Total Returns"), "datatype": "Int"},
        {"value": total_renewals, "label": _("Total Renewals"), "datatype": "Int"}
    ]
