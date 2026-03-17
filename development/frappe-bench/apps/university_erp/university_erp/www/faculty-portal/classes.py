# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_days, get_first_day, get_last_day


def get_context(context):
    """Faculty classes/schedule page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Faculty Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("You are not registered as faculty"), frappe.PermissionError)

    # Get week start from query string
    week_start_str = frappe.form_dict.get("week_start")
    if week_start_str:
        week_start = getdate(week_start_str)
    else:
        today = getdate(nowdate())
        # Get Monday of current week
        week_start = today - frappe.utils.datetime.timedelta(days=today.weekday())

    context.no_cache = 1
    context.instructor = instructor
    context.week_start = week_start
    context.week_end = add_days(week_start, 6)
    context.schedule = get_weekly_schedule(instructor.name, week_start)
    context.days = get_week_days(week_start)
    context.assigned_courses = get_assigned_courses(instructor.name)

    return context


def get_weekly_schedule(instructor, week_start):
    """Get weekly class schedule"""
    week_end = add_days(week_start, 6)

    schedules = frappe.db.sql("""
        SELECT
            cs.name,
            cs.course,
            cs.student_group,
            cs.room,
            cs.schedule_date,
            cs.from_time,
            cs.to_time,
            sg.program,
            (SELECT COUNT(*) FROM `tabStudent Group Student` WHERE parent = sg.name AND active = 1) as student_count
        FROM `tabCourse Schedule` cs
        JOIN `tabStudent Group` sg ON sg.name = cs.student_group
        WHERE cs.instructor = %s
        AND cs.schedule_date BETWEEN %s AND %s
        ORDER BY cs.schedule_date, cs.from_time
    """, (instructor, week_start, week_end), as_dict=1)

    # Group by day
    schedule = {}
    for s in schedules:
        day = s.schedule_date.strftime("%A")
        if day not in schedule:
            schedule[day] = []
        schedule[day].append(s)

    return schedule


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


def get_assigned_courses(instructor):
    """Get unique courses assigned to instructor"""
    courses = frappe.db.sql("""
        SELECT DISTINCT
            cs.course,
            c.course_name,
            COUNT(DISTINCT cs.student_group) as groups_count
        FROM `tabCourse Schedule` cs
        JOIN `tabCourse` c ON c.name = cs.course
        WHERE cs.instructor = %s
        AND cs.schedule_date >= %s
        GROUP BY cs.course, c.course_name
    """, (instructor, nowdate()), as_dict=1)

    return courses


@frappe.whitelist()
def get_class_schedule(instructor=None, start_date=None, end_date=None):
    """API to get class schedule"""
    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    if not instructor:
        inst = get_current_instructor()
        if not inst:
            frappe.throw(_("Not authorized"), frappe.PermissionError)
        instructor = inst.name

    if not start_date:
        start_date = nowdate()
    if not end_date:
        end_date = add_days(start_date, 7)

    schedules = frappe.db.sql("""
        SELECT
            cs.name,
            cs.course,
            cs.student_group,
            cs.room,
            cs.schedule_date,
            cs.from_time,
            cs.to_time
        FROM `tabCourse Schedule` cs
        WHERE cs.instructor = %s
        AND cs.schedule_date BETWEEN %s AND %s
        ORDER BY cs.schedule_date, cs.from_time
    """, (instructor, start_date, end_date), as_dict=1)

    return schedules
