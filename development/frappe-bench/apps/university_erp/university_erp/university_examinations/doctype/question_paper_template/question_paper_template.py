"""
Question Paper Template DocType Controller

Defines the structure and rules for generating question papers
including sections, marks distribution, and question selection criteria.
"""

import frappe
from frappe import _
from frappe.model.document import Document


class QuestionPaperTemplate(Document):
    """Controller for Question Paper Template DocType"""

    def validate(self):
        """Validate the template"""
        self.validate_sections()
        self.validate_marks()
        self.validate_distribution()
        self.calculate_section_marks()

    def validate_sections(self):
        """Validate sections configuration"""
        if not self.sections:
            frappe.throw(_("At least one section is required"))

        for section in self.sections:
            if section.questions_to_attempt > section.total_questions:
                frappe.throw(
                    _("Questions to attempt ({0}) cannot exceed total questions ({1}) in section '{2}'").format(
                        section.questions_to_attempt, section.total_questions, section.section_name
                    )
                )

            if section.marks_per_question <= 0:
                frappe.throw(
                    _("Marks per question must be greater than 0 in section '{0}'").format(
                        section.section_name
                    )
                )

    def validate_marks(self):
        """Validate total marks match section marks"""
        calculated_marks = 0

        for section in self.sections:
            # Section marks = questions to attempt * marks per question
            section_marks = section.questions_to_attempt * section.marks_per_question
            calculated_marks += section_marks

        if calculated_marks != self.total_marks:
            frappe.msgprint(
                _("Total marks ({0}) does not match sum of section marks ({1}). "
                  "Consider adjusting the total marks.").format(
                    self.total_marks, calculated_marks
                ),
                indicator="orange",
                title=_("Marks Mismatch")
            )

    def validate_distribution(self):
        """Validate distribution rules"""
        # Validate unit distribution
        if self.unit_wise_distribution:
            total_percentage = sum(d.percentage for d in self.unit_wise_distribution)
            if abs(total_percentage - 100) > 0.01:
                frappe.throw(
                    _("Unit distribution percentages must sum to 100%. Current sum: {0}%").format(
                        total_percentage
                    )
                )

        # Validate bloom distribution
        if self.bloom_distribution:
            total_percentage = sum(d.percentage for d in self.bloom_distribution)
            if abs(total_percentage - 100) > 0.01:
                frappe.throw(
                    _("Bloom's taxonomy distribution percentages must sum to 100%. Current sum: {0}%").format(
                        total_percentage
                    )
                )

    def calculate_section_marks(self):
        """Calculate and set section marks"""
        for section in self.sections:
            section.section_marks = section.questions_to_attempt * section.marks_per_question

    def get_question_requirements(self):
        """
        Get question requirements for each section

        Returns:
            Dict with section-wise question requirements
        """
        requirements = {}

        for section in self.sections:
            requirements[section.section_name] = {
                "question_type": section.question_type,
                "total_questions": section.total_questions,
                "marks_per_question": section.marks_per_question,
                "negative_marking": section.negative_marking,
                "negative_marks": section.negative_marks
            }

        return requirements

    def check_question_availability(self):
        """
        Check if enough questions are available for this template

        Returns:
            Dict with availability status for each section
        """
        availability = {}

        for section in self.sections:
            filters = {
                "course": self.course,
                "status": "Approved"
            }

            if section.question_type:
                filters["question_type"] = section.question_type

            available_count = frappe.db.count("Question Bank", filters)

            availability[section.section_name] = {
                "required": section.total_questions,
                "available": available_count,
                "sufficient": available_count >= section.total_questions
            }

        return availability

    @frappe.whitelist()
    def generate_paper(self, set_code=None, exam_date=None):
        """
        Generate a question paper from this template

        Args:
            set_code: Optional set identifier (A, B, C, D)
            exam_date: Date of examination

        Returns:
            Generated Question Paper name
        """
        from university_erp.university_erp.examination.question_paper_generator import QuestionPaperGenerator

        generator = QuestionPaperGenerator(self.name)
        return generator.generate_paper(set_code, exam_date)
