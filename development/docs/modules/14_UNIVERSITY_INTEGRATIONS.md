# University Integrations Module

## Overview

The University Integrations module provides connectivity to external systems including payment gateways, biometric devices, SMS providers, DigiLocker for digital certificates, and certificate generation. It acts as the integration hub for all third-party services.

## Module Location
```
university_erp/university_integrations/
```

## DocTypes (13 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Payment Gateway Settings | Main | Gateway configuration |
| Payment Transaction | Main | Transaction records |
| Biometric Device | Main | Attendance device config |
| Biometric Attendance Log | Main | Raw attendance data |
| SMS Template | Main | Message templates |
| SMS Log | Main | Sent SMS records |
| University SMS Settings | Main | SMS provider config |
| DigiLocker Settings | Main | DigiLocker API config |
| DigiLocker Document Type | Main | Document type definitions |
| DigiLocker Issued Document | Main | Issued document records |
| Certificate Template | Main | Certificate designs |
| Certificate Field | Child | Template fields |
| Certificate Request | Main | Certificate issuance requests |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                  UNIVERSITY INTEGRATIONS MODULE                   |
+------------------------------------------------------------------+
|                                                                   |
|  PAYMENT GATEWAYS                                                 |
|  +-------------------+       +-------------------+                |
|  |  Payment Gateway  |       |    Payment        |                |
|  |    Settings       |       |   Transaction     |                |
|  +-------------------+       +-------------------+                |
|  | - Razorpay        |       | - Order ID        |                |
|  | - PayU            |       | - Status          |                |
|  +-------------------+       +-------------------+                |
|                                                                   |
|  BIOMETRIC INTEGRATION                                            |
|  +-------------------+       +-------------------+                |
|  | Biometric Device  |       | Biometric         |                |
|  |                   |       | Attendance Log    |                |
|  +-------------------+       +-------------------+                |
|  | - IP Address      |       | - Punch time      |                |
|  | - Device Type     |       | - User ID         |                |
|  +-------------------+       +-------------------+                |
|                                                                   |
|  SMS INTEGRATION                                                  |
|  +-------------------+       +-------------------+                |
|  | University SMS    |       |    SMS Log        |                |
|  |    Settings       |       |                   |                |
|  +-------------------+       +-------------------+                |
|  | - Provider        |       | - Recipient       |                |
|  | - API Key         |       | - Status          |                |
|  +-------------------+       +-------------------+                |
|                                      |                            |
|                              +-------------------+                |
|                              |   SMS Template    |                |
|                              +-------------------+                |
|                                                                   |
|  DIGILOCKER INTEGRATION                                           |
|  +-------------------+       +-------------------+                |
|  | DigiLocker        |       | DigiLocker        |                |
|  |    Settings       |       | Issued Document   |                |
|  +-------------------+       +-------------------+                |
|           |                  | - Document URI    |                |
|           v                  | - Student         |                |
|  +-------------------+       +-------------------+                |
|  | DigiLocker        |                                            |
|  | Document Type     |                                            |
|  +-------------------+                                            |
|                                                                   |
|  CERTIFICATE MANAGEMENT                                           |
|  +-------------------+       +-------------------+                |
|  | Certificate       |       | Certificate       |                |
|  |    Template       |       |    Request        |                |
|  +-------------------+       +-------------------+                |
|  | - Design          |       | - Student         |                |
|  | - Fields          |       | - Status          |                |
|  +-------------------+       +-------------------+                |
|                                                                   |
+------------------------------------------------------------------+
```

## External System Connections

```
+------------------------------------------------------------------+
|                    EXTERNAL INTEGRATIONS                          |
+------------------------------------------------------------------+
|                                                                   |
|                    +-------------------+                          |
|                    | UNIVERSITY ERP    |                          |
|                    +-------------------+                          |
|                            |                                      |
|     +----------+----------+----------+----------+                 |
|     |          |          |          |          |                 |
|     v          v          v          v          v                 |
| +--------+ +--------+ +--------+ +--------+ +--------+            |
| |RAZORPAY| |  PAYU  | |  MSG91 | |DIGILOCK| |BIOMETRIC|           |
| |        | |        | | TWILIO | |   ER   | | DEVICES |           |
| +--------+ +--------+ +--------+ +--------+ +--------+            |
| | Payment| | Payment| |  SMS   | |Document| |Attendance|          |
| | Gateway| | Gateway| |WhatsApp| |  Issue | |  Data   |           |
| +--------+ +--------+ +--------+ +--------+ +--------+            |
|                                                                   |
+------------------------------------------------------------------+
```

## DocType Details

### 1. Payment Gateway Settings
**Purpose**: Configure payment gateway credentials

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| gateway_name | Select | Razorpay/PayU/Custom |
| is_enabled | Check | Active gateway |
| is_sandbox | Check | Test mode |
| api_key | Data | API key |
| api_secret | Password | API secret |
| merchant_id | Data | Merchant identifier |
| webhook_url | Data | Callback URL |
| success_url | Data | Success redirect |
| failure_url | Data | Failure redirect |

### 2. Payment Transaction
**Purpose**: Record all payment transactions

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| transaction_id | Data | System transaction ID |
| gateway | Select | Payment gateway used |
| gateway_transaction_id | Data | Gateway's transaction ID |
| order_id | Data | Order reference |
| reference_doctype | Link | Source document type |
| reference_name | Dynamic Link | Source document |
| student | Link (Student) | Payer |
| amount | Currency | Transaction amount |
| currency | Data | Currency code |
| payment_status | Select | Initiated/Success/Failed/Refunded |
| payment_method | Data | Card/UPI/NetBanking |
| bank_reference | Data | Bank reference number |
| gateway_response | JSON | Full gateway response |
| initiated_at | Datetime | Request time |
| completed_at | Datetime | Completion time |
| failure_reason | Data | If failed |

### 3. Biometric Device
**Purpose**: Configure biometric attendance devices

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| device_name | Data | Device identifier |
| device_type | Select | ZKTeco/eSSL/Custom |
| ip_address | Data | Device IP |
| port | Int | Connection port |
| serial_number | Data | Device serial |
| location | Data | Physical location |
| communication_key | Data | Device key |
| last_sync_time | Datetime | Last data pull |
| is_active | Check | Device status |

### 4. Biometric Attendance Log
**Purpose**: Raw attendance punches

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| device | Link (Biometric Device) | Source device |
| user_id | Data | Device user ID |
| punch_time | Datetime | Punch timestamp |
| punch_type | Select | In/Out |
| verification_type | Select | Fingerprint/Face/Card |
| employee | Link (Employee) | Mapped employee |
| student | Link (Student) | Mapped student |
| is_processed | Check | Synced to attendance |

### 5. SMS Template
**Purpose**: Predefined message templates

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| template_name | Data | Template identifier |
| template_type | Select | Transactional/Promotional |
| dlt_template_id | Data | DLT registration ID |
| message_content | Text | Message with variables |
| variables | Small Text | Available variables |
| is_active | Check | Template active |

**Template Variables**:
```
Fee Reminder:
"Dear {{student_name}}, your fee of Rs. {{amount}} for {{fee_type}}
is due on {{due_date}}. Please pay to avoid late fee."

