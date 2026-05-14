# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


import json

import frappe
from frappe import _
from frappe.model.document import Document


class Course(Document):
	def validate(self):
		self.validate_assessment_criteria()
		# University-specific validations (absorbed from former UniversityCourse override)
		self.validate_course_code()
		self.calculate_credits()
		self.validate_assessment_weightage()

	def validate_assessment_criteria(self):
		if self.assessment_criteria:
			total_weightage = 0
			for criteria in self.assessment_criteria:
				total_weightage += criteria.weightage or 0
			if total_weightage != 100:
				frappe.throw(_("Total Weightage of all Assessment Criteria must be 100%"))

	def get_topics(self):
		topic_data = []
		for topic in self.topics:
			topic_doc = frappe.get_doc("Topic", topic.topic)
			if topic_doc.topic_content:
				topic_data.append(topic_doc)
		return topic_data

	# =========================================================================
	# University-specific methods (absorbed from former UniversityCourse override)
	# =========================================================================

	def validate_course_code(self):
		"""Validate that course code is unique"""
		if not self.get("custom_course_code"):
			return

		existing = frappe.db.exists(
			"Course",
			{"custom_course_code": self.custom_course_code, "name": ("!=", self.name)},
		)

		if existing:
			frappe.throw(
				_("Course Code {0} already exists").format(self.custom_course_code)
			)

	def calculate_credits(self):
		"""
		Calculate credits based on L-T-P formula:
		Credits = L + T + (P/2) + Self Study Credits
		"""
		lecture = self.get("custom_lecture_hours") or 0
		tutorial = self.get("custom_tutorial_hours") or 0
		practical = self.get("custom_practical_hours") or 0
		self_study = self.get("custom_self_study_credits") or 0

		credits = lecture + tutorial + (practical / 2) + self_study
		self.custom_credits = credits

		if credits > 10:
			frappe.msgprint(
				_("Course credits ({0}) seems unusually high").format(credits),
				alert=True,
				indicator="orange",
			)

	def validate_assessment_weightage(self):
		"""Validate that assessment weightages sum to 100%"""
		internal = self.get("custom_internal_weightage") or 0
		external = self.get("custom_external_weightage") or 0
		practical = self.get("custom_practical_weightage") or 0

		total = internal + external + practical

		if abs(total - 100) > 0.01 and total > 0:
			frappe.throw(
				_("Total assessment weightage must be 100%. Current total: {0}%").format(total)
			)

		if internal < 20 and self.get("custom_course_type") in ["Core", "Elective"]:
			frappe.msgprint(
				_("Internal weightage ({0}%) is less than recommended minimum of 20%").format(
					internal
				),
				alert=True,
				indicator="orange",
			)


@frappe.whitelist()
def add_course_to_programs(course, programs, mandatory=False):
	programs = json.loads(programs)
	for entry in programs:
		program = frappe.get_doc("Program", entry)
		program.append(
			"courses", {"course": course, "course_name": course, "mandatory": mandatory}
		)
		program.flags.ignore_mandatory = True
		program.save()
	frappe.msgprint(
		_("Course {0} has been added to all the selected programs successfully.").format(
			frappe.bold(course)
		),
		title=_("Programs updated"),
		indicator="green",
	)


@frappe.whitelist()
def get_programs_without_course(course):
	data = []
	for entry in frappe.db.get_all("Program"):
		program = frappe.get_doc("Program", entry.name)
		courses = [c.course for c in program.courses]
		if not courses or course not in courses:
			data.append(program.name)
	return data


# =============================================================================
# Module-level helpers (absorbed from former university_erp.overrides.course)
# =============================================================================


def get_course_details(course):
	"""Get detailed information about a course"""
	if not course:
		return {}

	course_doc = frappe.get_doc("Course", course)

	return {
		"course_name": course_doc.course_name,
		"course_code": course_doc.get("custom_course_code"),
		"credits": course_doc.get("custom_credits"),
		"course_type": course_doc.get("custom_course_type"),
		"department": course_doc.get("custom_department"),
		"lecture_hours": course_doc.get("custom_lecture_hours"),
		"tutorial_hours": course_doc.get("custom_tutorial_hours"),
		"practical_hours": course_doc.get("custom_practical_hours"),
		"self_study_credits": course_doc.get("custom_self_study_credits"),
		"internal_weightage": course_doc.get("custom_internal_weightage"),
		"external_weightage": course_doc.get("custom_external_weightage"),
		"practical_weightage": course_doc.get("custom_practical_weightage"),
	}


def get_ltp_format(course):
	"""Get L-T-P format string for a course"""
	if not course:
		return ""

	course_doc = frappe.get_doc("Course", course)

	lecture = course_doc.get("custom_lecture_hours") or 0
	tutorial = course_doc.get("custom_tutorial_hours") or 0
	practical = course_doc.get("custom_practical_hours") or 0

	return f"{lecture}-{tutorial}-{practical}"


def calculate_contact_hours(course):
	"""Calculate total contact hours per week for a course"""
	if not course:
		return 0

	course_doc = frappe.get_doc("Course", course)

	lecture = course_doc.get("custom_lecture_hours") or 0
	tutorial = course_doc.get("custom_tutorial_hours") or 0
	practical = course_doc.get("custom_practical_hours") or 0

	return lecture + tutorial + practical
