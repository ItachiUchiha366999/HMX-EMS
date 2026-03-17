# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GrievanceCommittee(Document):
    """Grievance Committee DocType for managing grievance redressal committees"""

    def validate(self):
        """Validate committee configuration"""
        self.validate_chairperson_not_in_members()
        self.validate_secretary_not_chairperson()

    def validate_chairperson_not_in_members(self):
        """Ensure chairperson is not duplicated in members list"""
        if self.members:
            member_users = [m.user for m in self.members]
            if self.chairperson in member_users:
                frappe.throw(_("Chairperson should not be listed in members table"))

    def validate_secretary_not_chairperson(self):
        """Ensure secretary is different from chairperson"""
        if self.secretary and self.secretary == self.chairperson:
            frappe.throw(_("Secretary and Chairperson must be different persons"))

    def get_active_members(self):
        """Get list of all active committee members including chairperson and secretary"""
        members = []

        # Add chairperson
        if self.chairperson:
            members.append({
                "user": self.chairperson,
                "role": "Chairperson"
            })

        # Add secretary
        if self.secretary:
            members.append({
                "user": self.secretary,
                "role": "Secretary"
            })

        # Add other members
        for member in self.members or []:
            members.append({
                "user": member.user,
                "role": member.role_in_committee or "Member",
                "designation": member.designation
            })

        return members

    def get_all_member_emails(self):
        """Get email addresses of all committee members"""
        emails = []
        members = self.get_active_members()

        for member in members:
            email = frappe.db.get_value("User", member["user"], "email")
            if email:
                emails.append(email)

        return list(set(emails))

    def handles_category(self, category):
        """Check if this committee handles a specific grievance category"""
        if not self.grievance_categories:
            return True  # Handle all if no specific categories defined

        for cat_link in self.grievance_categories:
            if cat_link.category == category:
                return True

        return False
