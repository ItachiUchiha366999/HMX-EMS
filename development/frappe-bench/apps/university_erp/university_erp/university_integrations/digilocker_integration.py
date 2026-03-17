# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
DigiLocker Integration Module
India's National Digital Locker System for document issuance
"""

import frappe
from frappe import _
from frappe.utils import now_datetime
import requests
import hashlib
import hmac
import base64
import json


class DigiLockerClient:
    """DigiLocker API integration client"""

    def __init__(self):
        self.settings = frappe.get_single("DigiLocker Settings")

        if not self.settings.enabled:
            frappe.throw(_("DigiLocker integration is not enabled"))

        self.base_url = (
            "https://api.digitallocker.gov.in"
            if self.settings.environment == "Production"
            else "https://apisetu.gov.in/stg"
        )

        self.client_id = self.settings.client_id
        self.client_secret = self.settings.get_password("client_secret")
        self.hmac_key = self.settings.get_password("hmac_key")

    def _generate_hmac(self, data):
        """Generate HMAC signature for request"""
        if isinstance(data, dict):
            message = json.dumps(data, separators=(',', ':'), sort_keys=True)
        else:
            message = str(data)

        signature = hmac.new(
            self.hmac_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _get_headers(self, hmac_signature=None):
        """Get API request headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if hmac_signature:
            headers["x-digilocker-hmac"] = hmac_signature
        if self.client_id:
            headers["x-client-id"] = self.client_id

        return headers

    def issue_document(self, doc_type, doc_data, student):
        """Issue document to DigiLocker"""
        try:
            # Get document type configuration
            doc_config = self.settings.get_document_type_config(doc_type)

            if not doc_config:
                return {
                    "success": False,
                    "error": f"Document type {doc_type} not configured"
                }

            student_doc = frappe.get_doc("Student", student)

            # Get Aadhaar number
            aadhaar = getattr(student_doc, 'custom_aadhaar_number', None)
            if not aadhaar:
                return {
                    "success": False,
                    "error": "Student Aadhaar number not found"
                }

            # Prepare document data
            payload = {
                "orgId": self.settings.org_id,
                "issuerId": self.settings.issuer_id,
                "docType": doc_config.doc_type_code,
                "docData": doc_data,
                "recipientId": aadhaar,
                "issueDate": frappe.utils.today(),
                "docName": f"{doc_type} - {student_doc.student_name}"
            }

            hmac_signature = self._generate_hmac(payload)

            response = requests.post(
                f"{self.base_url}/issuedoc/{self.settings.api_version}/issue",
                headers=self._get_headers(hmac_signature),
                json=payload,
                timeout=30
            )

            response_data = response.json() if response.text else {}

            if response.status_code == 200:
                # Log issued document
                issued_doc = frappe.get_doc({
                    "doctype": "DigiLocker Issued Document",
                    "student": student,
                    "document_type": doc_type,
                    "document_uri": response_data.get("uri"),
                    "aadhaar_number": aadhaar[-4:].rjust(12, '*'),  # Mask Aadhaar
                    "status": "Issued",
                    "issued_date": now_datetime(),
                    "issued_by": frappe.session.user,
                    "api_response": json.dumps(response_data)
                })
                issued_doc.insert(ignore_permissions=True)
                frappe.db.commit()

                return {
                    "success": True,
                    "uri": response_data.get("uri"),
                    "issued_document": issued_doc.name
                }
            else:
                # Log failed attempt
                frappe.get_doc({
                    "doctype": "DigiLocker Issued Document",
                    "student": student,
                    "document_type": doc_type,
                    "aadhaar_number": aadhaar[-4:].rjust(12, '*'),
                    "status": "Failed",
                    "api_response": json.dumps(response_data),
                    "error_message": response_data.get("message", response.text)
                }).insert(ignore_permissions=True)
                frappe.db.commit()

                return {
                    "success": False,
                    "error": response_data.get("message", "Document issuance failed")
                }

        except Exception as e:
            frappe.log_error(f"DigiLocker issue failed: {str(e)}", "DigiLocker Integration")
            return {"success": False, "error": str(e)}

    def verify_document(self, document_uri):
        """Verify document from DigiLocker"""
        try:
            payload = {"uri": document_uri}
            hmac_signature = self._generate_hmac(payload)

            response = requests.post(
                f"{self.base_url}/docverify/{self.settings.api_version}/verify",
                headers=self._get_headers(hmac_signature),
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "verified": result.get("verified", False),
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }

        except Exception as e:
            frappe.log_error(f"DigiLocker verify failed: {str(e)}", "DigiLocker Integration")
            return {"success": False, "error": str(e)}

    def pull_document(self, document_uri):
        """Pull document from DigiLocker"""
        try:
            payload = {"uri": document_uri}
            hmac_signature = self._generate_hmac(payload)

            response = requests.post(
                f"{self.base_url}/pulluri/{self.settings.api_version}/pull",
                headers=self._get_headers(hmac_signature),
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "document": response.content,
                    "content_type": response.headers.get("Content-Type")
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }

        except Exception as e:
            frappe.log_error(f"DigiLocker pull failed: {str(e)}", "DigiLocker Integration")
            return {"success": False, "error": str(e)}


