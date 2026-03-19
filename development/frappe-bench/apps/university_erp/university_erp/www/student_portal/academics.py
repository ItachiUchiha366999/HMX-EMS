# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def get_context(context):
    """Student academics page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "academics"
    context.results = get_student_results(student.name)
    context.semester_results = get_semester_wise_results(student.name)
    context.cgpa_trend = get_cgpa_trend(student.name)
    context.current_courses = get_current_courses(student.name)
    context.total_courses = get_total_courses(student.name)
    context.total_credits = get_total_credits(student.name)
    context.current_cgpa = get_current_cgpa(student.name)

    return context


def get_current_student():
    """Get current logged in student"""
    try:
        user = frappe.session.user
        student = frappe.db.get_value(
            "Student",
            {"user": user},
            ["name", "student_name", "image"],
            as_dict=1
        )
        return student
    except Exception:
        return None


def get_student_results(student):
    """Get all results for student using Assessment Result"""
    try:
        # Check if Assessment Result doctype exists
        if not frappe.db.exists("DocType", "Assessment Result"):
            return []

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
        if not frappe.db.exists("DocType", "Assessment Result"):
            return {}

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

        query = """
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
            key = "{year} - {term}".format(term=term, year=year)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(result)

        return grouped
    except Exception:
        return {}


def get_cgpa_trend(student):
    """Get CGPA trend over semesters - calculated from Assessment Results"""
    try:
        if not frappe.db.exists("DocType", "Assessment Result"):
            return []

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
            sgpa = round(avg_pct / 10, 2)
            trend.append({
                "semester": semester,
                "sgpa": sgpa,
                "cgpa": sgpa
            })

        return trend
    except Exception:
        return []


def get_current_courses(student):
    """Get currently enrolled courses"""
    try:
        student_groups = frappe.db.get_all(
            "Student Group Student",
            filters={"student": student, "active": 1},
            pluck="parent"
        )

        if not student_groups:
            return []

        courses = []
        for sg in student_groups:
            group_info = frappe.db.get_value(
                "Student Group",
                sg,
                ["course", "program"],
                as_dict=1
            )

            if group_info and group_info.course:
                # Check which fields exist on Course
                course_meta = frappe.get_meta("Course")
                course_fields = [f.fieldname for f in course_meta.fields]

                fetch_fields = ["name"]
                if "course_name" in course_fields:
                    fetch_fields.append("course_name")
                if "course_code" in course_fields:
                    fetch_fields.append("course_code")
                if "credits" in course_fields:
                    fetch_fields.append("credits")

                course_info = frappe.db.get_value(
                    "Course",
                    group_info.course,
                    fetch_fields,
                    as_dict=1
                )

                if course_info:
                    courses.append({
                        "course": group_info.course,
                        "course_name": course_info.get("course_name", group_info.course),
                        "credits": course_info.get("credits", 0)
                    })

        return courses
    except Exception:
        return []


def get_total_courses(student):
    """Get total number of courses completed"""
    try:
        if not frappe.db.exists("DocType", "Assessment Result"):
            return 0

        count = frappe.db.sql("""
            SELECT COUNT(DISTINCT course) as count
            FROM `tabAssessment Result`
            WHERE student = %s
            AND docstatus = 1
        """, student, as_dict=1)

        return count[0].count if count else 0
    except Exception:
        return 0


def get_total_credits(student):
    """Get total credits earned"""
    try:
        if not frappe.db.exists("DocType", "Assessment Result"):
            return 0

        # Check if Course has credits field
        course_meta = frappe.get_meta("Course")
        course_fields = [f.fieldname for f in course_meta.fields]

        if "credits" not in course_fields:
            return 0

        # Check if Assessment Result has grade field
        ar_meta = frappe.get_meta("Assessment Result")
        ar_fields = [f.fieldname for f in ar_meta.fields]

        if "grade" in ar_fields:
            credits = frappe.db.sql("""
                SELECT COALESCE(SUM(c.credits), 0) as total
                FROM `tabAssessment Result` ar
                JOIN `tabCourse` c ON c.name = ar.course
                WHERE ar.student = %s
                AND ar.docstatus = 1
                AND ar.grade NOT IN ('F', 'Fail')
            """, student, as_dict=1)
        else:
            # Without grade filtering
            credits = frappe.db.sql("""
                SELECT COALESCE(SUM(c.credits), 0) as total
                FROM `tabAssessment Result` ar
                JOIN `tabCourse` c ON c.name = ar.course
                WHERE ar.student = %s
                AND ar.docstatus = 1
            """, student, as_dict=1)

        return int(credits[0].total) if credits else 0
    except Exception:
        return 0


def get_current_cgpa(student):
    """Get current CGPA from student record or calculate"""
    try:
        # First try from custom field on Student
        cgpa = frappe.db.get_value("Student", student, "custom_cgpa")
        if cgpa:
            return flt(cgpa, 2)

        if not frappe.db.exists("DocType", "Assessment Result"):
            return 0.0

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
            return round(result[0].avg_percentage / 10, 2)

        return 0.0
    except Exception:
        return 0.0
