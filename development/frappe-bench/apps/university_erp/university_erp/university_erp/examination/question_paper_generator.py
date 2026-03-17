"""
Question Paper Generator

Automated question paper generation based on templates with support for
question selection by unit, Bloom's taxonomy, difficulty level, and usage frequency.
"""

import frappe
from frappe import _
from frappe.utils import today
import random
from typing import List, Dict, Optional


class QuestionPaperGenerator:
    """
    Automated question paper generator based on templates
    """

    def __init__(self, template_name: str):
        """
        Initialize the generator with a template

        Args:
            template_name: Name of the Question Paper Template
        """
        self.template = frappe.get_doc("Question Paper Template", template_name)
        self.selected_questions = []
        self.section_questions = {}

    def generate_paper(self, set_code: str = None, exam_date: str = None) -> str:
        """
        Generate a question paper from template

        Args:
            set_code: Optional set identifier (A, B, C, D)
            exam_date: Date of examination

        Returns:
            Generated Question Paper name
        """
        # Validate template
        self._validate_template()

        # Get question pool
        question_pool = self._get_question_pool()

        # Select questions for each section
        for section in self.template.sections:
            self._select_questions_for_section(section, question_pool)

        # Create question paper document
        paper = self._create_question_paper(set_code, exam_date)

        return paper.name

    def _validate_template(self):
        """Validate template has enough questions available"""
        for section in self.template.sections:
            filters = {
                "course": self.template.course,
                "status": "Approved"
            }

            if section.question_type:
                filters["question_type"] = section.question_type

            available = frappe.db.count("Question Bank", filters)

            if available < section.total_questions:
                frappe.throw(_(
                    "Not enough {0} questions available for section '{1}'. "
                    "Need {2}, have {3}"
                ).format(
                    section.question_type or "general",
                    section.section_name,
                    section.total_questions,
                    available
                ))

    def _get_question_pool(self) -> Dict[str, List]:
        """
        Get available questions grouped by type

        Returns:
            Dict with question type as key and list of questions as value
        """
        pool = {}

        # Get all approved questions for the course
        questions = frappe.get_all("Question Bank",
            filters={
                "course": self.template.course,
                "status": "Approved"
            },
            fields=["name", "question_type", "difficulty_level",
                   "blooms_taxonomy", "unit", "marks", "times_used",
                   "last_used_date"]
        )

        # Group by type
        for q in questions:
            qtype = q.question_type or "general"
            if qtype not in pool:
                pool[qtype] = []
            pool[qtype].append(q)

        return pool

    def _select_questions_for_section(self, section, pool: Dict):
        """
        Select questions for a section based on rules

        Args:
            section: Question Paper Section row
            pool: Question pool dictionary
        """
        qtype = section.question_type or "general"
        available = pool.get(qtype, [])

        # If no specific type, get all questions
        if not section.question_type:
            available = []
            for questions in pool.values():
                available.extend(questions)

        # Apply distribution rules
        selected = []

        # Unit-wise distribution
        if self.template.unit_wise_distribution:
            selected = self._select_by_unit(
                available,
                section.total_questions
            )

        # Bloom's taxonomy distribution
        elif self.template.bloom_distribution:
            selected = self._select_by_bloom(
                available,
                section.total_questions
            )

        # Random selection if no rules
        else:
            selected = self._weighted_random_select(
                available,
                section.total_questions
            )

        # Shuffle if required
        if self.template.shuffle_questions:
            random.shuffle(selected)

        self.section_questions[section.section_name] = selected
        self.selected_questions.extend(selected)

    def _select_by_unit(self, questions: List, count: int) -> List:
        """
        Select questions ensuring unit coverage

        Args:
            questions: List of available questions
            count: Number of questions to select

        Returns:
            List of selected questions
        """
        selected = []
        unit_rules = {r.unit: r.percentage for r in self.template.unit_wise_distribution}

        for unit, percentage in unit_rules.items():
            unit_count = max(1, int(count * percentage / 100))
            unit_questions = [q for q in questions if q.unit == unit]

            # Sort by usage (prefer less used questions)
            unit_questions.sort(key=lambda x: (x.times_used or 0, x.last_used_date or ""))

            # Select questions from this unit
            for q in unit_questions[:unit_count]:
                if q not in selected:
                    selected.append(q)

        # Fill remaining with random
        remaining = count - len(selected)
        if remaining > 0:
            unused = [q for q in questions if q not in selected]
            unused.sort(key=lambda x: (x.times_used or 0, x.last_used_date or ""))
            selected.extend(unused[:remaining])

        return selected[:count]

    def _select_by_bloom(self, questions: List, count: int) -> List:
        """
        Select questions by Bloom's taxonomy levels

        Args:
            questions: List of available questions
            count: Number of questions to select

        Returns:
            List of selected questions
        """
        selected = []
        bloom_rules = {r.level: r.percentage for r in self.template.bloom_distribution}

        for level, percentage in bloom_rules.items():
            level_count = max(1, int(count * percentage / 100))
            level_questions = [q for q in questions if q.blooms_taxonomy == level]

            # Sort by usage
            level_questions.sort(key=lambda x: (x.times_used or 0, x.last_used_date or ""))

            # Select questions from this level
            for q in level_questions[:level_count]:
                if q not in selected:
                    selected.append(q)

        # Fill remaining
        remaining = count - len(selected)
        if remaining > 0:
            unused = [q for q in questions if q not in selected]
            unused.sort(key=lambda x: (x.times_used or 0, x.last_used_date or ""))
            selected.extend(unused[:remaining])

        return selected[:count]

    def _weighted_random_select(self, questions: List, count: int) -> List:
        """
        Weighted random selection preferring less-used questions

        Args:
            questions: List of available questions
            count: Number of questions to select

        Returns:
            List of selected questions
        """
        if not questions:
            return []

        # Calculate weights (inverse of usage)
        max_usage = max([q.times_used or 0 for q in questions] or [1])
        weights = [(max_usage - (q.times_used or 0) + 1) for q in questions]

        selected = []
        available = questions.copy()
        available_weights = weights.copy()

        for _ in range(min(count, len(questions))):
            if not available:
                break

            # Weighted random choice
            total_weight = sum(available_weights)
            if total_weight == 0:
                # If all weights are 0, select randomly
                idx = random.randint(0, len(available) - 1)
            else:
                r = random.uniform(0, total_weight)
                cumulative = 0

                idx = 0
                for i, w in enumerate(available_weights):
                    cumulative += w
                    if cumulative >= r:
                        idx = i
                        break

            selected.append(available[idx])
            available.pop(idx)
            available_weights.pop(idx)

        return selected

    def _create_question_paper(self, set_code: str, exam_date: str):
        """
        Create the question paper document

        Args:
            set_code: Set identifier
            exam_date: Exam date

        Returns:
            Generated Question Paper document
        """
        paper = frappe.new_doc("Generated Question Paper")
        paper.paper_title = f"{self.template.template_name} - {set_code or 'Main'}"
        paper.course = self.template.course
        paper.template = self.template.name
        paper.total_marks = self.template.total_marks
        paper.duration_minutes = self.template.duration_minutes
        paper.exam_date = exam_date
        paper.set_code = set_code
        paper.instructions = self.template.instructions
        paper.status = "Draft"

        # Get current academic year
        paper.academic_year = frappe.db.get_value(
            "Academic Year",
            {"is_current": 1},
            "name"
        )

        # Set created_by
        faculty = frappe.db.get_value(
            "Instructor",
            {"user": frappe.session.user},
            "name"
        )
        if faculty:
            paper.created_by = faculty

        # Add questions with numbering
        question_number = 1
        for section in self.template.sections:
            section_questions = self.section_questions.get(section.section_name, [])

            for q in section_questions:
                paper.append("paper_questions", {
                    "question": q.name,
                    "question_number": question_number,
                    "marks": section.marks_per_question
                })
                question_number += 1

        paper.total_questions = question_number - 1
        paper.insert()

        return paper


