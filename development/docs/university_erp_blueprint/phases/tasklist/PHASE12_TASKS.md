# Phase 12: Integrations & Certificate Generation - Task List

## Overview
This phase implements external system integrations (payment gateways, SMS, biometric, DigiLocker) and comprehensive certificate generation system.

**Module**: University Integrations
**Total Estimated Tasks**: 85+
**Priority**: High

---

## Section A: Payment Gateway Integration

### A1. Payment Gateway Settings DocType (Single)
- [x] Create payment_gateway_settings folder
- [x] Create payment_gateway_settings.json with fields:
  - default_gateway (Select: Razorpay, PayU, Paytm, CCAvenue, Stripe)
  - environment (Select: Sandbox, Production)
  - razorpay_key_id, razorpay_key_secret, razorpay_webhook_secret
  - payu_merchant_key, payu_merchant_salt, payu_auth_header
  - success_url, failure_url, webhook_url
- [x] Create payment_gateway_settings.py controller

### A2. Payment Transaction DocType
- [x] Create payment_transaction folder
- [x] Create payment_transaction.json with fields:
  - student (Link), student_name (Data, fetch)
  - reference_doctype (Link: DocType), reference_name (Dynamic Link)
  - transaction_date (Datetime), status (Select: Initiated, Pending, Success, Failed, Refunded, Cancelled)
  - amount (Currency), currency (Link: Currency), payment_gateway (Select)
  - gateway_order_id, gateway_payment_id, gateway_signature
  - payment_method (Select: Card, NetBanking, UPI, Wallet, EMI)
  - gateway_response (Code: JSON), error_message (Small Text)
  - refund_id, refund_amount, refund_date, refund_reason
- [x] Create payment_transaction.py controller with status tracking

### A3. Payment Gateway Controller
- [x] Create payment_gateway.py with:
  - PaymentGateway base class
  - RazorpayGateway implementation (create_order, verify_payment, process_refund)
  - PayUGateway implementation
  - StripeGateway implementation
  - initiate_payment() API endpoint
  - payment_callback() guest API endpoint
  - razorpay_webhook() guest API endpoint
  - process_refund() API endpoint

---

## Section B: SMS Gateway Integration

### B1. SMS Template DocType (Child Table)
- [x] Create sms_template folder
- [x] Create sms_template.json with fields:
  - template_name (Data), template_id (Data: DLT Template ID)
  - event_trigger (Select: Fee Due, Payment Confirmation, Attendance Alert, etc.)
  - message_template (Text)

### B2. SMS Settings DocType (Single)
- [x] Create sms_settings folder
- [x] Create sms_settings.json with fields:
  - sms_gateway (Select: MSG91, Twilio, TextLocal, Fast2SMS)
  - sender_id (Data)
  - msg91_auth_key, msg91_template_id
  - twilio_account_sid, twilio_auth_token, twilio_phone_number
  - textlocal_api_key, textlocal_sender
  - fast2sms_api_key, fast2sms_sender_id
  - sms_templates (Table: SMS Template)
  - daily_limit, sms_sent_today
- [x] Create sms_settings.py controller

### B3. SMS Log DocType
- [x] Create sms_log folder
- [x] Create sms_log.json with fields:
  - recipient (Data), recipient_name (Data)
  - message (Text), sent_on (Datetime)
  - status (Select: Queued, Sent, Delivered, Failed)
  - sms_gateway (Data), message_id (Data)
  - gateway_response (Code: JSON), error_message (Small Text)
- [x] Create sms_log.py controller

### B4. SMS Gateway Controller
- [x] Create sms_gateway.py with:
  - SMSGateway base class
  - MSG91Gateway implementation
  - TwilioGateway implementation
  - TextLocalGateway implementation
  - Fast2SMSGateway implementation
  - get_sms_gateway() factory function
  - send_sms() API endpoint
  - send_bulk_sms() API endpoint
  - send_templated_sms() utility function
  - test_sms_gateway() API endpoint
  - Event handlers (on_fee_due, on_payment_success, send_attendance_alert)
  - send_exam_schedule_sms(), send_result_declaration_sms()

---

## Section C: Biometric Integration

### C1. Biometric Device DocType
- [x] Create biometric_device folder
- [x] Create biometric_device.json with fields:
  - device_name (Data), device_type (Select: ZKTeco, ESSL, BioMax, Mantra, Other)
  - serial_number (Data), location (Data), department (Link: Department)
  - status (Select: Active, Inactive, Maintenance)
  - ip_address (Data), port (Int), communication_password (Password)
  - last_sync (Datetime), auto_sync (Check), sync_interval (Int)
- [x] Create biometric_device.py controller with test_connection()

