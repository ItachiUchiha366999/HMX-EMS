# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data, filters)

    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "period", "label": _("Period"), "fieldtype": "Data", "width": 120},
        {"fieldname": "drives_conducted", "label": _("Drives"), "fieldtype": "Int", "width": 80},
        {"fieldname": "companies_visited", "label": _("Companies"), "fieldtype": "Int", "width": 100},
        {"fieldname": "applications", "label": _("Applications"), "fieldtype": "Int", "width": 100},
        {"fieldname": "shortlisted", "label": _("Shortlisted"), "fieldtype": "Int", "width": 100},
        {"fieldname": "placed", "label": _("Placed"), "fieldtype": "Int", "width": 80},
        {"fieldname": "offers_made", "label": _("Offers Made"), "fieldtype": "Int", "width": 100},
        {"fieldname": "offers_accepted", "label": _("Offers Accepted"), "fieldtype": "Int", "width": 120},
        {"fieldname": "avg_package", "label": _("Avg Package"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "conversion_rate", "label": _("Conversion %"), "fieldtype": "Percent", "width": 110}
    ]


def get_data(filters):
    group_by = filters.get("group_by", "Month")
    conditions = ""

    if filters.get("academic_year"):
        conditions += " AND pd.academic_year = %(academic_year)s"
    if filters.get("from_date"):
        conditions += " AND pd.drive_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND pd.drive_date <= %(to_date)s"

    if group_by == "Month":
        date_format = "DATE_FORMAT(pd.drive_date, '%%Y-%%m')"
    elif group_by == "Quarter":
        date_format = "CONCAT(YEAR(pd.drive_date), '-Q', QUARTER(pd.drive_date))"
    else:  # Year
        date_format = "YEAR(pd.drive_date)"

    data = frappe.db.sql("""
        SELECT
            {date_format} as period,
            COUNT(DISTINCT pd.name) as drives_conducted,
            COUNT(DISTINCT pd.company) as companies_visited,
            COUNT(pa.name) as applications,
            SUM(CASE WHEN pa.status IN ('Shortlisted', 'Selected', 'Offer Accepted', 'Offer Rejected') THEN 1 ELSE 0 END) as shortlisted,
            SUM(CASE WHEN pa.status = 'Offer Accepted' THEN 1 ELSE 0 END) as placed,
            SUM(CASE WHEN pa.status IN ('Selected', 'Offer Accepted', 'Offer Rejected') THEN 1 ELSE 0 END) as offers_made,
            SUM(CASE WHEN pa.status = 'Offer Accepted' THEN 1 ELSE 0 END) as offers_accepted,
            AVG(CASE WHEN pa.status = 'Offer Accepted' THEN pjo.package_offered ELSE NULL END) as avg_package
        FROM `tabPlacement Drive` pd
        LEFT JOIN `tabPlacement Application` pa ON pa.placement_drive = pd.name
        LEFT JOIN `tabPlacement Job Opening` pjo ON pjo.name = pa.job_opening
        WHERE pd.docstatus < 2 AND pd.drive_date IS NOT NULL {conditions}
        GROUP BY {date_format}
        ORDER BY period ASC
    """.format(date_format=date_format, conditions=conditions), filters, as_dict=True)

    for row in data:
        if row.applications:
            row["conversion_rate"] = (row.placed or 0) / row.applications * 100
        else:
            row["conversion_rate"] = 0

    return data


def get_chart(data, filters):
    if not data:
        return None

    labels = [row.period for row in data]
    placed = [row.placed or 0 for row in data]
    applications = [row.applications or 0 for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Applications"), "values": applications, "chartType": "bar"},
                {"name": _("Placed"), "values": placed, "chartType": "line"}
            ]
        },
        "type": "axis-mixed",
        "colors": ["#7575ff", "#36a2eb"],
        "lineOptions": {"regionFill": 1}
    }
