"""Bootstrap the public admission Web Form at /admission-apply.

Idempotent — drops any existing Web Form named 'apply-for-admission' and
recreates it with the canonical 21-field layout. Bound to Student Applicant.

Usage:
    bench --site <site> execute university_erp.setup.create_admission_webform.run
"""
import frappe


WF_NAME = "apply-for-admission"
ROUTE = "admission-apply"


def run():
    if frappe.db.exists("Web Form", WF_NAME):
        frappe.delete_doc("Web Form", WF_NAME, force=True, ignore_permissions=True)
        frappe.db.commit()

    wf = frappe.get_doc({
        "doctype": "Web Form",
        "name": WF_NAME,
        "title": "Apply for Admission",
        "route": ROUTE,
        "doc_type": "Student Applicant",
        "module": "University Admissions",
        "is_standard": 0,
        "published": 1,
        "login_required": 0,
        "allow_multiple": 1,
        "allow_edit": 0,
        "allow_delete": 0,
        "allow_print": 0,
        "show_sidebar": 0,
        "anonymous": 1,
        "apply_document_permissions": 0,
        "introduction_text": (
            "<h3>Apply for Admission — AY 2026-2027</h3>"
            "<p>Fill in the details below. After submission, the Registrar's office will "
            "review your documents and update you on next steps via email.</p>"
        ),
        "success_message": (
            "<h4>Application received ✓</h4>"
            "<p>Thank you. Your application has been submitted. You will receive an "
            "email when the Registrar's office moves it forward.</p>"
        ),
        "button_label": "Submit Application",
        "web_form_fields": [
            {"fieldname": "first_name", "label": "First Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "middle_name", "label": "Middle Name", "fieldtype": "Data", "reqd": 0},
            {"fieldname": "last_name", "label": "Last Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "student_email_id", "label": "Email", "fieldtype": "Data", "options": "Email", "reqd": 1},
            {"fieldname": "student_mobile_number", "label": "Mobile Number", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "date_of_birth", "label": "Date of Birth", "fieldtype": "Date", "reqd": 1},
            {"fieldname": "gender", "label": "Gender", "fieldtype": "Link", "options": "Gender", "reqd": 1},
            {"fieldname": "custom_admission_cycle", "label": "Admission Cycle", "fieldtype": "Link", "options": "Admission Cycle", "reqd": 1},
            {"fieldname": "academic_year", "label": "Academic Year", "fieldtype": "Link", "options": "Academic Year", "reqd": 1},
            {"fieldname": "program", "label": "Program (primary preference)", "fieldtype": "Link", "options": "Program", "reqd": 1},
            {"fieldname": "custom_program_preference_1", "label": "Program Preference 1", "fieldtype": "Link", "options": "Program", "reqd": 1},
            {"fieldname": "custom_program_preference_2", "label": "Program Preference 2", "fieldtype": "Link", "options": "Program", "reqd": 0},
            {"fieldname": "custom_program_preference_3", "label": "Program Preference 3", "fieldtype": "Link", "options": "Program", "reqd": 0},
            {"fieldname": "custom_category", "label": "Category", "fieldtype": "Select", "options": "General\nOBC\nSC\nST\nEWS", "reqd": 1, "default": "General"},
            {"fieldname": "custom_percentage_10th", "label": "10th Standard %", "fieldtype": "Float", "reqd": 1},
            {"fieldname": "custom_percentage_12th", "label": "12th Standard %", "fieldtype": "Float", "reqd": 1},
            {"fieldname": "custom_entrance_exam_score", "label": "Entrance Exam Score", "fieldtype": "Float", "reqd": 1},
            {"fieldname": "address_line_1", "label": "Address Line 1", "fieldtype": "Data", "reqd": 0},
            {"fieldname": "city", "label": "City", "fieldtype": "Data", "reqd": 0},
            {"fieldname": "state", "label": "State", "fieldtype": "Data", "reqd": 0},
            {"fieldname": "pincode", "label": "Pincode", "fieldtype": "Data", "reqd": 0},
        ],
    })
    wf.flags.ignore_permissions = True
    wf.flags.ignore_mandatory = True
    wf.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"Created Web Form {wf.name} at /{wf.route}")
