# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_days


class UserNotification(Document):
    def before_insert(self):
        # Set default expiry if not provided
        if not self.expires_on:
            self.expires_on = add_days(now_datetime(), 30)

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read:
            self.read = 1
            self.read_at = now_datetime()
            self.save(ignore_permissions=True)

    def get_notification_icon(self):
        """Get icon based on notification type"""
        icons = {
            "info": "info-circle",
            "success": "check-circle",
            "warning": "exclamation-triangle",
            "error": "times-circle",
            "announcement": "bullhorn"
        }
        return self.icon or icons.get(self.notification_type, "bell")


def get_notification_colors():
    """Get color mapping for notification types"""
    return {
        "info": "#3498db",
        "success": "#27ae60",
        "warning": "#f39c12",
        "error": "#e74c3c",
        "announcement": "#9b59b6"
    }
