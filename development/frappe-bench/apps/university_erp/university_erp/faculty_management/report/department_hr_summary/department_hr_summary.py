# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	summary = get_summary(data)
	chart = get_chart(data)
	return columns, data, None, chart, summary

def get_columns():
	return [
		{"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department", "width": 200},
		{"fieldname": "total_faculty", "label": "Total Faculty", "fieldtype": "Int", "width": 120},
		{"fieldname": "teaching_staff", "label": "Teaching Staff", "fieldtype": "Int", "width": 120},
		{"fieldname": "non_teaching", "label": "Non-Teaching", "fieldtype": "Int", "width": 120},
		{"fieldname": "avg_workload", "label": "Avg Workload", "fieldtype": "Float", "width": 120, "precision": 2},
		{"fieldname": "overloaded", "label": "Overloaded", "fieldtype": "Int", "width": 100},
		{"fieldname": "underutilized", "label": "Underutilized", "fieldtype": "Int", "width": 120},
		{"fieldname": "avg_publications", "label": "Avg Publications", "fieldtype": "Float", "width": 140, "precision": 1}
	]

def _has_custom_field(doctype, fieldname):
	"""Check if a custom field exists on the given doctype."""
	try:
		meta = frappe.get_meta(doctype)
		return meta.has_field(fieldname)
	except Exception:
		return False

def get_data(filters):
	has_is_faculty = _has_custom_field("Employee", "custom_is_faculty")
	has_employee_category = _has_custom_field("Employee", "custom_employee_category")
	has_current_workload = _has_custom_field("Employee", "custom_current_workload")

	# Build WHERE clause
	where_parts = ["e.status = 'Active'"]
	if has_is_faculty:
		where_parts.append("e.custom_is_faculty = 1")

	conditions = " AND ".join(where_parts)

	# Build dynamic expressions
	if has_employee_category:
		teaching_expr = "SUM(CASE WHEN e.custom_employee_category = 'Teaching Staff' THEN 1 ELSE 0 END)"
		non_teaching_expr = "SUM(CASE WHEN e.custom_employee_category != 'Teaching Staff' THEN 1 ELSE 0 END)"
	else:
		teaching_expr = "COUNT(e.name)"
		non_teaching_expr = "0"

	if has_current_workload:
		avg_workload_expr = "AVG(e.custom_current_workload)"
		overloaded_expr = "SUM(CASE WHEN e.custom_current_workload > 18 THEN 1 ELSE 0 END)"
		underutilized_expr = "SUM(CASE WHEN e.custom_current_workload < 12 THEN 1 ELSE 0 END)"
	else:
		avg_workload_expr = "0"
		overloaded_expr = "0"
		underutilized_expr = "0"

	data = frappe.db.sql(f"""
		SELECT
			e.department,
			COUNT(e.name) as total_faculty,
			{teaching_expr} as teaching_staff,
			{non_teaching_expr} as non_teaching,
			{avg_workload_expr} as avg_workload,
			{overloaded_expr} as overloaded,
			{underutilized_expr} as underutilized,
			AVG(fp.total_publications) as avg_publications
		FROM `tabEmployee` e
		LEFT JOIN `tabFaculty Profile` fp ON fp.employee = e.name
		WHERE {conditions}
		GROUP BY e.department
		ORDER BY total_faculty DESC
	""", as_dict=True)

	return data

def get_summary(data):
	if not data:
		return []

	total_faculty = sum(d.total_faculty or 0 for d in data)
	total_teaching = sum(d.teaching_staff or 0 for d in data)
	total_overloaded = sum(d.overloaded or 0 for d in data)

	return [
		{"label": "Total Faculty", "value": total_faculty, "datatype": "Int"},
		{"label": "Teaching Staff", "value": total_teaching, "datatype": "Int", "indicator": "Green"},
		{"label": "Overloaded Faculty", "value": total_overloaded, "datatype": "Int", "indicator": "Red"}
	]

def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d.department for d in data],
			"datasets": [
				{"name": "Teaching", "values": [d.teaching_staff or 0 for d in data]},
				{"name": "Non-Teaching", "values": [d.non_teaching or 0 for d in data]}
			]
		},
		"type": "bar",
		"colors": ["#28a745", "#17a2b8"]
	}
