# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
Scheduled Tasks for University ERP
All scheduled jobs that run on daily, weekly, monthly basis
"""

import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate, now_datetime


# Daily Tasks

def expire_library_reservations():
    """Expire book reservations older than 3 days (daily job)"""
    expiry_date = add_days(nowdate(), -3)

    expired = frappe.db.sql("""
        UPDATE `tabBook Reservation`
        SET status = 'Expired'
        WHERE status = 'Active'
        AND reservation_date < %s
    """, (expiry_date,))

    if expired:
        frappe.db.commit()
        frappe.log_error(
            f"Expired {expired} library reservations",
            "Scheduled Task: Library Reservations"
        )


def update_student_cgpa():
    """Update CGPA for all students based on assessment results (daily job)"""
    # Get students with new assessment results
    students = frappe.db.sql("""
        SELECT DISTINCT ar.student
        FROM `tabAssessment Result` ar
        WHERE ar.docstatus = 1
        AND ar.modified >= DATE_SUB(NOW(), INTERVAL 1 DAY)
    """, as_dict=True)

    for student in students:
        try:
            calculate_and_update_cgpa(student.student)
        except Exception as e:
            frappe.log_error(
                f"CGPA calculation failed for {student.student}: {str(e)}",
                "Scheduled Task: CGPA Update"
            )


def calculate_and_update_cgpa(student_name):
    """Calculate and update CGPA for a student"""
    # Get all assessment results for the student
    results = frappe.db.sql("""
        SELECT
            ar.course,
            c.credit_hours,
            ar.grade,
            ar.grade_points
        FROM `tabAssessment Result` ar
        JOIN `tabCourse` c ON ar.course = c.name
        WHERE ar.student = %s
        AND ar.docstatus = 1
        AND ar.grade IS NOT NULL
    """, (student_name,), as_dict=True)

    if not results:
        return

    total_credits = 0
    total_points = 0

    for result in results:
        credit_hours = result.credit_hours or 3
        grade_points = result.grade_points or 0
        total_credits += credit_hours
        total_points += credit_hours * grade_points

    if total_credits > 0:
        cgpa = round(total_points / total_credits, 2)
        frappe.db.set_value("Student", student_name, "custom_cgpa", cgpa)


def check_attendance_thresholds():
    """Check and update attendance threshold warnings (daily job)"""
    settings = frappe.get_single("University ERP Settings")
    min_attendance = settings.get("minimum_attendance_percentage") or 75

    # Get students with low attendance in current academic term
    current_term = frappe.db.get_value(
        "Academic Term",
        {"is_current": 1},
        "name"
    )

    if not current_term:
        return

    low_attendance = frappe.db.sql("""
        SELECT
            sa.student,
            c.name as course,
            COUNT(*) as total_classes,
            SUM(CASE WHEN sa.status = 'Present' THEN 1 ELSE 0 END) as present_count
        FROM `tabStudent Attendance` sa
        JOIN `tabCourse` c ON sa.course = c.name
        WHERE sa.academic_term = %s
        GROUP BY sa.student, sa.course
        HAVING (present_count / total_classes * 100) < %s
    """, (current_term, min_attendance), as_dict=True)

    for record in low_attendance:
        # Update student's attendance warning status
        frappe.db.set_value(
            "Student",
            record.student,
            "custom_attendance_warning",
            1
        )


# Weekly Tasks

def send_placement_updates():
    """Send weekly placement updates to eligible students (weekly job)"""
    from university_erp.university_erp.notification_service import NotificationService

    # Get new job openings from the past week
    new_jobs = frappe.db.sql("""
        SELECT
            jo.name,
            jo.job_title,
            pc.company_name,
            jo.package_offered,
            jo.application_deadline
        FROM `tabPlacement Job Opening` jo
        JOIN `tabPlacement Company` pc ON jo.company = pc.name
        WHERE jo.status = 'Open'
        AND jo.creation >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    """, as_dict=True)

    if not new_jobs:
        return

    # Get students eligible for placement notifications
    eligible_students = frappe.db.sql("""
        SELECT
            s.name,
            s.student_name,
            s.student_email_id
        FROM `tabStudent` s
        WHERE s.enabled = 1
        AND s.custom_placement_registered = 1
        AND s.student_email_id IS NOT NULL
    """, as_dict=True)

    for student in eligible_students:
        context = {
            "student_name": student.student_name,
            "new_jobs": new_jobs,
            "job_count": len(new_jobs)
        }

        NotificationService.send_notification(
            recipients=[student.student_email_id],
            template_name="weekly_placement_update",
            context=context
        )


def cleanup_old_notifications():
    """Clean up old notification logs older than 90 days (weekly job)"""
    cutoff_date = add_days(nowdate(), -90)

    deleted = frappe.db.sql("""
        DELETE FROM `tabNotification Log`
        WHERE creation < %s
        AND read = 1
    """, (cutoff_date,))

    if deleted:
        frappe.db.commit()


# Monthly Tasks

def generate_monthly_reports():
    """Generate and store monthly reports (monthly job)"""
    from frappe.utils import get_first_day, get_last_day, add_months

    # Get previous month
    today = getdate(nowdate())
    first_day = get_first_day(add_months(today, -1))
    last_day = get_last_day(add_months(today, -1))

    # Generate fee collection summary
    fee_summary = frappe.db.sql("""
        SELECT
            fc.category_name,
            SUM(fd.amount) as total_amount
        FROM `tabFees` f
        JOIN `tabFee Detail` fd ON f.name = fd.parent
        JOIN `tabFee Category` fc ON fd.fee_category = fc.name
        WHERE f.docstatus = 1
        AND f.posting_date BETWEEN %s AND %s
        GROUP BY fc.category_name
    """, (first_day, last_day), as_dict=True)

    # Generate attendance summary
    attendance_summary = frappe.db.sql("""
        SELECT
            COUNT(DISTINCT student) as total_students,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as total_present,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as total_absent
        FROM `tabStudent Attendance`
        WHERE date BETWEEN %s AND %s
    """, (first_day, last_day), as_dict=True)

    # Store report (can be extended to create Report DocType entries)
    frappe.cache().set_value(
        f"monthly_report_{first_day.strftime('%Y%m')}",
        {
            "fee_summary": fee_summary,
            "attendance_summary": attendance_summary,
            "generated_at": now_datetime()
        },
        expires_in_sec=86400 * 365  # Keep for 1 year
    )


def update_placement_statistics():
    """Update placement statistics for dashboard (monthly job)"""
    current_year = getdate(nowdate()).year

    # Calculate placement statistics
    stats = frappe.db.sql("""
        SELECT
            COUNT(DISTINCT pa.student) as placed_count,
            AVG(jo.package_offered) as avg_package,
            MAX(jo.package_offered) as max_package,
            COUNT(DISTINCT pa.company) as company_count
        FROM `tabPlacement Application` pa
        JOIN `tabPlacement Job Opening` jo ON pa.job_opening = jo.name
        WHERE pa.status = 'Selected'
        AND YEAR(pa.creation) = %s
    """, (current_year,), as_dict=True)

    if stats:
        # Store in settings or cache
        frappe.cache().set_value(
            f"placement_stats_{current_year}",
            stats[0],
            expires_in_sec=86400 * 30  # Keep for 30 days
        )


# Cron Tasks

def send_exam_reminders():
    """Send exam reminders 3 days before exam (daily at 9 AM)"""
    from university_erp.university_erp.notification_service import NotificationService

    reminder_date = add_days(nowdate(), 3)

    # Get exams scheduled for reminder_date
    upcoming_exams = frappe.db.sql("""
        SELECT
            es.name,
            es.exam_date,
            es.start_time,
            es.end_time,
            es.exam_type,
            c.course_name,
            c.name as course,
            r.room_name as venue
        FROM `tabExam Schedule` es
        JOIN `tabCourse` c ON es.course = c.name
        LEFT JOIN `tabRoom` r ON es.room = r.name
        WHERE es.docstatus = 1
        AND es.exam_date = %s
    """, (reminder_date,), as_dict=True)

    for exam in upcoming_exams:
        # Get students enrolled in this course
        students = frappe.db.sql("""
            SELECT
                ce.student,
                s.student_name,
                s.student_email_id
            FROM `tabCourse Enrollment` ce
            JOIN `tabStudent` s ON ce.student = s.name
            WHERE ce.course = %s
            AND ce.docstatus = 1
            AND s.student_email_id IS NOT NULL
        """, (exam.course,), as_dict=True)

        for student in students:
            context = {
                "student_name": student.student_name,
                "course_name": exam.course_name,
                "exam_type": exam.exam_type,
                "exam_date": exam.exam_date,
                "start_time": exam.start_time,
                "venue": exam.venue or "TBA"
            }

            NotificationService.send_notification(
                recipients=[student.student_email_id],
                template_name="exam_reminder",
                context=context
            )


def send_assignment_reminders():
    """Send assignment deadline reminders (daily at 8 AM)"""
    from university_erp.university_erp.notification_service import NotificationService

    # Get assignments due in next 2 days
    deadline_start = nowdate()
    deadline_end = add_days(nowdate(), 2)

    upcoming_assignments = frappe.db.sql("""
        SELECT
            a.name,
            a.title,
            a.due_date,
            a.course,
            c.course_name
        FROM `tabAssignment` a
        JOIN `tabCourse` c ON a.course = c.name
        WHERE a.docstatus = 1
        AND a.due_date BETWEEN %s AND %s
    """, (deadline_start, deadline_end), as_dict=True)

    for assignment in upcoming_assignments:
        # Get students who haven't submitted
        students = frappe.db.sql("""
            SELECT
                ce.student,
                s.student_name,
                s.student_email_id
            FROM `tabCourse Enrollment` ce
            JOIN `tabStudent` s ON ce.student = s.name
            WHERE ce.course = %s
            AND ce.docstatus = 1
            AND s.student_email_id IS NOT NULL
            AND ce.student NOT IN (
                SELECT student FROM `tabAssignment Submission`
                WHERE assignment = %s AND docstatus = 1
            )
        """, (assignment.course, assignment.name), as_dict=True)

        for student in students:
            context = {
                "student_name": student.student_name,
                "assignment_title": assignment.title,
                "course_name": assignment.course_name,
                "due_date": assignment.due_date
            }

            NotificationService.send_notification(
                recipients=[student.student_email_id],
                template_name="assignment_reminder",
                context=context
            )
