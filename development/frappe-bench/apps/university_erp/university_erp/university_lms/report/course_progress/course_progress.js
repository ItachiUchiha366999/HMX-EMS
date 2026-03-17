// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Course Progress"] = {
	"filters": [
		{
			"fieldname": "lms_course",
			"label": __("LMS Course"),
			"fieldtype": "Link",
			"options": "LMS Course",
			"reqd": 1
		},
		{
			"fieldname": "academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term"
		}
	]
};
