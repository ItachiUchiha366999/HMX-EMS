# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_datetime
import json


class EmailQueueExtended(Document):
    def validate(self):
        self.validate_scheduled_time()

    def validate_scheduled_time(self):
        """Validate scheduled time is in future"""
        if self.scheduled_time:
            if get_datetime(self.scheduled_time) <= now_datetime():
                self.status = "Queued"
            else:
                self.status = "Scheduled"

    def process(self):
        """Process this queued email"""
        if self.status not in ["Queued", "Scheduled"]:
            return {"success": False, "error": f"Cannot process email with status {self.status}"}

        self.status = "Processing"
        self.save(ignore_permissions=True)

        try:
            # Parse attachments if JSON
            attachments = None
            if self.attachments:
                try:
                    attachments = json.loads(self.attachments)
                except json.JSONDecodeError:
                    pass

            # Parse CC and BCC
            cc = [e.strip() for e in self.cc.split(",")] if self.cc else None
            bcc = [e.strip() for e in self.bcc.split(",")] if self.bcc else None

            # Send email using Frappe's email queue
            frappe.sendmail(
                recipients=[self.recipient],
                cc=cc,
                bcc=bcc,
                subject=self.subject,
                message=self.message,
                attachments=attachments,
                delayed=False,
                now=True
            )

            self.status = "Sent"
            self.sent_at = now_datetime()
            self.save(ignore_permissions=True)

            return {"success": True}

        except Exception as e:
            self.handle_failure(str(e))
            self.save(ignore_permissions=True)
            return {"success": False, "error": str(e)}

    def handle_failure(self, error_message):
        """Handle email sending failure with retry logic"""
        self.error_message = error_message
        self.retry_count = (self.retry_count or 0) + 1

        if self.retry_count < (self.max_retries or 3):
            retry_minutes = self.retry_after or 10
            self.scheduled_time = add_to_date(now_datetime(), minutes=retry_minutes)
            self.status = "Scheduled"
        else:
            self.status = "Failed"

    def mark_bounced(self, reason=None):
        """Mark email as bounced"""
        self.bounced = 1
        self.bounce_reason = reason
        self.status = "Bounced"
        self.save(ignore_permissions=True)

    def mark_opened(self):
        """Mark email as opened"""
        if not self.opened:
            self.opened = 1
            self.opened_at = now_datetime()
            self.save(ignore_permissions=True)

    def mark_clicked(self):
        """Mark email link as clicked"""
        if not self.clicked:
            self.clicked = 1
            self.clicked_at = now_datetime()
            self.save(ignore_permissions=True)


# ========== Email Queue Functions ==========

def queue_email(recipient, subject, message, cc=None, bcc=None, scheduled_time=None,
                priority="Normal", category=None, template_name=None,
                attachments=None, recipient_name=None):
    """
    Queue an email for sending with priority and retry support

    Args:
        recipient: Recipient email address
        subject: Email subject
        message: Email body (HTML)
        cc: CC recipients (comma-separated string or list)
        bcc: BCC recipients (comma-separated string or list)
        scheduled_time: When to send (None = immediate)
        priority: Low/Normal/High/Urgent
        category: Email category for filtering
        template_name: Optional template reference
        attachments: List of attachments or JSON string
        recipient_name: Optional recipient name

    Returns:
        dict: Queue entry details
    """
    status = "Scheduled" if scheduled_time else "Queued"

    # Convert lists to comma-separated strings
    if isinstance(cc, list):
        cc = ", ".join(cc)
    if isinstance(bcc, list):
        bcc = ", ".join(bcc)
    if isinstance(attachments, list):
        attachments = json.dumps(attachments)

    queue_entry = frappe.get_doc({
        "doctype": "Email Queue Extended",
        "recipient": recipient,
        "recipient_name": recipient_name,
        "subject": subject,
        "message": message,
        "cc": cc,
        "bcc": bcc,
        "scheduled_time": scheduled_time,
        "status": status,
        "priority": priority,
        "category": category,
        "template_name": template_name,
        "attachments": attachments
    })
    queue_entry.insert(ignore_permissions=True)

    return {
        "success": True,
        "queue_id": queue_entry.name,
        "status": status
    }


def queue_bulk_email(recipients, subject, message, priority="Normal", category=None):
    """
    Queue bulk emails with personalization support

    Args:
        recipients: List of dicts with email and optional name
        subject: Email subject (can contain {name} placeholder)
        message: Email body (can contain {name} placeholder)
        priority: Email priority
        category: Email category

    Returns:
        dict: Batch summary
    """
    queued_count = 0

    for recipient in recipients:
        email = recipient.get("email") or recipient.get("recipient")
        if not email:
            continue

        name = recipient.get("name") or recipient.get("recipient_name", "")

        # Personalize subject and message
        personalized_subject = subject.replace("{name}", name) if name else subject
        personalized_message = message.replace("{name}", name) if name else message

        queue_email(
            recipient=email,
            subject=personalized_subject,
            message=personalized_message,
            priority=priority,
            category=category,
            recipient_name=name
        )
        queued_count += 1

    frappe.db.commit()

    return {
        "success": True,
        "queued_count": queued_count,
        "total_recipients": len(recipients)
    }


