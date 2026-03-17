# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def get_context(context):
    """Student results page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "results"
    context.results = get_student_results(student.name)
    context.semester_results = get_semester_wise_results(student.name)
    context.cgpa_trend = get_cgpa_trend(student.name)
    context.current_cgpa = get_current_cgpa(student.name)

    return context


def get_student_results(student):
    """Get all results for student using Assessment Result"""
    try:
        # Use Assessment Result instead of non-existent Student Result
        # Get available fields first
        meta = frappe.get_meta("Assessment Result")
        available_fields = [f.fieldname for f in meta.fields]

        base_fields = ["name", "student", "course"]
        optional_fields = [
            "academic_year", "academic_term", "assessment_plan",
            "maximum_score", "total_score", "grade", "comment"
        ]

        select_fields = base_fields.copy()
        for field in optional_fields:
            if field in available_fields:
                select_fields.append(field)

        results = frappe.db.get_all(
            "Assessment Result",
            filters={"student": student, "docstatus": 1},
            fields=select_fields,
            order_by="creation desc"
        )

        # Enrich with course names
        for result in results:
            if result.get("course"):
                course_name = frappe.db.get_value("Course", result.course, "course_name")
                result["course_name"] = course_name or result.course

            # Calculate percentage if scores available
            if result.get("total_score") and result.get("maximum_score"):
                result["percentage"] = round((result.total_score / result.maximum_score) * 100, 1)

        return results
    except Exception:
        return []


def get_semester_wise_results(student):
    """Get course-wise results grouped by semester"""
    try:
        meta = frappe.get_meta("Assessment Result")
        available_fields = [f.fieldname for f in meta.fields]

        # Build query based on available fields
        select_parts = ["ar.name", "ar.course", "ar.student"]

        if "academic_year" in available_fields:
            select_parts.append("ar.academic_year")
        if "academic_term" in available_fields:
            select_parts.append("ar.academic_term")
        if "assessment_plan" in available_fields:
            select_parts.append("ar.assessment_plan")
        if "maximum_score" in available_fields:
            select_parts.append("ar.maximum_score")
        if "total_score" in available_fields:
            select_parts.append("ar.total_score")
        if "grade" in available_fields:
            select_parts.append("ar.grade")

        query = f"""
            SELECT {', '.join(select_parts)}
            FROM `tabAssessment Result` ar
            WHERE ar.student = %s
            AND ar.docstatus = 1
            ORDER BY ar.creation DESC
        """

        course_results = frappe.db.sql(query, student, as_dict=1)

        # Enrich with course names
        for result in course_results:
            if result.get("course"):
                course_name = frappe.db.get_value("Course", result.course, "course_name")
                result["course_name"] = course_name or result.course

            # Calculate percentage
            if result.get("total_score") and result.get("maximum_score"):
                result["percentage"] = round((result.total_score / result.maximum_score) * 100, 1)

        # Group by semester if academic_year and academic_term available
        grouped = {}
        for result in course_results:
            year = result.get("academic_year", "Unknown")
            term = result.get("academic_term", "Unknown")
            key = f"{year} - {term}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(result)

        return grouped
    except Exception:
        return {}


def get_cgpa_trend(student):
    """Get CGPA trend over semesters - calculated from Assessment Results"""
    try:
        meta = frappe.get_meta("Assessment Result")
        available_fields = [f.fieldname for f in meta.fields]

        if "academic_year" not in available_fields or "academic_term" not in available_fields:
            return []

        if "maximum_score" not in available_fields or "total_score" not in available_fields:
            return []

        # Get semester-wise averages
        query = """
            SELECT
                ar.academic_year,
                ar.academic_term,
                AVG(ar.total_score * 100.0 / NULLIF(ar.maximum_score, 0)) as avg_percentage
            FROM `tabAssessment Result` ar
            WHERE ar.student = %s
            AND ar.docstatus = 1
            AND ar.maximum_score > 0
            GROUP BY ar.academic_year, ar.academic_term
            ORDER BY ar.academic_year ASC, ar.academic_term ASC
        """

        results = frappe.db.sql(query, student, as_dict=1)

        # Convert percentage to approximate GPA (10-point scale)
        trend = []
        for r in results:
            semester = f"{r.academic_year} - {r.academic_term}"
            avg_pct = r.avg_percentage or 0
            # Simple conversion: percentage/10 to get GPA on 10-point scale
            sgpa = round(avg_pct / 10, 2)
            trend.append({
                "semester": semester,
                "sgpa": sgpa,
                "cgpa": sgpa  # Simplified - would need cumulative calculation
            })

        return trend
    except Exception:
        return []


def get_current_cgpa(student):
    """Get current CGPA from student record or calculate"""
    try:
        # First try from custom field on Student
        cgpa = frappe.db.get_value("Student", student, "custom_cgpa")
        if cgpa:
            return flt(cgpa, 2)

        # Check if Assessment Result has the needed fields
        meta = frappe.get_meta("Assessment Result")
        available_fields = [f.fieldname for f in meta.fields]

        if "maximum_score" not in available_fields or "total_score" not in available_fields:
            return 0.0

        # Fallback: calculate from Assessment Results
        result = frappe.db.sql("""
            SELECT AVG(ar.total_score * 100.0 / NULLIF(ar.maximum_score, 0)) as avg_percentage
            FROM `tabAssessment Result` ar
            WHERE ar.student = %s
            AND ar.docstatus = 1
            AND ar.maximum_score > 0
        """, student, as_dict=1)

        if result and result[0].avg_percentage:
            # Convert to 10-point GPA
            return round(result[0].avg_percentage / 10, 2)

        return 0.0
    except Exception:
        return 0.0
