# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_datetime


class SMSQueue(Document):
    def validate(self):
        self.calculate_character_count()
        self.validate_scheduled_time()

    def calculate_character_count(self):
        """Calculate message character count"""
        if self.message:
            self.character_count = len(self.message)

    def validate_scheduled_time(self):
        """Validate scheduled time is in future"""
        if self.scheduled_time:
            if get_datetime(self.scheduled_time) <= now_datetime():
                self.status = "Queued"  # Process immediately if time has passed
            else:
                self.status = "Scheduled"

    def process(self):
        """Process this queued SMS"""
        if self.status not in ["Queued", "Scheduled"]:
            return {"success": False, "error": f"Cannot process SMS with status {self.status}"}

        self.status = "Processing"
        self.save(ignore_permissions=True)

        try:
            from university_erp.university_integrations.sms_gateway import send_sms

            result = send_sms(self.mobile_number, self.message)

            if result.get("success"):
                self.status = "Sent"
                self.sent_at = now_datetime()
                self.message_id = result.get("message_id")
            else:
                self.handle_failure(result.get("error", "Unknown error"))

            self.save(ignore_permissions=True)
            return result

        except Exception as e:
            self.handle_failure(str(e))
            self.save(ignore_permissions=True)
            return {"success": False, "error": str(e)}

    def handle_failure(self, error_message):
        """Handle SMS sending failure with retry logic"""
        self.error_message = error_message
        self.retry_count = (self.retry_count or 0) + 1

        if self.retry_count < (self.max_retries or 3):
            # Schedule retry
            retry_minutes = self.retry_after or 5
            self.scheduled_time = add_to_date(now_datetime(), minutes=retry_minutes)
            self.status = "Scheduled"
        else:
            self.status = "Failed"

    def cancel_sms(self):
        """Cancel queued SMS"""
        if self.status in ["Queued", "Scheduled"]:
            self.status = "Cancelled"
            self.save(ignore_permissions=True)
            return {"success": True}
        return {"success": False, "error": "Cannot cancel SMS that is already processed"}


# ========== Queue Management Functions ==========

def schedule_sms(mobile_number, message, scheduled_time=None, priority="Normal",
                 template_name=None, recipient_name=None, recipient_type=None,
                 recipient_reference=None, batch_id=None, batch_sequence=None):
    """
    Schedule an SMS for sending

    Args:
        mobile_number: Recipient mobile number
        message: SMS message content
        scheduled_time: When to send (None = immediate)
        priority: Low/Normal/High/Urgent
        template_name: Optional template reference
        recipient_name: Optional recipient name
        recipient_type: Student/Employee/Parent/Other
        recipient_reference: Reference document name
        batch_id: Batch identifier for bulk sends
        batch_sequence: Sequence number in batch

    Returns:
        dict: Queue entry details
    """
    status = "Scheduled" if scheduled_time else "Queued"

    queue_entry = frappe.get_doc({
        "doctype": "SMS Queue",
        "mobile_number": mobile_number,
        "message": message,
        "scheduled_time": scheduled_time,
        "status": status,
        "priority": priority,
        "template_name": template_name,
        "recipient_name": recipient_name,
        "recipient_type": recipient_type,
        "recipient_reference": recipient_reference,
        "batch_id": batch_id,
        "batch_sequence": batch_sequence
    })
    queue_entry.insert(ignore_permissions=True)

    return {
        "success": True,
        "queue_id": queue_entry.name,
        "status": status
    }


def schedule_bulk_sms(recipients, message, scheduled_time=None, priority="Normal",
                      template_name=None, batch_size=100):
    """
    Schedule bulk SMS with batch processing

    Args:
        recipients: List of dicts with mobile_number and optional name/type/reference
        message: SMS message content (can contain {name} placeholder)
        scheduled_time: When to send
        priority: Message priority
        template_name: Optional template reference
        batch_size: Number of messages per batch (for rate limiting)

    Returns:
        dict: Batch details with batch_id and count
    """
    batch_id = frappe.generate_hash(length=12)
    queued_count = 0

    for idx, recipient in enumerate(recipients):
        mobile = recipient.get("mobile_number") or recipient.get("mobile")
        if not mobile:
            continue

        # Personalize message if name placeholder exists
        personalized_message = message
        if "{name}" in message and recipient.get("name"):
            personalized_message = message.replace("{name}", recipient.get("name"))

        schedule_sms(
            mobile_number=mobile,
            message=personalized_message,
            scheduled_time=scheduled_time,
            priority=priority,
            template_name=template_name,
            recipient_name=recipient.get("name"),
            recipient_type=recipient.get("type"),
            recipient_reference=recipient.get("reference"),
            batch_id=batch_id,
            batch_sequence=idx + 1
        )
        queued_count += 1

    frappe.db.commit()

    return {
        "success": True,
        "batch_id": batch_id,
        "queued_count": queued_count,
        "total_recipients": len(recipients)
    }


