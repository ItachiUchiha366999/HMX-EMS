// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["CO-PO Mapping Matrix"] = {
	"filters": [
		{
			"fieldname": "program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program"
		},
		{
			"fieldname": "course",
			"label": __("Course"),
			"fieldtype": "Link",
			"options": "Course",
			"get_query": function() {
				let program = frappe.query_report.get_filter_value('program');
				if (program) {
					return {
						query: "university_erp.university_obe.report.co_po_mapping_matrix.co_po_mapping_matrix.get_program_courses",
						filters: { program: program }
					};
				}
				return { filters: {} };
			}
		},
		{
			"fieldname": "academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term"
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Color-code correlation levels
		if (column.fieldname && column.fieldname.startsWith("po") || column.fieldname.startsWith("pso")) {
			if (value == 3) {
				value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
			} else if (value == 2) {
				value = `<span style="color: #ffc107; font-weight: bold;">${value}</span>`;
			} else if (value == 1) {
				value = `<span style="color: #dc3545; font-weight: bold;">${value}</span>`;
			} else if (value == "-") {
				value = `<span style="color: #6c757d;">${value}</span>`;
			}
		}

		return value;
	}
};
