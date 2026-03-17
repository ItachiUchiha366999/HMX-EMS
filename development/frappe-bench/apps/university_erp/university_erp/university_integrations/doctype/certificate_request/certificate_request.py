# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, get_url


class CertificateRequest(Document):
    def validate(self):
        self.set_student_program()
        self.set_verification_url()

    def set_student_program(self):
        """Set program from student if not set"""
        if self.student and not self.program:
            # Try to get current program enrollment
            enrollment = frappe.db.get_value(
                "Program Enrollment",
                {"student": self.student, "docstatus": 1},
                "program",
                order_by="enrollment_date desc"
            )
            if enrollment:
                self.program = enrollment

    def set_verification_url(self):
        """Set verification URL if verification code exists"""
        if self.verification_code:
            base_url = get_url()
            self.verification_url = f"{base_url}/api/method/university_erp.university_integrations.certificate_generator.verify_certificate?code={self.verification_code}"

    def on_submit(self):
        """Generate certificate on submit if approved"""
        template = frappe.get_doc("Certificate Template", self.certificate_template)

        # Check if approval required
        if template.requires_approval and self.status != "Approved":
            frappe.throw(_("Certificate requires approval before submission"))

        # Auto-approve if no approval required
        if not template.requires_approval and self.status == "Pending":
            self.status = "Approved"
            self.approved_by = frappe.session.user
            self.approval_date = today()

    @frappe.whitelist()
    def generate_certificate(self):
        """Generate the certificate PDF"""
        from university_erp.university_integrations.certificate_generator import CertificateGenerator

        generator = CertificateGenerator(self)
        return generator.generate()

    @frappe.whitelist()
    def approve(self):
        """Approve the certificate request"""
        if self.status != "Pending":
            frappe.throw(_("Only pending requests can be approved"))

        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = today()
        self.save()

        return {"success": True}

    @frappe.whitelist()
    def reject(self, reason=None):
        """Reject the certificate request"""
        if self.status != "Pending":
            frappe.throw(_("Only pending requests can be rejected"))

        self.status = "Rejected"
        self.rejection_reason = reason
        self.save()

        return {"success": True}

    @frappe.whitelist()
    def issue_to_digilocker(self):
        """Issue certificate to DigiLocker"""
        if self.status != "Generated":
            frappe.throw(_("Certificate must be generated first"))

        from university_erp.university_integrations.digilocker_integration import issue_certificate_request_to_digilocker

        result = issue_certificate_request_to_digilocker(self.name)

        if result.get("success"):
            self.digilocker_issued = 1
            self.digilocker_uri = result.get("uri")
            self.save()

        return result


@frappe.whitelist()
def get_pending_approvals():
    """Get all pending certificate requests requiring approval"""
    return frappe.get_all(
        "Certificate Request",
        filters={"status": "Pending", "docstatus": 0},
        fields=["name", "student", "student_name", "certificate_type", "request_date", "purpose"],
        order_by="request_date"
    )


@frappe.whitelist()
def bulk_approve(requests):
    """Approve multiple certificate requests"""
    if isinstance(requests, str):
        requests = frappe.parse_json(requests)

    results = []
    for request_name in requests:
        try:
            request = frappe.get_doc("Certificate Request", request_name)
            request.approve()
            results.append({"name": request_name, "success": True})
        except Exception as e:
            results.append({"name": request_name, "success": False, "error": str(e)})

    return results
