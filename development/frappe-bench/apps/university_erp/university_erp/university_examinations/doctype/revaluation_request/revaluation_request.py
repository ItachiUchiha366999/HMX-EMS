"""
Revaluation Request DocType Controller

Handles student requests for answer sheet revaluation.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class RevaluationRequest(Document):
    """Controller for Revaluation Request DocType"""

    def validate(self):
        """Validate the request"""
        self.validate_answer_sheet()
        self.fetch_original_marks()
        self.calculate_difference()

    def before_submit(self):
        """Actions before submission"""
        self.status = "Pending"

        # Update answer sheet status
        answer_sheet = frappe.get_doc("Answer Sheet", self.answer_sheet)
        answer_sheet.status = "Revaluation Requested"
        answer_sheet.add_tracking_entry(
            "Revaluation Requested",
            remarks=f"Request: {self.name}"
        )

    def validate_answer_sheet(self):
        """Validate the answer sheet"""
        sheet = frappe.get_doc("Answer Sheet", self.answer_sheet)

        # Verify student owns this sheet
        if sheet.student != self.student:
            frappe.throw(_("You can only request revaluation for your own answer sheet"))

        # Check if already under revaluation
        if sheet.status == "Revaluation Requested":
            frappe.throw(_("Revaluation already requested for this answer sheet"))

        # Check if evaluation is complete
        if sheet.status not in ["Evaluated", "Moderated", "Result Published"]:
            frappe.throw(_("Answer sheet must be evaluated before requesting revaluation"))

    def fetch_original_marks(self):
        """Fetch original marks from answer sheet"""
        if not self.original_marks:
            sheet = frappe.get_doc("Answer Sheet", self.answer_sheet)
            self.original_marks = sheet.marks_after_moderation or sheet.marks_obtained

    def calculate_difference(self):
        """Calculate marks difference"""
        if self.revaluation_marks is not None and self.original_marks is not None:
            self.marks_difference = self.revaluation_marks - self.original_marks

    @frappe.whitelist()
    def assign_evaluator(self, evaluator: str):
        """
        Assign an evaluator for revaluation

        Args:
            evaluator: Faculty Member name
        """
        self.assigned_evaluator = evaluator
        self.status = "In Progress"
        self.save()

    @frappe.whitelist()
    def complete_revaluation(self, new_marks: float, remarks: str = None):
        """
        Complete the revaluation

        Args:
            new_marks: New marks after revaluation
            remarks: Evaluator remarks
        """
        self.revaluation_marks = new_marks
        self.calculate_difference()
        self.evaluation_date = now_datetime()
        self.decision_date = now_datetime()
        self.status = "Completed"

        if remarks:
            self.decision_remarks = remarks

        self.save()

        # Update answer sheet
        answer_sheet = frappe.get_doc("Answer Sheet", self.answer_sheet)
        answer_sheet.marks_after_moderation = new_marks
        answer_sheet.status = "Revaluation Done"
        answer_sheet.add_tracking_entry(
            "Revaluation Completed",
            remarks=f"New marks: {new_marks}. Difference: {self.marks_difference}"
        )

    @frappe.whitelist()
    def reject_request(self, reason: str):
        """
        Reject the revaluation request

        Args:
            reason: Rejection reason
        """
        self.status = "Rejected"
        self.decision_date = now_datetime()
        self.decision_remarks = f"Rejected: {reason}"
        self.save()

        # Update answer sheet status back
        answer_sheet = frappe.get_doc("Answer Sheet", self.answer_sheet)
        answer_sheet.status = answer_sheet.status.replace("Revaluation Requested", "Result Published")
        answer_sheet.add_tracking_entry(
            "Revaluation Rejected",
            remarks=reason
        )
