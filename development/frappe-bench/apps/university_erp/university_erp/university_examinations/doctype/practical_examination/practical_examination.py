"""
Practical Examination DocType Controller

Manages practical examinations including scheduling, examiner assignment,
slot management, and student evaluation.
"""

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, now_datetime, flt
from datetime import datetime, timedelta
from typing import Dict, List
import json


class PracticalExamination(Document):
    """
    Practical Examination management
    """

    def validate(self):
        self.validate_dates()
        self.validate_marks()
        self.validate_examiners()
        self.calculate_summary()

    def on_submit(self):
        self.status = "Scheduled"
        self.update_external_examiner_stats()

    def validate_dates(self):
        """Validate exam dates"""
        if self.start_date and self.end_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw(_("End date cannot be before start date"))

    def validate_marks(self):
        """Validate marks configuration"""
        if self.passing_marks and self.passing_marks > self.maximum_marks:
            frappe.throw(_("Passing marks cannot exceed maximum marks"))

        # Validate component marks sum
        component_sum = flt(self.experiment_marks) + flt(self.viva_marks) + flt(self.record_marks)
        if component_sum > 0 and component_sum != self.maximum_marks:
            frappe.msgprint(
                _("Sum of component marks ({0}) should equal maximum marks ({1})").format(
                    component_sum, self.maximum_marks
                )
            )

        # Validate criteria marks
        if self.evaluation_criteria:
            criteria_sum = sum(c.max_marks or 0 for c in self.evaluation_criteria)
            if criteria_sum != self.maximum_marks:
                frappe.msgprint(
                    _("Sum of criteria marks ({0}) should equal maximum marks ({1})").format(
                        criteria_sum, self.maximum_marks
                    )
                )

    def validate_examiners(self):
        """Validate examiner assignments"""
        has_internal = False
        has_external = False

        for examiner in self.examiners:
            if examiner.examiner_type == "Internal":
                has_internal = True
            elif examiner.examiner_type == "External":
                has_external = True

        if not has_internal:
            frappe.msgprint(_("At least one internal examiner is recommended"))

    def calculate_summary(self):
        """Calculate summary statistics"""
        if not self.student_scores:
            return

        self.total_students = len(self.student_scores)
        self.evaluated_count = sum(
            1 for s in self.student_scores
            if s.total_marks is not None and s.attendance_status == "Present"
        )

        marks_list = [
            s.total_marks for s in self.student_scores
            if s.total_marks is not None and s.attendance_status == "Present"
        ]

        if marks_list:
            self.average_marks = sum(marks_list) / len(marks_list)
            self.highest_marks = max(marks_list)
            self.lowest_marks = min(marks_list)

            if self.passing_marks:
                self.passed_count = sum(1 for m in marks_list if m >= self.passing_marks)

    def update_external_examiner_stats(self):
        """Update external examiner assignment statistics"""
        for examiner in self.examiners:
            if examiner.examiner_type == "External" and examiner.external_examiner:
                ext = frappe.get_doc("External Examiner", examiner.external_examiner)
                ext.update_assignment_stats()

    @frappe.whitelist()
    def fetch_students(self):
        """
        Fetch students from course enrollment or program
        """
        students = []

        if self.course and self.academic_year:
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
        existing = {s.student for s in self.student_scores}
        for student in students:
            if student["student"] not in existing:
                self.append("student_scores", {
                    "student": student["student"],
                    "student_name": student.get("student_name"),
                    "roll_number": student.get("roll_number"),
                    "attendance_status": "Present"
                })

        return len(students)

    @frappe.whitelist()
    def generate_slots(self):
        """
        Generate exam slots based on configuration
        """
        if not self.start_date or not self.end_date:
            frappe.throw(_("Please set start and end dates first"))

        if not self.students_per_slot:
            frappe.throw(_("Please set students per slot"))

        # Clear existing slots
        self.slots = []

        current_date = getdate(self.start_date)
        end_date = getdate(self.end_date)
        slot_number = 1

        while current_date <= end_date:
            # Morning slots (9 AM - 1 PM)
            self.append("slots", {
                "slot_date": current_date,
                "start_time": "09:00:00",
                "end_time": "13:00:00",
                "batch": f"Batch {slot_number}",
                "room": self.venue,
                "max_students": self.students_per_slot,
                "status": "Scheduled"
            })
            slot_number += 1

            # Afternoon slots (2 PM - 6 PM)
            self.append("slots", {
                "slot_date": current_date,
                "start_time": "14:00:00",
                "end_time": "18:00:00",
                "batch": f"Batch {slot_number}",
                "room": self.venue,
                "max_students": self.students_per_slot,
                "status": "Scheduled"
            })
            slot_number += 1

            current_date = current_date + timedelta(days=1)

        return len(self.slots)

    @frappe.whitelist()
    def assign_students_to_slots(self):
        """
        Auto-assign students to available slots
        """
        if not self.slots:
            frappe.throw(_("Please generate slots first"))

        unassigned = [s for s in self.student_scores if not s.slot]

        slot_idx = 0
        for score in unassigned:
            while slot_idx < len(self.slots):
                slot = self.slots[slot_idx]
                current_count = slot.enrolled_students or 0

                if current_count < slot.max_students:
                    score.slot = slot.batch
                    slot.enrolled_students = current_count + 1
                    break
                slot_idx += 1

            if slot_idx >= len(self.slots):
                frappe.msgprint(_("Not enough slots for all students"))
                break

        return len([s for s in self.student_scores if s.slot])

    @frappe.whitelist()
    def record_score(self, student: str, experiment_marks: float = None,
                    viva_marks: float = None, record_marks: float = None,
                    criteria_scores: dict = None, remarks: str = None,
                    internal_examiner: str = None, external_examiner: str = None):
        """
        Record evaluation score for a student

        Args:
            student: Student name
            experiment_marks: Marks for experiment
            viva_marks: Marks for viva
            record_marks: Marks for record
            criteria_scores: Dict of criteria-wise scores
            remarks: Evaluation remarks
            internal_examiner: Internal examiner
            external_examiner: External examiner
        """
        # Find student in scores
        score_row = None
        for s in self.student_scores:
            if s.student == student:
                score_row = s
                break

        if not score_row:
            frappe.throw(_("Student not found in examination"))

        if score_row.attendance_status == "Absent":
            frappe.throw(_("Cannot record score for absent student"))

        # Update marks
        if experiment_marks is not None:
            score_row.experiment_marks = experiment_marks
        if viva_marks is not None:
            score_row.viva_marks = viva_marks
        if record_marks is not None:
            score_row.record_marks = record_marks

        # Calculate total
        score_row.total_marks = flt(score_row.experiment_marks) + \
                               flt(score_row.viva_marks) + \
                               flt(score_row.record_marks)

        score_row.percentage = (score_row.total_marks / self.maximum_marks * 100) \
                              if self.maximum_marks else 0

        if criteria_scores:
            score_row.criteria_scores = json.dumps(criteria_scores)

        if remarks:
            score_row.remarks = remarks

        score_row.internal_examiner = internal_examiner or frappe.db.get_value(
            "Instructor", {"user": frappe.session.user}
        )
        score_row.external_examiner = external_examiner
        score_row.evaluation_date = getdate(now_datetime())

        # Apply grade
        if self.grading_scale:
            score_row.grade = self._get_grade(score_row.percentage)

        self.save()
        self.calculate_summary()

        return {
            "status": "success",
            "total_marks": score_row.total_marks,
            "percentage": score_row.percentage,
            "grade": score_row.grade
        }

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
    def mark_attendance(self, student: str, status: str):
        """
        Mark student attendance

        Args:
            student: Student name
            status: Present/Absent/Medical Leave
        """
        for score in self.student_scores:
            if score.student == student:
                score.attendance_status = status
                if status == "Absent":
                    score.total_marks = 0
                    score.percentage = 0
                self.save()
                return {"status": "success"}

        frappe.throw(_("Student not found"))

    @frappe.whitelist()
    def publish_results(self):
        """Publish practical examination results"""
        self.result_published = 1
        self.status = "Completed"
        self.save()

        # Create notifications for students
        for score in self.student_scores:
            if score.student and score.total_marks is not None:
                frappe.publish_realtime(
                    "practical_result_published",
                    {"examination": self.name, "student": score.student},
                    user=frappe.db.get_value("Student", score.student, "user")
                )

        return {"status": "success", "message": _("Results published successfully")}


@frappe.whitelist()
def get_student_practical_result(student: str, examination: str = None):
    """
    Get practical examination results for a student

    Args:
        student: Student name
        examination: Optional specific examination

    Returns:
        List of practical results
    """
    filters = {"result_published": 1}
    if examination:
        filters["name"] = examination

    exams = frappe.get_all(
        "Practical Examination",
        filters=filters,
        fields=["name", "examination_name", "course", "maximum_marks",
                "start_date", "status"]
    )

    results = []
    for exam in exams:
        score = frappe.db.get_value(
            "Practical Exam Student Score",
            {"parent": exam.name, "student": student},
            ["total_marks", "percentage", "grade", "experiment_marks",
             "viva_marks", "record_marks", "attendance_status"],
            as_dict=True
        )
        if score:
            exam.update(score)
            results.append(exam)

    return results
