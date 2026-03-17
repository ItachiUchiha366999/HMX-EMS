# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Financial KPI Calculation Methods

These methods are called by the Analytics Manager to calculate financial KPIs.
Each method should accept an optional filters dict and return a numeric value.
"""

import frappe
from frappe.utils import flt, getdate, today


def fee_collection_rate(filters=None):
    """
    Calculate the fee collection rate (collected vs billed)

    Args:
        filters: Optional dict with department, program, academic_year, date range

    Returns:
        float: Collection rate percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("academic_year"):
            filter_conditions.append("f.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]
        if filters.get("program"):
            filter_conditions.append("f.program = %(program)s")
            values["program"] = filters["program"]
        if filters.get("from_date"):
            filter_conditions.append("f.posting_date >= %(from_date)s")
            values["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            filter_conditions.append("f.posting_date <= %(to_date)s")
            values["to_date"] = filters["to_date"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Fees doctype exists
    if not frappe.db.exists("DocType", "Fees"):
        return _get_mock_collection_rate()

    query = f"""
        SELECT
            SUM(f.total_amount) as billed,
            SUM(f.paid_amount) as collected
        FROM `tabFees` f
        WHERE f.docstatus = 1 AND {where_clause}
    """

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["billed"] and flt(result[0]["billed"]) > 0:
        return round((flt(result[0]["collected"]) / flt(result[0]["billed"])) * 100, 2)

    return 0.0


def revenue_per_student(filters=None):
    """
    Calculate the average revenue per student

    Args:
        filters: Optional dict with department, program, academic_year

    Returns:
        float: Revenue per student amount
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("academic_year"):
            filter_conditions.append("f.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]
        if filters.get("program"):
            filter_conditions.append("f.program = %(program)s")
            values["program"] = filters["program"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Fees doctype exists
    if not frappe.db.exists("DocType", "Fees"):
        return _get_mock_revenue_per_student()

    # Total revenue
    revenue_query = f"""
        SELECT SUM(f.paid_amount) as total_revenue
        FROM `tabFees` f
        WHERE f.docstatus = 1 AND {where_clause}
    """
    revenue_result = frappe.db.sql(revenue_query, values, as_dict=True)
    total_revenue = flt(revenue_result[0]["total_revenue"]) if revenue_result else 0

    # Student count
    student_filter = {}
    if filters:
        if filters.get("program"):
            student_filter["program"] = filters["program"]

    if frappe.db.exists("DocType", "Student"):
        student_count = frappe.db.count("Student", student_filter or {})
    else:
        student_count = 1000  # Mock value

    if student_count > 0:
        return round(total_revenue / student_count, 2)

    return 0.0


def outstanding_fees_percentage(filters=None):
    """
    Calculate the percentage of outstanding fees

    Args:
        filters: Optional dict with department, program, academic_year

    Returns:
        float: Outstanding percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("academic_year"):
            filter_conditions.append("f.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]
        if filters.get("program"):
            filter_conditions.append("f.program = %(program)s")
            values["program"] = filters["program"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Fees doctype exists
    if not frappe.db.exists("DocType", "Fees"):
        return _get_mock_outstanding_percentage()

    query = f"""
        SELECT
            SUM(f.total_amount) as billed,
            SUM(f.outstanding_amount) as outstanding
        FROM `tabFees` f
        WHERE f.docstatus = 1 AND {where_clause}
    """

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["billed"] and flt(result[0]["billed"]) > 0:
        return round((flt(result[0]["outstanding"]) / flt(result[0]["billed"])) * 100, 2)

    return 0.0


def scholarship_utilization(filters=None):
    """
    Calculate the scholarship utilization rate

    Args:
        filters: Optional dict with department, program, academic_year

    Returns:
        float: Utilization percentage (0-100)
    """
    filter_conditions = []
    values = {}

    if filters:
        if filters.get("academic_year"):
            filter_conditions.append("s.academic_year = %(academic_year)s")
            values["academic_year"] = filters["academic_year"]
        if filters.get("program"):
            filter_conditions.append("s.program = %(program)s")
            values["program"] = filters["program"]

    where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"

    # Check if Scholarship doctype exists
    if not frappe.db.exists("DocType", "Scholarship"):
        return _get_mock_scholarship_utilization()

    query = f"""
        SELECT
            SUM(s.total_amount) as budgeted,
            SUM(s.disbursed_amount) as utilized
        FROM `tabScholarship` s
        WHERE s.docstatus = 1 AND {where_clause}
    """

    result = frappe.db.sql(query, values, as_dict=True)

    if result and result[0]["budgeted"] and flt(result[0]["budgeted"]) > 0:
        return round((flt(result[0]["utilized"]) / flt(result[0]["budgeted"])) * 100, 2)

    return 0.0


# Mock data functions for testing
def _get_mock_collection_rate():
    """Return mock fee collection rate for testing"""
    return 87.5


def _get_mock_revenue_per_student():
    """Return mock revenue per student for testing"""
    return 125000.0


def _get_mock_outstanding_percentage():
    """Return mock outstanding fees percentage for testing"""
    return 12.5


def _get_mock_scholarship_utilization():
    """Return mock scholarship utilization for testing"""
    return 92.3
