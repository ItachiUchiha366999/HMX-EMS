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

	if filters.get("department"):
		where_parts.append(f"e.department = '{filters.get('department')}'")

	if filters.get("designation"):
		where_parts.append(f"e.designation = '{filters.get('designation')}'")

	conditions = " AND ".join(where_parts)

	# Build SELECT fields
	category_expr = "e.custom_employee_category" if has_employee_category else "NULL"
	workload_expr = "e.custom_current_workload" if has_current_workload else "0"

	data = frappe.db.sql(f"""
		SELECT
			e.name as employee,
			e.employee_name,
			e.department,
			e.designation,
			{category_expr} as employee_category,
			fp.specialization,
			fp.h_index,
			fp.total_publications,
			{workload_expr} as current_workload,
			e.company_email as email,
			e.cell_number
		FROM `tabEmployee` e
		LEFT JOIN `tabFaculty Profile` fp ON fp.employee = e.name
		WHERE {conditions}
		ORDER BY e.employee_name
	""", as_dict=True)

	return data
