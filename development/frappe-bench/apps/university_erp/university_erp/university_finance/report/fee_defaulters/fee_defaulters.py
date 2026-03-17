# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart

def get_columns():
	return [
		{"fieldname": "student", "label": "Student", "fieldtype": "Link", "options": "Student", "width": 120},
		{"fieldname": "student_name", "label": "Student Name", "fieldtype": "Data", "width": 180},
		{"fieldname": "program", "label": "Program", "fieldtype": "Link", "options": "Program", "width": 150},
		{"fieldname": "fee_name", "label": "Fee ID", "fieldtype": "Link", "options": "Fees", "width": 120},
		{"fieldname": "due_date", "label": "Due Date", "fieldtype": "Date", "width": 100},
		{"fieldname": "days_overdue", "label": "Days Overdue", "fieldtype": "Int", "width": 100},
		{"fieldname": "grand_total", "label": "Total Amount", "fieldtype": "Currency", "width": 120},
		{"fieldname": "outstanding_amount", "label": "Outstanding", "fieldtype": "Currency", "width": 120},
		{"fieldname": "penalty_amount", "label": "Penalty", "fieldtype": "Currency", "width": 100},
		{"fieldname": "contact", "label": "Contact", "fieldtype": "Data", "width": 120}
	]

def get_data(filters):
	conditions = "f.docstatus = 1 AND f.outstanding_amount > 0"
	
	if filters.get("program"):
		conditions += f" AND f.program = '{filters.get('program')}'"
	
	if filters.get("academic_year"):
		conditions += f" AND fs.custom_academic_year = '{filters.get('academic_year')}'"
	
	if filters.get("min_days_overdue"):
		conditions += f" AND DATEDIFF(CURDATE(), f.custom_due_date) >= {filters.get('min_days_overdue')}"
	
	data = frappe.db.sql(f"""
		SELECT
			f.student,
			f.student_name,
			f.program,
			f.name as fee_name,
			f.custom_due_date as due_date,
			DATEDIFF(CURDATE(), f.custom_due_date) as days_overdue,
			f.grand_total,
			f.outstanding_amount,
			f.custom_penalty_amount as penalty_amount,
			s.student_mobile_number as contact
		FROM `tabFees` f
		LEFT JOIN `tabFee Structure` fs ON f.fee_structure = fs.name
		LEFT JOIN `tabStudent` s ON f.student = s.name
		WHERE {conditions}
		AND f.custom_due_date < CURDATE()
		ORDER BY days_overdue DESC
	""", as_dict=True)
	
	return data

def get_chart(data):
	if not data:
		return None
	
	# Group by days overdue range
	ranges = {"0-7": 0, "8-15": 0, "16-30": 0, "31-60": 0, "60+": 0}
	
	for d in data:
		days = d.days_overdue or 0
		if days <= 7:
			ranges["0-7"] += 1
		elif days <= 15:
			ranges["8-15"] += 1
		elif days <= 30:
			ranges["16-30"] += 1
		elif days <= 60:
			ranges["31-60"] += 1
		else:
			ranges["60+"] += 1
	
	return {
		"data": {
			"labels": list(ranges.keys()),
			"datasets": [{"name": "Defaulters", "values": list(ranges.values())}]
		},
		"type": "bar",
		"colors": ["#ff5858"]
	}
