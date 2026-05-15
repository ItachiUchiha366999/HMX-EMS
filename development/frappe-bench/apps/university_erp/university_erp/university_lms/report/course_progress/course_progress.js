// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Course Progress"] = {
	"filters": [
		{
			"fieldname": "lms_course",
			"label": __("LMS Course"),
			"fieldtype": "Link",
			"options": "LMS Course"
		},
		{
			"fieldname": "academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term"
		},
		{
			"fieldname": "student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student"
		},
		{
			"fieldname": "min_progress",
			"label": __("Min Progress %"),
			"fieldtype": "Int",
			"default": 0
		}
	]
};
