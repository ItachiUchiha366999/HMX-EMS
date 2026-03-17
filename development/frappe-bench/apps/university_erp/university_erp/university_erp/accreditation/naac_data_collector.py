# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
NAAC Data Collector

Automated data collection for NAAC metrics across all 7 criteria.
Collects data from various DocTypes in the university ERP system.
"""

import frappe
from frappe import _
from frappe.utils import today, add_years, getdate, flt
from typing import Dict, List


class NAACDataCollector:
    """
    Automated data collection for NAAC metrics
    """

    def __init__(self, accreditation_cycle: str):
        self.cycle = frappe.get_doc("Accreditation Cycle", accreditation_cycle)
        self.period_start = self.cycle.data_period_start
        self.period_end = self.cycle.data_period_end

    def collect_all_metrics(self) -> Dict:
        """Collect data for all NAAC metrics"""
        results = {
            "criterion_1": self._collect_criterion_1(),
            "criterion_2": self._collect_criterion_2(),
            "criterion_3": self._collect_criterion_3(),
            "criterion_4": self._collect_criterion_4(),
            "criterion_5": self._collect_criterion_5(),
            "criterion_6": self._collect_criterion_6(),
            "criterion_7": self._collect_criterion_7()
        }
        return results

    def collect_metric_by_number(self, metric_number: str) -> Dict:
        """
        Collect data for a specific metric by its number

        Args:
            metric_number: Metric number like "1.1.1", "2.3.2"

        Returns:
            Dict with metric data
        """
        criterion = metric_number.split(".")[0]
        method_name = f"_metric_{metric_number.replace('.', '_')}"

        # Check if specific method exists
        if hasattr(self, method_name):
            return getattr(self, method_name)()

        return {"metric_number": metric_number, "value": 0, "status": "Not Implemented"}

    def _collect_criterion_1(self) -> Dict:
        """
        Criterion 1: Curricular Aspects (100 marks)
        """
        return {
            "1.1.1": self._metric_1_1_1(),
            "1.1.2": self._metric_1_1_2(),
            "1.2.1": self._metric_1_2_1(),
            "1.2.2": self._metric_1_2_2(),
            "1.3.1": self._metric_1_3_1(),
            "1.3.2": self._metric_1_3_2(),
            "1.4.1": self._metric_1_4_1()
        }

    def _metric_1_1_1(self) -> Dict:
        """1.1.1 - Programs with CBCS/Elective course system"""
        total_programs = frappe.db.count("Program", {"is_published": 1})

        # Count programs with elective courses
        programs_with_electives = frappe.db.sql("""
            SELECT COUNT(DISTINCT p.name)
            FROM `tabProgram` p
            JOIN `tabProgram Course` pc ON pc.parent = p.name
            JOIN `tabCourse` c ON c.name = pc.course
            WHERE p.is_published = 1
            AND (c.is_elective = 1 OR pc.is_elective = 1)
        """)[0][0] or 0

        percentage = (programs_with_electives / total_programs * 100) if total_programs > 0 else 0

        return {
            "metric_number": "1.1.1",
            "description": "Curricula developed with CBCS/Elective system",
            "value": round(percentage, 2),
            "numerator": programs_with_electives,
            "denominator": total_programs,
            "unit": "%"
        }

    def _metric_1_1_2(self) -> Dict:
        """1.1.2 - Programs with focus on employability/entrepreneurship"""
        total_programs = frappe.db.count("Program", {"is_published": 1})

        # Count programs with employability focus courses
        programs_with_focus = frappe.db.sql("""
            SELECT COUNT(DISTINCT p.name)
            FROM `tabProgram` p
            JOIN `tabProgram Course` pc ON pc.parent = p.name
            JOIN `tabCourse` c ON c.name = pc.course
            WHERE p.is_published = 1
            AND (c.course_name LIKE '%%Entrepreneurship%%'
                 OR c.course_name LIKE '%%Skill%%'
                 OR c.course_name LIKE '%%Industry%%'
                 OR c.course_name LIKE '%%Internship%%'
                 OR c.course_name LIKE '%%Project%%')
        """)[0][0] or 0

        percentage = (programs_with_focus / total_programs * 100) if total_programs > 0 else 0

        return {
            "metric_number": "1.1.2",
            "description": "Programs with focus on employability/entrepreneurship",
            "value": round(percentage, 2),
            "numerator": programs_with_focus,
            "denominator": total_programs,
            "unit": "%"
        }

    def _metric_1_2_1(self) -> Dict:
        """1.2.1 - New courses introduced"""
        new_courses = frappe.db.count("Course", {
            "creation": ["between", [self.period_start, self.period_end]]
        })

        return {
            "metric_number": "1.2.1",
            "description": "New courses introduced during assessment period",
            "value": new_courses,
            "unit": "count"
        }

    def _metric_1_2_2(self) -> Dict:
        """1.2.2 - Add-on/Certificate courses offered"""
        addon_courses = frappe.db.count("Course", {
            "course_type": ["in", ["Certificate", "Add-on", "Value Added"]]
        })

        return {
            "metric_number": "1.2.2",
            "description": "Add-on/Certificate courses offered",
            "value": addon_courses,
            "unit": "count"
        }

    def _metric_1_3_1(self) -> Dict:
        """1.3.1 - Value-added courses"""
        value_added = frappe.db.count("Course", {
            "course_type": "Value Added"
        })

        return {
            "metric_number": "1.3.1",
            "description": "Value-added courses offered",
            "value": value_added,
            "unit": "count"
        }

    def _metric_1_3_2(self) -> Dict:
        """1.3.2 - Students enrolled in value-added courses"""
        # Get students enrolled in value-added courses
        enrollments = frappe.db.sql("""
            SELECT COUNT(DISTINCT ce.student)
            FROM `tabCourse Enrollment` ce
            JOIN `tabCourse` c ON c.name = ce.course
            WHERE c.course_type = 'Value Added'
            AND ce.enrollment_date BETWEEN %s AND %s
        """, (self.period_start, self.period_end))[0][0] or 0

        total_students = frappe.db.count("Student", {"enabled": 1})
        percentage = (enrollments / total_students * 100) if total_students > 0 else 0

        return {
            "metric_number": "1.3.2",
            "description": "Students enrolled in value-added courses",
            "value": round(percentage, 2),
            "numerator": enrollments,
            "denominator": total_students,
            "unit": "%"
        }

    def _metric_1_4_1(self) -> Dict:
        """1.4.1 - Feedback on curriculum from stakeholders"""
        # Count feedback responses on curriculum
        feedback_count = frappe.db.count("Feedback Response", {
            "creation": ["between", [self.period_start, self.period_end]],
            "status": "Valid"
        })

        return {
            "metric_number": "1.4.1",
            "description": "Feedback responses on curriculum",
            "value": feedback_count,
            "unit": "count"
        }

    def _collect_criterion_2(self) -> Dict:
        """
        Criterion 2: Teaching-Learning and Evaluation (200 marks)
        """
        return {
            "2.1.1": self._metric_2_1_1(),
            "2.1.2": self._metric_2_1_2(),
            "2.2.1": self._metric_2_2_1(),
            "2.3.1": self._metric_2_3_1(),
            "2.4.1": self._metric_2_4_1(),
            "2.4.2": self._metric_2_4_2(),
            "2.5.1": self._metric_2_5_1(),
            "2.6.1": self._metric_2_6_1(),
            "2.6.2": self._metric_2_6_2()
        }

    def _metric_2_1_1(self) -> Dict:
        """2.1.1 - Enrollment percentage"""
        # Get sanctioned strength from programs
        sanctioned = frappe.db.sql("""
            SELECT COALESCE(SUM(max_strength), 0) FROM `tabProgram` WHERE is_published = 1
        """)[0][0] or 0

        # Get enrolled students in period
        enrolled = frappe.db.count("Program Enrollment", {
            "enrollment_date": ["between", [self.period_start, self.period_end]]
        })

        percentage = (enrolled / sanctioned * 100) if sanctioned > 0 else 0

        return {
            "metric_number": "2.1.1",
            "description": "Enrollment percentage",
            "value": round(percentage, 2),
            "numerator": enrolled,
            "denominator": sanctioned,
            "unit": "%"
        }

    def _metric_2_1_2(self) -> Dict:
        """2.1.2 - Students from reserved categories"""
        total_students = frappe.db.count("Student", {
            "enabled": 1,
            "joining_date": ["between", [self.period_start, self.period_end]]
        })

        reserved = frappe.db.count("Student", {
            "enabled": 1,
            "joining_date": ["between", [self.period_start, self.period_end]],
            "caste_category": ["in", ["SC", "ST", "OBC", "EWS"]]
        })

        percentage = (reserved / total_students * 100) if total_students > 0 else 0

        return {
            "metric_number": "2.1.2",
            "description": "Students from reserved categories",
            "value": round(percentage, 2),
            "numerator": reserved,
            "denominator": total_students,
            "unit": "%"
        }

    def _metric_2_2_1(self) -> Dict:
        """2.2.1 - Student-Full time Teacher Ratio"""
        students = frappe.db.count("Student", {"enabled": 1})

        faculty = frappe.db.count("Instructor", {
            "status": "Active",
            "employment_type": "Full Time"
        })

        ratio = round(students / faculty, 2) if faculty > 0 else 0

        return {
            "metric_number": "2.2.1",
            "description": "Student-Teacher Ratio",
            "value": ratio,
            "numerator": students,
            "denominator": faculty,
            "unit": "ratio"
        }

    def _metric_2_3_1(self) -> Dict:
        """2.3.1 - Student-centric teaching methods"""
        # Count courses using various teaching methods
        methods_count = frappe.db.count("Course", {
            "teaching_methodology": ["is", "set"]
        })

        return {
            "metric_number": "2.3.1",
            "description": "Courses with student-centric methods",
            "value": methods_count,
            "unit": "count"
        }

    def _metric_2_4_1(self) -> Dict:
        """2.4.1 - Faculty with PhD/NET/SET"""
        total_faculty = frappe.db.count("Instructor", {"status": "Active"})

        qualified = frappe.db.count("Instructor", {
            "status": "Active",
            "highest_qualification": ["in", ["Ph.D.", "PhD", "NET", "SET", "M.Phil."]]
        })

        percentage = (qualified / total_faculty * 100) if total_faculty > 0 else 0

        return {
            "metric_number": "2.4.1",
            "description": "Faculty with PhD/NET/SET",
            "value": round(percentage, 2),
            "numerator": qualified,
            "denominator": total_faculty,
            "unit": "%"
        }

    def _metric_2_4_2(self) -> Dict:
        """2.4.2 - Faculty awards and recognitions"""
        # This would need a Faculty Award DocType
        awards = 0
        if frappe.db.exists("DocType", "Faculty Award"):
            awards = frappe.db.count("Faculty Award", {
                "award_date": ["between", [self.period_start, self.period_end]]
            })

        return {
            "metric_number": "2.4.2",
            "description": "Faculty awards and recognitions",
            "value": awards,
            "unit": "count"
        }

    def _metric_2_5_1(self) -> Dict:
        """2.5.1 - Examination reforms"""
        # Check for continuous assessment implementation
        courses_with_cie = frappe.db.count("Course", {
            "evaluation_method": ["like", "%Continuous%"]
        })

        return {
            "metric_number": "2.5.1",
            "description": "Courses with continuous assessment",
            "value": courses_with_cie,
            "unit": "count"
        }

    def _metric_2_6_1(self) -> Dict:
        """2.6.1 - Program Outcomes and Course Outcomes attainment"""
        # Get PO attainment from university_obe
        pos = frappe.get_all("Program Outcome",
            filters={"status": "Active"},
            fields=["current_attainment", "target_attainment"]
        )

        if not pos:
            return {
                "metric_number": "2.6.1",
                "description": "PO-CO attainment",
                "value": 0,
                "unit": "%"
            }

        total_pos = len(pos)
        attained = sum(1 for po in pos if flt(po.current_attainment) >= flt(po.target_attainment or 60))
        percentage = (attained / total_pos * 100) if total_pos > 0 else 0

        return {
            "metric_number": "2.6.1",
            "description": "PO-CO attainment percentage",
            "value": round(percentage, 2),
            "numerator": attained,
            "denominator": total_pos,
            "unit": "%"
        }

    def _metric_2_6_2(self) -> Dict:
        """2.6.2 - Pass percentage of students"""
        total = frappe.db.count("Assessment Result", {
            "academic_year": ["in", self._get_assessment_years()],
            "docstatus": 1
        })

        passed = frappe.db.count("Assessment Result", {
            "academic_year": ["in", self._get_assessment_years()],
            "docstatus": 1,
            "grade": ["not in", ["F", "Fail", "AB", "Absent"]]
        })

        percentage = (passed / total * 100) if total > 0 else 0

        return {
            "metric_number": "2.6.2",
            "description": "Pass percentage",
            "value": round(percentage, 2),
            "numerator": passed,
            "denominator": total,
            "unit": "%"
        }

    def _collect_criterion_3(self) -> Dict:
        """Criterion 3: Research, Innovations and Extension"""
        return {
            "3.1.1": self._metric_3_1_1(),
            "3.2.1": self._metric_3_2_1(),
            "3.3.1": self._metric_3_3_1(),
            "3.4.1": self._metric_3_4_1(),
            "3.5.1": self._metric_3_5_1()
        }

    def _metric_3_1_1(self) -> Dict:
        """3.1.1 - Research grants received"""
        grants = 0
        if frappe.db.exists("DocType", "Research Grant"):
            grants = frappe.db.sql("""
                SELECT COALESCE(SUM(amount), 0) FROM `tabResearch Grant`
                WHERE grant_date BETWEEN %s AND %s
                AND docstatus = 1
            """, (self.period_start, self.period_end))[0][0] or 0

        return {
            "metric_number": "3.1.1",
            "description": "Research grants received",
            "value": round(grants / 100000, 2),
            "unit": "Lakhs"
        }

    def _metric_3_2_1(self) -> Dict:
        """3.2.1 - Innovation ecosystem"""
        innovations = 0
        if frappe.db.exists("DocType", "Innovation"):
            innovations = frappe.db.count("Innovation", {
                "creation": ["between", [self.period_start, self.period_end]]
            })

        return {
            "metric_number": "3.2.1",
            "description": "Innovations/startups incubated",
            "value": innovations,
            "unit": "count"
        }

    def _metric_3_3_1(self) -> Dict:
        """3.3.1 - Research publications"""
        publications = 0
        if frappe.db.exists("DocType", "Research Publication"):
            publications = frappe.db.count("Research Publication", {
                "publication_date": ["between", [self.period_start, self.period_end]],
                "docstatus": 1
            })

        faculty = frappe.db.count("Instructor", {"status": "Active"})
        per_faculty = round(publications / faculty, 2) if faculty > 0 else 0

        return {
            "metric_number": "3.3.1",
            "description": "Research publications",
            "value": publications,
            "per_faculty": per_faculty,
            "unit": "count"
        }

    def _metric_3_4_1(self) -> Dict:
        """3.4.1 - Extension activities"""
        activities = 0
        if frappe.db.exists("DocType", "Extension Activity"):
            activities = frappe.db.count("Extension Activity", {
                "activity_date": ["between", [self.period_start, self.period_end]]
            })

        return {
            "metric_number": "3.4.1",
            "description": "Extension activities conducted",
            "value": activities,
            "unit": "count"
        }

    def _metric_3_5_1(self) -> Dict:
        """3.5.1 - MoUs and collaborations"""
        mous = 0
        if frappe.db.exists("DocType", "MoU"):
            mous = frappe.db.count("MoU", {
                "signing_date": ["between", [self.period_start, self.period_end]],
                "status": "Active"
            })

        return {
            "metric_number": "3.5.1",
            "description": "Active MoUs and collaborations",
            "value": mous,
            "unit": "count"
        }

    def _collect_criterion_4(self) -> Dict:
        """Criterion 4: Infrastructure and Learning Resources"""
        return {
            "4.1.1": {"metric_number": "4.1.1", "description": "Infrastructure augmentation", "value": 0},
            "4.2.1": {"metric_number": "4.2.1", "description": "Library automation", "value": 0},
            "4.3.1": {"metric_number": "4.3.1", "description": "IT facilities", "value": 0},
            "4.4.1": {"metric_number": "4.4.1", "description": "Infrastructure maintenance", "value": 0}
        }

    def _collect_criterion_5(self) -> Dict:
        """Criterion 5: Student Support and Progression"""
        return {
            "5.1.1": self._metric_5_1_1(),
            "5.1.2": {"metric_number": "5.1.2", "description": "Capacity building", "value": 0},
            "5.2.1": self._metric_5_2_1(),
            "5.2.2": self._metric_5_2_2(),
            "5.3.1": {"metric_number": "5.3.1", "description": "Student awards", "value": 0},
            "5.4.1": {"metric_number": "5.4.1", "description": "Alumni engagement", "value": 0}
        }

    def _metric_5_1_1(self) -> Dict:
        """5.1.1 - Scholarships and freeships"""
        beneficiaries = 0
        if frappe.db.exists("DocType", "Scholarship Award"):
            beneficiaries = frappe.db.count("Scholarship Award", {
                "award_date": ["between", [self.period_start, self.period_end]],
                "docstatus": 1
            })

        total_students = frappe.db.count("Student", {"enabled": 1})
        percentage = (beneficiaries / total_students * 100) if total_students > 0 else 0

        return {
            "metric_number": "5.1.1",
            "description": "Scholarship beneficiaries",
            "value": round(percentage, 2),
            "numerator": beneficiaries,
            "denominator": total_students,
            "unit": "%"
        }

    def _metric_5_2_1(self) -> Dict:
        """5.2.1 - Placement of outgoing students"""
        eligible = frappe.db.count("Student", {
            "enabled": 1
        })

        placed = 0
        if frappe.db.exists("DocType", "Placement Offer"):
            placed = frappe.db.count("Placement Offer", {
                "offer_date": ["between", [self.period_start, self.period_end]],
                "status": "Accepted"
            })

        percentage = (placed / eligible * 100) if eligible > 0 else 0

        return {
            "metric_number": "5.2.1",
            "description": "Placement percentage",
            "value": round(percentage, 2),
            "numerator": placed,
            "denominator": eligible,
            "unit": "%"
        }

    def _metric_5_2_2(self) -> Dict:
        """5.2.2 - Students progressing to higher education"""
        higher_ed = 0
        # This would require tracking students who went for higher education

        return {
            "metric_number": "5.2.2",
            "description": "Students for higher education",
            "value": higher_ed,
            "unit": "count"
        }

    def _collect_criterion_6(self) -> Dict:
        """Criterion 6: Governance, Leadership and Management"""
        return {
            "6.1.1": {"metric_number": "6.1.1", "description": "Vision and Mission deployment", "value": 0},
            "6.2.1": {"metric_number": "6.2.1", "description": "Strategic plan", "value": 0},
            "6.3.1": {"metric_number": "6.3.1", "description": "Faculty empowerment", "value": 0},
            "6.4.1": {"metric_number": "6.4.1", "description": "Financial management", "value": 0},
            "6.5.1": {"metric_number": "6.5.1", "description": "IQAC initiatives", "value": 0}
        }

    def _collect_criterion_7(self) -> Dict:
        """Criterion 7: Institutional Values and Best Practices"""
        return {
            "7.1.1": self._metric_7_1_1(),
            "7.1.2": {"metric_number": "7.1.2", "description": "Environmental consciousness", "value": 0},
            "7.1.3": {"metric_number": "7.1.3", "description": "Disabled-friendly facilities", "value": 0},
            "7.2.1": {"metric_number": "7.2.1", "description": "Best practices", "value": 0},
            "7.3.1": {"metric_number": "7.3.1", "description": "Institutional distinctiveness", "value": 0}
        }

    def _metric_7_1_1(self) -> Dict:
        """7.1.1 - Gender equity measures"""
        total_students = frappe.db.count("Student", {"enabled": 1})
        female_students = frappe.db.count("Student", {"enabled": 1, "gender": "Female"})

        percentage = (female_students / total_students * 100) if total_students > 0 else 0

        return {
            "metric_number": "7.1.1",
            "description": "Female student percentage",
            "value": round(percentage, 2),
            "numerator": female_students,
            "denominator": total_students,
            "unit": "%"
        }

    def _get_assessment_years(self) -> List[str]:
        """Get academic years within the assessment period"""
        return frappe.get_all("Academic Year",
            filters={
                "year_start_date": [">=", self.period_start],
                "year_end_date": ["<=", self.period_end]
            },
            pluck="name"
        ) or []
