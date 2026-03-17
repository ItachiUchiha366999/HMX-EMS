# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PushNotificationLog(Document):
    def before_insert(self):
        if not self.sent_at:
            self.sent_at = frappe.utils.now_datetime()


def create_push_log(user=None, platform=None, title=None, body=None, **kwargs):
    """Create a new push notification log entry"""
    log = frappe.get_doc({
        "doctype": "Push Notification Log",
        "user": user,
        "platform": platform,
        "title": title,
        "body": body,
        "status": "Queued",
        **kwargs
    })
    log.insert(ignore_permissions=True)
    return log


def mark_log_sent(log_name, message_id=None):
    """Mark log as sent"""
    frappe.db.set_value("Push Notification Log", log_name, {
        "status": "Sent",
        "message_id": message_id,
        "sent_at": frappe.utils.now_datetime()
    })


def mark_log_failed(log_name, error_message, raw_response=None):
    """Mark log as failed"""
    values = {
        "status": "Failed",
        "error_message": error_message
    }
    if raw_response:
        values["raw_response"] = raw_response

    frappe.db.set_value("Push Notification Log", log_name, values)
