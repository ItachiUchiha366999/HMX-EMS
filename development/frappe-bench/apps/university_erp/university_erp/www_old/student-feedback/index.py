# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
	"""Get context for student feedback portal page"""

	# Check if user is logged in
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to submit feedback"), frappe.PermissionError)

	# Get student linked to this user
	student = frappe.db.get_value(
		"Student",
		{"user": frappe.session.user},
		["name", "student_name", "program", "student_batch_name"],
		as_dict=True
	)

	if not student:
		frappe.throw(_("You are not authorized to access Student Feedback Portal"), frappe.PermissionError)

	context.student = student

	# Get enrolled courses for current term
	enrolled_courses = get_enrolled_courses(student.name)
	context.enrolled_courses = enrolled_courses

	# Get submitted feedbacks
	submitted_feedbacks = frappe.get_all(
		"Student Feedback",
		filters={
			"student": student.name
		},
		fields=[
			"name",
			"faculty",
			"faculty_name",
			"course",
			"course_name",
			"overall_rating",
			"creation",
			"docstatus"
		],
		order_by="creation desc"
	)
	context.submitted_feedbacks = submitted_feedbacks

	# Check which courses have pending feedback
	pending_feedback = []
	for course in enrolled_courses:
		# Check if feedback already submitted for this faculty-course combination
		existing = frappe.db.exists(
			"Student Feedback",
			{
				"student": student.name,
				"faculty": course.instructor,
				"course": course.course,
				"docstatus": 1
			}
		)
		if not existing:
			pending_feedback.append(course)

	context.pending_feedback = pending_feedback

	# Page metadata
	context.title = _("Student Feedback Portal")
	context.show_sidebar = False
	context.no_cache = 1

	return context


def get_enrolled_courses(student):
	"""Get courses student is enrolled in for current term"""

	# Get student's current program enrollment
	program_enrollment = frappe.db.get_value(
		"Program Enrollment",
		{
			"student": student,
			"docstatus": 1,
			"enabled": 1
		},
		["name", "program", "academic_year", "academic_term"],
		as_dict=True,
		order_by="creation desc"
	)

	if not program_enrollment:
		return []

	# Get teaching assignments for student's courses
	courses = frappe.db.sql("""
		SELECT DISTINCT
			ta.name,
			ta.course,
			ta.course_name,
			ta.instructor,
			e.employee_name as instructor_name,
			ta.program,
			ta.academic_year,
			ta.academic_term
		FROM `tabTeaching Assignment` ta
		INNER JOIN `tabEmployee` e ON ta.instructor = e.name
		WHERE ta.program = %(program)s
			AND ta.academic_year = %(academic_year)s
			AND ta.academic_term = %(academic_term)s
			AND ta.docstatus = 1
		ORDER BY ta.course_name
	""", {
		"program": program_enrollment.program,
		"academic_year": program_enrollment.academic_year,
		"academic_term": program_enrollment.academic_term
	}, as_dict=True)

	return courses
