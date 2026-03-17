# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"fieldname": "employee", "label": "Employee ID", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": "Name", "fieldtype": "Data", "width": 180},
		{"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department", "width": 150},
		{"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 150},
		{"fieldname": "employee_category", "label": "Category", "fieldtype": "Data", "width": 120},
		{"fieldname": "specialization", "label": "Specialization", "fieldtype": "Data", "width": 150},
		{"fieldname": "h_index", "label": "H-Index", "fieldtype": "Int", "width": 80},
		{"fieldname": "total_publications", "label": "Publications", "fieldtype": "Int", "width": 100},
		{"fieldname": "current_workload", "label": "Workload (Hrs)", "fieldtype": "Float", "width": 120, "precision": 2},
		{"fieldname": "email", "label": "Email", "fieldtype": "Data", "width": 200},
		{"fieldname": "cell_number", "label": "Mobile", "fieldtype": "Data", "width": 120}
	]

def get_data(filters):
	conditions = "e.custom_is_faculty = 1 AND e.status = 'Active'"
	
	if filters.get("department"):
		conditions += f" AND e.department = '{filters.get('department')}'"
	
	if filters.get("designation"):
		conditions += f" AND e.designation = '{filters.get('designation')}'"
	
	data = frappe.db.sql(f"""
		SELECT
			e.name as employee,
			e.employee_name,
			e.department,
			e.designation,
			e.custom_employee_category as employee_category,
			fp.specialization,
			fp.h_index,
			fp.total_publications,
			e.custom_current_workload as current_workload,
			e.company_email as email,
			e.cell_number
		FROM `tabEmployee` e
		LEFT JOIN `tabFaculty Profile` fp ON fp.employee = e.name
		WHERE {conditions}
		ORDER BY e.employee_name
	""", as_dict=True)
	
	return data
