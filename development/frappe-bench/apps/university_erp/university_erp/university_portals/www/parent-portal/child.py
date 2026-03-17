# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def get_context(context):
    """Child details page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Parent Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.parent_portal.index import get_current_guardian

    guardian = get_current_guardian()
    if not guardian:
        frappe.throw(_("You are not registered as a guardian"), frappe.PermissionError)

    student_id = frappe.form_dict.get("student")
    if not student_id:
        frappe.throw(_("Student not specified"), frappe.DoesNotExistError)

    # Verify parent-child relationship
    is_linked = frappe.db.exists("Student Guardian", {
        "parent": student_id,
        "guardian": guardian.name
    })

    if not is_linked:
        frappe.throw(_("You are not authorized to view this student's information"), frappe.PermissionError)

    student = frappe.get_doc("Student", student_id)

    context.no_cache = 1
    context.guardian = guardian
    context.student = student
    context.attendance = get_attendance_details(student_id)
    context.results = get_recent_results(student_id)
    context.fees = get_fee_details(student_id)
    context.timetable = get_today_timetable(student_id)

    return context


def get_attendance_details(student):
    """Get attendance details for student"""
    from university_erp.university_portals.www.parent_portal.index import get_student_attendance_summary

    summary = get_student_attendance_summary(student)

    # Get recent attendance
    recent = frappe.db.sql("""
        SELECT
            sa.date,
            sa.status,
            cs.course,
            cs.from_time,
            cs.to_time
        FROM `tabStudent Attendance` sa
        LEFT JOIN `tabCourse Schedule` cs ON cs.name = sa.course_schedule
        WHERE sa.student = %s
        ORDER BY sa.date DESC
        LIMIT 10
    """, student, as_dict=1)

    return {
        "summary": summary,
        "recent": recent
    }


def get_recent_results(student):
    """Get recent assessment results"""
    results = frappe.db.sql("""
        SELECT
            ar.course,
            ar.assessment_name,
            ar.maximum_marks,
            ar.obtained_marks,
            ar.grade,
            ar.percentage,
            ap.assessment_date
        FROM `tabAssessment Result` ar
        JOIN `tabAssessment Plan` ap ON ap.name = ar.assessment_plan
        WHERE ar.student = %s
        AND ar.docstatus = 1
        ORDER BY ap.assessment_date DESC
        LIMIT 10
    """, student, as_dict=1)

    return results


def get_fee_details(student):
    """Get fee details for student"""
    from university_erp.university_portals.www.parent_portal.index import get_student_fee_summary

    summary = get_student_fee_summary(student)

    # Get pending fees
    pending = frappe.db.sql("""
        SELECT
            fs.name,
            fs.fee_structure,
            fs.academic_term,
            fs.due_date,
            fs.outstanding_amount
        FROM `tabFee Schedule` fs
        WHERE fs.student = %s
        AND fs.outstanding_amount > 0
        AND fs.docstatus = 1
        ORDER BY fs.due_date
    """, student, as_dict=1)

    return {
        "summary": summary,
        "pending": pending
    }


def get_today_timetable(student):
    """Get today's timetable for student"""
    today = getdate(nowdate())

    # Get student groups
    student_groups = frappe.db.get_all(
        "Student Group Student",
        filters={"student": student, "active": 1},
        pluck="parent"
    )

    if not student_groups:
        return []

    classes = frappe.db.sql("""
        SELECT
            cs.course,
            cs.instructor_name,
            cs.room,
            cs.from_time,
            cs.to_time
        FROM `tabCourse Schedule` cs
        WHERE cs.student_group IN %s
        AND cs.schedule_date = %s
        ORDER BY cs.from_time
    """, (tuple(student_groups), today), as_dict=1)

    return classes
