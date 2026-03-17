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
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
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
