// Copyright (c) 2025, University and contributors
// For license information, please see license.txt

frappe.query_reports["Fee Collection Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": "2026-01-01"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": "2026-05-01"
		},
		{
			"fieldname": "program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program"
		}
	]
};
