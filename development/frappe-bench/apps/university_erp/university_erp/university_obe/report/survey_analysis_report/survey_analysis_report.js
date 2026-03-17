// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Survey Analysis Report"] = {
	"filters": [
		{
			"fieldname": "program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program",
			"reqd": 1
		},
		{
			"fieldname": "survey_type",
			"label": __("Survey Type"),
			"fieldtype": "Select",
			"options": "\nAlumni Survey\nEmployer Survey\nStudent Exit Survey\nCourse End Survey\nProgram Exit Survey\nMid-term Feedback"
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

		if (column.fieldname === "avg_rating") {
			if (data.avg_rating >= 4) {
				value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
			} else if (data.avg_rating >= 3) {
				value = `<span style="color: #ffc107;">${value}</span>`;
			} else {
				value = `<span style="color: #dc3545;">${value}</span>`;
			}
		}

		if (column.fieldname === "attainment_level") {
			if (data.attainment_level >= 2) {
				value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
			} else if (data.attainment_level >= 1) {
				value = `<span style="color: #ffc107;">${value}</span>`;
			} else {
				value = `<span style="color: #dc3545;">${value}</span>`;
			}
		}

		if (column.fieldname === "rating_5") {
			value = `<span style="color: #28a745;">${value}</span>`;
		}
		if (column.fieldname === "rating_1_2") {
			value = `<span style="color: #dc3545;">${value}</span>`;
		}

		return value;
	}
};
