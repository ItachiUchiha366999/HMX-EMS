# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class LMSQuiz(Document):
    def validate(self):
        self.validate_questions()
        self.calculate_total_marks()
        self.validate_dates()

    def validate_questions(self):
        """Validate quiz has questions"""
        if not self.questions:
            frappe.throw(_("Quiz must have at least one question"))

        for q in self.questions:
            if q.question_type in ["Multiple Choice", "Multiple Select", "True/False"]:
                if not q.options:
                    frappe.throw(_("Options are required for {0} questions").format(q.question_type))

                # Check if correct answer is marked
                if q.question_type in ["Multiple Choice", "True/False"]:
                    options = q.options.split("\n")
                    correct_count = sum(1 for o in options if o.strip().startswith("*"))
                    if correct_count != 1:
                        frappe.throw(_("Exactly one correct answer must be marked for Multiple Choice/True-False questions"))

    def calculate_total_marks(self):
        """Calculate total marks from questions"""
        self.total_marks = sum(q.marks or 0 for q in self.questions)

    def validate_dates(self):
        """Validate availability dates"""
        if self.available_from and self.available_until:
            if get_datetime(self.available_from) > get_datetime(self.available_until):
                frappe.throw(_("Available Until cannot be before Available From"))

    def is_available(self):
        """Check if quiz is currently available"""
        if self.docstatus != 1:
            return False

        current_time = now_datetime()

        if self.available_from and get_datetime(self.available_from) > current_time:
            return False

        if self.available_until and get_datetime(self.available_until) < current_time:
            return False

        return True


@frappe.whitelist()
def get_available_quizzes(lms_course=None, student=None):
    """Get available quizzes for a course"""
    filters = {"docstatus": 1}

    if lms_course:
        filters["lms_course"] = lms_course

    quizzes = frappe.get_all("LMS Quiz",
        filters=filters,
        fields=["name", "title", "lms_course", "quiz_type", "total_marks",
                "passing_marks", "time_limit_minutes", "max_attempts",
                "available_from", "available_until"]
    )

    if student:
        for quiz in quizzes:
            attempts = frappe.get_all("Quiz Attempt",
                filters={"quiz": quiz.name, "student": student},
                fields=["name", "status", "marks_obtained", "percentage", "passed"],
                order_by="attempt_number desc"
            )
            quiz["attempts"] = attempts
            quiz["remaining_attempts"] = quiz.max_attempts - len(attempts)

    return quizzes


@frappe.whitelist()
def start_quiz(quiz_name, student):
    """Start a quiz attempt"""
    quiz = frappe.get_doc("LMS Quiz", quiz_name)

    if not quiz.is_available():
        frappe.throw(_("This quiz is not currently available"))

    # Check attempts
    existing_attempts = frappe.db.count("Quiz Attempt", {
        "quiz": quiz_name,
        "student": student
    })

    if existing_attempts >= quiz.max_attempts:
        frappe.throw(_("Maximum attempts ({0}) reached for this quiz").format(quiz.max_attempts))

    # Check for in-progress attempt
    in_progress = frappe.db.exists("Quiz Attempt", {
        "quiz": quiz_name,
        "student": student,
        "status": "In Progress"
    })

    if in_progress:
        return {"attempt": in_progress, "message": _("Resuming existing attempt")}

    # Create new attempt
    import random

    attempt = frappe.get_doc({
        "doctype": "Quiz Attempt",
        "quiz": quiz_name,
        "student": student,
        "attempt_number": existing_attempts + 1,
        "start_time": now_datetime(),
        "status": "In Progress",
        "total_questions": len(quiz.questions),
        "total_marks": quiz.total_marks
    })

    # Prepare questions (optionally shuffled)
    questions = list(quiz.questions)
    if quiz.shuffle_questions:
        random.shuffle(questions)

    for idx, q in enumerate(questions, 1):
        options = q.options
        if quiz.shuffle_options and q.question_type in ["Multiple Choice", "Multiple Select"]:
            option_lines = options.split("\n")
            random.shuffle(option_lines)
            options = "\n".join(option_lines)

        # Get correct answer for auto-grading
        correct = ""
        if q.question_type in ["Multiple Choice", "Multiple Select", "True/False"]:
            for opt in (q.options or "").split("\n"):
                if opt.strip().startswith("*"):
                    correct = opt.strip()[1:].strip()
                    break
        else:
            correct = q.correct_answer or ""

        attempt.append("answers", {
            "question_idx": idx,
            "question_text": frappe.utils.strip_html_tags(q.question_text)[:500],
            "question_type": q.question_type,
            "correct_answer": correct
        })

    attempt.insert()

    return {
        "attempt": attempt.name,
        "questions": [{
            "idx": idx,
            "question": q.question_text,
            "type": q.question_type,
            "marks": q.marks,
            "options": q.options,
            "image": q.image
        } for idx, q in enumerate(questions, 1)],
        "time_limit": quiz.time_limit_minutes
    }