Exam Notification:
"Dear {{student_name}}, your {{exam_name}} is scheduled on {{date}}
at {{time}} in {{venue}}. Hall Ticket: {{hall_ticket_no}}"
```

### 6. SMS Log
**Purpose**: Track sent messages

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| recipient | Data | Phone number |
| message | Text | Sent message |
| template | Link (SMS Template) | Template used |
| reference_doctype | Link | Related document type |
| reference_name | Dynamic Link | Related document |
| sent_time | Datetime | Send timestamp |
| delivery_status | Select | Sent/Delivered/Failed |
| provider_message_id | Data | Provider reference |
| credits_used | Int | SMS credits consumed |

### 7. University SMS Settings
**Purpose**: SMS provider configuration

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| provider | Select | MSG91/Twilio/TextLocal |
| api_key | Password | Provider API key |
| sender_id | Data | Sender name/number |
| entity_id | Data | DLT entity ID |
| is_enabled | Check | SMS active |
| daily_limit | Int | Max SMS per day |
| monthly_limit | Int | Max SMS per month |

### 8. DigiLocker Settings
**Purpose**: DigiLocker API configuration

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| client_id | Data | OAuth client ID |
| client_secret | Password | OAuth secret |
| issuer_id | Data | Organization issuer ID |
| api_url | Data | API endpoint |
| document_types | Table | Registered document types |
| is_enabled | Check | Integration active |

### 9. DigiLocker Document Type
**Purpose**: Define issuable document types

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| document_name | Data | e.g., "Degree Certificate" |
| document_code | Data | DigiLocker type code |
| uri_template | Data | URI format |
| metadata_fields | Small Text | Required metadata |
| is_active | Check | Can be issued |

### 10. DigiLocker Issued Document
**Purpose**: Track issued documents

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Recipient |
| aadhaar_hash | Data | Hashed Aadhaar |
| document_type | Link (DigiLocker Document Type) | Type |
| document_uri | Data | DigiLocker URI |
| issue_date | Date | Issued date |
| metadata | JSON | Document metadata |
| status | Select | Issued/Revoked |
| revocation_reason | Data | If revoked |

### 11. Certificate Template
**Purpose**: Design certificate templates

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| template_name | Data | Template name |
| certificate_type | Select | Degree/Transcript/Bonafide |
| html_template | Code | HTML/CSS design |
| fields | Table | Dynamic fields |
| paper_size | Select | A4/Letter/Custom |
| orientation | Select | Portrait/Landscape |
| header_image | Attach Image | Header graphic |
| footer_image | Attach Image | Footer graphic |
| signature_image | Attach Image | Authorized signature |
| watermark | Attach Image | Background watermark |
| qr_code_enabled | Check | Include QR |

### 12. Certificate Request
**Purpose**: Certificate issuance requests

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Requestor |
| certificate_type | Link (Certificate Template) | Type |
| purpose | Data | Purpose of certificate |
| copies_required | Int | Number of copies |
| request_date | Date | Request date |
| generated_file | Attach | Generated PDF |
| certificate_number | Data | Unique certificate ID |
| issued_date | Date | Issue date |
| status | Select | Requested/Generated/Issued |
| digilocker_issued | Check | Sent to DigiLocker |

## Integration Implementation

### Payment Gateway Integration
```python
# Razorpay payment initiation
def initiate_razorpay_payment(fees_id, amount, student):
    """Create Razorpay order and return checkout data"""
    settings = frappe.get_single("Payment Gateway Settings")
    if settings.gateway_name != "Razorpay" or not settings.is_enabled:
        frappe.throw("Razorpay not configured")

    import razorpay
    client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

    # Create order
    order_data = {
        "amount": int(amount * 100),  # Convert to paise
        "currency": "INR",
        "receipt": fees_id,
        "notes": {
            "student": student,
            "fees_id": fees_id
        }
    }
    order = client.order.create(data=order_data)

    # Create transaction record
    txn = frappe.new_doc("Payment Transaction")
    txn.gateway = "Razorpay"
    txn.order_id = order["id"]
    txn.reference_doctype = "Fees"
    txn.reference_name = fees_id
    txn.student = student
    txn.amount = amount
    txn.payment_status = "Initiated"
    txn.insert()

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key": settings.api_key,
        "transaction_id": txn.name
    }

