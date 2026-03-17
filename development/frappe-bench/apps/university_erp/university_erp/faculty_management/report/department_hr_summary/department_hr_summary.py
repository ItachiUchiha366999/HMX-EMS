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

def get_data(filters):
	data = frappe.db.sql("""
		SELECT
			e.department,
			COUNT(e.name) as total_faculty,
			SUM(CASE WHEN e.custom_employee_category = 'Teaching Staff' THEN 1 ELSE 0 END) as teaching_staff,
			SUM(CASE WHEN e.custom_employee_category != 'Teaching Staff' THEN 1 ELSE 0 END) as non_teaching,
			AVG(e.custom_current_workload) as avg_workload,
			SUM(CASE WHEN e.custom_current_workload > 18 THEN 1 ELSE 0 END) as overloaded,
			SUM(CASE WHEN e.custom_current_workload < 12 THEN 1 ELSE 0 END) as underutilized,
			AVG(fp.total_publications) as avg_publications
		FROM `tabEmployee` e
		LEFT JOIN `tabFaculty Profile` fp ON fp.employee = e.name
		WHERE e.custom_is_faculty = 1
			AND e.status = 'Active'
		GROUP BY e.department
		ORDER BY total_faculty DESC
	""", as_dict=True)
	
	return data

def get_summary(data):
	total_faculty = sum(d.total_faculty for d in data)
	total_teaching = sum(d.teaching_staff for d in data)
	total_overloaded = sum(d.overloaded for d in data)
	
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
				{"name": "Teaching", "values": [d.teaching_staff for d in data]},
				{"name": "Non-Teaching", "values": [d.non_teaching for d in data]}
			]
		},
		"type": "bar",
		"colors": ["#28a745", "#17a2b8"]
	}
