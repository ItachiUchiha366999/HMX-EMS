"""
Student Feedback Portal Page Controller

Allows students to view and submit feedback for courses and faculty.
"""
import frappe
from frappe import _
from frappe.utils import getdate, now_datetime, flt


def get_context(context):
    """Get context for feedback portal page"""
    context.no_cache = 1

    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/student-portal/feedback"
        raise frappe.Redirect

    # Get student linked to current user
    student = get_student_for_user()
    if not student:
        context.error = _("No student record found for your account.")
        context.student = None
        return context

    context.student = student

    # Get pending feedback forms for this student
    pending_forms = get_pending_feedback_forms(student)
    context.pending_forms = pending_forms
    context.pending_count = len(pending_forms)

    # Get submitted feedback responses
    submitted_responses = frappe.get_all(
        "Feedback Response",
        filters={
            "respondent": frappe.session.user,
            "status": ["in", ["Valid", "Submitted"]]
        },
        fields=[
            "name", "feedback_form", "course", "instructor",
            "overall_score", "creation", "status"
        ],
        order_by="creation desc",
        limit=20
    )

    # Enrich with feedback form details
    for response in submitted_responses:
        form = frappe.get_cached_doc("Feedback Form", response.feedback_form)
        response.form_title = form.title
        response.form_type = form.form_type

    context.submitted_responses = submitted_responses
    context.submitted_count = len(submitted_responses)

    return context


def get_student_for_user():
    """Get student record linked to current user"""
    student_name = frappe.db.get_value("Student", {"user": frappe.session.user})

    if not student_name:
        student_name = frappe.db.get_value("Student", {"student_email_id": frappe.session.user})

    if student_name:
        return frappe.get_doc("Student", student_name)

    return None


def get_pending_feedback_forms(student):
    """Get feedback forms pending for this student"""
    pending_forms = []

    # Get active feedback forms
    active_forms = frappe.get_all(
        "Feedback Form",
        filters={
            "status": "Active",
            "end_date": [">=", getdate()]
        },
        fields=[
            "name", "title", "form_type", "description",
            "start_date", "end_date", "academic_term",
            "course", "instructor", "is_mandatory"
        ]
    )

    for form in active_forms:
        # Check if student has already submitted
        existing = frappe.db.exists(
            "Feedback Response",
            {
                "feedback_form": form.name,
                "respondent": frappe.session.user,
                "status": ["in", ["Valid", "Submitted"]]
            }
        )

        if existing:
            continue

        # Check if form applies to this student (filters)
        if is_form_applicable(form.name, student):
            pending_forms.append(form)

    return pending_forms


def is_form_applicable(form_name, student):
    """Check if feedback form is applicable to this student"""
    form = frappe.get_cached_doc("Feedback Form", form_name)

    # Check program filter
    if form.program_filters:
        student_program = student.program if hasattr(student, 'program') else None
        program_names = [p.program for p in form.program_filters]
        if student_program and student_program not in program_names:
            return False

    # Check department filter
    if form.department_filters:
        student_dept = student.department if hasattr(student, 'department') else None
        dept_names = [d.department for d in form.department_filters]
        if student_dept and student_dept not in dept_names:
            return False

    # Check course filter (if course feedback)
    if form.course_filters and form.form_type == "Course Feedback":
        # Check if student is enrolled in any of the courses
        course_names = [c.course for c in form.course_filters]
        enrolled = frappe.db.exists(
            "Course Enrollment",
            {
                "student": student.name,
                "course": ["in", course_names],
                "docstatus": 1
            }
        )
        if not enrolled:
            return False

    return True


@frappe.whitelist()
def get_feedback_form_questions(form_name):
    """Get questions for a feedback form"""
    try:
        form = frappe.get_doc("Feedback Form", form_name)

        # Check if form is active
        if form.status != "Active":
            return {"success": False, "message": _("This feedback form is no longer active.")}

        # Check if already submitted
        existing = frappe.db.exists(
            "Feedback Response",
            {
                "feedback_form": form_name,
                "respondent": frappe.session.user,
                "status": ["in", ["Valid", "Submitted"]]
            }
        )

        if existing:
            return {"success": False, "message": _("You have already submitted feedback for this form.")}

        # Build sections with questions
        sections = []
        current_section = None

        for section in form.sections:
            sections.append({
                "title": section.section_title,
                "description": section.section_description,
                "questions": []
            })

        # Add questions to appropriate sections
        for q in form.questions:
            question_data = {
                "idx": q.idx,
                "text": q.question_text,
                "type": q.question_type,
                "required": q.is_required,
                "options": q.options.split("\n") if q.options else [],
                "help_text": q.help_text,
                "category": q.category
            }

            # Add to last section or create default
            if sections:
                sections[-1]["questions"].append(question_data)
            else:
                if not sections:
                    sections.append({"title": "Questions", "description": "", "questions": []})
                sections[0]["questions"].append(question_data)

        return {
            "success": True,
            "form": {
                "name": form.name,
                "title": form.title,
                "description": form.description,
                "form_type": form.form_type,
                "course": form.course,
                "instructor": form.instructor,
                "allow_anonymous": form.allow_anonymous
            },
            "sections": sections
        }

    except frappe.DoesNotExistError:
        return {"success": False, "message": _("Feedback form not found.")}
    except Exception as e:
        frappe.log_error(f"Feedback form questions error: {str(e)}", "Feedback Portal")
        return {"success": False, "message": _("An error occurred.")}


