# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


class AttendanceManager:
	"""Manage student attendance"""

	def __init__(self):
		self.min_attendance_percentage = self.get_min_attendance_percentage()

	def get_min_attendance_percentage(self):
		"""Get minimum attendance percentage from settings"""
		return frappe.db.get_single_value(
			"University Settings",
			"min_attendance_percentage"
		) or 75.0

	def mark_attendance(self, course_schedule, attendance_data):
		"""Mark attendance for a course schedule"""
		created = []
		failed = []

		for student_data in attendance_data:
			try:
				attendance = frappe.new_doc("Student Attendance")
				attendance.student = student_data.get("student")
				attendance.course_schedule = course_schedule
				attendance.status = student_data.get("status", "Present")
				attendance.date = frappe.db.get_value("Course Schedule", course_schedule, "schedule_date")

				# Get course from schedule
				course = frappe.db.get_value("Course Schedule", course_schedule, "course")
				if course:
					attendance.course = course

				attendance.insert(ignore_permissions=True)
				created.append(attendance.name)

			except Exception as e:
				failed.append({
					"student": student_data.get("student"),
					"error": str(e)
				})

		frappe.db.commit()

		return {
			"created": len(created),
			"failed": len(failed),
			"attendance_records": created,
			"errors": failed
		}

	def get_attendance_percentage(self, student, course, academic_term=None):
		"""Calculate attendance percentage for a student in a course"""
		filters = {
			"student": student,
			"course": course
		}

		if academic_term:
			# Get schedules for this term
			schedules = frappe.get_all(
				"Course Schedule",
				filters={
					"course": course,
					"academic_term": academic_term
				},
				pluck="name"
			)
			if schedules:
				filters["course_schedule"] = ["in", schedules]

		# Total classes
		total = frappe.db.count("Student Attendance", filters)

		# Present classes
		filters["status"] = "Present"
		present = frappe.db.count("Student Attendance", filters)

		if total == 0:
			return 0.0

		percentage = (present / total) * 100
		return round(percentage, 2)

	def check_exam_eligibility(self, student, course, academic_term):
		"""Check if student meets minimum attendance for exams"""
		percentage = self.get_attendance_percentage(student, course, academic_term)

		eligible = percentage >= self.min_attendance_percentage

		return {
			"eligible": eligible,
			"attendance_percentage": percentage,
			"required_percentage": self.min_attendance_percentage,
			"shortage": max(0, self.min_attendance_percentage - percentage)
		}

	def get_shortage_students(self, course, academic_term, threshold=None):
		"""Get list of students with attendance below threshold"""
		if threshold is None:
			threshold = self.min_attendance_percentage

		# Get all students enrolled in this course
		enrollments = frappe.get_all(
			"Course Enrollment",
			filters={
				"course": course,
				"academic_term": academic_term
			},
			fields=["student", "student_name"]
		)

		shortage_students = []

		for enrollment in enrollments:
			percentage = self.get_attendance_percentage(
				enrollment.student,
				course,
				academic_term
			)

			if percentage < threshold:
				shortage_students.append({
					"student": enrollment.student,
					"student_name": enrollment.student_name,
					"attendance_percentage": percentage,
					"shortage": round(threshold - percentage, 2)
				})

		# Sort by shortage (highest first)
		shortage_students.sort(key=lambda x: x["shortage"], reverse=True)

		return shortage_students

	def get_student_attendance_summary(self, student, academic_term):
		"""Get attendance summary for all courses of a student"""
		# Get enrolled courses
		enrollments = frappe.get_all(
			"Course Enrollment",
			filters={
				"student": student,
				"academic_term": academic_term
			},
			fields=["course", "course_name"]
		)

		summary = []

		for enrollment in enrollments:
			percentage = self.get_attendance_percentage(
				student,
				enrollment.course,
				academic_term
			)

			eligibility = self.check_exam_eligibility(
				student,
				enrollment.course,
				academic_term
			)

			summary.append({
				"course": enrollment.course,
				"course_name": enrollment.course_name,
				"attendance_percentage": percentage,
				"eligible_for_exam": eligibility["eligible"],
				"shortage": eligibility["shortage"]
			})

		return summary


@frappe.whitelist()
def mark_attendance(course_schedule, attendance_data):
	"""API to mark attendance"""
	if isinstance(attendance_data, str):
		import json
		attendance_data = json.loads(attendance_data)

	manager = AttendanceManager()
	return manager.mark_attendance(course_schedule, attendance_data)


@frappe.whitelist()
def get_attendance_percentage(student, course, academic_term=None):
	"""API to get attendance percentage"""
	manager = AttendanceManager()
	return manager.get_attendance_percentage(student, course, academic_term)


@frappe.whitelist()
def check_exam_eligibility(student, course, academic_term):
	"""API to check exam eligibility"""
	manager = AttendanceManager()
	return manager.check_exam_eligibility(student, course, academic_term)


@frappe.whitelist()
def get_shortage_students(course, academic_term, threshold=None):
	"""API to get students with attendance shortage"""
	manager = AttendanceManager()
	if threshold:
		threshold = flt(threshold)
	return manager.get_shortage_students(course, academic_term, threshold)


@frappe.whitelist()
def get_student_attendance_summary(student, academic_term):
	"""API to get student attendance summary"""
	manager = AttendanceManager()
	return manager.get_student_attendance_summary(student, academic_term)
