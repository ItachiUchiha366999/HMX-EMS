// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Room Availability"] = {
    "filters": [
        {
            "fieldname": "hostel_building",
            "label": __("Hostel Building"),
            "fieldtype": "Link",
            "options": "Hostel Building"
        },
        {
            "fieldname": "hostel_type",
            "label": __("Hostel Type"),
            "fieldtype": "Select",
            "options": "\nBoys\nGirls\nCo-Ed"
        },
        {
            "fieldname": "room_type",
            "label": __("Room Type"),
            "fieldtype": "Select",
            "options": "\nSingle\nDouble\nTriple\nDormitory"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nAvailable\nPartially Occupied\nFully Occupied\nUnder Maintenance"
        },
        {
            "fieldname": "only_available",
            "label": __("Show Only Available"),
            "fieldtype": "Check",
            "default": 1
        }
    ]
};
