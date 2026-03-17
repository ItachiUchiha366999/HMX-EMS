# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt


def get_context(context):
    """Faculty grade entry page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Faculty Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("You are not registered as faculty"), frappe.PermissionError)

    # Get specific assessment if provided
    assessment_plan = frappe.form_dict.get("assessment")

    context.no_cache = 1
    context.instructor = instructor
    context.pending_assessments = get_pending_assessments(instructor.name)
    context.selected_assessment = get_assessment_details(assessment_plan) if assessment_plan else None
    context.students = get_students_for_grading(assessment_plan) if assessment_plan else []
    context.grading_scale = get_grading_scale()

    return context


def get_pending_assessments(instructor):
    """Get assessments pending grading"""
    assessments = frappe.db.sql("""
        SELECT
            ap.name,
            ap.assessment_name,
            ap.course,
            ap.student_group,
            ap.assessment_date,
            ap.maximum_assessment_score,
            (SELECT COUNT(*) FROM `tabStudent Group Student` WHERE parent = ap.student_group AND active = 1) as student_count,
            (SELECT COUNT(*) FROM `tabAssessment Result` WHERE assessment_plan = ap.name AND docstatus = 1) as graded_count
        FROM `tabAssessment Plan` ap
        WHERE ap.supervisor = %s
        AND ap.docstatus = 1
        ORDER BY ap.assessment_date DESC
        LIMIT 20
    """, instructor, as_dict=1)

    return assessments


def get_assessment_details(assessment_plan):
    """Get assessment plan details"""
    return frappe.db.get_value(
        "Assessment Plan",
        assessment_plan,
        ["name", "assessment_name", "course", "student_group", "assessment_date",
         "maximum_assessment_score", "grading_scale", "supervisor"],
        as_dict=1
    )


def get_students_for_grading(assessment_plan):
    """Get students for grade entry"""
    assessment = frappe.get_doc("Assessment Plan", assessment_plan)

    students = frappe.db.sql("""
        SELECT
            sgs.student,
            s.student_name,
            s.image,
            ar.name as result_id,
            ar.obtained_marks,
            ar.grade,
            ar.grade_points
        FROM `tabStudent Group Student` sgs
        JOIN `tabStudent` s ON s.name = sgs.student
        LEFT JOIN `tabAssessment Result` ar ON ar.student = sgs.student
            AND ar.assessment_plan = %s
            AND ar.docstatus = 1
        WHERE sgs.parent = %s
        AND sgs.active = 1
        ORDER BY s.student_name
    """, (assessment_plan, assessment.student_group), as_dict=1)

    return students


def get_grading_scale():
    """Get default grading scale"""
    # Try to get the default grading scale
    default_scale = frappe.db.get_value("Grading Scale", {"is_default": 1}, "name")
    if not default_scale:
        return []

    intervals = frappe.db.get_all(
        "Grading Scale Interval",
        filters={"parent": default_scale},
        fields=["grade_code", "grade_description", "threshold", "grade_points"],
        order_by="threshold desc"
    )

    return intervals


@frappe.whitelist()
def submit_assessment_results(assessment_plan, results_data):
    """Submit assessment results"""
    import json

    from university_erp.university_portals.www.faculty_portal.index import get_current_instructor

    instructor = get_current_instructor()
    if not instructor:
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    # Verify instructor is the supervisor
    assessment = frappe.get_doc("Assessment Plan", assessment_plan)
    if assessment.supervisor != instructor.name:
        frappe.throw(_("You can only grade assessments you supervise"), frappe.PermissionError)

    if isinstance(results_data, str):
        results_data = json.loads(results_data)

    saved_count = 0
    for record in results_data:
        student = record.get("student")
        obtained_marks = flt(record.get("obtained_marks", 0))

        # Calculate grade based on percentage
        percentage = (obtained_marks / assessment.maximum_assessment_score) * 100 if assessment.maximum_assessment_score else 0
        grade_info = calculate_grade(percentage, assessment.grading_scale)

        # Check if result exists
        existing = frappe.db.get_value("Assessment Result", {
            "student": student,
            "assessment_plan": assessment_plan,
            "docstatus": 1
        })

        if existing:
            # Update existing
            frappe.db.set_value("Assessment Result", existing, {
                "obtained_marks": obtained_marks,
                "percentage": percentage,
                "grade": grade_info.get("grade"),
                "grade_points": grade_info.get("grade_points")
            })
        else:
            # Create new
            result = frappe.get_doc({
                "doctype": "Assessment Result",
                "student": student,
                "assessment_plan": assessment_plan,
                "course": assessment.course,
                "assessment_name": assessment.assessment_name,
                "maximum_marks": assessment.maximum_assessment_score,
                "obtained_marks": obtained_marks,
                "percentage": percentage,
                "grade": grade_info.get("grade"),
                "grade_points": grade_info.get("grade_points")
            })
            result.insert(ignore_permissions=True)
            result.submit()

        saved_count += 1

    return {
        "success": True,
        "message": _("Results saved for {0} students").format(saved_count)
    }


def calculate_grade(percentage, grading_scale=None):
    """Calculate grade from percentage"""
    if not grading_scale:
        grading_scale = frappe.db.get_value("Grading Scale", {"is_default": 1}, "name")

    if not grading_scale:
        return {"grade": "", "grade_points": 0}

    intervals = frappe.db.get_all(
        "Grading Scale Interval",
        filters={"parent": grading_scale},
        fields=["grade_code", "threshold", "grade_points"],
        order_by="threshold desc"
    )

    for interval in intervals:
        if percentage >= interval.threshold:
            return {
                "grade": interval.grade_code,
                "grade_points": interval.grade_points
            }

    return {"grade": "F", "grade_points": 0}
