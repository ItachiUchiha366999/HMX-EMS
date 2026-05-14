# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils.csvutils import getlink

class StudentNotInGroupError(frappe.ValidationError):
	pass


# Forked inline from education.education.api (Phase 03.3.1 Plan 06).
# Original location: frappe-bench/apps/education/education/education/api.py
@frappe.whitelist()
def get_assessment_details(assessment_plan):
	"""Returns Assessment Criteria and Maximum Score from Assessment Plan Master."""
	return frappe.get_all(
		"Assessment Plan Criteria",
		fields=["assessment_criteria", "maximum_score", "docstatus"],
		filters={"parent": assessment_plan},
		order_by="idx",
	)


@frappe.whitelist()
def get_grade(grading_scale, percentage):
	"""Returns Grade based on the Grading Scale and Score."""
	grading_scale_intervals = {}
	if not hasattr(frappe.local, "grading_scale"):
		grading_scale_rows = frappe.get_all(
			"Grading Scale Interval",
			fields=["grade_code", "threshold"],
			filters={"parent": grading_scale},
		)
		frappe.local.grading_scale = grading_scale_rows
	for d in frappe.local.grading_scale:
		grading_scale_intervals.update({d.threshold: d.grade_code})
	intervals = sorted(grading_scale_intervals.keys(), key=float, reverse=True)
	grade = ""
	for interval in intervals:
		if flt(percentage) >= interval:
			grade = grading_scale_intervals.get(interval)
			break
	return grade


def validate_student_belongs_to_group(student, student_group):
	"""Forked from education.education.validate_student_belongs_to_group.

	Verifies that the given student is an active member of the specified
	student group. Throws StudentNotInGroupError otherwise.
	"""
	groups = frappe.db.get_all(
		"Student Group Student", ["parent"], dict(student=student, active=1)
	)
	if student_group not in [d.parent for d in groups]:
		frappe.throw(
			_("Student {0} does not belong to group {1}").format(
				frappe.bold(student), frappe.bold(student_group)
			),
			StudentNotInGroupError,
		)


class AssessmentResult(Document):
	def validate(self):
		validate_student_belongs_to_group(self.student, self.student_group)
		self.validate_maximum_score()
		self.validate_grade()
		self.validate_duplicate()

		# University-specific validations (absorbed from former UniversityAssessmentResult override)
		self.calculate_percentage()
		self.calculate_grade_points()
		self.calculate_credit_points()
		self.validate_absence()

	def validate_maximum_score(self):
		assessment_details = get_assessment_details(self.assessment_plan)
		max_scores = {}
		for d in assessment_details:
			max_scores.update({d.assessment_criteria: d.maximum_score})

		for d in self.details:
			d.maximum_score = max_scores.get(d.assessment_criteria)
			if d.score > d.maximum_score:
				frappe.throw(_("Score cannot be greater than Maximum Score"))

	def validate_grade(self):
		self.total_score = 0.0
		for d in self.details:
			d.grade = get_grade(self.grading_scale, (flt(d.score) / d.maximum_score) * 100)
			self.total_score += d.score
		self.grade = get_grade(
			self.grading_scale, (self.total_score / self.maximum_score) * 100
		)

	def validate_duplicate(self):
		assessment_result = frappe.get_list(
			"Assessment Result",
			filters={
				"name": ("not in", [self.name]),
				"student": self.student,
				"assessment_plan": self.assessment_plan,
				"docstatus": ("!=", 2),
			},
		)
		if assessment_result:
			frappe.throw(
				_("Assessment Result record {0} already exists.").format(
					getlink("Assessment Result", assessment_result[0].name)
				)
			)

	# =========================================================================
	# University-specific methods (absorbed from former UniversityAssessmentResult override)
	# =========================================================================

	def calculate_percentage(self):
		"""Calculate percentage from total_score and maximum_score"""
		if not self.total_score or not self.maximum_score:
			self.custom_percentage = 0.0
			return

		self.custom_percentage = (self.total_score / self.maximum_score) * 100

	def calculate_grade_points(self):
		"""Calculate grade points on 10-point scale (O=10 ... F=0)."""
		if self.get("custom_is_absent"):
			self.custom_grade_points = 0.0
			self.grade = "AB"
			return

		percentage = self.get("custom_percentage") or 0.0

		if percentage >= 90:
			self.custom_grade_points = 10.0
			self.grade = "O"
		elif percentage >= 80:
			self.custom_grade_points = 9.0
			self.grade = "A+"
		elif percentage >= 70:
			self.custom_grade_points = 8.0
			self.grade = "A"
		elif percentage >= 60:
			self.custom_grade_points = 7.0
			self.grade = "B+"
		elif percentage >= 55:
			self.custom_grade_points = 6.0
			self.grade = "B"
		elif percentage >= 50:
			self.custom_grade_points = 5.0
			self.grade = "C"
		elif percentage >= 45:
			self.custom_grade_points = 4.0
			self.grade = "P"
		else:
			self.custom_grade_points = 0.0
			self.grade = "F"

	def calculate_credit_points(self):
		"""Calculate credit points: Grade Points x Course Credits."""
		if not self.course:
			self.custom_credit_points = 0.0
			return

		course = frappe.get_doc("Course", self.course)
		credits = course.get("custom_credits") or 0.0

		self.custom_credits = credits
		self.custom_credit_points = (self.get("custom_grade_points") or 0.0) * credits

	def validate_absence(self):
		"""Handle absence cases"""
		if self.get("custom_is_absent"):
			self.custom_grade_points = 0.0
			self.custom_credit_points = 0.0
			self.grade = "AB"

			frappe.msgprint(
				_("Student marked as absent. Grade: AB, Grade Points: 0"),
				alert=True,
				indicator="red",
			)


