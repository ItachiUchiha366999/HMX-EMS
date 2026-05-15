# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


class CBCSManager:
	"""Manage Choice Based Credit System"""

	# CBCS Course Categories
	COURSE_TYPES = {
		"Core": {
			"abbreviation": "CC",
			"description": "Core Course - Compulsory",
			"credits_range": (3, 6)
		},
		"DSE": {
			"abbreviation": "DSE",
			"description": "Discipline Specific Elective",
			"credits_range": (3, 4)
		},
		"GE": {
			"abbreviation": "GE",
			"description": "Generic Elective",
			"credits_range": (3, 4)
		},
		"SEC": {
			"abbreviation": "SEC",
			"description": "Skill Enhancement Course",
			"credits_range": (2, 4)
		},
		"AEC": {
			"abbreviation": "AEC",
			"description": "Ability Enhancement Course",
			"credits_range": (2, 4)
		},
		"VAC": {
			"abbreviation": "VAC",
			"description": "Value Added Course",
			"credits_range": (2, 2)
		},
		"Project": {
			"abbreviation": "PROJ",
			"description": "Project/Dissertation",
			"credits_range": (4, 12)
		},
		"Internship": {
			"abbreviation": "INT",
			"description": "Internship/Industrial Training",
			"credits_range": (2, 6)
		}
	}

	def __init__(self, program=None):
		self.program = program
		if program:
			self.program_doc = frappe.get_doc("Program", program)

	def get_semester_courses(self, semester_number):
		"""Get all courses for a semester"""
		# This will fetch from Program curriculum once implemented
		return frappe.get_all(
			"Program Course",
			filters={
				"parent": self.program,
				"custom_semester": semester_number
			},
			fields=["course", "course_name", "required"]
		)

	def validate_course_selection(self, student, semester, courses):
		"""Validate if student can register for selected courses"""
		errors = []

		# Check prerequisites
		for course in courses:
			prerequisite_errors = self.check_prerequisites(student, course)
			errors.extend(prerequisite_errors)

		# Check credit limits
		total_credits = self.calculate_total_credits(courses)
		min_credits, max_credits = self.get_credit_limits(semester)

		if total_credits < min_credits:
			errors.append(f"Total credits ({total_credits}) below minimum ({min_credits})")
		if total_credits > max_credits:
			errors.append(f"Total credits ({total_credits}) exceeds maximum ({max_credits})")

		# Check elective selection
		elective_errors = self.validate_elective_selection(semester, courses)
		errors.extend(elective_errors)

		return errors

	def check_prerequisites(self, student, course):
		"""Check if student has completed prerequisite courses"""
		errors = []

		prerequisites = frappe.get_all(
			"Course Prerequisite",
			filters={"parent": course},
			fields=["prerequisite_course", "is_mandatory"]
		)

		for prereq in prerequisites:
			# Check if student has completed this course
			completed = frappe.db.exists(
				"Assessment Result",
				{
					"student": student,
					"course": prereq.prerequisite_course,
					"docstatus": 1,
					"custom_result_status": "Pass"
				}
			)

			if not completed and prereq.is_mandatory:
				course_name = frappe.db.get_value("Course", prereq.prerequisite_course, "course_name")
				errors.append(f"Prerequisite not met: {course_name}")

		return errors

	def calculate_total_credits(self, courses):
		"""Calculate total credits from course list"""
		total = 0.0
		for course in courses:
			credits = frappe.db.get_value("Course", course, "custom_credits") or 0.0
			total += flt(credits)
		return total

	def get_credit_limits(self, semester):
		"""Get min and max credit limits for semester"""
		# Default limits - can be configured per program
		min_credits = 18.0
		max_credits = 26.0

		if self.program:
			min_credits = frappe.db.get_value(
				"Program",
				self.program,
				"custom_min_credits_per_semester"
			) or min_credits
			max_credits = frappe.db.get_value(
				"Program",
				self.program,
				"custom_max_credits_per_semester"
			) or max_credits

		return min_credits, max_credits

	def validate_elective_selection(self, semester, selected_courses):
		"""Validate elective course selection against groups"""
		errors = []

		# Get elective groups for this semester
		elective_groups = frappe.get_all(
			"Elective Course Group",
			filters={
				"program": self.program,
				"semester": semester
			},
			fields=["name", "min_courses_to_select", "max_courses_to_select"]
		)

		for group in elective_groups:
			# Get courses in this group
			group_courses = frappe.get_all(
				"Elective Course Group Item",
				filters={"parent": group.name},
				pluck="course"
			)

			# Count how many from this group are selected
			selected_from_group = [c for c in selected_courses if c in group_courses]
			count = len(selected_from_group)

			if count < (group.min_courses_to_select or 0):
				errors.append(
					f"Must select at least {group.min_courses_to_select} "
					f"courses from {group.name}"
				)

			if group.max_courses_to_select and count > group.max_courses_to_select:
				errors.append(
					f"Cannot select more than {group.max_courses_to_select} "
					f"courses from {group.name}"
				)

		return errors


@frappe.whitelist()
def validate_course_registration(student, semester, courses):
	"""API to validate course registration"""
	if isinstance(courses, str):
		import json
		courses = json.loads(courses)

	program = frappe.db.get_value("Student", student, "custom_program")
	manager = CBCSManager(program)

	errors = manager.validate_course_selection(student, int(semester), courses)

	return {
		"valid": len(errors) == 0,
		"errors": errors
	}


@frappe.whitelist()
def calculate_credits_from_ltp(lecture_hours, tutorial_hours, practical_hours):
	"""Calculate credits from L-T-P hours"""
	lecture = flt(lecture_hours) or 0.0
	tutorial = flt(tutorial_hours) or 0.0
	practical = flt(practical_hours) or 0.0

	# Formula: Credits = L + T + (P/2)
	credits = lecture + tutorial + (practical / 2.0)

	return round(credits, 1)


@frappe.whitelist()
def get_course_types():
	"""Get list of CBCS course types"""
	manager = CBCSManager()
	return manager.COURSE_TYPES
