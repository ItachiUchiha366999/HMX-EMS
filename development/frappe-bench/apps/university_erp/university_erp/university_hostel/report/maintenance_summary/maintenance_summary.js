// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Maintenance Summary"] = {
	"filters": [
		{
			"fieldname": "building",
			"label": __("Building"),
			"fieldtype": "Link",
			"options": "Hostel Building"
		},
		{
			"fieldname": "request_type",
			"label": __("Request Type"),
			"fieldtype": "Select",
			"options": "\nElectrical\nPlumbing\nFurniture\nCleaning\nAC\nInternet\nOther"
		},
		{
			"fieldname": "priority",
			"label": __("Priority"),
			"fieldtype": "Select",
			"options": "\nLow\nMedium\nHigh\nUrgent"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nOpen\nIn Progress\nCompleted\nCancelled"
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
