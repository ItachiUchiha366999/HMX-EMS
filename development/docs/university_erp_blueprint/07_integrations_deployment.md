# University ERP - Integrations, Reporting & Deployment

## Overview

This document covers external integrations, reporting/dashboards, phased implementation roadmap, and deployment strategies for the University ERP.

---

## Part 1: External Integrations

### Integration Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      University ERP                             │
│                    (Single Frappe App)                          │
├─────────────────────────────────────────────────────────────────┤
│                   Integration Layer                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Payment  │ │ Biometric│ │ Messaging│ │Government│          │
│  │ Gateway  │ │ Devices  │ │ Services │ │ Portals  │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐
│ Razorpay     │ │ ZKTeco   │ │ Twilio  │ │ AISHE/NAAC │
│ PayU         │ │ eSSL     │ │ MSG91   │ │ UGC Portal │
│ HDFC Gateway │ │ BioMax   │ │ WhatsApp│ │ DigiLocker │
└──────────────┘ └──────────┘ └─────────┘ └────────────┘
```

---

### 1. Payment Gateway Integration

#### Razorpay Integration
```python
# university_erp/integrations/razorpay.py

import frappe
import razorpay

class RazorpayIntegration:
    """Razorpay payment gateway integration"""

    def __init__(self):
        settings = frappe.get_single("University Payment Settings")
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.get_password("razorpay_key_secret"))
        )

    def create_order(self, fee_payment):
        """Create Razorpay order for fee payment"""
        doc = frappe.get_doc("Fee Payment", fee_payment)

        order_data = {
            "amount": int(doc.outstanding_amount * 100),  # Amount in paise
            "currency": "INR",
            "receipt": doc.name,
            "notes": {
                "student": doc.student,
                "student_name": doc.student_name,
                "fee_type": "University Fees"
            }
        }

        order = self.client.order.create(data=order_data)

        # Store order reference
        frappe.db.set_value("Fee Payment", fee_payment, {
            "razorpay_order_id": order["id"],
            "payment_status": "Initiated"
        })

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": frappe.get_single("University Payment Settings").razorpay_key_id
        }

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify payment signature"""
        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    def capture_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Capture successful payment"""
        if not self.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            frappe.throw("Payment verification failed")

        # Get fee payment
        fee_payment = frappe.db.get_value(
            "Fee Payment",
            {"razorpay_order_id": razorpay_order_id}
        )

        if not fee_payment:
            frappe.throw("Fee payment not found")

        doc = frappe.get_doc("Fee Payment", fee_payment)

        # Update payment status
        doc.razorpay_payment_id = razorpay_payment_id
        doc.payment_status = "Completed"
        doc.paid_amount = doc.outstanding_amount
        doc.outstanding_amount = 0
        doc.status = "Paid"
        doc.payment_date = frappe.utils.today()
        doc.save()
        doc.submit()

        # Send receipt
        self.send_payment_receipt(doc)

        return doc.name

    def send_payment_receipt(self, doc):
        """Send payment receipt to student"""
        student = frappe.get_doc("University Student", doc.student)

        frappe.sendmail(
            recipients=[student.email],
            subject=f"Payment Receipt - {doc.name}",
            template="fee_payment_receipt",
            args={"doc": doc, "student": student}
        )
```

#### Payment API Endpoints
```python
# university_erp/api/payment.py

import frappe
from university_erp.integrations.razorpay import RazorpayIntegration

@frappe.whitelist()
def create_payment_order(fee_payment):
    """API to create payment order"""
    rp = RazorpayIntegration()
    return rp.create_order(fee_payment)

@frappe.whitelist()
def verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """API to verify and capture payment"""
    rp = RazorpayIntegration()
    return rp.capture_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature)
```

---

### 2. Biometric Attendance Integration

#### Biometric Device Handler
```python
# university_erp/integrations/biometric.py

import frappe
from datetime import datetime

