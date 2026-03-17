"""
Internal Assessment DocType Controller

Manages internal assessments including assignments, quizzes,
projects, and other continuous evaluation components.
"""

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now_datetime, getdate, flt
from typing import List, Dict


class InternalAssessment(Document):
    """
    Internal Assessment for continuous evaluation
    """

    def validate(self):
        self.validate_marks()
        self.validate_criteria_marks()
        self.validate_dates()
        self.calculate_summary()

    def on_submit(self):
        self.update_answer_sheet_status()

    def validate_marks(self):
        """Validate marks configuration"""
        if self.passing_marks and self.passing_marks > self.maximum_marks:
            frappe.throw(_("Passing marks cannot exceed maximum marks"))

    def validate_criteria_marks(self):
        """Validate that criteria marks sum equals maximum marks"""
        if self.criteria:
            total_criteria_marks = sum(c.max_marks or 0 for c in self.criteria)
            if total_criteria_marks != self.maximum_marks:
                frappe.msgprint(
                    _("Total criteria marks ({0}) should equal maximum marks ({1})").format(
                        total_criteria_marks, self.maximum_marks
                    )
                )

    def validate_dates(self):
        """Validate assessment dates"""
        if self.submission_deadline:
            deadline_date = getdate(self.submission_deadline)
            if deadline_date < getdate(self.assessment_date):
                frappe.throw(_("Submission deadline cannot be before assessment date"))

    def calculate_summary(self):
        """Calculate summary statistics from scores"""
        if not self.scores:
            return

        self.total_students = len(self.scores)
        self.evaluated_count = sum(1 for s in self.scores if s.total_marks is not None)

        marks_list = [s.total_marks for s in self.scores if s.total_marks is not None]

        if marks_list:
            self.average_marks = sum(marks_list) / len(marks_list)
            self.highest_marks = max(marks_list)
            self.lowest_marks = min(marks_list)

            if self.passing_marks:
                self.passed_count = sum(1 for m in marks_list if m >= self.passing_marks)

    def update_answer_sheet_status(self):
        """Update status to completed on submit"""
        self.status = "Completed"
        self.db_set("status", "Completed")

    @frappe.whitelist()
    def fetch_students(self):
        """
        Fetch students from student group or course enrollment
        """
        students = []

        if self.student_group:
            students = frappe.get_all(
                "Student Group Student",
                filters={"parent": self.student_group},
                fields=["student", "student_name", "roll_number"]
            )
        elif self.course and self.academic_year:
            enrollments = frappe.get_all(
                "Course Enrollment",
                filters={
                    "course": self.course,
                    "academic_year": self.academic_year,
                    "enrollment_status": "Enrolled"
                },
                fields=["student"]
            )
            for e in enrollments:
                student = frappe.get_doc("Student", e.student)
                students.append({
                    "student": student.name,
                    "student_name": student.student_name,
                    "roll_number": student.roll_number
                })

        # Add to scores table
        existing = {s.student for s in self.scores}
        for student in students:
            if student["student"] not in existing:
                self.append("scores", {
                    "student": student["student"],
                    "student_name": student.get("student_name"),
                    "roll_number": student.get("roll_number")
                })

        return len(students)

    @frappe.whitelist()
    def record_score(self, student: str, marks: float, criteria_scores: dict = None,
                    remarks: str = None):
        """
        Record score for a student

        Args:
            student: Student name
            marks: Total marks obtained
            criteria_scores: Dict of criteria-wise scores
            remarks: Evaluation remarks
        """
        # Find student in scores
        score_row = None
        for s in self.scores:
            if s.student == student:
                score_row = s
                break

        if not score_row:
            score_row = self.append("scores", {"student": student})

        score_row.total_marks = marks
        score_row.percentage = (marks / self.maximum_marks * 100) if self.maximum_marks else 0

        if criteria_scores:
            import json
            score_row.criteria_scores = json.dumps(criteria_scores)

        if remarks:
            score_row.remarks = remarks

        score_row.evaluated_by = frappe.db.get_value(
            "Instructor", {"user": frappe.session.user}
        )
        score_row.evaluation_date = getdate(now_datetime())

        # Apply grade from grading scale
        if self.grading_scale:
            grade = self._get_grade(score_row.percentage)
            score_row.grade = grade

        self.save()
        self.calculate_summary()

        return {"status": "success", "percentage": score_row.percentage, "grade": score_row.grade}

    def _get_grade(self, percentage: float) -> str:
        """Get grade from grading scale"""
        if not self.grading_scale:
            return None

        intervals = frappe.get_all(
            "Grading Scale Interval",
            filters={"parent": self.grading_scale},
            fields=["grade_code", "threshold"],
            order_by="threshold desc"
        )

        for interval in intervals:
            if percentage >= interval.threshold:
                return interval.grade_code

        return intervals[-1].grade_code if intervals else None

    @frappe.whitelist()
    def bulk_upload_scores(self, scores_data: list):
        """
        Bulk upload scores from list

        Args:
            scores_data: List of {student, marks, remarks}
        """
        import json
        if isinstance(scores_data, str):
            scores_data = json.loads(scores_data)

        updated = 0
        for data in scores_data:
            self.record_score(
                student=data.get("student"),
                marks=flt(data.get("marks")),
                remarks=data.get("remarks")
            )
            updated += 1

        return {"updated": updated}

    @frappe.whitelist()
    def calculate_co_attainment(self) -> Dict:
        """
        Calculate Course Outcome attainment for this assessment

        Returns:
            CO-wise attainment statistics
        """
        if not self.co_mapping:
            return {}

        attainment = {}
        for co in self.co_mapping:
            co_marks = co.max_marks_for_co or 0
            if co_marks == 0:
                continue

            # Calculate average score for this CO
            total_score = 0
            count = 0
            for score in self.scores:
                if score.criteria_scores:
                    import json
                    criteria = json.loads(score.criteria_scores)
                    # Sum up marks for criteria mapped to this CO
                    for c in self.criteria:
                        if c.co_mapping == co.course_outcome and c.criteria_name in criteria:
                            total_score += criteria[c.criteria_name]
                            count += 1

            if count > 0:
                attainment[co.course_outcome] = {
                    "average_score": total_score / count,
                    "max_marks": co_marks,
                    "attainment_percentage": (total_score / count / co_marks * 100)
                }

        return attainment


@frappe.whitelist()
def get_student_assessments(student: str, academic_year: str = None, course: str = None):
    """
    Get assessments for a student

    Args:
        student: Student name
        academic_year: Optional filter
        course: Optional filter

    Returns:
        List of assessments with scores
    """
    filters = {}
    if academic_year:
        filters["academic_year"] = academic_year
    if course:
        filters["course"] = course

    assessments = frappe.get_all(
        "Internal Assessment",
        filters=filters,
        fields=["name", "assessment_name", "assessment_type", "course",
                "maximum_marks", "assessment_date", "status"]
    )

    result = []
    for assessment in assessments:
        score = frappe.db.get_value(
            "Internal Assessment Score",
            {"parent": assessment.name, "student": student},
            ["total_marks", "percentage", "grade"],
            as_dict=True
        )
        if score:
            assessment.update(score)
            result.append(assessment)

    return result
