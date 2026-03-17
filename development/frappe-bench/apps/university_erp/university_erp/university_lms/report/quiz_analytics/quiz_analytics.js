// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Quiz Analytics"] = {
	"filters": [
		{
			"fieldname": "lms_course",
			"label": __("LMS Course"),
			"fieldtype": "Link",
			"options": "LMS Course"
		},
		{
			"fieldname": "quiz",
			"label": __("Quiz"),
			"fieldtype": "Link",
			"options": "LMS Quiz"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		}
	]
};
