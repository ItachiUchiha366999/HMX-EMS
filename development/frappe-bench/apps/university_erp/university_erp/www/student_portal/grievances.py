# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime


def get_context(context):
    """Student grievances page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "grievances"
    context.grievances = get_student_grievances(student.name)
    context.grievance_categories = get_grievance_categories()
    context.grievance_stats = get_grievance_stats(student.name)

    return context


def get_student_grievances(student):
    """Get all grievances submitted by student"""
    try:
        if not frappe.db.exists("DocType", "Student Grievance"):
            return []

        grievances = frappe.db.sql("""
            SELECT
                sg.name,
                sg.category,
                sg.subject,
                sg.description,
                sg.submission_date,
                sg.status,
                sg.priority,
                sg.assigned_to,
                sg.resolution,
                sg.resolved_date
            FROM `tabStudent Grievance` sg
            WHERE sg.student = %s
            ORDER BY sg.submission_date DESC
        """, student, as_dict=1)

        return grievances
    except Exception:
        return []


def get_grievance_categories():
    """Get available grievance categories"""
    return [
        {"value": "Academic", "label": _("Academic Issues")},
        {"value": "Examination", "label": _("Examination Related")},
        {"value": "Fees", "label": _("Fee/Financial Issues")},
        {"value": "Hostel", "label": _("Hostel/Accommodation")},
        {"value": "Transport", "label": _("Transport Issues")},
        {"value": "Library", "label": _("Library Services")},
        {"value": "Infrastructure", "label": _("Infrastructure/Facilities")},
        {"value": "Faculty", "label": _("Faculty Related")},
        {"value": "Administrative", "label": _("Administrative Issues")},
        {"value": "Other", "label": _("Other")}
    ]


def get_grievance_stats(student):
    """Get grievance statistics for student"""
    try:
        if not frappe.db.exists("DocType", "Student Grievance"):
            return {"total": 0, "pending": 0, "in_progress": 0, "resolved": 0, "closed": 0}

        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) as closed
            FROM `tabStudent Grievance`
            WHERE student = %s
        """, student, as_dict=1)

        result = stats[0] if stats else {}

        # Ensure all values are numbers
        return {
            "total": result.get("total") or 0,
            "pending": result.get("pending") or 0,
            "in_progress": result.get("in_progress") or 0,
            "resolved": result.get("resolved") or 0,
            "closed": result.get("closed") or 0
        }
    except Exception:
        return {"total": 0, "pending": 0, "in_progress": 0, "resolved": 0, "closed": 0}


@frappe.whitelist()
def submit_grievance(category, subject, description, priority="Medium"):
    """Submit a new grievance"""
    try:
        from university_erp.www.student_portal.index import get_current_student

        student = get_current_student()
        if not student:
            frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

        if not frappe.db.exists("DocType", "Student Grievance"):
            frappe.throw(_("Grievance system not configured"))

        grievance = frappe.get_doc({
            "doctype": "Student Grievance",
            "student": student.name,
            "category": category,
            "subject": subject,
            "description": description,
            "priority": priority,
            "submission_date": nowdate(),
            "status": "Pending"
        })
        grievance.insert()

        return {
            "success": True,
            "grievance_id": grievance.name,
            "message": _("Grievance submitted successfully. Your grievance ID is {0}").format(grievance.name)
        }
    except frappe.PermissionError:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def add_grievance_comment(grievance, comment):
    """Add a comment to an existing grievance"""
    try:
        from university_erp.www.student_portal.index import get_current_student

        student = get_current_student()
        if not student:
            frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

        if not frappe.db.exists("DocType", "Student Grievance"):
            frappe.throw(_("Grievance system not configured"))

        # Verify ownership
        grievance_doc = frappe.get_doc("Student Grievance", grievance)
        if grievance_doc.student != student.name:
            frappe.throw(_("You can only comment on your own grievances"), frappe.PermissionError)

        # Add comment
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": "Student Grievance",
            "reference_name": grievance,
            "content": comment
        }).insert(ignore_permissions=True)

        return {"success": True}
    except frappe.PermissionError:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
