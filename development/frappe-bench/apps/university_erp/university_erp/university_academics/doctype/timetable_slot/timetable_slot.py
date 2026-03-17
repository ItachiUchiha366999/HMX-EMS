# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds


class TimetableSlot(Document):
	def validate(self):
		"""Calculate duration"""
		if self.start_time and self.end_time:
			diff = time_diff_in_seconds(self.end_time, self.start_time)
			self.duration_minutes = int(diff / 60)
