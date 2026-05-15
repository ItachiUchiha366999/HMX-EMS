// Copyright (c) 2026, University ERP and contributors
// For license information, please see license.txt

frappe.query_reports["Member Borrowing History"] = {
    "filters": [
        {
            "fieldname": "member",
            "label": __("Member"),
            "fieldtype": "Link",
            "options": "Library Member",
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "transaction_type",
            "label": __("Transaction Type"),
            "fieldtype": "Select",
            "options": "\nIssue\nReturn\nRenew"
        }
    ]
};
