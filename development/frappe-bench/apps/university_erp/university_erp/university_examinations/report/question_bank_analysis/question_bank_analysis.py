"""
Question Bank Analysis Report

Provides analysis of question bank including distribution by
difficulty, Bloom's taxonomy, course outcomes, and usage statistics.
"""

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(filters)
    summary = get_summary(filters)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "course",
            "label": _("Course"),
            "fieldtype": "Link",
            "options": "Course",
            "width": 150
        },
        {
            "fieldname": "total_questions",
            "label": _("Total Questions"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "mcq_count",
            "label": _("MCQ"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "msq_count",
            "label": _("MSQ"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "short_answer",
            "label": _("Short Answer"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "long_answer",
            "label": _("Long Answer"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "easy",
            "label": _("Easy"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "medium",
            "label": _("Medium"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "hard",
            "label": _("Hard"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "approved",
            "label": _("Approved"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "pending_review",
            "label": _("Pending Review"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "avg_usage",
            "label": _("Avg Usage"),
            "fieldtype": "Float",
            "precision": 1,
            "width": 100
        }
    ]


def get_data(filters):
    conditions = ""
    if filters.get("course"):
        conditions += " AND qb.course = %(course)s"
    if filters.get("status"):
        conditions += " AND qb.status = %(status)s"

    data = frappe.db.sql("""
        SELECT
            qb.course,
            COUNT(*) as total_questions,
            SUM(CASE WHEN qb.question_type = 'Multiple Choice (MCQ)' THEN 1 ELSE 0 END) as mcq_count,
            SUM(CASE WHEN qb.question_type = 'Multiple Select (MSQ)' THEN 1 ELSE 0 END) as msq_count,
            SUM(CASE WHEN qb.question_type = 'Short Answer' THEN 1 ELSE 0 END) as short_answer,
            SUM(CASE WHEN qb.question_type = 'Long Answer' THEN 1 ELSE 0 END) as long_answer,
            SUM(CASE WHEN qb.difficulty_level = 'Easy' THEN 1 ELSE 0 END) as easy,
            SUM(CASE WHEN qb.difficulty_level = 'Medium' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN qb.difficulty_level IN ('Hard', 'Very Hard') THEN 1 ELSE 0 END) as hard,
            SUM(CASE WHEN qb.status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN qb.status = 'Pending Review' THEN 1 ELSE 0 END) as pending_review,
            AVG(COALESCE(qb.times_used, 0)) as avg_usage
        FROM `tabQuestion Bank` qb
        WHERE 1=1 {conditions}
        GROUP BY qb.course
        ORDER BY total_questions DESC
    """.format(conditions=conditions), filters, as_dict=True)

    return data


def get_chart_data(filters):
    # Get Bloom's taxonomy distribution
    conditions = ""
    if filters.get("course"):
        conditions += " AND course = %(course)s"

    blooms_data = frappe.db.sql("""
        SELECT
            blooms_taxonomy,
            COUNT(*) as count
        FROM `tabQuestion Bank`
        WHERE blooms_taxonomy IS NOT NULL AND blooms_taxonomy != '' {conditions}
        GROUP BY blooms_taxonomy
        ORDER BY
            CASE blooms_taxonomy
                WHEN 'Remember (L1)' THEN 1
                WHEN 'Understand (L2)' THEN 2
                WHEN 'Apply (L3)' THEN 3
                WHEN 'Analyze (L4)' THEN 4
                WHEN 'Evaluate (L5)' THEN 5
                WHEN 'Create (L6)' THEN 6
            END
    """.format(conditions=conditions), filters, as_dict=True)

    return {
        "data": {
            "labels": [d.blooms_taxonomy for d in blooms_data],
            "datasets": [{
                "name": _("Questions by Bloom's Level"),
                "values": [d.count for d in blooms_data]
            }]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(filters):
    conditions = ""
    if filters.get("course"):
        conditions += " AND course = %(course)s"

    totals = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'Pending Review' THEN 1 ELSE 0 END) as pending,
            AVG(COALESCE(times_used, 0)) as avg_usage,
            AVG(COALESCE(average_score_percentage, 0)) as avg_score
        FROM `tabQuestion Bank`
        WHERE 1=1 {conditions}
    """.format(conditions=conditions), filters, as_dict=True)[0]

    return [
        {
            "value": totals.total or 0,
            "label": _("Total Questions"),
            "datatype": "Int"
        },
        {
            "value": totals.approved or 0,
            "label": _("Approved"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": totals.pending or 0,
            "label": _("Pending Review"),
            "datatype": "Int",
            "indicator": "orange"
        },
        {
            "value": round(totals.avg_usage or 0, 1),
            "label": _("Avg Times Used"),
            "datatype": "Float"
        }
    ]