# Webhook handler
def handle_razorpay_webhook(payload):
    """Process Razorpay webhook"""
    event = payload.get("event")

    if event == "payment.captured":
        payment = payload["payload"]["payment"]["entity"]
        update_payment_status(
            order_id=payment["order_id"],
            gateway_transaction_id=payment["id"],
            status="Success"
        )

    elif event == "payment.failed":
        payment = payload["payload"]["payment"]["entity"]
        update_payment_status(
            order_id=payment["order_id"],
            status="Failed",
            failure_reason=payment.get("error_description")
        )
```

### Biometric Integration
```python
# Pull attendance from ZKTeco device
def sync_biometric_device(device_name):
    """Sync attendance data from biometric device"""
    device = frappe.get_doc("Biometric Device", device_name)

    from zk import ZK
    zk = ZK(device.ip_address, port=device.port, timeout=5)
    conn = zk.connect()

    # Get attendance records since last sync
    attendances = conn.get_attendance()

    for att in attendances:
        if att.timestamp > device.last_sync_time:
            # Create attendance log
            log = frappe.new_doc("Biometric Attendance Log")
            log.device = device_name
            log.user_id = str(att.user_id)
            log.punch_time = att.timestamp
            log.punch_type = "In" if att.punch == 0 else "Out"
            log.verification_type = get_verification_type(att.punch)
            log.insert()

    # Update last sync time
    device.last_sync_time = frappe.utils.now_datetime()
    device.save()

    conn.disconnect()

