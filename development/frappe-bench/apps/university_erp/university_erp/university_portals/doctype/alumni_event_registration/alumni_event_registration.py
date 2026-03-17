# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class AlumniEventRegistration(Document):
    def validate(self):
        self.validate_duplicate()
        self.validate_event_capacity()
        self.set_payment_amount()

    def validate_duplicate(self):
        """Check for duplicate registration"""
        existing = frappe.db.exists("Alumni Event Registration", {
            "event": self.event,
            "alumni": self.alumni,
            "name": ["!=", self.name],
            "attendance_status": ["!=", "Cancelled"]
        })
        if existing:
            frappe.throw(_("This alumni is already registered for this event"))

    def validate_event_capacity(self):
        """Check if event has capacity"""
        event = frappe.get_doc("Alumni Event", self.event)
        if not event.is_registration_open() and self.is_new():
            frappe.throw(_("Registration is closed for this event"))

    def set_payment_amount(self):
        """Set payment amount from event if not set"""
        if not self.payment_amount:
            event = frappe.get_doc("Alumni Event", self.event)
            self.payment_amount = event.registration_fee or 0
