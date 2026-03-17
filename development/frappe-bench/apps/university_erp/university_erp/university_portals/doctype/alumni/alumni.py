# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class Alumni(Document):
    def validate(self):
        self.validate_student()
        self.set_student_details()

    def validate_student(self):
        """Validate student exists and is not already an alumni"""
        if self.student:
            existing = frappe.db.get_value(
                "Alumni",
                {"student": self.student, "name": ["!=", self.name]},
                "name"
            )
            if existing:
                frappe.throw(_("An alumni record already exists for this student: {0}").format(existing))

    def set_student_details(self):
        """Set student details from linked student"""
        if self.student and not self.student_name:
            student_doc = frappe.get_doc("Student", self.student)
            self.student_name = student_doc.student_name
            if not self.email:
                self.email = student_doc.student_email_id
            if not self.program:
                self.program = student_doc.program
            if not self.batch:
                self.batch = student_doc.student_batch_name

    def on_update(self):
        """Create user account if not exists"""
        if self.email and not self.user:
            self.create_user_account()

    def create_user_account(self):
        """Create a user account for the alumni"""
        if frappe.db.exists("User", self.email):
            self.db_set("user", self.email)
            return

        user = frappe.get_doc({
            "doctype": "User",
            "email": self.email,
            "first_name": self.student_name.split()[0] if self.student_name else "Alumni",
            "last_name": " ".join(self.student_name.split()[1:]) if self.student_name and len(self.student_name.split()) > 1 else "",
            "enabled": 1,
            "user_type": "Website User"
        })
        user.flags.ignore_permissions = True
        user.insert()

        self.db_set("user", user.name)
