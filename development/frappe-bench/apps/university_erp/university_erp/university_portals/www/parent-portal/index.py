# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt


def get_context(context):
    """Main context function for Parent Portal"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Parent Portal"), frappe.PermissionError)

    guardian = get_current_guardian()
    if not guardian:
        frappe.throw(_("You are not registered as a guardian"), frappe.PermissionError)

    context.no_cache = 1
    context.guardian = guardian
    context.children = get_linked_children(guardian.name)
    context.announcements = get_parent_announcements()

    return context


def get_current_guardian():
    """Get current logged in guardian"""
    user = frappe.session.user
    guardian = frappe.db.get_value(
        "Guardian",
        {"user": user},
        ["name", "guardian_name", "email_address", "mobile_number", "image"],
        as_dict=1
    )
    return guardian


def get_linked_children(guardian):
    """Get children linked to guardian"""
    children = frappe.db.sql("""
        SELECT
            s.name as student,
            s.student_name,
            s.program,
            s.student_batch_name,
            s.image,
            sg.relation
        FROM `tabStudent Guardian` sg
        JOIN `tabStudent` s ON s.name = sg.parent
        WHERE sg.guardian = %s
    """, guardian, as_dict=1)

    # Add summary data for each child
    for child in children:
        child["attendance"] = get_student_attendance_summary(child["student"])
        child["fees"] = get_student_fee_summary(child["student"])
        child["grades"] = get_student_grade_summary(child["student"])

    return children


def get_student_attendance_summary(student):
    """Get attendance summary for a student"""
    summary = frappe.db.sql("""
        SELECT
            COUNT(*) as total_classes,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent
        FROM `tabStudent Attendance`
        WHERE student = %s
    """, student, as_dict=1)

    result = summary[0] if summary else {"total_classes": 0, "present": 0, "absent": 0}

    if result["total_classes"] > 0:
        result["percentage"] = round(result["present"] / result["total_classes"] * 100, 1)
    else:
        result["percentage"] = 0

    return result


def get_student_fee_summary(student):
    """Get fee summary for a student"""
    summary = frappe.db.sql("""
        SELECT
            COALESCE(SUM(total_amount), 0) as total,
            COALESCE(SUM(paid_amount), 0) as paid,
            COALESCE(SUM(outstanding_amount), 0) as pending
        FROM `tabFee Schedule`
        WHERE student = %s
        AND docstatus = 1
    """, student, as_dict=1)

    return summary[0] if summary else {"total": 0, "paid": 0, "pending": 0}


def get_student_grade_summary(student):
    """Get grade summary for a student"""
    result = frappe.db.get_value(
        "Student Result",
        {"student": student, "docstatus": 1},
        ["cgpa", "sgpa", "percentage", "result_status"],
        order_by="academic_year desc, academic_term desc",
        as_dict=1
    )

    return result or {"cgpa": 0, "sgpa": 0, "percentage": 0, "result_status": ""}


def get_parent_announcements():
    """Get announcements for parents"""
    announcements = frappe.db.get_all(
        "Announcement",
        filters={
            "for_parents": 1,
            "publish_date": ["<=", nowdate()],
            "expiry_date": [">=", nowdate()]
        },
        fields=["title", "description", "publish_date", "priority"],
        order_by="priority desc, publish_date desc",
        limit=5
    )

    return announcements
