"""
Answer Sheet DocType Controller

Tracks physical answer sheets through collection, evaluation, and moderation.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, random_string


class AnswerSheet(Document):
    """Controller for Answer Sheet DocType"""

    def validate(self):
        """Validate the answer sheet"""
        self.calculate_percentage()

    def before_insert(self):
        """Generate barcode before insert"""
        if not self.barcode:
            self.generate_barcode()

    def calculate_percentage(self):
        """Calculate percentage from marks"""
        if self.marks_obtained is not None and self.total_marks:
            final_marks = self.marks_after_moderation or self.marks_obtained
            final_marks = final_marks + (self.grace_marks or 0)
            self.percentage = (final_marks / self.total_marks * 100) if self.total_marks > 0 else 0

    def generate_barcode(self):
        """Generate unique barcode for the answer sheet"""
        exam_code = self.examination[:5] if self.examination else "EXAM"
        roll = self.roll_number or "000"
        random_part = random_string(4).upper()
        self.barcode = f"AS-{exam_code}-{roll}-{random_part}"

    @frappe.whitelist()
    def add_tracking_entry(self, action: str, location: str = None, remarks: str = None):
        """
        Add a tracking entry

        Args:
            action: Action performed
            location: Current location
            remarks: Additional remarks
        """
        self.append("tracking_history", {
            "action": action,
            "timestamp": now_datetime(),
            "location": location,
            "performed_by": frappe.session.user,
            "remarks": remarks
        })

        if location:
            self.current_location = location

        # Update status based on action
        status_mapping = {
            "Collected": "Collected",
            "Dispatched": "In Transit",
            "Received": "Received at Evaluation Center",
            "Assigned": "Assigned for Evaluation",
            "Evaluation Started": "Evaluation In Progress",
            "Evaluation Completed": "Evaluated",
            "Sent for Moderation": "Pending Moderation",
            "Moderation Completed": "Moderated",
            "Result Published": "Result Published"
        }

        if action in status_mapping:
            self.status = status_mapping[action]

        self.save()

    @frappe.whitelist()
    def assign_evaluator(self, evaluator: str):
        """
        Assign an evaluator to this answer sheet

        Args:
            evaluator: Faculty Member name
        """
        self.assigned_to = evaluator
        self.assignment_date = now_datetime()
        self.status = "Assigned for Evaluation"

        self.add_tracking_entry(
            "Assigned",
            f"Evaluator: {evaluator}",
            f"Assigned to {evaluator}"
        )

    @frappe.whitelist()
    def start_evaluation(self):
        """Mark evaluation as started"""
        self.evaluation_started = now_datetime()
        self.status = "Evaluation In Progress"
        self.add_tracking_entry("Evaluation Started")

    @frappe.whitelist()
    def record_scores(self, scores: list):
        """
        Record question-wise scores

        Args:
            scores: List of {question_number, max_marks, marks_obtained, comments}
        """
        # Clear existing scores
        self.question_scores = []

        total_marks = 0
        marks_obtained = 0

        for score in scores:
            self.append("question_scores", {
                "question_number": score.get("question_number"),
                "max_marks": score.get("max_marks", 0),
                "marks_obtained": score.get("marks_obtained", 0),
                "comments": score.get("comments")
            })

            total_marks += score.get("max_marks", 0)
            marks_obtained += score.get("marks_obtained", 0)

        self.total_marks = total_marks
        self.marks_obtained = marks_obtained
        self.calculate_percentage()

        self.evaluation_completed = now_datetime()
        self.status = "Evaluated"

        self.add_tracking_entry(
            "Evaluation Completed",
            remarks=f"Marks: {marks_obtained}/{total_marks}"
        )

    @frappe.whitelist()
    def moderate(self, new_marks: float = None, moderator: str = None, remarks: str = None):
        """
        Apply moderation to the answer sheet

        Args:
            new_marks: Moderated marks (if different)
            moderator: Faculty Member doing moderation
            remarks: Moderation remarks
        """
        if new_marks is not None:
            self.marks_after_moderation = new_marks

        self.moderated_by = moderator or frappe.db.get_value(
            "Instructor",
            {"user": frappe.session.user},
            "name"
        )
        self.moderation_date = now_datetime()
        self.status = "Moderated"

        self.calculate_percentage()

        self.add_tracking_entry(
            "Moderation Completed",
            remarks=remarks or f"Moderated marks: {new_marks}"
        )

    @frappe.whitelist()
    def apply_grace_marks(self, grace_marks: float, reason: str = None):
        """
        Apply grace marks

        Args:
            grace_marks: Grace marks to add
            reason: Reason for grace marks
        """
        self.grace_marks = grace_marks
        self.calculate_percentage()
        self.save()

        self.add_tracking_entry(
            "Grace Marks Applied",
            remarks=f"Grace marks: {grace_marks}. Reason: {reason or 'Not specified'}"
        )


@frappe.whitelist()
def bulk_create_answer_sheets(examination: str, course: str):
    """
    Create answer sheets for all registered students

    Args:
        examination: Examination name
        course: Course name

    Returns:
        Number of sheets created
    """
    # Get enrolled students (this would typically come from exam registration)
    # For now, get students enrolled in the course
    students = frappe.get_all("Student",
        filters={"enabled": 1},
        fields=["name", "roll_number"]
    )

    count = 0
    for student in students:
        # Check if sheet already exists
        existing = frappe.db.exists("Answer Sheet", {
            "examination": examination,
            "course": course,
            "student": student.name
        })

        if not existing:
            sheet = frappe.new_doc("Answer Sheet")
            sheet.examination = examination
            sheet.course = course
            sheet.student = student.name
            sheet.roll_number = student.roll_number
            sheet.status = "Collected"
            sheet.collection_datetime = now_datetime()
            sheet.collected_by = frappe.session.user
            sheet.insert()
            count += 1

    frappe.db.commit()
    return count


@frappe.whitelist()
def assign_sheets_to_evaluator(sheets: list, evaluator: str):
    """
    Assign multiple answer sheets to an evaluator

    Args:
        sheets: List of answer sheet names
        evaluator: Faculty Member name

    Returns:
        Number of sheets assigned
    """
    if isinstance(sheets, str):
        import json
        sheets = json.loads(sheets)

    count = 0
    for sheet_name in sheets:
        sheet = frappe.get_doc("Answer Sheet", sheet_name)
        if sheet.status in ["Received at Evaluation Center", "Collected"]:
            sheet.assign_evaluator(evaluator)
            count += 1

    return count
