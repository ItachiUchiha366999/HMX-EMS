"""
Question Bank DocType Controller

Manages the question bank for examinations with support for various
question types, difficulty levels, and Bloom's taxonomy classification.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class QuestionBank(Document):
    """Controller for Question Bank DocType"""

    def validate(self):
        """Validate the question"""
        self.validate_options()
        self.validate_correct_answer()
        self.validate_marks()

    def before_save(self):
        """Actions before saving"""
        self.set_created_by()

    def validate_options(self):
        """Validate options for MCQ/MSQ type questions"""
        option_types = ["Multiple Choice (MCQ)", "Multiple Select (MSQ)", "True/False", "Match the Following"]

        if self.question_type in option_types:
            if not self.options or len(self.options) < 2:
                frappe.throw(
                    _("At least 2 options are required for {0} type questions").format(self.question_type)
                )

            # Check for at least one correct option
            correct_count = sum(1 for opt in self.options if opt.is_correct)

            if self.question_type == "Multiple Choice (MCQ)":
                if correct_count != 1:
                    frappe.throw(_("MCQ must have exactly one correct option"))

            elif self.question_type == "Multiple Select (MSQ)":
                if correct_count < 1:
                    frappe.throw(_("MSQ must have at least one correct option"))

            elif self.question_type == "True/False":
                if len(self.options) != 2:
                    frappe.throw(_("True/False questions must have exactly 2 options"))
                if correct_count != 1:
                    frappe.throw(_("True/False must have exactly one correct option"))

            elif self.question_type == "Match the Following":
                # Validate match_with field is filled for all options
                for opt in self.options:
                    if not opt.match_with:
                        frappe.throw(
                            _("Match With field is required for all options in Match the Following type")
                        )

            # Validate option labels
            self.validate_option_labels()

    def validate_option_labels(self):
        """Ensure option labels are unique and properly set"""
        labels = []
        default_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]

        for idx, opt in enumerate(self.options):
            if not opt.option_label:
                if idx < len(default_labels):
                    opt.option_label = default_labels[idx]
                else:
                    opt.option_label = str(idx + 1)

            if opt.option_label in labels:
                frappe.throw(_("Duplicate option label: {0}").format(opt.option_label))
            labels.append(opt.option_label)

    def validate_correct_answer(self):
        """Validate correct answer for non-option type questions"""
        non_option_types = ["Short Answer", "Long Answer", "Numerical", "Fill in the Blanks", "Case Study"]

        if self.question_type in non_option_types:
            if not self.correct_answer and self.status == "Approved":
                frappe.msgprint(
                    _("Consider adding a model answer for {0} type questions").format(self.question_type),
                    indicator="orange"
                )

    def validate_marks(self):
        """Validate marks"""
        if self.marks <= 0:
            frappe.throw(_("Marks must be greater than 0"))

        if self.negative_marking and self.negative_marks:
            if self.negative_marks >= self.marks:
                frappe.throw(_("Negative marks should be less than total marks"))

    def set_created_by(self):
        """Set the created_by_faculty field"""
        if not self.created_by_faculty:
            # Try to get faculty member linked to current user
            faculty = frappe.db.get_value(
                "Instructor",
                {"user": frappe.session.user},
                "name"
            )
            if faculty:
                self.created_by_faculty = faculty

    @frappe.whitelist()
    def submit_for_review(self):
        """Submit question for review"""
        if self.status != "Draft":
            frappe.throw(_("Only Draft questions can be submitted for review"))

        self.status = "Pending Review"
        self.save()
        frappe.msgprint(_("Question submitted for review"))

    @frappe.whitelist()
    def approve_question(self):
        """Approve the question"""
        if self.status != "Pending Review":
            frappe.throw(_("Only questions Pending Review can be approved"))

        self.status = "Approved"
        self.reviewed_by = frappe.db.get_value(
            "Instructor",
            {"user": frappe.session.user},
            "name"
        )
        self.save()
        frappe.msgprint(_("Question approved"))

    @frappe.whitelist()
    def reject_question(self, reason=None):
        """Reject the question"""
        if self.status != "Pending Review":
            frappe.throw(_("Only questions Pending Review can be rejected"))

        self.status = "Rejected"
        self.reviewed_by = frappe.db.get_value(
            "Instructor",
            {"user": frappe.session.user},
            "name"
        )
        if reason:
            frappe.db.set_value(self.doctype, self.name, "answer_explanation",
                               f"Rejection Reason: {reason}\n\n{self.answer_explanation or ''}")
        self.save()
        frappe.msgprint(_("Question rejected"))

    @frappe.whitelist()
    def retire_question(self):
        """Retire the question from active use"""
        if self.status not in ["Approved", "Draft"]:
            frappe.throw(_("Only Approved or Draft questions can be retired"))

        self.status = "Retired"
        self.save()
        frappe.msgprint(_("Question retired"))

    def update_usage_stats(self, score_percentage=None):
        """
        Update usage statistics for the question

        Args:
            score_percentage: Optional - percentage of students who answered correctly
        """
        self.times_used = (self.times_used or 0) + 1
        self.last_used_date = today()

        if score_percentage is not None:
            # Calculate running average
            if self.average_score_percentage and self.times_used > 1:
                self.average_score_percentage = (
                    (self.average_score_percentage * (self.times_used - 1) + score_percentage)
                    / self.times_used
                )
            else:
                self.average_score_percentage = score_percentage

        self.db_update()

    def get_difficulty_score(self):
        """
        Get difficulty score based on average performance

        Returns:
            str: Difficulty level based on performance
        """
        if not self.average_score_percentage:
            return self.difficulty_level

        # Adjust difficulty based on actual performance
        if self.average_score_percentage >= 80:
            return "Easy"
        elif self.average_score_percentage >= 60:
            return "Medium"
        elif self.average_score_percentage >= 40:
            return "Hard"
        else:
            return "Very Hard"


def get_questions_for_course(course, filters=None):
    """
    Get approved questions for a course

    Args:
        course: Course name
        filters: Optional additional filters

    Returns:
        List of Question Bank records
    """
    query_filters = {
        "course": course,
        "status": "Approved"
    }

    if filters:
        query_filters.update(filters)

    return frappe.get_all("Question Bank",
        filters=query_filters,
        fields=["name", "question_type", "difficulty_level", "blooms_taxonomy",
                "unit", "marks", "times_used", "last_used_date", "average_score_percentage"]
    )


def get_question_count_by_type(course):
    """
    Get count of questions by type for a course

    Args:
        course: Course name

    Returns:
        Dict with question type counts
    """
    counts = frappe.db.sql("""
        SELECT question_type, COUNT(*) as count
        FROM `tabQuestion Bank`
        WHERE course = %s AND status = 'Approved'
        GROUP BY question_type
    """, course, as_dict=True)

    return {c.question_type: c.count for c in counts}


def get_question_count_by_difficulty(course):
    """
    Get count of questions by difficulty for a course

    Args:
        course: Course name

    Returns:
        Dict with difficulty level counts
    """
    counts = frappe.db.sql("""
        SELECT difficulty_level, COUNT(*) as count
        FROM `tabQuestion Bank`
        WHERE course = %s AND status = 'Approved'
        GROUP BY difficulty_level
    """, course, as_dict=True)

    return {c.difficulty_level: c.count for c in counts}