### C2. Biometric Attendance Log DocType
- [x] Create biometric_attendance_log folder
- [x] Create biometric_attendance_log.json with fields:
  - device (Link), user_id (Data), punch_time (Datetime)
  - punch_type (Select: Check In, Check Out, Break Start, Break End)
  - employee (Link), student (Link)
  - processed (Check), attendance_record (Dynamic Link), attendance_doctype (Link: DocType)
- [x] Create biometric_attendance_log.py controller

### C3. Biometric Integration Controller
- [x] Create biometric_integration.py with:
  - BiometricDevice base class
  - ZKTecoDevice implementation (connect, disconnect, get_attendance, sync_users)
  - get_biometric_device() factory function
  - sync_attendance() API endpoint
  - process_attendance_logs() API endpoint
  - get_employee_by_biometric_id(), get_student_by_biometric_id() helpers
  - create_employee_attendance(), create_student_attendance() functions
  - scheduled_sync_all_devices() scheduler task
  - test_device_connection() API endpoint

---

## Section D: DigiLocker Integration

### D1. DigiLocker Document Type (Child Table)
- [x] Create digilocker_document_type folder
- [x] Create digilocker_document_type.json with fields:
  - document_type (Data), doc_type_code (Data), uri_format (Data)

### D2. DigiLocker Settings DocType (Single)
- [x] Create digilocker_settings folder
- [x] Create digilocker_settings.json with fields:
  - enabled (Check), client_id (Data), client_secret (Password), hmac_key (Password)
  - environment (Select: Sandbox, Production)
  - org_id (Data), issuer_id (Data)
  - callback_url (Data)
  - document_types (Table: DigiLocker Document Type)
- [x] Create digilocker_settings.py controller

### D3. DigiLocker Issued Document DocType
- [x] Create digilocker_issued_document folder
- [x] Create digilocker_issued_document.json with fields:
  - student (Link), document_type (Data), document_uri (Data)
  - issued_date (Datetime), status (Select)
  - aadhaar_number (Data), digilocker_id (Data)
  - certificate_request (Link), issue_response (Code: JSON)
- [x] Create digilocker_issued_document.py controller

### D4. DigiLocker Integration Controller
- [x] Create digilocker_integration.py with:
  - DigiLockerClient class
  - _generate_hmac(), _get_headers() methods
  - issue_document() method
  - verify_document() method
  - get_issued_documents() method
  - issue_certificate_to_digilocker() API endpoint
  - verify_digilocker_document() API endpoint

---

## Section E: Certificate Generation System

### E1. Certificate Template DocType
- [x] Create certificate_template folder
- [x] Create certificate_template.json with fields:
  - template_name (Data, unique), certificate_type (Select: 10+ types)
  - description (Small Text), is_active (Check), requires_approval (Check)
  - approver_role (Link: Role)
  - html_template (Code: HTML), css_styles (Code: CSS)
  - page_size (Select: A4, Letter, Legal), orientation (Select: Portrait, Landscape)
  - header_image, footer_image, watermark_image (Attach Image)
  - numbering_prefix, numbering_suffix, numbering_digits
- [x] Create certificate_template.py controller

### E2. Certificate Field (Child Table)
- [x] Create certificate_field folder
- [x] Create certificate_field.json with fields:
  - field_name (Data), field_value (Data)

### E3. Certificate Request DocType (Submittable)
- [x] Create certificate_request folder
- [x] Create certificate_request.json with fields:
  - student (Link), student_name (Data, fetch), program (Link)
  - certificate_template (Link), request_date (Date), purpose (Small Text)
  - status (Select: Pending, Approved, Rejected, Generated, Issued)
  - additional_fields (Table: Certificate Field)
  - approved_by (Link: User), approval_date (Date), rejection_reason (Small Text)
  - certificate_number (Data), issue_date (Date), generated_pdf (Attach)
  - verification_code (Data), qr_code (Attach Image)
  - copies_requested (Int), fee_paid (Check)
- [x] Create certificate_request.py controller with workflow

### E4. Certificate Generator Controller
- [x] Create certificate_generator.py with:
  - CertificateGenerator class
  - generate() main method
  - _generate_certificate_number() method
  - _generate_verification_code() method
  - _generate_qr_code() method
  - _prepare_context() method
  - _render_template() method
  - _get_default_template() with 10+ templates (Bonafide, Character, Migration, Transfer, etc.)
  - generate_certificate() API endpoint
  - approve_certificate() API endpoint
  - reject_certificate() API endpoint
  - verify_certificate() guest API endpoint
  - bulk_generate_certificates() API endpoint

---

## Section F: Workspace & Reports

