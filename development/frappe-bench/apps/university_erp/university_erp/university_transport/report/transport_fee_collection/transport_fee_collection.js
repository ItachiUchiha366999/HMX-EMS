// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Transport Fee Collection"] = {
    "filters": [
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "default": "2026-2027"
        },
        {
            "fieldname": "route",
            "label": __("Route"),
            "fieldtype": "Link",
            "options": "Transport Route"
        },
        {
            "fieldname": "program",
            "label": __("Program"),
            "fieldtype": "Link",
            "options": "Program"
        },
        {
            "fieldname": "outstanding_only",
            "label": __("Show Routes With Outstanding Only"),
            "fieldtype": "Check",
            "default": 0
        }
    ]
};