# Process attendance logs to actual attendance
def process_biometric_logs():
    """Convert biometric logs to Student/Employee attendance"""
    unprocessed = frappe.get_all("Biometric Attendance Log", {
        "is_processed": 0
    })

    for log_name in unprocessed:
        log = frappe.get_doc("Biometric Attendance Log", log_name)

        # Map user_id to employee/student
        mapping = get_user_mapping(log.user_id)

        if mapping.get("employee"):
            create_employee_attendance(mapping["employee"], log)
        elif mapping.get("student"):
            create_student_attendance(mapping["student"], log)

        log.is_processed = 1
        log.save()
```

### SMS Integration
```python
# Send SMS using configured provider
def send_sms(recipient, template_name, variables):
    """Send SMS using template"""
    settings = frappe.get_single("University SMS Settings")
    if not settings.is_enabled:
        return

    template = frappe.get_doc("SMS Template", template_name)

    # Replace variables in template
    message = template.message_content
    for key, value in variables.items():
        message = message.replace(f"{{{{{key}}}}}", str(value))

    # Send via provider
    if settings.provider == "MSG91":
        response = send_msg91(settings, recipient, message, template.dlt_template_id)
    elif settings.provider == "Twilio":
        response = send_twilio(settings, recipient, message)

    # Log SMS
    log = frappe.new_doc("SMS Log")
    log.recipient = recipient
    log.message = message
    log.template = template_name
    log.sent_time = frappe.utils.now_datetime()
    log.delivery_status = "Sent" if response.get("success") else "Failed"
    log.provider_message_id = response.get("message_id")
    log.insert()

    return response
