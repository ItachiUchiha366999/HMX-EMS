// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Overdue Books"] = {
    "filters": [
        {
            "fieldname": "member_type",
            "label": __("Member Type"),
            "fieldtype": "Select",
            "options": "\nStudent\nFaculty\nStaff\nExternal"
        },
        {
            "fieldname": "category",
            "label": __("Category"),
            "fieldtype": "Link",
            "options": "Library Category"
        },
        {
            "fieldname": "min_overdue_days",
            "label": __("Min Overdue Days"),
            "fieldtype": "Int",
            "default": 1
        },
        {
            "fieldname": "max_overdue_days",
            "label": __("Max Overdue Days"),
            "fieldtype": "Int"
        }
    ]
};
