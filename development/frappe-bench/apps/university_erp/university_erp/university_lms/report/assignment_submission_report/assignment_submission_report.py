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
        {"fieldname": "student", "label": _("Student"), "fieldtype": "Link", "options": "Student", "width": 120},
        {"fieldname": "student_name", "label": _("Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "assignment", "label": _("Assignment"), "fieldtype": "Link", "options": "LMS Assignment", "width": 150},
        {"fieldname": "submission_date", "label": _("Submitted On"), "fieldtype": "Datetime", "width": 140},
        {"fieldname": "is_late", "label": _("Late"), "fieldtype": "Check", "width": 60},
        {"fieldname": "marks_obtained", "label": _("Marks"), "fieldtype": "Float", "width": 80},
        {"fieldname": "final_marks", "label": _("Final"), "fieldtype": "Float", "width": 80},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100}
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("lms_course"):
        conditions += " AND a.lms_course = %(lms_course)s"
        values["lms_course"] = filters.get("lms_course")

    if filters.get("assignment"):
        conditions += " AND s.assignment = %(assignment)s"
        values["assignment"] = filters.get("assignment")

    if filters.get("status"):
        conditions += " AND s.status = %(status)s"
        values["status"] = filters.get("status")

    if filters.get("from_date"):
        conditions += " AND s.submission_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND s.submission_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    return frappe.db.sql("""
        SELECT
            s.student,
            s.student_name,
            s.assignment,
            s.submission_date,
            s.is_late,
            s.marks_obtained,
            s.final_marks,
            s.status
        FROM `tabAssignment Submission` s
        INNER JOIN `tabLMS Assignment` a ON a.name = s.assignment
        WHERE 1=1 {conditions}
        ORDER BY s.submission_date DESC
    """.format(conditions=conditions), values, as_dict=True)


def get_chart(data):
    if not data:
        return None

    status_count = {}
    for row in data:
        status = row.get("status") or "Unknown"
        status_count[status] = status_count.get(status, 0) + 1

    return {
        "data": {
            "labels": list(status_count.keys()),
            "datasets": [{"name": _("Submissions"), "values": list(status_count.values())}]
        },
        "type": "pie",
        "colors": ["#5e64ff", "#98d85b", "#ffa00a", "#ff5858"]
    }


def get_summary(data):
    if not data:
        return []

    total = len(data)
    graded = len([d for d in data if d.get("status") == "Graded"])
    late = len([d for d in data if d.get("is_late")])
    avg_marks = sum(d.get("final_marks") or 0 for d in data if d.get("status") == "Graded")
    avg_marks = avg_marks / graded if graded else 0

    return [
        {"value": total, "label": _("Total Submissions"), "datatype": "Int"},
        {"value": graded, "label": _("Graded"), "datatype": "Int", "indicator": "green"},
        {"value": late, "label": _("Late Submissions"), "datatype": "Int", "indicator": "orange"},
        {"value": round(avg_marks, 2), "label": _("Avg Marks"), "datatype": "Float"}
    ]
