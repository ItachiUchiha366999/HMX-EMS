# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_update(doc, method):
	"""Auto-create faculty profile for teaching staff"""
	if getattr(doc, "custom_is_faculty", 0) and not getattr(doc, "custom_faculty_profile", None):
		create_faculty_profile(doc)


def create_faculty_profile(employee):
	"""Create Faculty Profile for employee"""
	try:
		# Check if profile already exists
		existing = frappe.db.exists("Faculty Profile", {"employee": employee.name})
		if existing:
			employee.custom_faculty_profile = existing
			employee.save()
			return
		
		# Create new faculty profile
		profile = frappe.get_doc({
			"doctype": "Faculty Profile",
			"employee": employee.name,
			"employee_name": employee.employee_name,
			"department": employee.department,
			"designation": employee.designation,
			"date_of_joining": employee.date_of_joining,
			"specialization": employee.get("custom_specialization"),
			"teaching_experience_years": employee.get("custom_teaching_experience"),
		})
		
		profile.insert(ignore_permissions=True)
		
		# Link back to employee
		employee.custom_faculty_profile = profile.name
		employee.save()
		
		frappe.msgprint(
			_("Faculty Profile {0} created automatically").format(profile.name),
			alert=True,
			indicator="green"
		)
	
	except Exception as e:
		frappe.log_error(f"Error creating faculty profile for {employee.name}: {str(e)}")
