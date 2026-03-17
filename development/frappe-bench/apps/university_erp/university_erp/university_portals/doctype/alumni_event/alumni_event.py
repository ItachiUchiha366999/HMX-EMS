# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, nowdate


class AlumniEvent(Document):
    def validate(self):
        self.validate_dates()

    def validate_dates(self):
        """Validate event dates"""
        if self.registration_deadline and self.event_date:
            if getdate(self.registration_deadline) > getdate(self.event_date):
                frappe.throw(_("Registration deadline cannot be after the event date"))

        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                frappe.throw(_("End time must be after start time"))

    def get_registration_count(self):
        """Get count of registrations for this event"""
        return frappe.db.count("Alumni Event Registration", {
            "event": self.name
        })

    def is_registration_open(self):
        """Check if registration is open"""
        if self.status != "Open":
            return False

        if self.registration_deadline and getdate(self.registration_deadline) < getdate(nowdate()):
            return False

        if self.max_participants:
            if self.get_registration_count() >= self.max_participants:
                return False

        return True