# API Endpoints

@frappe.whitelist()
def issue_certificate_to_digilocker(certificate_type, student, certificate_data=None):
    """Issue certificate to student's DigiLocker"""
    client = DigiLockerClient()

    if certificate_data and isinstance(certificate_data, str):
        certificate_data = json.loads(certificate_data)

    # If no certificate data provided, prepare basic data
    if not certificate_data:
        student_doc = frappe.get_doc("Student", student)
        certificate_data = {
            "studentName": student_doc.student_name,
            "studentId": student,
            "certificateType": certificate_type,
            "issueDate": frappe.utils.today()
        }

    return client.issue_document(certificate_type, certificate_data, student)


@frappe.whitelist()
def verify_digilocker_document(document_uri):
    """Verify a DigiLocker document"""
    client = DigiLockerClient()
    return client.verify_document(document_uri)


@frappe.whitelist()
def pull_digilocker_document(document_uri):
    """Pull document content from DigiLocker"""
    client = DigiLockerClient()
    return client.pull_document(document_uri)


@frappe.whitelist(allow_guest=True)
def digilocker_callback():
    """Handle DigiLocker callbacks"""
    try:
        data = dict(frappe.form_dict)

        # Log callback
        frappe.log_error(
            f"DigiLocker callback received: {json.dumps(data)}",
            "DigiLocker Callback"
        )

        # Process based on callback type
        callback_type = data.get("type")

        if callback_type == "document_issued":
            # Update issued document status
            uri = data.get("uri")
            if uri:
                issued_doc = frappe.db.get_value(
                    "DigiLocker Issued Document",
                    {"document_uri": uri},
                    "name"
                )
                if issued_doc:
                    frappe.db.set_value(
                        "DigiLocker Issued Document", issued_doc,
                        "status", "Issued"
                    )

        return {"status": "ok"}

    except Exception as e:
        frappe.log_error(f"DigiLocker callback failed: {str(e)}", "DigiLocker Integration")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def issue_certificate_request_to_digilocker(certificate_request):
    """Issue a generated certificate to DigiLocker"""
    request = frappe.get_doc("Certificate Request", certificate_request)

    if request.status != "Generated":
        return {"success": False, "error": "Certificate must be generated first"}

    # Get certificate template
    template = frappe.get_doc("Certificate Template", request.certificate_template)

    # Prepare certificate data
    student_doc = frappe.get_doc("Student", request.student)
    certificate_data = {
        "studentName": student_doc.student_name,
        "studentId": request.student,
        "certificateType": template.certificate_type,
        "certificateNumber": request.certificate_number,
        "issueDate": str(request.issue_date),
        "verificationCode": request.verification_code
    }

    # Add program info if available
    if request.program:
        program = frappe.get_doc("Program", request.program)
        certificate_data["programName"] = program.program_name

    client = DigiLockerClient()
    result = client.issue_document(
        template.certificate_type,
        certificate_data,
        request.student
    )

    if result.get("success"):
        # Update certificate request with DigiLocker URI
        frappe.db.set_value(
            "Certificate Request", certificate_request,
            "status", "Issued"
        )

        # Link DigiLocker issued document
        frappe.db.set_value(
            "DigiLocker Issued Document", result.get("issued_document"),
            {
                "certificate_request": certificate_request,
                "reference_doctype": "Certificate Request",
                "reference_name": certificate_request
            }
        )

    return result


@frappe.whitelist()
def get_student_digilocker_documents(student):
    """Get all DigiLocker documents for a student"""
    return frappe.get_all(
        "DigiLocker Issued Document",
        filters={"student": student, "status": "Issued"},
        fields=["name", "document_type", "document_uri", "issued_date", "certificate_request"],
        order_by="issued_date desc"
    )


@frappe.whitelist()
def test_digilocker_connection():
    """Test DigiLocker API connection"""
    try:
        settings = frappe.get_single("DigiLocker Settings")

        if not settings.enabled:
            return {"success": False, "message": "DigiLocker integration is not enabled"}

        if not settings.client_id or not settings.client_secret:
            return {"success": False, "message": "DigiLocker credentials not configured"}

        # For now, just validate settings are present
        return {
            "success": True,
            "message": "DigiLocker settings configured",
            "environment": settings.environment,
            "org_id": settings.org_id
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
