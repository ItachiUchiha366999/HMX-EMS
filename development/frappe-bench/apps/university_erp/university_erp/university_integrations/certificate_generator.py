# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Certificate Generation System
Generates PDF certificates with QR code verification
"""

import frappe
from frappe import _
from frappe.utils import today, get_url, format_date
from frappe.utils.pdf import get_pdf
import hashlib
import io
import base64
import json


class CertificateGenerator:
    """Certificate generation and management"""

    def __init__(self, certificate_request):
        if isinstance(certificate_request, str):
            self.request = frappe.get_doc("Certificate Request", certificate_request)
        else:
            self.request = certificate_request

        self.template = frappe.get_doc(
            "Certificate Template",
            self.request.certificate_template
        )
        self.student = frappe.get_doc("Student", self.request.student)

    def generate(self):
        """Generate certificate PDF"""
        try:
            # Check approval requirement
            if self.template.requires_approval and self.request.status not in ["Approved", "Generated"]:
                frappe.throw(_("Certificate requires approval before generation"))

            # Generate certificate number if not exists
            if not self.request.certificate_number:
                self.request.certificate_number = self.template.get_next_certificate_number()

            # Generate verification code
            if not self.request.verification_code:
                self.request.verification_code = self._generate_verification_code()

            # Generate QR code
            qr_code_data = self._generate_qr_code()

            # Prepare context for template
            context = self._prepare_context()
            context["qr_code"] = qr_code_data

            # Render HTML
            html_content = self._render_template(context)

            # Generate PDF
            pdf_options = {
                "page-size": self.template.page_size or "A4",
                "orientation": self.template.orientation or "Portrait",
                "margin-top": f"{self.template.margin_top or 10}mm",
                "margin-bottom": f"{self.template.margin_bottom or 10}mm",
                "margin-left": f"{self.template.margin_left or 10}mm",
                "margin-right": f"{self.template.margin_right or 10}mm",
                "encoding": "UTF-8"
            }

            pdf_content = get_pdf(html_content, options=pdf_options)

            # Save PDF
            file_name = f"{self.request.name}_{self.request.certificate_number.replace('/', '-')}.pdf"
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "is_private": 0,
                "content": pdf_content,
                "attached_to_doctype": "Certificate Request",
                "attached_to_name": self.request.name
            })
            file_doc.save(ignore_permissions=True)

            # Update request
            self.request.generated_pdf = file_doc.file_url
            self.request.qr_code = qr_code_data
            self.request.status = "Generated"
            self.request.issue_date = today()
            self.request.save(ignore_permissions=True)
            frappe.db.commit()

            return {
                "success": True,
                "pdf_url": file_doc.file_url,
                "certificate_number": self.request.certificate_number,
                "verification_code": self.request.verification_code
            }

        except Exception as e:
            frappe.log_error(f"Certificate generation failed: {str(e)}", "Certificate Generator")
            return {"success": False, "error": str(e)}

    def _generate_verification_code(self):
        """Generate verification code for certificate"""
        data = f"{self.request.name}-{self.request.student}-{frappe.utils.now()}"
        hash_code = hashlib.sha256(data.encode()).hexdigest()[:12].upper()
        return hash_code

    def _generate_qr_code(self):
        """Generate QR code for verification"""
        try:
            import qrcode

            verification_url = get_url(
                f"/api/method/university_erp.university_integrations.certificate_generator.verify_certificate"
                f"?code={self.request.verification_code}"
            )

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4
            )
            qr.add_data(verification_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Save to buffer
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Convert to base64
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{qr_base64}"

        except ImportError:
            frappe.log_error("qrcode library not installed", "Certificate Generator")
            return ""

    def _prepare_context(self):
        """Prepare context dictionary for template rendering"""
        # Get student enrollment details
        enrollment = frappe.get_all(
            "Program Enrollment",
            filters={"student": self.student.name, "docstatus": 1},
            fields=["*"],
            limit=1,
            order_by="enrollment_date desc"
        )
        enrollment = enrollment[0] if enrollment else {}

        context = {
            "student": self.student.as_dict(),
            "enrollment": enrollment,
            "certificate_number": self.request.certificate_number,
            "verification_code": self.request.verification_code,
            "issue_date": format_date(self.request.issue_date or today()),
            "issue_date_raw": self.request.issue_date or today(),
            "purpose": self.request.purpose,
            "template": self.template.as_dict(),
            "today": today(),
            "today_formatted": format_date(today())
        }

        # Add additional fields
        for field in self.request.additional_fields:
            context[field.field_name] = field.field_value

        # Add program details
        if self.request.program:
            program = frappe.get_doc("Program", self.request.program)
            context["program"] = program.as_dict()

        # Add institution details
        education_settings = frappe.get_single("Education Settings") if frappe.db.exists("DocType", "Education Settings") else None
        if education_settings:
            context["institution_name"] = education_settings.institution_name or "University"
            context["institution_address"] = getattr(education_settings, "institution_address", "")
        else:
            context["institution_name"] = frappe.db.get_single_value("System Settings", "company") or "University"
            context["institution_address"] = ""

        return context

    def _render_template(self, context):
        """Render HTML template with context"""
        from jinja2 import Template

        # Base HTML structure
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: {self.template.page_size or 'A4'} {self.template.orientation.lower() if self.template.orientation else 'portrait'};
                    margin: 0;
                }}
                body {{
                    font-family: 'Times New Roman', serif;
                    margin: 0;
                    padding: 40px;
                    min-height: 100vh;
                    box-sizing: border-box;
                }}
                .certificate-container {{
                    position: relative;
                    border: 3px solid #000;
                    padding: 40px;
                    min-height: calc(100vh - 100px);
                    box-sizing: border-box;
                }}
                .watermark {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    opacity: 0.08;
                    z-index: -1;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    font-size: 28px;
                    margin: 10px 0;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                .header h2 {{
                    font-size: 20px;
                    margin: 5px 0;
                    font-weight: normal;
                }}
                .content {{
                    line-height: 2;
                    text-align: justify;
                    font-size: 16px;
                    margin: 30px 0;
                }}
                .content p {{
                    margin: 15px 0;
                    text-indent: 50px;
                }}
                .footer {{
                    margin-top: 60px;
                    display: flex;
                    justify-content: space-between;
                }}
                .signature {{
                    text-align: center;
                    min-width: 150px;
                }}
                .signature-line {{
                    border-top: 1px solid #000;
                    margin-top: 50px;
                    padding-top: 5px;
                }}
                .qr-code {{
                    position: absolute;
                    bottom: 30px;
                    right: 30px;
                    width: 80px;
                }}
                .verification-code {{
                    font-size: 10px;
                    text-align: center;
                    margin-top: 5px;
                }}
                .cert-number {{
                    position: absolute;
                    top: 20px;
                    right: 30px;
                    font-size: 12px;
                }}
                .issue-date {{
                    position: absolute;
                    top: 35px;
                    right: 30px;
                    font-size: 12px;
                }}
                .seal {{
                    position: absolute;
                    bottom: 120px;
                    left: 50%;
                    transform: translateX(-50%);
                    opacity: 0.7;
                }}
                {self.template.css_styles or ''}
            </style>
        </head>
        <body>
            <div class="certificate-container">
                <div class="cert-number">No: {context.get('certificate_number', '')}</div>
                <div class="issue-date">Date: {context.get('issue_date', '')}</div>
        """

        # Add watermark if configured
        if self.template.watermark_image:
            html += f'<img class="watermark" src="{self.template.watermark_image}" width="400">'

        # Add header if configured
        if self.template.header_image:
            html += f'''
            <div class="header">
                <img src="{self.template.header_image}" style="max-width: 100%; max-height: 150px;">
            </div>
            '''
        else:
            # Default header
            html += f'''
            <div class="header">
                <h2>{context.get('institution_name', 'University')}</h2>
                <h1>{self.template.certificate_type}</h1>
            </div>
            '''

        # Render main template content
        if self.template.html_template:
            template = Template(self.template.html_template)
            html += '<div class="content">' + template.render(**context) + '</div>'
        else:
            # Use default template
            html += '<div class="content">' + self._get_default_template(context) + '</div>'

        # Add seal if configured
        if self.template.seal_image:
            html += f'<img class="seal" src="{self.template.seal_image}" width="100">'

        # Add QR code
        if context.get('qr_code'):
            html += f'''
                <div style="position: absolute; bottom: 30px; right: 30px; text-align: center;">
                    <img class="qr-code" src="{context.get('qr_code')}" alt="Verification QR" style="width: 80px;">
                    <div class="verification-code">
                        Code: {context.get('verification_code', '')}
                    </div>
                </div>
            '''

        # Add footer if configured
        if self.template.footer_image:
            html += f'''
            <div style="position: absolute; bottom: 10px; left: 40px; right: 40px;">
                <img src="{self.template.footer_image}" style="max-width: 100%;">
            </div>
            '''

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def _get_default_template(self, context):
        """Get default template based on certificate type"""
        student = context.get('student', {})
        student_name = student.get('student_name', 'Student')

        templates = {
            "Bonafide Certificate": f"""
                <p>This is to certify that <strong>{student_name}</strong>,
                Son/Daughter of <strong>{student.get('custom_father_name', '___________')}</strong>,
                bearing Roll No. <strong>{student.get('name', '')}</strong> is a bonafide student of this institution.</p>

                <p>{'He' if student.get('gender') == 'Male' else 'She'} is currently enrolled in
                <strong>{context.get('program', {}).get('program_name', 'the program')}</strong>.</p>

                {f"<p>This certificate is issued for the purpose of {context.get('purpose')}.</p>" if context.get('purpose') else ""}

                <div class="footer">
                    <div class="signature">
                        <div class="signature-line">Principal</div>
                    </div>
                    <div class="signature">
                        <div class="signature-line">Registrar</div>
                    </div>
                </div>
            """,

            "Character Certificate": f"""
                <p>This is to certify that <strong>{student_name}</strong>,
                bearing Roll No. <strong>{student.get('name', '')}</strong>, has been a student of this institution.</p>

                <p>During {'his' if student.get('gender') == 'Male' else 'her'} stay in this institution,
                {'his' if student.get('gender') == 'Male' else 'her'} character and conduct have been found to be <strong>GOOD</strong>.</p>

                <p>{'He' if student.get('gender') == 'Male' else 'She'} bears good moral character and is not involved in any
                anti-institutional or anti-national activities.</p>

                <p>We wish {'him' if student.get('gender') == 'Male' else 'her'} all success in future endeavors.</p>

                <div class="footer">
                    <div class="signature">
                        <div class="signature-line">Principal</div>
                    </div>
                </div>
            """,

            "No Dues Certificate": f"""
                <p>This is to certify that <strong>{student_name}</strong>,
                bearing Roll No. <strong>{student.get('name', '')}</strong>,
                of <strong>{context.get('program', {}).get('program_name', 'the program')}</strong>
                has no dues pending against {'his' if student.get('gender') == 'Male' else 'her'} name in the following departments:</p>

                <table style="width: 100%; margin: 30px 0; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #000; padding: 12px; width: 50%;">Accounts Section</td>
                        <td style="border: 1px solid #000; padding: 12px; text-align: center;">✓ Cleared</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 12px;">Library</td>
                        <td style="border: 1px solid #000; padding: 12px; text-align: center;">✓ Cleared</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 12px;">Hostel</td>
                        <td style="border: 1px solid #000; padding: 12px; text-align: center;">✓ Cleared</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 12px;">Department</td>
                        <td style="border: 1px solid #000; padding: 12px; text-align: center;">✓ Cleared</td>
                    </tr>
                </table>

                <div class="footer">
                    <div class="signature">
                        <div class="signature-line">Accounts Officer</div>
                    </div>
                    <div class="signature">
                        <div class="signature-line">Registrar</div>
                    </div>
                </div>
            """
        }

        return templates.get(
            self.template.certificate_type,
            templates.get("Bonafide Certificate")
        )


