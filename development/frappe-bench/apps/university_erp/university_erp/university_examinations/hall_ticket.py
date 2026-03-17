# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today
import hashlib


class HallTicketGenerator:
	"""Generate hall tickets for students"""

	def __init__(self, academic_term, exam_type="Regular"):
		self.academic_term = academic_term
		self.exam_type = exam_type

	def generate_for_student(self, student):
		"""Generate hall ticket for a single student"""
		# Check if hall ticket already exists
		existing = frappe.db.exists(
			"Hall Ticket",
			{
				"student": student,
				"academic_term": self.academic_term,
				"exam_type": self.exam_type,
				"docstatus": ["<", 2]
			}
		)

		if existing:
			return existing

		# Get enrolled courses
		enrolled_courses = self.get_student_courses(student)

		if not enrolled_courses:
			frappe.msgprint(f"No courses found for student {student}")
			return None

		# Create hall ticket
		hall_ticket = frappe.new_doc("Hall Ticket")
		hall_ticket.student = student
		hall_ticket.academic_term = self.academic_term
		hall_ticket.exam_type = self.exam_type
		hall_ticket.issue_date = today()

		# Add exam schedules
		for course in enrolled_courses:
			exam_schedule = self.get_exam_schedule(course.course)
			if exam_schedule:
				hall_ticket.append("exams", {
					"course": course.course,
					"course_name": course.course_name,
					"exam_date": exam_schedule.exam_date,
					"exam_time": exam_schedule.start_time,
					"venue": exam_schedule.venue
				})

		if not hall_ticket.exams:
			frappe.msgprint(f"No exam schedules found for student {student}")
			return None

		hall_ticket.insert(ignore_permissions=True)
		hall_ticket.submit()

		return hall_ticket.name

	def generate_bulk(self, program):
		"""Generate hall tickets for all students in a program"""
		students = frappe.get_all(
			"Student",
			filters={"custom_program": program, "custom_student_status": "Active"},
			pluck="name"
		)

		generated = []
		failed = []

		for student in students:
			try:
				ticket = self.generate_for_student(student)
				if ticket:
					generated.append(ticket)
			except Exception as e:
				failed.append({"student": student, "error": str(e)})
				frappe.log_error(f"Hall ticket generation failed for {student}: {str(e)}")

		return {
			"generated": len(generated),
			"failed": len(failed),
			"hall_tickets": generated,
			"errors": failed
		}

	def generate_for_group(self, student_group):
		"""Generate hall tickets for student group"""
		group_doc = frappe.get_doc("Student Group", student_group)
		students = [student.student for student in group_doc.students]

		generated = []
		failed = []

		for student in students:
			try:
				ticket = self.generate_for_student(student)
				if ticket:
					generated.append(ticket)
			except Exception as e:
				failed.append({"student": student, "error": str(e)})

		return {
			"generated": len(generated),
			"failed": len(failed),
			"hall_tickets": generated,
			"errors": failed
		}

	def get_student_courses(self, student):
		"""Get courses student is enrolled in"""
		return frappe.get_all(
			"Course Enrollment",
			filters={
				"student": student,
				"academic_term": self.academic_term
			},
			fields=["course", "course_name"]
		)

	def get_exam_schedule(self, course):
		"""Get exam schedule for a course"""
		schedule = frappe.db.get_value(
			"Exam Schedule",
			{
				"course": course,
				"academic_term": self.academic_term,
				"exam_type": self.exam_type
			},
			["exam_date", "start_time", "venue"],
			as_dict=True
		)
		return schedule


@frappe.whitelist()
def generate_hall_ticket(student, academic_term, exam_type="Regular"):
	"""API to generate single hall ticket"""
	generator = HallTicketGenerator(academic_term, exam_type)
	return generator.generate_for_student(student)


@frappe.whitelist()
def bulk_generate_hall_tickets(program, academic_term, exam_type="Regular"):
	"""API to bulk generate hall tickets"""
	generator = HallTicketGenerator(academic_term, exam_type)
	return generator.generate_bulk(program)


@frappe.whitelist()
def generate_hall_tickets_for_group(student_group, academic_term, exam_type="Regular"):
	"""API to generate hall tickets for group"""
	generator = HallTicketGenerator(academic_term, exam_type)
	return generator.generate_for_group(student_group)


@frappe.whitelist()
def verify_hall_ticket(verification_code):
	"""API to verify hall ticket"""
	hall_ticket = frappe.db.get_value(
		"Hall Ticket",
		{"verification_code": verification_code, "docstatus": 1},
		["name", "student", "student_name", "enrollment_number", "is_eligible"],
		as_dict=True
	)

	if hall_ticket:
		return {
			"valid": True,
			"hall_ticket": hall_ticket
		}
	else:
		return {
			"valid": False,
			"message": "Invalid verification code"
		}
