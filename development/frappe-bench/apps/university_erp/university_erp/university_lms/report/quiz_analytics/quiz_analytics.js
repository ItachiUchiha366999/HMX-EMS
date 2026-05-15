// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Quiz Analytics"] = {
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
			"fieldname": "quiz",
			"label": __("Quiz"),
			"fieldtype": "Link",
			"options": "LMS Quiz"
		},
		{
			"fieldname": "student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student"
		},
		{
			"fieldname": "passed",
			"label": __("Passed Only"),
			"fieldtype": "Check",
			"default": 0
		}
	]
};
