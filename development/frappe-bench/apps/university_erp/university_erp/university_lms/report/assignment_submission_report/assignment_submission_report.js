// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Assignment Submission Report"] = {
	"filters": [
		{
			"fieldname": "lms_course",
			"label": __("LMS Course"),
			"fieldtype": "Link",
			"options": "LMS Course"
		},
		{
			"fieldname": "assignment",
			"label": __("Assignment"),
			"fieldtype": "Link",
			"options": "LMS Assignment"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nSubmitted\nUnder Review\nGraded\nResubmission Required"
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
