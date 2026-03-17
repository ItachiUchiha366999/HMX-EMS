# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart

def get_columns():
	return [
		{"fieldname": "employee", "label": "Employee ID", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": "Faculty Name", "fieldtype": "Data", "width": 180},
		{"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department", "width": 150},
		{"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 150},
		{"fieldname": "total_assignments", "label": "Assignments", "fieldtype": "Int", "width": 100},
		{"fieldname": "total_hours", "label": "Weekly Hours", "fieldtype": "Float", "width": 120, "precision": 2},
		{"fieldname": "lecture_hours", "label": "Lecture Hrs", "fieldtype": "Float", "width": 100, "precision": 2},
		{"fieldname": "tutorial_hours", "label": "Tutorial Hrs", "fieldtype": "Float", "width": 100, "precision": 2},
		{"fieldname": "practical_hours", "label": "Practical Hrs", "fieldtype": "Float", "width": 100, "precision": 2},
		{"fieldname": "utilization", "label": "Utilization", "fieldtype": "Data", "width": 120}
	]

def get_data(filters):
	conditions = ""
	
	if filters.get("academic_term"):
		conditions += f" AND ta.academic_term = '{filters.get('academic_term')}'"
	
	if filters.get("department"):
		conditions += f" AND e.department = '{filters.get('department')}'"
	
	data = frappe.db.sql(f"""
		SELECT
			e.name as employee,
			e.employee_name,
			e.department,
			e.designation,
			COUNT(ta.name) as total_assignments,
			SUM(ta.total_weekly_hours) as total_hours,
			SUM(ta.lecture_hours) as lecture_hours,
			SUM(ta.tutorial_hours) as tutorial_hours,
			SUM(ta.practical_hours) as practical_hours
		FROM `tabEmployee` e
		LEFT JOIN `tabTeaching Assignment` ta ON ta.instructor = e.name AND ta.docstatus = 1
		WHERE e.custom_is_faculty = 1
			AND e.status = 'Active'
			{conditions}
		GROUP BY e.name
		ORDER BY total_hours DESC
	""", as_dict=True)
	
	for row in data:
		hours = row.total_hours or 0
		if hours == 0:
			row.utilization = "No Assignment"
		elif hours < 12:
			row.utilization = "Underutilized"
		elif hours <= 18:
			row.utilization = "Optimal"
		else:
			row.utilization = "Overloaded"
	
	return data

def get_chart(data):
	if not data:
		return None
	
	utilization_counts = {"No Assignment": 0, "Underutilized": 0, "Optimal": 0, "Overloaded": 0}
	
	for row in data:
		utilization_counts[row.utilization] = utilization_counts.get(row.utilization, 0) + 1
	
	return {
		"data": {
			"labels": list(utilization_counts.keys()),
			"datasets": [{"name": "Faculty Count", "values": list(utilization_counts.values())}]
		},
		"type": "bar",
		"colors": ["#cccccc", "#ffa00", "#28a745", "#dc3545"]
	}
