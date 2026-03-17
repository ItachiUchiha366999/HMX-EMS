# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, nowdate


class PlacementDrive(Document):
    def validate(self):
        self.validate_dates()
        self.update_stats()

    def validate_dates(self):
        """Validate drive dates"""
        if getdate(self.last_date_to_apply) > getdate(self.drive_date):
            frappe.throw(_("Last date to apply cannot be after the drive date"))

    def update_stats(self):
        """Update application statistics"""
        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status IN ('Shortlisted', 'Interview Scheduled', 'Selected') THEN 1 ELSE 0 END) as shortlisted,
                SUM(CASE WHEN status = 'Selected' THEN 1 ELSE 0 END) as selected
            FROM `tabPlacement Application`
            WHERE placement_drive = %s
        """, self.name, as_dict=1)

        if stats:
            self.applications_count = stats[0].total or 0
            self.shortlisted_count = stats[0].shortlisted or 0
            self.selected_count = stats[0].selected or 0

    def is_application_open(self):
        """Check if applications are open"""
        if self.status != "Open":
            return False

        if getdate(self.last_date_to_apply) < getdate(nowdate()):
            return False

        return True
