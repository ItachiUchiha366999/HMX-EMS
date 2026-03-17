# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Default Notification Templates for University ERP
"""

import frappe


def get_notification_templates():
    """Return list of default notification templates"""
    return [
        # Fee Notifications
        {
            "template_name": "fee_reminder",
            "subject": "Fee Payment Reminder - {{ fee_name }}",
            "category": "Fee",
            "send_email": 1,
            "send_sms": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p>This is a reminder that your fee payment of <strong>{{ frappe.format_currency(outstanding_amount, 'INR') }}</strong>
is due on <strong>{{ frappe.format_date(due_date) }}</strong>.</p>

<p><strong>Fee Details:</strong></p>
<ul>
    <li>Fee ID: {{ fee_name }}</li>
    <li>Amount Due: {{ frappe.format_currency(outstanding_amount, 'INR') }}</li>
    <li>Due Date: {{ frappe.format_date(due_date) }}</li>
</ul>

<p>Please make the payment before the due date to avoid late fees.</p>

<p>You can pay online through the student portal or visit the accounts office.</p>

<p>Best regards,<br>
University Finance Department</p>
""",
            "sms_template": "Fee reminder: Rs.{{ outstanding_amount }} due on {{ due_date }}. Pay via student portal to avoid late fees."
        },
        {
            "template_name": "fee_overdue",
            "subject": "URGENT: Overdue Fee Notice - {{ fee_name }}",
            "category": "Fee",
            "send_email": 1,
            "send_sms": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p><strong>URGENT:</strong> Your fee payment is overdue by <strong>{{ days_overdue }} days</strong>.</p>

<p><strong>Overdue Details:</strong></p>
<ul>
    <li>Fee ID: {{ fee_name }}</li>
    <li>Outstanding Amount: {{ frappe.format_currency(amount, 'INR') }}</li>
    <li>Original Due Date: {{ frappe.format_date(due_date) }}</li>
    <li>Days Overdue: {{ days_overdue }}</li>
</ul>

<p>Please clear this payment immediately to avoid:</p>
<ul>
    <li>Additional late fees</li>
    <li>Restriction on academic services</li>
    <li>Withholding of examination hall ticket</li>
</ul>

<p>Contact the accounts office immediately if you have any concerns.</p>

<p>Best regards,<br>
University Finance Department</p>
""",
            "sms_template": "URGENT: Fee overdue by {{ days_overdue }} days. Amount: Rs.{{ amount }}. Clear immediately to avoid restrictions."
        },
        # Library Notifications
        {
            "template_name": "library_overdue",
            "subject": "Library Book Overdue Notice",
            "category": "Library",
            "send_email": 1,
            "send_sms": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ member_name }},</p>

<p>The following library book is overdue:</p>

<p><strong>Book Details:</strong></p>
<ul>
    <li>Title: {{ book_title }}</li>
    <li>Due Date: {{ frappe.format_date(due_date) }}</li>
    <li>Days Overdue: {{ days_overdue }}</li>
    <li>Fine Accrued: {{ frappe.format_currency(fine_amount, 'INR') }}</li>
</ul>

<p>Please return the book immediately to avoid further fines.</p>

<p>Current fine rate: Rs.5 per day</p>

<p>Best regards,<br>
University Library</p>
""",
            "sms_template": "Library book '{{ book_title }}' overdue by {{ days_overdue }} days. Fine: Rs.{{ fine_amount }}. Return immediately."
        },
        {
            "template_name": "book_reserved",
            "subject": "Book Reservation Confirmation",
            "category": "Library",
            "send_email": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ member_name }},</p>

<p>Your book reservation has been confirmed:</p>

<p><strong>Book Details:</strong></p>
<ul>
    <li>Title: {{ book_title }}</li>
    <li>Author: {{ author }}</li>
    <li>Reservation Date: {{ frappe.format_date(reservation_date) }}</li>
</ul>

<p>You will be notified when the book becomes available.
Please collect within 3 days of notification or the reservation will expire.</p>

