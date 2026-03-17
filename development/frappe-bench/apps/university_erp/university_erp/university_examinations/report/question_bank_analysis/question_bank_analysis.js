frappe.query_reports["Question Bank Analysis"] = {
    "filters": [
        {
            "fieldname": "course",
            "label": __("Course"),
            "fieldtype": "Link",
            "options": "Course"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nPending Review\nApproved\nRejected\nRetired"
        }
    ]
};
