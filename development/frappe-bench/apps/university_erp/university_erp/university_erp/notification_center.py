# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
In-App Notification Center
Manages user notifications with real-time delivery.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, getdate


class NotificationCenter:
    """Central notification management system"""

    NOTIFICATION_TYPES = {
        "info": {"icon": "info-circle", "color": "#3498db"},
        "success": {"icon": "check-circle", "color": "#27ae60"},
        "warning": {"icon": "exclamation-triangle", "color": "#f39c12"},
        "error": {"icon": "times-circle", "color": "#e74c3c"},
        "announcement": {"icon": "bullhorn", "color": "#9b59b6"}
    }

    @staticmethod
    def send(
        user,
        title,
        message=None,
        notification_type="info",
        link=None,
        link_doctype=None,
        link_name=None,
        category="General",
        priority="Normal",
        expires_in_days=30,
        source_doctype=None,
        source_name=None,
        icon=None
    ):
        """
        Send notification to a user

        Args:
            user: User ID/email
            title: Notification title
            message: Notification message
            notification_type: Type (info/success/warning/error/announcement)
            link: URL to navigate on click
            link_doctype: DocType to link
            link_name: Document name to link
            category: Category for filtering
            priority: Priority (Low/Normal/High/Urgent)
            expires_in_days: Days until notification expires
            source_doctype: Source document type
            source_name: Source document name
            icon: Custom icon class

        Returns:
            str: Notification name
        """
        notification = frappe.get_doc({
            "doctype": "User Notification",
            "user": user,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "link": link,
            "link_doctype": link_doctype,
            "link_name": link_name,
            "category": category,
            "priority": priority,
            "expires_on": add_days(now_datetime(), expires_in_days),
            "source_doctype": source_doctype,
            "source_name": source_name,
            "icon": icon,
            "read": 0
        })
        notification.insert(ignore_permissions=True)

        # Send real-time notification via Socket.IO
        frappe.publish_realtime(
            event="new_notification",
            message={
                "notification": notification.name,
                "title": title,
                "message": message,
                "type": notification_type,
                "category": category,
                "priority": priority
            },
            user=user
        )

        return notification.name

    @staticmethod
    def send_to_role(
        role,
        title,
        message=None,
        notification_type="info",
        link=None,
        category="General",
        priority="Normal"
    ):
        """
        Send notification to all users with a specific role

        Args:
            role: Role name
            title, message, etc.: Same as send()

        Returns:
            list: List of notification names
        """
        users = frappe.get_all(
            "Has Role",
            filters={"role": role, "parenttype": "User"},
            pluck="parent"
        )

        notifications = []
        for user in users:
            if user not in ["Administrator", "Guest"]:
                notif_name = NotificationCenter.send(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    link=link,
                    category=category,
                    priority=priority
                )
                notifications.append(notif_name)

        return notifications

    @staticmethod
    def send_to_students(
        title,
        message=None,
        notification_type="info",
        link=None,
        category="Academic",
        program=None,
        batch=None
    ):
        """
        Send notification to students

        Args:
            title, message, notification_type, link, category: As in send()
            program: Filter by program
            batch: Filter by batch

        Returns:
            list: List of notification names
        """
        filters = {"enabled": 1}
        if program:
            filters["program"] = program
        if batch:
            filters["batch"] = batch

        students = frappe.get_all(
            "Student",
            filters=filters,
            fields=["user"]
        )

        notifications = []
        for student in students:
            if student.user:
                notif_name = NotificationCenter.send(
                    user=student.user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    link=link,
                    category=category
                )
                notifications.append(notif_name)

        return notifications

    @staticmethod
    def send_to_faculty(
        title,
        message=None,
        notification_type="info",
        link=None,
        category="Academic",
        department=None
    ):
        """
        Send notification to faculty members

        Args:
            title, message, etc.: As in send()
            department: Filter by department

        Returns:
            list: List of notification names
        """
        filters = {"is_instructor": 1}
        if department:
            filters["department"] = department

        instructors = frappe.get_all(
            "Instructor",
            filters=filters,
            fields=["user"]
        )

        notifications = []
        for instructor in instructors:
            if instructor.user:
                notif_name = NotificationCenter.send(
                    user=instructor.user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    link=link,
                    category=category
                )
                notifications.append(notif_name)

        return notifications

    @staticmethod
    def get_user_notifications(user, limit=50, unread_only=False, category=None):
        """
        Get notifications for a user

        Args:
            user: User ID/email
            limit: Max number of notifications
            unread_only: Only return unread notifications
            category: Filter by category

        Returns:
            list: List of notification dicts
        """
        filters = {
            "user": user,
            "expires_on": [">=", now_datetime()]
        }

        if unread_only:
            filters["read"] = 0

        if category:
            filters["category"] = category

        notifications = frappe.get_all(
            "User Notification",
            filters=filters,
            fields=[
                "name", "title", "message", "notification_type",
                "link", "link_doctype", "link_name", "category",
                "priority", "read", "creation", "icon"
            ],
            order_by="creation desc",
            limit=limit
        )

        # Add type metadata
        for notif in notifications:
            type_info = NotificationCenter.NOTIFICATION_TYPES.get(
                notif.notification_type,
                {"icon": "bell", "color": "#666"}
            )
            notif["type_icon"] = notif.icon or type_info["icon"]
            notif["type_color"] = type_info["color"]

        return notifications

    @staticmethod
    def mark_as_read(notification_name):
        """Mark a notification as read"""
        notif = frappe.get_doc("User Notification", notification_name)
        notif.mark_as_read()
        return {"success": True}

    @staticmethod
    def mark_all_read(user):
        """Mark all notifications as read for a user"""
        frappe.db.sql("""
            UPDATE `tabUser Notification`
            SET `read` = 1, read_at = %s
            WHERE user = %s AND `read` = 0
        """, (now_datetime(), user))
        frappe.db.commit()
        return {"success": True}

    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for a user"""
        return frappe.db.count(
            "User Notification",
            filters={
                "user": user,
                "read": 0,
                "expires_on": [">=", now_datetime()]
            }
        )

    @staticmethod
    def delete_notification(notification_name, user):
        """Delete a notification (only owner can delete)"""
        notif = frappe.get_doc("User Notification", notification_name)
        if notif.user != user:
            frappe.throw(_("You can only delete your own notifications"))
        frappe.delete_doc("User Notification", notification_name, ignore_permissions=True)
        return {"success": True}

    @staticmethod
    def delete_old_notifications(days=90):
        """Delete notifications older than specified days (scheduled job)"""
        cutoff_date = add_days(now_datetime(), -days)
        frappe.db.sql("""
            DELETE FROM `tabUser Notification`
            WHERE creation < %s
        """, cutoff_date)
        frappe.db.commit()


# ========== API Endpoints ==========

@frappe.whitelist()
def get_notifications(limit=50, unread_only=False, category=None):
    """Get current user's notifications"""
    unread_only = frappe.utils.sbool(unread_only)
    return NotificationCenter.get_user_notifications(
        frappe.session.user,
        limit=int(limit),
        unread_only=unread_only,
        category=category
    )


