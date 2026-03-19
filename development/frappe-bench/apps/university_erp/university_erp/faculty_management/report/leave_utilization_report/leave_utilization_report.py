# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"fieldname": "employee", "label": "Employee", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": "Name", "fieldtype": "Data", "width": 180},
		{"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department", "width": 150},
		{"fieldname": "leave_type", "label": "Leave Type", "fieldtype": "Link", "options": "Leave Type", "width": 120},
		{"fieldname": "total_leave_days", "label": "Total Leave Taken", "fieldtype": "Float", "width": 140, "precision": 1},
		{"fieldname": "allocated_days", "label": "Allocated", "fieldtype": "Float", "width": 100, "precision": 1},
		{"fieldname": "balance", "label": "Balance", "fieldtype": "Float", "width": 100, "precision": 1},
		{"fieldname": "utilization_pct", "label": "Utilization %", "fieldtype": "Percent", "width": 120},
		{"fieldname": "classes_affected", "label": "Classes Affected", "fieldtype": "Int", "width": 140}
	]

def _has_custom_field(doctype, fieldname):
	"""Check if a custom field exists on the given doctype."""
	try:
		meta = frappe.get_meta(doctype)
		return meta.has_field(fieldname)
	except Exception:
		return False

def get_data(filters):
	has_classes_affected = _has_custom_field("Leave Application", "custom_total_classes_affected")

	conditions = "la.docstatus = 1"

	if filters.get("employee"):
		conditions += f" AND la.employee = '{filters.get('employee')}'"

	if filters.get("department"):
		conditions += f" AND e.department = '{filters.get('department')}'"

	if filters.get("leave_type"):
		conditions += f" AND la.leave_type = '{filters.get('leave_type')}'"

	if filters.get("from_date"):
		conditions += f" AND la.from_date >= '{filters.get('from_date')}'"

	if filters.get("to_date"):
		conditions += f" AND la.to_date <= '{filters.get('to_date')}'"

	classes_expr = "SUM(la.custom_total_classes_affected)" if has_classes_affected else "0"

	data = frappe.db.sql(f"""
		SELECT
			la.employee,
			e.employee_name,
			e.department,
			la.leave_type,
			SUM(la.total_leave_days) as total_leave_days,
			{classes_expr} as classes_affected
		FROM `tabLeave Application` la
		INNER JOIN `tabEmployee` e ON la.employee = e.name
		WHERE {conditions}
		GROUP BY la.employee, la.leave_type
		ORDER BY total_leave_days DESC
	""", as_dict=True)

	# Get allocation data
	for row in data:
		allocation = frappe.db.get_value(
			"Leave Allocation",
			{"employee": row.employee, "leave_type": row.leave_type, "docstatus": 1},
			["total_leaves_allocated", "total_leaves_allocated - leaves_taken as balance"],
			as_dict=True
		)
		if allocation:
			row.allocated_days = allocation.total_leaves_allocated
			row.balance = allocation.balance
			row.utilization_pct = (row.total_leave_days / allocation.total_leaves_allocated * 100) if allocation.total_leaves_allocated else 0
		else:
			row.allocated_days = 0
			row.balance = 0
			row.utilization_pct = 0

	return data
