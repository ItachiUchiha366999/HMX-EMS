// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["PO Attainment Report"] = {
	"filters": [
		{
			"fieldname": "program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program",
			"reqd": 1
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

		if (column.fieldname === "achieved") {
			if (data.achieved === "✓") {
				value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
			} else {
				value = `<span style="color: #dc3545; font-weight: bold;">${value}</span>`;
			}
		}

		if (column.fieldname === "is_pso") {
			if (data.is_pso === "PSO") {
				value = `<span style="color: #17a2b8;">${value}</span>`;
			} else {
				value = `<span style="color: #6c757d;">${value}</span>`;
			}
		}

		if (column.fieldname === "final_attainment") {
			if (data.final_attainment >= 2) {
				value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
			} else if (data.final_attainment >= 1) {
				value = `<span style="color: #ffc107;">${value}</span>`;
			} else {
				value = `<span style="color: #dc3545;">${value}</span>`;
			}
		}

		return value;
	}
};
