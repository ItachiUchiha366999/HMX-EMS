# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Executive Dashboard Methods

Provides high-level metrics and visualizations for university leadership.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, today, add_months, add_days, get_first_day, get_last_day


@frappe.whitelist()
def get_executive_dashboard_data(filters=None):
    """
    Get all data for the executive dashboard

    Args:
        filters: Optional dict with date_range, academic_year

    Returns:
        dict: Complete dashboard data
    """
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    return {
        "overview": get_overview_metrics(filters),
        "enrollment_trend": get_enrollment_trend(filters),
        "financial_summary": get_financial_summary(filters),
        "department_performance": get_department_performance(filters),
        "alerts": get_alerts(filters),
        "kpi_summary": get_kpi_summary(filters)
    }


def get_overview_metrics(filters=None):
    """
    Get overview metrics for the dashboard

    Args:
        filters: Optional filters

    Returns:
        dict: Key metrics
    """
    metrics = {
        "total_students": _get_total_students(filters),
        "total_faculty": _get_total_faculty(filters),
        "total_programs": _get_total_programs(),
        "total_courses": _get_total_courses(),
        "active_batches": _get_active_batches(filters),
        "pending_grievances": _get_pending_grievances(),
        "upcoming_exams": _get_upcoming_exams(),
        "fee_collection_today": _get_fee_collection_today()
    }

    # Add comparison with previous period
    metrics["student_change"] = _calculate_change(
        metrics["total_students"],
        _get_total_students(filters, previous_period=True)
    )

    return metrics


def get_enrollment_trend(filters=None):
    """
    Get student enrollment trend data

    Args:
        filters: Optional filters

    Returns:
        dict: Enrollment trend data for chart
    """
    months = []
    enrollment_data = []

    today_date = getdate(today())

    for i in range(11, -1, -1):
        month_date = add_months(today_date, -i)
        month_start = get_first_day(month_date)
        month_end = get_last_day(month_date)

        months.append(month_date.strftime("%b %Y"))

        # Get enrollment count for month
        if frappe.db.exists("DocType", "Student"):
            count = frappe.db.count(
                "Student",
                filters={
                    "creation": ["between", [month_start, month_end]]
                }
            )
        else:
            # Mock data
            count = 50 + (12 - i) * 10

        enrollment_data.append(count)

    return {
        "labels": months,
        "datasets": [{
            "name": "New Enrollments",
            "values": enrollment_data
        }]
    }


def get_financial_summary(filters=None):
    """
    Get financial summary data

    Args:
        filters: Optional filters

    Returns:
        dict: Financial metrics
    """
    today_date = getdate(today())
    month_start = get_first_day(today_date)
    year_start = today_date.replace(month=1, day=1)

    # Check if Fees doctype exists
    if frappe.db.exists("DocType", "Fees"):
        # Monthly collection
        monthly_collection = frappe.db.sql("""
            SELECT SUM(paid_amount) as total
            FROM `tabFees`
            WHERE docstatus = 1
            AND posting_date >= %s
        """, month_start, as_dict=True)

        # Yearly collection
        yearly_collection = frappe.db.sql("""
            SELECT SUM(paid_amount) as total
            FROM `tabFees`
            WHERE docstatus = 1
            AND posting_date >= %s
        """, year_start, as_dict=True)

        # Outstanding
        outstanding = frappe.db.sql("""
            SELECT SUM(outstanding_amount) as total
            FROM `tabFees`
            WHERE docstatus = 1
        """, as_dict=True)

        return {
            "monthly_collection": flt(monthly_collection[0]["total"]) if monthly_collection else 0,
            "yearly_collection": flt(yearly_collection[0]["total"]) if yearly_collection else 0,
            "total_outstanding": flt(outstanding[0]["total"]) if outstanding else 0,
            "collection_rate": 87.5  # Calculate from actual data
        }
    else:
        # Mock data
        return {
            "monthly_collection": 2500000,
            "yearly_collection": 28000000,
            "total_outstanding": 3500000,
            "collection_rate": 87.5
        }


