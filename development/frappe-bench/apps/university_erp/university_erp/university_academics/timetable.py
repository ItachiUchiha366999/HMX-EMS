# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate


class TimetableGenerator:
	"""Generate and manage timetables"""

	DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

	def __init__(self, academic_term):
		self.academic_term = academic_term

	def get_timetable(self, entity_type, entity_name):
		"""Get timetable for student group, instructor, or room"""
		filters = {
			"academic_term": self.academic_term
		}

		if entity_type == "Student Group":
			filters["student_group"] = entity_name
		elif entity_type == "Instructor":
			filters["instructor"] = entity_name
		elif entity_type == "Room":
			filters["room"] = entity_name

		schedules = frappe.get_all(
			"Course Schedule",
			filters=filters,
			fields=[
				"name", "course", "course_name", "instructor", "instructor_name",
				"student_group", "room", "schedule_date", "from_time", "to_time"
			],
			order_by="schedule_date, from_time"
		)

		# Organize by day and time
		timetable = {day: [] for day in self.DAYS}

		for schedule in schedules:
			if schedule.schedule_date:
				day = getdate(schedule.schedule_date).strftime("%A")
				if day in timetable:
					timetable[day].append(schedule)

		return timetable

	def create_schedule(self, course, student_group, instructor, day, slot_name, room):
		"""Create a schedule entry"""
		# Get slot details
		slot = frappe.get_doc("Timetable Slot", slot_name)

		# Check for conflicts
		conflicts = self.check_conflicts(instructor, room, student_group, day, slot)
		if conflicts:
			frappe.throw(f"Scheduling conflict: {', '.join(conflicts)}")

		# Get academic term dates
		term = frappe.get_doc("Academic Term", self.academic_term)

		# Create Course Schedule
		schedule = frappe.new_doc("Course Schedule")
		schedule.student_group = student_group
		schedule.course = course
		schedule.instructor = instructor
		schedule.room = room
		schedule.schedule_date = self.get_next_day_date(day, term.term_start_date)
		schedule.from_time = slot.start_time
		schedule.to_time = slot.end_time
		schedule.academic_term = self.academic_term

		schedule.insert()

		return schedule.name

	def check_conflicts(self, instructor, room, student_group, day, slot):
		"""Check for scheduling conflicts"""
		conflicts = []

		# Get date for the day
		term = frappe.get_doc("Academic Term", self.academic_term)
		target_date = self.get_next_day_date(day, term.term_start_date)

		# Check instructor conflict
		if instructor:
			instructor_schedules = frappe.get_all(
				"Course Schedule",
				filters={
					"instructor": instructor,
					"schedule_date": target_date,
					"from_time": ["<=", slot.end_time],
					"to_time": [">=", slot.start_time]
				}
			)
			if instructor_schedules:
				instructor_name = frappe.db.get_value("Instructor", instructor, "instructor_name")
				conflicts.append(f"Instructor {instructor_name} already scheduled")

		# Check room conflict
		if room:
			room_schedules = frappe.get_all(
				"Course Schedule",
				filters={
					"room": room,
					"schedule_date": target_date,
					"from_time": ["<=", slot.end_time],
					"to_time": [">=", slot.start_time]
				}
			)
			if room_schedules:
				conflicts.append(f"Room {room} already booked")

		# Check student group conflict
		if student_group:
			group_schedules = frappe.get_all(
				"Course Schedule",
				filters={
					"student_group": student_group,
					"schedule_date": target_date,
					"from_time": ["<=", slot.end_time],
					"to_time": [">=", slot.start_time]
				}
			)
			if group_schedules:
				conflicts.append(f"Student group {student_group} already scheduled")

		return conflicts

	def get_next_day_date(self, day_name, start_date):
		"""Get next occurrence of a day from start date"""
		from datetime import timedelta

		target_date = getdate(start_date)
		target_weekday = self.DAYS.index(day_name)
		current_weekday = target_date.weekday()

		days_ahead = target_weekday - current_weekday
		if days_ahead < 0:
			days_ahead += 7

		return target_date + timedelta(days=days_ahead)


@frappe.whitelist()
def get_timetable(entity_type, entity_name, academic_term):
	"""API to get timetable"""
	generator = TimetableGenerator(academic_term)
	return generator.get_timetable(entity_type, entity_name)


@frappe.whitelist()
def create_schedule_entry(course, student_group, instructor, day, slot_name, room, academic_term):
	"""API to create schedule entry"""
	generator = TimetableGenerator(academic_term)
	return generator.create_schedule(course, student_group, instructor, day, slot_name, room)


@frappe.whitelist()
def check_conflicts(instructor, room, student_group, day, slot, academic_term):
	"""API to check scheduling conflicts"""
	generator = TimetableGenerator(academic_term)
	slot_doc = frappe.get_doc("Timetable Slot", slot)
	conflicts = generator.check_conflicts(instructor, room, student_group, day, slot_doc)

	return {
		"has_conflict": len(conflicts) > 0,
		"conflicts": conflicts
	}
