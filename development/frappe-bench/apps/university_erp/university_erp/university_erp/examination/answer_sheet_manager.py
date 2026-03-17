"""
Answer Sheet Manager

Manager class for handling physical answer sheet operations including
tracking, assignment, evaluation workflow, and QR code generation.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, random_string
from typing import Dict, List
import io
import base64


class AnswerSheetManager:
    """
    Manager for physical answer sheet tracking
    """

    @staticmethod
    def generate_barcode(answer_sheet_name: str) -> str:
        """
        Generate unique barcode for answer sheet

        Args:
            answer_sheet_name: Answer sheet document name

        Returns:
            Barcode string
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        exam_code = sheet.examination[:5] if sheet.examination else "EXAM"
        roll = sheet.roll_number or "000"
        random_part = random_string(4).upper()

        barcode = f"AS-{exam_code}-{roll}-{random_part}"

        frappe.db.set_value("Answer Sheet", answer_sheet_name, "barcode", barcode)

        return barcode

    @staticmethod
    def generate_qr_code(answer_sheet_name: str) -> str:
        """
        Generate QR code for answer sheet

        Args:
            answer_sheet_name: Answer sheet name

        Returns:
            Base64 encoded QR code image
        """
        try:
            import qrcode
        except ImportError:
            frappe.throw(_("qrcode library not installed. Run: pip install qrcode[pil]"))

        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        qr_data = {
            "id": sheet.name,
            "barcode": sheet.barcode,
            "exam": sheet.examination,
            "course": sheet.course,
            "roll": sheet.roll_number
        }

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(qr_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def bulk_create_answer_sheets(examination: str, course: str) -> int:
        """
        Create answer sheets for all registered students

        Args:
            examination: Examination ID
            course: Course ID

        Returns:
            Number of sheets created
        """
        # Get enrolled students for the examination
        # This would typically come from Examination Entry or similar
        students = frappe.get_all("Student",
            filters={"enabled": 1},
            fields=["name", "roll_number"]
        )

        count = 0
        for student in students:
            # Check if sheet already exists
            existing = frappe.db.exists("Answer Sheet", {
                "examination": examination,
                "course": course,
                "student": student.name
            })

            if not existing:
                sheet = frappe.new_doc("Answer Sheet")
                sheet.examination = examination
                sheet.course = course
                sheet.student = student.name
                sheet.roll_number = student.roll_number
                sheet.status = "Collected"
                sheet.collection_datetime = now_datetime()
                sheet.collected_by = frappe.session.user
                sheet.insert()

                # Generate barcode
                AnswerSheetManager.generate_barcode(sheet.name)
                count += 1

        frappe.db.commit()
        return count

    @staticmethod
    def update_tracking(answer_sheet_name: str, action: str,
                       location: str = None, user: str = None, remarks: str = None):
        """
        Update answer sheet tracking

        Args:
            answer_sheet_name: Answer sheet ID
            action: Tracking action
            location: Current location
            user: User performing action
            remarks: Additional remarks
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)
        sheet.add_tracking_entry(action, location, remarks)

    @staticmethod
    def assign_for_evaluation(answer_sheets: list, evaluator: str) -> int:
        """
        Assign multiple answer sheets to an evaluator

        Args:
            answer_sheets: List of answer sheet names
            evaluator: Faculty member to assign

        Returns:
            Number of sheets assigned
        """
        count = 0
        for sheet_name in answer_sheets:
            sheet = frappe.get_doc("Answer Sheet", sheet_name)

            if sheet.status in ["Received at Evaluation Center", "Collected"]:
                sheet.assign_evaluator(evaluator)
                count += 1

        return count

    @staticmethod
    def record_evaluation(answer_sheet_name: str, question_scores: list,
                         evaluator: str = None, remarks: str = None):
        """
        Record evaluation scores for answer sheet

        Args:
            answer_sheet_name: Answer sheet ID
            question_scores: List of {question_number, marks_obtained, max_marks, comments}
            evaluator: Evaluator ID
            remarks: Overall remarks
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)
        sheet.record_scores(question_scores)

        if remarks:
            sheet.add_tracking_entry("Evaluation Notes", remarks=remarks)

    @staticmethod
    def request_revaluation(answer_sheet_name: str, student: str, reason: str) -> str:
        """
        Request revaluation for an answer sheet

        Args:
            answer_sheet_name: Answer sheet ID
            student: Student requesting
            reason: Reason for revaluation

        Returns:
            Revaluation Request name
        """
        sheet = frappe.get_doc("Answer Sheet", answer_sheet_name)

        # Validate student owns this sheet
        if sheet.student != student:
            frappe.throw(_("You can only request revaluation for your own answer sheet"))

        # Check if revaluation already requested
        if sheet.status == "Revaluation Requested":
            frappe.throw(_("Revaluation already requested"))

        # Create revaluation request
        request = frappe.new_doc("Revaluation Request")
        request.answer_sheet = answer_sheet_name
        request.student = student
        request.reason = reason
        request.original_marks = sheet.marks_after_moderation or sheet.marks_obtained
        request.status = "Draft"
        request.insert()

        return request.name


