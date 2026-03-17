# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_months, get_first_day, get_last_day


def get_context(context):
    """Student attendance page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    # Get month from query string or default to current
    month_str = frappe.form_dict.get("month")
    if month_str:
        selected_month = getdate(month_str + "-01")
    else:
        selected_month = get_first_day(nowdate())

    context.no_cache = 1
    context.student = student
    context.selected_month = selected_month
    context.attendance_summary = get_attendance_summary(student.name)
    context.monthly_attendance = get_monthly_attendance(student.name, selected_month)
    context.course_attendance = get_course_wise_attendance(student.name)
    context.attendance_calendar = get_attendance_calendar(student.name, selected_month)

    return context


def get_attendance_summary(student):
    """Get overall attendance summary"""
    summary = frappe.db.sql("""
        SELECT
            COUNT(*) as total_classes,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent,
            SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late
        FROM `tabStudent Attendance`
        WHERE student = %s
    """, student, as_dict=1)

    result = summary[0] if summary else {"total_classes": 0, "present": 0, "absent": 0, "late": 0}

    if result["total_classes"] > 0:
        result["percentage"] = round((result["present"] + result.get("late", 0) * 0.5) / result["total_classes"] * 100, 1)
    else:
        result["percentage"] = 0

    return result


def get_monthly_attendance(student, month):
    """Get attendance for a specific month"""
    month_start = get_first_day(month)
    month_end = get_last_day(month)

    attendance = frappe.db.sql("""
        SELECT
            sa.date,
            sa.status,
            sa.course_schedule,
            cs.course,
            cs.from_time,
            cs.to_time
        FROM `tabStudent Attendance` sa
        LEFT JOIN `tabCourse Schedule` cs ON cs.name = sa.course_schedule
        WHERE sa.student = %s
        AND sa.date BETWEEN %s AND %s
        ORDER BY sa.date DESC, cs.from_time
    """, (student, month_start, month_end), as_dict=1)

    return attendance


def get_course_wise_attendance(student):
    """Get attendance breakdown by course"""
    courses = frappe.db.sql("""
        SELECT
            cs.course,
            COUNT(*) as total,
            SUM(CASE WHEN sa.status = 'Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN sa.status = 'Absent' THEN 1 ELSE 0 END) as absent,
            ROUND(SUM(CASE WHEN sa.status = 'Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as percentage
        FROM `tabStudent Attendance` sa
        JOIN `tabCourse Schedule` cs ON cs.name = sa.course_schedule
        WHERE sa.student = %s
        GROUP BY cs.course
        ORDER BY percentage ASC
    """, student, as_dict=1)

    return courses


def get_attendance_calendar(student, month):
    """Get attendance in calendar format"""
    month_start = get_first_day(month)
    month_end = get_last_day(month)

    attendance = frappe.db.sql("""
        SELECT
            date,
            status,
            COUNT(*) as class_count
        FROM `tabStudent Attendance`
        WHERE student = %s
        AND date BETWEEN %s AND %s
        GROUP BY date, status
    """, (student, month_start, month_end), as_dict=1)

    # Create calendar data
    calendar = {}
    for record in attendance:
        date_str = str(record.date)
        if date_str not in calendar:
            calendar[date_str] = {"present": 0, "absent": 0, "late": 0}
        calendar[date_str][record.status.lower()] = record.class_count

    return calendar
