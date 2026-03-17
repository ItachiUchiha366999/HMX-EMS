# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WebhookLog(Document):
    pass


def log_webhook(webhook_type, event_type, payload, processed=False, error_message=None):
    """Create a webhook log entry"""
    import json

    try:
        doc = frappe.get_doc({
            "doctype": "Webhook Log",
            "webhook_type": webhook_type,
            "event_type": event_type,
            "payload": json.dumps(payload) if isinstance(payload, dict) else payload,
            "received_at": frappe.utils.now_datetime(),
            "processed": processed,
            "error_message": error_message
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc.name
    except Exception as e:
        frappe.log_error(f"Error logging webhook: {str(e)}", "Webhook Log")
        return None


def mark_webhook_processed(webhook_log_name, response=None, processing_time=None):
    """Mark a webhook log as processed"""
    import json

    frappe.db.set_value("Webhook Log", webhook_log_name, {
        "processed": 1,
        "response": json.dumps(response) if isinstance(response, dict) else response,
        "processing_time": processing_time
    })
    frappe.db.commit()
