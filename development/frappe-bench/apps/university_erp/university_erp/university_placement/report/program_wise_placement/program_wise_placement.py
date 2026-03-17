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
        {"fieldname": "program", "label": _("Program"), "fieldtype": "Link", "options": "Program", "width": 200},
        {"fieldname": "total_students", "label": _("Total Students"), "fieldtype": "Int", "width": 120},
        {"fieldname": "registered", "label": _("Registered"), "fieldtype": "Int", "width": 100},
        {"fieldname": "placed", "label": _("Placed"), "fieldtype": "Int", "width": 80},
        {"fieldname": "placement_rate", "label": _("Placement %"), "fieldtype": "Percent", "width": 110},
        {"fieldname": "avg_package", "label": _("Avg Package"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "highest_package", "label": _("Highest Package"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "multiple_offers", "label": _("Multiple Offers"), "fieldtype": "Int", "width": 120},
        {"fieldname": "avg_offers", "label": _("Avg Offers/Student"), "fieldtype": "Float", "width": 130, "precision": 2}
    ]


def get_data(filters):
    conditions = ""
    if filters.get("academic_year"):
        conditions += " AND pd.academic_year = %(academic_year)s"
    if filters.get("program"):
        conditions += " AND pa.program = %(program)s"

    data = frappe.db.sql("""
        SELECT
            pa.program,
            COUNT(DISTINCT pa.student) as registered,
            COUNT(DISTINCT CASE WHEN pa.status = 'Offer Accepted' THEN pa.student ELSE NULL END) as placed,
            AVG(CASE WHEN pa.status = 'Offer Accepted' THEN pjo.package_offered ELSE NULL END) as avg_package,
            MAX(CASE WHEN pa.status = 'Offer Accepted' THEN pjo.package_offered ELSE NULL END) as highest_package
        FROM `tabPlacement Application` pa
        LEFT JOIN `tabPlacement Drive` pd ON pd.name = pa.placement_drive
        LEFT JOIN `tabPlacement Job Opening` pjo ON pjo.name = pa.job_opening
        WHERE pa.docstatus < 2 {conditions}
        GROUP BY pa.program
        ORDER BY placed DESC
    """.format(conditions=conditions), filters, as_dict=True)

    # Get total students per program and multiple offers
    for row in data:
        row["total_students"] = frappe.db.count("Student", {"program": row.program, "enabled": 1}) or 0

        if row.total_students:
            row["placement_rate"] = (row.placed or 0) / row.total_students * 100
        else:
            row["placement_rate"] = 0

        # Count students with multiple offers
        multiple_offers = frappe.db.sql("""
            SELECT COUNT(*) as count FROM (
                SELECT student, COUNT(*) as offer_count
                FROM `tabPlacement Application`
                WHERE program = %s AND status = 'Offer Accepted'
                GROUP BY student
                HAVING offer_count > 1
            ) as multi
        """, (row.program,), as_dict=True)[0]
        row["multiple_offers"] = multiple_offers.count or 0

        # Average offers per placed student
        if row.placed:
            total_offers = frappe.db.count("Placement Application", {
                "program": row.program,
                "status": "Offer Accepted"
            })
            row["avg_offers"] = total_offers / row.placed if row.placed else 0
        else:
            row["avg_offers"] = 0

    return data


def get_chart(data):
    if not data:
        return None

    labels = [row.program for row in data[:10]]
    placed = [row.placed or 0 for row in data[:10]]
    registered = [row.registered or 0 for row in data[:10]]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Registered"), "values": registered},
                {"name": _("Placed"), "values": placed}
            ]
        },
        "type": "bar",
        "colors": ["#7575ff", "#36a2eb"]
    }


def get_summary(data):
    if not data:
        return []

    total_students = sum(row.total_students or 0 for row in data)
    total_placed = sum(row.placed or 0 for row in data)
    total_registered = sum(row.registered or 0 for row in data)

    return [
        {"value": total_students, "label": _("Total Students"), "datatype": "Int"},
        {"value": total_registered, "label": _("Registered for Placement"), "datatype": "Int"},
        {"value": total_placed, "label": _("Placed"), "datatype": "Int", "indicator": "green"},
        {"value": (total_placed / total_students * 100) if total_students else 0,
         "label": _("Overall Placement Rate"), "datatype": "Percent", "indicator": "blue"}
    ]