def process_sms_queue(limit=100):
    """
    Process pending SMS queue entries - scheduled task

    Args:
        limit: Maximum number of messages to process in one run

    Returns:
        dict: Processing summary
    """
    now = now_datetime()

    # Get pending entries ordered by priority and scheduled time
    priority_order = {"Urgent": 1, "High": 2, "Normal": 3, "Low": 4}

    pending = frappe.get_all(
        "SMS Queue",
        filters={
            "status": ["in", ["Queued", "Scheduled"]],
            "scheduled_time": ["<=", now]
        },
        fields=["name", "priority"],
        order_by="creation asc",
        limit=limit * 2  # Get more to sort by priority
    )

    # Also get queued without scheduled time
    queued = frappe.get_all(
        "SMS Queue",
        filters={
            "status": "Queued",
            "scheduled_time": ["is", "not set"]
        },
        fields=["name", "priority"],
        order_by="creation asc",
        limit=limit
    )

    # Combine and sort by priority
    all_pending = pending + queued
    all_pending = list({p["name"]: p for p in all_pending}.values())  # Deduplicate
    all_pending.sort(key=lambda x: priority_order.get(x.get("priority", "Normal"), 3))

    # Process limited number
    processed = 0
    sent = 0
    failed = 0

    for entry in all_pending[:limit]:
        try:
            doc = frappe.get_doc("SMS Queue", entry["name"])
            result = doc.process()

            processed += 1
            if result.get("success"):
                sent += 1
            else:
                failed += 1

        except Exception as e:
            frappe.log_error(f"SMS Queue processing error: {str(e)}", "SMS Queue")
            failed += 1

    frappe.db.commit()

    return {
        "processed": processed,
        "sent": sent,
        "failed": failed
    }


def retry_failed_sms():
    """Retry failed SMS that haven't exceeded max retries - scheduled task"""
    failed = frappe.get_all(
        "SMS Queue",
        filters={
            "status": "Failed",
            "retry_count": ["<", 3]
        },
        pluck="name"
    )

    retried = 0
    for name in failed:
        doc = frappe.get_doc("SMS Queue", name)
        doc.status = "Queued"
        doc.scheduled_time = add_to_date(now_datetime(), minutes=5)
        doc.save(ignore_permissions=True)
        retried += 1

    frappe.db.commit()
    return {"retried": retried}


def get_sms_delivery_status(message_id):
    """Get delivery status for an SMS from gateway"""
    from university_erp.university_integrations.sms_gateway import get_delivery_status

    status = get_delivery_status(message_id)

    # Update queue entry if found
    queue_entry = frappe.db.get_value(
        "SMS Queue",
        {"message_id": message_id},
        "name"
    )

    if queue_entry and status.get("status") == "Delivered":
        frappe.db.set_value("SMS Queue", queue_entry, "status", "Delivered")

    return status


def cleanup_old_queue_entries(days=30):
    """Clean up old processed queue entries - scheduled task"""
    cutoff = add_to_date(now_datetime(), days=-days)

    deleted = frappe.db.delete(
        "SMS Queue",
        filters={
            "status": ["in", ["Sent", "Delivered", "Failed", "Cancelled"]],
            "creation": ["<", cutoff]
        }
    )

    frappe.db.commit()
    return {"deleted": deleted}


# ========== API Endpoints ==========

@frappe.whitelist()
def queue_sms(mobile_number, message, scheduled_time=None, priority="Normal"):
    """API endpoint to queue an SMS"""
    return schedule_sms(mobile_number, message, scheduled_time, priority)


@frappe.whitelist()
def cancel_queued_sms(queue_id):
    """API endpoint to cancel a queued SMS"""
    doc = frappe.get_doc("SMS Queue", queue_id)
    return doc.cancel_sms()


@frappe.whitelist()
def get_queue_status(batch_id=None):
    """Get SMS queue status summary"""
    filters = {}
    if batch_id:
        filters["batch_id"] = batch_id

    status_counts = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabSMS Queue`
        {where}
        GROUP BY status
    """.format(where=f"WHERE batch_id = '{batch_id}'" if batch_id else ""), as_dict=True)

    return {
        "status_counts": {s.status: s.count for s in status_counts},
        "total": sum(s.count for s in status_counts)
    }
