// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Faculty Feedback Report"] = {
    "filters": [
        {
            "fieldname": "academic_term",
            "label": __("Academic Term"),
            "fieldtype": "Link",
            "options": "Academic Term"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname": "instructor",
            "label": __("Faculty"),
            "fieldtype": "Link",
            "options": "Instructor"
        }
    ]
};
