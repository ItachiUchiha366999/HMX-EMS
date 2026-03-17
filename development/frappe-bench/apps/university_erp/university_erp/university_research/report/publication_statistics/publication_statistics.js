// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Publication Statistics"] = {
	"filters": [
		{
			"fieldname": "publication_type",
			"label": __("Type"),
			"fieldtype": "Select",
			"options": "\nJournal Article\nConference Paper\nBook Chapter\nBook\nPatent\nThesis\nTechnical Report\nOther"
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Int"
		},
		{
			"fieldname": "indexing",
			"label": __("Indexing"),
			"fieldtype": "Select",
			"options": "\nScopus\nWoS\nUGC"
		}
	]
};
