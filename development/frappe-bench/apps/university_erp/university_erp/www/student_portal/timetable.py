# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_days


def get_context(context):
    """Student timetable page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    try:
        week_start = getdate(frappe.form_dict.get("week_start") or nowdate())
    except Exception:
        week_start = getdate(nowdate())

    context.no_cache = 1
    context.student = student
    context.active_page = "timetable"
    context.week_start = week_start
    context.timetable = get_weekly_timetable(student.name, week_start)
    context.days = get_week_days(week_start)

    return context


def get_weekly_timetable(student, week_start):
    """Get weekly timetable for student"""
    try:
        if not frappe.db.exists("DocType", "Course Schedule"):
            return {}

        week_end = add_days(week_start, 6)

        # Get student groups
        student_groups = frappe.db.get_all(
            "Student Group Student",
            filters={"student": student, "active": 1},
            pluck="parent"
        )

        if not student_groups:
            return {}

        # Check what fields exist on Course Schedule
        meta = frappe.get_meta("Course Schedule")
        available_fields = [f.fieldname for f in meta.fields]

        select_parts = ["cs.name", "cs.schedule_date", "cs.student_group"]

        if "course" in available_fields:
            select_parts.append("cs.course")
        if "instructor" in available_fields:
            select_parts.append("cs.instructor")
        if "instructor_name" in available_fields:
            select_parts.append("cs.instructor_name")
        if "room" in available_fields:
            select_parts.append("cs.room")
        if "from_time" in available_fields:
            select_parts.append("cs.from_time")
        if "to_time" in available_fields:
            select_parts.append("cs.to_time")

        query = f"""
            SELECT {', '.join(select_parts)}
            FROM `tabCourse Schedule` cs
            WHERE cs.student_group IN %s
            AND cs.schedule_date BETWEEN %s AND %s
            ORDER BY cs.schedule_date, cs.from_time
        """

        schedules = frappe.db.sql(query, (tuple(student_groups), week_start, week_end), as_dict=1)

        # Group by day
        timetable = {}
        for schedule in schedules:
            if schedule.schedule_date:
                day = schedule.schedule_date.strftime("%A")
                if day not in timetable:
                    timetable[day] = []
                timetable[day].append(schedule)

        return timetable
    except Exception:
        return {}


def get_week_days(week_start):
    """Get list of days in the week"""
    try:
        days = []
        today = getdate(nowdate())
        for i in range(7):
            day = add_days(week_start, i)
            days.append({
                "date": day,
                "day_name": day.strftime("%A"),
                "short_name": day.strftime("%a"),
                "day_num": day.strftime("%d"),
                "is_today": day == today
            })
        return days
    except Exception:
        return []
