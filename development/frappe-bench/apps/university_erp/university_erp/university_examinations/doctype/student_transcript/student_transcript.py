# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import hashlib


class StudentTranscript(Document):
	def before_save(self):
		"""Generate verification code and calculate totals"""
		if not self.verification_code:
			data = f"{self.student}{self.name}{frappe.utils.now()}"
			self.verification_code = hashlib.md5(data.encode()).hexdigest()[:12].upper()
		
		self.calculate_totals()

	def calculate_totals(self):
		"""Calculate total credits and CGPA"""
		total_credits = 0.0
		
		for sem in self.semester_results:
			total_credits += sem.credits_earned or 0.0
		
		self.total_credits_earned = total_credits
		
		# CGPA is from last semester
		if self.semester_results:
			self.cgpa = self.semester_results[-1].cgpa or 0.0
			self.degree_classification = self.get_degree_classification(self.cgpa)

	def get_degree_classification(self, cgpa):
		"""Get degree classification based on CGPA"""
		if cgpa >= 9.0:
			return "First Class with Distinction"
		elif cgpa >= 7.5:
			return "First Class"
		elif cgpa >= 6.0:
			return "Second Class"
		elif cgpa >= 4.0:
			return "Pass"
		else:
			return "Incomplete"
