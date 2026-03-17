"""
Practical Exam Manager

Manager class for handling practical examination operations including
scheduling, examiner assignment, and result processing.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, flt, add_days
from typing import Dict, List
from datetime import timedelta
import json


class PracticalExamManager:
    """
    Manager for practical examination operations
    """

    @staticmethod
    def create_practical_exam(examination: str, course: str) -> str:
        """
        Create practical examination from parent examination

        Args:
            examination: Parent examination name
            course: Course name

        Returns:
            Created practical exam name
        """
        exam = frappe.get_doc("Examination", examination)
        course_doc = frappe.get_doc("Course", course)

        practical = frappe.new_doc("Practical Examination")
        practical.examination_name = f"{course_doc.course_code} - Practical Exam"
        practical.examination = examination
        practical.academic_year = exam.academic_year
        practical.academic_term = exam.academic_term
        practical.course = course
        practical.program = exam.program
        practical.status = "Draft"
        practical.insert()

        return practical.name

    @staticmethod
    def bulk_create_practicals(examination: str) -> List[str]:
        """
        Create practical exams for all courses with practicals in an examination

        Args:
            examination: Parent examination name

        Returns:
            List of created practical exam names
        """
        exam = frappe.get_doc("Examination", examination)

        # Get courses with practical component
        courses = frappe.get_all(
            "Course",
            filters={
                "program": exam.program,
                "has_practical": 1
            },
            pluck="name"
        )

        created = []
        for course in courses:
            # Check if practical already exists
            existing = frappe.db.exists("Practical Examination", {
                "examination": examination,
                "course": course
            })

            if not existing:
                name = PracticalExamManager.create_practical_exam(examination, course)
                created.append(name)

        return created

    @staticmethod
    def assign_examiners(practical_exam: str, internal_examiners: list,
                        external_examiners: list = None) -> Dict:
        """
        Assign examiners to a practical examination

        Args:
            practical_exam: Practical examination name
            internal_examiners: List of faculty member names
            external_examiners: List of external examiner names

        Returns:
            Assignment summary
        """
        exam = frappe.get_doc("Practical Examination", practical_exam)

        # Clear existing examiners
        exam.examiners = []

        # Add internal examiners
        for faculty in internal_examiners:
            exam.append("examiners", {
                "examiner_type": "Internal",
                "faculty_member": faculty,
                "role": "Examiner",
                "can_evaluate": 1
            })

        # Add external examiners
        if external_examiners:
            for ext in external_examiners:
                exam.append("examiners", {
                    "examiner_type": "External",
                    "external_examiner": ext,
                    "role": "External Examiner",
                    "can_evaluate": 1
                })

        exam.save()

        return {
            "internal_count": len(internal_examiners),
            "external_count": len(external_examiners) if external_examiners else 0
        }

    @staticmethod
    def auto_assign_external_examiners(practical_exam: str) -> Dict:
        """
        Auto-assign available external examiners based on specialization

        Args:
            practical_exam: Practical examination name

        Returns:
            Assignment result
        """
        exam = frappe.get_doc("Practical Examination", practical_exam)
        course = frappe.get_doc("Course", exam.course)

        # Get available external examiners
        available = frappe.get_all(
            "External Examiner",
            filters={
                "status": "Active",
                "empanelment_valid_till": [">=", getdate(now_datetime())]
            },
            fields=["name", "specialization", "times_assigned", "average_rating"],
            order_by="times_assigned asc, average_rating desc"
        )

        if not available:
            return {"status": "error", "message": _("No available external examiners")}

        # Select best match
        selected = available[0]

        exam.append("examiners", {
            "examiner_type": "External",
            "external_examiner": selected.name,
            "role": "External Examiner",
            "can_evaluate": 1
        })
        exam.save()

        return {
            "status": "success",
            "assigned": selected.name
        }

    @staticmethod
    def generate_schedule(practical_exam: str, start_date: str, end_date: str,
                         slots_per_day: int = 2, students_per_slot: int = 20) -> int:
        """
        Generate examination schedule with slots

        Args:
            practical_exam: Practical examination name
            start_date: Start date
            end_date: End date
            slots_per_day: Number of slots per day
            students_per_slot: Students per slot

        Returns:
            Number of slots created
        """
        exam = frappe.get_doc("Practical Examination", practical_exam)
        exam.start_date = start_date
        exam.end_date = end_date
        exam.students_per_slot = students_per_slot

        # Clear existing slots
        exam.slots = []

        current_date = getdate(start_date)
        end = getdate(end_date)

        slot_times = [
            ("09:00:00", "12:00:00"),  # Morning
            ("14:00:00", "17:00:00"),  # Afternoon
        ]

        batch_num = 1
        while current_date <= end:
            for i in range(min(slots_per_day, len(slot_times))):
                exam.append("slots", {
                    "slot_date": current_date,
                    "start_time": slot_times[i][0],
                    "end_time": slot_times[i][1],
                    "batch": f"Batch {batch_num}",
                    "room": exam.venue,
                    "max_students": students_per_slot,
                    "status": "Scheduled"
                })
                batch_num += 1

            current_date = current_date + timedelta(days=1)

        exam.save()
        return len(exam.slots)

    @staticmethod
    def distribute_students(practical_exam: str, method: str = "sequential") -> Dict:
        """
        Distribute students across slots

        Args:
            practical_exam: Practical examination name
            method: Distribution method (sequential, random, roll_wise)

        Returns:
            Distribution summary
        """
        exam = frappe.get_doc("Practical Examination", practical_exam)

        if not exam.student_scores:
            exam.fetch_students()
            exam.reload()

        if not exam.slots:
            return {"status": "error", "message": _("No slots available")}

        students = list(exam.student_scores)

        if method == "random":
            import random
            random.shuffle(students)
        elif method == "roll_wise":
            students.sort(key=lambda x: x.roll_number or "")

        slot_idx = 0
        distributed = 0

        for student in students:
            while slot_idx < len(exam.slots):
                slot = exam.slots[slot_idx]
                current = slot.enrolled_students or 0

                if current < slot.max_students:
                    student.slot = slot.batch
                    slot.enrolled_students = current + 1
                    distributed += 1
                    break

                slot_idx += 1

            if slot_idx >= len(exam.slots):
                break

        exam.save()

        return {
            "status": "success",
            "distributed": distributed,
            "total_students": len(students),
            "slots_used": slot_idx + 1
        }

    @staticmethod
    def record_bulk_scores(practical_exam: str, scores: list) -> Dict:
        """
        Record scores for multiple students

        Args:
            practical_exam: Practical examination name
            scores: List of {student, experiment_marks, viva_marks, record_marks, remarks}

        Returns:
            Recording result
        """
        exam = frappe.get_doc("Practical Examination", practical_exam)
        recorded = 0
        errors = []

        for score_data in scores:
            try:
                exam.record_score(
                    student=score_data.get("student"),
                    experiment_marks=flt(score_data.get("experiment_marks")),
                    viva_marks=flt(score_data.get("viva_marks")),
                    record_marks=flt(score_data.get("record_marks")),
                    remarks=score_data.get("remarks")
                )
                recorded += 1
            except Exception as e:
                errors.append({
                    "student": score_data.get("student"),
                    "error": str(e)
                })

        return {
            "recorded": recorded,
            "errors": errors
        }

    @staticmethod
    def get_examiner_schedule(examiner: str, examiner_type: str = "Internal") -> List[Dict]:
        """
        Get examination schedule for an examiner

        Args:
            examiner: Examiner name (faculty or external)
            examiner_type: Internal or External

        Returns:
            List of scheduled examinations
        """
        field = "faculty_member" if examiner_type == "Internal" else "external_examiner"

        # Get examinations where this examiner is assigned
        exams = frappe.db.sql("""
            SELECT pe.name, pe.examination_name, pe.course, pe.start_date, pe.end_date,
                   pe.venue, pe.status
            FROM `tabPractical Examination` pe
            INNER JOIN `tabPractical Exam Examiner` pee ON pee.parent = pe.name
            WHERE pee.{0} = %s AND pe.status IN ('Scheduled', 'In Progress')
            ORDER BY pe.start_date
        """.format(field), (examiner,), as_dict=True)

        for exam in exams:
            # Get slots
            slots = frappe.get_all(
                "Practical Exam Slot",
                filters={"parent": exam.name},
                fields=["slot_date", "start_time", "end_time", "batch", "room",
                       "enrolled_students", "status"],
                order_by="slot_date, start_time"
            )
            exam["slots"] = slots

        return exams

    @staticmethod
    def generate_result_summary(practical_exam: str) -> Dict:
        """
        Generate comprehensive result summary

        Args:
            practical_exam: Practical examination name

        Returns:
            Result summary with statistics
        """
        exam = frappe.get_doc("Practical Examination", practical_exam)

        summary = {
            "examination": exam.name,
            "examination_name": exam.examination_name,
            "course": exam.course,
            "total_students": exam.total_students,
            "evaluated": exam.evaluated_count,
            "passed": exam.passed_count,
            "average_marks": exam.average_marks,
            "highest_marks": exam.highest_marks,
            "lowest_marks": exam.lowest_marks,
            "pass_percentage": (exam.passed_count / exam.evaluated_count * 100
                               if exam.evaluated_count > 0 else 0),
            "grade_distribution": {},
            "component_averages": {
                "experiment": 0,
                "viva": 0,
                "record": 0
            }
        }

        # Calculate grade distribution
        exp_total = viva_total = record_total = count = 0

        for score in exam.student_scores:
            if score.attendance_status == "Present" and score.total_marks is not None:
                grade = score.grade or "Ungraded"
                summary["grade_distribution"][grade] = \
                    summary["grade_distribution"].get(grade, 0) + 1

                exp_total += flt(score.experiment_marks)
                viva_total += flt(score.viva_marks)
                record_total += flt(score.record_marks)
                count += 1

        if count > 0:
            summary["component_averages"]["experiment"] = exp_total / count
            summary["component_averages"]["viva"] = viva_total / count
            summary["component_averages"]["record"] = record_total / count

        return summary


# API Functions

@frappe.whitelist()
def get_practical_exams(examination: str = None, course: str = None,
                       academic_year: str = None):
    """
    Get practical examinations with filters

    Args:
        examination: Parent examination filter
        course: Course filter
        academic_year: Academic year filter

    Returns:
        List of practical examinations
    """
    filters = {}
    if examination:
        filters["examination"] = examination
    if course:
        filters["course"] = course
    if academic_year:
        filters["academic_year"] = academic_year

    return frappe.get_all(
        "Practical Examination",
        filters=filters,
        fields=["name", "examination_name", "course", "start_date", "end_date",
                "status", "total_students", "evaluated_count", "result_published"]
    )


@frappe.whitelist()
def assign_exam_examiners(practical_exam: str, internal_examiners: str,
                         external_examiners: str = None):
    """
    API to assign examiners

    Args:
        practical_exam: Practical examination name
        internal_examiners: JSON list of faculty members
        external_examiners: JSON list of external examiners

    Returns:
        Assignment result
    """
    internal = json.loads(internal_examiners) if internal_examiners else []
    external = json.loads(external_examiners) if external_examiners else []

    return PracticalExamManager.assign_examiners(practical_exam, internal, external)


@frappe.whitelist()
def generate_exam_schedule(practical_exam: str, start_date: str, end_date: str,
                          slots_per_day: int = 2, students_per_slot: int = 20):
    """
    API to generate examination schedule

    Args:
        practical_exam: Practical examination name
        start_date: Start date
        end_date: End date
        slots_per_day: Slots per day
        students_per_slot: Students per slot

    Returns:
        Number of slots created
    """
    return PracticalExamManager.generate_schedule(
        practical_exam, start_date, end_date,
        int(slots_per_day), int(students_per_slot)
    )


@frappe.whitelist()
def get_result_summary(practical_exam: str):
    """
    API to get result summary

    Args:
        practical_exam: Practical examination name

    Returns:
        Result summary
    """
    return PracticalExamManager.generate_result_summary(practical_exam)
