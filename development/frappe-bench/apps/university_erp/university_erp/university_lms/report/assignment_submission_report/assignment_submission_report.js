// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Assignment Submission Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
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
			"fieldname": "student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nSubmitted\nUnder Review\nGraded\nResubmission Required"
		}
	]
};