@frappe.whitelist()
def submit_feedback(form_name, answers, is_anonymous=0, comments=None):
    """Submit feedback response"""
    try:
        form = frappe.get_doc("Feedback Form", form_name)

        # Validate form is still active
        if form.status != "Active":
            return {"success": False, "message": _("This feedback form is no longer active.")}

        if getdate() > form.end_date:
            return {"success": False, "message": _("The deadline for this feedback has passed.")}

        # Check for duplicate
        existing = frappe.db.exists(
            "Feedback Response",
            {
                "feedback_form": form_name,
                "respondent": frappe.session.user,
                "status": ["in", ["Valid", "Submitted"]]
            }
        )

        if existing:
            return {"success": False, "message": _("You have already submitted feedback for this form.")}

        # Parse answers
        if isinstance(answers, str):
            import json
            answers = json.loads(answers)

        # Create feedback response
        response = frappe.new_doc("Feedback Response")
        response.feedback_form = form_name
        response.respondent = frappe.session.user
        response.respondent_type = "Student"
        response.course = form.course
        response.instructor = form.instructor
        response.academic_term = form.academic_term
        response.submission_date = getdate()
        response.is_anonymous = 1 if (is_anonymous and form.allow_anonymous) else 0
        response.comments = comments
        response.status = "Valid"

        # Get student info
        student = get_student_for_user()
        if student:
            response.respondent_name = student.student_name if not response.is_anonymous else "Anonymous"

        # Add answers
        for answer in answers:
            response.append("answers", {
                "question_id": str(answer.get("question_idx", "")),
                "question_text": answer.get("question_text", ""),
                "answer_value": str(answer.get("answer", ""))
            })

        # Calculate scores
        total_score = 0
        score_count = 0
        section_scores = {}

        for q in form.questions:
            answer_data = next((a for a in answers if a.get("question_idx") == q.idx), None)
            if answer_data and q.question_type in ["Rating", "Scale"]:
                try:
                    score = flt(answer_data.get("answer", 0))
                    weightage = flt(q.weightage) or 1

                    # Normalize to percentage (assuming 5-point scale)
                    normalized = (score / 5) * 100

                    total_score += normalized * weightage
                    score_count += weightage

                    # Track by category for section scores
                    category = q.category or "General"
                    if category not in section_scores:
                        section_scores[category] = {"total": 0, "count": 0}
                    section_scores[category]["total"] += normalized * weightage
                    section_scores[category]["count"] += weightage
                except (ValueError, TypeError):
                    pass

        # Set overall score
        if score_count > 0:
            response.overall_score = total_score / score_count

        # Add section scores
        for section_name, scores in section_scores.items():
            if scores["count"] > 0:
                response.append("section_scores", {
                    "section_name": section_name,
                    "score": scores["total"] / scores["count"],
                    "responses_count": 1
                })

        # Calculate NPS if applicable
        nps_answer = next((a for a in answers if "recommend" in a.get("question_text", "").lower()), None)
        if nps_answer:
            try:
                nps_score = int(nps_answer.get("answer", 0))
                if nps_score >= 9:
                    response.nps_category = "Promoter"
                elif nps_score >= 7:
                    response.nps_category = "Passive"
                else:
                    response.nps_category = "Detractor"
            except (ValueError, TypeError):
                pass

        response.insert(ignore_permissions=True)

        # Update form statistics
        update_form_statistics(form_name)

        return {
            "success": True,
            "message": _("Thank you! Your feedback has been submitted successfully."),
            "response_id": response.name
        }

    except Exception as e:
        frappe.log_error(f"Feedback submission error: {str(e)}", "Feedback Portal")
        return {"success": False, "message": _("An error occurred while submitting feedback.")}


def update_form_statistics(form_name):
    """Update feedback form statistics after new response"""
    try:
        response_count = frappe.db.count(
            "Feedback Response",
            {"feedback_form": form_name, "status": ["in", ["Valid", "Submitted"]]}
        )

        avg_score = frappe.db.sql("""
            SELECT AVG(overall_score) as avg
            FROM `tabFeedback Response`
            WHERE feedback_form = %s AND status IN ('Valid', 'Submitted')
        """, form_name)[0][0] or 0

        frappe.db.set_value("Feedback Form", form_name, {
            "response_count": response_count,
            "average_score": avg_score
        }, update_modified=False)

    except Exception as e:
        frappe.log_error(f"Form statistics update error: {str(e)}", "Feedback Portal")
