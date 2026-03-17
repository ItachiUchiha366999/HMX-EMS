"""
Student Grievance Portal Page Controller

Allows students to submit grievances and track their status.
"""
import frappe
from frappe import _
from frappe.utils import getdate, now_datetime


def get_context(context):
    """Get context for grievance portal page"""
    context.no_cache = 1

    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/student-portal/grievances"
        raise frappe.Redirect

    # Get student linked to current user
    student = get_student_for_user()
    if not student:
        context.error = _("No student record found for your account.")
        context.student = None
        return context

    context.student = student

    # Get grievance types for the form
    context.grievance_types = frappe.get_all(
        "Grievance Type",
        filters={"is_active": 1},
        fields=["name", "grievance_type_name", "category", "sla_days", "description"],
        order_by="category, grievance_type_name"
    )

    # Group types by category
    context.grievance_categories = {}
    for gtype in context.grievance_types:
        category = gtype.category or "Other"
        if category not in context.grievance_categories:
            context.grievance_categories[category] = []
        context.grievance_categories[category].append(gtype)

    # Get student's grievances
    grievances = frappe.get_all(
        "Grievance",
        filters={"complainant": frappe.session.user},
        fields=[
            "name", "subject", "category", "grievance_type", "status",
            "priority", "creation", "expected_resolution_date", "resolution_date",
            "is_anonymous", "days_open", "sla_status"
        ],
        order_by="creation desc"
    )

    context.grievances = grievances

    # Calculate statistics
    context.total_grievances = len(grievances)
    context.pending_grievances = len([g for g in grievances if g.status in ["Submitted", "Under Review", "Assigned", "In Progress", "Pending Information"]])
    context.resolved_grievances = len([g for g in grievances if g.status in ["Resolved", "Closed"]])

    return context


def get_student_for_user():
    """Get student record linked to current user"""
    # Try by user link
    student_name = frappe.db.get_value("Student", {"user": frappe.session.user})

    # Try by email
    if not student_name:
        student_name = frappe.db.get_value("Student", {"student_email_id": frappe.session.user})

    if student_name:
        return frappe.get_doc("Student", student_name)

    return None


@frappe.whitelist()
def submit_grievance(subject, description, category, grievance_type=None, is_anonymous=0, attachments=None):
    """Submit a new grievance from student portal"""
    try:
        # Validate inputs
        if not subject or not description or not category:
            return {"success": False, "message": _("Please fill all required fields.")}

        # Create grievance document
        grievance = frappe.new_doc("Grievance")
        grievance.complainant = frappe.session.user
        grievance.complainant_type = "Student"
        grievance.subject = subject
        grievance.description = description
        grievance.category = category
        grievance.grievance_type = grievance_type
        grievance.is_anonymous = 1 if is_anonymous else 0
        grievance.submission_date = getdate()
        grievance.status = "Submitted"

        # Get complainant name
        student = get_student_for_user()
        if student:
            grievance.complainant_name = student.student_name
            grievance.contact_email = student.student_email_id
            grievance.contact_phone = student.student_mobile_number

        # Add attachments if any
        if attachments:
            for att in attachments:
                grievance.append("attachments", {
                    "file_name": att.get("file_name"),
                    "file_url": att.get("file_url"),
                    "description": att.get("description", "")
                })

        grievance.insert(ignore_permissions=True)
        grievance.submit()

        return {
            "success": True,
            "message": _("Your grievance has been submitted successfully."),
            "grievance_id": grievance.name
        }

    except Exception as e:
        frappe.log_error(f"Grievance submission error: {str(e)}", "Grievance Portal")
        return {"success": False, "message": _("An error occurred while submitting your grievance.")}


@frappe.whitelist()
def get_grievance_details(grievance_id):
    """Get details of a specific grievance"""
    try:
        # Check if user owns this grievance
        grievance = frappe.get_doc("Grievance", grievance_id)

        if grievance.complainant != frappe.session.user:
            return {"success": False, "message": _("You do not have access to this grievance.")}

        # Get communications (visible to complainant)
        communications = []
        for comm in grievance.communications:
            if comm.communication_type in ["Response", "System"]:
                communications.append({
                    "type": comm.communication_type,
                    "message": comm.message,
                    "timestamp": comm.timestamp,
                    "sent_by": comm.sent_by if not grievance.is_anonymous else "System"
                })

        return {
            "success": True,
            "grievance": {
                "name": grievance.name,
                "subject": grievance.subject,
                "description": grievance.description,
                "category": grievance.category,
                "grievance_type": grievance.grievance_type,
                "status": grievance.status,
                "priority": grievance.priority,
                "creation": grievance.creation,
                "expected_resolution_date": grievance.expected_resolution_date,
                "resolution_date": grievance.resolution_date,
                "resolution_summary": grievance.resolution_summary,
                "days_open": grievance.days_open,
                "sla_status": grievance.sla_status,
                "communications": communications
            }
        }

    except frappe.DoesNotExistError:
        return {"success": False, "message": _("Grievance not found.")}
    except Exception as e:
        frappe.log_error(f"Grievance details error: {str(e)}", "Grievance Portal")
        return {"success": False, "message": _("An error occurred.")}


@frappe.whitelist()
def add_grievance_response(grievance_id, message):
    """Add a response to an existing grievance"""
    try:
        grievance = frappe.get_doc("Grievance", grievance_id)

        if grievance.complainant != frappe.session.user:
            return {"success": False, "message": _("You do not have access to this grievance.")}

        if grievance.status in ["Closed", "Resolved"]:
            return {"success": False, "message": _("This grievance is already closed.")}

        # Add communication
        grievance.append("communications", {
            "communication_type": "Response",
            "message": message,
            "timestamp": now_datetime(),
            "sent_by": frappe.session.user
        })

        # If status is "Pending Information", move to "In Progress"
        if grievance.status == "Pending Information":
            grievance.status = "In Progress"

        grievance.save(ignore_permissions=True)

        return {
            "success": True,
            "message": _("Your response has been added.")
        }

    except Exception as e:
        frappe.log_error(f"Grievance response error: {str(e)}", "Grievance Portal")
        return {"success": False, "message": _("An error occurred.")}
