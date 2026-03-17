# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, now_datetime


def get_context(context):
    """Faculty attendance marking page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Faculty Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("You are not registered as faculty"), frappe.PermissionError)

    # Get specific class if provided
    class_schedule = frappe.form_dict.get("class")

    context.no_cache = 1
    context.instructor = instructor
    context.today_classes = get_today_classes_for_attendance(instructor.name)
    context.selected_class = get_class_details(class_schedule) if class_schedule else None
    context.students = get_students_for_attendance(class_schedule) if class_schedule else []

    return context


def get_today_classes_for_attendance(instructor):
    """Get today's classes for attendance marking"""
    today = nowdate()

    classes = frappe.db.sql("""
        SELECT
            cs.name,
            cs.course,
            cs.student_group,
            cs.room,
            cs.from_time,
            cs.to_time,
            (SELECT COUNT(*) FROM `tabStudent Group Student` WHERE parent = cs.student_group AND active = 1) as student_count,
            CASE WHEN EXISTS (
                SELECT 1 FROM `tabStudent Attendance` sa
                WHERE sa.course_schedule = cs.name
            ) THEN 1 ELSE 0 END as attendance_marked
        FROM `tabCourse Schedule` cs
        WHERE cs.instructor = %s
        AND cs.schedule_date = %s
        ORDER BY cs.from_time
    """, (instructor, today), as_dict=1)

    return classes


def get_class_details(class_schedule):
    """Get class schedule details"""
    return frappe.db.get_value(
        "Course Schedule",
        class_schedule,
        ["name", "course", "student_group", "room", "from_time", "to_time", "schedule_date", "instructor"],
        as_dict=1
    )


def get_students_for_attendance(class_schedule):
    """Get students for attendance marking"""
    class_doc = frappe.get_doc("Course Schedule", class_schedule)

    students = frappe.db.sql("""
        SELECT
            sgs.student,
            s.student_name,
            s.image,
            COALESCE(sa.status, '') as current_status
        FROM `tabStudent Group Student` sgs
        JOIN `tabStudent` s ON s.name = sgs.student
        LEFT JOIN `tabStudent Attendance` sa ON sa.student = sgs.student
            AND sa.course_schedule = %s
        WHERE sgs.parent = %s
        AND sgs.active = 1
        ORDER BY s.student_name
    """, (class_schedule, class_doc.student_group), as_dict=1)

    return students


@frappe.whitelist()
def mark_attendance(class_schedule, attendance_data):
    """Mark attendance for a class"""
    import json

    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    # Verify instructor owns this class
    class_doc = frappe.get_doc("Course Schedule", class_schedule)
    if class_doc.instructor != instructor.name:
        frappe.throw(_("You can only mark attendance for your own classes"), frappe.PermissionError)

    if isinstance(attendance_data, str):
        attendance_data = json.loads(attendance_data)

    marked_count = 0
    for record in attendance_data:
        student = record.get("student")
        status = record.get("status", "Present")

        # Check if attendance already exists
        existing = frappe.db.get_value("Student Attendance", {
            "student": student,
            "course_schedule": class_schedule
        })

        if existing:
            # Update existing
            frappe.db.set_value("Student Attendance", existing, "status", status)
        else:
            # Create new
            att = frappe.get_doc({
                "doctype": "Student Attendance",
                "student": student,
                "course_schedule": class_schedule,
                "student_group": class_doc.student_group,
                "date": class_doc.schedule_date,
                "status": status
            })
            att.insert(ignore_permissions=True)

        marked_count += 1

    return {
        "success": True,
        "message": _("Attendance marked for {0} students").format(marked_count)
    }


@frappe.whitelist()
def get_student_group_students(student_group):
    """Get students in a student group"""
    students = frappe.db.sql("""
        SELECT
            sgs.student,
            s.student_name,
            s.image
        FROM `tabStudent Group Student` sgs
        JOIN `tabStudent` s ON s.name = sgs.student
        WHERE sgs.parent = %s
        AND sgs.active = 1
        ORDER BY s.student_name
    """, student_group, as_dict=1)

    return students


@frappe.whitelist()
def get_pending_attendance(instructor=None):
    """Get pending attendance for instructor"""
    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    if not instructor:
        inst = get_current_instructor()
        if not inst:
            frappe.throw(_("Not authorized"), frappe.PermissionError)
        instructor = inst.name

    pending = frappe.db.sql("""
        SELECT
            cs.name,
            cs.course,
            cs.student_group,
            cs.schedule_date,
            cs.from_time,
            cs.to_time,
            (SELECT COUNT(*) FROM `tabStudent Group Student` WHERE parent = cs.student_group AND active = 1) as student_count
        FROM `tabCourse Schedule` cs
        WHERE cs.instructor = %s
        AND cs.schedule_date <= %s
        AND NOT EXISTS (
            SELECT 1 FROM `tabStudent Attendance` sa
            WHERE sa.course_schedule = cs.name
        )
        ORDER BY cs.schedule_date DESC, cs.from_time
        LIMIT 20
    """, (instructor, nowdate()), as_dict=1)

    return pending
