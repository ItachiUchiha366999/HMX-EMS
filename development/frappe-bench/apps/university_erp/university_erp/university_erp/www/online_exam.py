"""
Online Exam Portal Page Controller
"""

import frappe
from frappe import _


def get_context(context):
    """Set context for online exam page"""
    context.no_cache = 1

    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Check if user is a student
    student = frappe.db.get_value("Student", {"user": frappe.session.user})
    if not student:
        frappe.throw(_("You must be a student to access this page"))

    context.student = student
    context.title = _("Online Examination")

    return context
