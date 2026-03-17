// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Route Wise Students"] = {
    "filters": [
        {
            "fieldname": "route",
            "label": __("Route"),
            "fieldtype": "Link",
            "options": "Transport Route"
        },
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year"
        }
    ]
};
