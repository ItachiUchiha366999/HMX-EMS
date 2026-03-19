# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Program-wise Fee Report

Provides a breakdown of fee collection, outstanding amounts,
and payment statistics grouped by academic program.
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "program", "label": _("Program"), "fieldtype": "Link", "options": "Program", "width": 200},
        {"fieldname": "total_students", "label": _("Students"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_fees", "label": _("Total Fees"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "collected", "label": _("Collected"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "outstanding", "label": _("Outstanding"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "collection_rate", "label": _("Collection %"), "fieldtype": "Percent", "width": 110},
        {"fieldname": "avg_fee_per_student", "label": _("Avg Fee/Student"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "fully_paid", "label": _("Fully Paid"), "fieldtype": "Int", "width": 100},
        {"fieldname": "partially_paid", "label": _("Partially Paid"), "fieldtype": "Int", "width": 110},
        {"fieldname": "unpaid", "label": _("Unpaid"), "fieldtype": "Int", "width": 80},
    ]


def get_data(filters):
    conditions = "f.docstatus = 1"

    if filters.get("academic_year"):
        conditions += " AND f.academic_year = %(academic_year)s"

    if filters.get("program"):
        conditions += " AND f.program = %(program)s"

    if filters.get("from_date"):
        conditions += " AND f.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND f.posting_date <= %(to_date)s"

    data = frappe.db.sql(f"""
        SELECT
            f.program,
            COUNT(DISTINCT f.student) as total_students,
            SUM(f.grand_total) as total_fees,
            SUM(f.grand_total - f.outstanding_amount) as collected,
            SUM(f.outstanding_amount) as outstanding,
            SUM(CASE WHEN f.outstanding_amount = 0 THEN 1 ELSE 0 END) as fully_paid,
            SUM(CASE WHEN f.outstanding_amount > 0 AND f.outstanding_amount < f.grand_total THEN 1 ELSE 0 END) as partially_paid,
            SUM(CASE WHEN f.outstanding_amount = f.grand_total THEN 1 ELSE 0 END) as unpaid
        FROM `tabFees` f
        WHERE {conditions}
        GROUP BY f.program
        ORDER BY total_fees DESC
    """, filters or {}, as_dict=True)

    for row in data:
        if row.total_fees:
            row["collection_rate"] = flt(row.collected) / flt(row.total_fees) * 100
        else:
            row["collection_rate"] = 0

        if row.total_students:
            row["avg_fee_per_student"] = flt(row.total_fees) / row.total_students
        else:
            row["avg_fee_per_student"] = 0

    return data


def get_chart(data):
    if not data:
        return None

    return {
        "data": {
            "labels": [d.program or "Unknown" for d in data[:10]],
            "datasets": [
                {"name": _("Collected"), "values": [flt(d.collected) for d in data[:10]]},
                {"name": _("Outstanding"), "values": [flt(d.outstanding) for d in data[:10]]}
            ]
        },
        "type": "bar",
        "barOptions": {"stacked": 1},
        "colors": ["#28a745", "#dc3545"]
    }


def get_summary(data):
    if not data:
        return []

    total_fees = sum(flt(d.total_fees) for d in data)
    total_collected = sum(flt(d.collected) for d in data)
    total_outstanding = sum(flt(d.outstanding) for d in data)
    total_students = sum(d.total_students or 0 for d in data)
    overall_rate = (total_collected / total_fees * 100) if total_fees else 0

    return [
        {"value": total_students, "label": _("Total Students"), "datatype": "Int"},
        {"value": total_fees, "label": _("Total Fees"), "datatype": "Currency", "indicator": "Blue"},
        {"value": total_collected, "label": _("Collected"), "datatype": "Currency", "indicator": "Green"},
        {"value": total_outstanding, "label": _("Outstanding"), "datatype": "Currency", "indicator": "Red"},
        {"value": flt(overall_rate, 1), "label": _("Collection Rate"), "datatype": "Percent",
         "indicator": "Green" if overall_rate >= 80 else "Orange" if overall_rate >= 60 else "Red"}
    ]
