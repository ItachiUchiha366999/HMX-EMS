# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document


class Program(Document):
	def validate(self):
		# University-specific validations (absorbed from former UniversityProgram override)
		self.validate_program_code()
		self.validate_cbcs_structure()
		self.calculate_total_credits()

	def get_course_list(self):
		program_course_list = self.courses
		course_list = [
			frappe.get_doc("Course", program_course.course)
			for program_course in program_course_list
		]
		return course_list

	# =========================================================================
	# University-specific methods (absorbed from former UniversityProgram override)
	# =========================================================================

	def validate_program_code(self):
		"""Validate that program code is unique"""
		if not self.get("custom_program_code"):
			return

		existing = frappe.db.exists(
			"Program",
			{"custom_program_code": self.custom_program_code, "name": ("!=", self.name)},
		)

		if existing:
			frappe.throw(
				_("Program Code {0} already exists").format(self.custom_program_code)
			)

	def validate_cbcs_structure(self):
		"""Validate CBCS credit structure"""
		if self.get("custom_credit_system") != "CBCS":
			return

		if not self.get("custom_min_credits_graduation"):
			frappe.throw(_("Minimum Credits for Graduation is mandatory for CBCS programs"))

		if not self.get("custom_duration_years"):
			frappe.throw(_("Duration in Years is mandatory"))

		if self.custom_min_credits_graduation < 100:
			frappe.msgprint(
				_("Minimum credits ({0}) seems low for a degree program").format(
					self.custom_min_credits_graduation
				),
				alert=True,
				indicator="orange",
			)

	def calculate_total_credits(self):
		"""Calculate total credits from all courses in the program"""
		if not self.courses:
			self.custom_total_credits = 0.0
			return

		total_credits = 0.0

		for course_row in self.courses:
			if course_row.course:
				course = frappe.get_doc("Course", course_row.course)
				credits = course.get("custom_credits") or 0.0
				total_credits += credits

		self.custom_total_credits = total_credits

		if (
			self.get("custom_credit_system") == "CBCS"
			and self.get("custom_min_credits_graduation")
		):
			if total_credits < self.custom_min_credits_graduation:
				frappe.msgprint(
					_(
						"Total program credits ({0}) is less than minimum required ({1})"
					).format(total_credits, self.custom_min_credits_graduation),
					alert=True,
					indicator="orange",
				)


# =============================================================================
# Module-level helpers (absorbed from former university_erp.overrides.program)
# =============================================================================


def get_program_courses(program):
	"""Get all courses for a program with their credits"""
	if not program:
		return []

	program_doc = frappe.get_doc("Program", program)
	courses = []

	if program_doc.courses:
		for course_row in program_doc.courses:
			if course_row.course:
				course = frappe.get_doc("Course", course_row.course)
				courses.append(
					{
						"course": course.name,
						"course_name": course.course_name,
						"course_code": course.get("custom_course_code"),
						"credits": course.get("custom_credits"),
						"course_type": course.get("custom_course_type"),
						"required": course_row.required,
					}
				)

	return courses


def get_program_credit_summary(program):
	"""Get credit summary for a program"""
	courses = get_program_courses(program)

	summary = {
		"total_credits": 0.0,
		"core_credits": 0.0,
		"elective_credits": 0.0,
		"mandatory_credits": 0.0,
		"optional_credits": 0.0,
	}

	for course in courses:
		credits = course.get("credits") or 0.0
		course_type = course.get("course_type") or ""
		required = course.get("required") or 0

		summary["total_credits"] += credits

		if course_type == "Core":
			summary["core_credits"] += credits
		elif course_type == "Elective":
			summary["elective_credits"] += credits

		if required:
			summary["mandatory_credits"] += credits
		else:
			summary["optional_credits"] += credits

	return summary
