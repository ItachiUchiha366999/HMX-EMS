# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CourseRegistration(Document):
	def validate(self):
		"""Validate course registration"""
		self.calculate_total_credits()
		self.validate_prerequisites()

	def calculate_total_credits(self):
		"""Calculate total credits from courses"""
		total = 0.0
		for course in self.courses:
			total += course.credits or 0.0
		self.total_credits = total

	def validate_prerequisites(self):
		"""Check if student has completed prerequisites"""
		# Will be implemented with CBCS validation
		pass
