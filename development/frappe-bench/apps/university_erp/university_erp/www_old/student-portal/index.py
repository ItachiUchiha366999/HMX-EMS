# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
	"""Student portal main page context"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to access the portal"), frappe.AuthenticationError)

	student = get_student_for_user()
	if not student:
		frappe.throw(_("No student record found for this user"))

	student_doc = frappe.get_doc("Student", student)

	context.no_cache = 1
	context.student = student_doc
	context.current_semester = get_current_semester(student)
	context.enrolled_courses = get_enrolled_courses(student)
	context.attendance_summary = get_attendance_summary(student)
	context.fee_status = get_fee_status(student)
	context.recent_results = get_recent_results(student)
	context.announcements = get_announcements(student_doc.custom_program)
	context.upcoming_events = get_upcoming_events(student)


def get_student_for_user():
	"""Get student linked to current user"""
	return frappe.db.get_value("Student", {"user": frappe.session.user})


def get_current_semester(student):
	"""Get current academic term"""
	return frappe.db.get_value(
		"Academic Term",
		{
			"term_start_date": ["<=", frappe.utils.today()],
			"term_end_date": [">=", frappe.utils.today()]
		}
	) or "N/A"


def get_enrolled_courses(student):
	"""Get courses student is enrolled in"""
	current_term = get_current_semester(student)
	if current_term == "N/A":
		return []

	return frappe.get_all(
		"Course Enrollment",
		filters={"student": student, "academic_term": current_term},
		fields=["course", "course_name", "enrollment_date"]
	)


def get_attendance_summary(student):
	"""Get attendance percentage for current semester"""
	courses = get_enrolled_courses(student)
	summary = []

	for course in courses:
		# Get attendance count
		total = frappe.db.count(
			"Student Attendance",
			{
				"student": student,
				"course_schedule": ["like", f"%{course.course}%"]
			}
		)

		present = frappe.db.count(
			"Student Attendance",
			{
				"student": student,
				"course_schedule": ["like", f"%{course.course}%"],
				"status": "Present"
			}
		)

		percentage = (present / total * 100) if total > 0 else 0

		summary.append({
			"course": course.course_name,
			"percentage": round(percentage, 1),
			"status": "Good" if percentage >= 75 else "Low"
		})

	return summary


def get_fee_status(student):
	"""Get pending fees"""
	return frappe.get_all(
		"Fees",
		filters={"student": student, "outstanding_amount": [">", 0]},
		fields=["name", "fee_structure", "grand_total", "outstanding_amount", "due_date"],
		order_by="due_date asc"
	)


def get_recent_results(student):
	"""Get recent assessment results"""
	return frappe.get_all(
		"Assessment Result",
		filters={"student": student, "docstatus": 1},
		fields=[
			"course", "custom_grade", "custom_grade_points",
			"custom_credits", "custom_result_status"
		],
		order_by="creation desc",
		limit=10
	)


def get_announcements(program):
	"""Get relevant announcements"""
	return frappe.get_all(
		"University Announcement",
		filters={
			"publish_date": ["<=", frappe.utils.today()],
			"target_audience": ["in", ["All", "Students", "Program Specific"]]
		},
		fields=["title", "content", "publish_date", "priority"],
		order_by="publish_date desc",
		limit=5
	)


def get_upcoming_events(student):
	"""Get upcoming events for student"""
	# This will be implemented in later phases when Event DocType is created
	return []


@frappe.whitelist()
def get_student_dashboard_data():
	"""API to get dashboard data for current student"""
	student = get_student_for_user()
	if not student:
		frappe.throw("No student record found")

	student_doc = frappe.get_doc("Student", student)

	return {
		"student": {
			"name": student_doc.name,
			"student_name": student_doc.student_name,
			"enrollment_number": student_doc.custom_enrollment_number,
			"program": student_doc.custom_program,
			"cgpa": student_doc.custom_cgpa,
			"total_credits": student_doc.custom_total_credits_earned or 0,
			"status": student_doc.custom_student_status
		},
		"current_semester": get_current_semester(student),
		"enrolled_courses": get_enrolled_courses(student),
		"attendance": get_attendance_summary(student),
		"fees": get_fee_status(student),
		"results": get_recent_results(student),
		"announcements": get_announcements(student_doc.custom_program)
	}
