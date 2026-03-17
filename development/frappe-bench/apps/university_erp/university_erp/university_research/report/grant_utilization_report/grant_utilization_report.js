// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Grant Utilization Report"] = {
	"filters": [
		{
			"fieldname": "funding_agency",
			"label": __("Funding Agency"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "grant_type",
			"label": __("Grant Type"),
			"fieldtype": "Select",
			"options": "\nMajor\nMinor\nSeed Grant\nTravel Grant\nEquipment Grant"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nApplied\nUnder Review\nApproved\nRejected\nCompleted"
		}
	]
};
