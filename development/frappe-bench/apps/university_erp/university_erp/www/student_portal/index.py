# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import json
import os

import frappe
from frappe import _


def get_context(context):
    """SPA shell for the Vue 3 Student Portal"""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to=/student_portal{frappe.local.request.path.replace('/student_portal', '') or '/'}"
        )
        raise frappe.Redirect

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.show_sidebar = False

    # Read Vite manifest to get hashed asset filenames
    manifest = get_vite_manifest()
    context.vue_js = manifest.get("js", "")
    context.vue_css = manifest.get("css", "")

    return context


def get_vite_manifest():
    """Read the Vite build manifest to get hashed filenames"""
    manifest_path = frappe.get_app_path(
        "university_erp", "public", "student-portal-spa", ".vite", "manifest.json"
    )

    if not os.path.exists(manifest_path):
        # Fallback: try older manifest location
        manifest_path = frappe.get_app_path(
            "university_erp", "public", "student-portal-spa", "manifest.json"
        )

    if not os.path.exists(manifest_path):
        frappe.log_error("Vite manifest not found. Run npm run build in student-portal-vue/")
        return {"js": "", "css": ""}

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Find the entry point (index.html)
    entry = manifest.get("index.html", {})
    base = "/assets/university_erp/student-portal-spa/"

    result = {
        "js": base + entry.get("file", "") if entry.get("file") else "",
        "css": "",
    }

    # Collect CSS files
    css_files = entry.get("css", [])
    if css_files:
        result["css"] = base + css_files[0]

    return result


def get_current_student():
    """Get current logged in student"""
    user = frappe.session.user
    student = frappe.db.get_value(
        "Student",
        {"user": user},
        ["name", "student_name", "image", "custom_cgpa"],
        as_dict=1,
    )

    if student:
        program = frappe.db.get_value(
            "Program Enrollment",
            {"student": student.name, "docstatus": 1},
            "program",
            order_by="enrollment_date desc",
        )
        student.program = program

    return student
