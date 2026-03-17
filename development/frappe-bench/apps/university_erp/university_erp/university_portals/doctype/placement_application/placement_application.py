# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PlacementApplication(Document):
    def validate(self):
        self.validate_duplicate()
        self.validate_eligibility()

    def validate_duplicate(self):
        """Check for duplicate application"""
        existing = frappe.db.exists("Placement Application", {
            "student": self.student,
            "placement_drive": self.placement_drive,
            "name": ["!=", self.name],
            "status": ["!=", "Withdrawn"]
        })
        if existing:
            frappe.throw(_("You have already applied for this placement drive"))

    def validate_eligibility(self):
        """Validate student eligibility for the drive"""
        if self.is_new():
            drive = frappe.get_doc("Placement Drive", self.placement_drive)

            # Check if applications are open
            if not drive.is_application_open():
                frappe.throw(_("Applications are closed for this placement drive"))

            # Check CGPA requirement
            if drive.minimum_cgpa:
                profile = frappe.db.get_value("Placement Profile", {"student": self.student}, "cgpa")
                if profile and profile < drive.minimum_cgpa:
                    frappe.throw(_("Your CGPA ({0}) does not meet the minimum requirement ({1})").format(
                        profile, drive.minimum_cgpa))

    def on_update(self):
        """Update placement drive statistics"""
        if self.placement_drive:
            drive = frappe.get_doc("Placement Drive", self.placement_drive)
            drive.update_stats()
            drive.db_update()

        # Update placement profile if selected
        if self.status == "Selected":
            frappe.db.set_value("Placement Profile", {"student": self.student}, "status", "Placed")
