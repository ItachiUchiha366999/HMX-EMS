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
        {"fieldname": "quiz", "label": _("Quiz"), "fieldtype": "Link", "options": "LMS Quiz", "width": 150},
        {"fieldname": "attempt_number", "label": _("Attempt"), "fieldtype": "Int", "width": 70},
        {"fieldname": "marks_obtained", "label": _("Marks"), "fieldtype": "Float", "width": 80},
        {"fieldname": "total_marks", "label": _("Total"), "fieldtype": "Float", "width": 80},
        {"fieldname": "percentage", "label": _("Score %"), "fieldtype": "Percent", "width": 100},
        {"fieldname": "passed", "label": _("Passed"), "fieldtype": "Check", "width": 70},
        {"fieldname": "time_taken_minutes", "label": _("Time (min)"), "fieldtype": "Int", "width": 80}
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("lms_course"):
        conditions += " AND q.lms_course = %(lms_course)s"
        values["lms_course"] = filters.get("lms_course")

    if filters.get("quiz"):
        conditions += " AND qa.quiz = %(quiz)s"
        values["quiz"] = filters.get("quiz")

    if filters.get("from_date"):
        conditions += " AND qa.start_time >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND qa.start_time <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    return frappe.db.sql("""
        SELECT
            qa.student,
            s.student_name,
            qa.quiz,
            qa.attempt_number,
            qa.marks_obtained,
            qa.total_marks,
            qa.percentage,
            qa.passed,
            qa.time_taken_minutes
        FROM `tabQuiz Attempt` qa
        INNER JOIN `tabStudent` s ON s.name = qa.student
        INNER JOIN `tabLMS Quiz` q ON q.name = qa.quiz
        WHERE qa.status = 'Graded' {conditions}
        ORDER BY qa.start_time DESC
    """.format(conditions=conditions), values, as_dict=True)


def get_chart(data):
    if not data:
        return None

    # Score distribution
    ranges = {"0-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0}
    for row in data:
        pct = row.get("percentage") or 0
        if pct < 40:
            ranges["0-40%"] += 1
        elif pct < 60:
            ranges["40-60%"] += 1
        elif pct < 80:
            ranges["60-80%"] += 1
        else:
            ranges["80-100%"] += 1

    return {
        "data": {
            "labels": list(ranges.keys()),
            "datasets": [{"name": _("Students"), "values": list(ranges.values())}]
        },
        "type": "bar",
        "colors": ["#ff5858", "#ffa00a", "#5e64ff", "#98d85b"]
    }


def get_summary(data):
    if not data:
        return []

    total = len(data)
    passed = len([d for d in data if d.get("passed")])
    avg_score = sum(d.get("percentage") or 0 for d in data) / total if total else 0
    avg_time = sum(d.get("time_taken_minutes") or 0 for d in data) / total if total else 0

    return [
        {"value": total, "label": _("Total Attempts"), "datatype": "Int"},
        {"value": passed, "label": _("Passed"), "datatype": "Int", "indicator": "green"},
        {"value": round(avg_score, 2), "label": _("Avg Score %"), "datatype": "Percent"},
        {"value": round(avg_time, 1), "label": _("Avg Time (min)"), "datatype": "Float"}
    ]
