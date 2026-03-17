frappe.query_reports["Internal Assessment Summary"] = {
    "filters": [
        {
            "fieldname": "course",
            "label": __("Course"),
            "fieldtype": "Link",
            "options": "Course",
            "reqd": 1
        },
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "reqd": 1
        },
        {
            "fieldname": "academic_term",
            "label": __("Academic Term"),
            "fieldtype": "Link",
            "options": "Academic Term"
        },
        {
            "fieldname": "grading_scale",
            "label": __("Grading Scale"),
            "fieldtype": "Link",
            "options": "Grading Scale"
        }
    ]
};
