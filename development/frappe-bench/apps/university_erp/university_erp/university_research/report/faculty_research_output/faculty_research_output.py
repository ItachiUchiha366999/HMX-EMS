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
        {"fieldname": "employee", "label": _("Faculty"), "fieldtype": "Link", "options": "Employee", "width": 120},
        {"fieldname": "employee_name", "label": _("Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "department", "label": _("Department"), "fieldtype": "Data", "width": 120},
        {"fieldname": "journal_papers", "label": _("Journal"), "fieldtype": "Int", "width": 70},
        {"fieldname": "conference_papers", "label": _("Conference"), "fieldtype": "Int", "width": 80},
        {"fieldname": "books_chapters", "label": _("Books"), "fieldtype": "Int", "width": 70},
        {"fieldname": "patents", "label": _("Patents"), "fieldtype": "Int", "width": 70},
        {"fieldname": "total_publications", "label": _("Total"), "fieldtype": "Int", "width": 70},
        {"fieldname": "total_citations", "label": _("Citations"), "fieldtype": "Int", "width": 80}
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("department"):
        conditions += " AND e.department = %(department)s"
        values["department"] = filters.get("department")

    if filters.get("employee"):
        conditions += " AND pa.employee = %(employee)s"
        values["employee"] = filters.get("employee")

    if filters.get("from_date"):
        conditions += " AND p.publication_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND p.publication_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    # Get all employees with publications
    data = frappe.db.sql("""
        SELECT
            pa.employee,
            e.employee_name,
            e.department,
            SUM(CASE WHEN p.publication_type = 'Journal Article' THEN 1 ELSE 0 END) as journal_papers,
            SUM(CASE WHEN p.publication_type = 'Conference Paper' THEN 1 ELSE 0 END) as conference_papers,
            SUM(CASE WHEN p.publication_type IN ('Book', 'Book Chapter') THEN 1 ELSE 0 END) as books_chapters,
            SUM(CASE WHEN p.publication_type = 'Patent' THEN 1 ELSE 0 END) as patents,
            COUNT(DISTINCT p.name) as total_publications,
            SUM(p.citations) as total_citations
        FROM `tabPublication Author` pa
        INNER JOIN `tabResearch Publication` p ON p.name = pa.parent
        INNER JOIN `tabEmployee` e ON e.name = pa.employee
        WHERE pa.employee IS NOT NULL
        AND p.status = 'Published'
        {conditions}
        GROUP BY pa.employee, e.employee_name, e.department
        ORDER BY total_publications DESC
    """.format(conditions=conditions), values, as_dict=True)

    return data


def get_chart(data):
    if not data:
        return None

    # Top 10 faculty by publications
    top_10 = data[:10]
    labels = [d.get("employee_name", "")[:15] for d in top_10]
    values = [d.get("total_publications") or 0 for d in top_10]

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Publications"), "values": values}]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data):
    if not data:
        return []

    total_faculty = len(data)
    total_pubs = sum(d.get("total_publications") or 0 for d in data)
    total_citations = sum(d.get("total_citations") or 0 for d in data)
    avg_per_faculty = total_pubs / total_faculty if total_faculty else 0

    return [
        {"value": total_faculty, "label": _("Faculty with Publications"), "datatype": "Int"},
        {"value": total_pubs, "label": _("Total Publications"), "datatype": "Int"},
        {"value": total_citations, "label": _("Total Citations"), "datatype": "Int"},
        {"value": round(avg_per_faculty, 1), "label": _("Avg per Faculty"), "datatype": "Float"}
    ]
