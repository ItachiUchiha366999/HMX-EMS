// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Program Wise Placement"] = {
    "filters": [
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "default": "2026-2027"
        }
    ]
};
