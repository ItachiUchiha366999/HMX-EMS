# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Feedback Manager Module

This module provides the FeedbackManager class for handling feedback operations
including form creation, response submission, score calculation, and analysis.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, cint, flt
from typing import Dict, List, Optional
import json


class FeedbackManager:
    """
    Manager class for feedback forms and responses

    Features:
    - Automatic course feedback form creation
    - Response submission and validation
    - Score calculation (overall, section, NPS)
    - Feedback analysis and reporting
    """

    @staticmethod
    def create_course_feedback_forms(academic_term: str) -> int:
        """
        Auto-create course feedback forms for all courses in a term

        Args:
            academic_term: Academic term to create forms for

        Returns:
            int: Number of forms created
        """
        # Get all courses with instructors in this term
        courses = frappe.get_all("Course Schedule",
            filters={"academic_term": academic_term},
            fields=["course", "instructor"],
            distinct=True
        )

        created = 0
        for course_data in courses:
            # Check if feedback form already exists
            existing = frappe.db.exists("Feedback Form", {
                "form_type": "Course Feedback",
                "academic_term": academic_term,
            })

            if not existing:
                try:
                    form_name = FeedbackManager.create_standard_course_feedback(
                        course_data.course,
                        academic_term
                    )
                    if form_name:
                        created += 1
                except Exception as e:
                    frappe.log_error(f"Failed to create feedback form for course {course_data.course}: {str(e)}")

        return created

    @staticmethod
    def create_standard_course_feedback(course: str, academic_term: str) -> str:
        """
        Create a standard course feedback form

        Args:
            course: Course name
            academic_term: Academic term

        Returns:
            str: Feedback form name
        """
        course_doc = frappe.get_doc("Course", course)

        form = frappe.new_doc("Feedback Form")
        form.form_title = f"Course Feedback - {course_doc.course_name}"
        form.form_type = "Course Feedback"
        form.target_audience = "Students"
        form.academic_term = academic_term
        form.allow_anonymous = True
        form.is_mandatory = True

        # Set default dates (can be adjusted later)
        from frappe.utils import add_days, today, get_datetime
        form.start_date = get_datetime(today())
        form.end_date = get_datetime(add_days(today(), 30))

        # Add standard questions for course feedback
        questions = [
            # Course Content Section
            {"question_text": "The course objectives were clearly defined", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content", "weightage": 1},
            {"question_text": "The course content was relevant and up-to-date", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content", "weightage": 1},
            {"question_text": "The course materials were helpful", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content", "weightage": 1},
            {"question_text": "The difficulty level was appropriate", "question_type": "Rating (1-5)", "is_required": 1, "category": "Content", "weightage": 1},
            # Teaching Section
            {"question_text": "The instructor explained concepts clearly", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching", "weightage": 1.5},
            {"question_text": "The instructor was well prepared for classes", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching", "weightage": 1},
            {"question_text": "The instructor encouraged student participation", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching", "weightage": 1},
            {"question_text": "The instructor was available for doubts and queries", "question_type": "Rating (1-5)", "is_required": 1, "category": "Teaching", "weightage": 1},
            # Assessment Section
            {"question_text": "Assignments were relevant to course content", "question_type": "Rating (1-5)", "is_required": 1, "category": "Assessment", "weightage": 1},
            {"question_text": "Feedback on assignments was helpful", "question_type": "Rating (1-5)", "is_required": 1, "category": "Assessment", "weightage": 1},
            {"question_text": "Examinations covered the syllabus appropriately", "question_type": "Rating (1-5)", "is_required": 1, "category": "Assessment", "weightage": 1},
            # Overall Section
            {"question_text": "Overall, I am satisfied with this course", "question_type": "Rating (1-5)", "is_required": 1, "category": "Overall", "weightage": 2},
            {"question_text": "I would recommend this course to other students", "question_type": "Rating (1-5)", "is_required": 1, "category": "Overall", "weightage": 1},
            {"question_text": "On a scale of 0-10, how likely are you to recommend this course?", "question_type": "Rating (1-10)", "is_required": 1, "category": "NPS", "weightage": 1},
            {"question_text": "What did you like most about this course?", "question_type": "Long Text", "is_required": 0, "category": "Comments", "weightage": 0},
            {"question_text": "What improvements would you suggest?", "question_type": "Long Text", "is_required": 0, "category": "Suggestions", "weightage": 0}
        ]

        for q in questions:
            form.append("questions", q)

        form.append("courses", {"course": course})

        form.thank_you_message = "<p>Thank you for your valuable feedback! Your responses will help us improve the course.</p>"
        form.status = "Draft"

        form.insert()
        return form.name

    @staticmethod
    def submit_response(feedback_form: str, answers: List[Dict],
                       context: Dict = None, is_anonymous: bool = False) -> str:
        """
        Submit a feedback response

        Args:
            feedback_form: Feedback form name
            answers: List of {question_id, answer, question_text} dicts
            context: {course, instructor} for course feedback
            is_anonymous: Whether response is anonymous

        Returns:
            str: Response document name
        """
        form = frappe.get_doc("Feedback Form", feedback_form)

        # Validate form is active
        if form.status != "Active":
            frappe.throw(_("This feedback form is not currently active"))

        # Check if already submitted
        if not form.allow_multiple_responses:
            existing = FeedbackManager._check_existing_response(feedback_form, context)
            if existing:
                frappe.throw(_("You have already submitted feedback for this"))

        response = frappe.new_doc("Feedback Response")
        response.feedback_form = feedback_form
        response.is_anonymous = is_anonymous or form.allow_anonymous

        # Set respondent
        if not response.is_anonymous:
            student = frappe.db.get_value("Student", {"user": frappe.session.user})
            if student:
                response.respondent_type = "Student"
                response.student = student
            else:
                instructor = frappe.db.get_value("Instructor", {"user": frappe.session.user})
                if instructor:
                    response.respondent_type = "Faculty"
                    response.faculty = instructor
        else:
            response.respondent_type = "Anonymous"

        # Set context
        if context:
            response.course = context.get("course")
            response.instructor = context.get("instructor")

        # Add answers
        for ans in answers:
            answer_value = ans.get("answer")
            if isinstance(answer_value, (list, dict)):
                answer_value = json.dumps(answer_value)
            else:
                answer_value = str(answer_value) if answer_value is not None else ""

            response.append("answers", {
                "question_id": ans.get("question_id"),
                "answer_value": answer_value,
                "question_text": ans.get("question_text")
            })

        response.submission_datetime = now_datetime()
        response.ip_address = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None
        response.device_info = (frappe.request.headers.get("User-Agent", "")[:200]
                               if hasattr(frappe, 'request') and frappe.request else None)
        response.status = "Submitted"

        response.insert()

        # Calculate scores
        FeedbackManager.calculate_response_scores(response.name)

        # Update form statistics
        FeedbackManager.update_form_statistics(feedback_form)

        return response.name

    @staticmethod
    def calculate_response_scores(response_name: str):
        """
        Calculate various scores for a feedback response

        Args:
            response_name: Feedback response name
        """
        response = frappe.get_doc("Feedback Response", response_name)
        form = frappe.get_doc("Feedback Form", response.feedback_form)

        total_score = 0
        total_weight = 0
        section_scores = {}
        nps_score = None

        # Build question lookup
        questions = {}
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
        for ans in response.answers:
            q_info = questions.get(ans.question_id)
            if not q_info:
                continue

            # Calculate numeric score
            score = FeedbackManager._get_numeric_score(ans.answer_value, q_info["type"])

            if score is not None:
                # Overall score
                total_score += score * q_info["weight"]
                total_weight += q_info["weight"]

                # Section score
                section = q_info["category"]
                section_scores[section]["total"] += score * q_info["weight"]
                section_scores[section]["weight"] += q_info["weight"]
                section_scores[section]["count"] += 1

                # NPS score
                if q_info["category"] == "NPS" and q_info["type"] == "Rating (1-10)":
                    try:
                        nps_score = int(float(ans.answer_value))
                    except (ValueError, TypeError):
                        pass

        # Save overall score
        if total_weight > 0:
            response.overall_score = (total_score / total_weight) * 100

        # Save section scores
        response.section_scores = []
        for section_name, scores in section_scores.items():
            if scores["weight"] > 0:
                avg = (scores["total"] / scores["weight"]) * 100
                response.append("section_scores", {
                    "section_name": section_name,
                    "score": avg,
                    "responses_count": scores["count"]
                })

        # NPS calculation
        if nps_score is not None:
            response.nps_score = nps_score
            if nps_score >= 9:
                response.nps_category = "Promoter"
            elif nps_score >= 7:
                response.nps_category = "Passive"
            else:
                response.nps_category = "Detractor"

        response.status = "Valid"
        response.save()

    @staticmethod
    def _get_numeric_score(answer: str, question_type: str) -> Optional[float]:
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

    @staticmethod
    def _check_existing_response(feedback_form: str, context: Dict) -> bool:
        """Check if user already submitted response"""
        filters = {"feedback_form": feedback_form, "status": ["in", ["Submitted", "Valid"]]}

        student = frappe.db.get_value("Student", {"user": frappe.session.user})
        if student:
            filters["student"] = student
        else:
            instructor = frappe.db.get_value("Instructor", {"user": frappe.session.user})
            if instructor:
                filters["faculty"] = instructor
            else:
                return False

        if context:
            if context.get("course"):
                filters["course"] = context.get("course")
            if context.get("instructor"):
                filters["instructor"] = context.get("instructor")

        return frappe.db.exists("Feedback Response", filters)

    @staticmethod
    def update_form_statistics(feedback_form: str):
        """Update form response statistics"""
        form = frappe.get_doc("Feedback Form", feedback_form)

        total_responses = frappe.db.count("Feedback Response", {
            "feedback_form": feedback_form,
            "status": ["in", ["Submitted", "Valid"]]
        })

        form.total_responses = total_responses

        # Calculate response rate
        target_count = FeedbackManager._get_target_count(form)
        if target_count > 0:
            form.response_rate = (total_responses / target_count) * 100
        else:
            form.response_rate = 0

        form.save()

    @staticmethod
    def _get_target_count(form) -> int:
        """Get expected number of respondents"""
        if form.target_audience == "Students":
            if form.courses:
                course_list = [c.course for c in form.courses]
                return frappe.db.count("Course Enrollment",
                    filters={"course": ["in", course_list]}
                )
            elif form.programs:
                program_list = [p.program for p in form.programs]
                return frappe.db.count("Program Enrollment",
                    filters={"program": ["in", program_list]}
                )
        return 0

    @staticmethod
    def get_feedback_analysis(feedback_form: str) -> Dict:
        """
        Get comprehensive feedback analysis

        Args:
            feedback_form: Feedback form name

        Returns:
            Dict with analysis including scores, trends, comments
        """
        form = frappe.get_doc("Feedback Form", feedback_form)

        responses = frappe.get_all("Feedback Response",
            filters={
                "feedback_form": feedback_form,
                "status": "Valid"
            },
            fields=["name", "overall_score", "nps_score", "nps_category",
                   "course", "instructor", "submission_datetime"]
        )

        if not responses:
            return {"message": "No responses yet"}

        # Overall metrics
        valid_scores = [r.overall_score for r in responses if r.overall_score is not None]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        # NPS calculation
        promoters = len([r for r in responses if r.nps_category == "Promoter"])
        passives = len([r for r in responses if r.nps_category == "Passive"])
        detractors = len([r for r in responses if r.nps_category == "Detractor"])
        nps = ((promoters - detractors) / len(responses)) * 100 if responses else 0

        # Question-wise analysis
        question_scores = FeedbackManager._get_question_analysis(feedback_form)

        # Section-wise analysis
        section_scores = frappe.db.sql("""
            SELECT fss.section_name, AVG(fss.score) as avg_score
            FROM `tabFeedback Section Score` fss
            JOIN `tabFeedback Response` fr ON fss.parent = fr.name
            WHERE fr.feedback_form = %s AND fr.status = 'Valid'
            GROUP BY fss.section_name
        """, feedback_form, as_dict=True)

        # Comments extraction
        comments = FeedbackManager._extract_comments(feedback_form)

        return {
            "total_responses": len(responses),
            "average_score": round(avg_score, 2),
            "nps_score": round(nps, 1),
            "nps_breakdown": {
                "promoters": promoters,
                "passives": passives,
                "detractors": detractors
            },
            "section_scores": section_scores,
            "question_scores": question_scores,
            "positive_comments": comments.get("positive", [])[:10],
            "improvement_suggestions": comments.get("suggestions", [])[:10]
        }

    @staticmethod
    def _get_question_analysis(feedback_form: str) -> List[Dict]:
        """Get question-wise score analysis"""
        return frappe.db.sql("""
            SELECT
                fa.question_text,
                AVG(CAST(fa.answer_value AS DECIMAL(10,2))) as avg_score,
                COUNT(*) as responses
            FROM `tabFeedback Answer` fa
            JOIN `tabFeedback Response` fr ON fa.parent = fr.name
            JOIN `tabFeedback Question` fq ON fa.question_id = fq.name
            WHERE fr.feedback_form = %s
            AND fr.status = 'Valid'
            AND fq.question_type IN ('Rating (1-5)', 'Rating (1-10)')
            GROUP BY fa.question_text
            ORDER BY avg_score ASC
        """, feedback_form, as_dict=True)

    @staticmethod
    def _extract_comments(feedback_form: str) -> Dict:
        """Extract and categorize text comments"""
        comments = frappe.db.sql("""
            SELECT fa.answer_value, fq.category
            FROM `tabFeedback Answer` fa
            JOIN `tabFeedback Response` fr ON fa.parent = fr.name
            JOIN `tabFeedback Question` fq ON fa.question_id = fq.name
            WHERE fr.feedback_form = %s
            AND fr.status = 'Valid'
            AND fq.question_type IN ('Short Text', 'Long Text')
            AND fa.answer_value != ''
            AND fa.answer_value IS NOT NULL
        """, feedback_form, as_dict=True)

        positive = []
        suggestions = []

        for c in comments:
            if c.category == "Comments":
                positive.append(c.answer_value)
            elif c.category == "Suggestions":
                suggestions.append(c.answer_value)

        return {"positive": positive, "suggestions": suggestions}


# API Endpoints

@frappe.whitelist()
def get_pending_feedback_forms():
    """Get pending feedback forms for current user"""
    student = frappe.db.get_value("Student", {"user": frappe.session.user})

    if not student:
        return []

    # Get student's enrolled courses
    enrollments = frappe.get_all("Course Enrollment",
        filters={"student": student},
        pluck="course"
    )

    forms = frappe.get_all("Feedback Form",
        filters={
            "status": "Active",
            "target_audience": ["in", ["Students", "All"]]
        },
        fields=["name", "form_title", "form_type", "end_date", "is_mandatory"]
    )

    pending = []
    for form in forms:
        # Check if already responded
        responded = frappe.db.exists("Feedback Response", {
            "feedback_form": form.name,
            "student": student,
            "status": ["in", ["Submitted", "Valid"]]
        })

        if not responded:
            pending.append(form)

    return pending


@frappe.whitelist()
def submit_feedback(feedback_form: str, answers: str,
                   course: str = None, instructor: str = None,
                   is_anonymous: bool = False):
    """API to submit feedback response"""
    answers_list = json.loads(answers) if isinstance(answers, str) else answers
    context = {}
    if course:
        context["course"] = course
    if instructor:
        context["instructor"] = instructor

    return FeedbackManager.submit_response(
        feedback_form,
        answers_list,
        context,
        is_anonymous
    )


@frappe.whitelist()
def get_feedback_analysis(feedback_form: str):
    """API to get feedback analysis"""
    return FeedbackManager.get_feedback_analysis(feedback_form)


@frappe.whitelist()
def get_form_questions(feedback_form: str):
    """API to get questions for a feedback form"""
    form = frappe.get_doc("Feedback Form", feedback_form)

    if form.status != "Active":
        frappe.throw(_("This feedback form is not active"))

    questions = []
    for q in form.questions:
        questions.append({
            "name": q.name,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "is_required": q.is_required,
            "options": q.options.split("\n") if q.options else [],
            "help_text": q.help_text
        })

    if form.randomize_questions:
        import random
        random.shuffle(questions)

    return {
        "form_title": form.form_title,
        "description": form.description,
        "questions": questions,
        "allow_anonymous": form.allow_anonymous,
        "show_progress": form.show_progress
    }