def get_department_performance(filters=None):
    """
    Get department-wise performance metrics

    Args:
        filters: Optional filters

    Returns:
        list: Department performance data
    """
    if frappe.db.exists("DocType", "Department"):
        departments = frappe.get_all("Department", fields=["name"])

        performance_data = []
        for dept in departments[:10]:  # Limit to 10 departments
            dept_data = {
                "department": dept["name"],
                "students": _get_department_student_count(dept["name"]),
                "faculty": _get_department_faculty_count(dept["name"]),
                "attendance_rate": _get_department_attendance(dept["name"]),
                "pass_rate": _get_department_pass_rate(dept["name"])
            }
            performance_data.append(dept_data)

        return performance_data
    else:
        # Mock data
        return [
            {"department": "Computer Science", "students": 450, "faculty": 25, "attendance_rate": 85.5, "pass_rate": 88.2},
            {"department": "Electronics", "students": 380, "faculty": 20, "attendance_rate": 82.3, "pass_rate": 85.1},
            {"department": "Mechanical", "students": 400, "faculty": 22, "attendance_rate": 80.5, "pass_rate": 82.5},
            {"department": "Civil", "students": 350, "faculty": 18, "attendance_rate": 83.2, "pass_rate": 86.3},
            {"department": "Electrical", "students": 320, "faculty": 17, "attendance_rate": 81.8, "pass_rate": 84.7}
        ]


def get_alerts(filters=None):
    """
    Get system alerts and notifications

    Args:
        filters: Optional filters

    Returns:
        list: Alert items
    """
    alerts = []

    # Check for pending grievances
    pending_grievances = _get_pending_grievances()
    if pending_grievances > 10:
        alerts.append({
            "type": "warning",
            "title": "Pending Grievances",
            "message": f"{pending_grievances} grievances pending resolution",
            "link": "/app/grievance?status=Open"
        })

    # Check for SLA breaches
    sla_breaches = _get_sla_breaches()
    if sla_breaches > 0:
        alerts.append({
            "type": "danger",
            "title": "SLA Breaches",
            "message": f"{sla_breaches} grievances have breached SLA",
            "link": "/app/grievance?sla_status=Breached"
        })

    # Check for low attendance
    low_attendance_depts = _get_low_attendance_departments()
    if low_attendance_depts:
        alerts.append({
            "type": "warning",
            "title": "Low Attendance",
            "message": f"{len(low_attendance_depts)} departments with attendance below 75%",
            "link": "/app/query-report/Student%20Attendance%20Summary"
        })

    # Check for overdue fees
    overdue_count = _get_overdue_fees_count()
    if overdue_count > 0:
        alerts.append({
            "type": "info",
            "title": "Overdue Fees",
            "message": f"{overdue_count} students with overdue fee payments",
            "link": "/app/fees?outstanding_amount=[\">\",0]"
        })

    return alerts


def get_kpi_summary(filters=None):
    """
    Get summary of key KPIs

    Args:
        filters: Optional filters

    Returns:
        list: KPI summary data
    """
    kpis = []

    # Get KPIs marked for executive dashboard
    if frappe.db.exists("DocType", "KPI Definition"):
        kpi_definitions = frappe.get_all(
            "KPI Definition",
            filters={
                "is_active": 1,
                "show_on_executive_dashboard": 1
            },
            fields=["name", "kpi_name", "category", "target_value", "unit", "higher_is_better"]
        )

        for kpi_def in kpi_definitions[:8]:  # Limit to 8 KPIs
            # Get latest value
            latest_value = frappe.db.get_value(
                "KPI Value",
                {"kpi": kpi_def["name"]},
                ["value", "status", "variance"],
                order_by="period_start DESC"
            )

            kpis.append({
                "name": kpi_def["kpi_name"],
                "category": kpi_def["category"],
                "value": latest_value[0] if latest_value else 0,
                "target": kpi_def["target_value"],
                "unit": kpi_def["unit"],
                "status": latest_value[1] if latest_value else "Red",
                "variance": latest_value[2] if latest_value else 0,
                "higher_is_better": kpi_def["higher_is_better"]
            })
    else:
        # Mock data
        kpis = [
            {"name": "Student Pass Rate", "category": "Academic", "value": 85.5, "target": 80, "unit": "%", "status": "Green", "variance": 6.9},
            {"name": "Fee Collection Rate", "category": "Financial", "value": 87.5, "target": 90, "unit": "%", "status": "Yellow", "variance": -2.8},
            {"name": "Student Attendance", "category": "Academic", "value": 82.3, "target": 85, "unit": "%", "status": "Yellow", "variance": -3.2},
            {"name": "Faculty-Student Ratio", "category": "Academic", "value": 20, "target": 25, "unit": ":1", "status": "Green", "variance": 20}
        ]

    return kpis


