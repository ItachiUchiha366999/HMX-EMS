"""
Internal Assessment Summary Report

Summary of internal assessments including student-wise
performance across all assessment types for a course.
"""

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    summary = get_summary(data, filters)

    return columns, data, None, chart, summary


def get_columns(filters):
    columns = [
        {
            "fieldname": "student",
            "label": _("Student"),
            "fieldtype": "Link",
            "options": "Student",
            "width": 120
        },
        {
            "fieldname": "student_name",
            "label": _("Student Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "roll_number",
            "label": _("Roll No"),
            "fieldtype": "Data",
            "width": 100
        }
    ]

    # Get assessments for dynamic columns
    if filters.get("course") and filters.get("academic_year"):
        assessments = frappe.get_all(
            "Internal Assessment",
            filters={
                "course": filters.get("course"),
                "academic_year": filters.get("academic_year"),
                "academic_term": filters.get("academic_term") if filters.get("academic_term") else ["is", "set"]
            },
            fields=["name", "assessment_name", "assessment_type", "maximum_marks"],
            order_by="assessment_date"
        )

        for assessment in assessments:
            columns.append({
                "fieldname": assessment.name,
                "label": f"{assessment.assessment_type[:3]}-{assessment.maximum_marks}",
                "fieldtype": "Float",
                "precision": 1,
                "width": 80
            })

    columns.extend([
        {
            "fieldname": "total_marks",
            "label": _("Total"),
            "fieldtype": "Float",
            "precision": 1,
            "width": 80
        },
        {
            "fieldname": "max_marks",
            "label": _("Max"),
            "fieldtype": "Float",
            "precision": 1,
            "width": 80
        },
        {
            "fieldname": "percentage",
            "label": _("Percentage"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "grade",
            "label": _("Grade"),
            "fieldtype": "Data",
            "width": 80
        }
    ])

    return columns


def get_data(filters):
    if not filters.get("course") or not filters.get("academic_year"):
        return []

    # Get all assessments
    term_filter = ""
    if filters.get("academic_term"):
        term_filter = "AND ia.academic_term = %(academic_term)s"

    assessments = frappe.db.sql("""
        SELECT name, assessment_name, assessment_type, maximum_marks
        FROM `tabInternal Assessment`
        WHERE course = %(course)s
        AND academic_year = %(academic_year)s
        {term_filter}
        ORDER BY assessment_date
    """.format(term_filter=term_filter), filters, as_dict=True)

    if not assessments:
        return []

    # Get students enrolled in the course
    students = frappe.db.sql("""
        SELECT
            s.name as student,
            s.student_name,
            s.roll_number
        FROM `tabStudent` s
        INNER JOIN `tabCourse Enrollment` ce ON ce.student = s.name
        WHERE ce.course = %(course)s
        AND ce.academic_year = %(academic_year)s
        AND ce.enrollment_status = 'Enrolled'
        ORDER BY s.roll_number
    """, filters, as_dict=True)

    # Get scores for each student
    data = []
    total_max_marks = sum(a.maximum_marks or 0 for a in assessments)

    for student in students:
        row = {
            "student": student.student,
            "student_name": student.student_name,
            "roll_number": student.roll_number,
            "total_marks": 0,
            "max_marks": total_max_marks
        }

        for assessment in assessments:
            score = frappe.db.get_value(
                "Internal Assessment Score",
                {"parent": assessment.name, "student": student.student},
                "total_marks"
            )
            row[assessment.name] = score
            row["total_marks"] += score or 0

        row["percentage"] = (row["total_marks"] / row["max_marks"] * 100) if row["max_marks"] else 0
        row["grade"] = get_grade(row["percentage"], filters.get("grading_scale"))

        data.append(row)

    return data


def get_grade(percentage, grading_scale=None):
    """Get grade from percentage"""
    if not grading_scale:
        # Default grading
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"
        else:
            return "F"

    intervals = frappe.get_all(
        "Grading Scale Interval",
        filters={"parent": grading_scale},
        fields=["grade_code", "threshold"],
        order_by="threshold desc"
    )

    for interval in intervals:
        if percentage >= interval.threshold:
            return interval.grade_code

    return intervals[-1].grade_code if intervals else "F"


def get_chart_data(data, filters):
    if not data:
        return None

    # Grade distribution
    grade_counts = {}
    for row in data:
        grade = row.get("grade", "F")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    return {
        "data": {
            "labels": list(grade_counts.keys()),
            "datasets": [{
                "name": _("Students"),
                "values": list(grade_counts.values())
            }]
        },
        "type": "pie",
        "colors": ["#28a745", "#17a2b8", "#6c757d", "#ffc107", "#fd7e14", "#dc3545"]
    }


def get_summary(data, filters):
    if not data:
        return []

    total_students = len(data)
    percentages = [d["percentage"] for d in data]
    avg_percentage = sum(percentages) / total_students if total_students else 0
    passed = sum(1 for p in percentages if p >= 50)

    return [
        {
            "value": total_students,
            "label": _("Total Students"),
            "datatype": "Int"
        },
        {
            "value": passed,
            "label": _("Passed"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": total_students - passed,
            "label": _("Failed"),
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": round(avg_percentage, 1),
            "label": _("Avg %"),
            "datatype": "Percent"
        },
        {
            "value": round(max(percentages), 1) if percentages else 0,
            "label": _("Highest %"),
            "datatype": "Percent"
        }
    ]
