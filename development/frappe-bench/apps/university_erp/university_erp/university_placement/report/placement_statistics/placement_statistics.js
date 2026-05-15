// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Placement Statistics"] = {
    "filters": [
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "default": "2026-2027"
        },
        {
            "fieldname": "program",
            "label": __("Program"),
            "fieldtype": "Link",
            "options": "Program"
        }
    ]
};