# Helper functions

def _get_total_students(filters=None, previous_period=False):
    """Get total student count"""
    if frappe.db.exists("DocType", "Student"):
        filter_dict = {}
        if previous_period:
            filter_dict["creation"] = ["<", add_months(today(), -1)]
        return frappe.db.count("Student", filter_dict or {})
    return 2500


def _get_total_faculty(filters=None):
    """Get total faculty count"""
    if frappe.db.exists("DocType", "Instructor"):
        return frappe.db.count("Instructor", {})
    return 150


def _get_total_programs():
    """Get total program count"""
    if frappe.db.exists("DocType", "Program"):
        return frappe.db.count("Program", {})
    return 25


def _get_total_courses():
    """Get total course count"""
    if frappe.db.exists("DocType", "Course"):
        return frappe.db.count("Course", {})
    return 180


def _get_active_batches(filters=None):
    """Get active batch count"""
    if frappe.db.exists("DocType", "Student Batch Name"):
        return frappe.db.count("Student Batch Name", {"status": "Active"})
    return 45


def _get_pending_grievances():
    """Get pending grievance count"""
    if frappe.db.exists("DocType", "Grievance"):
        return frappe.db.count("Grievance", {"status": ["in", ["Open", "In Progress"]]})
    return 15


def _get_sla_breaches():
    """Get SLA breach count"""
    if frappe.db.exists("DocType", "Grievance"):
        return frappe.db.count("Grievance", {"sla_status": "Breached"})
    return 3


def _get_upcoming_exams():
    """Get upcoming exam count"""
    if frappe.db.exists("DocType", "Examination"):
        return frappe.db.count("Examination", {
            "exam_date": [">=", today()],
            "docstatus": 1
        })
    return 8


def _get_fee_collection_today():
    """Get today's fee collection"""
    if frappe.db.exists("DocType", "Fees"):
        result = frappe.db.sql("""
            SELECT SUM(paid_amount) as total
            FROM `tabFees`
            WHERE docstatus = 1 AND posting_date = %s
        """, today(), as_dict=True)
        return flt(result[0]["total"]) if result else 0
    return 125000


def _get_department_student_count(department):
    """Get student count for department"""
    if frappe.db.exists("DocType", "Student"):
        return frappe.db.count("Student", {"department": department})
    return 100


def _get_department_faculty_count(department):
    """Get faculty count for department"""
    if frappe.db.exists("DocType", "Instructor"):
        return frappe.db.count("Instructor", {"department": department})
    return 10


def _get_department_attendance(department):
    """Get attendance rate for department"""
    return 82.5  # Mock value


def _get_department_pass_rate(department):
    """Get pass rate for department"""
    return 85.0  # Mock value


def _get_low_attendance_departments():
    """Get departments with low attendance"""
    return []  # Return empty for now


def _get_overdue_fees_count():
    """Get count of students with overdue fees"""
    if frappe.db.exists("DocType", "Fees"):
        return frappe.db.count("Fees", {
            "outstanding_amount": [">", 0],
            "due_date": ["<", today()]
        })
    return 50


def _calculate_change(current, previous):
    """Calculate percentage change"""
    if previous and previous > 0:
        return round(((current - previous) / previous) * 100, 1)
    return 0
