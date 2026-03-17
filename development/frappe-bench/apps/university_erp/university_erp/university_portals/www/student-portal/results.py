# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def get_context(context):
    """Student results page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.results = get_student_results(student.name)
    context.semester_results = get_semester_wise_results(student.name)
    context.cgpa_trend = get_cgpa_trend(student.name)

    return context


def get_student_results(student):
    """Get all results for student"""
    results = frappe.db.sql("""
        SELECT
            sr.name,
            sr.academic_year,
            sr.academic_term,
            sr.program,
            sr.total_marks,
            sr.percentage,
            sr.grade,
            sr.sgpa,
            sr.cgpa,
            sr.result_status,
            sr.publish_date
        FROM `tabStudent Result` sr
        WHERE sr.student = %s
        AND sr.docstatus = 1
        ORDER BY sr.academic_year DESC, sr.academic_term DESC
    """, student, as_dict=1)

    return results


def get_semester_wise_results(student):
    """Get course-wise results grouped by semester"""
    course_results = frappe.db.sql("""
        SELECT
            ar.name,
            ar.course,
            ar.course_name,
            ar.assessment_name,
            ar.maximum_marks,
            ar.obtained_marks,
            ar.percentage,
            ar.grade,
            ar.grade_points,
            ar.academic_year,
            ar.academic_term
        FROM `tabAssessment Result` ar
        WHERE ar.student = %s
        AND ar.docstatus = 1
        ORDER BY ar.academic_year DESC, ar.academic_term DESC, ar.course
    """, student, as_dict=1)

    # Group by semester
    grouped = {}
    for result in course_results:
        key = f"{result.academic_year} - {result.academic_term}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(result)

    return grouped


def get_cgpa_trend(student):
    """Get CGPA trend over semesters"""
    trend = frappe.db.sql("""
        SELECT
            CONCAT(academic_year, ' - ', academic_term) as semester,
            sgpa,
            cgpa
        FROM `tabStudent Result`
        WHERE student = %s
        AND docstatus = 1
        ORDER BY academic_year ASC, academic_term ASC
    """, student, as_dict=1)

    return trend