@frappe.whitelist()
def mark_notification_read(notification):
    """Mark notification as read"""
    # Verify ownership
    notif_user = frappe.db.get_value("User Notification", notification, "user")
    if notif_user != frappe.session.user:
        frappe.throw(_("Not authorized"))

    return NotificationCenter.mark_as_read(notification)


@frappe.whitelist()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    return NotificationCenter.mark_all_read(frappe.session.user)


@frappe.whitelist()
def get_unread_count():
    """Get unread notification count"""
    return NotificationCenter.get_unread_count(frappe.session.user)


@frappe.whitelist()
def delete_notification(notification):
    """Delete a notification"""
    return NotificationCenter.delete_notification(notification, frappe.session.user)


@frappe.whitelist()
def send_notification_to_user(user, title, message=None, notification_type="info", link=None, category="General"):
    """Send notification to a specific user (requires permission)"""
    if not frappe.has_permission("User Notification", "create"):
        frappe.throw(_("Not authorized to send notifications"))

    return NotificationCenter.send(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
        category=category
    )


# ========== Scheduled Jobs ==========

def cleanup_old_notifications():
    """Scheduled job to clean up old notifications"""
    NotificationCenter.delete_old_notifications(days=90)


def cleanup_expired_notifications():
    """Remove expired notifications"""
    frappe.db.sql("""
        DELETE FROM `tabUser Notification`
        WHERE expires_on < NOW()
    """)
    frappe.db.commit()
