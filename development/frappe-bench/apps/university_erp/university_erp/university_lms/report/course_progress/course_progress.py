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
        {"fieldname": "content_completed", "label": _("Content Completed"), "fieldtype": "Int", "width": 120},
        {"fieldname": "total_content", "label": _("Total Content"), "fieldtype": "Int", "width": 100},
        {"fieldname": "assignments_submitted", "label": _("Assignments"), "fieldtype": "Int", "width": 100},
        {"fieldname": "quizzes_attempted", "label": _("Quizzes"), "fieldtype": "Int", "width": 100},
        {"fieldname": "avg_quiz_score", "label": _("Avg Quiz %"), "fieldtype": "Percent", "width": 100},
        {"fieldname": "overall_progress", "label": _("Overall Progress"), "fieldtype": "Percent", "width": 120}
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("lms_course"):
        conditions += " AND lcp.lms_course = %(lms_course)s"
        values["lms_course"] = filters.get("lms_course")

    if filters.get("academic_term"):
        conditions += " AND lc.academic_term = %(academic_term)s"
        values["academic_term"] = filters.get("academic_term")

    # Get students with progress records
    data = frappe.db.sql("""
        SELECT
            lcp.student,
            s.student_name,
            SUM(CASE WHEN lcp.status = 'Completed' THEN 1 ELSE 0 END) as content_completed,
            COUNT(lcp.name) as total_content,
            0 as assignments_submitted,
            0 as quizzes_attempted,
            0 as avg_quiz_score,
            ROUND(SUM(CASE WHEN lcp.status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(lcp.name), 2) as overall_progress
        FROM `tabLMS Content Progress` lcp
        INNER JOIN `tabStudent` s ON s.name = lcp.student
        INNER JOIN `tabLMS Course` lc ON lc.name = lcp.lms_course
        WHERE 1=1 {conditions}
        GROUP BY lcp.student, s.student_name
        ORDER BY overall_progress DESC
    """.format(conditions=conditions), values, as_dict=True)

    # Add assignment and quiz data
    for row in data:
        lms_course = filters.get("lms_course")
        if lms_course:
            # Get assignment submissions
            row["assignments_submitted"] = frappe.db.count("Assignment Submission", {
                "student": row["student"]
            })

            # Get quiz attempts
            quiz_data = frappe.db.sql("""
                SELECT COUNT(*) as attempts, AVG(percentage) as avg_score
                FROM `tabQuiz Attempt`
                WHERE student = %s AND status = 'Graded'
            """, row["student"], as_dict=True)

            if quiz_data:
                row["quizzes_attempted"] = quiz_data[0].get("attempts") or 0
                row["avg_quiz_score"] = quiz_data[0].get("avg_score") or 0

    return data


def get_chart(data):
    if not data:
        return None

    # Progress distribution
    ranges = {"0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0}
    for row in data:
        progress = row.get("overall_progress") or 0
        if progress <= 25:
            ranges["0-25%"] += 1
        elif progress <= 50:
            ranges["25-50%"] += 1
        elif progress <= 75:
            ranges["50-75%"] += 1
        else:
            ranges["75-100%"] += 1

    return {
        "data": {
            "labels": list(ranges.keys()),
            "datasets": [{"name": _("Students"), "values": list(ranges.values())}]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data):
    if not data:
        return []

    total_students = len(data)
    avg_progress = sum(row.get("overall_progress") or 0 for row in data) / total_students if total_students else 0
    completed = len([row for row in data if (row.get("overall_progress") or 0) >= 100])

    return [
        {"value": total_students, "label": _("Total Students"), "datatype": "Int"},
        {"value": round(avg_progress, 2), "label": _("Avg Progress %"), "datatype": "Percent"},
        {"value": completed, "label": _("Completed"), "datatype": "Int", "indicator": "green"}
    ]
