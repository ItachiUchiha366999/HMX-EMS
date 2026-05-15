// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Faculty Workload Summary"] = {
	"filters": [
		{
			"fieldname": "academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term",
			"default": "2026-2027 (Semester 2)"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		}
	]
};
