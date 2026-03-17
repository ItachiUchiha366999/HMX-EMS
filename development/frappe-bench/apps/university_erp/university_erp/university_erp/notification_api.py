# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Notification API endpoints for client-side integration
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_notifications(limit=20, offset=0, unread_only=False):
    """Get notifications for current user"""
    user = frappe.session.user
    filters = {"for_user": user}

    if unread_only:
        filters["read"] = 0

    notifications = frappe.get_all(
        "Notification Log",
        filters=filters,
        fields=[
            "name", "subject", "email_content", "type",
            "document_type", "document_name", "read",
            "creation", "modified"
        ],
        order_by="creation desc",
        limit_page_length=limit,
        start=offset
    )

    # Get unread count
    unread_count = frappe.db.count(
        "Notification Log",
        {"for_user": user, "read": 0}
    )

    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total": frappe.db.count("Notification Log", {"for_user": user})
    }


@frappe.whitelist()
def mark_as_read(notification_name):
    """Mark a notification as read"""
    user = frappe.session.user

    # Verify ownership
    owner = frappe.db.get_value("Notification Log", notification_name, "for_user")
    if owner != user:
        frappe.throw(_("You don't have permission to access this notification"))

    frappe.db.set_value("Notification Log", notification_name, "read", 1)
    frappe.db.commit()

    return {"success": True}


@frappe.whitelist()
def mark_all_as_read():
    """Mark all notifications as read for current user"""
    user = frappe.session.user

    frappe.db.sql("""
        UPDATE `tabNotification Log`
        SET `read` = 1
        WHERE for_user = %s AND `read` = 0
    """, (user,))
    frappe.db.commit()

    return {"success": True}


@frappe.whitelist()
def delete_notification(notification_name):
    """Delete a notification"""
    user = frappe.session.user

    # Verify ownership
    owner = frappe.db.get_value("Notification Log", notification_name, "for_user")
    if owner != user:
        frappe.throw(_("You don't have permission to delete this notification"))

    frappe.delete_doc("Notification Log", notification_name, ignore_permissions=True)

    return {"success": True}


@frappe.whitelist()
def get_unread_count():
    """Get unread notification count for current user"""
    user = frappe.session.user

    count = frappe.db.count(
        "Notification Log",
        {"for_user": user, "read": 0}
    )

    return {"count": count}


@frappe.whitelist()
def subscribe_to_push(push_token, device_type="web"):
    """Subscribe to push notifications"""
    user = frappe.session.user

    # Store push token in user settings
    user_settings = frappe.get_doc("User", user)

    # Create or update push subscription
    existing = frappe.db.exists(
        "Push Subscription",
        {"user": user, "device_type": device_type}
    )

    if existing:
        frappe.db.set_value("Push Subscription", existing, "push_token", push_token)
    else:
        # Create Push Subscription if DocType exists
        try:
            frappe.get_doc({
                "doctype": "Push Subscription",
                "user": user,
                "push_token": push_token,
                "device_type": device_type,
                "enabled": 1
            }).insert(ignore_permissions=True)
        except Exception:
            # Fallback to storing in cache if DocType doesn't exist
            frappe.cache().hset(f"push_tokens:{user}", device_type, push_token)

    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def unsubscribe_from_push(device_type="web"):
    """Unsubscribe from push notifications"""
    user = frappe.session.user

    # Remove push subscription
    existing = frappe.db.exists(
        "Push Subscription",
        {"user": user, "device_type": device_type}
    )

    if existing:
        frappe.delete_doc("Push Subscription", existing, ignore_permissions=True)
    else:
        frappe.cache().hdel(f"push_tokens:{user}", device_type)

    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def send_test_notification():
    """Send a test notification to current user (for debugging)"""
    from university_erp.university_erp.notification_service import NotificationService

    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    context = {
        "user_name": user_doc.full_name or user,
        "test_time": frappe.utils.now()
    }

    # Send in-app notification directly (bypass template)
    NotificationService.create_in_app_notification(
        recipients=[user],
        subject="Test Notification",
        message=f"This is a test notification sent at {context['test_time']}",
        notification_type="Test"
    )

    return {"success": True, "message": "Test notification sent"}


@frappe.whitelist()
def get_notification_settings():
    """Get notification settings for current user"""
    from university_erp.university_erp.doctype.notification_preference.notification_preference import (
        get_user_preferences
    )

    return get_user_preferences()


@frappe.whitelist()
def update_notification_settings(settings):
    """Update notification settings for current user"""
    from university_erp.university_erp.doctype.notification_preference.notification_preference import (
        update_preferences
    )

    return update_preferences(settings)


# Real-time notification support
def notify_user(user, message, title=None, notification_type="Alert"):
    """Send real-time notification to user via frappe.publish_realtime"""
    frappe.publish_realtime(
        event="university_notification",
        message={
            "title": title or "Notification",
            "message": message,
            "type": notification_type
        },
        user=user
    )


def broadcast_notification(message, title=None, roles=None):
    """Broadcast notification to multiple users"""
    if roles:
        users = frappe.get_all(
            "Has Role",
            filters={"role": ["in", roles], "parenttype": "User"},
            pluck="parent"
        )
        users = list(set(users))
    else:
        users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")

    for user in users:
        notify_user(user, message, title)
