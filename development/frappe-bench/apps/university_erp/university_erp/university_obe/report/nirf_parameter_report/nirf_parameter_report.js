// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["NIRF Parameter Report"] = {
    "filters": [
        {
            "fieldname": "ranking_year",
            "label": __("Ranking Year"),
            "fieldtype": "Data",
            "reqd": 0
        },
        {
            "fieldname": "category",
            "label": __("Category"),
            "fieldtype": "Select",
            "options": "\nOverall\nUniversity\nEngineering\nManagement\nPharmacy\nMedical\nLaw",
            "reqd": 0
        }
    ]
};
