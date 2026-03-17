# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate


def get_context(context):
    """Student profile page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.www.student_portal.index import get_current_student

    student_link = get_current_student()
    if not student_link:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    # Get full student document
    student = frappe.get_doc("Student", student_link.name)

    context.no_cache = 1
    context.student = student
    context.active_page = "profile"
    context.guardians = get_guardians(student.name)
    context.academic_info = get_academic_info(student.name)
    context.editable_fields = get_editable_fields()

    return context


def get_guardians(student):
    """Get guardian information"""
    guardians = frappe.db.sql("""
        SELECT
            sg.guardian,
            sg.guardian_name,
            sg.relation,
            g.mobile_number,
            g.email_address
        FROM `tabStudent Guardian` sg
        JOIN `tabGuardian` g ON g.name = sg.guardian
        WHERE sg.parent = %s
    """, student, as_dict=1)

    return guardians


def get_academic_info(student):
    """Get academic information"""
    info = frappe.db.get_value(
        "Student",
        student,
        ["custom_program", "joining_date"],
        as_dict=1
    )

    # Rename for template compatibility
    if info:
        info["program"] = info.pop("custom_program", None)

    # Get program details
    if info.get("program"):
        program_doc = frappe.db.get_value(
            "Program",
            info.program,
            ["program_name", "department"],
            as_dict=1
        )
        info.update(program_doc or {})

    return info


def get_editable_fields():
    """Get list of fields that students can edit"""
    return [
        "student_mobile_number",
        "student_email_id",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "pincode"
    ]


@frappe.whitelist()
def update_student_profile(**kwargs):
    """Update student profile information"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    editable_fields = get_editable_fields()
    student_doc = frappe.get_doc("Student", student.name)

    updated = False
    for field, value in kwargs.items():
        if field in editable_fields:
            student_doc.set(field, value)
            updated = True

    if updated:
        student_doc.save(ignore_permissions=True)
        return {
            "success": True,
            "message": _("Profile updated successfully")
        }
    else:
        return {
            "success": False,
            "message": _("No changes to update")
        }


@frappe.whitelist()
def update_profile_image():
    """Update student profile image"""
    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    files = frappe.request.files
    if 'image' not in files:
        frappe.throw(_("No image file provided"))

    image_file = files['image']

    # Save file
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": image_file.filename,
        "attached_to_doctype": "Student",
        "attached_to_name": student.name,
        "attached_to_field": "image",
        "content": image_file.read(),
        "is_private": 0
    })
    file_doc.save(ignore_permissions=True)

    # Update student
    frappe.db.set_value("Student", student.name, "image", file_doc.file_url)

    return {
        "success": True,
        "image_url": file_doc.file_url,
        "message": _("Profile image updated successfully")
    }
