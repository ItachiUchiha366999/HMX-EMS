# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Centralized notification service for University ERP
Supports multiple channels: Email, SMS, Push, In-App
"""

import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate


class NotificationService:
    """Centralized notification service for multi-channel delivery"""

    # Map template categories to preference fields
    CATEGORY_MAP = {
        "Fee": "fee",
        "Academic": "academic",
        "Library": "library",
        "Placement": "placement",
        "Hostel": "fee",  # Use fee category for hostel
        "Admission": "academic"  # Use academic for admission
    }

    @staticmethod
    def send_notification(
        recipients,
        template_name,
        context,
        channels=None,
        attachments=None,
        respect_preferences=True
    ):
        """
        Send notification through specified channels

        Args:
            recipients: List of email addresses or user names
            template_name: Name of Notification Template
            context: Dictionary with template variables
            channels: List of channels ['email', 'sms', 'push', 'in_app']
            attachments: List of attachments for email
            respect_preferences: Whether to check user preferences (default True)
        """
        if isinstance(recipients, str):
            recipients = [recipients]

        # Get template
        template = frappe.db.get_value(
            "Notification Template",
            template_name,
            ["subject", "template", "sms_template", "enabled", "category",
             "send_email", "send_sms", "send_push", "send_in_app"],
            as_dict=True
        )

        if not template or not template.enabled:
            frappe.log_error(
                f"Template '{template_name}' not found or disabled",
                "Notification Service"
            )
            return []

        # Determine channels from template if not specified
        if channels is None:
            channels = []
            if template.send_email:
                channels.append("email")
            if template.send_sms:
                channels.append("sms")
            if template.send_push:
                channels.append("push")
            if template.send_in_app:
                channels.append("in_app")

        # Get category for preference checking
        category = NotificationService.CATEGORY_MAP.get(template.category, "academic")

        # Render template
        try:
            subject = frappe.render_template(template.subject, context)
            message = frappe.render_template(template.template, context)
            sms_message = frappe.render_template(
                template.sms_template or "", context
            ) if template.sms_template else None
        except Exception as e:
            frappe.log_error(
                f"Template rendering failed: {str(e)}",
                "Notification Service"
            )
            return []

        results = []

        if "email" in channels:
            # Filter recipients based on preferences
            if respect_preferences:
                email_recipients = NotificationService.filter_by_preferences(
                    recipients, category, "email"
                )
            else:
                email_recipients = recipients

            if email_recipients:
                result = NotificationService.send_email(
                    email_recipients, subject, message, attachments
                )
                results.append(("email", result))

        if "sms" in channels and sms_message:
            if respect_preferences:
                sms_recipients = NotificationService.filter_by_preferences(
                    recipients, category, "sms"
                )
            else:
                sms_recipients = recipients

            if sms_recipients:
                result = NotificationService.send_sms(sms_recipients, sms_message)
                results.append(("sms", result))

        if "push" in channels:
            if respect_preferences:
                push_recipients = NotificationService.filter_by_preferences(
                    recipients, category, "push"
                )
            else:
                push_recipients = recipients

            if push_recipients:
                result = NotificationService.send_push(push_recipients, subject, message)
                results.append(("push", result))

        if "in_app" in channels:
            if respect_preferences:
                in_app_recipients = NotificationService.filter_by_preferences(
                    recipients, category, "in_app"
                )
            else:
                in_app_recipients = recipients

            if in_app_recipients:
                result = NotificationService.create_in_app_notification(
                    in_app_recipients, subject, message, template_name
                )
                results.append(("in_app", result))

        return results

    @staticmethod
    def filter_by_preferences(recipients, category, channel):
        """Filter recipients based on their notification preferences"""
        from university_erp.university_erp.doctype.notification_preference.notification_preference import (
            should_send_notification
        )

        filtered = []
        for recipient in recipients:
            user = NotificationService.get_user(recipient)
            if user:
                if should_send_notification(user, category, channel):
                    filtered.append(recipient)
            else:
                # No user found, include by default
                filtered.append(recipient)

        return filtered

    @staticmethod
    def send_email(recipients, subject, message, attachments=None):
        """Send email notification"""
        try:
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message,
                attachments=attachments,
                delayed=True
            )
            return {"success": True, "count": len(recipients)}
        except Exception as e:
            frappe.log_error(f"Email send failed: {str(e)}", "Notification Error")
            return {"success": False, "error": str(e)}

    @staticmethod
    def send_sms(recipients, message):
        """Send SMS notification"""
        settings = frappe.get_single("University ERP Settings")

        if not settings.get("sms_enabled"):
            return {"success": False, "error": "SMS not enabled"}

        # Truncate message for SMS
        sms_message = message[:160] if len(message) > 160 else message
        sent_count = 0

        for recipient in recipients:
            mobile = NotificationService.get_mobile(recipient)
            if mobile:
                try:
                    # Create SMS log for gateway processing
                    frappe.get_doc({
                        "doctype": "SMS Log",
                        "mobile_no": mobile,
                        "message": sms_message,
                        "status": "Queued"
                    }).insert(ignore_permissions=True)
                    sent_count += 1
                except Exception as e:
                    frappe.log_error(f"SMS queue failed: {str(e)}", "Notification Error")

        return {"success": True, "count": sent_count}

    @staticmethod
    def send_push(recipients, title, message):
        """Send push notification"""
        settings = frappe.get_single("University ERP Settings")

        if not settings.get("push_notifications_enabled"):
            return {"success": False, "error": "Push notifications not enabled"}

        # Implementation depends on push service (Firebase/OneSignal)
        # This is a placeholder for actual implementation
        sent_count = 0

        for recipient in recipients:
            user = NotificationService.get_user(recipient)
            if user:
                # Get push token from user settings
                push_token = frappe.db.get_value(
                    "User Settings",
                    {"user": user},
                    "push_token"
                )
                if push_token:
                    # Queue push notification
                    sent_count += 1

        return {"success": True, "count": sent_count}

    @staticmethod
    def create_in_app_notification(recipients, subject, message, notification_type):
        """Create in-app notification"""
        created = 0

        for recipient in recipients:
            user = NotificationService.get_user(recipient)
            if user:
                try:
                    frappe.get_doc({
                        "doctype": "Notification Log",
                        "for_user": user,
                        "subject": subject,
                        "email_content": message,
                        "type": "Alert",
                        "document_type": notification_type
                    }).insert(ignore_permissions=True)
                    created += 1
                except Exception as e:
                    frappe.log_error(
                        f"In-app notification failed: {str(e)}",
                        "Notification Error"
                    )

        return {"success": True, "count": created}

    @staticmethod
    def get_mobile(recipient):
        """Get mobile number for recipient"""
        if "@" in recipient:
            # It's an email, find user's mobile
            mobile = frappe.db.get_value("User", recipient, "mobile_no")
            if mobile:
                return mobile

            # Try to get from Student
            student = frappe.db.get_value("Student", {"student_email_id": recipient}, "student_mobile_number")
            if student:
                return student

            # Try to get from Employee
            employee = frappe.db.get_value("Employee", {"prefered_email": recipient}, "cell_number")
            if employee:
                return employee

        # Already a mobile number
        if recipient and recipient.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            return recipient

        return None

    @staticmethod
    def get_user(recipient):
        """Get user for recipient"""
        if "@" in recipient:
            if frappe.db.exists("User", recipient):
                return recipient

            # Try to get user from Student
            user = frappe.db.get_value("Student", {"student_email_id": recipient}, "user")
            if user:
                return user

        return None


# Scheduled notification jobs
def send_fee_reminders():
    """Send fee payment reminders (scheduled daily job)"""
    # Get fees due in next 7 days
    upcoming_dues = frappe.db.sql("""
        SELECT
            f.name as fee_name,
            f.student,
            f.student_name,
            f.outstanding_amount,
            f.custom_due_date,
            s.student_email_id
        FROM `tabFees` f
        JOIN `tabStudent` s ON f.student = s.name
        WHERE f.docstatus = 1
        AND f.outstanding_amount > 0
        AND f.custom_due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
    """, as_dict=True)

    for fee in upcoming_dues:
        if fee.student_email_id:
            context = {
                "student_name": fee.student_name,
                "amount": fee.outstanding_amount,
                "due_date": fee.custom_due_date,
                "fee_name": fee.fee_name,
                "outstanding_amount": fee.outstanding_amount
            }

            NotificationService.send_notification(
                recipients=[fee.student_email_id],
                template_name="fee_reminder",
                context=context
            )


def send_overdue_notices():
    """Send overdue fee notices (scheduled daily job)"""
    overdue_fees = frappe.db.sql("""
        SELECT
            f.name as fee_name,
            f.student,
            f.student_name,
            f.outstanding_amount,
            f.custom_due_date,
            DATEDIFF(CURDATE(), f.custom_due_date) as days_overdue,
            s.student_email_id
        FROM `tabFees` f
        JOIN `tabStudent` s ON f.student = s.name
        WHERE f.docstatus = 1
        AND f.outstanding_amount > 0
        AND f.custom_due_date < CURDATE()
    """, as_dict=True)

    for fee in overdue_fees:
        # Send progressively stronger reminders at key intervals
        if fee.days_overdue in [1, 7, 14, 30]:
            if fee.student_email_id:
                context = {
                    "student_name": fee.student_name,
                    "amount": fee.outstanding_amount,
                    "due_date": fee.custom_due_date,
                    "days_overdue": fee.days_overdue,
                    "fee_name": fee.fee_name
                }

                NotificationService.send_notification(
                    recipients=[fee.student_email_id],
                    template_name="fee_reminder",
                    context=context
                )


def send_library_overdue_notices():
    """Send library overdue notices (scheduled daily job)"""
    overdue_books = frappe.db.sql("""
        SELECT
            lt.name,
            lt.library_member,
            lm.member_name,
            la.title as book_title,
            lt.to_date as due_date,
            DATEDIFF(CURDATE(), lt.to_date) as days_overdue,
            s.student_email_id
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Member` lm ON lt.library_member = lm.name
        JOIN `tabLibrary Article` la ON lt.article = la.name
        LEFT JOIN `tabStudent` s ON lm.student = s.name
        WHERE lt.type = 'Issue'
        AND lt.docstatus = 1
        AND lt.to_date < CURDATE()
        AND lt.name NOT IN (
            SELECT issue_reference FROM `tabLibrary Transaction`
            WHERE type = 'Return' AND docstatus = 1 AND issue_reference IS NOT NULL
        )
    """, as_dict=True)

    fine_per_day = frappe.db.get_single_value("University ERP Settings", "library_fine_per_day") or 5

    for book in overdue_books:
        if book.student_email_id:
            context = {
                "member_name": book.member_name,
                "book_title": book.book_title,
                "due_date": book.due_date,
                "days_overdue": book.days_overdue,
                "fine_amount": book.days_overdue * fine_per_day
            }

            NotificationService.send_notification(
                recipients=[book.student_email_id],
                template_name="library_overdue",
                context=context
            )


def send_attendance_warnings():
    """Send attendance warning notifications (scheduled weekly job)"""
    # Get students with low attendance
    low_attendance = frappe.db.sql("""
        SELECT
            sa.student,
            s.student_name,
            c.course_name,
            COUNT(*) as total_classes,
            SUM(CASE WHEN sa.status = 'Present' THEN 1 ELSE 0 END) as present_count,
            s.student_email_id
        FROM `tabStudent Attendance` sa
        JOIN `tabStudent` s ON sa.student = s.name
        JOIN `tabCourse` c ON sa.course = c.name
        WHERE sa.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY sa.student, sa.course
        HAVING (present_count / total_classes * 100) < 75
    """, as_dict=True)

    for record in low_attendance:
        if record.student_email_id and record.total_classes > 0:
            attendance_percentage = round(record.present_count / record.total_classes * 100, 1)

            context = {
                "student_name": record.student_name,
                "course_name": record.course_name,
                "attendance_percentage": attendance_percentage,
                "required_percentage": 75
            }

            NotificationService.send_notification(
                recipients=[record.student_email_id],
                template_name="attendance_warning",
                context=context
            )


def send_welcome_email(student_name):
    """Send welcome email to newly admitted student"""
    student = frappe.get_doc("Student", student_name)

    if not student.student_email_id:
        return {"success": False, "error": "Student has no email address"}

    # Get program details
    program_name = ""
    batch_year = ""
    if student.get("student_academic_year"):
        batch_year = student.student_academic_year

    enrollment = frappe.db.get_value(
        "Program Enrollment",
        {"student": student_name, "docstatus": 1},
        ["program", "academic_year"],
        as_dict=True
    )
    if enrollment:
        program_name = frappe.db.get_value("Program", enrollment.program, "program_name") or enrollment.program
        batch_year = enrollment.academic_year or batch_year

    context = {
        "student_name": student.student_name,
        "first_name": student.first_name or student.student_name.split()[0],
        "student_id": student.name,
        "program_name": program_name,
        "batch_year": batch_year,
        "email": student.student_email_id,
        "university_name": frappe.db.get_single_value("University ERP Settings", "university_name") or "University",
        "portal_url": frappe.utils.get_url("/student")
    }

    return NotificationService.send_notification(
        recipients=[student.student_email_id],
        template_name="student_welcome",
        context=context,
        respect_preferences=False  # Welcome emails always sent
    )


def send_exam_reminder(exam_schedule_name):
    """Send exam reminder to students before examination"""
    exam = frappe.get_doc("Exam Schedule", exam_schedule_name)

    # Get all students in the program/batch
    students = frappe.db.sql("""
        SELECT DISTINCT
            s.name as student,
            s.student_name,
            s.student_email_id
        FROM `tabStudent` s
        JOIN `tabProgram Enrollment` pe ON pe.student = s.name
        WHERE pe.docstatus = 1
        AND pe.program = %s
        AND s.enabled = 1
        AND s.student_email_id IS NOT NULL
    """, (exam.program,), as_dict=True)

    sent_count = 0
    for student in students:
        context = {
            "student_name": student.student_name,
            "exam_name": exam.exam_name or exam.name,
            "course_name": frappe.db.get_value("Course", exam.course, "course_name") or exam.course,
            "exam_date": frappe.utils.format_date(exam.schedule_date),
            "exam_time": exam.from_time,
            "venue": exam.room or "To be announced",
            "duration": f"{exam.duration or 180} minutes",
            "instructions": exam.get("instructions") or "Please arrive 15 minutes before exam time with your ID card."
        }

        NotificationService.send_notification(
            recipients=[student.student_email_id],
            template_name="exam_reminder",
            context=context
        )
        sent_count += 1

    return {"success": True, "sent_count": sent_count}


def send_result_notification(student_name, assessment_result_name=None, exam_result_name=None):
    """Send result notification to student when results are published"""
    student = frappe.get_doc("Student", student_name)

    if not student.student_email_id:
        return {"success": False, "error": "Student has no email address"}

    context = {
        "student_name": student.student_name,
        "first_name": student.first_name or student.student_name.split()[0],
        "portal_url": frappe.utils.get_url("/student/results")
    }

    if assessment_result_name:
        result = frappe.get_doc("Assessment Result", assessment_result_name)
        context.update({
            "result_type": "Assessment",
            "course_name": frappe.db.get_value("Course", result.course, "course_name") or result.course,
            "assessment_name": result.assessment_plan,
            "score": result.total_score,
            "max_score": result.maximum_score,
            "grade": result.grade or "N/A",
            "result_date": frappe.utils.format_date(result.creation)
        })

    if exam_result_name:
        # For semester/final exam results
        result = frappe.get_doc("Exam Result", exam_result_name) if frappe.db.exists("DocType", "Exam Result") else None
        if result:
            context.update({
                "result_type": "Examination",
                "exam_name": result.get("exam_name") or result.name,
                "sgpa": result.get("sgpa") or "N/A",
                "cgpa": result.get("cgpa") or "N/A",
                "result_status": result.get("result_status") or "Pass",
                "result_date": frappe.utils.format_date(result.creation)
            })

    return NotificationService.send_notification(
        recipients=[student.student_email_id],
        template_name="result_published",
        context=context
    )


def send_placement_notification(placement_opportunity_name, target_students=None):
    """Send placement opportunity notification to eligible students"""
    opportunity = frappe.get_doc("Placement Opportunity", placement_opportunity_name) if frappe.db.exists("DocType", "Placement Opportunity") else None

    if not opportunity:
        # Fallback for basic job posting
        return {"success": False, "error": "Placement Opportunity doctype not found"}

    # Get eligible students based on criteria
    if target_students:
        students = target_students
    else:
        filters = {"enabled": 1}
        if opportunity.get("eligible_programs"):
            # Get students from eligible programs
            students = frappe.db.sql("""
                SELECT DISTINCT
                    s.name as student,
                    s.student_name,
                    s.student_email_id
                FROM `tabStudent` s
                JOIN `tabProgram Enrollment` pe ON pe.student = s.name
                WHERE pe.docstatus = 1
                AND pe.program IN (
                    SELECT program FROM `tabPlacement Eligible Program`
                    WHERE parent = %s
                )
                AND s.enabled = 1
                AND s.student_email_id IS NOT NULL
            """, (placement_opportunity_name,), as_dict=True)
        else:
            students = frappe.get_all(
                "Student",
                filters={"enabled": 1, "student_email_id": ["is", "set"]},
                fields=["name as student", "student_name", "student_email_id"]
            )

    sent_count = 0
    for student in students:
        context = {
            "student_name": student.student_name,
            "company_name": opportunity.company_name,
            "job_title": opportunity.get("job_title") or opportunity.get("position") or "Position",
            "package": opportunity.get("package") or opportunity.get("ctc") or "As per industry standards",
            "location": opportunity.get("location") or "To be announced",
            "eligibility": opportunity.get("eligibility_criteria") or "As per company requirements",
            "last_date": frappe.utils.format_date(opportunity.get("application_deadline")) if opportunity.get("application_deadline") else "Open",
            "apply_url": frappe.utils.get_url(f"/placement/{opportunity.name}")
        }

        NotificationService.send_notification(
            recipients=[student.student_email_id],
            template_name="placement_opportunity",
            context=context
        )
        sent_count += 1

    return {"success": True, "sent_count": sent_count}


def send_hostel_allocation_notification(hostel_allocation_name):
    """Send hostel room allocation notification to student"""
    allocation = frappe.get_doc("Hostel Room Allocation", hostel_allocation_name) if frappe.db.exists("DocType", "Hostel Room Allocation") else None

    if not allocation:
        return {"success": False, "error": "Hostel Room Allocation doctype not found"}

    student = frappe.get_doc("Student", allocation.student)
    if not student.student_email_id:
        return {"success": False, "error": "Student has no email address"}

    # Get room and hostel details
    room = frappe.get_doc("Hostel Room", allocation.room) if frappe.db.exists("DocType", "Hostel Room") else None
    hostel = frappe.get_doc("Hostel", allocation.hostel) if frappe.db.exists("DocType", "Hostel") else None

    context = {
        "student_name": student.student_name,
        "hostel_name": hostel.hostel_name if hostel else allocation.hostel,
        "room_number": room.room_number if room else allocation.room,
        "room_type": room.get("room_type") if room else "Standard",
        "floor": room.get("floor") if room else "Ground",
        "allocation_date": frappe.utils.format_date(allocation.from_date),
        "valid_until": frappe.utils.format_date(allocation.to_date) if allocation.get("to_date") else "End of academic year",
        "warden_name": hostel.get("warden_name") if hostel else "Hostel Warden",
        "warden_contact": hostel.get("warden_contact") if hostel else "Contact hostel office",
        "check_in_instructions": "Please report to the hostel office with your ID card and allocation letter."
    }

    return NotificationService.send_notification(
        recipients=[student.student_email_id],
        template_name="hostel_allocation",
        context=context
    )
