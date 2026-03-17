# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt


def get_context(context):
    """Main context function for Faculty Portal"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Faculty Portal"), frappe.PermissionError)

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("You are not registered as faculty"), frappe.PermissionError)

    context.no_cache = 1
    context.instructor = instructor
    context.dashboard = get_faculty_dashboard(instructor.name)
    context.today_classes = get_today_classes(instructor.name)
    context.pending_tasks = get_pending_tasks(instructor.name)
    context.announcements = get_faculty_announcements()
    context.quick_links = get_quick_links()

    return context


def get_current_instructor():
    """Get current logged in instructor"""
    user = frappe.session.user
    instructor = frappe.db.get_value(
        "Instructor",
        {"user": user},
        ["name", "instructor_name", "department", "image"],
        as_dict=1
    )
    return instructor


def get_faculty_dashboard(instructor):
    """Get faculty dashboard summary data"""
    return {
        "assigned_courses": get_assigned_courses_count(instructor),
        "total_students": get_total_students_count(instructor),
        "pending_assessments": get_pending_assessments_count(instructor),
        "attendance_status": get_attendance_status_today(instructor),
        "publications": get_publications_count(instructor),
        "pending_approvals": get_pending_approvals_count(instructor)
    }


def get_assigned_courses_count(instructor):
    """Get count of courses assigned to instructor"""
    count = frappe.db.sql("""
        SELECT COUNT(DISTINCT course) as count
        FROM `tabCourse Schedule`
        WHERE instructor = %s
        AND schedule_date >= %s
    """, (instructor, nowdate()), as_dict=1)

    return count[0].count if count else 0


def get_total_students_count(instructor):
    """Get total students in instructor's classes"""
    count = frappe.db.sql("""
        SELECT COUNT(DISTINCT sgs.student) as count
        FROM `tabStudent Group Student` sgs
        JOIN `tabStudent Group` sg ON sg.name = sgs.parent
        JOIN `tabStudent Group Instructor` sgi ON sgi.parent = sg.name
        WHERE sgi.instructor = %s
        AND sgs.active = 1
    """, instructor, as_dict=1)

    return count[0].count if count else 0


def get_pending_assessments_count(instructor):
    """Get count of assessments pending grading"""
    count = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabAssessment Plan` ap
        WHERE ap.supervisor = %s
        AND ap.docstatus = 1
        AND ap.assessment_date <= %s
        AND NOT EXISTS (
            SELECT 1 FROM `tabAssessment Result` ar
            WHERE ar.assessment_plan = ap.name
            AND ar.docstatus = 1
        )
    """, (instructor, nowdate()), as_dict=1)

    return count[0].count if count else 0


def get_attendance_status_today(instructor):
    """Get attendance marking status for today's classes"""
    today = nowdate()

    total_classes = frappe.db.count("Course Schedule", {
        "instructor": instructor,
        "schedule_date": today
    })

    marked_classes = frappe.db.sql("""
        SELECT COUNT(DISTINCT cs.name) as count
        FROM `tabCourse Schedule` cs
        JOIN `tabStudent Attendance` sa ON sa.course_schedule = cs.name
        WHERE cs.instructor = %s
        AND cs.schedule_date = %s
    """, (instructor, today), as_dict=1)

    marked = marked_classes[0].count if marked_classes else 0

    return {
        "total": total_classes,
        "marked": marked,
        "pending": total_classes - marked
    }


def get_publications_count(instructor):
    """Get count of research publications"""
    count = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabResearch Publication` rp
        JOIN `tabResearch Publication Author` rpa ON rpa.parent = rp.name
        WHERE rpa.author = %s
        AND rp.docstatus = 1
    """, instructor, as_dict=1)

    return count[0].count if count else 0


def get_pending_approvals_count(instructor):
    """Get count of items pending approval"""
    # Count pending leave requests for supervised students
    leave_count = frappe.db.count("Student Leave Application", {
        "status": "Pending",
        "docstatus": 0
    })

    return leave_count


def get_today_classes(instructor):
    """Get today's class schedule"""
    today = getdate(nowdate())

    classes = frappe.db.sql("""
        SELECT
            cs.name,
            cs.course,
            cs.student_group,
            cs.room,
            cs.from_time,
            cs.to_time,
            sg.program,
            (SELECT COUNT(*) FROM `tabStudent Group Student` WHERE parent = sg.name AND active = 1) as student_count,
            CASE WHEN EXISTS (
                SELECT 1 FROM `tabStudent Attendance` sa
                WHERE sa.course_schedule = cs.name
            ) THEN 1 ELSE 0 END as attendance_marked
        FROM `tabCourse Schedule` cs
        JOIN `tabStudent Group` sg ON sg.name = cs.student_group
        WHERE cs.instructor = %s
        AND cs.schedule_date = %s
        ORDER BY cs.from_time
    """, (instructor, today), as_dict=1)

    return classes


