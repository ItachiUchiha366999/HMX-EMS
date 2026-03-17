# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document


class NotificationTemplate(Document):
    """Custom notification templates for University ERP"""

    def validate(self):
        self.validate_placeholders()
        self.validate_sms_length()

    def validate_placeholders(self):
        """Extract and validate template placeholders"""
        placeholders = re.findall(r'\{\{(\w+)\}\}', self.template or "")
        if self.subject:
            placeholders.extend(re.findall(r'\{\{(\w+)\}\}', self.subject))
        self.available_fields = ", ".join(set(placeholders))

    def validate_sms_length(self):
        """Validate SMS template length"""
        if self.send_sms and self.sms_template:
            if len(self.sms_template) > 160:
                frappe.msgprint(
                    f"SMS template is {len(self.sms_template)} characters. "
                    "Messages over 160 characters may be split.",
                    indicator="orange",
                    title="SMS Length Warning"
                )

    def render(self, context):
        """Render template with context"""
        subject = frappe.render_template(self.subject, context)
        message = frappe.render_template(self.template, context)
        sms = frappe.render_template(self.sms_template or "", context) if self.sms_template else None
        return subject, message, sms


def get_template(template_name):
    """Get notification template by name"""
    if frappe.db.exists("Notification Template", template_name):
        return frappe.get_doc("Notification Template", template_name)
    return None


def create_default_templates():
    """Create default notification templates"""
    templates = [
        {
            "template_name": "fee_generated",
            "subject": "Fee Generated - {{fee_name}}",
            "category": "Fee",
            "event_type": "fee_created",
            "template": """
Dear {{student_name}},

A fee of ₹{{amount}} has been generated for {{fee_type}}.

Fee ID: {{fee_name}}
Due Date: {{due_date}}

Please make the payment before the due date to avoid late fees.

Regards,
Finance Department
{{institution_name}}
            """,
            "sms_template": "Fee of Rs.{{amount}} generated. Due: {{due_date}}. Pay before due date to avoid late fees."
        },
        {
            "template_name": "fee_reminder",
            "subject": "Fee Payment Reminder - Due: {{due_date}}",
            "category": "Fee",
            "event_type": "fee_reminder",
            "template": """
Dear {{student_name}},

This is a reminder that your fee payment of ₹{{amount}} is due on {{due_date}}.

Fee ID: {{fee_name}}
Outstanding Amount: ₹{{outstanding_amount}}

Please make the payment to avoid late fee charges.

Regards,
Finance Department
            """,
            "sms_template": "Reminder: Fee of Rs.{{outstanding_amount}} due on {{due_date}}. Pay now to avoid late charges."
        },
        {
            "template_name": "exam_schedule",
            "subject": "Examination Schedule Published - {{academic_term}}",
            "category": "Examination",
            "event_type": "exam_schedule_published",
            "template": """
Dear {{student_name}},

The examination schedule for {{academic_term}} has been published.

Please download your hall ticket from the student portal.

All the best!
Examination Department
            """,
            "sms_template": "Exam schedule for {{academic_term}} published. Download hall ticket from student portal."
        },
        {
            "template_name": "result_published",
            "subject": "Results Published - {{academic_term}}",
            "category": "Examination",
            "event_type": "result_published",
            "template": """
Dear {{student_name}},

Your results for {{academic_term}} have been published.

SGPA: {{sgpa}}
CGPA: {{cgpa}}

View detailed results on the student portal.

Regards,
Examination Department
            """,
            "sms_template": "Results published for {{academic_term}}. SGPA: {{sgpa}}, CGPA: {{cgpa}}. Check portal."
        },
        {
            "template_name": "placement_opportunity",
            "subject": "New Placement Opportunity - {{company_name}}",
            "category": "Placement",
            "event_type": "new_job_opening",
            "template": """
Dear {{student_name}},

A new job opportunity is available:

Company: {{company_name}}
Position: {{job_title}}
Package: {{package}} LPA
Application Deadline: {{deadline}}

Apply now through the placement portal.

Regards,
Training & Placement Cell
            """,
            "sms_template": "New job: {{company_name}} - {{job_title}}. Package: {{package}} LPA. Apply before {{deadline}}."
        },
        {
            "template_name": "leave_status",
            "subject": "Leave Application {{status}}",
            "category": "Leave",
            "event_type": "leave_status_change",
            "template": """
Dear {{employee_name}},

Your leave application has been {{status}}.

Leave Type: {{leave_type}}
From: {{from_date}}
To: {{to_date}}
Days: {{total_days}}

{{remarks}}

Regards,
HR Department
            """,
            "sms_template": "Leave {{status}}: {{leave_type}} from {{from_date}} to {{to_date}}."
        },
        {
            "template_name": "library_overdue",
            "subject": "Library Book Overdue Notice",
            "category": "Library",
            "event_type": "book_overdue",
            "template": """
Dear {{member_name}},

The following book is overdue:

Title: {{book_title}}
Due Date: {{due_date}}
Days Overdue: {{days_overdue}}

Please return the book immediately to avoid fines.

Current Fine: ₹{{fine_amount}}

Regards,
Library
            """,
            "sms_template": "Library book '{{book_title}}' overdue by {{days_overdue}} days. Fine: Rs.{{fine_amount}}. Return immediately."
        },
        {
            "template_name": "hostel_allocation",
            "subject": "Hostel Room Allocated",
            "category": "Hostel",
            "event_type": "room_allocated",
            "template": """
Dear {{student_name}},

You have been allocated a hostel room:

Building: {{hostel_building}}
Room: {{room_number}}
Bed Number: {{bed_number}}

Please complete the check-in process at the hostel office.

Regards,
Hostel Administration
            """,
            "sms_template": "Hostel allocated: {{hostel_building}}, Room {{room_number}}, Bed {{bed_number}}. Complete check-in at hostel office."
        },
        {
            "template_name": "attendance_warning",
            "subject": "Attendance Warning - {{course_name}}",
            "category": "Attendance",
            "event_type": "low_attendance",
            "template": """
Dear {{student_name}},

Your attendance in {{course_name}} is below the required minimum.

Current Attendance: {{attendance_percentage}}%
Required Minimum: {{required_percentage}}%

Please ensure regular attendance to avoid academic penalties.

Regards,
Academic Department
            """,
            "sms_template": "Attendance warning: {{course_name}} - {{attendance_percentage}}%. Minimum required: {{required_percentage}}%."
        }
    ]

    for template in templates:
        if not frappe.db.exists("Notification Template", template["template_name"]):
            doc = frappe.get_doc({
                "doctype": "Notification Template",
                **template,
                "enabled": 1,
                "send_email": 1,
                "send_sms": 0,
                "send_in_app": 1
            })
            doc.insert(ignore_permissions=True)

    frappe.db.commit()
