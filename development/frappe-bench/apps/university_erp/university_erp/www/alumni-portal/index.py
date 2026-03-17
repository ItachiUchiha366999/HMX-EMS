# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate


def get_context(context):
    """Main context function for Alumni Portal"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Alumni Portal"), frappe.PermissionError)

    alumni = get_current_alumni()
    if not alumni:
        frappe.throw(_("You are not registered as an alumni"), frappe.PermissionError)

    context.no_cache = 1
    context.alumni = alumni
    context.upcoming_events = get_upcoming_events()
    context.recent_news = get_recent_news()
    context.featured_alumni = get_featured_alumni()
    context.quick_links = get_quick_links()

    return context


def get_current_alumni():
    """Get current logged in alumni"""
    user = frappe.session.user
    alumni = frappe.db.get_value(
        "Alumni",
        {"user": user},
        ["name", "student_name", "batch", "program", "graduation_year",
         "current_company", "designation", "city", "image"],
        as_dict=1
    )
    return alumni


def get_upcoming_events():
    """Get upcoming alumni events"""
    events = frappe.db.get_all(
        "Alumni Event",
        filters={
            "status": "Open",
            "event_date": [">=", nowdate()]
        },
        fields=["name", "event_name", "event_type", "event_date", "venue", "city", "image"],
        order_by="event_date asc",
        limit=5
    )

    return events


def get_recent_news():
    """Get recent alumni news"""
    news = frappe.db.get_all(
        "Alumni News",
        filters={
            "publish_date": ["<=", nowdate()]
        },
        fields=["name", "title", "content", "image", "publish_date"],
        order_by="publish_date desc",
        limit=5
    )

    return news


def get_featured_alumni():
    """Get featured alumni profiles"""
    alumni = frappe.db.sql("""
        SELECT
            name,
            student_name,
            batch,
            program,
            current_company,
            designation,
            image
        FROM `tabAlumni`
        WHERE current_company IS NOT NULL AND current_company != ''
        ORDER BY RAND()
        LIMIT 6
    """, as_dict=1)

    return alumni


def get_quick_links():
    """Get quick links for alumni portal"""
    return [
        {"label": _("Alumni Directory"), "url": "/alumni-portal/directory", "icon": "users"},
        {"label": _("Events"), "url": "/alumni-portal/events", "icon": "calendar"},
        {"label": _("Job Board"), "url": "/alumni-portal/jobs", "icon": "briefcase"},
        {"label": _("My Profile"), "url": "/alumni-portal/profile", "icon": "user"},
        {"label": _("Donate"), "url": "/alumni-portal/donate", "icon": "heart"}
    ]
