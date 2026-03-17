# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UserDeviceToken(Document):
    def before_insert(self):
        # Check for duplicate token
        existing = frappe.db.get_value(
            "User Device Token",
            {"token": self.token},
            "name"
        )

        if existing:
            # Update existing instead of creating new
            frappe.db.set_value("User Device Token", existing, {
                "user": self.user,
                "platform": self.platform,
                "device_name": self.device_name,
                "device_id": self.device_id,
                "active": 1,
                "last_used": frappe.utils.now_datetime()
            })
            frappe.throw(f"Token already exists, updated instead", frappe.DuplicateEntryError)

        if not self.created_at:
            self.created_at = frappe.utils.now_datetime()

    def validate(self):
        if not self.token:
            frappe.throw("Device token is required")

    def deactivate(self):
        """Deactivate this token"""
        self.active = 0
        self.save(ignore_permissions=True)

    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used = frappe.utils.now_datetime()
        self.save(ignore_permissions=True)


def get_user_tokens(user, platform=None, active_only=True):
    """Get device tokens for a user"""
    filters = {"user": user}

    if active_only:
        filters["active"] = 1

    if platform:
        filters["platform"] = platform

    return frappe.get_all(
        "User Device Token",
        filters=filters,
        fields=["name", "token", "platform", "device_name", "device_id"]
    )


def deactivate_user_tokens(user, platform=None):
    """Deactivate all tokens for a user"""
    filters = {"user": user}

    if platform:
        filters["platform"] = platform

    tokens = frappe.get_all("User Device Token", filters=filters, pluck="name")

    for token_name in tokens:
        frappe.db.set_value("User Device Token", token_name, "active", 0)

    frappe.db.commit()


def cleanup_inactive_tokens(days=90):
    """Remove tokens not used in specified days"""
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -days)

    inactive_tokens = frappe.get_all(
        "User Device Token",
        filters={
            "active": 0,
            "last_used": ["<", cutoff]
        },
        pluck="name"
    )

    for token_name in inactive_tokens:
        frappe.delete_doc("User Device Token", token_name, force=True, ignore_permissions=True)

    frappe.db.commit()

    return len(inactive_tokens)
