# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.www.student_portal.index import get_current_student
    from university_erp.university_academics.doctype.course_registration.course_registration import (
        get_registrable_courses, get_my_registrations,
    )

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    available = get_registrable_courses()
    my_regs = get_my_registrations()

    context.no_cache = 1
    context.student = student
    context.active_page = "register"
    context.available_courses = available.get("courses", [])
    context.academic_term = available.get("academic_term")
    context.program = available.get("program")
    context.my_registrations = my_regs

    return context
