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
        {"fieldname": "academic_year", "label": _("Academic Year"), "fieldtype": "Link", "options": "Academic Year", "width": 120},
        {"fieldname": "total_companies", "label": _("Total Companies"), "fieldtype": "Int", "width": 120},
        {"fieldname": "total_drives", "label": _("Total Drives"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_openings", "label": _("Total Openings"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_applications", "label": _("Applications"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_placed", "label": _("Placed"), "fieldtype": "Int", "width": 80},
        {"fieldname": "placement_rate", "label": _("Placement %"), "fieldtype": "Percent", "width": 100},
        {"fieldname": "avg_package", "label": _("Avg Package (LPA)"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "highest_package", "label": _("Highest Package"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "lowest_package", "label": _("Lowest Package"), "fieldtype": "Currency", "width": 120}
    ]


def get_data(filters):
    conditions = ""
    if filters.get("academic_year"):
        conditions += " AND pd.academic_year = %(academic_year)s"

    data = frappe.db.sql("""
        SELECT
            pd.academic_year,
            COUNT(DISTINCT pd.company) as total_companies,
            COUNT(DISTINCT pd.name) as total_drives,
            COUNT(DISTINCT pjo.name) as total_openings,
            COUNT(pa.name) as total_applications,
            SUM(CASE WHEN pa.status IN ('Placed', 'Selected') THEN 1 ELSE 0 END) as total_placed,
            AVG(CASE WHEN pa.status IN ('Placed', 'Selected') THEN pa.offered_ctc ELSE NULL END) as avg_package,
            MAX(CASE WHEN pa.status IN ('Placed', 'Selected') THEN pa.offered_ctc ELSE NULL END) as highest_package,
            MIN(CASE WHEN pa.status IN ('Placed', 'Selected') THEN pa.offered_ctc ELSE NULL END) as lowest_package
        FROM `tabPlacement Drive` pd
        LEFT JOIN `tabPlacement Job Opening` pjo ON pjo.company = pd.company
        LEFT JOIN `tabPlacement Application` pa ON pa.job_opening = pjo.name
        WHERE pd.docstatus < 2 {conditions}
        GROUP BY pd.academic_year
        ORDER BY pd.academic_year DESC
    """.format(conditions=conditions), filters, as_dict=True)

    # Calculate placement rate
    for row in data:
        if row.total_applications:
            row["placement_rate"] = (row.total_placed or 0) / row.total_applications * 100
        else:
            row["placement_rate"] = 0

    return data


def get_chart(data):
    if not data:
        return None

    labels = [row.academic_year for row in data]
    placed = [row.total_placed or 0 for row in data]
    applications = [row.total_applications or 0 for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Applications"), "values": applications},
                {"name": _("Placed"), "values": placed}
            ]
        },
        "type": "bar",
        "colors": ["#7575ff", "#36a2eb"],
        "barOptions": {"stacked": 0}
    }


def get_summary(data):
    if not data:
        return []

    total_placed = sum(row.total_placed or 0 for row in data)
    total_applications = sum(row.total_applications or 0 for row in data)
    total_companies = sum(row.total_companies or 0 for row in data)

    return [
        {"value": total_companies, "label": _("Total Companies"), "datatype": "Int"},
        {"value": total_applications, "label": _("Total Applications"), "datatype": "Int"},
        {"value": total_placed, "label": _("Total Placed"), "datatype": "Int", "indicator": "green"},
        {"value": (total_placed / total_applications * 100) if total_applications else 0,
         "label": _("Overall Placement Rate"), "datatype": "Percent", "indicator": "blue"}
    ]
