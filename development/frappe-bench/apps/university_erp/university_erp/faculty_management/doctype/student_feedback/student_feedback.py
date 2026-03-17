# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class StudentFeedback(Document):
	def validate(self):
		"""Validate feedback before submission"""
		self.validate_ratings()

	def validate_ratings(self):
		"""Ensure all ratings are within 1-5"""
		ratings = [
			self.subject_knowledge,
			self.teaching_methodology,
			self.communication_skills,
			self.availability,
			self.course_coverage,
			self.overall_rating
		]
		for rating in ratings:
			if rating and (rating < 1 or rating > 5):
				frappe.throw(_("All ratings must be between 1 and 5"))


@frappe.whitelist()
def get_pending_feedback(student, academic_term):
	"""Get list of courses for which student hasn't submitted feedback"""
	# Get all enrolled courses
	enrolled_courses = frappe.db.sql("""
		SELECT DISTINCT pe.course, pe.instructor, c.course_name
		FROM `tabProgram Enrollment` pe
		LEFT JOIN `tabCourse` c ON pe.course = c.name
		WHERE pe.student = %s
			AND pe.academic_term = %s
			AND pe.docstatus = 1
	""", (student, academic_term), as_dict=True)

	# Get courses with existing feedback
	existing_feedback = frappe.db.sql("""
		SELECT course, instructor
		FROM `tabStudent Feedback`
		WHERE student = %s
			AND academic_term = %s
			AND docstatus = 1
	""", (student, academic_term), as_dict=True)

	feedback_set = {(f.course, f.instructor) for f in existing_feedback}
	pending = [c for c in enrolled_courses if (c.course, c.instructor) not in feedback_set]

	return pending


@frappe.whitelist()
def get_feedback_summary(instructor, academic_year=None):
	"""Get feedback summary for an instructor"""
	filters = {"instructor": instructor, "docstatus": 1}
	if academic_year:
		filters["academic_year"] = academic_year

	feedbacks = frappe.get_all(
		"Student Feedback",
		filters=filters,
		fields=[
			"subject_knowledge", "teaching_methodology", "communication_skills",
			"availability", "course_coverage", "overall_rating", "course"
		]
	)

	if not feedbacks:
		return {
			"count": 0,
			"averages": {}
		}

	# Calculate averages
	total = len(feedbacks)
	averages = {
		"subject_knowledge": sum([f.subject_knowledge for f in feedbacks]) / total,
		"teaching_methodology": sum([f.teaching_methodology for f in feedbacks]) / total,
		"communication_skills": sum([f.communication_skills for f in feedbacks]) / total,
		"availability": sum([f.availability for f in feedbacks]) / total,
		"course_coverage": sum([f.course_coverage for f in feedbacks]) / total,
		"overall_rating": sum([f.overall_rating for f in feedbacks]) / total
	}

	return {
		"count": total,
		"averages": averages,
		"feedbacks": feedbacks
	}
