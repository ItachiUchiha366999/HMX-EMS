# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExamSchedule(Document):
	def validate(self):
		"""Validate exam schedule"""
		self.check_venue_conflict()
		self.check_instructor_conflict()

	def check_venue_conflict(self):
		"""Check if venue is already booked"""
		conflict = frappe.db.exists(
			"Exam Schedule",
			{
				"venue": self.venue,
				"exam_date": self.exam_date,
				"start_time": ["<", self.end_time],
				"end_time": [">", self.start_time],
				"name": ["!=", self.name]
			}
		)
		if conflict:
			frappe.throw(f"Venue {self.venue} already booked for this time slot")

	def check_instructor_conflict(self):
		"""Check if any invigilator has conflict"""
		for invigilator in self.invigilators:
			conflict = frappe.db.sql("""
				SELECT parent FROM `tabExam Invigilator`
				WHERE instructor = %(instructor)s
				AND parent IN (
					SELECT name FROM `tabExam Schedule`
					WHERE exam_date = %(exam_date)s
					AND start_time < %(end_time)s
					AND end_time > %(start_time)s
					AND name != %(name)s
				)
			""", {
				"instructor": invigilator.instructor,
				"exam_date": self.exam_date,
				"start_time": self.start_time,
				"end_time": self.end_time,
				"name": self.name or ""
			})
			if conflict:
				frappe.throw(f"Instructor {invigilator.instructor_name} has conflicting exam duty")
