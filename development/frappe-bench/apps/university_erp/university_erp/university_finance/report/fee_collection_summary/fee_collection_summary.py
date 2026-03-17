# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary

def get_columns():
	return [
		{"fieldname": "program", "label": "Program", "fieldtype": "Link", "options": "Program", "width": 200},
		{"fieldname": "total_students", "label": "Total Students", "fieldtype": "Int", "width": 120},
		{"fieldname": "fees_generated", "label": "Fees Generated", "fieldtype": "Currency", "width": 150},
		{"fieldname": "fees_collected", "label": "Fees Collected", "fieldtype": "Currency", "width": 150},
		{"fieldname": "fees_outstanding", "label": "Outstanding", "fieldtype": "Currency", "width": 150},
		{"fieldname": "collection_percentage", "label": "Collection %", "fieldtype": "Percent", "width": 120}
	]

def get_data(filters):
	conditions = "f.docstatus = 1"
	
	if filters.get("academic_year"):
		conditions += f" AND fs.custom_academic_year = '{filters.get('academic_year')}'"
	
	if filters.get("from_date"):
		conditions += f" AND f.posting_date >= '{filters.get('from_date')}'"
	
	if filters.get("to_date"):
		conditions += f" AND f.posting_date <= '{filters.get('to_date')}'"
	
	data = frappe.db.sql(f"""
		SELECT
			f.program,
			COUNT(DISTINCT f.student) as total_students,
			SUM(f.grand_total) as fees_generated,
			SUM(f.grand_total - f.outstanding_amount) as fees_collected,
			SUM(f.outstanding_amount) as fees_outstanding,
			ROUND(SUM(f.grand_total - f.outstanding_amount) / NULLIF(SUM(f.grand_total), 0) * 100, 2) as collection_percentage
		FROM `tabFees` f
		LEFT JOIN `tabFee Structure` fs ON f.fee_structure = fs.name
		WHERE {conditions}
		GROUP BY f.program
		ORDER BY fees_generated DESC
	""", as_dict=True)
	
	return data

def get_chart(data):
	if not data:
		return None
	
	return {
		"data": {
			"labels": [d["program"] for d in data],
			"datasets": [
				{"name": "Collected", "values": [d["fees_collected"] or 0 for d in data]},
				{"name": "Outstanding", "values": [d["fees_outstanding"] or 0 for d in data]}
			]
		},
		"type": "bar",
		"colors": ["#28a745", "#dc3545"]
	}

def get_summary(data):
	total_generated = sum(d["fees_generated"] or 0 for d in data)
	total_collected = sum(d["fees_collected"] or 0 for d in data)
	total_outstanding = sum(d["fees_outstanding"] or 0 for d in data)
	
	return [
		{"label": "Total Generated", "value": total_generated, "datatype": "Currency"},
		{"label": "Total Collected", "value": total_collected, "datatype": "Currency", "indicator": "Green"},
		{"label": "Total Outstanding", "value": total_outstanding, "datatype": "Currency", "indicator": "Red"},
		{"label": "Collection Rate", "value": f"{(total_collected/total_generated*100):.1f}%" if total_generated else "0%", "indicator": "Blue"}
	]