@frappe.whitelist()
def submit_quiz(attempt_name, answers):
    """Submit quiz answers and calculate results"""
    import json

    if isinstance(answers, str):
        answers = json.loads(answers)

    attempt = frappe.get_doc("Quiz Attempt", attempt_name)

    if attempt.status != "In Progress":
        frappe.throw(_("This quiz attempt has already been submitted"))

    attempt.end_time = now_datetime()

    # Calculate time taken
    start = get_datetime(attempt.start_time)
    end = get_datetime(attempt.end_time)
    attempt.time_taken_minutes = int((end - start).total_seconds() / 60)

    # Get quiz for auto-grading
    quiz = frappe.get_doc("LMS Quiz", attempt.quiz)

    # Grade answers
    total_marks = 0
    correct_count = 0
    attempted = 0

    for answer in attempt.answers:
        student_answer = answers.get(str(answer.question_idx), "")
        answer.student_answer = student_answer

        if student_answer:
            attempted += 1

        # Auto-grade
        is_correct = False
        question = quiz.questions[answer.question_idx - 1]

        if question.question_type in ["Multiple Choice", "True/False"]:
            correct = answer.correct_answer
            is_correct = student_answer.strip().lower() == correct.strip().lower()

        elif question.question_type == "Short Answer":
            correct = question.correct_answer or ""
            is_correct = student_answer.strip().lower() == correct.strip().lower()

        elif question.question_type == "Fill in Blank":
            correct = question.correct_answer or ""
            is_correct = student_answer.strip().lower() == correct.strip().lower()

        if is_correct:
            answer.is_correct = 1
            answer.marks_obtained = question.marks
            total_marks += question.marks
            correct_count += 1
        else:
            answer.is_correct = 0
            if student_answer and question.negative_marks:
                answer.marks_obtained = -question.negative_marks
                total_marks -= question.negative_marks
            else:
                answer.marks_obtained = 0

    attempt.marks_obtained = max(0, total_marks)
    attempt.attempted = attempted
    attempt.correct = correct_count
    attempt.percentage = (attempt.marks_obtained / attempt.total_marks * 100) if attempt.total_marks else 0
    attempt.passed = 1 if quiz.passing_marks and attempt.marks_obtained >= quiz.passing_marks else 0
    attempt.status = "Graded"

    attempt.save()

    return {
        "marks_obtained": attempt.marks_obtained,
        "total_marks": attempt.total_marks,
        "percentage": attempt.percentage,
        "passed": attempt.passed,
        "correct": correct_count,
        "attempted": attempted,
        "total_questions": attempt.total_questions
    }


@frappe.whitelist()
def get_quiz_results(attempt_name):
    """Get quiz results with answers"""
    attempt = frappe.get_doc("Quiz Attempt", attempt_name)

    if attempt.status == "In Progress":
        frappe.throw(_("Quiz attempt is still in progress"))

    quiz = frappe.get_doc("LMS Quiz", attempt.quiz)

    result = {
        "marks_obtained": attempt.marks_obtained,
        "total_marks": attempt.total_marks,
        "percentage": attempt.percentage,
        "passed": attempt.passed,
        "time_taken": attempt.time_taken_minutes,
        "correct": attempt.correct,
        "attempted": attempt.attempted,
        "total_questions": attempt.total_questions
    }

    if quiz.show_correct_answers or quiz.allow_review:
        result["answers"] = []
        for ans in attempt.answers:
            answer_detail = {
                "question_idx": ans.question_idx,
                "question_text": ans.question_text,
                "student_answer": ans.student_answer,
                "is_correct": ans.is_correct,
                "marks_obtained": ans.marks_obtained
            }
            if quiz.show_correct_answers:
                answer_detail["correct_answer"] = ans.correct_answer
            result["answers"].append(answer_detail)

    return result