```

### DigiLocker Integration
```python
# Issue document to DigiLocker
def issue_to_digilocker(student, document_type, document_data):
    """Issue document to student's DigiLocker"""
    settings = frappe.get_single("DigiLocker Settings")
    if not settings.is_enabled:
        frappe.throw("DigiLocker integration not enabled")

    doc_type = frappe.get_doc("DigiLocker Document Type", document_type)

    # Get student's Aadhaar (hashed)
    aadhaar_hash = get_student_aadhaar_hash(student)

    # Prepare document metadata
    metadata = {
        "student_name": document_data.get("student_name"),
        "enrollment_number": document_data.get("enrollment_number"),
        "program": document_data.get("program"),
        "issue_date": frappe.utils.today(),
        # Add other required fields
    }

    # Call DigiLocker API
    headers = {
        "Authorization": f"Bearer {get_digilocker_token(settings)}",
        "Content-Type": "application/json"
    }

    payload = {
        "doc_type": doc_type.document_code,
        "digilocker_id": aadhaar_hash,
        "metadata": metadata,
        "document_uri": generate_document_uri(doc_type, document_data)
    }

    response = requests.post(
        f"{settings.api_url}/issuers/document/issue",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        # Create issued document record
        issued = frappe.new_doc("DigiLocker Issued Document")
        issued.student = student
        issued.aadhaar_hash = aadhaar_hash
        issued.document_type = document_type
        issued.document_uri = response.json().get("uri")
        issued.metadata = json.dumps(metadata)
        issued.status = "Issued"
        issued.insert()

        return issued

    frappe.throw(f"DigiLocker issue failed: {response.text}")
```

### Certificate Generation
```python
# Generate certificate PDF
def generate_certificate(student, template_name, variables=None):
    """Generate certificate from template"""
    template = frappe.get_doc("Certificate Template", template_name)
    student_doc = frappe.get_doc("Student", student)

    # Prepare data for template
    data = {
        "student_name": student_doc.student_name,
        "enrollment_number": student_doc.custom_enrollment_number,
        "program": student_doc.custom_program,
        "issue_date": frappe.utils.format_date(frappe.utils.today()),
        "certificate_number": generate_certificate_number(),
        **(variables or {})
    }

    # Render HTML template
    html = frappe.render_template(template.html_template, data)

    # Add QR code if enabled
    if template.qr_code_enabled:
        qr_data = f"{data['certificate_number']}|{student}"
        html = add_qr_code(html, qr_data)

    # Generate PDF
    from frappe.utils.pdf import get_pdf
    pdf = get_pdf(html, {"page-size": template.paper_size})

    return {
        "pdf": pdf,
        "certificate_number": data["certificate_number"],
        "data": data
    }
```

## API Endpoints

### Payment
```python
@frappe.whitelist()
def initiate_fee_payment(fees_id):
    """Initiate payment for fees"""
    fees = frappe.get_doc("Fees", fees_id)
    return initiate_razorpay_payment(
        fees_id=fees_id,
        amount=fees.outstanding_amount,
        student=fees.student
    )

@frappe.whitelist(allow_guest=True)
def payment_webhook():
    """Handle payment gateway webhook"""
    payload = frappe.request.get_json()
    gateway = determine_gateway(payload)

    if gateway == "Razorpay":
        handle_razorpay_webhook(payload)
    elif gateway == "PayU":
        handle_payu_webhook(payload)
```

### SMS
```python
@frappe.whitelist()
def send_bulk_sms(recipients, template_name, variables_list):
    """Send SMS to multiple recipients"""
    results = []
    for recipient, variables in zip(recipients, variables_list):
        result = send_sms(recipient, template_name, variables)
        results.append(result)
    return results
```

## Reports

1. **Payment Transaction Report** - All transactions
2. **Payment Success Rate** - Gateway-wise statistics
3. **SMS Delivery Report** - SMS status tracking
4. **Biometric Attendance Report** - Device-wise punches
5. **Certificate Issuance Report** - Issued certificates
6. **DigiLocker Status Report** - Documents issued

## Related Files

```
university_erp/
+-- university_integrations/
    +-- doctype/
    |   +-- payment_gateway_settings/
    |   +-- payment_transaction/
    |   +-- biometric_device/
    |   +-- biometric_attendance_log/
    |   +-- sms_template/
    |   +-- sms_log/
    |   +-- university_sms_settings/
    |   +-- digilocker_settings/
    |   +-- digilocker_document_type/
    |   +-- digilocker_issued_document/
    |   +-- certificate_template/
    |   +-- certificate_field/
    |   +-- certificate_request/
    +-- api.py
    +-- payment_gateway.py
    +-- biometric_sync.py
    +-- sms_service.py
    +-- digilocker_api.py
    +-- certificate_generator.py
```

## See Also

- [University Payments Module](16_UNIVERSITY_PAYMENTS.md)
- [University Finance Module](05_UNIVERSITY_FINANCE.md)
- [Examinations Module](04_EXAMINATIONS.md)
