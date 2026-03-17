# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, date_diff
from datetime import datetime, timedelta


def on_submit(doc, method):
	"""Calculate academic impact when leave is submitted"""
	if not doc.custom_affects_teaching:
		return
	
	calculate_academic_impact(doc)
	notify_hod(doc)


def on_cancel(doc, method):
	"""Clean up when leave is cancelled"""
	if doc.custom_temporary_assignment:
		# Cancel temporary assignment if exists
		temp_assign = frappe.get_doc("Temporary Teaching Assignment", doc.custom_temporary_assignment)
		if temp_assign.docstatus == 1:
			temp_assign.cancel()


def calculate_academic_impact(leave_doc):
	"""Calculate which courses and how many classes are affected"""
	if not leave_doc.custom_affects_teaching:
		return
	
	# Get teaching assignments for this faculty
	assignments = frappe.get_all(
		"Teaching Assignment",
		filters={
			"instructor": leave_doc.employee,
			"docstatus": 1
		},
		fields=["name", "course", "course_name", "program"]
	)
	
	total_classes = 0
	affected_courses = []
	
	for assignment in assignments:
		# Get schedule for this assignment
		schedules = frappe.get_all(
			"Teaching Assignment Schedule",
			filters={"parent": assignment.name},
			fields=["day", "start_time", "end_time"]
		)
		
		classes_affected = count_classes_in_period(
			schedules,
			leave_doc.from_date,
			leave_doc.to_date
		)
		
		if classes_affected > 0:
			affected_courses.append({
				"course": assignment.course,
				"program": assignment.program,
				"classes_affected": classes_affected
			})
			total_classes += classes_affected
	
	# Update leave application
	leave_doc.custom_total_classes_affected = total_classes
	
	# Clear and add affected courses
	leave_doc.custom_affected_courses = []
	for course in affected_courses:
		leave_doc.append("custom_affected_courses", course)
	
	leave_doc.save()


def count_classes_in_period(schedules, from_date, to_date):
	"""Count how many classes fall within the leave period"""
	classes = 0
	current_date = getdate(from_date)
	end_date = getdate(to_date)
	
	while current_date <= end_date:
		day_name = current_date.strftime("%A")
		
		# Check if there's a class on this day
		for schedule in schedules:
			if schedule.day == day_name:
				classes += 1
		
		current_date += timedelta(days=1)
	
	return classes


def notify_hod(leave_doc):
	"""Notify Head of Department about leave with academic impact"""
	if not leave_doc.custom_total_classes_affected:
		return
	
	# Get HoD from employee's department
	department = frappe.get_value("Employee", leave_doc.employee, "department")
	if not department:
		return
	
	# In a real implementation, you would:
	# 1. Get HoD email from Department DocType custom field
	# 2. Send email notification
	# 3. Create a notification document
	
	# For now, just mark as notified
	leave_doc.custom_hod_notified = 1
	leave_doc.save()
	
	frappe.msgprint(
		_("HoD has been notified about leave affecting {0} classes").format(
			leave_doc.custom_total_classes_affected
		),
		alert=True
	)
