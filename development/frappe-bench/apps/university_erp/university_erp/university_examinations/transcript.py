# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


class TranscriptGenerator:
	"""Generate academic transcripts for students"""

	DEGREE_CLASSIFICATIONS = [
		{"min_cgpa": 9.0, "classification": "First Class with Distinction"},
		{"min_cgpa": 7.5, "classification": "First Class"},
		{"min_cgpa": 6.0, "classification": "Second Class"},
		{"min_cgpa": 4.0, "classification": "Pass"},
		{"min_cgpa": 0.0, "classification": "Incomplete"}
	]

	def __init__(self, student):
		self.student = student
		self.student_doc = frappe.get_doc("Student", student)

	def generate(self, transcript_type="Provisional", purpose="Higher Studies"):
		"""Generate transcript"""
		# Check if transcript already exists
		existing = frappe.db.exists(
			"Student Transcript",
			{
				"student": self.student,
				"transcript_type": transcript_type,
				"docstatus": 1
			}
		)

		if existing and transcript_type != "Duplicate":
			return existing

		# Create transcript
		transcript = frappe.new_doc("Student Transcript")
		transcript.student = self.student
		transcript.transcript_type = transcript_type
		transcript.purpose = purpose

		# Get semester results
		semester_results = self.get_semester_results()

		for sem_result in semester_results:
			transcript.append("semester_results", sem_result)

		# Calculate totals
		total_credits = sum([sem.credits_earned for sem in semester_results])
		final_cgpa = semester_results[-1].cgpa if semester_results else 0.0

		transcript.total_credits_earned = total_credits
		transcript.cgpa = final_cgpa
		transcript.degree_classification = self.get_degree_classification(final_cgpa)

		transcript.insert(ignore_permissions=True)
		transcript.submit()

		return transcript.name

	def get_semester_results(self):
		"""Get semester-wise results for student"""
		# Get all academic terms student was enrolled in
		enrollments = frappe.get_all(
			"Course Enrollment",
			filters={"student": self.student},
			fields=["academic_term"],
			distinct=True,
			order_by="academic_term"
		)

		semester_results = []

		for idx, enrollment in enumerate(enrollments, 1):
			academic_term = enrollment.academic_term

			# Get results for this term
			results = frappe.get_all(
				"Assessment Result",
				filters={
					"student": self.student,
					"custom_academic_term": academic_term,
					"docstatus": 1
				},
				fields=["custom_credits", "custom_grade_points"]
			)

			if not results:
				continue

			# Calculate SGPA
			total_credit_points = 0.0
			total_credits = 0.0

			for result in results:
				credits = flt(result.custom_credits)
				grade_points = flt(result.custom_grade_points)
				total_credit_points += credits * grade_points
				total_credits += credits

			sgpa = (total_credit_points / total_credits) if total_credits > 0 else 0.0

			# Calculate cumulative CGPA
			all_results_so_far = frappe.get_all(
				"Assessment Result",
				filters={
					"student": self.student,
					"docstatus": 1,
					"custom_academic_term": ["<=", academic_term]
				},
				fields=["custom_credits", "custom_grade_points"]
			)

			total_cumulative_cp = 0.0
			total_cumulative_credits = 0.0

			for result in all_results_so_far:
				credits = flt(result.custom_credits)
				grade_points = flt(result.custom_grade_points)
				total_cumulative_cp += credits * grade_points
				total_cumulative_credits += credits

			cgpa = (total_cumulative_cp / total_cumulative_credits) if total_cumulative_credits > 0 else 0.0

			semester_results.append({
				"semester": idx,
				"academic_term": academic_term,
				"credits_earned": round(total_credits, 1),
				"sgpa": round(sgpa, 2),
				"cgpa": round(cgpa, 2)
			})

		return semester_results

	def get_degree_classification(self, cgpa):
		"""Get degree classification based on CGPA"""
		for classification in self.DEGREE_CLASSIFICATIONS:
			if cgpa >= classification["min_cgpa"]:
				return classification["classification"]
		return "Incomplete"

	def get_academic_summary(self):
		"""Get complete academic summary"""
		return {
			"student": self.student,
			"student_name": self.student_doc.student_name,
			"enrollment_number": self.student_doc.custom_enrollment_number,
			"program": self.student_doc.custom_program,
			"semester_results": self.get_semester_results()
		}


@frappe.whitelist()
def generate_transcript(student, transcript_type="Provisional", purpose="Higher Studies"):
	"""API to generate transcript"""
	generator = TranscriptGenerator(student)
	return generator.generate(transcript_type, purpose)


@frappe.whitelist()
def get_student_academic_summary(student):
	"""API to get academic summary"""
	generator = TranscriptGenerator(student)
	return generator.get_academic_summary()


@frappe.whitelist()
def get_semester_results(student, academic_term=None):
	"""API to get semester results"""
	generator = TranscriptGenerator(student)

	if academic_term:
		# Get specific semester
		all_results = generator.get_semester_results()
		for result in all_results:
			if result.get("academic_term") == academic_term:
				return result
		return None
	else:
		# Get all semesters
		return generator.get_semester_results()


@frappe.whitelist()
def verify_transcript(transcript_number):
	"""API to verify transcript"""
	transcript = frappe.db.get_value(
		"Student Transcript",
		{"name": transcript_number, "docstatus": 1},
		[
			"name", "student", "student_name", "enrollment_number",
			"cgpa", "degree_classification", "verification_code"
		],
		as_dict=True
	)

	if transcript:
		return {
			"valid": True,
			"transcript": transcript
		}
	else:
		return {
			"valid": False,
			"message": "Invalid transcript number"
		}
