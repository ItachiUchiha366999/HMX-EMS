# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class EmergencyAcknowledgment(Document):
    def before_insert(self):
        if not self.acknowledged_at:
            self.acknowledged_at = now_datetime()

        # Capture IP and device info
        self.ip_address = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None

        user_agent = frappe.request.headers.get('User-Agent', '') if frappe.request else ''
        if user_agent:
            self.device_info = user_agent[:140]  # Truncate to fit field

    def after_insert(self):
        """Update emergency alert counts"""
        frappe.db.sql("""
            UPDATE `tabEmergency Alert`
            SET acknowledgments_received = (
                SELECT COUNT(*) FROM `tabEmergency Acknowledgment`
                WHERE emergency_alert = %s
            )
            WHERE name = %s
        """, (self.emergency_alert, self.emergency_alert))
