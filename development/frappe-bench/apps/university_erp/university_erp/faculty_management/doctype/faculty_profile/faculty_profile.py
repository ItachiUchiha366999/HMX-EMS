# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class FacultyProfile(Document):
	def validate(self):
		"""Validate faculty profile before saving"""
		self.validate_employee()
		self.calculate_publication_count()
		self.update_employee_link()

	def validate_employee(self):
		"""Ensure employee is teaching staff"""
		if not self.employee:
			return

		employee = frappe.get_doc("Employee", self.employee)
		if not employee.get("custom_is_faculty"):
			frappe.throw(_("Employee {0} must be marked as Faculty to create a Faculty Profile").format(self.employee))

	def calculate_publication_count(self):
		"""Calculate total and Scopus publication counts"""
		self.total_publications = len(self.publications) if self.publications else 0

	def update_employee_link(self):
		"""Update Employee record with Faculty Profile link"""
		if self.employee:
			frappe.db.set_value("Employee", self.employee, "custom_faculty_profile", self.name)


@frappe.whitelist()
def get_faculty_metrics(faculty_profile):
	"""Get comprehensive faculty metrics for performance evaluation"""
	profile = frappe.get_doc("Faculty Profile", faculty_profile)

	# Count publications by type
	publications = {
		"total": len(profile.publications) if profile.publications else 0,
		"scopus": len([p for p in profile.publications if p.scopus_indexed]) if profile.publications else 0,
		"journals": len([p for p in profile.publications if p.type == "Journal"]) if profile.publications else 0,
		"conferences": len([p for p in profile.publications if p.type == "Conference"]) if profile.publications else 0,
		"books": len([p for p in profile.publications if p.type in ["Book", "Book Chapter"]]) if profile.publications else 0,
		"patents": len([p for p in profile.publications if p.type == "Patent"]) if profile.publications else 0
	}

	# Count research projects by status
	projects = {
		"total": len(profile.research_projects) if profile.research_projects else 0,
		"ongoing": len([p for p in profile.research_projects if p.status == "Ongoing"]) if profile.research_projects else 0,
		"completed": len([p for p in profile.research_projects if p.status == "Completed"]) if profile.research_projects else 0,
		"total_funding": sum([p.amount or 0 for p in profile.research_projects]) if profile.research_projects else 0
	}

	# Count awards
	awards = len(profile.awards) if profile.awards else 0

	# Get teaching assignments for current term
	current_term = frappe.db.get_value("Academic Term", {"is_active": 1}, "name")
	teaching_assignments = frappe.db.count("Teaching Assignment", {
		"instructor": profile.employee,
		"academic_term": current_term,
		"docstatus": 1
	})

	return {
		"publications": publications,
		"projects": projects,
		"awards": awards,
		"teaching_assignments": teaching_assignments,
		"h_index": profile.h_index or 0,
		"total_citations": profile.total_citations or 0,
		"current_workload": profile.current_workload_hours or 0
	}


@frappe.whitelist()
def get_faculty_list(department=None, designation=None):
	"""Get list of faculty with basic information"""
	filters = {"docstatus": 0}
	if department:
		filters["department"] = department
	if designation:
		filters["designation"] = designation

	faculty_list = frappe.get_all(
		"Faculty Profile",
		filters=filters,
		fields=["name", "employee", "employee_name", "department", "designation",
				"specialization", "h_index", "total_publications", "current_workload_hours"],
		order_by="employee_name"
	)

	return faculty_list
