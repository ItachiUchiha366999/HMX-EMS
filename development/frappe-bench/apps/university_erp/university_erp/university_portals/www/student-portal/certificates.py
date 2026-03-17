# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate


def get_context(context):
    """Student certificates page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.certificate_requests = get_certificate_requests(student.name)
    context.available_certificates = get_available_certificate_types()
    context.issued_certificates = get_issued_certificates(student.name)

    return context


def get_certificate_requests(student):
    """Get all certificate requests by student"""
    requests = frappe.db.sql("""
        SELECT
            cr.name,
            cr.certificate_template,
            ct.certificate_name,
            cr.request_date,
            cr.status,
            cr.purpose,
            cr.certificate_number,
            cr.issue_date,
            cr.remarks
        FROM `tabCertificate Request` cr
        JOIN `tabCertificate Template` ct ON ct.name = cr.certificate_template
        WHERE cr.student = %s
        ORDER BY cr.request_date DESC
    """, student, as_dict=1)

    return requests


def get_available_certificate_types():
    """Get list of available certificate types"""
    templates = frappe.db.get_all(
        "Certificate Template",
        filters={"is_active": 1, "available_for_student_request": 1},
        fields=["name", "certificate_name", "description", "processing_days", "fee_amount"]
    )

    return templates


def get_issued_certificates(student):
    """Get list of issued certificates that can be downloaded"""
    issued = frappe.db.sql("""
        SELECT
            cr.name,
            cr.certificate_template,
            ct.certificate_name,
            cr.certificate_number,
            cr.issue_date,
            cr.certificate_file
        FROM `tabCertificate Request` cr
        JOIN `tabCertificate Template` ct ON ct.name = cr.certificate_template
        WHERE cr.student = %s
        AND cr.status IN ('Generated', 'Issued')
        ORDER BY cr.issue_date DESC
    """, student, as_dict=1)

    return issued


@frappe.whitelist()
def request_certificate(certificate_template, purpose, copies=1):
    """Submit a new certificate request"""
    from university_erp.university_portals.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    # Check if template is valid
    template = frappe.get_doc("Certificate Template", certificate_template)
    if not template.is_active or not template.available_for_student_request:
        frappe.throw(_("This certificate type is not available for request"))

    # Create certificate request
    request = frappe.get_doc({
        "doctype": "Certificate Request",
        "student": student.name,
        "certificate_template": certificate_template,
        "request_date": nowdate(),
        "purpose": purpose,
        "copies_required": copies,
        "status": "Pending"
    })
    request.insert()

    return {
        "success": True,
        "request_id": request.name,
        "message": _("Certificate request submitted successfully")
    }
