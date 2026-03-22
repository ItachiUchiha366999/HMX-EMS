// Copyright (c) 2025, University and contributors
// For license information, please see license.txt

frappe.query_reports["Fee Defaulters"] = {
	"filters": [
		{
			"fieldname": "program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program"
		},
		{
			"fieldname": "academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year"
		},
		{
			"fieldname": "min_days_overdue",
			"label": __("Minimum Days Overdue"),
			"fieldtype": "Int",
			"default": 0
		}
	]
};
