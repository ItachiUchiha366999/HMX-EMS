# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_update(doc, method):
	"""Calculate current strength and vacancies"""
	# Skip if custom fields don't exist yet (during initial setup)
	if not custom_fields_exist():
		return
	calculate_department_strength(doc)


def custom_fields_exist():
	"""Check if university_erp custom fields exist on Employee doctype"""
	try:
		# Check if custom_is_faculty field exists
		return frappe.db.exists("Custom Field", {
			"dt": "Employee",
			"fieldname": "custom_is_faculty"
		})
	except Exception:
		return False


def calculate_department_strength(department):
	"""Auto-calculate current strength and vacancies for department"""

	# Double-check custom fields exist before querying
	if not custom_fields_exist():
		return

	try:
		# Get current teaching strength
		teaching_count = frappe.db.count(
			"Employee",
			filters={
				"department": department.name,
				"custom_is_faculty": 1,
				"status": "Active"
			}
		)

		# Get current non-teaching strength
		non_teaching_count = frappe.db.count(
			"Employee",
			filters={
				"department": department.name,
				"custom_is_faculty": ["!=", 1],
				"status": "Active"
			}
		)
	except Exception:
		# If query fails (field doesn't exist), skip silently
		return

	# Check if department has the custom fields before updating
	if not hasattr(department, 'custom_current_teaching_strength'):
		return

	# Update current strength
	department.custom_current_teaching_strength = teaching_count
	department.custom_current_non_teaching_strength = non_teaching_count

	# Calculate vacancies
	sanctioned_teaching = department.get("custom_sanctioned_teaching_strength") or 0
	sanctioned_non_teaching = department.get("custom_sanctioned_non_teaching_strength") or 0

	teaching_vacancies = max(0, sanctioned_teaching - teaching_count)
	non_teaching_vacancies = max(0, sanctioned_non_teaching - non_teaching_count)

	department.custom_teaching_vacancies = teaching_vacancies
	department.custom_non_teaching_vacancies = non_teaching_vacancies
	department.custom_total_vacancies = teaching_vacancies + non_teaching_vacancies

	# Save without triggering the event again
	department.db_update()


def on_employee_change():
	"""Recalculate all department strengths when employee changes"""
	departments = frappe.get_all("Department", pluck="name")

	for dept_name in departments:
		dept = frappe.get_doc("Department", dept_name)
		calculate_department_strength(dept)
