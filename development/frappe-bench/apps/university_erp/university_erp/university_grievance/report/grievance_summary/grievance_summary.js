// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["Grievance Summary"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "category",
            "label": __("Category"),
            "fieldtype": "Select",
            "options": "\nAcademic\nAdministrative\nFinancial\nInfrastructure\nHostel\nTransport\nLibrary\nExamination\nFaculty Related\nRagging\nHarassment\nDiscrimination\nOther"
        },
        {
            "fieldname": "grievance_type",
            "label": __("Grievance Type"),
            "fieldtype": "Link",
            "options": "Grievance Type"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nSubmitted\nUnder Review\nAssigned\nIn Progress\nPending Information\nEscalated\nResolved\nClosed\nReopened"
        }
    ]
};
