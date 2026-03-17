# Copyright (c) 2026, University and contributors
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
        {
            "fieldname": "name",
            "label": _("Transaction ID"),
            "fieldtype": "Link",
            "options": "Payment Transaction",
            "width": 140
        },
        {
            "fieldname": "transaction_date",
            "label": _("Date"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "student",
            "label": _("Student"),
            "fieldtype": "Link",
            "options": "Student",
            "width": 120
        },
        {
            "fieldname": "student_name",
            "label": _("Student Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "fieldname": "payment_gateway",
            "label": _("Gateway"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "payment_method",
            "label": _("Method"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "reference_doctype",
            "label": _("Ref Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "reference_name",
            "label": _("Reference"),
            "fieldtype": "Dynamic Link",
            "options": "reference_doctype",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("from_date"):
        conditions.append("transaction_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("transaction_date <= %(to_date)s")
        values["to_date"] = filters["to_date"] + " 23:59:59"

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]

    if filters.get("payment_gateway"):
        conditions.append("payment_gateway = %(payment_gateway)s")
        values["payment_gateway"] = filters["payment_gateway"]

    if filters.get("student"):
        conditions.append("student = %(student)s")
        values["student"] = filters["student"]

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    return frappe.db.sql(f"""
        SELECT
            name,
            transaction_date,
            student,
            student_name,
            amount,
            payment_gateway,
            payment_method,
            status,
            reference_doctype,
            reference_name
        FROM `tabPayment Transaction`
        WHERE {where_clause}
        ORDER BY transaction_date DESC
    """, values, as_dict=True)


def get_chart(data):
    # Group by status
    status_counts = {}
    for row in data:
        status = row.get("status", "Unknown")
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1

    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [
                {"values": list(status_counts.values())}
            ]
        },
        "type": "donut",
        "title": _("Transactions by Status"),
        "colors": ["#28a745", "#ffc107", "#dc3545", "#17a2b8"]
    }


def get_summary(data):
    total_amount = sum(row.get("amount", 0) for row in data if row.get("status") == "Success")
    success_count = len([row for row in data if row.get("status") == "Success"])
    failed_count = len([row for row in data if row.get("status") == "Failed"])

    return [
        {
            "value": total_amount,
            "label": _("Total Success Amount"),
            "datatype": "Currency",
            "indicator": "green"
        },
        {
            "value": success_count,
            "label": _("Successful Transactions"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": failed_count,
            "label": _("Failed Transactions"),
            "datatype": "Int",
            "indicator": "red" if failed_count > 0 else "gray"
        },
        {
            "value": len(data),
            "label": _("Total Transactions"),
            "datatype": "Int",
            "indicator": "blue"
        }
    ]
