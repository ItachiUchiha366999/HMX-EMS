// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Program Attainment Summary"] = {
	"filters": [
		{
			"fieldname": "program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year"
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "status") {
			if (data.status === "Excellent") {
				value = `<span class="badge" style="background-color: #28a745; color: white;">${value}</span>`;
			} else if (data.status === "Good") {
				value = `<span class="badge" style="background-color: #17a2b8; color: white;">${value}</span>`;
			} else if (data.status === "Needs Improvement") {
				value = `<span class="badge" style="background-color: #ffc107; color: black;">${value}</span>`;
			} else {
				value = `<span class="badge" style="background-color: #dc3545; color: white;">${value}</span>`;
			}
		}

		if (column.fieldname === "nba_compliance" || column.fieldname === "naac_compliance") {
			let score = data[column.fieldname];
			if (score >= 80) {
				value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
			} else if (score >= 60) {
				value = `<span style="color: #17a2b8;">${value}</span>`;
			} else if (score >= 40) {
				value = `<span style="color: #ffc107;">${value}</span>`;
			} else {
				value = `<span style="color: #dc3545;">${value}</span>`;
			}
		}

		return value;
	}
};