def get_pending_tasks(instructor):
    """Get pending tasks for faculty"""
    tasks = []

    # Pending attendance
    pending_attendance = frappe.db.sql("""
        SELECT
            cs.name as reference,
            cs.course,
            cs.schedule_date,
            cs.from_time,
            'Attendance' as task_type
        FROM `tabCourse Schedule` cs
        WHERE cs.instructor = %s
        AND cs.schedule_date <= %s
        AND NOT EXISTS (
            SELECT 1 FROM `tabStudent Attendance` sa
            WHERE sa.course_schedule = cs.name
        )
        ORDER BY cs.schedule_date DESC
        LIMIT 5
    """, (instructor, nowdate()), as_dict=1)

    for att in pending_attendance:
        tasks.append({
            "type": "attendance",
            "title": _("Mark Attendance: {0}").format(att.course),
            "date": att.schedule_date,
            "reference": att.reference
        })

    # Pending grade entry
    pending_grades = frappe.db.sql("""
        SELECT
            ap.name as reference,
            ap.assessment_name,
            ap.course,
            ap.assessment_date,
            'Grading' as task_type
        FROM `tabAssessment Plan` ap
        WHERE ap.supervisor = %s
        AND ap.docstatus = 1
        AND ap.assessment_date <= %s
        AND NOT EXISTS (
            SELECT 1 FROM `tabAssessment Result` ar
            WHERE ar.assessment_plan = ap.name
            AND ar.docstatus = 1
        )
        LIMIT 5
    """, (instructor, nowdate()), as_dict=1)

    for grade in pending_grades:
        tasks.append({
            "type": "grading",
            "title": _("Grade: {0}").format(grade.assessment_name),
            "date": grade.assessment_date,
            "reference": grade.reference
        })

    return tasks


def get_faculty_announcements():
    """Get announcements for faculty"""
    announcements = frappe.db.get_all(
        "Announcement",
        filters={
            "for_faculty": 1,
            "publish_date": ["<=", nowdate()],
            "expiry_date": [">=", nowdate()]
        },
        fields=["title", "description", "publish_date", "priority"],
        order_by="priority desc, publish_date desc",
        limit=5
    )

    return announcements


def get_quick_links():
    """Get quick links for faculty portal"""
    return [
        {"label": _("Mark Attendance"), "url": "/faculty-portal/attendance", "icon": "check-circle"},
        {"label": _("My Classes"), "url": "/faculty-portal/classes", "icon": "calendar"},
        {"label": _("Grade Entry"), "url": "/faculty-portal/grades", "icon": "edit"},
        {"label": _("Student Groups"), "url": "/faculty-portal/student-groups", "icon": "users"},
        {"label": _("Research"), "url": "/faculty-portal/research", "icon": "book"},
        {"label": _("Leave Management"), "url": "/faculty-portal/leave", "icon": "clock"}
    ]