# =============================================================================
# Module-level helpers (absorbed from former university_erp.overrides.assessment_result)
# =============================================================================


def calculate_sgpa(student, academic_term):
	"""Calculate Semester Grade Point Average (SGPA) for a student in a term."""
	if not student or not academic_term:
		return 0.0

	results = frappe.get_all(
		"Assessment Result",
		filters={
			"student": student,
			"academic_term": academic_term,
			"docstatus": 1,
			"custom_is_absent": 0,
		},
		fields=["custom_grade_points", "custom_credits"],
	)

	if not results:
		return 0.0

	total_credit_points = sum(r.custom_grade_points * r.custom_credits for r in results)
	total_credits = sum(r.custom_credits for r in results)

	if total_credits > 0:
		return round(total_credit_points / total_credits, 2)

	return 0.0


def calculate_cgpa(student):
	"""Calculate Cumulative Grade Point Average (CGPA) for a student."""
	if not student:
		return 0.0

	results = frappe.get_all(
		"Assessment Result",
		filters={"student": student, "docstatus": 1, "custom_is_absent": 0},
		fields=["custom_grade_points", "custom_credits"],
	)

	if not results:
		return 0.0

	total_credit_points = sum(r.custom_grade_points * r.custom_credits for r in results)
	total_credits = sum(r.custom_credits for r in results)

	if total_credits > 0:
		return round(total_credit_points / total_credits, 2)

	return 0.0


def get_grade_description(grade):
	"""Get description for a grade"""
	descriptions = {
		"O": "Outstanding",
		"A+": "Excellent",
		"A": "Very Good",
		"B+": "Good",
		"B": "Above Average",
		"C": "Average",
		"P": "Pass",
		"F": "Fail",
		"AB": "Absent",
	}
	return descriptions.get(grade, "")


def get_student_grade_sheet(student, academic_year=None):
	"""Get complete grade sheet for a student"""
	filters = {"student": student, "docstatus": 1}

	if academic_year:
		filters["academic_year"] = academic_year

	results = frappe.get_all(
		"Assessment Result",
		filters=filters,
		fields=[
			"name",
			"course",
			"academic_term",
			"academic_year",
			"custom_percentage",
			"grade",
			"custom_grade_points",
			"custom_credits",
			"custom_credit_points",
			"custom_is_absent",
		],
		order_by="academic_year desc, academic_term",
	)

	grade_sheet = {}
	for result in results:
		term = result.academic_term
		if term not in grade_sheet:
			grade_sheet[term] = {"results": [], "sgpa": 0.0, "credits": 0.0}

		grade_sheet[term]["results"].append(result)

	for term, data in grade_sheet.items():
		total_credit_points = sum(
			r.custom_credit_points for r in data["results"] if not r.custom_is_absent
		)
		total_credits = sum(
			r.custom_credits for r in data["results"] if not r.custom_is_absent
		)

		if total_credits > 0:
			data["sgpa"] = round(total_credit_points / total_credits, 2)
		data["credits"] = total_credits

	return grade_sheet
