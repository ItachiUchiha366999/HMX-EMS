# Copyright (c) 2026, University and contributors
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
        {
            "label": _("Faculty"),
            "fieldname": "instructor",
            "fieldtype": "Link",
            "options": "Instructor",
            "width": 200
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Courses"),
            "fieldname": "courses",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Responses"),
            "fieldname": "responses",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Avg Score"),
            "fieldname": "avg_score",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("Content"),
            "fieldname": "content_score",
            "fieldtype": "Percent",
            "width": 90
        },
        {
            "label": _("Teaching"),
            "fieldname": "teaching_score",
            "fieldtype": "Percent",
            "width": 90
        },
        {
            "label": _("NPS"),
            "fieldname": "nps",
            "fieldtype": "Float",
            "width": 80,
            "precision": 1
        }
    ]


def get_data(filters):
    filters = filters or {}
    conditions, values = get_conditions(filters)

    having_clause = ""
    if filters.get("min_rating"):
        having_clause = " HAVING avg_score >= %(min_rating)s"
        values["min_rating"] = filters.get("min_rating")

    data = frappe.db.sql("""
        SELECT
            fr.instructor,
            inst.department,
            COUNT(DISTINCT fr.course) as courses,
            COUNT(*) as responses,
            AVG(fr.overall_score) as avg_score,
            AVG(CASE WHEN fss.section_name LIKE '%%Content%%' THEN fss.score END) as content_score,
            AVG(CASE WHEN fss.section_name LIKE '%%Teaching%%' THEN fss.score END) as teaching_score,
            (SUM(CASE WHEN fr.nps_category = 'Promoter' THEN 1 ELSE 0 END) -
             SUM(CASE WHEN fr.nps_category = 'Detractor' THEN 1 ELSE 0 END)) * 100.0 / COUNT(*) as nps
        FROM `tabFeedback Response` fr
        JOIN `tabFeedback Form` ff ON fr.feedback_form = ff.name
        LEFT JOIN `tabInstructor` inst ON fr.instructor = inst.name
        LEFT JOIN `tabFeedback Section Score` fss ON fss.parent = fr.name
        WHERE fr.status = 'Valid'
        AND ff.form_type IN ('Course Feedback', 'Faculty Feedback')
        AND fr.instructor IS NOT NULL
        {conditions}
        GROUP BY fr.instructor, inst.department
        {having_clause}
        ORDER BY avg_score DESC
    """.format(conditions=conditions, having_clause=having_clause), values, as_dict=True)

    return data


def get_conditions(filters):
    """Build parameterised condition string + values dict."""
    conditions = ""
    values = {}

    if filters.get("academic_term"):
        conditions += " AND ff.academic_term = %(academic_term)s"
        values["academic_term"] = filters.get("academic_term")
    if filters.get("department"):
        conditions += " AND inst.department = %(department)s"
        values["department"] = filters.get("department")
    if filters.get("instructor"):
        conditions += " AND fr.instructor = %(instructor)s"
        values["instructor"] = filters.get("instructor")
    if filters.get("from_date"):
        conditions += " AND fr.creation >= %(from_date)s"
        values["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions += " AND fr.creation <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    return conditions, values


def get_chart(data):
    if not data or len(data) == 0:
        return None

    # Top 10 faculty by score
    top_data = data[:10]

    return {
        "data": {
            "labels": [d.instructor[:20] if d.instructor else "Unknown" for d in top_data],
            "datasets": [
                {
                    "name": _("Overall Score"),
                    "values": [d.avg_score or 0 for d in top_data]
                },
                {
                    "name": _("Teaching Score"),
                    "values": [d.teaching_score or 0 for d in top_data]
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#28a745"]
    }
