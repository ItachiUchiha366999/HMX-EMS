# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Unified Communication Manager
Provides a single interface for sending notifications across all channels
with fallback logic, rate limiting, and deduplication.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, cint
import hashlib
import json


class UnifiedCommunicationManager:
    """
    Unified interface for multi-channel communication

    Supports:
    - Channel priority and fallback
    - Rate limiting across channels
    - Deduplication for multi-channel sends
    - Quiet hours enforcement
    - User preference respect
    """

    # Channel priority order (higher number = higher priority)
    CHANNEL_PRIORITY = {
        "in_app": 1,
        "email": 2,
        "push": 3,
        "sms": 4,
        "whatsapp": 5
    }

    # Rate limits per channel (messages per hour per user)
    RATE_LIMITS = {
        "email": 10,
        "sms": 5,
        "whatsapp": 5,
        "push": 20,
        "in_app": 50
    }

    def __init__(self):
        self.sent_cache = {}  # For deduplication within session

    def send(self, recipient, title, message, channels=None, category=None,
             priority="Normal", data=None, attachments=None,
             respect_preferences=True, respect_quiet_hours=True,
             fallback_on_failure=True, deduplicate=True):
        """
        Send notification through multiple channels with smart routing

        Args:
            recipient: User email or phone number
            title: Notification title
            message: Notification message
            channels: List of channels ['email', 'sms', 'whatsapp', 'push', 'in_app']
                     If None, uses all enabled channels for user
            category: Notification category for preference filtering
            priority: Low/Normal/High/Urgent
            data: Additional data payload (for push notifications)
            attachments: Email attachments
            respect_preferences: Check user notification preferences
            respect_quiet_hours: Respect user quiet hours settings
            fallback_on_failure: Try next channel if primary fails
            deduplicate: Prevent duplicate sends within short time window

        Returns:
            dict: Results for each channel attempted
        """
        user = self._get_user(recipient)
        results = {}

        # Check deduplication
        if deduplicate:
            message_hash = self._get_message_hash(recipient, title, message)
            if self._is_duplicate(message_hash):
                return {"success": False, "error": "Duplicate message blocked", "deduplicated": True}
            self._mark_sent(message_hash)

        # Get user preferences
        preferences = None
        if respect_preferences and user:
            preferences = self._get_user_preferences(user)

            # Check if notifications are enabled
            if preferences and not preferences.get("enabled"):
                return {"success": False, "error": "User has disabled notifications"}

        # Check quiet hours
        if respect_quiet_hours and preferences:
            if self._is_quiet_hours(preferences):
                if priority != "Urgent":  # Urgent bypasses quiet hours
                    return {"success": False, "error": "Quiet hours active", "quiet_hours": True}

        # Determine channels to use
        if channels is None:
            channels = self._get_enabled_channels(preferences)

        # Filter channels based on category preferences
        if category and preferences:
            channels = self._filter_by_category(channels, category, preferences)

        # Sort channels by priority
        channels = sorted(channels, key=lambda c: self.CHANNEL_PRIORITY.get(c, 0), reverse=True)

        # Send through each channel
        for channel in channels:
            # Check rate limit
            if not self._check_rate_limit(user or recipient, channel):
                results[channel] = {"success": False, "error": "Rate limit exceeded"}
                continue

            try:
                result = self._send_channel(
                    channel, recipient, user, title, message,
                    data, attachments, priority
                )
                results[channel] = result

                if result.get("success"):
                    self._increment_rate_counter(user or recipient, channel)

                    # If primary channel succeeds and no fallback needed
                    if not fallback_on_failure:
                        break
                else:
                    # Try fallback if enabled
                    if fallback_on_failure:
                        continue
                    else:
                        break

            except Exception as e:
                results[channel] = {"success": False, "error": str(e)}
                frappe.log_error(f"Channel {channel} failed: {str(e)}", "Unified Communication")

        # Determine overall success
        any_success = any(r.get("success") for r in results.values())

        return {
            "success": any_success,
            "channels": results,
            "recipient": recipient
        }

    def send_to_role(self, role, title, message, channels=None, category=None, **kwargs):
        """Send notification to all users with a specific role"""
        users = frappe.get_all(
            "Has Role",
            filters={"role": role, "parenttype": "User"},
            pluck="parent"
        )

        results = []
        for user in users:
            result = self.send(user, title, message, channels, category, **kwargs)
            results.append({"user": user, "result": result})

        return {
            "success": True,
            "total": len(users),
            "results": results
        }

    def send_to_students(self, title, message, program=None, batch=None, **kwargs):
        """Send notification to students"""
        filters = {"enabled": 1}

        students = frappe.get_all(
            "Student",
            filters=filters,
            fields=["student_email_id", "user"]
        )

        results = []
        for student in students:
            recipient = student.user or student.student_email_id
            if recipient:
                result = self.send(recipient, title, message, **kwargs)
                results.append({"recipient": recipient, "result": result})

        return {
            "success": True,
            "total": len(students),
            "sent": len([r for r in results if r["result"].get("success")])
        }

    def _get_user(self, recipient):
        """Get user from recipient (email or phone)"""
        if "@" in recipient:
            if frappe.db.exists("User", recipient):
                return recipient
        return None

    def _get_user_preferences(self, user):
        """Get user notification preferences"""
        try:
            pref = frappe.get_doc("Notification Preference", {"user": user})
            return {
                "enabled": pref.enabled,
                "email_enabled": pref.email_enabled,
                "sms_enabled": pref.sms_enabled,
                "whatsapp_enabled": pref.get("whatsapp_enabled", 0),
                "push_enabled": pref.push_enabled,
                "in_app_enabled": pref.in_app_enabled,
                "quiet_hours_enabled": pref.quiet_hours_enabled,
                "quiet_start_time": pref.quiet_start_time,
                "quiet_end_time": pref.quiet_end_time,
                "fee_notifications": pref.fee_notifications,
                "academic_notifications": pref.academic_notifications,
                "library_notifications": pref.library_notifications,
                "placement_notifications": pref.placement_notifications,
                "preferred_language": pref.get("preferred_language")
            }
        except frappe.DoesNotExistError:
            return None

    def _get_enabled_channels(self, preferences):
        """Get list of enabled channels based on preferences"""
        if not preferences:
            return ["email", "in_app"]  # Default channels

        channels = []
        if preferences.get("email_enabled"):
            channels.append("email")
        if preferences.get("sms_enabled"):
            channels.append("sms")
        if preferences.get("whatsapp_enabled"):
            channels.append("whatsapp")
        if preferences.get("push_enabled"):
            channels.append("push")
        if preferences.get("in_app_enabled"):
            channels.append("in_app")

        return channels or ["email", "in_app"]

    def _filter_by_category(self, channels, category, preferences):
        """Filter channels based on category preferences"""
        category_map = {
            "Fee": "fee_notifications",
            "Academic": "academic_notifications",
            "Library": "library_notifications",
            "Placement": "placement_notifications"
        }

        pref_field = category_map.get(category)
        if pref_field and not preferences.get(pref_field, True):
            return []  # User has disabled this category

        return channels

    def _is_quiet_hours(self, preferences):
        """Check if current time is within quiet hours"""
        if not preferences.get("quiet_hours_enabled"):
            return False

        from frappe.utils import get_time, nowtime

        current_time = get_time(nowtime())
        start_time = get_time(preferences.get("quiet_start_time", "22:00"))
        end_time = get_time(preferences.get("quiet_end_time", "07:00"))

        # Handle overnight quiet hours (e.g., 22:00 to 07:00)
        if start_time > end_time:
            return current_time >= start_time or current_time <= end_time
        else:
            return start_time <= current_time <= end_time

    def _check_rate_limit(self, recipient, channel):
        """Check if rate limit is exceeded for channel"""
        cache_key = f"rate_limit:{recipient}:{channel}"
        count = frappe.cache().get(cache_key) or 0
        limit = self.RATE_LIMITS.get(channel, 10)
        return cint(count) < limit

    def _increment_rate_counter(self, recipient, channel):
        """Increment rate limit counter"""
        cache_key = f"rate_limit:{recipient}:{channel}"
        count = frappe.cache().get(cache_key) or 0
        frappe.cache().set(cache_key, cint(count) + 1, expires_in_sec=3600)

    def _get_message_hash(self, recipient, title, message):
        """Generate hash for deduplication"""
        content = f"{recipient}:{title}:{message[:100]}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_duplicate(self, message_hash):
        """Check if message was recently sent"""
        cache_key = f"msg_dedup:{message_hash}"
        return frappe.cache().get(cache_key) is not None

    def _mark_sent(self, message_hash):
        """Mark message as sent for deduplication"""
        cache_key = f"msg_dedup:{message_hash}"
        frappe.cache().set(cache_key, 1, expires_in_sec=300)  # 5 minute window

    def _send_channel(self, channel, recipient, user, title, message, data, attachments, priority):
        """Route to appropriate channel sender"""
        if channel == "email":
            return self._send_email(recipient, title, message, attachments, priority)
        elif channel == "sms":
            return self._send_sms(recipient, message, priority)
        elif channel == "whatsapp":
            return self._send_whatsapp(recipient, message)
        elif channel == "push":
            return self._send_push(user, title, message, data)
        elif channel == "in_app":
            return self._send_in_app(user, title, message, priority)
        else:
            return {"success": False, "error": f"Unknown channel: {channel}"}

    def _send_email(self, recipient, title, message, attachments, priority):
        """Send email notification"""
        try:
            from university_erp.university_integrations.doctype.email_queue_extended.email_queue_extended import queue_email

            result = queue_email(
                recipient=recipient,
                subject=title,
                message=message,
                attachments=attachments,
                priority=priority
            )
            return result
        except Exception as e:
            # Fallback to direct send
            try:
                frappe.sendmail(
                    recipients=[recipient],
                    subject=title,
                    message=message,
                    attachments=attachments,
                    delayed=True
                )
                return {"success": True}
            except Exception as e2:
                return {"success": False, "error": str(e2)}

    def _send_sms(self, recipient, message, priority):
        """Send SMS notification"""
        try:
            from university_erp.university_integrations.doctype.sms_queue.sms_queue import schedule_sms

            # Get mobile number
            mobile = self._get_mobile(recipient)
            if not mobile:
                return {"success": False, "error": "No mobile number found"}

            result = schedule_sms(
                mobile_number=mobile,
                message=message[:160],  # SMS limit
                priority=priority
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_whatsapp(self, recipient, message):
        """Send WhatsApp notification"""
        try:
            from university_erp.university_integrations.whatsapp_gateway import get_whatsapp_gateway

            mobile = self._get_mobile(recipient)
            if not mobile:
                return {"success": False, "error": "No mobile number found"}

            gateway = get_whatsapp_gateway()
            return gateway.send_text_message(mobile, message)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_push(self, user, title, message, data):
        """Send push notification"""
        if not user:
            return {"success": False, "error": "No user for push notification"}

        try:
            from university_erp.university_integrations.firebase_admin import send_push_notification

            return send_push_notification(user, title, message, data)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_in_app(self, user, title, message, priority):
        """Send in-app notification"""
        if not user:
            return {"success": False, "error": "No user for in-app notification"}

        try:
            from university_erp.university_erp.notification_center import NotificationCenter

            priority_map = {"Low": "Low", "Normal": "Normal", "High": "High", "Urgent": "Urgent"}

            NotificationCenter.send(
                user=user,
                title=title,
                message=message,
                notification_type="info",
                priority=priority_map.get(priority, "Normal")
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_mobile(self, recipient):
        """Get mobile number from recipient"""
        if "@" in recipient:
            # It's an email, find mobile
            mobile = frappe.db.get_value("User", recipient, "mobile_no")
            if mobile:
                return mobile

            # Try Student
            student = frappe.db.get_value(
                "Student",
                {"student_email_id": recipient},
                "student_mobile_number"
            )
            if student:
                return student

            return None
        else:
            # Assume it's already a mobile number
            return recipient


# ========== Factory Function ==========

def get_unified_manager():
    """Get UnifiedCommunicationManager instance"""
    return UnifiedCommunicationManager()


# ========== Convenience Functions ==========

def unified_send(recipient, title, message, channels=None, category=None, **kwargs):
    """
    Send notification through unified communication manager

    This is the main entry point for sending notifications.

    Args:
        recipient: User email or phone number
        title: Notification title
        message: Notification message
        channels: List of channels or None for auto-selection
        category: Notification category
        **kwargs: Additional options (priority, data, attachments, etc.)

    Returns:
        dict: Send results
    """
    manager = get_unified_manager()
    return manager.send(recipient, title, message, channels, category, **kwargs)


def send_urgent(recipient, title, message, channels=None):
    """Send urgent notification (bypasses quiet hours)"""
    return unified_send(
        recipient, title, message, channels,
        priority="Urgent",
        respect_quiet_hours=False
    )


def send_broadcast(title, message, role=None, channels=None, **kwargs):
    """Send broadcast to a role or all users"""
    manager = get_unified_manager()

    if role:
        return manager.send_to_role(role, title, message, channels, **kwargs)
    else:
        # Send to all active users
        users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
        results = []
        for user in users:
            if user not in ["Administrator", "Guest"]:
                result = manager.send(user, title, message, channels, **kwargs)
                results.append({"user": user, "result": result})

        return {
            "success": True,
            "total": len(results),
            "sent": len([r for r in results if r["result"].get("success")])
        }


# ========== API Endpoints ==========

@frappe.whitelist()
def send_notification(recipient, title, message, channels=None, category=None, priority="Normal"):
    """API endpoint for unified notification sending"""
    if channels and isinstance(channels, str):
        channels = json.loads(channels)

    return unified_send(
        recipient=recipient,
        title=title,
        message=message,
        channels=channels,
        category=category,
        priority=priority
    )


@frappe.whitelist()
def send_notification_to_role(role, title, message, channels=None, category=None):
    """API endpoint for role-based notification"""
    if channels and isinstance(channels, str):
        channels = json.loads(channels)

    manager = get_unified_manager()
    return manager.send_to_role(role, title, message, channels, category)
