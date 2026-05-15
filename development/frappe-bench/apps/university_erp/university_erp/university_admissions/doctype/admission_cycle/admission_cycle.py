# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class AdmissionCycle(Document):
	def validate(self):
		"""Validate admission cycle dates"""
		self.validate_dates()

	def validate_dates(self):
		"""Ensure dates are in logical order"""
		if self.application_start_date and self.application_deadline:
			if getdate(self.application_deadline) < getdate(self.application_start_date):
				frappe.throw("Application Deadline cannot be before Application Start Date")

		if self.counseling_start_date and self.application_deadline:
			if getdate(self.counseling_start_date) < getdate(self.application_deadline):
				frappe.throw("Counseling Start Date should be after Application Deadline")

		if self.admission_deadline and self.counseling_start_date:
			if getdate(self.admission_deadline) < getdate(self.counseling_start_date):
				frappe.throw("Admission Deadline should be after Counseling Start Date")

	def on_update(self):
		"""Auto-update status based on dates"""
		self.update_status()

	def update_status(self):
		"""Update status based on current date"""
		from frappe.utils import today, getdate

		current_date = getdate(today())

		if getdate(self.application_start_date) > current_date:
			self.db_set('status', 'Upcoming', update_modified=False)
		elif getdate(self.application_deadline) >= current_date:
			self.db_set('status', 'Open', update_modified=False)
		elif self.admission_deadline and getdate(self.admission_deadline) >= current_date:
			self.db_set('status', 'Closed', update_modified=False)
		else:
			self.db_set('status', 'Completed', update_modified=False)