<p>Best regards,<br>
University Library</p>
""",
            "sms_template": "Book '{{ book_title }}' reserved. You'll be notified when available."
        },
        # Academic Notifications
        {
            "template_name": "attendance_warning",
            "subject": "Low Attendance Warning - {{ course_name }}",
            "category": "Academic",
            "send_email": 1,
            "send_sms": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p><strong>Warning:</strong> Your attendance in the following course is below the required minimum:</p>

<p><strong>Attendance Details:</strong></p>
<ul>
    <li>Course: {{ course_name }}</li>
    <li>Current Attendance: {{ attendance_percentage }}%</li>
    <li>Required Minimum: {{ required_percentage }}%</li>
</ul>

<p>As per university regulations, students with attendance below {{ required_percentage }}% may be:</p>
<ul>
    <li>Debarred from examinations</li>
    <li>Required to repeat the course</li>
</ul>

<p>Please improve your attendance immediately.</p>

<p>Best regards,<br>
Academic Office</p>
""",
            "sms_template": "ALERT: {{ course_name }} attendance {{ attendance_percentage }}% (min {{ required_percentage }}%). Improve immediately to avoid exam debarment."
        },
        {
            "template_name": "exam_reminder",
            "subject": "Exam Reminder: {{ course_name }} - {{ exam_type }}",
            "category": "Academic",
            "send_email": 1,
            "send_push": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p>This is a reminder for your upcoming examination:</p>

<p><strong>Exam Details:</strong></p>
<ul>
    <li>Course: {{ course_name }}</li>
    <li>Exam Type: {{ exam_type }}</li>
    <li>Date: {{ frappe.format_date(exam_date) }}</li>
    <li>Time: {{ start_time }}</li>
    <li>Venue: {{ venue }}</li>
</ul>

<p><strong>Important Instructions:</strong></p>
<ul>
    <li>Arrive at least 15 minutes before the exam</li>
    <li>Carry your ID card and hall ticket</li>
    <li>Electronic devices are not allowed</li>
</ul>

<p>Good luck!</p>

<p>Best regards,<br>
Examination Cell</p>
""",
            "sms_template": "Exam: {{ course_name }} ({{ exam_type }}) on {{ exam_date }} at {{ start_time }}, {{ venue }}. Carry ID & hall ticket."
        },
        {
            "template_name": "assignment_reminder",
            "subject": "Assignment Due: {{ assignment_title }}",
            "category": "Academic",
            "send_email": 1,
            "send_push": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p>Reminder: The following assignment is due soon:</p>

<p><strong>Assignment Details:</strong></p>
<ul>
    <li>Title: {{ assignment_title }}</li>
    <li>Course: {{ course_name }}</li>
    <li>Due Date: {{ frappe.format_date(due_date) }}</li>
</ul>

<p>Please submit before the deadline to avoid late submission penalties.</p>

<p>Best regards,<br>
{{ course_name }} Faculty</p>
""",
            "sms_template": "Assignment '{{ assignment_title }}' for {{ course_name }} due on {{ due_date }}. Submit before deadline."
        },
        # Placement Notifications
        {
            "template_name": "new_job_opening",
            "subject": "New Job Opening: {{ job_title }} at {{ company_name }}",
            "category": "Placement",
            "send_email": 1,
            "send_push": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p>A new job opportunity matching your profile is available:</p>

<p><strong>Job Details:</strong></p>
<ul>
    <li>Company: {{ company_name }}</li>
    <li>Position: {{ job_title }}</li>
    <li>Package: {{ package }}</li>
    <li>Application Deadline: {{ frappe.format_date(deadline) }}</li>
</ul>

<p><strong>Eligibility:</strong></p>
<ul>
    <li>Programs: {{ eligible_programs }}</li>
    <li>Minimum CGPA: {{ min_cgpa }}</li>
</ul>

<p>Apply now through the placement portal!</p>

<p>Best regards,<br>
Training & Placement Cell</p>
""",
            "sms_template": "New job: {{ job_title }} at {{ company_name }}. Package: {{ package }}. Apply by {{ deadline }} on placement portal."
        },
        {
            "template_name": "application_status",
            "subject": "Application Update: {{ company_name }} - {{ status }}",
            "category": "Placement",
            "send_email": 1,
            "send_push": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p>Your job application status has been updated:</p>

<p><strong>Application Details:</strong></p>
<ul>
    <li>Company: {{ company_name }}</li>
    <li>Position: {{ job_title }}</li>
    <li>Status: <strong>{{ status }}</strong></li>
</ul>

{% if status == 'Shortlisted' %}
<p>Congratulations! You have been shortlisted for the next round.
Please check the placement portal for further instructions.</p>
{% elif status == 'Selected' %}
<p>Congratulations! You have been selected!
Please visit the placement office for further formalities.</p>
{% elif status == 'Rejected' %}
<p>We regret to inform you that your application was not successful this time.
Keep trying - more opportunities await!</p>
{% endif %}

<p>Best regards,<br>
Training & Placement Cell</p>
""",
            "sms_template": "Application update: {{ company_name }} - {{ status }}. Check placement portal for details."
        },
        {
            "template_name": "weekly_placement_update",
            "subject": "Weekly Placement Update: {{ job_count }} New Opportunities",
            "category": "Placement",
            "send_email": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p>Here's your weekly placement update:</p>

<p><strong>New Job Openings This Week: {{ job_count }}</strong></p>

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
    <tr>
        <th>Company</th>
        <th>Position</th>
        <th>Package</th>
        <th>Deadline</th>
    </tr>
    {% for job in new_jobs %}
    <tr>
        <td>{{ job.company_name }}</td>
        <td>{{ job.job_title }}</td>
        <td>{{ job.package_offered }} LPA</td>
        <td>{{ frappe.format_date(job.application_deadline) }}</td>
    </tr>
    {% endfor %}
</table>

<p>Visit the placement portal to apply!</p>

<p>Best regards,<br>
Training & Placement Cell</p>
""",
            "sms_template": "{{ job_count }} new jobs this week! Check placement portal."
        },
        # Hostel Notifications
        {
            "template_name": "hostel_allocation",
            "subject": "Hostel Room Allocation Confirmation",
            "category": "Hostel",
            "send_email": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p>Your hostel room has been allocated:</p>

<p><strong>Allocation Details:</strong></p>
<ul>
    <li>Building: {{ building_name }}</li>
    <li>Room Number: {{ room_number }}</li>
    <li>Room Type: {{ room_type }}</li>
    <li>Check-in Date: {{ frappe.format_date(from_date) }}</li>
</ul>

<p>Please report to the hostel office on the check-in date with:</p>
<ul>
    <li>ID Card</li>
    <li>Allocation letter</li>
    <li>Fee receipt</li>
</ul>

<p>Best regards,<br>
Hostel Administration</p>
""",
            "sms_template": "Hostel allocated: {{ building_name }}, Room {{ room_number }}. Check-in: {{ from_date }}. Report to hostel office."
        },
        # Admission Notifications
        {
            "template_name": "admission_confirmation",
            "subject": "Admission Confirmed - Welcome to {{ university_name }}!",
            "category": "Admission",
            "send_email": 1,
            "send_in_app": 1,
            "enabled": 1,
            "template": """
<p>Dear {{ student_name }},</p>

<p><strong>Congratulations!</strong> Your admission has been confirmed.</p>

<p><strong>Admission Details:</strong></p>
<ul>
    <li>Program: {{ program_name }}</li>
    <li>Batch: {{ academic_year }}</li>
    <li>Enrollment Number: {{ enrollment_number }}</li>
</ul>

<p><strong>Next Steps:</strong></p>
<ol>
    <li>Complete fee payment by {{ frappe.format_date(fee_deadline) }}</li>
    <li>Submit original documents for verification</li>
    <li>Attend orientation on {{ frappe.format_date(orientation_date) }}</li>
</ol>

<p>Welcome to our university family!</p>

<p>Best regards,<br>
Admissions Office</p>
""",
            "sms_template": "Admission confirmed! Program: {{ program_name }}. Complete fee payment & document verification. Welcome!"
        }
    ]


def create_default_templates():
    """Create default notification templates if they don't exist"""
    templates = get_notification_templates()

    for template_data in templates:
        template_name = template_data.get("template_name")

        if not frappe.db.exists("Notification Template", template_name):
            try:
                doc = frappe.new_doc("Notification Template")
                doc.update(template_data)
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(
                    f"Failed to create template {template_name}: {str(e)}",
                    "Notification Template Creation"
                )
