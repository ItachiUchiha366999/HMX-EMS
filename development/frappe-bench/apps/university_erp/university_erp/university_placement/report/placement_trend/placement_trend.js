// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Placement Trend"] = {
    "filters": [
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "default": "2026-2027"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -6)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), 3)
        },
        {
            "fieldname": "group_by",
            "label": __("Group By"),
            "fieldtype": "Select",
            "options": "Month\nQuarter\nYear",
            "default": "Month"
        }
    ]
};
