"""
Online Examination DocType Controller

Manages online examinations with scheduling, proctoring settings,
student registration, and access control.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime


class OnlineExamination(Document):
    """Controller for Online Examination DocType"""

    def validate(self):
        """Validate the examination"""
        self.validate_dates()
        self.validate_duration()
        self.validate_question_paper()
        self.update_statistics()

    def before_submit(self):
        """Actions before submission"""
        if not self.eligible_students:
            frappe.throw(_("At least one student must be registered for the examination"))

        self.status = "Scheduled"

    def on_submit(self):
        """Actions on submission"""
        # Lock the question paper
        if self.question_paper:
            paper = frappe.get_doc("Generated Question Paper", self.question_paper)
            if paper.status == "Approved":
                paper.lock_paper()

    def validate_dates(self):
        """Validate exam dates"""
        if get_datetime(self.start_datetime) >= get_datetime(self.end_datetime):
            frappe.throw(_("End date & time must be after start date & time"))

        # Calculate expected end based on duration
        from datetime import timedelta
        expected_duration = timedelta(minutes=self.duration_minutes + (self.late_submission_minutes or 0))
        start = get_datetime(self.start_datetime)
        end = get_datetime(self.end_datetime)

        if (end - start) < expected_duration:
            frappe.msgprint(
                _("The exam window ({0} minutes) is less than the duration + grace period ({1} minutes). "
                  "Students may not have enough time to complete the exam.").format(
                    int((end - start).total_seconds() / 60),
                    self.duration_minutes + (self.late_submission_minutes or 0)
                ),
                indicator="orange"
            )

    def validate_duration(self):
        """Validate duration"""
        if self.duration_minutes <= 0:
            frappe.throw(_("Duration must be greater than 0"))

    def validate_question_paper(self):
        """Validate question paper"""
        if self.question_paper:
            paper = frappe.get_doc("Generated Question Paper", self.question_paper)

            # Fetch course from paper
            if not self.course:
                self.course = paper.course

            # Fetch duration from paper
            if not self.duration_minutes:
                self.duration_minutes = paper.duration_minutes

    def update_statistics(self):
        """Update registration and attempt statistics"""
        self.total_registered = len(self.eligible_students) if self.eligible_students else 0

        if self.name:
            # Count attempts
            self.total_appeared = frappe.db.count("Student Exam Attempt", {
                "online_examination": self.name,
                "status": ["!=", "Not Started"]
            })

            self.total_submitted = frappe.db.count("Student Exam Attempt", {
                "online_examination": self.name,
                "status": ["in", ["Submitted", "Auto Submitted", "Evaluated"]]
            })

    @frappe.whitelist()
    def populate_students(self, student_group=None, program=None):
        """
        Populate eligible students from student group or program

        Args:
            student_group: Student Group name
            program: Program name
        """
        students = []

        if student_group:
            group = frappe.get_doc("Student Group", student_group)
            for s in group.students:
                students.append(s.student)

        elif program:
            students = frappe.get_all("Student",
                filters={"program": program, "enabled": 1},
                pluck="name"
            )

        # Add students to eligible list
        existing = [s.student for s in self.eligible_students]

        for student in students:
            if student not in existing:
                self.append("eligible_students", {"student": student})

        self.save()
        frappe.msgprint(_("Added {0} students").format(len(students) - len(existing)))

    @frappe.whitelist()
    def start_examination(self):
        """Start the examination (make it live)"""
        if self.docstatus != 1:
            frappe.throw(_("Examination must be submitted before starting"))

        self.status = "Live"
        self.db_update()
        frappe.msgprint(_("Examination is now live"))

    @frappe.whitelist()
    def end_examination(self):
        """End the examination"""
        if self.status != "Live":
            frappe.throw(_("Only Live examinations can be ended"))

        # Auto-submit all in-progress attempts
        attempts = frappe.get_all("Student Exam Attempt",
            filters={
                "online_examination": self.name,
                "status": "In Progress"
            },
            pluck="name"
        )

        for attempt_name in attempts:
            attempt = frappe.get_doc("Student Exam Attempt", attempt_name)
            attempt.auto_submit("Time Expired")

        self.status = "Completed"
        self.db_update()
        self.update_statistics()

        frappe.msgprint(_("Examination ended. {0} attempts auto-submitted").format(len(attempts)))

    def is_live(self):
        """Check if examination is currently live"""
        if self.status != "Live":
            return False

        now = now_datetime()
        return get_datetime(self.start_datetime) <= now <= get_datetime(self.end_datetime)

    def can_start(self, student):
        """
        Check if a student can start the examination

        Args:
            student: Student name

        Returns:
            tuple: (can_start: bool, message: str)
        """
        # Check if student is eligible
        eligible = any(s.student == student for s in self.eligible_students)
        if not eligible:
            return False, _("You are not registered for this examination")

        # Check exam status
        if self.status != "Live":
            return False, _("Examination is not currently live")

        # Check timing
        now = now_datetime()
        if now < get_datetime(self.start_datetime):
            return False, _("Examination has not started yet")

        if now > get_datetime(self.end_datetime):
            return False, _("Examination has ended")

        # Check previous attempts
        attempts = frappe.db.count("Student Exam Attempt", {
            "online_examination": self.name,
            "student": student,
            "status": ["in", ["Submitted", "Auto Submitted", "Evaluated"]]
        })

        if attempts >= self.max_attempts:
            return False, _("Maximum attempts exhausted")

        return True, ""


def auto_start_scheduled_exams():
    """
    Scheduled task to automatically start exams when their start time is reached
    """
    now = now_datetime()

    exams = frappe.get_all("Online Examination",
        filters={
            "status": "Scheduled",
            "docstatus": 1,
            "start_datetime": ["<=", now],
            "end_datetime": [">", now]
        },
        pluck="name"
    )

    for exam_name in exams:
        try:
            exam = frappe.get_doc("Online Examination", exam_name)
            exam.start_examination()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to auto-start exam {exam_name}: {str(e)}")


def auto_end_completed_exams():
    """
    Scheduled task to automatically end exams when their end time is reached
    """
    now = now_datetime()

    exams = frappe.get_all("Online Examination",
        filters={
            "status": "Live",
            "docstatus": 1,
            "end_datetime": ["<=", now]
        },
        pluck="name"
    )

    for exam_name in exams:
        try:
            exam = frappe.get_doc("Online Examination", exam_name)
            exam.end_examination()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to auto-end exam {exam_name}: {str(e)}")
