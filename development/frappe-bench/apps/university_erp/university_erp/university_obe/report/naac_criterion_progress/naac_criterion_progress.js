// Copyright (c) 2026, University and contributors
// For license information, please see license.txt

frappe.query_reports["NAAC Criterion Progress"] = {
    "filters": [
        {
            "fieldname": "accreditation_cycle",
            "label": __("Accreditation Cycle"),
            "fieldtype": "Link",
            "options": "Accreditation Cycle",
            "reqd": 0
        },
        {
            "fieldname": "criterion",
            "label": __("Criterion"),
            "fieldtype": "Select",
            "options": "\n1. Curricular Aspects\n2. Teaching-Learning\n3. Research & Extension\n4. Infrastructure\n5. Student Support\n6. Governance\n7. Institutional Values",
            "reqd": 0
        }
    ]
};
