# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PlacementProfile(Document):
    def validate(self):
        self.fetch_student_details()

    def fetch_student_details(self):
        """Fetch CGPA from student's latest result"""
        if self.student and not self.cgpa:
            cgpa = frappe.db.get_value(
                "Student Result",
                {"student": self.student, "docstatus": 1},
                "cgpa",
                order_by="academic_year desc, academic_term desc"
            )
            if cgpa:
                self.cgpa = cgpa