# API Endpoints

@frappe.whitelist()
def generate_certificate(certificate_request):
    """Generate certificate PDF"""
    generator = CertificateGenerator(certificate_request)
    return generator.generate()


@frappe.whitelist()
def approve_certificate(certificate_request, approve=True, reason=None):
    """Approve or reject certificate request"""
    request = frappe.get_doc("Certificate Request", certificate_request)

    if approve:
        request.approve()
    else:
        request.reject(reason)

    return {"success": True, "status": request.status}


@frappe.whitelist(allow_guest=True)
def verify_certificate(code):
    """Verify certificate by verification code"""
    request = frappe.db.get_value(
        "Certificate Request",
        {"verification_code": code},
        ["name", "student", "certificate_template", "certificate_number",
         "issue_date", "status", "student_name", "program"],
        as_dict=True
    )

    if not request:
        return {
            "valid": False,
            "message": "Certificate not found"
        }

    if request.status not in ["Generated", "Issued"]:
        return {
            "valid": False,
            "message": "Certificate is not valid"
        }

    template = frappe.get_doc("Certificate Template", request.certificate_template)

    # Get institution name
    institution = "University"
    if frappe.db.exists("DocType", "Education Settings"):
        institution = frappe.db.get_single_value("Education Settings", "institution_name") or institution

    return {
        "valid": True,
        "certificate_number": request.certificate_number,
        "certificate_type": template.certificate_type,
        "student_name": request.student_name,
        "program": frappe.db.get_value("Program", request.program, "program_name") if request.program else "",
        "issue_date": str(request.issue_date),
        "institution": institution
    }


