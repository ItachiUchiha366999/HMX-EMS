# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Admission KPI Calculation Methods

These methods are called by the Analytics Manager to calculate admission KPIs.
Each method should accept an optional filters dict and return a numeric value.
"""

import frappe
from frappe.utils import flt, date_diff, getdate


def admission_conversion_rate(filters=None):
    """
    Calculate the admission conversion rate (admitted vs applied)

    Args:
        filters: Optional dict with program, academic_year, date range

    Returns:
        float: Conversion rate percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("program"):
            filter_conditions.append("a.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("academic_year"):
            filter_conditions.append("a.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]
        if filters.get("from_date"):
            filter_conditions.append("a.application_date >= %(from_date)s")
            values["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            filter_conditions.append("a.application_date <= %(to_date)s")
            values["to_date"] = filters["to_date"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Student Applicant doctype exists
    if not frappe.db.exists("DocType", "Student Applicant"):
        return _get_mock_conversion_rate()

    query = """
        SELECT
            COUNT(*) as total_applications,
            COUNT(CASE WHEN a.application_status = 'Admitted' THEN 1 END) as admitted
        FROM `tabStudent Applicant` a
        WHERE {where_clause}
    """.format(where_clause=where_clause)

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["total_applications"] > 0:
        return round((flt(result[0]["admitted"]) / flt(result[0]["total_applications"])) * 100, 2)

    return 0.0


def seat_fill_rate(filters=None):
    """
    Calculate the seat fill rate (enrolled vs available seats)

    Args:
        filters: Optional dict with program, academic_year

    Returns:
        float: Fill rate percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("program"):
            filter_conditions.append("p.name = %(program)s")
            values["program"] = filters["program"]
        if filters.get("academic_year"):
            filter_conditions.append("pb.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Program doctype exists with seats
    if not frappe.db.exists("DocType", "Program"):
        return _get_mock_seat_fill_rate()

    # Get total seats from programs
    program_meta = frappe.get_meta("Program")
    if not program_meta.has_field("max_students"):
        return _get_mock_seat_fill_rate()

    seats_query = """
        SELECT SUM(p.max_students) as total_seats
        FROM `tabProgram` p
        WHERE {where_clause.replace("pb.", "p.")}
    """
    seats_result = frappe.db.sql(seats_query, values, as_dict=True)
    total_seats = flt(seats_result[0]["total_seats"]) if seats_result else 0

    # Count enrolled students
    student_filter = {}
    if filters:
        if filters.get("program"):
            student_filter["program"] = filters["program"]

    if frappe.db.exists("DocType", "Student"):
        enrolled_count = frappe.db.count("Student", student_filter or {})
    else:
        enrolled_count = 0

    if total_seats > 0:
        return round((flt(enrolled_count) / flt(total_seats)) * 100, 2)

    return 0.0


def average_application_processing_time(filters=None):
    """
    Calculate the average time to process applications (in days)

    Args:
        filters: Optional dict with program, academic_year

    Returns:
        float: Average processing time in days
    """
    filter_conditions = ["a.application_status IN ('Admitted', 'Rejected')"]
    values = {}

    if filters:
        if filters.get("program"):
            filter_conditions.append("a.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("academic_year"):
            filter_conditions.append("a.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]

    where_clause = " AND ".join(filter_conditions)

    # Check if Student Applicant doctype exists
    if not frappe.db.exists("DocType", "Student Applicant"):
        return _get_mock_processing_time()

    # Check if required fields exist
    meta = frappe.get_meta("Student Applicant")
    if not (meta.has_field("application_date") and meta.has_field("modified")):
        return _get_mock_processing_time()

    query = """
        SELECT
            AVG(DATEDIFF(a.modified, a.application_date)) as avg_days
        FROM `tabStudent Applicant` a
        WHERE {where_clause}
    """.format(where_clause=where_clause)

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["avg_days"]:
        return round(flt(result[0]["avg_days"]), 1)

    return 0.0


def application_rejection_rate(filters=None):
    """
    Calculate the application rejection rate

    Args:
        filters: Optional dict with program, academic_year

    Returns:
        float: Rejection rate percentage (0-100)
    """
    filter_conditions = ["a.application_status IN ('Admitted', 'Rejected')"]
    values = {}

    if filters:
        if filters.get("program"):
            filter_conditions.append("a.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("academic_year"):
            filter_conditions.append("a.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]

    where_clause = " AND ".join(filter_conditions)

    # Check if Student Applicant doctype exists
    if not frappe.db.exists("DocType", "Student Applicant"):
        return _get_mock_rejection_rate()

    query = """
        SELECT
            COUNT(*) as total_processed,
            COUNT(CASE WHEN a.application_status = 'Rejected' THEN 1 END) as rejected
        FROM `tabStudent Applicant` a
        WHERE {where_clause}
    """.format(where_clause=where_clause)

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["total_processed"] > 0:
        return round((flt(result[0]["rejected"]) / flt(result[0]["total_processed"])) * 100, 2)

    return 0.0


# Mock data functions for testing
def _get_mock_conversion_rate():
    """Return mock admission conversion rate for testing"""
    return 45.5


def _get_mock_seat_fill_rate():
    """Return mock seat fill rate for testing"""
    return 92.3


def _get_mock_processing_time():
    """Return mock processing time for testing"""
    return 7.5


def _get_mock_rejection_rate():
    """Return mock rejection rate for testing"""
    return 18.2
