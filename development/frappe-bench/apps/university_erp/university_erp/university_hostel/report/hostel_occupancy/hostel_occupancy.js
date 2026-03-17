// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Hostel Occupancy"] = {
    "filters": [
        {
            "fieldname": "hostel_type",
            "label": __("Hostel Type"),
            "fieldtype": "Select",
            "options": "\nBoys\nGirls\nCo-Ed"
        },
        {
            "fieldname": "building",
            "label": __("Building"),
            "fieldtype": "Link",
            "options": "Hostel Building"
        }
    ]
};
