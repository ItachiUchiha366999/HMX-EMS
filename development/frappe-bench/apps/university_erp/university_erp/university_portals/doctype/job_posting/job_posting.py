# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, nowdate


class JobPosting(Document):
    def validate(self):
        self.set_alumni_posting()
        self.auto_close_expired()

    def set_alumni_posting(self):
        """Set is_alumni_posting flag"""
        if self.posted_by:
            self.is_alumni_posting = 1

    def auto_close_expired(self):
        """Auto close expired postings"""
        if self.expiry_date and getdate(self.expiry_date) < getdate(nowdate()):
            self.status = "Closed"
