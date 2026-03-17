"""
Internal Assessment Manager

Manager class for handling internal assessment operations including
bulk score entry, CO attainment calculation, and grade processing.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, flt
from typing import Dict, List
import json


class InternalAssessmentManager:
    """
    Manager for internal assessment operations
    """

    @staticmethod
    def create_assessment(data: dict) -> str:
        """
        Create a new internal assessment

        Args:
            data: Assessment data dict

        Returns:
            Created assessment name
        """
        assessment = frappe.new_doc("Internal Assessment")
        assessment.update(data)
        assessment.insert()
        return assessment.name

    @staticmethod
    def bulk_create_assessments(course: str, academic_year: str,
                               academic_term: str, assessment_types: list) -> List[str]:
        """
        Create multiple assessments for a course

        Args:
            course: Course name
            academic_year: Academic year
            academic_term: Academic term
            assessment_types: List of assessment types to create

        Returns:
            List of created assessment names
        """
        created = []
        course_doc = frappe.get_doc("Course", course)

        for idx, atype in enumerate(assessment_types, 1):
            assessment = frappe.new_doc("Internal Assessment")
            assessment.assessment_name = f"{course_doc.course_code} - {atype} {idx}"
            assessment.assessment_type = atype
            assessment.course = course
            assessment.academic_year = academic_year
            assessment.academic_term = academic_term
            assessment.assessment_date = getdate(now_datetime())
            assessment.maximum_marks = 20  # Default
            assessment.status = "Draft"
            assessment.insert()
            created.append(assessment.name)

        return created

    @staticmethod
    def import_scores_from_excel(assessment_name: str, file_path: str) -> Dict:
        """
        Import scores from Excel file

        Args:
            assessment_name: Assessment document name
            file_path: Path to Excel file

        Returns:
            Import result summary
        """
        try:
            import pandas as pd
        except ImportError:
            frappe.throw(_("pandas library required for Excel import"))

        assessment = frappe.get_doc("Internal Assessment", assessment_name)

        # Read Excel
        df = pd.read_excel(file_path)
        required_cols = ['roll_number', 'marks']

        for col in required_cols:
            if col not in df.columns:
                frappe.throw(_("Column '{0}' not found in Excel").format(col))

        imported = 0
        errors = []

        for _, row in df.iterrows():
            roll = str(row['roll_number'])
            marks = flt(row['marks'])

            # Find student by roll number
            student = frappe.db.get_value("Student", {"roll_number": roll})
            if not student:
                errors.append(f"Student with roll {roll} not found")
                continue

            try:
                assessment.record_score(student, marks)
                imported += 1
            except Exception as e:
                errors.append(f"Error for {roll}: {str(e)}")

        return {
            "imported": imported,
            "errors": errors,
            "total_rows": len(df)
        }

    @staticmethod
    def calculate_course_co_attainment(course: str, academic_year: str,
                                       academic_term: str = None) -> Dict:
        """
        Calculate overall CO attainment for a course across all assessments

        Args:
            course: Course name
            academic_year: Academic year
            academic_term: Optional term filter

        Returns:
            CO-wise attainment summary
        """
        filters = {
            "course": course,
            "academic_year": academic_year,
            "docstatus": 1
        }
        if academic_term:
            filters["academic_term"] = academic_term

        assessments = frappe.get_all(
            "Internal Assessment",
            filters=filters,
            pluck="name"
        )

        co_data = {}

        for assessment_name in assessments:
            assessment = frappe.get_doc("Internal Assessment", assessment_name)
            attainment = assessment.calculate_co_attainment()

            for co, data in attainment.items():
                if co not in co_data:
                    co_data[co] = {
                        "total_attainment": 0,
                        "count": 0,
                        "assessments": []
                    }

                co_data[co]["total_attainment"] += data.get("attainment_percentage", 0)
                co_data[co]["count"] += 1
                co_data[co]["assessments"].append({
                    "assessment": assessment_name,
                    "attainment": data.get("attainment_percentage", 0)
                })

        # Calculate averages
        result = {}
        for co, data in co_data.items():
            result[co] = {
                "average_attainment": data["total_attainment"] / data["count"]
                                     if data["count"] > 0 else 0,
                "assessment_count": data["count"],
                "details": data["assessments"]
            }

        return result

    @staticmethod
    def get_student_assessment_summary(student: str, academic_year: str,
                                       course: str = None) -> Dict:
        """
        Get comprehensive assessment summary for a student

        Args:
            student: Student name
            academic_year: Academic year
            course: Optional course filter

        Returns:
            Summary with all assessment scores
        """
        filters = {"academic_year": academic_year}
        if course:
            filters["course"] = course

        assessments = frappe.get_all(
            "Internal Assessment",
            filters=filters,
            fields=["name", "assessment_name", "assessment_type", "course",
                   "maximum_marks", "weightage"]
        )

        summary = {
            "student": student,
            "academic_year": academic_year,
            "assessments": [],
            "total_weighted_score": 0,
            "total_weightage": 0,
            "course_summaries": {}
        }

        for assessment in assessments:
            score = frappe.db.get_value(
                "Internal Assessment Score",
                {"parent": assessment.name, "student": student},
                ["total_marks", "percentage", "grade"],
                as_dict=True
            )

            if score:
                assessment_data = {
                    **assessment,
                    **score,
                    "weighted_score": (score.percentage or 0) * (assessment.weightage or 0) / 100
                }
                summary["assessments"].append(assessment_data)
                summary["total_weighted_score"] += assessment_data["weighted_score"]
                summary["total_weightage"] += assessment.weightage or 0

                # Course-wise summary
                if assessment.course not in summary["course_summaries"]:
                    summary["course_summaries"][assessment.course] = {
                        "total_marks": 0,
                        "total_max": 0,
                        "assessments": []
                    }

                summary["course_summaries"][assessment.course]["total_marks"] += score.total_marks or 0
                summary["course_summaries"][assessment.course]["total_max"] += assessment.maximum_marks
                summary["course_summaries"][assessment.course]["assessments"].append(assessment.name)

        return summary

    @staticmethod
    def generate_grade_sheet(course: str, academic_year: str, academic_term: str) -> List[Dict]:
        """
        Generate comprehensive grade sheet for a course

        Args:
            course: Course name
            academic_year: Academic year
            academic_term: Academic term

        Returns:
            List of student grades
        """
        # Get all assessments for the course
        assessments = frappe.get_all(
            "Internal Assessment",
            filters={
                "course": course,
                "academic_year": academic_year,
                "academic_term": academic_term
            },
            fields=["name", "assessment_name", "assessment_type",
                   "maximum_marks", "weightage"],
            order_by="assessment_date"
        )

        # Get all students
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={
                "course": course,
                "academic_year": academic_year,
                "enrollment_status": "Enrolled"
            },
            fields=["student"]
        )

        grade_sheet = []

        for enrollment in enrollments:
            student = frappe.get_doc("Student", enrollment.student)
            student_row = {
                "student": student.name,
                "student_name": student.student_name,
                "roll_number": student.roll_number,
                "assessments": {},
                "total_marks": 0,
                "total_max_marks": 0,
                "total_weighted": 0
            }

            for assessment in assessments:
                score = frappe.db.get_value(
                    "Internal Assessment Score",
                    {"parent": assessment.name, "student": student.name},
                    ["total_marks", "percentage", "grade"],
                    as_dict=True
                )

                student_row["assessments"][assessment.name] = {
                    "type": assessment.assessment_type,
                    "marks": score.total_marks if score else None,
                    "max_marks": assessment.maximum_marks,
                    "percentage": score.percentage if score else None,
                    "grade": score.grade if score else None
                }

                if score and score.total_marks:
                    student_row["total_marks"] += score.total_marks
                    student_row["total_weighted"] += (
                        score.percentage * (assessment.weightage or 0) / 100
                    )

                student_row["total_max_marks"] += assessment.maximum_marks

            student_row["overall_percentage"] = (
                student_row["total_marks"] / student_row["total_max_marks"] * 100
                if student_row["total_max_marks"] > 0 else 0
            )

            grade_sheet.append(student_row)

        return sorted(grade_sheet, key=lambda x: x.get("roll_number", ""))


# API Functions

@frappe.whitelist()
def get_course_assessments(course: str, academic_year: str, academic_term: str = None):
    """
    Get all assessments for a course

    Args:
        course: Course name
        academic_year: Academic year
        academic_term: Optional term filter

    Returns:
        List of assessments with summary
    """
    filters = {
        "course": course,
        "academic_year": academic_year
    }
    if academic_term:
        filters["academic_term"] = academic_term

    return frappe.get_all(
        "Internal Assessment",
        filters=filters,
        fields=["name", "assessment_name", "assessment_type", "maximum_marks",
                "assessment_date", "status", "evaluated_count", "total_students",
                "average_marks"],
        order_by="assessment_date"
    )


@frappe.whitelist()
def record_bulk_scores(assessment_name: str, scores_json: str):
    """
    Record scores for multiple students

    Args:
        assessment_name: Assessment document name
        scores_json: JSON string of [{student, marks, remarks}, ...]

    Returns:
        Result summary
    """
    scores = json.loads(scores_json)
    assessment = frappe.get_doc("Internal Assessment", assessment_name)
    return assessment.bulk_upload_scores(scores)


@frappe.whitelist()
def get_co_attainment_report(course: str, academic_year: str, academic_term: str = None):
    """
    Get CO attainment report for a course

    Args:
        course: Course name
        academic_year: Academic year
        academic_term: Optional term filter

    Returns:
        CO attainment data
    """
    return InternalAssessmentManager.calculate_course_co_attainment(
        course, academic_year, academic_term
    )
