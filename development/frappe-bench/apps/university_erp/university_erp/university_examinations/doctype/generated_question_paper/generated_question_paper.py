"""
Generated Question Paper DocType Controller

Represents a generated question paper with selected questions,
approval workflow, and print/export capabilities.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class GeneratedQuestionPaper(Document):
    """Controller for Generated Question Paper DocType"""

    def validate(self):
        """Validate the question paper"""
        self.validate_questions()
        self.calculate_totals()
        self.set_created_by()

    def before_submit(self):
        """Actions before submission"""
        if self.status not in ["Approved", "Locked"]:
            frappe.throw(_("Only Approved or Locked papers can be submitted"))

    def on_submit(self):
        """Actions on submission"""
        self.status = "Locked"
        self.update_question_usage()

    def validate_questions(self):
        """Validate that questions are properly assigned"""
        if not self.paper_questions:
            frappe.throw(_("At least one question is required"))

        # Check for duplicate questions
        question_ids = [q.question for q in self.paper_questions]
        if len(question_ids) != len(set(question_ids)):
            frappe.throw(_("Duplicate questions found in the paper"))

        # Validate all questions belong to the same course
        for q in self.paper_questions:
            question_course = frappe.db.get_value("Question Bank", q.question, "course")
            if question_course != self.course:
                frappe.throw(
                    _("Question {0} does not belong to course {1}").format(q.question, self.course)
                )

    def calculate_totals(self):
        """Calculate total questions and marks"""
        self.total_questions = len(self.paper_questions)

        # Calculate total marks
        total = 0
        for q in self.paper_questions:
            total += q.marks or 0

        if total != self.total_marks:
            frappe.msgprint(
                _("Total marks from questions ({0}) does not match paper total ({1})").format(
                    total, self.total_marks
                ),
                indicator="orange"
            )

    def set_created_by(self):
        """Set the created_by field"""
        if not self.created_by:
            faculty = frappe.db.get_value(
                "Instructor",
                {"user": frappe.session.user},
                "name"
            )
            if faculty:
                self.created_by = faculty

    def update_question_usage(self):
        """Update usage statistics for all questions in the paper"""
        from frappe.utils import today

        for q in self.paper_questions:
            frappe.db.sql("""
                UPDATE `tabQuestion Bank`
                SET times_used = times_used + 1,
                    last_used_date = %s
                WHERE name = %s
            """, (today(), q.question))

    @frappe.whitelist()
    def submit_for_review(self):
        """Submit paper for review"""
        if self.status != "Draft":
            frappe.throw(_("Only Draft papers can be submitted for review"))

        self.status = "Ready for Review"
        self.save()
        frappe.msgprint(_("Paper submitted for review"))

    @frappe.whitelist()
    def approve_paper(self):
        """Approve the question paper"""
        if self.status != "Ready for Review":
            frappe.throw(_("Only papers Ready for Review can be approved"))

        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = now_datetime()
        self.save()
        frappe.msgprint(_("Question paper approved"))

    @frappe.whitelist()
    def lock_paper(self):
        """Lock the paper to prevent further changes"""
        if self.status not in ["Approved", "Draft"]:
            frappe.throw(_("Only Approved or Draft papers can be locked"))

        self.status = "Locked"
        self.save()
        frappe.msgprint(_("Question paper locked"))

    @frappe.whitelist()
    def mark_as_used(self):
        """Mark the paper as used in an examination"""
        if self.status != "Locked":
            frappe.throw(_("Only Locked papers can be marked as used"))

        self.status = "Used"
        self.save()

    def get_question_details(self):
        """
        Get detailed information for all questions

        Returns:
            List of question details
        """
        details = []

        for q in self.paper_questions:
            question = frappe.get_doc("Question Bank", q.question)
            details.append({
                "question_number": q.question_number,
                "question_id": q.question,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "marks": q.marks,
                "difficulty": question.difficulty_level,
                "bloom_level": question.blooms_taxonomy,
                "options": [
                    {
                        "label": opt.option_label,
                        "text": opt.option_text,
                        "is_correct": opt.is_correct
                    }
                    for opt in question.options
                ] if question.options else [],
                "correct_answer": question.correct_answer,
                "image": question.question_image
            })

        return details

    @frappe.whitelist()
    def generate_pdf(self):
        """
        Generate PDF of the question paper

        Returns:
            PDF file path or URL
        """
        # This would integrate with Frappe's print format system
        # For now, return a placeholder
        return frappe.utils.get_url_to_form(self.doctype, self.name) + "?format=pdf"


@frappe.whitelist()
def create_paper_from_template(template_name, set_code=None, exam_date=None, academic_year=None):
    """
    Create a question paper from a template

    Args:
        template_name: Question Paper Template name
        set_code: Optional set identifier
        exam_date: Optional exam date
        academic_year: Academic year

    Returns:
        Generated Question Paper name
    """
    from university_erp.university_erp.examination.question_paper_generator import QuestionPaperGenerator

    generator = QuestionPaperGenerator(template_name)
    return generator.generate_paper(set_code, exam_date)
