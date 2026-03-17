# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate


class Announcement(Document):
    def validate(self):
        self.validate_dates()
        self.validate_audience()

    def validate_dates(self):
        """Validate publish and expiry dates"""
        if getdate(self.expiry_date) < getdate(self.publish_date):
            frappe.throw(_("Expiry date cannot be before publish date"))

    def validate_audience(self):
        """Ensure at least one audience is selected"""
        if not any([self.for_students, self.for_faculty, self.for_parents, self.for_alumni]):
            frappe.throw(_("Please select at least one target audience"))
