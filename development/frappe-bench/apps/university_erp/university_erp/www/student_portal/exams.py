# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, get_datetime, date_diff, format_datetime


def get_context(context):
	"""Get examinations page context"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

	# Get current student
	user = frappe.session.user
	student = frappe.db.get_value("Student", {"user": user}, ["name", "student_name", "image", "custom_cgpa"], as_dict=1)

	if student:
		# Get program from Program Enrollment (active enrollment)
		program = frappe.db.get_value(
			"Program Enrollment",
			{"student": student.name, "docstatus": 1},
			"program",
			order_by="enrollment_date desc"
		)
		student.program = program

	if not student:
		frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

	context.no_cache = 1
	context.student = student
	context.active_page = "exams"

	# Get exam data
	context.upcoming_exams = get_upcoming_exams(student.name)
	context.completed_exams = get_completed_exams(student.name)
	context.hall_tickets = get_hall_tickets(student.name)

	# Calculate stats
	context.stats = {
		'upcoming': len(context.upcoming_exams),
		'completed': len(context.completed_exams),
		'hall_tickets': len([h for h in context.hall_tickets if h.get('is_eligible')]),
		'total': len(context.upcoming_exams) + len(context.completed_exams)
	}

	return context


def get_upcoming_exams(student):
	"""Get upcoming exams for the student"""
	try:
		today = nowdate()

		# Get student's enrolled courses through Student Group
		student_groups = frappe.db.get_all(
			"Student Group Student",
			filters={"student": student, "active": 1},
			pluck="parent"
		)

		if not student_groups:
			return []

		# Get upcoming exams from Exam Schedule
		# Note: Exam Schedule has exam_date, start_time, end_time, venue (not schedule_date, from_time, to_time, room)
		exams = frappe.db.sql("""
			SELECT
				es.name,
				es.course,
				es.academic_term,
				es.exam_type,
				es.exam_date as schedule_date,
				es.start_time as from_time,
				es.end_time as to_time,
				es.venue as room,
				es.max_students,
				c.course_name
			FROM `tabExam Schedule` es
			LEFT JOIN `tabCourse` c ON c.name = es.course
			WHERE es.docstatus = 1
			AND es.exam_date >= %(today)s
			ORDER BY es.exam_date, es.start_time
		""", {
			'today': today
		}, as_dict=1)

		# Filter by student's courses
		student_courses = []
		for sg in student_groups:
			sg_doc = frappe.get_doc("Student Group", sg)
			if hasattr(sg_doc, 'course') and sg_doc.course:
				student_courses.append(sg_doc.course)

		# Only include exams for courses the student is enrolled in
		if student_courses:
			exams = [e for e in exams if e.course in student_courses]

		# Add countdown info
		for exam in exams:
			exam.days_remaining = date_diff(exam.schedule_date, today)
			if exam.days_remaining == 0:
				exam.countdown_text = "Today"
			elif exam.days_remaining == 1:
				exam.countdown_text = "Tomorrow"
			else:
				exam.countdown_text = f"{exam.days_remaining} days"

		return exams

	except Exception as e:
		frappe.log_error(f"Error getting upcoming exams: {str(e)}")
		return []


def get_completed_exams(student):
	"""Get past/completed exams for the student"""
	try:
		today = nowdate()

		# Get student's enrolled courses
		student_groups = frappe.db.get_all(
			"Student Group Student",
			filters={"student": student, "active": 1},
			pluck="parent"
		)

		if not student_groups:
			return []

		# Get completed exams from Exam Schedule
		exams = frappe.db.sql("""
			SELECT
				es.name,
				es.course,
				es.academic_term,
				es.exam_type,
				es.exam_date as schedule_date,
				es.start_time as from_time,
				es.end_time as to_time,
				es.venue as room,
				c.course_name,
				ar.grade as obtained_grade,
				ar.total_score as obtained_marks
			FROM `tabExam Schedule` es
			LEFT JOIN `tabCourse` c ON c.name = es.course
			LEFT JOIN `tabAssessment Result` ar ON ar.course = es.course
				AND ar.student = %(student)s
			WHERE es.exam_date < %(today)s
			AND es.docstatus = 1
			ORDER BY es.exam_date DESC, es.start_time DESC
			LIMIT 20
		""", {
			'student': student,
			'today': today
		}, as_dict=1)

		# Filter by student's courses
		student_courses = []
		for sg in student_groups:
			sg_doc = frappe.get_doc("Student Group", sg)
			if hasattr(sg_doc, 'course') and sg_doc.course:
				student_courses.append(sg_doc.course)

		if student_courses:
			exams = [e for e in exams if e.course in student_courses]

		return exams

	except Exception as e:
		frappe.log_error(f"Error getting completed exams: {str(e)}")
		return []


def get_hall_tickets(student):
	"""Get hall tickets for the student"""
	try:
		# Check if Hall Ticket DocType exists
		if not frappe.db.exists("DocType", "Hall Ticket"):
			return []

		# Get hall tickets - using actual Hall Ticket fields
		tickets = frappe.db.sql("""
			SELECT
				ht.name,
				ht.student,
				ht.student_name,
				ht.enrollment_number,
				ht.academic_term,
				ht.exam_type,
				ht.issue_date,
				ht.verification_code,
				ht.is_eligible,
				ht.ineligibility_reason,
				at.term_name
			FROM `tabHall Ticket` ht
			LEFT JOIN `tabAcademic Term` at ON at.name = ht.academic_term
			WHERE ht.student = %(student)s
			AND ht.docstatus = 1
			ORDER BY ht.issue_date DESC
			LIMIT 20
		""", {'student': student}, as_dict=1)

		# Get exam details for each hall ticket
		for ticket in tickets:
			ticket.exams = get_hall_ticket_exams(ticket.name)

		return tickets

	except Exception as e:
		frappe.log_error(f"Error getting hall tickets: {str(e)}")
		return []


def get_hall_ticket_exams(hall_ticket):
	"""Get list of exams in a hall ticket"""
	try:
		# Check if Hall Ticket Exam child table exists
		if not frappe.db.exists("DocType", "Hall Ticket Exam"):
			return []

		# Query actual Hall Ticket Exam fields
		exams = frappe.db.sql("""
			SELECT
				hte.course,
				hte.course_name,
				hte.exam_date,
				hte.exam_time,
				hte.venue
			FROM `tabHall Ticket Exam` hte
			WHERE hte.parent = %(hall_ticket)s
			ORDER BY hte.exam_date, hte.exam_time
		""", {'hall_ticket': hall_ticket}, as_dict=1)

		return exams

	except Exception:
		return []


@frappe.whitelist()
def download_hall_ticket(hall_ticket_name):
	"""Download hall ticket as PDF"""
	try:
		# Check if user owns this hall ticket
		user = frappe.session.user
		student = frappe.db.get_value("Student", {"user": user}, ["name"], as_dict=1)
		if not student:
			frappe.throw(_("Not authorized"), frappe.PermissionError)

		# Validate ownership
		ticket_student = frappe.db.get_value("Hall Ticket", hall_ticket_name, "student")
		if ticket_student != student.name:
			frappe.throw(_("Not authorized to download this hall ticket"), frappe.PermissionError)

		# Generate PDF using print format with admin permissions (since we validated ownership)
		print_format = frappe.db.get_value("Property Setter", {
			"doc_type": "Hall Ticket",
			"property": "default_print_format"
		}, "value") or "Standard"

		# Temporarily elevate permissions for PDF generation
		frappe.set_user("Administrator")

		# Return PDF
		frappe.local.response.filename = f"Hall_Ticket_{hall_ticket_name}.pdf"
		frappe.local.response.filecontent = frappe.get_print(
			"Hall Ticket",
			hall_ticket_name,
			print_format,
			as_pdf=True,
			no_letterhead=0
		)
		frappe.local.response.type = "download"

		# Restore user
		frappe.set_user(user)

	except frappe.PermissionError:
		raise
	except Exception as e:
		frappe.log_error(f"Error downloading hall ticket: {str(e)}")
		frappe.throw(_("Failed to download hall ticket"))
