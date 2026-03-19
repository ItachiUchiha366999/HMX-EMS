# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Academic KPI Calculation Methods

These methods are called by the Analytics Manager to calculate academic KPIs.
Each method should accept an optional filters dict and return a numeric value.
"""

import frappe
from frappe.utils import flt, cint


def student_pass_percentage(filters=None):
    """
    Calculate the percentage of students who passed their exams

    Args:
        filters: Optional dict with department, program, academic_year

    Returns:
        float: Pass percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("department"):
            filter_conditions.append("s.department = %(department)s")
            values["department"] = filters["department"]
        if filters.get("program"):
            filter_conditions.append("s.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("academic_year"):
            filter_conditions.append("er.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Exam Result doctype exists
    if not frappe.db.exists("DocType", "Exam Result"):
        return _get_mock_pass_percentage()

    query = """
        SELECT
            COUNT(CASE WHEN er.result = 'Pass' THEN 1 END) as passed,
            COUNT(*) as total
        FROM `tabExam Result` er
        LEFT JOIN `tabStudent` s ON er.student = s.name
        WHERE {where_clause}
    """.format(where_clause=where_clause)

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["total"] > 0:
        return (flt(result[0]["passed"]) / flt(result[0]["total"])) * 100

    return 0.0


def average_cgpa(filters=None):
    """
    Calculate the average CGPA of all students

    Args:
        filters: Optional dict with department, program, academic_year

    Returns:
        float: Average CGPA
    """
    filter_conditions = ["s.cgpa IS NOT NULL", "s.cgpa > 0"]
    values = {}

    if filters:
        if filters.get("department"):
            filter_conditions.append("s.department = %(department)s")
            values["department"] = filters["department"]
        if filters.get("program"):
            filter_conditions.append("s.program = %(program)s")
            values["program"] = filters["program"]

    where_clause = " AND ".join(filter_conditions)

    # Check if Student doctype has cgpa field
    if not frappe.db.exists("DocType", "Student"):
        return _get_mock_cgpa()

    meta = frappe.get_meta("Student")
    if not meta.has_field("cgpa"):
        return _get_mock_cgpa()

    query = """
        SELECT AVG(s.cgpa) as avg_cgpa
        FROM `tabStudent` s
        WHERE {where_clause}
    """.format(where_clause=where_clause)

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["avg_cgpa"]:
        return round(flt(result[0]["avg_cgpa"]), 2)

    return 0.0


def student_attendance_rate(filters=None):
    """
    Calculate the average student attendance rate

    Args:
        filters: Optional dict with department, program, academic_year, date range

    Returns:
        float: Attendance percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("department"):
            filter_conditions.append("s.department = %(department)s")
            values["department"] = filters["department"]
        if filters.get("program"):
            filter_conditions.append("s.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("from_date"):
            filter_conditions.append("a.attendance_date >= %(from_date)s")
            values["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            filter_conditions.append("a.attendance_date <= %(to_date)s")
            values["to_date"] = filters["to_date"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Student Attendance doctype exists
    if not frappe.db.exists("DocType", "Student Attendance"):
        return _get_mock_attendance_rate()

    query = """
        SELECT
            COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as present,
            COUNT(*) as total
        FROM `tabStudent Attendance` a
        LEFT JOIN `tabStudent` s ON a.student = s.name
        WHERE {where_clause}
    """.format(where_clause=where_clause)

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["total"] > 0:
        return round((flt(result[0]["present"]) / flt(result[0]["total"])) * 100, 2)

    return 0.0


def faculty_student_ratio(filters=None):
    """
    Calculate the faculty to student ratio

    Args:
        filters: Optional dict with department

    Returns:
        float: Ratio (e.g., 25 means 1:25)
    """
    filter_conditions_faculty = []
    filter_conditions_student = []
    values = {}

    if filters:
        if filters.get("department"):
            filter_conditions_faculty.append("department = %(department)s")
            filter_conditions_student.append("department = %(department)s")
            values["department"] = filters["department"]

    where_faculty = " AND ".join(filter_conditions_faculty) if filter_conditions_faculty else "1=1"
    where_student = " AND ".join(filter_conditions_student) if filter_conditions_student else "1=1"

    # Count faculty
    if frappe.db.exists("DocType", "Instructor"):
        faculty_count = frappe.db.count("Instructor", where_faculty if filter_conditions_faculty else {})
    else:
        faculty_count = 50  # Mock value

    # Count students
    if frappe.db.exists("DocType", "Student"):
        student_filter = {}
        if filters and filters.get("department"):
            student_filter["department"] = filters["department"]
        student_count = frappe.db.count("Student", student_filter or {})
    else:
        student_count = 1000  # Mock value

    if faculty_count > 0:
        return round(flt(student_count) / flt(faculty_count), 1)

    return 0.0


def course_completion_rate(filters=None):
    """
    Calculate the course completion rate

    Args:
        filters: Optional dict with department, program, academic_year

    Returns:
        float: Completion percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("department"):
            filter_conditions.append("c.department = %(department)s")
            values["department"] = filters["department"]
        if filters.get("program"):
            filter_conditions.append("ce.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("academic_year"):
            filter_conditions.append("ce.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Course Enrollment doctype exists
    if not frappe.db.exists("DocType", "Course Enrollment"):
        return _get_mock_completion_rate()

    query = """
        SELECT
            COUNT(CASE WHEN ce.status = 'Completed' THEN 1 END) as completed,
            COUNT(*) as total
        FROM `tabCourse Enrollment` ce
        LEFT JOIN `tabCourse` c ON ce.course = c.name
        WHERE {where_clause}
    """.format(where_clause=where_clause)

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["total"] > 0:
        return round((flt(result[0]["completed"]) / flt(result[0]["total"])) * 100, 2)

    return 0.0


# Mock data functions for testing when real data isn't available
def _get_mock_pass_percentage():
    """Return mock pass percentage for testing"""
    return 85.5


def _get_mock_cgpa():
    """Return mock CGPA for testing"""
    return 7.8


def _get_mock_attendance_rate():
    """Return mock attendance rate for testing"""
    return 82.3


def _get_mock_completion_rate():
    """Return mock completion rate for testing"""
    return 78.5
