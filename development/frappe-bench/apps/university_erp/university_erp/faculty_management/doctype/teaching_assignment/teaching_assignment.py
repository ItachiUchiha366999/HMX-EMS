# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TeachingAssignment(Document):
	def validate(self):
		"""Validate teaching assignment before saving"""
		self.validate_instructor()
		self.calculate_weekly_hours()
		self.check_schedule_conflicts()

	def on_submit(self):
		"""Update faculty workload when assignment is submitted"""
		self.update_faculty_workload()

	def on_cancel(self):
		"""Update faculty workload when assignment is cancelled"""
		self.update_faculty_workload(add=False)

	def validate_instructor(self):
		"""Ensure instructor is teaching staff"""
		if not self.instructor:
			return

		employee = frappe.get_doc("Employee", self.instructor)
		if not employee.get("custom_is_faculty"):
			frappe.throw(_("Employee {0} is not marked as Faculty").format(self.instructor))

	def calculate_weekly_hours(self):
		"""Calculate total weekly hours from schedule"""
		self.total_weekly_hours = flt(self.lecture_hours or 0) + flt(self.tutorial_hours or 0) + flt(self.practical_hours or 0)

	def check_schedule_conflicts(self):
		"""Check for instructor and room conflicts in schedule"""
		if not self.schedule:
			return

		for schedule in self.schedule:
			# Check instructor conflict
			conflicts = frappe.db.sql("""
				SELECT DISTINCT ta.name, ta.course, ta.instructor_name
				FROM `tabTeaching Assignment` ta
				INNER JOIN `tabTeaching Assignment Schedule` tas ON tas.parent = ta.name
				WHERE ta.docstatus = 1
					AND ta.name != %s
					AND ta.instructor = %s
					AND ta.academic_term = %s
					AND tas.day = %s
					AND (
						(tas.start_time <= %s AND tas.end_time > %s)
						OR (tas.start_time < %s AND tas.end_time >= %s)
						OR (tas.start_time >= %s AND tas.end_time <= %s)
					)
			""", (self.name or 'new', self.instructor, self.academic_term,
				  schedule.day, schedule.start_time, schedule.start_time,
				  schedule.end_time, schedule.end_time,
				  schedule.start_time, schedule.end_time), as_dict=True)

			if conflicts:
				conflict_msg = _("Instructor {0} has a conflict on {1} from {2} to {3} with {4}").format(
					self.instructor_name, schedule.day, schedule.start_time,
					schedule.end_time, conflicts[0].name
				)
				frappe.throw(conflict_msg)

			# Check room conflict
			if schedule.room:
				room_conflicts = frappe.db.sql("""
					SELECT DISTINCT ta.name, ta.course
					FROM `tabTeaching Assignment` ta
					INNER JOIN `tabTeaching Assignment Schedule` tas ON tas.parent = ta.name
					WHERE ta.docstatus = 1
						AND ta.name != %s
						AND ta.academic_term = %s
						AND tas.day = %s
						AND tas.room = %s
						AND (
							(tas.start_time <= %s AND tas.end_time > %s)
							OR (tas.start_time < %s AND tas.end_time >= %s)
							OR (tas.start_time >= %s AND tas.end_time <= %s)
						)
				""", (self.name or 'new', self.academic_term, schedule.day, schedule.room,
					  schedule.start_time, schedule.start_time,
					  schedule.end_time, schedule.end_time,
					  schedule.start_time, schedule.end_time), as_dict=True)

				if room_conflicts:
					conflict_msg = _("Room {0} is already booked on {1} from {2} to {3} for {4}").format(
						schedule.room, schedule.day, schedule.start_time,
						schedule.end_time, room_conflicts[0].name
					)
					frappe.throw(conflict_msg)

	def update_faculty_workload(self, add=True):
		"""Update faculty profile with current workload"""
		if not self.instructor:
			return

		# Get or create faculty profile
		faculty_profile = frappe.db.get_value("Faculty Profile", {"employee": self.instructor}, "name")
		if not faculty_profile:
			return

		# Calculate total workload for this faculty
		total_workload = frappe.db.sql("""
			SELECT SUM(total_weekly_hours) as total
			FROM `tabTeaching Assignment`
			WHERE docstatus = 1
				AND instructor = %s
				AND academic_term = %s
		""", (self.instructor, self.academic_term), as_dict=True)

		workload = flt(total_workload[0].total if total_workload else 0)

		# Update faculty profile
		frappe.db.set_value("Faculty Profile", faculty_profile, "current_workload_hours", workload)

		# Also update Employee custom field
		frappe.db.set_value("Employee", self.instructor, "custom_current_workload", workload)


@frappe.whitelist()
def get_instructor_schedule(instructor, academic_term, day=None):
	"""Get instructor's teaching schedule for a specific term and optional day"""
	filters = {
		"docstatus": 1,
		"instructor": instructor,
		"academic_term": academic_term
	}

	if day:
		filters["day"] = day

	schedule = frappe.db.sql("""
		SELECT tas.day, tas.start_time, tas.end_time, tas.room, tas.type,
			   ta.course, ta.course_name, ta.program
		FROM `tabTeaching Assignment Schedule` tas
		INNER JOIN `tabTeaching Assignment` ta ON tas.parent = ta.name
		WHERE ta.docstatus = 1
			AND ta.instructor = %(instructor)s
			AND ta.academic_term = %(academic_term)s
			{day_filter}
		ORDER BY tas.day, tas.start_time
	""".format(day_filter="AND tas.day = %(day)s" if day else ""), filters, as_dict=True)

	return schedule


@frappe.whitelist()
def check_instructor_availability(instructor, academic_term, day, start_time, end_time):
	"""Check if instructor is available at the given time slot"""
	conflicts = frappe.db.sql("""
		SELECT ta.name, ta.course, tas.start_time, tas.end_time
		FROM `tabTeaching Assignment` ta
		INNER JOIN `tabTeaching Assignment Schedule` tas ON tas.parent = ta.name
		WHERE ta.docstatus = 1
			AND ta.instructor = %s
			AND ta.academic_term = %s
			AND tas.day = %s
			AND (
				(tas.start_time <= %s AND tas.end_time > %s)
				OR (tas.start_time < %s AND tas.end_time >= %s)
				OR (tas.start_time >= %s AND tas.end_time <= %s)
			)
	""", (instructor, academic_term, day, start_time, start_time,
		  end_time, end_time, start_time, end_time), as_dict=True)

	return {
		"available": len(conflicts) == 0,
		"conflicts": conflicts
	}


@frappe.whitelist()
def check_room_availability(room, academic_term, day, start_time, end_time):
	"""Check if room is available at the given time slot"""
	conflicts = frappe.db.sql("""
		SELECT ta.name, ta.course, ta.instructor_name, tas.start_time, tas.end_time
		FROM `tabTeaching Assignment` ta
		INNER JOIN `tabTeaching Assignment Schedule` tas ON tas.parent = ta.name
		WHERE ta.docstatus = 1
			AND ta.academic_term = %s
			AND tas.day = %s
			AND tas.room = %s
			AND (
				(tas.start_time <= %s AND tas.end_time > %s)
				OR (tas.start_time < %s AND tas.end_time >= %s)
				OR (tas.start_time >= %s AND tas.end_time <= %s)
			)
	""", (academic_term, day, room, start_time, start_time,
		  end_time, end_time, start_time, end_time), as_dict=True)

	return {
		"available": len(conflicts) == 0,
		"conflicts": conflicts
	}
