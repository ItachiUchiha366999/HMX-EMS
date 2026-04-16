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


def get_dashboard_data(student_name):
    """Get summary stats for the student dashboard"""
    from frappe.utils import flt

    data = {
        "attendance_percentage": 0.0,
        "pending_fees": 0.0,
        "cgpa": 0.0,
        "total_courses": 0,
    }

    # Attendance percentage
    try:
        total = frappe.db.count("Student Attendance", {"student": student_name})
        present = frappe.db.count(
            "Student Attendance", {"student": student_name, "status": "Present"}
        )
        if total:
            data["attendance_percentage"] = round(flt(present) / flt(total) * 100, 1)
    except Exception:
        pass

    # Pending fees
    try:
        pending = frappe.db.get_value(
            "Fees",
            {"student": student_name, "docstatus": 1, "outstanding_amount": [">", 0]},
            "sum(outstanding_amount)",
        )
        data["pending_fees"] = flt(pending)
    except Exception:
        pass

    # CGPA
    try:
        cgpa = frappe.db.get_value("Student", student_name, "custom_cgpa")
        data["cgpa"] = flt(cgpa)
    except Exception:
        pass

    # Total enrolled courses in current program enrollment
    try:
        enrollment = frappe.db.get_value(
            "Program Enrollment",
            {"student": student_name, "docstatus": 1},
            "name",
            order_by="enrollment_date desc",
        )
        if enrollment:
            data["total_courses"] = frappe.db.count(
                "Program Enrollment Course", {"parent": enrollment}
            )
    except Exception:
        pass

    return data


def get_today_classes(student_name):
    """Get today's timetable slots for the student"""
    from frappe.utils import nowdate, get_weekday

    today = nowdate()
    day_of_week = get_weekday()  # e.g. "Monday"

    classes = []
    try:
        # Get student groups the student belongs to
        student_groups = frappe.db.get_all(
            "Student Group Student",
            filters={"student": student_name},
            pluck="parent",
        )

        if student_groups:
            slots = frappe.db.get_all(
                "Course Schedule",
                filters={
                    "student_group": ["in", student_groups],
                    "schedule_date": today,
                },
                fields=["course", "from_time", "to_time", "room", "instructor"],
                order_by="from_time asc",
                limit=10,
            )

            for slot in slots:
                instructor_name = ""
                if slot.get("instructor"):
                    instructor_name = (
                        frappe.db.get_value("Instructor", slot["instructor"], "instructor_name")
                        or slot["instructor"]
                    )
                classes.append(
                    {
                        "course": slot.get("course", ""),
                        "from_time": str(slot.get("from_time", "")),
                        "to_time": str(slot.get("to_time", "")),
                        "room": slot.get("room", ""),
                        "instructor_name": instructor_name,
                    }
                )
    except Exception:
        pass

    return classes


def get_announcements():
    """Get recent active notice board announcements"""
    from frappe.utils import nowdate

    announcements = []
    try:
        if frappe.db.exists("DocType", "Notice Board"):
            records = frappe.db.get_all(
                "Notice Board",
                filters={
                    "docstatus": 1,
                    "publish_date": ["<=", nowdate()],
                    "expiry_date": [">=", nowdate()],
                },
                fields=["title", "content", "publish_date", "priority"],
                order_by="publish_date desc",
                limit=5,
            )
            announcements = records
    except Exception:
        pass

    return announcements
