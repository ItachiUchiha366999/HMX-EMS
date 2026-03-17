# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
    """Get notification center page context"""
    pass


@frappe.whitelist()
def get_notification_stats():
    """Get notification statistics for current user"""
    user = frappe.session.user

    # Get counts
    total = frappe.db.count("User Notification", {"user": user})
    unread = frappe.db.count("User Notification", {"user": user, "read": 0})

    # Get by category
    categories = frappe.db.sql("""
        SELECT category, COUNT(*) as count
        FROM `tabUser Notification`
        WHERE user = %s
        GROUP BY category
    """, (user,), as_dict=True)

    category_counts = {c.category: c.count for c in categories}

    return {
        "total": total,
        "unread": unread,
        "read": total - unread,
        "categories": category_counts
    }


@frappe.whitelist()
def get_notifications_paginated(page=1, page_size=20, category=None, read_status=None):
    """Get paginated notifications with filters"""
    user = frappe.session.user
    page = int(page)
    page_size = int(page_size)

    filters = {"user": user}

    if category and category != "All":
        filters["category"] = category

    if read_status == "unread":
        filters["read"] = 0
    elif read_status == "read":
        filters["read"] = 1

    # Get total count
    total = frappe.db.count("User Notification", filters)

    # Get notifications
    notifications = frappe.get_all(
        "User Notification",
        filters=filters,
        fields=[
            "name", "title", "message", "notification_type", "category",
            "priority", "read", "read_at", "creation", "link", "icon",
            "link_doctype", "link_name"
        ],
        order_by="creation desc",
        start=(page - 1) * page_size,
        limit=page_size
    )

    return {
        "notifications": notifications,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@frappe.whitelist()
def bulk_mark_read(notification_names):
    """Mark multiple notifications as read"""
    if isinstance(notification_names, str):
        import json
        notification_names = json.loads(notification_names)

    user = frappe.session.user
    now = frappe.utils.now()

    for name in notification_names:
        frappe.db.set_value(
            "User Notification",
            {"name": name, "user": user},
            {"read": 1, "read_at": now}
        )

    frappe.db.commit()
    return {"success": True, "marked": len(notification_names)}


@frappe.whitelist()
def bulk_delete(notification_names):
    """Delete multiple notifications"""
    if isinstance(notification_names, str):
        import json
        notification_names = json.loads(notification_names)

    user = frappe.session.user
    deleted = 0

    for name in notification_names:
        if frappe.db.exists("User Notification", {"name": name, "user": user}):
            frappe.delete_doc("User Notification", name, ignore_permissions=True)
            deleted += 1

    frappe.db.commit()
    return {"success": True, "deleted": deleted}