def generate_multiple_sets(template_name: str, num_sets: int = 4,
                          exam_date: str = None) -> List[str]:
    """
    Generate multiple question paper sets

    Args:
        template_name: Template to use
        num_sets: Number of sets (default 4: A, B, C, D)
        exam_date: Examination date

    Returns:
        List of generated paper names
    """
    set_codes = ['A', 'B', 'C', 'D', 'E', 'F'][:num_sets]
    papers = []

    for code in set_codes:
        generator = QuestionPaperGenerator(template_name)
        paper_name = generator.generate_paper(code, exam_date)
        papers.append(paper_name)

    return papers


@frappe.whitelist()
def generate_paper_from_template(template_name: str, set_code: str = None,
                                 exam_date: str = None) -> str:
    """
    API to generate a question paper from template

    Args:
        template_name: Template name
        set_code: Optional set code
        exam_date: Optional exam date

    Returns:
        Generated paper name
    """
    generator = QuestionPaperGenerator(template_name)
    return generator.generate_paper(set_code, exam_date)


@frappe.whitelist()
def generate_multiple_paper_sets(template_name: str, num_sets: int = 4,
                                 exam_date: str = None) -> List[str]:
    """
    API to generate multiple question paper sets

    Args:
        template_name: Template name
        num_sets: Number of sets to generate
        exam_date: Optional exam date

    Returns:
        List of generated paper names
    """
    return generate_multiple_sets(template_name, int(num_sets), exam_date)
