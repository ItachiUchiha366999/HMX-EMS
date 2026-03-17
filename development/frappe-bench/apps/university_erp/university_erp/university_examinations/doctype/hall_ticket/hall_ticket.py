# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import hashlib


class HallTicket(Document):
	def before_save(self):
		"""Generate verification code"""
		if not self.verification_code:
			data = f"{self.student}{self.academic_term}{self.name}"
			self.verification_code = hashlib.md5(data.encode()).hexdigest()[:10].upper()

	def validate(self):
		"""Validate hall ticket eligibility"""
		self.check_eligibility()

	def check_eligibility(self):
		"""Check if student is eligible for exams"""
		# Check attendance eligibility for all courses
		from university_erp.academics.attendance import AttendanceManager
		
		manager = AttendanceManager()
		ineligible_courses = []
		
		for exam in self.exams:
			result = manager.check_exam_eligibility(
				self.student,
				exam.course,
				self.academic_term
			)
			if not result.get("eligible"):
				ineligible_courses.append(exam.course_name)
		
		if ineligible_courses:
			self.is_eligible = 0
			self.ineligibility_reason = f"Attendance shortage in: {', '.join(ineligible_courses)}"
