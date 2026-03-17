// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Visitor Log"] = {
	"filters": [
		{
			"fieldname": "building",
			"label": __("Building"),
			"fieldtype": "Link",
			"options": "Hostel Building"
		},
		{
			"fieldname": "student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student"
		},
		{
			"fieldname": "relationship",
			"label": __("Relationship"),
			"fieldtype": "Select",
			"options": "\nParent\nGuardian\nSibling\nRelative\nFriend\nOther"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nChecked In\nChecked Out\nDenied"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}
	]
};
