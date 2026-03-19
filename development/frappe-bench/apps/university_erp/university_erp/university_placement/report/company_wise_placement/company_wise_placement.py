# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "company", "label": _("Company"), "fieldtype": "Link", "options": "Placement Company", "width": 180},
        {"fieldname": "company_name", "label": _("Company Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "industry_type", "label": _("Industry"), "fieldtype": "Data", "width": 120},
        {"fieldname": "total_drives", "label": _("Drives"), "fieldtype": "Int", "width": 80},
        {"fieldname": "total_openings", "label": _("Openings"), "fieldtype": "Int", "width": 90},
        {"fieldname": "total_applications", "label": _("Applications"), "fieldtype": "Int", "width": 100},
        {"fieldname": "shortlisted", "label": _("Shortlisted"), "fieldtype": "Int", "width": 100},
        {"fieldname": "selected", "label": _("Selected"), "fieldtype": "Int", "width": 90},
        {"fieldname": "placed", "label": _("Placed"), "fieldtype": "Int", "width": 80},
        {"fieldname": "avg_package", "label": _("Avg Package"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "selection_rate", "label": _("Selection %"), "fieldtype": "Percent", "width": 100}
    ]


def get_data(filters):
    conditions = ""
    if filters.get("academic_year"):
        conditions += " AND pd.academic_year = %(academic_year)s"
    if filters.get("industry_type"):
        conditions += " AND pc.industry_type = %(industry_type)s"
    if filters.get("company"):
        conditions += " AND pc.name = %(company)s"

    data = frappe.db.sql("""
        SELECT
            pc.name as company,
            pc.company_name,
            pc.industry_type,
            COUNT(DISTINCT pd.name) as total_drives,
            COUNT(DISTINCT pd.job_opening) as total_openings,
            COUNT(pa.name) as total_applications,
            SUM(CASE WHEN pa.status IN ('Shortlisted', 'Selected', 'Placed') THEN 1 ELSE 0 END) as shortlisted,
            SUM(CASE WHEN pa.status IN ('Selected', 'Placed') THEN 1 ELSE 0 END) as selected,
            SUM(CASE WHEN pa.status = 'Placed' THEN 1 ELSE 0 END) as placed,
            AVG(CASE WHEN pa.status = 'Placed' THEN pa.offered_ctc ELSE NULL END) as avg_package
        FROM `tabPlacement Company` pc
        LEFT JOIN `tabPlacement Drive` pd ON pd.company = pc.name
        LEFT JOIN `tabPlacement Application` pa ON pa.placement_drive = pd.name
        WHERE pc.docstatus < 2 {conditions}
        GROUP BY pc.name
        ORDER BY placed DESC, total_applications DESC
    """.format(conditions=conditions), filters, as_dict=True)

    for row in data:
        if row.total_applications:
            row["selection_rate"] = (row.placed or 0) / row.total_applications * 100
        else:
            row["selection_rate"] = 0

    return data


def get_chart(data):
    if not data:
        return None

    # Top 10 companies by placements
    top_companies = sorted(data, key=lambda x: x.placed or 0, reverse=True)[:10]

    labels = [row.company_name for row in top_companies]
    values = [row.placed or 0 for row in top_companies]

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Students Placed"), "values": values}]
        },
        "type": "bar",
        "colors": ["#36a2eb"]
    }
