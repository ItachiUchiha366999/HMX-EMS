"""
Student Exam Attempt DocType Controller

Tracks individual student attempts at online examinations including
answers, timing, scoring, and proctoring data.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds
import json


class StudentExamAttempt(Document):
    """Controller for Student Exam Attempt DocType"""

    def validate(self):
        """Validate the attempt"""
        self.calculate_time_taken()

    def on_update(self):
        """Actions on update"""
        # Update exam statistics
        if self.online_examination:
            exam = frappe.get_doc("Online Examination", self.online_examination)
            exam.update_statistics()
            exam.db_update()

    def calculate_time_taken(self):
        """Calculate time taken in minutes"""
        if self.start_time and self.end_time:
            seconds = time_diff_in_seconds(self.end_time, self.start_time)
            self.time_taken_minutes = max(0, int(seconds / 60))

    def calculate_score(self):
        """Calculate score from answers (for auto-evaluated questions)"""
        total_marks = 0
        marks_obtained = 0
        correct = 0
        incorrect = 0
        negative_applied = 0

        for ans in self.answers:
            question = frappe.get_cached_doc("Question Bank", ans.question)

            # Get marks for this question
            q_marks = self._get_question_marks(ans.question)
            total_marks += q_marks

            if ans.is_correct:
                marks_obtained += ans.marks_obtained or q_marks
                correct += 1
            elif ans.answer:
                # Wrong answer
                incorrect += 1
                if question.negative_marking:
                    negative_applied += question.negative_marks or 0

        self.total_marks = total_marks
        self.marks_obtained = marks_obtained - negative_applied
        self.negative_marks_applied = negative_applied
        self.correct = correct
        self.incorrect = incorrect
        self.attempted = len([a for a in self.answers if a.answer])
        self.percentage = (self.marks_obtained / total_marks * 100) if total_marks > 0 else 0

    def _get_question_marks(self, question_id):
        """Get marks for a question from the paper"""
        exam = frappe.get_doc("Online Examination", self.online_examination)
        paper = frappe.get_doc("Generated Question Paper", exam.question_paper)

        for q in paper.paper_questions:
            if q.question == question_id:
                return q.marks or 0

        return 0

    @frappe.whitelist()
    def save_answer(self, question_id: str, answer, marked_for_review: bool = False):
        """
        Save an answer for a question

        Args:
            question_id: Question Bank name
            answer: Student's answer (string or list for MCQ/MSQ)
            marked_for_review: Whether to mark for review
        """
        if self.status not in ["In Progress", "Not Started"]:
            frappe.throw(_("Cannot save answer - exam is not in progress"))

        # Encode answer as JSON if it's a list
        answer_str = json.dumps(answer) if isinstance(answer, (list, dict)) else str(answer)

        # Find existing answer or create new
        existing = None
        for ans in self.answers:
            if ans.question == question_id:
                existing = ans
                break

        if existing:
            existing.answer = answer_str
            existing.marked_for_review = marked_for_review
            existing.answer_time = now_datetime()
        else:
            self.append("answers", {
                "question": question_id,
                "answer": answer_str,
                "marked_for_review": marked_for_review,
                "answer_time": now_datetime()
            })

        self.attempted = len([a for a in self.answers if a.answer])
        self.save()

    @frappe.whitelist()
    def submit_exam(self):
        """Submit the examination"""
        if self.status not in ["In Progress", "Not Started"]:
            frappe.throw(_("Exam already submitted or not started"))

        self.end_time = now_datetime()
        self.calculate_time_taken()
        self.status = "Submitted"
        self.submit_type = "Manual"

        # Auto-evaluate if possible
        if self._can_auto_evaluate():
            self._auto_evaluate()

        self.save()

        return {
            "status": "submitted",
            "marks_obtained": self.marks_obtained,
            "total_marks": self.total_marks,
            "percentage": self.percentage
        }

    def auto_submit(self, reason="Time Expired"):
        """Auto-submit on time expiry or violation"""
        if self.status != "In Progress":
            return

        self.end_time = now_datetime()
        self.calculate_time_taken()
        self.status = "Auto Submitted"
        self.submit_type = f"Auto ({reason})"

        if self._can_auto_evaluate():
            self._auto_evaluate()

        self.save()

    def _can_auto_evaluate(self):
        """Check if all questions can be auto-evaluated"""
        auto_types = [
            "Multiple Choice (MCQ)",
            "Multiple Select (MSQ)",
            "True/False",
            "Numerical",
            "Fill in the Blanks"
        ]

        for ans in self.answers:
            question = frappe.get_cached_doc("Question Bank", ans.question)
            if question.question_type not in auto_types:
                return False

        return True

    def _auto_evaluate(self):
        """Auto-evaluate objective questions"""
        total_marks = 0
        marks_obtained = 0
        correct = 0
        incorrect = 0
        negative_applied = 0

        for ans in self.answers:
            question = frappe.get_cached_doc("Question Bank", ans.question)
            q_marks = self._get_question_marks(ans.question)
            total_marks += q_marks

            is_correct, partial_marks = self._check_answer(question, ans.answer)

            if is_correct:
                marks_obtained += q_marks
                correct += 1
                ans.marks_obtained = q_marks
                ans.is_correct = True
            elif partial_marks > 0:
                marks_obtained += partial_marks
                ans.marks_obtained = partial_marks
                ans.is_correct = False
            else:
                if question.negative_marking and ans.answer:
                    negative_applied += question.negative_marks or 0
                if ans.answer:
                    incorrect += 1
                ans.marks_obtained = 0
                ans.is_correct = False

        self.total_marks = total_marks
        self.marks_obtained = max(0, marks_obtained - negative_applied)
        self.negative_marks_applied = negative_applied
        self.correct = correct
        self.incorrect = incorrect
        self.percentage = (self.marks_obtained / total_marks * 100) if total_marks > 0 else 0
        self.status = "Evaluated"
        self.evaluation_date = now_datetime()

    def _check_answer(self, question, answer_str: str):
        """
        Check if answer is correct

        Returns:
            (is_correct: bool, partial_marks: float)
        """
        if not answer_str:
            return False, 0

        try:
            student_answer = json.loads(answer_str) if answer_str.startswith('[') else answer_str
        except:
            student_answer = answer_str

        if question.question_type == "Multiple Choice (MCQ)":
            correct_option = None
            for opt in question.options:
                if opt.is_correct:
                    correct_option = opt.option_label
                    break
            return student_answer == correct_option, 0

        elif question.question_type == "Multiple Select (MSQ)":
            correct_options = set(opt.option_label for opt in question.options if opt.is_correct)
            student_options = set(student_answer) if isinstance(student_answer, list) else {student_answer}

            if student_options == correct_options:
                return True, 0

            # Partial marking
            if question.partial_marking:
                correct_selected = len(student_options & correct_options)
                incorrect_selected = len(student_options - correct_options)
                total_correct = len(correct_options)

                if incorrect_selected == 0 and correct_selected > 0:
                    partial = (correct_selected / total_correct) * question.marks
                    return False, partial

            return False, 0

        elif question.question_type == "True/False":
            correct_answer = question.correct_answer.strip().lower() if question.correct_answer else ""
            return student_answer.lower() == correct_answer, 0

        elif question.question_type == "Numerical":
            try:
                student_val = float(student_answer)
                correct_val = float(question.correct_answer.strip())
                # Allow 1% tolerance
                tolerance = abs(correct_val * 0.01) if correct_val != 0 else 0.01
                return abs(student_val - correct_val) <= tolerance, 0
            except:
                return False, 0

        elif question.question_type == "Fill in the Blanks":
            correct_answers = [a.strip().lower() for a in (question.correct_answer or "").split(',')]
            return student_answer.strip().lower() in correct_answers, 0

        return False, 0

    @frappe.whitelist()
    def record_tab_switch(self):
        """Record a tab switch event"""
        self.tab_switches = (self.tab_switches or 0) + 1

        exam = frappe.get_doc("Online Examination", self.online_examination)

        if self.tab_switches > exam.max_tab_switches:
            self.proctoring_violations = (self.proctoring_violations or 0) + 1

            # Disqualify if too many violations
            if self.proctoring_violations >= 3:
                self.status = "Disqualified"
                self.remarks = "Disqualified due to multiple proctoring violations"

        self.save()

        return {
            "tab_switches": self.tab_switches,
            "max_allowed": exam.max_tab_switches,
            "violations": self.proctoring_violations
        }

    @frappe.whitelist()
    def add_proctoring_snapshot(self, image_data: str, event_type: str = "Random Capture"):
        """
        Add a proctoring snapshot

        Args:
            image_data: Base64 encoded image
            event_type: Type of capture event
        """
        self.append("proctoring_snapshots", {
            "timestamp": now_datetime(),
            "snapshot_image": image_data,
            "event_type": event_type
        })
        self.save()
