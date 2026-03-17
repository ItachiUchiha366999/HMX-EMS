# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate


def get_context(context):
    """Student notifications page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "notifications"

    # Get notifications
    context.notifications = get_notifications(student.name)
    context.announcements = get_announcements()

    # Counts
    context.unread_count = len([n for n in context.notifications if not n.get("read")])
    context.announcements_count = len(context.announcements)
    context.total_count = len(context.notifications)

    return context


def get_current_student():
    """Get current logged in student"""
    try:
        user = frappe.session.user
        student = frappe.db.get_value(
            "Student",
            {"user": user},
            ["name", "student_name", "image"],
            as_dict=1
        )
        return student
    except Exception:
        return None


def get_notifications(student):
    """Get notifications for student"""
    try:
        user = frappe.session.user
        notifications = []

        # Get system notifications from Notification Log
        if frappe.db.exists("DocType", "Notification Log"):
            system_notifications = frappe.db.sql("""
                SELECT
                    name,
                    subject as title,
                    email_content as message,
                    creation,
                    `read`,
                    'general' as type
                FROM `tabNotification Log`
                WHERE for_user = %s
                ORDER BY creation DESC
                LIMIT 50
            """, user, as_dict=1)
            notifications.extend(system_notifications)

        # Add fee due notifications from Fees (not Fee Schedule)
        if frappe.db.exists("DocType", "Fees"):
            try:
                fee_dues = frappe.db.sql("""
                    SELECT
                        'Fee Payment Due' as title,
                        CONCAT('You have a pending fee payment of ', outstanding_amount, ' due on ', due_date) as message,
                        due_date as creation,
                        0 as `read`,
                        'alert' as type
                    FROM `tabFees`
                    WHERE student = %s
                    AND outstanding_amount > 0
                    AND docstatus = 1
                    LIMIT 5
                """, student, as_dict=1)
                notifications.extend(fee_dues)
            except Exception:
                pass

        # Sort by creation date
        notifications.sort(key=lambda x: x.get("creation") or "", reverse=True)

        return notifications[:30]
    except Exception:
        return []


def get_announcements():
    """Get recent announcements for students"""
    try:
        if not frappe.db.exists("DocType", "Announcement"):
            return []

        # Check what fields exist in Announcement
        meta = frappe.get_meta("Announcement")
        fields = [f.fieldname for f in meta.fields]

        filters = {}
        if "for_students" in fields:
            filters["for_students"] = 1
        if "publish_date" in fields:
            filters["publish_date"] = ["<=", nowdate()]
        if "expiry_date" in fields:
            filters["expiry_date"] = [">=", nowdate()]

        select_fields = ["name", "title"]
        if "description" in fields:
            select_fields.append("description")
        if "publish_date" in fields:
            select_fields.append("publish_date")
        if "priority" in fields:
            select_fields.append("priority")

        order_by = "creation desc"
        if "priority" in fields and "publish_date" in fields:
            order_by = "priority desc, publish_date desc"
        elif "priority" in fields:
            order_by = "priority desc, creation desc"
        elif "publish_date" in fields:
            order_by = "publish_date desc"

        announcements = frappe.db.get_all(
            "Announcement",
            filters=filters,
            fields=select_fields,
            order_by=order_by,
            limit=10
        )

        return announcements
    except Exception:
        return []
