# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, date_diff


def get_context(context):
    """Student assignments page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "assignments"

    # Get all assignments data
    all_data = get_all_assignments(student.name)
    context.pending_assignments = all_data.get("pending", [])
    context.completed_assignments = all_data.get("completed", [])
    context.all_assignments = all_data.get("all", [])

    # Counts
    context.pending_count = len(context.pending_assignments)
    context.completed_count = len(context.completed_assignments)
    context.overdue_count = len([a for a in context.pending_assignments if a.get("is_overdue")])
    context.total_count = len(context.all_assignments)

    return context


def get_current_student():
    """Get current logged in student"""
    user = frappe.session.user
    student = frappe.db.get_value(
        "Student",
        {"user": user},
        ["name", "student_name", "image"],
        as_dict=1
    )
    return student


def get_all_assignments(student):
    """Get all assignments for student"""
    today = getdate(nowdate())

    # Get all LMS assignments (LMS Assignment doesn't have student_group linking)
    # So we get all assignments and let students see all available ones
    assignments = frappe.db.sql("""
        SELECT
            a.name,
            a.title,
            a.lms_course,
            a.due_date,
            a.max_marks,
            a.instructions,
            a.available_from,
            s.name as submission_name,
            s.submission_date,
            s.marks_obtained
        FROM `tabLMS Assignment` a
        LEFT JOIN `tabAssignment Submission` s
            ON s.assignment = a.name AND s.student = %s
        WHERE a.docstatus = 1
        ORDER BY a.due_date ASC
    """, (student,), as_dict=1)

    pending = []
    completed = []
    all_assignments = []

    for assignment in assignments:
        due_date = getdate(assignment.due_date) if assignment.due_date else None
        is_overdue = due_date and due_date < today
        days_left = date_diff(due_date, today) if due_date else 0

        assignment_data = {
            "name": assignment.name,
            "title": assignment.title,
            "lms_course": assignment.lms_course,
            "course": assignment.lms_course,  # For compatibility
            "due_date": assignment.due_date,
            "max_marks": assignment.max_marks,
            "is_overdue": is_overdue,
            "days_left": max(0, days_left),
            "submission_date": assignment.submission_date,
            "marks_obtained": assignment.marks_obtained,
            "status": "Completed" if assignment.submission_name else ("Overdue" if is_overdue else "Pending")
        }

        all_assignments.append(assignment_data)

        if assignment.submission_name:
            completed.append(assignment_data)
        else:
            pending.append(assignment_data)

    return {
        "pending": pending,
        "completed": completed,
        "all": all_assignments
    }
