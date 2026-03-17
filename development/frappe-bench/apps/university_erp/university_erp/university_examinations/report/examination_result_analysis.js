frappe.query_reports["Examination Result Analysis"] = {
    "filters": [
        {
            "fieldname": "examination",
            "label": __("Examination"),
            "fieldtype": "Link",
            "options": "Online Examination"
        },
        {
            "fieldname": "course",
            "label": __("Course"),
            "fieldtype": "Link",
            "options": "Course"
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
        }
    ]
};
