# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Scheduled Tasks for Grievance & Feedback Module

This module contains scheduled tasks for:
- SLA monitoring and auto-escalation
- Reminder notifications
- Feedback form status management
- Statistics cleanup
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, date_diff, today, getdate, get_datetime


def daily_sla_check():
    """
    Daily job to check SLA status for all open grievances

    - Updates SLA status (Within SLA, At Risk, Breached)
    - Auto-escalates breached grievances if configured
    - Updates days_open counter
    """
    from university_erp.university_erp.grievance.grievance_manager import GrievanceManager
    GrievanceManager.check_sla_status()


def send_pending_reminders():
    """
    Send reminders for grievances at risk of SLA breach
    """
    pending = frappe.get_all("Grievance",
        filters={
            "status": ["in", ["Assigned", "In Progress"]],
            "sla_status": "At Risk"
        },
        fields=["name", "assigned_to", "subject", "expected_resolution_date"]
    )

    for g in pending:
        if g.assigned_to:
            try:
                frappe.sendmail(
                    recipients=[g.assigned_to],
                    subject=_("Reminder: Grievance {0} requires attention").format(g.name),
                    template="grievance_reminder",
                    args={
                        "grievance_name": g.name,
                        "subject": g.subject,
                        "expected_resolution_date": g.expected_resolution_date
                    },
                    delayed=True
                )
            except Exception:
                frappe.log_error(f"Failed to send reminder for grievance {g.name}")


def update_days_open():
    """
    Update days_open counter for all open grievances
    """
    open_grievances = frappe.get_all("Grievance",
        filters={
            "status": ["not in", ["Resolved", "Closed"]]
        },
        fields=["name", "creation"]
    )

    for g in open_grievances:
        days_open = date_diff(today(), getdate(g.creation))
        frappe.db.set_value("Grievance", g.name, "days_open", days_open)


def send_feedback_reminders():
    """
    Send reminders for pending feedback forms
    """
    # Get active feedback forms that allow reminders
    forms = frappe.get_all("Feedback Form",
        filters={
            "status": "Active",
            "is_mandatory": 1,
            "reminder_days": [">", 0]
        },
        fields=["name", "form_title", "end_date", "reminder_days", "target_audience"]
    )

    for form in forms:
        # Get students who haven't responded
        if form.target_audience in ["Students", "All"]:
            _send_student_feedback_reminders(form)


def _send_student_feedback_reminders(form):
    """Send feedback reminders to students"""
    form_doc = frappe.get_doc("Feedback Form", form.name)

    # Get enrolled students
    student_filters = {"enabled": 1}

    if form_doc.programs:
        program_list = [p.program for p in form_doc.programs]
        students = frappe.get_all("Program Enrollment",
            filters={"program": ["in", program_list]},
            pluck="student"
        )
    elif form_doc.courses:
        course_list = [c.course for c in form_doc.courses]
        students = frappe.get_all("Course Enrollment",
            filters={"course": ["in", course_list]},
            pluck="student"
        )
    else:
        students = frappe.get_all("Student", filters=student_filters, pluck="name")

    # Filter out students who have already responded
    responded_students = frappe.get_all("Feedback Response",
        filters={
            "feedback_form": form.name,
            "status": ["in", ["Submitted", "Valid"]]
        },
        pluck="student"
    )

    pending_students = set(students) - set(responded_students)

    for student in pending_students:
        email = frappe.db.get_value("Student", student, "student_email_id")
        if email:
            try:
                frappe.sendmail(
                    recipients=[email],
                    subject=_("Feedback Reminder: {0}").format(form.form_title),
                    template="feedback_reminder",
                    args={
                        "form_title": form.form_title,
                        "end_date": form.end_date,
                        "feedback_link": f"/student-portal/feedback?form={form.name}"
                    },
                    delayed=True
                )
            except Exception:
                frappe.log_error(f"Failed to send feedback reminder to {student}")


def close_expired_feedback_forms():
    """
    Close feedback forms that have passed their end date
    """
    expired_forms = frappe.get_all("Feedback Form",
        filters={
            "status": "Active",
            "end_date": ["<", now_datetime()]
        },
        pluck="name"
    )

    for form_name in expired_forms:
        frappe.db.set_value("Feedback Form", form_name, "status", "Closed")


def activate_scheduled_feedback_forms():
    """
    Activate feedback forms that have reached their start date
    """
    scheduled_forms = frappe.get_all("Feedback Form",
        filters={
            "status": "Scheduled",
            "start_date": ["<=", now_datetime()]
        },
        pluck="name"
    )

    for form_name in scheduled_forms:
        form = frappe.get_doc("Feedback Form", form_name)
        if form.questions:  # Only activate if form has questions
            form.status = "Active"
            form.save()


def cleanup_old_grievances():
    """
    Monthly job to archive old closed grievances
    """
    # Archive grievances closed more than 2 years ago
    cutoff_date = add_days(today(), -730)

    old_grievances = frappe.get_all("Grievance",
        filters={
            "status": "Closed",
            "resolution_date": ["<", cutoff_date]
        },
        pluck="name"
    )

    # Just log for now - actual archival would depend on requirements
    if old_grievances:
        frappe.log_error(
            f"Found {len(old_grievances)} grievances eligible for archival",
            "Grievance Archival Check"
        )


def update_feedback_form_statistics():
    """
    Update statistics for all active feedback forms
    """
    active_forms = frappe.get_all("Feedback Form",
        filters={"status": "Active"},
        pluck="name"
    )

    for form_name in active_forms:
        try:
            form = frappe.get_doc("Feedback Form", form_name)
            form.update_statistics()
        except Exception:
            frappe.log_error(f"Failed to update statistics for form {form_name}")
