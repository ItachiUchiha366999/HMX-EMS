// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Student Performance Analysis"] = {
    "filters": [
        {
            "fieldname": "program",
            "label": __("Program"),
            "fieldtype": "Link",
            "options": "Program",
            "width": 200
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 200
        },
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "width": 150
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "performance_grade") {
            if (data.performance_grade == "Excellent") {
                value = "<span class='indicator-pill green'>" + value + "</span>";
            } else if (data.performance_grade == "Good") {
                value = "<span class='indicator-pill blue'>" + value + "</span>";
            } else if (data.performance_grade == "Average") {
                value = "<span class='indicator-pill yellow'>" + value + "</span>";
            } else if (data.performance_grade == "Below Average" || data.performance_grade == "Poor") {
                value = "<span class='indicator-pill red'>" + value + "</span>";
            }
        }

        if (column.fieldname == "cgpa") {
            if (data.cgpa >= 8.5) {
                value = "<span style='color: green; font-weight: bold;'>" + value + "</span>";
            } else if (data.cgpa >= 7.0) {
                value = "<span style='color: blue;'>" + value + "</span>";
            } else if (data.cgpa < 5.0) {
                value = "<span style='color: red;'>" + value + "</span>";
            }
        }

        if (column.fieldname == "attendance_percentage") {
            if (data.attendance_percentage >= 85) {
                value = "<span style='color: green;'>" + value + "</span>";
            } else if (data.attendance_percentage < 75) {
                value = "<span style='color: red;'>" + value + "</span>";
            }
        }

        return value;
    }
};
