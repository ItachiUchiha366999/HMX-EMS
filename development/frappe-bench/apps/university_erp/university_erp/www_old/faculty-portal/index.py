# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
	"""Get context for faculty portal page"""

	# Check if user is logged in
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to access Faculty Portal"), frappe.PermissionError)

	# Get employee linked to this user
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": frappe.session.user, "custom_is_faculty": 1},
		["name", "employee_name", "department", "designation", "custom_faculty_profile"],
		as_dict=True
	)

	if not employee:
		frappe.throw(_("You are not authorized to access Faculty Portal"), frappe.PermissionError)

	context.employee = employee

	# Get faculty profile details
	if employee.custom_faculty_profile:
		faculty_profile = frappe.get_doc("Faculty Profile", employee.custom_faculty_profile)
		context.faculty_profile = faculty_profile
	else:
		context.faculty_profile = None

	# Get teaching assignments
	teaching_assignments = frappe.get_all(
		"Teaching Assignment",
		filters={
			"instructor": employee.name,
			"docstatus": 1
		},
		fields=[
			"name",
			"course",
			"course_name",
			"program",
			"academic_year",
			"academic_term",
			"total_weekly_hours",
			"lecture_hours",
			"lab_hours",
			"tutorial_hours"
		],
		order_by="academic_year desc, academic_term desc"
	)
	context.teaching_assignments = teaching_assignments

	# Get leave balance
	leave_balance = get_leave_balance(employee.name)
	context.leave_balance = leave_balance

	# Get recent leave applications
	recent_leaves = frappe.get_all(
		"Leave Application",
		filters={"employee": employee.name},
		fields=[
			"name",
			"leave_type",
			"from_date",
			"to_date",
			"total_leave_days",
			"status",
			"custom_total_classes_affected"
		],
		order_by="creation desc",
		limit=5
	)
	context.recent_leaves = recent_leaves

	# Get performance evaluations
	performance_evals = frappe.get_all(
		"Faculty Performance Evaluation",
		filters={"faculty": employee.custom_faculty_profile},
		fields=[
			"name",
			"evaluation_period",
			"evaluation_date",
			"overall_rating",
			"status"
		],
		order_by="evaluation_date desc",
		limit=5
	)
	context.performance_evals = performance_evals

	# Get student feedback summary
	if employee.custom_faculty_profile:
		feedback_summary = get_feedback_summary(employee.custom_faculty_profile)
		context.feedback_summary = feedback_summary
	else:
		context.feedback_summary = None

	# Page metadata
	context.title = _("Faculty Portal")
	context.show_sidebar = False
	context.no_cache = 1

	return context


def get_leave_balance(employee):
	"""Get leave balance for employee"""
	leave_types = frappe.get_all("Leave Type", pluck="name")
	balance = []

	for leave_type in leave_types:
		allocation = frappe.db.get_value(
			"Leave Allocation",
			{
				"employee": employee,
				"leave_type": leave_type,
				"docstatus": 1
			},
			["total_leaves_allocated", "new_leaves_allocated"],
			as_dict=True
		)

		if allocation:
			# Get used leaves
			used_leaves = frappe.db.sql("""
				SELECT IFNULL(SUM(total_leave_days), 0)
				FROM `tabLeave Application`
				WHERE employee = %s
					AND leave_type = %s
					AND docstatus = 1
					AND status = 'Approved'
			""", (employee, leave_type))[0][0]

			total_allocated = (allocation.total_leaves_allocated or 0) + (allocation.new_leaves_allocated or 0)
			remaining = total_allocated - used_leaves

			balance.append({
				"leave_type": leave_type,
				"total_allocated": total_allocated,
				"used": used_leaves,
				"remaining": remaining
			})

	return balance


def get_feedback_summary(faculty_profile):
	"""Get student feedback summary for faculty"""
	feedback = frappe.db.sql("""
		SELECT
			AVG(overall_rating) as avg_rating,
			COUNT(*) as total_feedbacks,
			AVG(teaching_effectiveness) as avg_teaching,
			AVG(subject_knowledge) as avg_knowledge,
			AVG(communication_skills) as avg_communication
		FROM `tabStudent Feedback`
		WHERE faculty = %s
			AND docstatus = 1
	""", faculty_profile, as_dict=True)

	return feedback[0] if feedback else None
