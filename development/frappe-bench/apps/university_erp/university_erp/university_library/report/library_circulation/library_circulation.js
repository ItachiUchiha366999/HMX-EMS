// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Library Circulation"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": "2026-02-01",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": "2026-05-01",
            "reqd": 1
        },
        {
            "fieldname": "member_type",
            "label": __("Member Type"),
            "fieldtype": "Select",
            "options": "\nStudent\nFaculty\nStaff\nExternal"
        },
        {
            "fieldname": "category",
            "label": __("Article Category"),
            "fieldtype": "Link",
            "options": "Library Category"
        },
        {
            "fieldname": "transaction_type",
            "label": __("Transaction Type"),
            "fieldtype": "Select",
            "options": "\nIssue\nReturn\nRenew"
        }
    ]
};
