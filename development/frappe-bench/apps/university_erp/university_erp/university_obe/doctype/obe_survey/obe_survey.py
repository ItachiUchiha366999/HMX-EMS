# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class OBESurvey(Document):
    def validate(self):
        self.validate_respondent()
        self.set_survey_defaults()

    def validate_respondent(self):
        """Validate respondent details based on survey type"""
        if self.survey_type in ["Alumni Survey", "Employer Survey"]:
            if not self.organization:
                frappe.msgprint(_("Organization is recommended for {0}").format(self.survey_type))

        if self.survey_type == "Alumni Survey":
            if not self.graduation_year:
                frappe.msgprint(_("Graduation year is recommended for Alumni Survey"))

    def set_survey_defaults(self):
        """Set default values based on survey type"""
        if not self.survey_date:
            self.survey_date = frappe.utils.today()

        # Auto-populate PO ratings if empty
        if not self.po_ratings and self.program:
            self.populate_po_ratings()

    def populate_po_ratings(self):
        """Populate PO ratings table with program outcomes"""
        pos = frappe.get_all(
            "Program Outcome",
            filters={"program": self.program, "status": "Active"},
            fields=["name", "po_code", "po_statement"],
            order_by="is_pso, po_number"
        )

        for po in pos:
            self.append("po_ratings", {
                "program_outcome": po.name,
                "po_code": po.po_code,
                "po_statement": po.po_statement,
                "rating": 3  # Default neutral rating
            })

    def on_update(self):
        """Handle survey submission"""
        if self.status == "Submitted" and not self.submitted_on:
            self.db_set("submitted_on", frappe.utils.now())


@frappe.whitelist(allow_guest=True)
def get_survey_form(survey_type, program, course=None, template=None):
    """Get survey form structure for web portal"""
    # Get program outcomes for rating
    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": program, "status": "Active"},
        fields=["name", "po_number", "po_code", "po_title", "po_statement", "is_pso"],
        order_by="is_pso, po_number"
    )

    # Get survey template if specified
    template_data = None
    if template:
        template_data = frappe.get_doc("Survey Template", template)
    else:
        # Try to find default template for this survey type
        templates = frappe.get_all(
            "Survey Template",
            filters={"survey_type": survey_type, "is_active": 1},
            fields=["name"]
        )
        if templates:
            template_data = frappe.get_doc("Survey Template", templates[0].name)

    # Build form structure
    form = {
        "survey_type": survey_type,
        "program": program,
        "course": course,
        "program_outcomes": pos,
        "additional_questions": []
    }

    if template_data:
        form["introduction"] = template_data.introduction_text
        form["thank_you_message"] = template_data.thank_you_message
        form["include_po_ratings"] = template_data.include_po_ratings

        if template_data.additional_questions:
            form["additional_questions"] = [
                {
                    "question": q.question,
                    "type": q.question_type,
                    "options": q.options.split("\n") if q.options else [],
                    "required": q.is_required
                }
                for q in template_data.additional_questions
            ]

    return form


@frappe.whitelist(allow_guest=True)
def submit_survey(data):
    """Submit survey from web portal"""
    if isinstance(data, str):
        import json
        data = json.loads(data)

    # Create OBE Survey document
    survey = frappe.new_doc("OBE Survey")
    survey.survey_type = data.get("survey_type")
    survey.program = data.get("program")
    survey.course = data.get("course")
    survey.academic_year = data.get("academic_year")
    survey.respondent_name = data.get("respondent_name")
    survey.respondent_email = data.get("respondent_email")
    survey.respondent_phone = data.get("respondent_phone")

    # Alumni/Employer specific fields
    survey.graduation_year = data.get("graduation_year")
    survey.organization = data.get("organization")
    survey.designation = data.get("designation")
    survey.years_of_experience = data.get("years_of_experience")

    # Overall feedback
    survey.overall_satisfaction = data.get("overall_satisfaction", 0)
    survey.program_relevance = data.get("program_relevance", 0)
    survey.employability_rating = data.get("employability_rating", 0)
    survey.skill_development_rating = data.get("skill_development_rating", 0)

    # Comments
    survey.strengths = data.get("strengths")
    survey.improvements = data.get("improvements")
    survey.additional_comments = data.get("additional_comments")

    # PO Ratings
    po_ratings = data.get("po_ratings", [])
    for rating in po_ratings:
        survey.append("po_ratings", {
            "program_outcome": rating.get("program_outcome"),
            "rating": rating.get("rating", 3),
            "comments": rating.get("comments")
        })

    # Set submission details
    survey.status = "Submitted"
    survey.submitted_on = frappe.utils.now()
    survey.ip_address = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None

    survey.insert(ignore_permissions=True)

    return {
        "success": True,
        "message": _("Thank you for submitting the survey!"),
        "survey_id": survey.name
    }


@frappe.whitelist()
def get_survey_statistics(program=None, survey_type=None, academic_year=None):
    """Get survey statistics for analysis"""
    filters = {"status": ["in", ["Submitted", "Verified"]]}
    if program:
        filters["program"] = program
    if survey_type:
        filters["survey_type"] = survey_type
    if academic_year:
        filters["academic_year"] = academic_year

    surveys = frappe.get_all(
        "OBE Survey",
        filters=filters,
        fields=["name", "survey_type", "overall_satisfaction", "program_relevance",
                "employability_rating", "skill_development_rating"]
    )

    if not surveys:
        return {"total_responses": 0, "avg_satisfaction": 0, "po_ratings": {}}

    # Calculate averages
    total = len(surveys)
    avg_satisfaction = sum(s.overall_satisfaction or 0 for s in surveys) / total
    avg_relevance = sum(s.program_relevance or 0 for s in surveys) / total
    avg_employability = sum(s.employability_rating or 0 for s in surveys) / total
    avg_skills = sum(s.skill_development_rating or 0 for s in surveys) / total

    # Get PO-wise ratings
    po_ratings = {}
    for survey in surveys:
        ratings = frappe.get_all(
            "Survey PO Rating",
            filters={"parent": survey.name},
            fields=["program_outcome", "po_code", "rating"]
        )
        for r in ratings:
            po_key = r.po_code or r.program_outcome
            if po_key not in po_ratings:
                po_ratings[po_key] = []
            if r.rating:
                po_ratings[po_key].append(r.rating)

    # Calculate PO averages
    po_averages = {}
    for po, ratings in po_ratings.items():
        if ratings:
            po_averages[po] = round(sum(ratings) / len(ratings), 2)

    return {
        "total_responses": total,
        "avg_satisfaction": round(avg_satisfaction, 2),
        "avg_relevance": round(avg_relevance, 2),
        "avg_employability": round(avg_employability, 2),
        "avg_skills": round(avg_skills, 2),
        "po_ratings": po_averages
    }
