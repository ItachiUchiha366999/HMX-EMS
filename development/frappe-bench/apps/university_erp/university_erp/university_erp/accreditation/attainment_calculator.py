# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
CO-PO Attainment Calculator for OBE/NBA Accreditation

This module calculates Course Outcome (CO) and Program Outcome (PO) attainment
following NBA/NAAC guidelines. It integrates with the existing university_obe module.
"""

import frappe
from frappe import _
from frappe.utils import flt
from typing import Dict, List, Optional


class COPOAttainmentCalculator:
    """
    Calculator for Course Outcome and Program Outcome attainment
    Following NBA/NAAC guidelines

    Integrates with existing university_obe module DocTypes:
    - Course Outcome (university_obe)
    - Program Outcome (university_obe)
    - CO PO Mapping (university_obe)
    """

    def __init__(self, course: str, academic_year: str = None, academic_term: str = None):
        self.course = course
        self.academic_year = academic_year or self._get_current_academic_year()
        self.academic_term = academic_term
        self.course_outcomes = self._get_course_outcomes()

    def _get_current_academic_year(self) -> str:
        """Get current default academic year"""
        return frappe.db.get_value("Academic Year", {"is_default": 1}, "name") or ""

    def _get_course_outcomes(self) -> List:
        """Get all course outcomes for the course from university_obe module"""
        return frappe.get_all("Course Outcome",
            filters={"course": self.course, "status": "Active"},
            fields=["name", "co_number", "co_code", "co_statement", "target_attainment",
                    "bloom_level", "current_attainment"],
            order_by="co_number"
        )

    def calculate_direct_attainment(self) -> Dict:
        """
        Calculate direct CO attainment from assessments

        Direct attainment sources:
        - University Examinations
        - Internal Assessments
        - Lab/Practical Exams
        - Assignments/Projects

        Returns:
            Dict with CO-wise direct attainment data
        """
        results = {}

        for co in self.course_outcomes:
            co_code = co.co_code or f"CO{co.co_number}"

            # Get assessment results mapped to this CO
            assessment_data = self._get_co_assessment_data(co.name)

            if assessment_data["total_students"] == 0:
                results[co_code] = {
                    "attainment": 0,
                    "level": 0,
                    "level_text": "Not Calculated",
                    "students_achieved": 0,
                    "total_students": 0,
                    "target": co.target_attainment or 60
                }
                continue

            # Calculate attainment percentage
            attainment_pct = (assessment_data["students_achieved"] / assessment_data["total_students"]) * 100

            # Determine attainment level (NBA criteria)
            if attainment_pct >= 70:
                level = 3
                level_text = "Level 3 (>=70%)"
            elif attainment_pct >= 60:
                level = 2
                level_text = "Level 2 (60-69%)"
            elif attainment_pct >= 50:
                level = 1
                level_text = "Level 1 (50-59%)"
            else:
                level = 0
                level_text = "Not Attained (<50%)"

            results[co_code] = {
                "attainment": round(attainment_pct, 2),
                "level": level,
                "level_text": level_text,
                "students_achieved": assessment_data["students_achieved"],
                "total_students": assessment_data["total_students"],
                "target": co.target_attainment or 60
            }

        return results

    def _get_co_assessment_data(self, course_outcome: str) -> Dict:
        """
        Get assessment data for a specific CO

        Looks for assessments linked to this CO via Assessment CO Link child table
        """
        total_students = 0
        students_achieved = 0
        threshold = 50  # 50% threshold for achievement

        # Check if Assessment Plan doctype exists with CO mapping
        if frappe.db.exists("DocType", "Assessment Plan"):
            assessments = frappe.get_all("Assessment Plan",
                filters={
                    "course": self.course,
                    "academic_year": self.academic_year
                },
                fields=["name", "maximum_score"]
            )

            for assessment in assessments:
                # Check if this assessment is mapped to the CO
                co_link = frappe.db.exists("Assessment CO Link", {
                    "parent": assessment.name,
                    "course_outcome": course_outcome
                })

                if not co_link:
                    continue

                # Get student results for this assessment
                results = frappe.get_all("Assessment Result",
                    filters={
                        "assessment_plan": assessment.name,
                        "docstatus": 1
                    },
                    fields=["student", "score", "maximum_score"]
                )

                for result in results:
                    total_students += 1
                    if result.maximum_score and result.maximum_score > 0:
                        percentage = (flt(result.score) / flt(result.maximum_score)) * 100
                        if percentage >= threshold:
                            students_achieved += 1

        # If no assessment data, try to get from CO Attainment doctype
        if total_students == 0:
            co_attainment = frappe.db.get_value("CO Direct Attainment",
                {
                    "course_outcome": course_outcome,
                    "academic_year": self.academic_year
                },
                ["total_students", "students_above_threshold"],
                as_dict=True
            )
            if co_attainment:
                total_students = co_attainment.total_students or 0
                students_achieved = co_attainment.students_above_threshold or 0

        return {
            "total_students": total_students,
            "students_achieved": students_achieved
        }

    def calculate_indirect_attainment(self) -> Dict:
        """
        Calculate indirect CO attainment from surveys

        Indirect attainment sources:
        - Course Exit Survey
        - Graduate Exit Survey
        - Alumni Survey
        - Employer Survey

        Returns:
            Dict with CO-wise indirect attainment data
        """
        results = {}

        for co in self.course_outcomes:
            co_code = co.co_code or f"CO{co.co_number}"

            # Get survey responses for this CO
            survey_data = self._get_co_survey_data(co.name)

            if survey_data["total_responses"] == 0:
                results[co_code] = {
                    "attainment": 0,
                    "responses": 0,
                    "average_rating": 0
                }
                continue

            # Convert 5-point scale to percentage
            attainment_pct = survey_data["average_rating"] * 20

            results[co_code] = {
                "attainment": round(attainment_pct, 2),
                "responses": survey_data["total_responses"],
                "average_rating": survey_data["average_rating"]
            }

        return results

    def _get_co_survey_data(self, course_outcome: str) -> Dict:
        """Get survey data for a specific CO from OBE Survey or Feedback"""
        total_responses = 0
        avg_rating = 0

        # Try to get from CO Indirect Attainment
        indirect = frappe.db.get_value("CO Indirect Attainment",
            {
                "course_outcome": course_outcome,
                "academic_year": self.academic_year
            },
            ["average_rating", "total_responses"],
            as_dict=True
        )

        if indirect:
            return {
                "total_responses": indirect.total_responses or 0,
                "average_rating": flt(indirect.average_rating)
            }

        # Try to get from OBE Survey
        if frappe.db.exists("DocType", "OBE Survey"):
            survey_responses = frappe.db.sql("""
                SELECT AVG(spr.rating) as avg_rating, COUNT(*) as count
                FROM `tabSurvey PO Rating` spr
                JOIN `tabOBE Survey` os ON spr.parent = os.name
                WHERE os.course = %s
                AND os.docstatus = 1
                AND spr.outcome_type = 'CO'
                AND spr.outcome = %s
            """, (self.course, course_outcome), as_dict=True)

            if survey_responses and survey_responses[0].avg_rating:
                return {
                    "total_responses": survey_responses[0].count or 0,
                    "average_rating": flt(survey_responses[0].avg_rating)
                }

        return {"total_responses": 0, "average_rating": 0}

    def calculate_overall_attainment(self, direct_weight: float = 0.8,
                                    indirect_weight: float = 0.2) -> Dict:
        """
        Calculate overall CO attainment

        Args:
            direct_weight: Weight for direct attainment (default 80%)
            indirect_weight: Weight for indirect attainment (default 20%)

        Returns:
            Dict with CO-wise overall attainment data
        """
        direct = self.calculate_direct_attainment()
        indirect = self.calculate_indirect_attainment()

        results = {}

        for co in self.course_outcomes:
            co_code = co.co_code or f"CO{co.co_number}"

            direct_att = direct.get(co_code, {}).get("attainment", 0)
            indirect_att = indirect.get(co_code, {}).get("attainment", 0)

            overall = (direct_att * direct_weight) + (indirect_att * indirect_weight)

            # Determine if target is met
            target = co.target_attainment or 60
            target_met = overall >= target

            results[co_code] = {
                "direct_attainment": direct_att,
                "indirect_attainment": indirect_att,
                "overall_attainment": round(overall, 2),
                "target": target,
                "target_met": target_met,
                "gap": round(target - overall, 2) if not target_met else 0
            }

            # Update Course Outcome document
            frappe.db.set_value("Course Outcome", co.name, {
                "current_attainment": overall
            })

        return results

    def calculate_po_attainment(self, program: str) -> Dict:
        """
        Calculate Program Outcome attainment from Course Outcomes

        Uses weighted average based on CO-PO correlation levels from
        the CO PO Mapping doctype in university_obe module

        Args:
            program: Program name/ID

        Returns:
            Dict with PO-wise attainment data
        """
        # Get Program Outcomes from university_obe
        program_outcomes = frappe.get_all("Program Outcome",
            filters={"program": program, "status": "Active"},
            fields=["name", "po_number", "po_code", "target_attainment", "po_title"]
        )

        results = {}

        for po in program_outcomes:
            po_code = po.po_code or f"PO{po.po_number}"

            # Get CO-PO mappings from CO PO Mapping Entry
            mappings = frappe.db.sql("""
                SELECT
                    cpe.course_outcome,
                    co.course,
                    co.current_attainment,
                    cpe.correlation_level
                FROM `tabCO PO Mapping Entry` cpe
                JOIN `tabCO PO Mapping` cpm ON cpe.parent = cpm.name
                JOIN `tabCourse Outcome` co ON cpe.course_outcome = co.name
                WHERE cpe.program_outcome = %s
                AND cpm.docstatus = 1
            """, po.name, as_dict=True)

            if not mappings:
                results[po_code] = {
                    "attainment": 0,
                    "level": "Not Calculated",
                    "contributing_cos": 0,
                    "target": po.target_attainment or 60
                }
                continue

            # Calculate weighted average
            total_weighted = 0
            total_weight = 0

            for mapping in mappings:
                weight = flt(mapping.correlation_level) or 1
                attainment = flt(mapping.current_attainment) or 0

                total_weighted += attainment * weight
                total_weight += weight

            po_attainment = total_weighted / total_weight if total_weight > 0 else 0

            # Determine level
            if po_attainment >= 70:
                level = "Level 3 (High)"
            elif po_attainment >= 60:
                level = "Level 2 (Medium)"
            elif po_attainment >= 50:
                level = "Level 1 (Low)"
            else:
                level = "Not Attained"

            target = po.target_attainment or 60

            results[po_code] = {
                "attainment": round(po_attainment, 2),
                "level": level,
                "target": target,
                "target_met": po_attainment >= target,
                "contributing_cos": len(mappings)
            }

            # Update Program Outcome document
            frappe.db.set_value("Program Outcome", po.name, {
                "current_attainment": po_attainment
            })

        return results


@frappe.whitelist()
def calculate_course_attainment(course: str, academic_year: str = None) -> Dict:
    """
    API to calculate course attainment

    Args:
        course: Course name/ID
        academic_year: Optional academic year

    Returns:
        Dict with CO-wise attainment data
    """
    calculator = COPOAttainmentCalculator(course, academic_year)
    return calculator.calculate_overall_attainment()


@frappe.whitelist()
def calculate_program_attainment(program: str, academic_year: str = None) -> Dict:
    """
    API to calculate program attainment

    Args:
        program: Program name/ID
        academic_year: Optional academic year

    Returns:
        Dict with PO-wise attainment data
    """
    # First calculate CO attainment for all courses in program
    courses = frappe.get_all("Program Course",
        filters={"parent": program},
        pluck="course"
    )

    # Calculate CO attainment for each course
    for course in courses:
        calculator = COPOAttainmentCalculator(course, academic_year)
        calculator.calculate_overall_attainment()

    # Then calculate PO attainment
    if courses:
        calculator = COPOAttainmentCalculator(courses[0], academic_year)
        return calculator.calculate_po_attainment(program)

    return {}


@frappe.whitelist()
def get_copo_matrix(course: str, program: str, academic_term: str = None) -> Dict:
    """
    Get CO-PO mapping matrix with attainment values

    Args:
        course: Course name/ID
        program: Program name/ID
        academic_term: Optional academic term

    Returns:
        Dict with matrix data for display
    """
    # Get Course Outcomes
    cos = frappe.get_all("Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "co_number", "co_code", "co_statement", "current_attainment"],
        order_by="co_number"
    )

    # Get Program Outcomes
    pos = frappe.get_all("Program Outcome",
        filters={"program": program, "status": "Active"},
        fields=["name", "po_number", "po_code", "po_title", "current_attainment"],
        order_by="po_number"
    )

    # Get CO-PO Mapping
    mapping = frappe.get_all("CO PO Mapping",
        filters={
            "course": course,
            "program": program,
            "docstatus": 1
        },
        fields=["name"]
    )

    matrix = []
    for co in cos:
        row = {
            "co_code": co.co_code or f"CO{co.co_number}",
            "co_statement": co.co_statement,
            "co_attainment": co.current_attainment
        }

        # Get mapping for each PO
        for po in pos:
            po_code = po.po_code or f"PO{po.po_number}"

            # Get correlation level from mapping
            correlation = 0
            if mapping:
                entry = frappe.db.get_value("CO PO Mapping Entry",
                    {
                        "parent": mapping[0].name,
                        "course_outcome": co.name,
                        "program_outcome": po.name
                    },
                    "correlation_level"
                )
                if entry:
                    correlation = entry

            row[po_code] = correlation

        matrix.append(row)

    return {
        "course_outcomes": cos,
        "program_outcomes": pos,
        "matrix": matrix
    }
