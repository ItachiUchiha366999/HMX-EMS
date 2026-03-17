# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime
from typing import Optional


class FeedbackResponse(Document):
    """
    Feedback Response DocType for storing survey responses

    Features:
    - Automatic score calculation
    - NPS (Net Promoter Score) calculation
    - Section-wise scoring
    - Anonymous response support
    """

    def validate(self):
        """Validate feedback response"""
        self.validate_form_active()
        self.validate_single_response()

    def before_save(self):
        """Actions before saving"""
        if self.status == "Submitted":
            self.calculate_scores()
            self.calculate_nps()

    def after_insert(self):
        """Actions after insert"""
        self.update_form_statistics()

    def on_update(self):
        """Actions after update"""
        if self.has_value_changed("status") and self.status in ["Submitted", "Valid"]:
            self.update_form_statistics()

    def validate_form_active(self):
        """Validate that feedback form is active"""
        form = frappe.get_doc("Feedback Form", self.feedback_form)
        if form.status not in ["Active", "Scheduled"]:
            frappe.throw(_("This feedback form is not currently accepting responses"))

    def validate_single_response(self):
        """Validate single response per user (unless multiple allowed)"""
        if self.is_new():
            form = frappe.get_doc("Feedback Form", self.feedback_form)
            if not form.allow_multiple_responses:
                existing = self._check_existing_response()
                if existing:
                    frappe.throw(_("You have already submitted a response to this feedback form"))

    def _check_existing_response(self):
        """Check if user has already responded"""
        filters = {
            "feedback_form": self.feedback_form,
            "status": ["in", ["Submitted", "Valid"]]
        }

        if self.student:
            filters["student"] = self.student
        elif self.faculty:
            filters["faculty"] = self.faculty
        else:
            return False

        # Exclude current document
        if self.name:
            filters["name"] = ["!=", self.name]

        return frappe.db.exists("Feedback Response", filters)

    def calculate_scores(self):
        """Calculate overall and section scores"""
        form = frappe.get_doc("Feedback Form", self.feedback_form)

        total_score = 0
        total_weight = 0
        section_scores = {}

        # Build question lookup from form
        questions = {}
        current_section = "General"

        for section in form.sections or []:
            current_section = section.section_title
            section_scores[current_section] = {"total": 0, "count": 0, "weight": 0}

        for q in form.questions:
            questions[q.name] = {
                "type": q.question_type,
                "weight": q.weightage or 1,
                "category": q.category or "General"
            }
            # Initialize section if not exists
            section_name = q.category or "General"
            if section_name not in section_scores:
                section_scores[section_name] = {"total": 0, "count": 0, "weight": 0}

        # Process answers
        for ans in self.answers:
            q_info = questions.get(ans.question_id)
            if not q_info:
                continue

            # Calculate numeric score
            score = self._get_numeric_score(ans.answer_value, q_info["type"])

            if score is not None:
                weight = q_info["weight"]

                # Overall score
                total_score += score * weight
                total_weight += weight

                # Section score
                section = q_info.get("category") or "General"
                if section in section_scores:
                    section_scores[section]["total"] += score * weight
                    section_scores[section]["weight"] += weight
                    section_scores[section]["count"] += 1

        # Save overall score (as percentage)
        if total_weight > 0:
            self.overall_score = (total_score / total_weight) * 100

        # Save section scores
        self.section_scores = []
        for section_name, scores in section_scores.items():
            if scores["weight"] > 0:
                avg = (scores["total"] / scores["weight"]) * 100
                self.append("section_scores", {
                    "section_name": section_name,
                    "score": avg,
                    "responses_count": scores["count"]
                })

    def _get_numeric_score(self, answer: str, question_type: str) -> Optional[float]:
        """Convert answer to numeric score (0-1 scale)"""
        try:
            if question_type == "Rating (1-5)":
                return (float(answer) - 1) / 4  # Normalize to 0-1
            elif question_type == "Rating (1-10)":
                return (float(answer) - 1) / 9
            elif question_type == "Yes/No":
                return 1.0 if str(answer).lower() in ["yes", "true", "1"] else 0.0
            elif question_type == "Likert Scale":
                # Assume 5-point Likert
                likert_map = {
                    "strongly disagree": 0,
                    "disagree": 0.25,
                    "neutral": 0.5,
                    "agree": 0.75,
                    "strongly agree": 1.0
                }
                return likert_map.get(str(answer).lower(), 0.5)
        except (ValueError, TypeError):
            pass
        return None

    def calculate_nps(self):
        """Calculate NPS score and category"""
        form = frappe.get_doc("Feedback Form", self.feedback_form)

        # Find NPS question (Rating 1-10 with NPS category)
        nps_question = None
        for q in form.questions:
            if q.question_type == "Rating (1-10)" and q.category == "NPS":
                nps_question = q
                break

        if not nps_question:
            return

        # Find answer to NPS question
        for ans in self.answers:
            if ans.question_id == nps_question.name:
                try:
                    self.nps_score = int(float(ans.answer_value))

                    # Categorize
                    if self.nps_score >= 9:
                        self.nps_category = "Promoter"
                    elif self.nps_score >= 7:
                        self.nps_category = "Passive"
                    else:
                        self.nps_category = "Detractor"
                except (ValueError, TypeError):
                    pass
                break

    def update_form_statistics(self):
        """Update parent form statistics"""
        try:
            form = frappe.get_doc("Feedback Form", self.feedback_form)
            form.update_statistics()
        except Exception:
            frappe.log_error("Failed to update feedback form statistics")

    @frappe.whitelist()
    def submit_response(self):
        """Submit the feedback response"""
        self.submission_datetime = now_datetime()
        self.status = "Submitted"
        self.save()

        return {
            "status": "success",
            "message": _("Thank you for your feedback!")
        }

    @frappe.whitelist()
    def mark_valid(self):
        """Mark response as valid after review"""
        self.status = "Valid"
        self.save()

    @frappe.whitelist()
    def mark_invalid(self, reason=None):
        """Mark response as invalid"""
        self.status = "Invalid"
        if reason:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": self.doctype,
                "reference_name": self.name,
                "content": f"Marked as invalid: {reason}"
            }).insert()
        self.save()