class BiometricIntegration:
    """Integration with biometric attendance devices"""

    SUPPORTED_DEVICES = ["ZKTeco", "eSSL", "BioMax"]

    def __init__(self, device_type="ZKTeco"):
        self.device_type = device_type
        self.settings = frappe.get_single("Biometric Settings")

    def sync_attendance(self, device_ip):
        """Sync attendance from biometric device"""
        if self.device_type == "ZKTeco":
            return self.sync_zkteco(device_ip)
        elif self.device_type == "eSSL":
            return self.sync_essl(device_ip)

    def sync_zkteco(self, device_ip):
        """Sync from ZKTeco device"""
        from zk import ZK

        zk = ZK(device_ip, port=4370, timeout=5)
        conn = zk.connect()

        try:
            attendance_records = conn.get_attendance()
            processed = 0

            for record in attendance_records:
                self.process_attendance_record(record)
                processed += 1

            # Clear device logs after sync
            if self.settings.clear_after_sync:
                conn.clear_attendance()

            return {"status": "success", "records_processed": processed}

        finally:
            conn.disconnect()

    def process_attendance_record(self, record):
        """Process single attendance record"""
        # Find student/faculty by biometric ID
        person = self.find_person_by_biometric_id(record.user_id)

        if not person:
            return

        if person["type"] == "student":
            self.create_student_attendance(person["id"], record.timestamp)
        else:
            self.create_faculty_attendance(person["id"], record.timestamp)

    def find_person_by_biometric_id(self, biometric_id):
        """Find student or faculty by biometric ID"""
        # Check students
        student = frappe.db.get_value(
            "University Student",
            {"biometric_id": biometric_id},
            "name"
        )
        if student:
            return {"type": "student", "id": student}

        # Check faculty
        faculty = frappe.db.get_value(
            "University Faculty",
            {"biometric_id": biometric_id},
            "name"
        )
        if faculty:
            return {"type": "faculty", "id": faculty}

        return None

    def create_student_attendance(self, student, timestamp):
        """Create student attendance record"""
        date = timestamp.date()

        # Check if already marked
        existing = frappe.db.exists(
            "Student Attendance",
            {"student": student, "date": date}
        )

        if not existing:
            # Get scheduled courses for today
            courses = self.get_scheduled_courses(student, date)

            for course in courses:
                att = frappe.new_doc("Student Attendance")
                att.student = student
                att.course = course
                att.date = date
                att.status = "Present"
                att.check_in_time = timestamp.time()
                att.attendance_source = "Biometric"
                att.insert(ignore_permissions=True)

    def create_faculty_attendance(self, faculty, timestamp):
        """Create faculty attendance record"""
        date = timestamp.date()

        existing = frappe.db.exists(
            "Faculty Attendance",
            {"faculty": faculty, "date": date}
        )

        if not existing:
            att = frappe.new_doc("Faculty Attendance")
            att.faculty = faculty
            att.date = date
            att.status = "Present"
            att.check_in_time = timestamp.time()
            att.attendance_source = "Biometric"
            att.insert(ignore_permissions=True)
```

---

### 3. SMS/Email/WhatsApp Integration

#### Messaging Service
```python
# university_erp/integrations/messaging.py

import frappe
import requests

