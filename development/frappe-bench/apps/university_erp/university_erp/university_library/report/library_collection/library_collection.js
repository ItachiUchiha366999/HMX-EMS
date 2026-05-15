// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Library Collection"] = {
    "filters": [
        {
            "fieldname": "category",
            "label": __("Category"),
            "fieldtype": "Link",
            "options": "Library Category"
        },
        {
            "fieldname": "subject",
            "label": __("Subject"),
            "fieldtype": "Link",
            "options": "Library Subject"
        },
        {
            "fieldname": "status",
            "label": __("Article Status"),
            "fieldtype": "Select",
            "options": "\nAvailable\nPartially Available\nAll Issued\nReserved\nLost\nWritten Off"
        }
    ]
};
