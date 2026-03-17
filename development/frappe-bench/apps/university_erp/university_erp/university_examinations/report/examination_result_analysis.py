"""
Examination Result Analysis Report

Comprehensive analysis of examination results including
pass/fail rates, grade distribution, and performance trends.
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
            "fieldname": "examination",
            "label": _("Examination"),
            "fieldtype": "Link",
            "options": "Online Examination",
            "width": 200
        },
        {
            "fieldname": "course",
            "label": _("Course"),
            "fieldtype": "Link",
            "options": "Course",
            "width": 150
        },
        {
            "fieldname": "total_attempts",
            "label": _("Total Attempts"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "submitted",
            "label": _("Submitted"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "passed",
            "label": _("Passed"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "failed",
            "label": _("Failed"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "pass_percentage",
            "label": _("Pass %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "avg_score",
            "label": _("Avg Score"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        },
        {
            "fieldname": "highest_score",
            "label": _("Highest"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 80
        },
        {
            "fieldname": "lowest_score",
            "label": _("Lowest"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 80
        },
        {
            "fieldname": "avg_time_mins",
            "label": _("Avg Time (mins)"),
            "fieldtype": "Float",
            "precision": 1,
            "width": 120
        }
    ]


def get_data(filters):
    conditions = ""
    if filters.get("examination"):
        conditions += " AND sea.online_examination = %(examination)s"
    if filters.get("course"):
        conditions += " AND oe.course = %(course)s"
    if filters.get("from_date"):
        conditions += " AND DATE(sea.start_time) >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND DATE(sea.start_time) <= %(to_date)s"

    data = frappe.db.sql("""
        SELECT
            sea.online_examination as examination,
            oe.course,
            COUNT(*) as total_attempts,
            SUM(CASE WHEN sea.status IN ('Submitted', 'Auto Submitted', 'Evaluated') THEN 1 ELSE 0 END) as submitted,
            SUM(CASE WHEN sea.is_passed = 1 THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN sea.is_passed = 0 AND sea.status IN ('Submitted', 'Auto Submitted', 'Evaluated') THEN 1 ELSE 0 END) as failed,
            AVG(sea.score_obtained) as avg_score,
            MAX(sea.score_obtained) as highest_score,
            MIN(CASE WHEN sea.score_obtained > 0 THEN sea.score_obtained ELSE NULL END) as lowest_score,
            AVG(TIMESTAMPDIFF(MINUTE, sea.start_time, sea.end_time)) as avg_time_mins
        FROM `tabStudent Exam Attempt` sea
        INNER JOIN `tabOnline Examination` oe ON oe.name = sea.online_examination
        WHERE 1=1 {conditions}
        GROUP BY sea.online_examination, oe.course
        ORDER BY oe.course, sea.online_examination
    """.format(conditions=conditions), filters, as_dict=True)

    # Calculate pass percentage
    for row in data:
        if row.submitted and row.submitted > 0:
            row.pass_percentage = (row.passed / row.submitted) * 100
        else:
            row.pass_percentage = 0

    return data


def get_chart_data(filters):
    conditions = ""
    if filters.get("examination"):
        conditions += " AND online_examination = %(examination)s"

    # Grade distribution
    grade_data = frappe.db.sql("""
        SELECT
            CASE
                WHEN percentage >= 90 THEN 'A+ (90-100%)'
                WHEN percentage >= 80 THEN 'A (80-89%)'
                WHEN percentage >= 70 THEN 'B (70-79%)'
                WHEN percentage >= 60 THEN 'C (60-69%)'
                WHEN percentage >= 50 THEN 'D (50-59%)'
                ELSE 'F (<50%)'
            END as grade_range,
            COUNT(*) as count
        FROM `tabStudent Exam Attempt`
        WHERE status IN ('Submitted', 'Auto Submitted', 'Evaluated')
        {conditions}
        GROUP BY grade_range
        ORDER BY
            CASE grade_range
                WHEN 'A+ (90-100%)' THEN 1
                WHEN 'A (80-89%)' THEN 2
                WHEN 'B (70-79%)' THEN 3
                WHEN 'C (60-69%)' THEN 4
                WHEN 'D (50-59%)' THEN 5
                ELSE 6
            END
    """.format(conditions=conditions), filters, as_dict=True)

    return {
        "data": {
            "labels": [d.grade_range for d in grade_data],
            "datasets": [{
                "name": _("Students"),
                "values": [d.count for d in grade_data]
            }]
        },
        "type": "bar",
        "colors": ["#28a745", "#17a2b8", "#6c757d", "#ffc107", "#fd7e14", "#dc3545"]
    }


def get_summary(filters):
    conditions = ""
    if filters.get("examination"):
        conditions += " AND online_examination = %(examination)s"

    totals = frappe.db.sql("""
        SELECT
            COUNT(*) as total_attempts,
            SUM(CASE WHEN status IN ('Submitted', 'Auto Submitted', 'Evaluated') THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN is_passed = 1 THEN 1 ELSE 0 END) as passed,
            AVG(score_obtained) as avg_score,
            AVG(percentage) as avg_percentage
        FROM `tabStudent Exam Attempt`
        WHERE 1=1 {conditions}
    """.format(conditions=conditions), filters, as_dict=True)[0]

    pass_rate = (totals.passed / totals.completed * 100) if totals.completed else 0

    return [
        {
            "value": totals.total_attempts or 0,
            "label": _("Total Attempts"),
            "datatype": "Int"
        },
        {
            "value": totals.completed or 0,
            "label": _("Completed"),
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": totals.passed or 0,
            "label": _("Passed"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": round(pass_rate, 1),
            "label": _("Pass Rate %"),
            "datatype": "Percent",
            "indicator": "green" if pass_rate >= 60 else "orange"
        },
        {
            "value": round(totals.avg_percentage or 0, 1),
            "label": _("Avg Score %"),
            "datatype": "Percent"
        }
    ]
