"""
CO Attainment Report

Course Outcome attainment analysis report based on internal
assessments, examinations, and practical evaluations.
"""

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data, filters)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "course_outcome",
            "label": _("Course Outcome"),
            "fieldtype": "Link",
            "options": "Course Outcome",
            "width": 150
        },
        {
            "fieldname": "co_code",
            "label": _("CO Code"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "co_description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 250
        },
        {
            "fieldname": "target_attainment",
            "label": _("Target %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "internal_attainment",
            "label": _("Internal %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "exam_attainment",
            "label": _("Exam %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "practical_attainment",
            "label": _("Practical %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "overall_attainment",
            "label": _("Overall %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "attainment_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        }
    ]


def get_data(filters):
    if not filters.get("course") or not filters.get("academic_year"):
        return []

    # Get course outcomes for the course
    course_outcomes = frappe.get_all(
        "Course Outcome",
        filters={"course": filters.get("course")},
        fields=["name", "co_code", "description", "target_attainment"]
    )

    data = []
    for co in course_outcomes:
        row = {
            "course_outcome": co.name,
            "co_code": co.co_code,
            "co_description": co.description[:100] + "..." if len(co.description or "") > 100 else co.description,
            "target_attainment": co.target_attainment or 60,
            "internal_attainment": 0,
            "exam_attainment": 0,
            "practical_attainment": 0,
            "overall_attainment": 0
        }

        # Calculate internal assessment attainment
        internal_scores = get_internal_attainment(co.name, filters)
        row["internal_attainment"] = internal_scores

        # Calculate exam attainment
        exam_scores = get_exam_attainment(co.name, filters)
        row["exam_attainment"] = exam_scores

        # Calculate practical attainment
        practical_scores = get_practical_attainment(co.name, filters)
        row["practical_attainment"] = practical_scores

        # Calculate overall (weighted average)
        components = []
        if row["internal_attainment"] > 0:
            components.append(row["internal_attainment"])
        if row["exam_attainment"] > 0:
            components.append(row["exam_attainment"])
        if row["practical_attainment"] > 0:
            components.append(row["practical_attainment"])

        if components:
            row["overall_attainment"] = sum(components) / len(components)

        # Determine status
        if row["overall_attainment"] >= row["target_attainment"]:
            row["attainment_status"] = "Achieved"
        elif row["overall_attainment"] >= row["target_attainment"] * 0.8:
            row["attainment_status"] = "Partially Achieved"
        else:
            row["attainment_status"] = "Not Achieved"

        data.append(row)

    return data


def get_internal_attainment(course_outcome, filters):
    """Calculate internal assessment attainment for a CO"""
    # Get assessments with this CO mapping
    attainment_data = frappe.db.sql("""
        SELECT
            AVG(ias.percentage) as avg_percentage
        FROM `tabInternal Assessment Score` ias
        INNER JOIN `tabInternal Assessment` ia ON ia.name = ias.parent
        INNER JOIN `tabAssessment CO Link` acl ON acl.parent = ia.name
        WHERE acl.course_outcome = %s
        AND ia.academic_year = %s
        AND ia.course = %s
        AND ia.docstatus = 1
        AND ias.total_marks IS NOT NULL
    """, (course_outcome, filters.get("academic_year"), filters.get("course")), as_dict=True)

    return attainment_data[0].avg_percentage or 0 if attainment_data else 0


def get_exam_attainment(course_outcome, filters):
    """Calculate examination attainment for a CO"""
    # Get questions mapped to this CO and their performance
    attainment_data = frappe.db.sql("""
        SELECT
            AVG(qb.average_score_percentage) as avg_percentage
        FROM `tabQuestion Bank` qb
        WHERE qb.course_outcome = %s
        AND qb.course = %s
        AND qb.average_score_percentage > 0
    """, (course_outcome, filters.get("course")), as_dict=True)

    return attainment_data[0].avg_percentage or 0 if attainment_data else 0


def get_practical_attainment(course_outcome, filters):
    """Calculate practical exam attainment for a CO"""
    attainment_data = frappe.db.sql("""
        SELECT
            AVG(pess.percentage) as avg_percentage
        FROM `tabPractical Exam Student Score` pess
        INNER JOIN `tabPractical Examination` pe ON pe.name = pess.parent
        INNER JOIN `tabPractical Evaluation Criteria` pec ON pec.parent = pe.name
        WHERE pec.co_mapping = %s
        AND pe.academic_year = %s
        AND pe.course = %s
        AND pe.docstatus = 1
        AND pess.total_marks IS NOT NULL
    """, (course_outcome, filters.get("academic_year"), filters.get("course")), as_dict=True)

    return attainment_data[0].avg_percentage or 0 if attainment_data else 0


def get_chart_data(data):
    if not data:
        return None

    return {
        "data": {
            "labels": [d["co_code"] for d in data],
            "datasets": [
                {
                    "name": _("Target"),
                    "values": [d["target_attainment"] for d in data]
                },
                {
                    "name": _("Achieved"),
                    "values": [d["overall_attainment"] for d in data]
                }
            ]
        },
        "type": "bar",
        "colors": ["#bfbfbf", "#5e64ff"]
    }


def get_summary(data, filters):
    if not data:
        return []

    total_cos = len(data)
    achieved = sum(1 for d in data if d["attainment_status"] == "Achieved")
    partially = sum(1 for d in data if d["attainment_status"] == "Partially Achieved")
    not_achieved = sum(1 for d in data if d["attainment_status"] == "Not Achieved")
    avg_attainment = sum(d["overall_attainment"] for d in data) / total_cos if total_cos else 0

    return [
        {
            "value": total_cos,
            "label": _("Total COs"),
            "datatype": "Int"
        },
        {
            "value": achieved,
            "label": _("Achieved"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": partially,
            "label": _("Partially Achieved"),
            "datatype": "Int",
            "indicator": "orange"
        },
        {
            "value": not_achieved,
            "label": _("Not Achieved"),
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": round(avg_attainment, 1),
            "label": _("Avg Attainment %"),
            "datatype": "Percent"
        }
    ]
