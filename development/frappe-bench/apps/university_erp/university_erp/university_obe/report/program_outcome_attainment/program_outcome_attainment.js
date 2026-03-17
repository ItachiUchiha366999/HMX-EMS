// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Program Outcome Attainment"] = {
    "filters": [
        {
            "fieldname": "program",
            "label": __("Program"),
            "fieldtype": "Link",
            "options": "Program",
            "reqd": 0
        },
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "reqd": 0
        }
    ]
};
