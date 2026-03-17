# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WorkloadDistributor(Document):
	def onload(self):
		"""Load workload analysis when form loads"""
		self.analyze_workload()

	def analyze_workload(self):
		"""Analyze workload distribution"""
		if not self.academic_term:
			return

		# Get all courses for the term
		filters = {"academic_term": self.academic_term}
		if self.program:
			filters["program"] = self.program

		all_courses = frappe.get_all("Course", filters=filters, fields=["name", "course_name"])
		self.total_courses = len(all_courses)

		# Get assigned courses
		assigned = frappe.get_all(
			"Teaching Assignment",
			filters={"academic_term": self.academic_term, "docstatus": 1},
			fields=["course"]
		)
		assigned_courses = {a.course for a in assigned}
		self.assigned_courses = len(assigned_courses)
		self.unassigned_courses = self.total_courses - self.assigned_courses

		# Get faculty workload
		faculty_workload = frappe.db.sql("""
			SELECT e.name, e.employee_name, e.custom_current_workload
			FROM `tabEmployee` e
			WHERE e.custom_is_faculty = 1
				AND e.status = 'Active'
				{dept_filter}
			ORDER BY e.custom_current_workload DESC
		""".format(dept_filter=f"AND e.department = '{self.department}'" if self.department else ""),
		as_dict=True)

		self.total_faculty = len(faculty_workload)
		self.overloaded_faculty = len([f for f in faculty_workload if (f.custom_current_workload or 0) > 18])
		self.underutilized_faculty = len([f for f in faculty_workload if (f.custom_current_workload or 0) < 12])

		# Generate recommendations HTML
		recommendations = []
		if self.unassigned_courses > 0:
			recommendations.append(f"<li><strong>{self.unassigned_courses} courses</strong> need instructor assignment</li>")

		if self.overloaded_faculty > 0:
			recommendations.append(f"<li><strong>{self.overloaded_faculty} faculty members</strong> are overloaded (>18 hrs/week)</li>")

		if self.underutilized_faculty > 0:
			recommendations.append(f"<li><strong>{self.underutilized_faculty} faculty members</strong> are underutilized (<12 hrs/week)</li>")

		if recommendations:
			self.recommendations = f"<ul>{''.join(recommendations)}</ul>"
		else:
			self.recommendations = "<p><strong>All courses are assigned and faculty workload is balanced.</strong></p>"


@frappe.whitelist()
def get_available_faculty(academic_term, department=None):
	"""Get list of available faculty for assignment"""
	filters = {"custom_is_faculty": 1, "status": "Active"}
	if department:
		filters["department"] = department

	faculty = frappe.get_all(
		"Employee",
		filters=filters,
		fields=["name", "employee_name", "custom_current_workload", "custom_specialization"],
		order_by="custom_current_workload"
	)

	return faculty