@frappe.whitelist()
def bulk_generate_certificates(template, students, purpose=None):
    """Generate certificates in bulk for multiple students"""
    if isinstance(students, str):
        students = frappe.parse_json(students)

    results = []

    for student in students:
        try:
            # Create certificate request
            request = frappe.get_doc({
                "doctype": "Certificate Request",
                "student": student,
                "certificate_template": template,
                "purpose": purpose,
                "status": "Approved"  # Auto-approve for bulk
            })
            request.insert(ignore_permissions=True)

            # Generate certificate
            generator = CertificateGenerator(request)
            result = generator.generate()

            results.append({
                "student": student,
                "success": result.get("success"),
                "certificate_number": result.get("certificate_number"),
                "pdf_url": result.get("pdf_url"),
                "error": result.get("error")
            })

        except Exception as e:
            results.append({
                "student": student,
                "success": False,
                "error": str(e)
            })

    return results


@frappe.whitelist()
def get_certificate_templates():
    """Get all active certificate templates"""
    return frappe.get_all(
        "Certificate Template",
        filters={"is_active": 1},
        fields=["name", "template_name", "certificate_type", "requires_approval"]
    )


@frappe.whitelist()
def preview_certificate(certificate_request):
    """Generate certificate preview (without saving)"""
    request = frappe.get_doc("Certificate Request", certificate_request)
    generator = CertificateGenerator(request)

    # Generate temporary values
    if not request.certificate_number:
        template = frappe.get_doc("Certificate Template", request.certificate_template)
        request.certificate_number = template.get_next_certificate_number()

    if not request.verification_code:
        request.verification_code = generator._generate_verification_code()

    context = generator._prepare_context()
    context["qr_code"] = generator._generate_qr_code()

    html_content = generator._render_template(context)

    return {"html": html_content}
