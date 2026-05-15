// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Hostel Attendance Report"] = {
    "filters": [
        {
            "fieldname": "hostel_building",
            "label": __("Hostel Building"),
            "fieldtype": "Link",
            "options": "Hostel Building"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": "2026-04-01",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": "2026-05-01",
            "reqd": 1
        },
        {
            "fieldname": "student",
            "label": __("Student"),
            "fieldtype": "Link",
            "options": "Student"
        }
    ]
};