def process_email_queue(limit=50):
    """
    Process pending email queue entries - scheduled task

    Args:
        limit: Maximum number of emails to process in one run

    Returns:
        dict: Processing summary
    """
    now = now_datetime()
    priority_order = {"Urgent": 1, "High": 2, "Normal": 3, "Low": 4}

    # Get pending entries
    pending = frappe.get_all(
        "Email Queue Extended",
        filters={
            "status": ["in", ["Queued", "Scheduled"]],
            "scheduled_time": ["<=", now]
        },
        fields=["name", "priority"],
        order_by="creation asc",
        limit=limit * 2
    )

    # Get queued without scheduled time
    queued = frappe.get_all(
        "Email Queue Extended",
        filters={
            "status": "Queued",
            "scheduled_time": ["is", "not set"]
        },
        fields=["name", "priority"],
        order_by="creation asc",
        limit=limit
    )

    # Combine, dedupe, and sort by priority
    all_pending = pending + queued
    all_pending = list({p["name"]: p for p in all_pending}.values())
    all_pending.sort(key=lambda x: priority_order.get(x.get("priority", "Normal"), 3))

    processed = 0
    sent = 0
    failed = 0

    for entry in all_pending[:limit]:
        try:
            doc = frappe.get_doc("Email Queue Extended", entry["name"])
            result = doc.process()

            processed += 1
            if result.get("success"):
                sent += 1
            else:
                failed += 1

        except Exception as e:
            frappe.log_error(f"Email Queue processing error: {str(e)}", "Email Queue")
            failed += 1

    frappe.db.commit()

    return {
        "processed": processed,
        "sent": sent,
        "failed": failed
    }


def retry_failed_emails():
    """Retry failed emails that haven't exceeded max retries - scheduled task"""
    failed = frappe.get_all(
        "Email Queue Extended",
        filters={
            "status": "Failed",
            "retry_count": ["<", 3]
        },
        pluck="name"
    )

    retried = 0
    for name in failed:
        doc = frappe.get_doc("Email Queue Extended", name)
        doc.status = "Queued"
        doc.scheduled_time = add_to_date(now_datetime(), minutes=10)
        doc.save(ignore_permissions=True)
        retried += 1

    frappe.db.commit()
    return {"retried": retried}


def handle_bounce(email_address, bounce_reason=None):
    """
    Handle email bounce notification

    Args:
        email_address: Bounced email address
        bounce_reason: Reason for bounce

    Returns:
        dict: Update result
    """
    # Find recent emails to this address
    recent_emails = frappe.get_all(
        "Email Queue Extended",
        filters={
            "recipient": email_address,
            "status": "Sent",
            "sent_at": [">=", add_to_date(now_datetime(), days=-7)]
        },
        pluck="name",
        limit=5
    )

    updated = 0
    for name in recent_emails:
        doc = frappe.get_doc("Email Queue Extended", name)
        doc.mark_bounced(bounce_reason)
        updated += 1

    # Log the bounce for the email address
    frappe.log_error(
        f"Email bounce for {email_address}: {bounce_reason}",
        "Email Bounce"
    )

    return {"updated": updated, "email": email_address}


def get_email_delivery_stats(days=30):
    """Get email delivery statistics"""
    cutoff = add_to_date(now_datetime(), days=-days)

    stats = frappe.db.sql("""
        SELECT
            status,
            COUNT(*) as count,
            category
        FROM `tabEmail Queue Extended`
        WHERE creation >= %s
        GROUP BY status, category
    """, (cutoff,), as_dict=True)

    # Calculate rates
    total = sum(s.count for s in stats)
    sent = sum(s.count for s in stats if s.status == "Sent")
    bounced = sum(s.count for s in stats if s.status == "Bounced")
    opened = frappe.db.count("Email Queue Extended", {"opened": 1, "creation": [">=", cutoff]})

    return {
        "total": total,
        "sent": sent,
        "bounced": bounced,
        "opened": opened,
        "delivery_rate": round(sent / total * 100, 1) if total else 0,
        "bounce_rate": round(bounced / sent * 100, 1) if sent else 0,
        "open_rate": round(opened / sent * 100, 1) if sent else 0,
        "by_status": {s.status: s.count for s in stats},
        "by_category": {}
    }


def cleanup_old_emails(days=90):
    """Clean up old processed email queue entries - scheduled task"""
    cutoff = add_to_date(now_datetime(), days=-days)

    deleted = frappe.db.delete(
        "Email Queue Extended",
        filters={
            "status": ["in", ["Sent", "Failed", "Bounced", "Cancelled"]],
            "creation": ["<", cutoff]
        }
    )

    frappe.db.commit()
    return {"deleted": deleted}


# ========== API Endpoints ==========

@frappe.whitelist()
def send_priority_email(recipient, subject, message, priority="High", category=None):
    """API endpoint to send a priority email"""
    return queue_email(
        recipient=recipient,
        subject=subject,
        message=message,
        priority=priority,
        category=category
    )


@frappe.whitelist()
def get_email_queue_status():
    """Get email queue status summary"""
    status_counts = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabEmail Queue Extended`
        GROUP BY status
    """, as_dict=True)

    return {
        "status_counts": {s.status: s.count for s in status_counts},
        "total": sum(s.count for s in status_counts)
    }
