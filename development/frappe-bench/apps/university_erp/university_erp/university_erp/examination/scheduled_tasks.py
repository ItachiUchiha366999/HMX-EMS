"""
Examination Module Scheduled Tasks

Contains scheduled tasks for examination management including
auto-submission, exam status updates, and notifications.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, add_to_date
from datetime import datetime


def auto_submit_expired_exams():
    """
    Auto-submit exam attempts that have exceeded time limit

    Runs: Every 5 minutes
    """
    # Find in-progress attempts that have expired
    expired_attempts = frappe.db.sql("""
        SELECT sea.name, sea.online_examination, sea.student, sea.start_time,
               oe.duration_minutes, oe.late_submission_minutes
        FROM `tabStudent Exam Attempt` sea
        INNER JOIN `tabOnline Examination` oe ON oe.name = sea.online_examination
        WHERE sea.status = 'In Progress'
        AND TIMESTAMPDIFF(SECOND, sea.start_time, NOW()) >
            (oe.duration_minutes + COALESCE(oe.late_submission_minutes, 0)) * 60
    """, as_dict=True)

    for attempt in expired_attempts:
        try:
            doc = frappe.get_doc("Student Exam Attempt", attempt.name)
            doc.auto_submit("Time Expired")
            frappe.db.commit()

            # Send notification to student
            student_user = frappe.db.get_value("Student", attempt.student, "user")
            if student_user:
                frappe.publish_realtime(
                    "exam_auto_submitted",
                    {"attempt": attempt.name, "reason": "Time Expired"},
                    user=student_user
                )
        except Exception as e:
            frappe.log_error(f"Auto-submit failed for {attempt.name}: {str(e)}")


def update_exam_status():
    """
    Update examination status based on schedule

    Runs: Every hour
    """
    now = now_datetime()

    # Start scheduled exams
    scheduled_exams = frappe.get_all(
        "Online Examination",
        filters={
            "status": "Scheduled",
            "start_datetime": ["<=", now],
            "end_datetime": [">=", now]
        },
        pluck="name"
    )

    for exam_name in scheduled_exams:
        frappe.db.set_value("Online Examination", exam_name, "status", "Live")

    # End live exams
    ended_exams = frappe.get_all(
        "Online Examination",
        filters={
            "status": "Live",
            "end_datetime": ["<", now]
        },
        pluck="name"
    )

    for exam_name in ended_exams:
        frappe.db.set_value("Online Examination", exam_name, "status", "Completed")

    frappe.db.commit()


def send_exam_reminders():
    """
    Send reminders for upcoming exams

    Runs: Daily
    """
    # Get exams starting in next 24 hours
    tomorrow = add_to_date(now_datetime(), hours=24)
    today = now_datetime()

    upcoming_exams = frappe.get_all(
        "Online Examination",
        filters={
            "status": "Scheduled",
            "start_datetime": ["between", [today, tomorrow]]
        },
        fields=["name", "examination_name", "start_datetime", "duration_minutes"]
    )

    for exam in upcoming_exams:
        # Get eligible students
        students = frappe.get_all(
            "Online Exam Student",
            filters={"parent": exam.name},
            fields=["student"]
        )

        for student in students:
            student_doc = frappe.get_doc("Student", student.student)
            if student_doc.user and student_doc.email:
                try:
                    frappe.sendmail(
                        recipients=[student_doc.email],
                        subject=_("Exam Reminder: {0}").format(exam.examination_name),
                        message=_("""
                            <p>Dear {0},</p>
                            <p>This is a reminder that your examination <b>{1}</b> is scheduled to start on {2}.</p>
                            <p>Duration: {3} minutes</p>
                            <p>Please ensure you have a stable internet connection and are ready before the exam starts.</p>
                            <p>Best regards,<br>Examination Cell</p>
                        """).format(
                            student_doc.student_name,
                            exam.examination_name,
                            exam.start_datetime,
                            exam.duration_minutes
                        )
                    )
                except Exception as e:
                    frappe.log_error(f"Failed to send exam reminder: {str(e)}")


def process_pending_evaluations():
    """
    Send reminders for pending answer sheet evaluations

    Runs: Daily
    """
    # Get sheets pending evaluation for more than 3 days
    three_days_ago = add_to_date(now_datetime(), days=-3)

    pending_sheets = frappe.db.sql("""
        SELECT
            assigned_to,
            COUNT(*) as pending_count
        FROM `tabAnswer Sheet`
        WHERE status = 'Assigned for Evaluation'
        AND assignment_datetime < %s
        AND assigned_to IS NOT NULL
        GROUP BY assigned_to
    """, (three_days_ago,), as_dict=True)

    for item in pending_sheets:
        evaluator = frappe.get_doc("Instructor", item.assigned_to)
        if evaluator.user and evaluator.email:
            try:
                frappe.sendmail(
                    recipients=[evaluator.email],
                    subject=_("Pending Answer Sheet Evaluations"),
                    message=_("""
                        <p>Dear {0},</p>
                        <p>You have <b>{1}</b> answer sheets pending evaluation for more than 3 days.</p>
                        <p>Please complete the evaluations at your earliest convenience.</p>
                        <p>Best regards,<br>Examination Cell</p>
                    """).format(evaluator.employee_name, item.pending_count)
                )
            except Exception as e:
                frappe.log_error(f"Failed to send evaluation reminder: {str(e)}")


def cleanup_expired_exam_attempts():
    """
    Clean up incomplete exam attempts older than 30 days

    Runs: Weekly
    """
    thirty_days_ago = add_to_date(now_datetime(), days=-30)

    # Get abandoned attempts (in progress but old)
    abandoned = frappe.get_all(
        "Student Exam Attempt",
        filters={
            "status": "In Progress",
            "start_time": ["<", thirty_days_ago]
        },
        pluck="name"
    )

    for attempt_name in abandoned:
        try:
            doc = frappe.get_doc("Student Exam Attempt", attempt_name)
            doc.status = "Abandoned"
            doc.remarks = "Auto-marked as abandoned after 30 days"
            doc.save()
        except Exception as e:
            frappe.log_error(f"Failed to cleanup attempt {attempt_name}: {str(e)}")

    frappe.db.commit()


def update_question_statistics():
    """
    Update question bank statistics based on exam performance

    Runs: Daily
    """
    # Get questions used in last 7 days
    seven_days_ago = add_to_date(now_datetime(), days=-7)

    questions_used = frappe.db.sql("""
        SELECT DISTINCT gppq.question
        FROM `tabQuestion Paper Question Item` gppq
        INNER JOIN `tabGenerated Question Paper` gpp ON gpp.name = gppq.parent
        INNER JOIN `tabOnline Examination` oe ON oe.question_paper = gpp.name
        WHERE oe.end_datetime >= %s
    """, (seven_days_ago,))

    for (question_name,) in questions_used:
        try:
            # Calculate average score for this question
            avg_score = frappe.db.sql("""
                SELECT AVG(
                    CASE WHEN sa.is_correct = 1 THEN 100
                         WHEN sa.is_correct = 0 THEN 0
                         ELSE sa.marks_obtained / gppq.marks * 100
                    END
                ) as avg_percentage
                FROM `tabStudent Answer` sa
                INNER JOIN `tabQuestion Paper Question Item` gppq ON gppq.question = sa.question
                WHERE sa.question = %s
            """, (question_name,))

            if avg_score and avg_score[0][0] is not None:
                frappe.db.set_value(
                    "Question Bank", question_name,
                    "average_score_percentage", avg_score[0][0]
                )

            # Update times used
            times_used = frappe.db.count(
                "Question Paper Question Item",
                {"question": question_name}
            )
            frappe.db.set_value("Question Bank", question_name, "times_used", times_used)
            frappe.db.set_value("Question Bank", question_name, "last_used_date", now_datetime())

        except Exception as e:
            frappe.log_error(f"Failed to update stats for {question_name}: {str(e)}")

    frappe.db.commit()


def publish_scheduled_results():
    """
    Publish exam results scheduled for today

    Runs: Daily
    """
    today = frappe.utils.today()

    # Get exams with result publish date today
    exams_to_publish = frappe.get_all(
        "Online Examination",
        filters={
            "status": "Completed",
            "result_publish_date": today,
            "results_published": 0
        },
        pluck="name"
    )

    for exam_name in exams_to_publish:
        try:
            exam = frappe.get_doc("Online Examination", exam_name)
            exam.publish_results()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to publish results for {exam_name}: {str(e)}")


# Scheduler hooks configuration
scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "university_erp.university_erp.examination.scheduled_tasks.auto_submit_expired_exams"
        ]
    },
    "hourly": [
        "university_erp.university_erp.examination.scheduled_tasks.update_exam_status"
    ],
    "daily": [
        "university_erp.university_erp.examination.scheduled_tasks.send_exam_reminders",
        "university_erp.university_erp.examination.scheduled_tasks.process_pending_evaluations",
        "university_erp.university_erp.examination.scheduled_tasks.update_question_statistics",
        "university_erp.university_erp.examination.scheduled_tasks.publish_scheduled_results"
    ],
    "weekly": [
        "university_erp.university_erp.examination.scheduled_tasks.cleanup_expired_exam_attempts"
    ]
}
