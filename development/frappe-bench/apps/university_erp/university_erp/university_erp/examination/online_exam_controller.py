"""
Online Exam Controller

API controller for managing online examinations including
starting exams, saving answers, submitting, and proctoring.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, time_diff_in_seconds, get_datetime
from datetime import datetime, timedelta
import json
from typing import Dict, List


class OnlineExamController:
    """
    Controller for managing online examinations
    """

    def __init__(self, exam_name: str):
        """
        Initialize controller with exam

        Args:
            exam_name: Online Examination name
        """
        self.exam = frappe.get_doc("Online Examination", exam_name)

    def validate_access(self, student: str) -> Dict:
        """
        Validate if student can access the exam

        Args:
            student: Student name

        Returns:
            Dict with status and message
        """
        # Check if student is eligible
        eligible = any(s.student == student for s in self.exam.eligible_students)
        if not eligible:
            return {
                "status": "error",
                "message": _("You are not eligible for this examination")
            }

        # Check exam status
        if self.exam.status not in ["Live", "Scheduled"]:
            return {
                "status": "error",
                "message": _("Examination is not available")
            }

        # Check exam timing
        now = now_datetime()
        start = get_datetime(self.exam.start_datetime)
        end = get_datetime(self.exam.end_datetime)

        if now < start:
            return {
                "status": "error",
                "message": _("Examination has not started yet"),
                "starts_at": str(self.exam.start_datetime)
            }

        if now > end:
            return {
                "status": "error",
                "message": _("Examination has ended")
            }

        # Check previous attempts
        attempts = frappe.db.count("Student Exam Attempt", {
            "online_examination": self.exam.name,
            "student": student,
            "status": ["in", ["Submitted", "Auto Submitted", "Evaluated"]]
        })

        if attempts >= self.exam.max_attempts:
            return {
                "status": "error",
                "message": _("Maximum attempts exhausted")
            }

        # Check IP restriction
        if self.exam.ip_restriction:
            client_ip = frappe.local.request_ip
            if not self._is_ip_allowed(client_ip):
                return {
                    "status": "error",
                    "message": _("Access denied from your IP address")
                }

        return {"status": "success"}

    def _is_ip_allowed(self, ip: str) -> bool:
        """Check if IP is in allowed ranges"""
        if not self.exam.allowed_ip_ranges:
            return True

        try:
            import ipaddress
            client_ip = ipaddress.ip_address(ip)
            allowed_ranges = self.exam.allowed_ip_ranges.split('\n')

            for range_str in allowed_ranges:
                range_str = range_str.strip()
                if not range_str:
                    continue

                try:
                    network = ipaddress.ip_network(range_str, strict=False)
                    if client_ip in network:
                        return True
                except ValueError:
                    # Try as single IP
                    if ip == range_str:
                        return True

            return False
        except Exception:
            return True  # Allow if IP checking fails

    def start_exam(self, student: str, password: str = None) -> Dict:
        """
        Start examination for a student

        Args:
            student: Student name
            password: Exam password if required

        Returns:
            Exam attempt details
        """
        # Validate password
        if self.exam.requires_password:
            if not password or password != self.exam.get_password("exam_password"):
                frappe.throw(_("Invalid exam password"))

        # Check for existing in-progress attempt
        existing_attempt = frappe.db.get_value("Student Exam Attempt", {
            "online_examination": self.exam.name,
            "student": student,
            "status": "In Progress"
        })

        if existing_attempt:
            return self._resume_attempt(existing_attempt)

        # Create new attempt
        attempt = frappe.new_doc("Student Exam Attempt")
        attempt.online_examination = self.exam.name
        attempt.student = student
        attempt.start_time = now_datetime()
        attempt.status = "In Progress"
        attempt.ip_address = frappe.local.request_ip
        attempt.browser_info = (frappe.request.headers.get("User-Agent", "")[:500]
                               if hasattr(frappe, 'request') and frappe.request else "")

        # Get attempt number
        prev_attempts = frappe.db.count("Student Exam Attempt", {
            "online_examination": self.exam.name,
            "student": student
        })
        attempt.attempt_number = prev_attempts + 1

        # Get question paper and prepare questions
        questions = self._prepare_questions(student)
        attempt.total_questions = len(questions)

        attempt.insert()

        # Calculate end time for this student
        now = datetime.now()
        duration_end = now + timedelta(minutes=self.exam.duration_minutes)
        exam_end = get_datetime(self.exam.end_datetime)
        end_time = min(duration_end, exam_end)

        return {
            "status": "success",
            "attempt_id": attempt.name,
            "questions": questions,
            "duration_minutes": self.exam.duration_minutes,
            "end_time": str(end_time),
            "settings": self._get_exam_settings()
        }

    def _resume_attempt(self, attempt_id: str) -> Dict:
        """Resume an existing attempt"""
        attempt = frappe.get_doc("Student Exam Attempt", attempt_id)

        # Get questions
        questions = self._prepare_questions(attempt.student)

        # Map saved answers
        saved_answers = {}
        for ans in attempt.answers:
            saved_answers[ans.question] = {
                "answer": ans.answer,
                "marked_for_review": ans.marked_for_review
            }

        # Calculate remaining time
        elapsed = time_diff_in_seconds(now_datetime(), attempt.start_time)
        remaining = max(0, self.exam.duration_minutes * 60 - elapsed)

        return {
            "status": "success",
            "attempt_id": attempt.name,
            "questions": questions,
            "saved_answers": saved_answers,
            "duration_minutes": int(remaining / 60),
            "remaining_seconds": int(remaining),
            "settings": self._get_exam_settings(),
            "resumed": True
        }

    def _prepare_questions(self, student: str) -> List[Dict]:
        """Prepare questions for student (with shuffling if enabled)"""
        paper = frappe.get_doc("Generated Question Paper", self.exam.question_paper)
        questions = []

        for q_item in paper.paper_questions:
            question = frappe.get_doc("Question Bank", q_item.question)

            q_data = {
                "id": question.name,
                "number": q_item.question_number,
                "type": question.question_type,
                "text": question.question_text,
                "marks": q_item.marks,
                "image": question.question_image,
                "diagram": question.question_diagram,
                "negative_marking": question.negative_marking,
                "negative_marks": question.negative_marks if question.negative_marking else 0
            }

            # Add options for MCQ/MSQ
            if question.question_type in ["Multiple Choice (MCQ)", "Multiple Select (MSQ)",
                                          "True/False", "Match the Following"]:
                options = [{
                    "id": o.option_label,
                    "text": o.option_text,
                    "image": o.option_image,
                    "match_with": o.match_with if question.question_type == "Match the Following" else None
                } for o in question.options]

                # Shuffle options if enabled
                if self.exam.shuffle_options:
                    import random
                    random.seed(f"{student}-{question.name}")
                    random.shuffle(options)

                q_data["options"] = options

            questions.append(q_data)

        # Shuffle questions if enabled
        if self.exam.shuffle_questions:
            import random
            random.seed(f"{student}-{self.exam.name}")
            random.shuffle(questions)

            # Renumber after shuffle
            for i, q in enumerate(questions, 1):
                q["display_number"] = i

        return questions

    def _get_exam_settings(self) -> Dict:
        """Get exam settings for frontend"""
        return {
            "one_question_per_page": self.exam.one_question_per_page,
            "allow_back_navigation": self.exam.allow_back_navigation,
            "show_timer": self.exam.show_timer,
            "show_question_palette": self.exam.show_question_palette,
            "allow_review_marking": self.exam.allow_review_marking,
            "show_calculator": self.exam.show_calculator,
            "full_screen_mode": self.exam.full_screen_mode,
            "disable_copy_paste": self.exam.disable_copy_paste,
            "disable_right_click": self.exam.disable_right_click,
            "proctoring_enabled": self.exam.enable_proctoring,
            "webcam_required": self.exam.webcam_required,
            "capture_snapshots": self.exam.capture_snapshots,
            "snapshot_interval": self.exam.snapshot_interval_seconds,
            "tab_switch_warning": self.exam.tab_switch_warning,
            "max_tab_switches": self.exam.max_tab_switches
        }

    def save_answer(self, attempt_id: str, question_id: str,
                   answer, marked_for_review: bool = False) -> Dict:
        """
        Save student's answer

        Args:
            attempt_id: Exam attempt ID
            question_id: Question ID
            answer: Student's answer
            marked_for_review: Whether marked for review

        Returns:
            Save status
        """
        attempt = frappe.get_doc("Student Exam Attempt", attempt_id)

        # Validate attempt is still in progress
        if attempt.status != "In Progress":
            frappe.throw(_("Exam attempt is not active"))

        # Check time
        if self._is_time_expired(attempt):
            attempt.auto_submit("Time Expired")
            return {"status": "time_expired", "message": _("Time has expired")}

        # Save answer
        attempt.save_answer(question_id, answer, marked_for_review)

        return {"status": "saved"}

    def _is_time_expired(self, attempt) -> bool:
        """Check if exam time has expired"""
        elapsed = time_diff_in_seconds(now_datetime(), attempt.start_time)
        allowed = (self.exam.duration_minutes * 60 +
                  (self.exam.late_submission_minutes or 0) * 60)
        return elapsed > allowed or now_datetime() > get_datetime(self.exam.end_datetime)

    def submit_exam(self, attempt_id: str) -> Dict:
        """
        Submit examination

        Args:
            attempt_id: Exam attempt ID

        Returns:
            Submission result
        """
        attempt = frappe.get_doc("Student Exam Attempt", attempt_id)
        result = attempt.submit_exam()

        # Add result details if showing immediately
        if self.exam.show_result_immediately:
            result["show_result"] = True
            result["correct"] = attempt.correct
            result["incorrect"] = attempt.incorrect
            result["attempted"] = attempt.attempted
            result["total_questions"] = attempt.total_questions

        if self.exam.show_correct_answers:
            result["show_answers"] = True

        return result

    def record_proctoring_event(self, attempt_id: str, event_type: str,
                               snapshot: str = None, details: dict = None):
        """
        Record proctoring event

        Args:
            attempt_id: Exam attempt ID
            event_type: Type of event (snapshot, tab_switch, violation)
            snapshot: Base64 image data
            details: Additional details
        """
        attempt = frappe.get_doc("Student Exam Attempt", attempt_id)

        if event_type == "tab_switch":
            return attempt.record_tab_switch()

        elif event_type == "snapshot" and snapshot:
            attempt.add_proctoring_snapshot(snapshot, "Random Capture")

        elif event_type == "violation":
            attempt.proctoring_violations = (attempt.proctoring_violations or 0) + 1
            attempt.append("proctoring_snapshots", {
                "timestamp": now_datetime(),
                "event_type": details.get("violation_type", "Unknown") if details else "Unknown",
                "remarks": details.get("description", "") if details else ""
            })

            # Disqualify if too many violations
            if attempt.proctoring_violations >= 3:
                attempt.status = "Disqualified"
                attempt.remarks = "Disqualified due to multiple proctoring violations"

            attempt.save()

        return {"status": "recorded"}


# API Endpoints

@frappe.whitelist()
def start_examination(exam_name: str, password: str = None):
    """API to start an examination"""
    student = get_current_student()
    if not student:
        frappe.throw(_("Student profile not found"))

    controller = OnlineExamController(exam_name)

    # Validate access
    validation = controller.validate_access(student)
    if validation.get("status") != "success":
        return validation

    return controller.start_exam(student, password)


@frappe.whitelist()
def save_exam_answer(attempt_id: str, question_id: str,
                    answer: str, marked_for_review: bool = False):
    """API to save an answer"""
    exam_name = frappe.db.get_value("Student Exam Attempt", attempt_id, "online_examination")
    if not exam_name:
        frappe.throw(_("Invalid attempt"))

    controller = OnlineExamController(exam_name)
    return controller.save_answer(attempt_id, question_id, answer,
                                 frappe.utils.sbool(marked_for_review))


@frappe.whitelist()
def submit_examination(attempt_id: str):
    """API to submit examination"""
    exam_name = frappe.db.get_value("Student Exam Attempt", attempt_id, "online_examination")
    if not exam_name:
        frappe.throw(_("Invalid attempt"))

    controller = OnlineExamController(exam_name)
    return controller.submit_exam(attempt_id)


@frappe.whitelist()
def report_proctoring_event(attempt_id: str, event_type: str,
                           snapshot: str = None, details: str = None):
    """API to report proctoring events"""
    exam_name = frappe.db.get_value("Student Exam Attempt", attempt_id, "online_examination")
    if not exam_name:
        frappe.throw(_("Invalid attempt"))

    controller = OnlineExamController(exam_name)

    details_dict = json.loads(details) if details else {}
    return controller.record_proctoring_event(attempt_id, event_type, snapshot, details_dict)


@frappe.whitelist()
def get_exam_status(attempt_id: str):
    """Get current status of an exam attempt"""
    attempt = frappe.get_doc("Student Exam Attempt", attempt_id)

    # Calculate remaining time
    if attempt.start_time and attempt.status == "In Progress":
        exam = frappe.get_doc("Online Examination", attempt.online_examination)
        elapsed = time_diff_in_seconds(now_datetime(), attempt.start_time)
        remaining = max(0, exam.duration_minutes * 60 - elapsed)
    else:
        remaining = 0

    return {
        "status": attempt.status,
        "attempted": attempt.attempted,
        "total_questions": attempt.total_questions,
        "remaining_seconds": int(remaining),
        "tab_switches": attempt.tab_switches,
        "violations": attempt.proctoring_violations
    }


def get_current_student():
    """Get current logged in student"""
    return frappe.db.get_value("Student", {"user": frappe.session.user})
