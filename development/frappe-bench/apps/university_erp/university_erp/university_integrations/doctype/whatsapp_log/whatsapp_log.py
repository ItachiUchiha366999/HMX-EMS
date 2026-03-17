# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WhatsAppLog(Document):
    def before_insert(self):
        if not self.sent_at and self.direction == "Outgoing":
            self.sent_at = frappe.utils.now_datetime()

    def mark_delivered(self, timestamp=None):
        """Mark message as delivered"""
        self.status = "Delivered"
        self.delivered_at = timestamp or frappe.utils.now_datetime()
        self.save(ignore_permissions=True)

    def mark_read(self, timestamp=None):
        """Mark message as read"""
        self.status = "Read"
        self.read_at = timestamp or frappe.utils.now_datetime()
        self.save(ignore_permissions=True)

    def mark_failed(self, error_message, raw_response=None):
        """Mark message as failed"""
        self.status = "Failed"
        self.failed_at = frappe.utils.now_datetime()
        self.error_message = error_message
        if raw_response:
            self.raw_response = raw_response
        self.save(ignore_permissions=True)


def create_whatsapp_log(phone_number, message_type, direction="Outgoing", **kwargs):
    """Create a new WhatsApp log entry"""
    log = frappe.get_doc({
        "doctype": "WhatsApp Log",
        "phone_number": phone_number,
        "message_type": message_type,
        "direction": direction,
        "status": "Queued" if direction == "Outgoing" else "Received",
        **kwargs
    })
    log.insert(ignore_permissions=True)
    return log


def update_message_status(message_id, status, timestamp=None, error_message=None):
    """Update status of a WhatsApp message by message_id"""
    log_name = frappe.db.get_value("WhatsApp Log", {"message_id": message_id}, "name")

    if not log_name:
        return None

    log = frappe.get_doc("WhatsApp Log", log_name)

    if status == "delivered":
        log.mark_delivered(timestamp)
    elif status == "read":
        log.mark_read(timestamp)
    elif status == "failed":
        log.mark_failed(error_message or "Unknown error")
    else:
        log.status = status.capitalize()
        log.save(ignore_permissions=True)

    return log
