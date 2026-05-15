// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Faculty Feedback Report"] = {
    "filters": [
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
        },
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
        },
        {
            "fieldname": "min_rating",
            "label": __("Min Rating"),
            "fieldtype": "Float",
            "default": 0
        }
    ]
};
