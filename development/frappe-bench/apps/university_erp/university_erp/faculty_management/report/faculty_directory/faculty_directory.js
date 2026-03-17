// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Faculty Directory"] = {
	"filters": [
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation"
		}
	]
};