class EvaluationWorkflow:
    """
    Workflow management for answer sheet evaluation
    """

    @staticmethod
    def get_evaluator_workload(evaluator: str) -> Dict:
        """
        Get current workload for an evaluator

        Args:
            evaluator: Faculty member ID

        Returns:
            Workload statistics
        """
        assigned = frappe.db.count("Answer Sheet", {
            "assigned_to": evaluator,
            "status": ["in", ["Assigned for Evaluation", "Evaluation In Progress"]]
        })

        completed_today = frappe.db.count("Answer Sheet", {
            "assigned_to": evaluator,
            "evaluation_completed": [">=", frappe.utils.today()],
            "status": ["in", ["Evaluated", "Moderated"]]
        })

        total_completed = frappe.db.count("Answer Sheet", {
            "assigned_to": evaluator,
            "status": ["in", ["Evaluated", "Moderated", "Result Published"]]
        })

        return {
            "pending": assigned,
            "completed_today": completed_today,
            "total_completed": total_completed
        }

    @staticmethod
    def auto_assign_sheets(examination: str, course: str) -> Dict:
        """
        Auto-assign answer sheets to available evaluators

        Args:
            examination: Examination ID
            course: Course ID

        Returns:
            Assignment summary
        """
        # Get unassigned sheets
        unassigned = frappe.get_all("Answer Sheet",
            filters={
                "examination": examination,
                "course": course,
                "status": "Received at Evaluation Center",
                "assigned_to": ["is", "not set"]
            },
            pluck="name"
        )

        if not unassigned:
            return {"message": "No unassigned sheets", "assigned": 0}

        # Get available evaluators for this course
        # This would typically check Course Instructor or Faculty assignments
        evaluators = frappe.get_all("Instructor",
            filters={"status": "Active"},
            pluck="name",
            limit=10
        )

        if not evaluators:
            return {"message": "No evaluators available", "assigned": 0}

        # Get workload for each evaluator
        evaluator_loads = {}
        for e in evaluators:
            workload = EvaluationWorkflow.get_evaluator_workload(e)
            evaluator_loads[e] = workload["pending"]

        # Distribute sheets evenly
        assignments = {e: [] for e in evaluator_loads}

        for sheet in unassigned:
            # Assign to evaluator with least pending
            min_evaluator = min(evaluator_loads, key=evaluator_loads.get)
            assignments[min_evaluator].append(sheet)
            evaluator_loads[min_evaluator] += 1

        # Perform assignments
        total_assigned = 0
        for evaluator, sheets in assignments.items():
            if sheets:
                count = AnswerSheetManager.assign_for_evaluation(sheets, evaluator)
                total_assigned += count

        return {
            "message": f"Assigned {total_assigned} sheets",
            "assigned": total_assigned,
            "distribution": {e: len(s) for e, s in assignments.items() if s}
        }

    @staticmethod
    def get_evaluation_progress(examination: str, course: str = None) -> Dict:
        """
        Get overall evaluation progress for an examination

        Args:
            examination: Examination ID
            course: Optional course filter

        Returns:
            Progress statistics
        """
        filters = {"examination": examination}
        if course:
            filters["course"] = course

        total = frappe.db.count("Answer Sheet", filters)

        evaluated = frappe.db.count("Answer Sheet", {
            **filters,
            "status": ["in", ["Evaluated", "Moderated", "Result Published"]]
        })

        in_progress = frappe.db.count("Answer Sheet", {
            **filters,
            "status": ["in", ["Assigned for Evaluation", "Evaluation In Progress"]]
        })

        pending = frappe.db.count("Answer Sheet", {
            **filters,
            "status": ["in", ["Collected", "In Transit", "Received at Evaluation Center"]]
        })

        return {
            "total": total,
            "evaluated": evaluated,
            "in_progress": in_progress,
            "pending": pending,
            "progress_percentage": (evaluated / total * 100) if total > 0 else 0
        }


# API functions

@frappe.whitelist()
def get_sheet_by_barcode(barcode: str):
    """
    Get answer sheet by barcode

    Args:
        barcode: Barcode string

    Returns:
        Answer sheet details
    """
    sheet_name = frappe.db.get_value("Answer Sheet", {"barcode": barcode})
    if not sheet_name:
        frappe.throw(_("Answer sheet not found with barcode: {0}").format(barcode))

    return frappe.get_doc("Answer Sheet", sheet_name).as_dict()


@frappe.whitelist()
def update_sheet_location(barcode: str, action: str, location: str, remarks: str = None):
    """
    Update answer sheet location via barcode scan

    Args:
        barcode: Barcode string
        action: Action performed
        location: New location
        remarks: Optional remarks
    """
    sheet_name = frappe.db.get_value("Answer Sheet", {"barcode": barcode})
    if not sheet_name:
        frappe.throw(_("Answer sheet not found with barcode: {0}").format(barcode))

    AnswerSheetManager.update_tracking(sheet_name, action, location, remarks=remarks)

    return {"status": "success", "message": _("Location updated")}
