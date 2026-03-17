# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_days


def get_context(context):
    """Student timetable page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.week_start = getdate(frappe.form_dict.get("week_start") or nowdate())
    context.timetable = get_weekly_timetable(student.name, context.week_start)
    context.days = get_week_days(context.week_start)

    return context


def get_weekly_timetable(student, week_start):
    """Get weekly timetable for student"""
    week_end = add_days(week_start, 6)

    # Get student groups
    student_groups = frappe.db.get_all(
        "Student Group Student",
        filters={"student": student, "active": 1},
        pluck="parent"
    )

    if not student_groups:
        return {}

    schedules = frappe.db.sql("""
        SELECT
            cs.name,
            cs.course,
            cs.instructor,
            cs.instructor_name,
            cs.room,
            cs.schedule_date,
            cs.from_time,
            cs.to_time,
            cs.student_group
        FROM `tabCourse Schedule` cs
        WHERE cs.student_group IN %s
        AND cs.schedule_date BETWEEN %s AND %s
        ORDER BY cs.schedule_date, cs.from_time
    """, (tuple(student_groups), week_start, week_end), as_dict=1)

    # Group by day
    timetable = {}
    for schedule in schedules:
        day = schedule.schedule_date.strftime("%A")
        if day not in timetable:
            timetable[day] = []
        timetable[day].append(schedule)

    return timetable


def get_week_days(week_start):
    """Get list of days in the week"""
    days = []
    for i in range(7):
        day = add_days(week_start, i)
        days.append({
            "date": day,
            "day_name": day.strftime("%A"),
            "short_name": day.strftime("%a"),
            "day_num": day.strftime("%d"),
            "is_today": day == getdate(nowdate())
        })
    return days
