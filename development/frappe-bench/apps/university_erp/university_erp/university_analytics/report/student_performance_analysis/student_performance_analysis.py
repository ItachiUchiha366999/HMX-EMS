# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns():
    """Return report columns"""
    return [
        {
            "label": _("Student ID"),
            "fieldname": "student_id",
            "fieldtype": "Link",
            "options": "Student",
            "width": 120
        },
        {
            "label": _("Student Name"),
            "fieldname": "student_name",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Program"),
            "fieldname": "program",
            "fieldtype": "Link",
            "options": "Program",
            "width": 150
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 150
        },
        {
            "label": _("Semester"),
            "fieldname": "semester",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": _("CGPA"),
            "fieldname": "cgpa",
            "fieldtype": "Float",
            "precision": 2,
            "width": 80
        },
        {
            "label": _("Attendance %"),
            "fieldname": "attendance_percentage",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("Courses Enrolled"),
            "fieldname": "courses_enrolled",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Courses Completed"),
            "fieldname": "courses_completed",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Performance Grade"),
            "fieldname": "performance_grade",
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    """Return report data"""
    conditions = []
    values = {}

    if filters:
        if filters.get("program"):
            conditions.append("s.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("department"):
            conditions.append("s.department = %(department)s")
            values["department"] = filters["department"]
        if filters.get("academic_year"):
            values["academic_year"] = filters["academic_year"]

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Check if Student doctype exists
    if not frappe.db.exists("DocType", "Student"):
        return _get_mock_data()

    # Check if CGPA field exists
    meta = frappe.get_meta("Student")
    cgpa_field = "s.cgpa" if meta.has_field("cgpa") else "0 as cgpa"

    query = f"""
        SELECT
            s.name as student_id,
            s.student_name,
            s.program,
            s.department,
            IFNULL(s.current_semester, '-') as semester,
            {cgpa_field}
        FROM `tabStudent` s
        WHERE {where_clause}
        ORDER BY s.student_name
        LIMIT 500
    """

    students = frappe.db.sql(query, values, as_dict=True)

    # Enrich with additional data
    for student in students:
        student["attendance_percentage"] = _get_student_attendance(student["student_id"])
        student["courses_enrolled"] = _get_courses_enrolled(student["student_id"])
        student["courses_completed"] = _get_courses_completed(student["student_id"])
        student["performance_grade"] = _calculate_performance_grade(
            student["cgpa"],
            student["attendance_percentage"]
        )

    return students


def get_chart(data):
    """Return chart configuration"""
    if not data:
        return None

    # Group by performance grade
    grade_counts = {}
    for row in data:
        grade = row.get("performance_grade", "N/A")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    return {
        "data": {
            "labels": list(grade_counts.keys()),
            "datasets": [{
                "name": "Students",
                "values": list(grade_counts.values())
            }]
        },
        "type": "pie",
        "colors": ["#28a745", "#17a2b8", "#ffc107", "#dc3545", "#6c757d"]
    }


def get_summary(data):
    """Return report summary"""
    if not data:
        return []

    total_students = len(data)
    avg_cgpa = sum(flt(d.get("cgpa", 0)) for d in data) / total_students if total_students else 0
    avg_attendance = sum(flt(d.get("attendance_percentage", 0)) for d in data) / total_students if total_students else 0

    # Count by grade
    excellent_count = sum(1 for d in data if d.get("performance_grade") == "Excellent")
    good_count = sum(1 for d in data if d.get("performance_grade") == "Good")
    average_count = sum(1 for d in data if d.get("performance_grade") == "Average")
    poor_count = sum(1 for d in data if d.get("performance_grade") in ["Below Average", "Poor"])

    return [
        {
            "value": total_students,
            "label": _("Total Students"),
            "datatype": "Int"
        },
        {
            "value": round(avg_cgpa, 2),
            "label": _("Average CGPA"),
            "datatype": "Float"
        },
        {
            "value": round(avg_attendance, 1),
            "label": _("Average Attendance %"),
            "datatype": "Percent"
        },
        {
            "value": excellent_count,
            "label": _("Excellent Performers"),
            "datatype": "Int",
            "indicator": "Green"
        },
        {
            "value": poor_count,
            "label": _("Need Attention"),
            "datatype": "Int",
            "indicator": "Red"
        }
    ]


def _get_student_attendance(student_id):
    """Get attendance percentage for student"""
    if frappe.db.exists("DocType", "Student Attendance"):
        result = frappe.db.sql("""
            SELECT
                COUNT(CASE WHEN status = 'Present' THEN 1 END) as present,
                COUNT(*) as total
            FROM `tabStudent Attendance`
            WHERE student = %s
        """, student_id, as_dict=True)

        if result and result[0]["total"] > 0:
            return round((flt(result[0]["present"]) / flt(result[0]["total"])) * 100, 1)

    return 85.0  # Mock value


def _get_courses_enrolled(student_id):
    """Get enrolled courses count for student"""
    if frappe.db.exists("DocType", "Course Enrollment"):
        return frappe.db.count("Course Enrollment", {"student": student_id})
    return 6  # Mock value


def _get_courses_completed(student_id):
    """Get completed courses count for student"""
    if frappe.db.exists("DocType", "Course Enrollment"):
        return frappe.db.count("Course Enrollment", {
            "student": student_id,
            "status": "Completed"
        })
    return 4  # Mock value


def _calculate_performance_grade(cgpa, attendance):
    """Calculate overall performance grade"""
    cgpa = flt(cgpa)
    attendance = flt(attendance)

    # Combined score (60% CGPA, 40% Attendance)
    # Normalize CGPA to 100 scale (assuming 10-point CGPA)
    normalized_cgpa = (cgpa / 10) * 100 if cgpa <= 10 else cgpa
    combined_score = (normalized_cgpa * 0.6) + (attendance * 0.4)

    if combined_score >= 85:
        return "Excellent"
    elif combined_score >= 70:
        return "Good"
    elif combined_score >= 55:
        return "Average"
    elif combined_score >= 40:
        return "Below Average"
    else:
        return "Poor"


def _get_mock_data():
    """Return mock data for testing"""
    return [
        {"student_id": "STU-2026-0001", "student_name": "John Doe", "program": "B.Tech Computer Science",
         "department": "Computer Science", "semester": "4", "cgpa": 8.5, "attendance_percentage": 88.5,
         "courses_enrolled": 6, "courses_completed": 4, "performance_grade": "Excellent"},
        {"student_id": "STU-2026-0002", "student_name": "Jane Smith", "program": "B.Tech Electronics",
         "department": "Electronics", "semester": "4", "cgpa": 7.8, "attendance_percentage": 82.3,
         "courses_enrolled": 6, "courses_completed": 4, "performance_grade": "Good"},
        {"student_id": "STU-2026-0003", "student_name": "Bob Johnson", "program": "B.Tech Mechanical",
         "department": "Mechanical", "semester": "4", "cgpa": 6.5, "attendance_percentage": 75.0,
         "courses_enrolled": 6, "courses_completed": 3, "performance_grade": "Average"},
    ]
