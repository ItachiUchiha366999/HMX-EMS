frappe.query_reports["Internal Assessment Summary"] = {
    "filters": [
        {
            "fieldname": "academic_year",
            "label": __("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "default": "2026-2027",
            "reqd": 1
        },
        {
            "fieldname": "academic_term",
            "label": __("Academic Term"),
            "fieldtype": "Link",
            "options": "Academic Term",
            "default": "2026-2027 (Semester 2)"
        },
        {
            "fieldname": "course",
            "label": __("Course"),
            "fieldtype": "Link",
            "options": "Course",
            "default": "Operations Management"
        },
        {
            "fieldname": "student_group",
            "label": __("Student Group"),
            "fieldtype": "Link",
            "options": "Student Group"
        }
    ]
};
