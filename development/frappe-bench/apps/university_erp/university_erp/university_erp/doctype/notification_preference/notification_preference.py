# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NotificationPreference(Document):
    def validate(self):
        self.validate_quiet_hours()

    def validate_quiet_hours(self):
        """Validate quiet hours configuration"""
        if self.quiet_hours_enabled:
            if not self.quiet_start_time or not self.quiet_end_time:
                frappe.throw("Please set both quiet start and end times")


@frappe.whitelist()
def get_user_preferences(user=None):
    """Get notification preferences for a user"""
    if not user:
        user = frappe.session.user

    preferences = frappe.db.get_value(
        "Notification Preference",
        {"user": user},
        [
            "enabled", "email_enabled", "sms_enabled", "push_enabled",
            "in_app_enabled", "fee_notifications", "academic_notifications",
            "library_notifications", "placement_notifications",
            "quiet_hours_enabled", "quiet_start_time", "quiet_end_time",
            "email_digest", "digest_frequency"
        ],
        as_dict=True
    )

    if not preferences:
        # Return defaults
        return {
            "enabled": 1,
            "email_enabled": 1,
            "sms_enabled": 0,
            "push_enabled": 1,
            "in_app_enabled": 1,
            "fee_notifications": 1,
            "academic_notifications": 1,
            "library_notifications": 1,
            "placement_notifications": 1,
            "quiet_hours_enabled": 0,
            "email_digest": 0
        }

    return preferences


@frappe.whitelist()
def update_preferences(preferences):
    """Update notification preferences for current user"""
    import json
    if isinstance(preferences, str):
        preferences = json.loads(preferences)

    user = frappe.session.user
    pref_name = f"{user}-preferences"

    if frappe.db.exists("Notification Preference", pref_name):
        doc = frappe.get_doc("Notification Preference", pref_name)
    else:
        doc = frappe.new_doc("Notification Preference")
        doc.user = user

    for key, value in preferences.items():
        if hasattr(doc, key):
            setattr(doc, key, value)

    doc.save(ignore_permissions=True)
    return {"success": True, "message": "Preferences updated"}


def should_send_notification(user, category, channel):
    """Check if notification should be sent based on user preferences"""
    preferences = get_user_preferences(user)

    if not preferences.get("enabled"):
        return False

    # Check channel
    channel_field = f"{channel}_enabled"
    if not preferences.get(channel_field, True):
        return False

    # Check category
    category_field = f"{category}_notifications"
    if not preferences.get(category_field, True):
        return False

    # Check quiet hours
    if preferences.get("quiet_hours_enabled"):
        from frappe.utils import now_datetime, get_time
        current_time = now_datetime().time()
        quiet_start = get_time(preferences.get("quiet_start_time", "22:00"))
        quiet_end = get_time(preferences.get("quiet_end_time", "07:00"))

        # Handle overnight quiet hours
        if quiet_start > quiet_end:
            # e.g., 22:00 to 07:00
            if current_time >= quiet_start or current_time <= quiet_end:
                return False
        else:
            # e.g., 01:00 to 06:00
            if quiet_start <= current_time <= quiet_end:
                return False

    return True