### F1. Integration Workspace
- [x] Create university_integrations workspace folder
- [x] Create university_integrations.json with:
  - Shortcuts: Payment Settings, SMS Settings, DigiLocker Settings, Biometric Device
  - Links: Payment Transaction, SMS Log, Certificate Request, Certificate Template
  - Reports: Payment Transaction Report, SMS Delivery Report, Certificate Issuance Report

### F2. Payment Transaction Report
- [x] Create payment_transaction_report folder
- [x] Create payment_transaction_report.json
- [x] Create payment_transaction_report.py with filters:
  - date_range, gateway, status, student
  - Chart: Payment trends by gateway
  - Summary: Total transactions, success rate, revenue
- [x] Create payment_transaction_report.js

### F3. SMS Delivery Report
- [x] Create sms_delivery_report folder
- [x] Create sms_delivery_report.json
- [x] Create sms_delivery_report.py with filters:
  - date_range, gateway, status, recipient
  - Chart: Delivery status distribution
  - Summary: Total SMS, delivery rate
- [x] Create sms_delivery_report.js

### F4. Certificate Issuance Report
- [x] Create certificate_issuance_report folder
- [x] Create certificate_issuance_report.json
- [x] Create certificate_issuance_report.py with filters:
  - date_range, certificate_type, status, program, student
  - Chart: Certificates by type
  - Summary: Total requests, completion rate
- [x] Create certificate_issuance_report.js

---

## Section G: Fixtures & Configuration

### G1. Default Certificate Templates
- [x] Create default templates in certificate_generator.py:
  - Bonafide Certificate template
  - Character Certificate template
  - Migration Certificate template
  - Transfer Certificate template
  - Degree Certificate template
  - Provisional Certificate template
  - Conduct Certificate template
  - Study Certificate template
  - No Dues Certificate template
  - Medium of Instruction Certificate template

### G2. Custom Fields
- [x] Add custom_biometric_id to Employee DocType
- [x] Add custom_biometric_id to Student DocType
- [x] Add custom_aadhaar_number to Student DocType (for DigiLocker)
- [x] Add custom_digilocker_id to Student DocType
- [x] Add custom_biometric_enrolled to Employee DocType
- [x] Add custom_biometric_enrollment_date to Employee DocType

---

## Summary

| Section | DocTypes | APIs | Reports |
|---------|----------|------|---------|
| A. Payment Gateway | 2 | 6 | 1 |
| B. SMS Gateway | 3 | 5 | 1 |
| C. Biometric | 2 | 5 | 0 |
| D. DigiLocker | 3 | 2 | 0 |
| E. Certificate | 3 | 5 | 1 |
| F. Workspace | 1 | 0 | 3 |
| **Total** | **14** | **23** | **6** |

---

## Implementation Notes

1. **Security**: All API keys stored as Password fieldtype
2. **Webhooks**: All webhook endpoints include signature verification (HMAC)
3. **Guest Access**: Certificate verification and payment callbacks allow guest access
4. **QR Codes**: Using qrcode library for certificate verification
5. **PDF Generation**: Using Frappe's built-in get_pdf() utility with Jinja2 templates
6. **Scheduled Tasks**: Biometric sync runs every 15 minutes (configurable)
7. **Factory Pattern**: Gateway selection uses factory functions for flexibility

---

## Files Created

### DocTypes (14)
1. `payment_gateway_settings/` - Single DocType
2. `payment_transaction/` - Standard DocType
3. `sms_template/` - Child Table
4. `sms_settings/` - Single DocType
5. `sms_log/` - Standard DocType
6. `biometric_device/` - Standard DocType
7. `biometric_attendance_log/` - Standard DocType
8. `digilocker_document_type/` - Child Table
9. `digilocker_settings/` - Single DocType
10. `digilocker_issued_document/` - Standard DocType
11. `certificate_template/` - Standard DocType
12. `certificate_field/` - Child Table
13. `certificate_request/` - Submittable DocType

### Controllers (4)
1. `payment_gateway.py` - RazorpayGateway, PayUGateway, StripeGateway
2. `sms_gateway.py` - MSG91, Twilio, TextLocal, Fast2SMS
3. `biometric_integration.py` - ZKTeco device integration
4. `digilocker_integration.py` - DigiLocker API client
5. `certificate_generator.py` - PDF generation with QR codes

### Reports (3)
1. `payment_transaction_report/` - Payment analytics
2. `sms_delivery_report/` - SMS delivery tracking
3. `certificate_issuance_report/` - Certificate statistics

### Workspace (1)
1. `university_integrations/` - Integration module workspace

---

**Created**: 2026-01-02
**Completed**: 2026-01-02
**Status**: Completed
