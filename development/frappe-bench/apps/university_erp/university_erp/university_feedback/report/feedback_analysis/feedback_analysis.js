// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Feedback Analysis"] = {
    "filters": [
        {
            "fieldname": "feedback_form",
            "label": __("Feedback Form"),
            "fieldtype": "Link",
            "options": "Feedback Form"
        },
        {
            "fieldname": "form_type",
            "label": __("Form Type"),
            "fieldtype": "Select",
            "options": "\nCourse Feedback\nFaculty Feedback\nGeneral Feedback\nEvent Feedback\nInfrastructure Feedback"
        },
        {
            "fieldname": "academic_term",
            "label": __("Academic Term"),
            "fieldtype": "Link",
            "options": "Academic Term"
        },
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
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "avg_score" || column.fieldname === "response_rate") {
            if (data && data[column.fieldname] >= 80) {
                value = "<span style='color: green; font-weight: bold;'>" + value + "</span>";
            } else if (data && data[column.fieldname] >= 60) {
                value = "<span style='color: orange;'>" + value + "</span>";
            } else if (data && data[column.fieldname] < 60) {
                value = "<span style='color: red;'>" + value + "</span>";
            }
        }

        if (column.fieldname === "nps") {
            if (data && data[column.fieldname] >= 50) {
                value = "<span style='color: green; font-weight: bold;'>" + value + "</span>";
            } else if (data && data[column.fieldname] >= 0) {
                value = "<span style='color: orange;'>" + value + "</span>";
            } else if (data && data[column.fieldname] < 0) {
                value = "<span style='color: red;'>" + value + "</span>";
            }
        }

        return value;
    }
};