class MessagingService:
    """Unified messaging service for SMS, Email, WhatsApp"""

    def __init__(self):
        self.settings = frappe.get_single("University Messaging Settings")

    def send_notification(self, recipients, message, channels=None):
        """Send notification via specified channels"""
        channels = channels or ["email"]
        results = {}

        for channel in channels:
            if channel == "email":
                results["email"] = self.send_email(recipients, message)
            elif channel == "sms":
                results["sms"] = self.send_sms(recipients, message)
            elif channel == "whatsapp":
                results["whatsapp"] = self.send_whatsapp(recipients, message)

        return results

    def send_sms(self, recipients, message):
        """Send SMS via MSG91 or similar"""
        if not self.settings.sms_enabled:
            return {"status": "disabled"}

        api_key = self.settings.get_password("sms_api_key")
        sender_id = self.settings.sms_sender_id

        # MSG91 API
        url = "https://api.msg91.com/api/v5/flow/"

        for recipient in recipients:
            mobile = self.get_mobile(recipient)
            if mobile:
                payload = {
                    "flow_id": self.settings.sms_flow_id,
                    "mobiles": mobile,
                    "message": message[:160]  # SMS limit
                }
                headers = {"authkey": api_key}

                try:
                    response = requests.post(url, json=payload, headers=headers)
                    self.log_message("SMS", recipient, message, response.status_code == 200)
                except Exception as e:
                    frappe.log_error(f"SMS Error: {str(e)}")

        return {"status": "sent"}

    def send_whatsapp(self, recipients, message):
        """Send WhatsApp message via Twilio or similar"""
        if not self.settings.whatsapp_enabled:
            return {"status": "disabled"}

        from twilio.rest import Client

        client = Client(
            self.settings.twilio_account_sid,
            self.settings.get_password("twilio_auth_token")
        )

        for recipient in recipients:
            mobile = self.get_mobile(recipient)
            if mobile:
                try:
                    client.messages.create(
                        body=message,
                        from_=f"whatsapp:{self.settings.whatsapp_number}",
                        to=f"whatsapp:+91{mobile}"
                    )
                    self.log_message("WhatsApp", recipient, message, True)
                except Exception as e:
                    frappe.log_error(f"WhatsApp Error: {str(e)}")

        return {"status": "sent"}

    def send_email(self, recipients, message, subject=None):
        """Send email notification"""
        for recipient in recipients:
            email = self.get_email(recipient)
            if email:
                frappe.sendmail(
                    recipients=[email],
                    subject=subject or "University Notification",
                    message=message
                )
                self.log_message("Email", recipient, message, True)

        return {"status": "sent"}

    def get_mobile(self, recipient):
        """Get mobile number for recipient"""
        if isinstance(recipient, str) and recipient.isdigit():
            return recipient

        # Try student
        mobile = frappe.db.get_value("University Student", recipient, "mobile")
        if mobile:
            return mobile

        # Try faculty
        mobile = frappe.db.get_value("University Faculty", recipient, "mobile")
        return mobile

    def get_email(self, recipient):
        """Get email for recipient"""
        if "@" in str(recipient):
            return recipient

        email = frappe.db.get_value("University Student", recipient, "email")
        if email:
            return email

        email = frappe.db.get_value("University Faculty", recipient, "email")
        return email

    def log_message(self, channel, recipient, message, success):
        """Log message for tracking"""
        frappe.get_doc({
            "doctype": "Message Log",
            "channel": channel,
            "recipient": recipient,
            "message": message[:500],
            "status": "Sent" if success else "Failed",
            "timestamp": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)
```

#### Notification Templates
```python
# university_erp/integrations/notification_templates.py

NOTIFICATION_TEMPLATES = {
    "fee_reminder": {
        "subject": "Fee Payment Reminder - {fee_type}",
        "message": """
Dear {student_name},

This is a reminder that your {fee_type} of Rs. {amount} is due on {due_date}.

Please make the payment at the earliest to avoid late fees.

Payment Link: {payment_link}

Regards,
University Finance Department
        """,
        "channels": ["email", "sms", "whatsapp"]
    },

    "result_declared": {
        "subject": "Examination Results Declared - {semester}",
        "message": """
Dear {student_name},

Your results for {semester} examinations have been declared.

Login to the student portal to view your results.

Regards,
Examination Cell
        """,
        "channels": ["email", "sms"]
    },

    "attendance_shortage": {
        "subject": "Attendance Shortage Alert",
        "message": """
Dear {student_name},

Your attendance in {course} is currently at {percentage}%.
Minimum required attendance is 75%.

Please ensure regular attendance.

Regards,
Academic Office
        """,
        "channels": ["email", "sms"]
    }
}
```

---

### 4. Government Portal Integration

#### AISHE Integration
```python
# university_erp/integrations/aishe.py

import frappe
import requests

class AISHEIntegration:
    """Integration with AISHE (All India Survey on Higher Education)"""

    def __init__(self):
        self.settings = frappe.get_single("Government Integration Settings")
        self.base_url = "https://aishe.gov.in/api"

    def generate_aishe_report(self, academic_year):
        """Generate data for AISHE submission"""
        report_data = {
            "institution_details": self.get_institution_details(),
            "student_enrollment": self.get_enrollment_data(academic_year),
            "faculty_data": self.get_faculty_data(academic_year),
            "program_data": self.get_program_data(),
            "infrastructure_data": self.get_infrastructure_data(),
            "financial_data": self.get_financial_data(academic_year),
        }

        return report_data

    def get_enrollment_data(self, academic_year):
        """Get student enrollment statistics"""
        return frappe.db.sql("""
            SELECT
                p.program_name,
                p.degree_type,
                COUNT(CASE WHEN s.gender = 'Male' THEN 1 END) as male_count,
                COUNT(CASE WHEN s.gender = 'Female' THEN 1 END) as female_count,
                COUNT(CASE WHEN s.category = 'General' THEN 1 END) as general_count,
                COUNT(CASE WHEN s.category = 'OBC' THEN 1 END) as obc_count,
                COUNT(CASE WHEN s.category = 'SC' THEN 1 END) as sc_count,
                COUNT(CASE WHEN s.category = 'ST' THEN 1 END) as st_count
            FROM `tabUniversity Student` s
            JOIN `tabUniversity Program` p ON s.program = p.name
            WHERE s.status = 'Active'
            GROUP BY p.name
        """, as_dict=True)

    def get_faculty_data(self, academic_year):
        """Get faculty statistics"""
        return frappe.db.sql("""
            SELECT
                designation,
                COUNT(*) as count,
                COUNT(CASE WHEN gender = 'Male' THEN 1 END) as male_count,
                COUNT(CASE WHEN gender = 'Female' THEN 1 END) as female_count,
                COUNT(CASE WHEN highest_qualification = 'PhD' THEN 1 END) as phd_count
            FROM `tabUniversity Faculty`
            WHERE status = 'Active'
            GROUP BY designation
        """, as_dict=True)
```

#### DigiLocker Integration
```python
# university_erp/integrations/digilocker.py

import frappe
import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

class DigiLockerIntegration:
    """Integration with DigiLocker for certificate issuance"""

    def __init__(self):
        self.settings = frappe.get_single("DigiLocker Settings")

    def issue_certificate(self, certificate_doc):
        """Issue certificate to DigiLocker"""
        # Prepare certificate data
        cert_data = {
            "cert_type": certificate_doc.certificate_type,
            "student_name": certificate_doc.student_name,
            "enrollment_no": certificate_doc.enrollment_number,
            "program": certificate_doc.program,
            "issue_date": str(certificate_doc.issue_date),
            "certificate_number": certificate_doc.name
        }

        # Sign the data
        signed_data = self.sign_certificate(cert_data)

        # Push to DigiLocker
        response = self.push_to_digilocker(signed_data)

        if response.get("status") == "success":
            frappe.db.set_value(
                "Student Certificate",
                certificate_doc.name,
                {
                    "digilocker_uri": response.get("uri"),
                    "digilocker_status": "Issued"
                }
            )

        return response

    def sign_certificate(self, data):
        """Digitally sign certificate data"""
        # Load private key
        private_key = serialization.load_pem_private_key(
            self.settings.get_password("private_key").encode(),
            password=None
        )

        # Sign
        signature = private_key.sign(
            frappe.as_json(data).encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return {
            "data": data,
            "signature": signature.hex()
        }
```

---

## Part 2: Reporting & Dashboards

### Custom Dashboard Charts
```python
# university_erp/analytics/charts.py

import frappe

def get_student_enrollment_chart():
    """Student enrollment trend chart"""
    data = frappe.db.sql("""
        SELECT
            YEAR(admission_date) as year,
            COUNT(*) as count
        FROM `tabUniversity Student`
        WHERE status != 'Rejected'
        GROUP BY YEAR(admission_date)
        ORDER BY year DESC
        LIMIT 5
    """, as_dict=True)

    return {
        "labels": [d.year for d in reversed(data)],
        "datasets": [{"values": [d.count for d in reversed(data)]}]
    }

def get_fee_collection_chart():
    """Monthly fee collection chart"""
    data = frappe.db.sql("""
        SELECT
            MONTH(payment_date) as month,
            SUM(paid_amount) as total
        FROM `tabFee Payment`
        WHERE docstatus = 1
        AND YEAR(payment_date) = YEAR(CURDATE())
        GROUP BY MONTH(payment_date)
        ORDER BY month
    """, as_dict=True)

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    return {
        "labels": months[:len(data)],
        "datasets": [{"values": [d.total for d in data]}]
    }

def get_department_wise_strength():
    """Department-wise student strength"""
    data = frappe.db.sql("""
        SELECT
            d.department_name,
            COUNT(s.name) as count
        FROM `tabUniversity Department` d
        LEFT JOIN `tabUniversity Program` p ON p.department = d.name
        LEFT JOIN `tabUniversity Student` s ON s.program = p.name AND s.status = 'Active'
        GROUP BY d.name
        ORDER BY count DESC
    """, as_dict=True)

    return {
        "labels": [d.department_name for d in data],
        "datasets": [{"values": [d.count for d in data]}]
    }
```

### Number Cards
```json
[
    {
        "doctype": "Number Card",
        "name": "Total Active Students",
        "document_type": "University Student",
        "function": "Count",
        "filters_json": "[[\"status\", \"=\", \"Active\"]]",
        "is_standard": 1,
        "module": "University ERP"
    },
    {
        "doctype": "Number Card",
        "name": "Total Faculty",
        "document_type": "University Faculty",
        "function": "Count",
        "filters_json": "[[\"status\", \"=\", \"Active\"]]",
        "is_standard": 1,
        "module": "University ERP"
    },
    {
        "doctype": "Number Card",
        "name": "Monthly Fee Collection",
        "document_type": "Fee Payment",
        "function": "Sum",
        "aggregate_function_based_on": "paid_amount",
        "filters_json": "[[\"payment_date\", \"Timespan\", \"this month\"], [\"docstatus\", \"=\", 1]]",
        "is_standard": 1,
        "module": "University ERP"
    },
    {
        "doctype": "Number Card",
        "name": "Pending Applications",
        "document_type": "Admission Application",
        "function": "Count",
        "filters_json": "[[\"status\", \"in\", [\"Submitted\", \"Under Review\"]]]",
        "is_standard": 1,
        "module": "University ERP"
    }
]
```

### Accreditation-Ready Reports
```python
# university_erp/analytics/accreditation_reports.py

import frappe

class AccreditationReports:
    """Generate reports for NAAC/NBA accreditation"""

    def get_naac_criteria_2(self):
        """Criterion 2: Teaching-Learning and Evaluation"""
        return {
            "2.1": self.get_student_enrollment_data(),
            "2.2": self.get_seat_filling_ratio(),
            "2.3": self.get_teaching_learning_process(),
            "2.4": self.get_teacher_profile(),
            "2.5": self.get_evaluation_process(),
            "2.6": self.get_student_performance(),
            "2.7": self.get_student_satisfaction()
        }

    def get_student_enrollment_data(self):
        """2.1 Student Enrollment and Profile"""
        return frappe.db.sql("""
            SELECT
                academic_year,
                COUNT(*) as total_students,
                COUNT(CASE WHEN gender = 'Female' THEN 1 END) as female_students,
                COUNT(CASE WHEN category IN ('SC', 'ST') THEN 1 END) as reserved_category
            FROM `tabUniversity Student`
            WHERE status = 'Active'
            GROUP BY academic_year
        """, as_dict=True)

    def get_teacher_student_ratio(self):
        """Teacher-student ratio by program"""
        return frappe.db.sql("""
            SELECT
                p.program_name,
                COUNT(DISTINCT s.name) as students,
                COUNT(DISTINCT ta.faculty) as teachers,
                ROUND(COUNT(DISTINCT s.name) / NULLIF(COUNT(DISTINCT ta.faculty), 0), 2) as ratio
            FROM `tabUniversity Program` p
            LEFT JOIN `tabUniversity Student` s ON s.program = p.name AND s.status = 'Active'
            LEFT JOIN `tabUniversity Course` c ON c.department = p.department
            LEFT JOIN `tabTeaching Assignment` ta ON ta.course = c.name
            GROUP BY p.name
        """, as_dict=True)

    def get_co_po_attainment(self, program):
        """CO-PO attainment report for OBE"""
        return frappe.db.sql("""
            SELECT
                co.course_outcome,
                po.program_outcome,
                copm.correlation_level,
                AVG(er.percentage) as average_attainment
            FROM `tabCO PO Mapping` copm
            JOIN `tabCourse Outcome` co ON copm.course_outcome = co.name
            JOIN `tabProgram Outcome` po ON copm.program_outcome = po.name
            LEFT JOIN `tabExamination Result` er ON er.course = co.parent
            WHERE po.program = %(program)s
            GROUP BY co.name, po.name
        """, {"program": program}, as_dict=True)
```

---

## Part 3: Phased Implementation Roadmap

### Phase Overview
```
Phase 1 (Months 1-3): Foundation
├── Core Masters Setup
├── HRMS Backend Integration
└── Basic User Management

Phase 2 (Months 4-6): Admissions & SIS
├── Admission Workflow
├── Student Information System
└── Student Portal v1

Phase 3 (Months 7-9): Academics & Exams
├── Course & Program Management
├── Timetable & Attendance
├── Examination System

Phase 4 (Months 10-12): Fees & Finance
├── Fee Structure & Collection
├── Payment Gateway Integration
├── Financial Reports

Phase 5 (Months 13-15): Extended Modules
├── LMS Integration
├── Placement Module
├── Accreditation/OBE

Phase 6 (Months 16-18): Analytics & Polish
├── Dashboards & Reports
├── External Integrations
├── Mobile Apps
└── Performance Optimization
```

### Phase 1: Foundation (Months 1-3)

#### Deliverables
| Week | Deliverable | Dependencies |
|------|-------------|--------------|
| 1-2 | App scaffold, hooks.py setup | Fresh Frappe/ERPNext |
| 3-4 | Core DocTypes (Department, Program, Course) | - |
| 5-6 | Role definitions, basic permissions | Core DocTypes |
| 7-8 | Faculty/Staff DocTypes with HRMS linking | ERPNext HRMS |
| 9-10 | Workspace setup, ERPNext hiding | All DocTypes |
| 11-12 | Testing, documentation | All above |

#### Risks
- HRMS integration complexity
- Permission edge cases

---

### Phase 2: Admissions & SIS (Months 4-6)

#### Deliverables
| Week | Deliverable | Dependencies |
|------|-------------|--------------|
| 1-2 | Admission Application DocType | Core Masters |
| 3-4 | Admission workflow implementation | Admission DocType |
| 5-6 | Student DocType with lifecycle | - |
| 7-8 | Program/Course Enrollment | Student, Course |
| 9-10 | Student Portal (basic) | Student DocType |
| 11-12 | Testing, data migration tools | All above |

#### Risks
- Data migration from legacy system
- Portal security

---

### Phase 3: Academics & Exams (Months 7-9)

#### Deliverables
| Week | Deliverable | Dependencies |
|------|-------------|--------------|
| 1-2 | Timetable management | Course, Faculty |
| 3-4 | Attendance system | Timetable |
| 5-6 | Examination DocTypes | Course, Student |
| 7-8 | Result processing & grading | Examination |
| 9-10 | Transcript generation | Results |
| 11-12 | Faculty portal | Faculty, Courses |

#### Risks
- Complex grading rules (CBCS)
- Exam security

---

### Phase 4: Fees & Finance (Months 10-12)

#### Deliverables
| Week | Deliverable | Dependencies |
|------|-------------|--------------|
| 1-2 | Fee Structure DocTypes | Program, Student |
| 3-4 | Fee collection workflow | Fee Structure |
| 5-6 | Payment gateway integration | Fee Collection |
| 7-8 | Scholarship/Concession system | Fee Structure |
| 9-10 | GL integration with ERPNext | Fee Payment |
| 11-12 | Financial reports | All Finance |

#### Risks
- Payment gateway testing
- GL entry accuracy

---

### Phase 5: Extended Modules (Months 13-15)

#### Deliverables
- LMS basic functionality
- Placement module
- Library integration
- Hostel management
- OBE/Accreditation framework

---

### Phase 6: Analytics & Polish (Months 16-18)

#### Deliverables
- Executive dashboards
- NAAC/NBA reports
- Government portal integrations
- Mobile app (Flutter/React Native)
- Performance optimization
- Documentation & training

---

## Part 4: Deployment Strategy

### Deployment Architecture

#### Cloud Deployment (Recommended)
```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                        │
│                    (nginx / AWS ALB)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  App 1   │    │  App 2   │    │  App 3   │
    │ (Frappe) │    │ (Frappe) │    │ (Frappe) │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │ MariaDB  │          │  Redis   │
        │ (Primary)│          │ (Cache)  │
        └────┬─────┘          └──────────┘
             │
             ▼
        ┌──────────┐
        │ MariaDB  │
        │(Replica) │
        └──────────┘
```

#### Docker Compose Production
```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  backend:
    image: university-erp:latest
    deploy:
      replicas: 3
    environment:
      - FRAPPE_SITE=university.example.com
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    networks:
      - university-net

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    networks:
      - university-net

  mariadb:
    image: mariadb:10.6
    environment:
      - MYSQL_ROOT_PASSWORD_FILE=/run/secrets/db_root_password
    volumes:
      - db-data:/var/lib/mysql
    secrets:
      - db_root_password
    networks:
      - university-net

  redis-cache:
    image: redis:alpine
    networks:
      - university-net

  redis-queue:
    image: redis:alpine
    networks:
      - university-net

volumes:
  sites:
  db-data:

secrets:
  db_root_password:
    external: true

networks:
  university-net:
```

### Multi-Campus Support
```python
# university_erp/multi_campus.py

import frappe

class MultiCampusManager:
    """Handle multi-campus deployment"""

    def get_user_campus(self, user=None):
        """Get campus for current user"""
        user = user or frappe.session.user

        # Check if user is linked to a campus
        campus = frappe.db.get_value(
            "Campus User",
            {"user": user},
            "campus"
        )

        return campus

    def apply_campus_filter(self, doctype, user=None):
        """Get campus filter for queries"""
        campus = self.get_user_campus(user)

        if not campus:
            return ""  # No filter for central users

        # Check if doctype has campus field
        if frappe.db.has_column(doctype, "campus"):
            return f"`tab{doctype}`.campus = '{campus}'"

        return ""
```

### Backup Strategy
```python
# university_erp/maintenance/backup.py

import frappe
import subprocess
from datetime import datetime

class BackupManager:
    """Manage database and file backups"""

    def create_backup(self, with_files=True):
        """Create full backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"/backups/university_erp_{timestamp}"

        # Database backup
        self.backup_database(backup_path)

        # Files backup
        if with_files:
            self.backup_files(backup_path)

        # Upload to S3
        self.upload_to_s3(backup_path)

        return backup_path

    def backup_database(self, backup_path):
        """Backup MariaDB database"""
        site = frappe.local.site
        db_name = frappe.conf.db_name
        db_password = frappe.conf.db_password

        cmd = f"mysqldump -u root -p{db_password} {db_name} | gzip > {backup_path}_db.sql.gz"
        subprocess.run(cmd, shell=True, check=True)

    def backup_files(self, backup_path):
        """Backup site files"""
        site_path = frappe.get_site_path()

        cmd = f"tar -czf {backup_path}_files.tar.gz {site_path}/public/files {site_path}/private/files"
        subprocess.run(cmd, shell=True, check=True)

    def upload_to_s3(self, backup_path):
        """Upload backup to S3"""
        import boto3

        s3 = boto3.client('s3')
        bucket = frappe.get_single("Backup Settings").s3_bucket

        for ext in ["_db.sql.gz", "_files.tar.gz"]:
            s3.upload_file(
                f"{backup_path}{ext}",
                bucket,
                f"backups/{backup_path.split('/')[-1]}{ext}"
            )
```

### Upgrade Strategy
```python
# university_erp/maintenance/upgrade.py

import frappe
import subprocess

def pre_upgrade_checks():
    """Checks before upgrading"""
    checks = {
        "backup_exists": check_recent_backup(),
        "disk_space": check_disk_space(),
        "no_active_users": check_active_users(),
        "migrations_pending": check_pending_migrations(),
    }

    failed = [k for k, v in checks.items() if not v]

    if failed:
        frappe.throw(f"Pre-upgrade checks failed: {', '.join(failed)}")

    return True

def upgrade_university_erp():
    """Upgrade university_erp app"""
    # 1. Pre-checks
    pre_upgrade_checks()

    # 2. Put site in maintenance mode
    frappe.db.set_value("Website Settings", None, "maintenance_mode", 1)

    try:
        # 3. Pull latest code
        subprocess.run(
            ["bench", "get-app", "university_erp", "--upgrade"],
            check=True
        )

        # 4. Run migrations
        subprocess.run(["bench", "migrate"], check=True)

        # 5. Clear cache
        subprocess.run(["bench", "clear-cache"], check=True)

    finally:
        # 6. Disable maintenance mode
        frappe.db.set_value("Website Settings", None, "maintenance_mode", 0)

    return True
```

---

## Summary

This blueprint provides a complete technical foundation for building a production-grade University ERP as a single ERPNext app. Key highlights:

1. **Single App Architecture** - All functionality in `university_erp` app
2. **Hidden ERPNext** - Core ERPNext modules act as backend engines only
3. **University-First UI** - Custom workspaces and role-based access
4. **Modular Design** - Clear separation of academic, HR, finance modules
5. **Secure by Design** - Comprehensive permission model with audit logging
6. **Integration Ready** - Standard patterns for external systems
7. **Scalable Deployment** - Multi-campus, cloud-native architecture

The phased implementation approach ensures manageable delivery while the upgrade strategy maintains long-term maintainability.
