# Copyright (c) 2025, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class BulkFeeGenerator(Document):

    def validate(self):
        self.load_eligible_students()

    def load_eligible_students(self):
        """Populate the students child table from Program Enrollment"""
        if not self.program or not self.academic_year:
            return

        filters = {
            "program": self.program,
            "academic_year": self.academic_year,
            "docstatus": 1,
        }
        if self.semester:
            filters["academic_term"] = self.semester
        if self.student_batch:
            filters["student_batch_name"] = self.student_batch

        enrollments = frappe.get_all(
            "Program Enrollment",
            filters=filters,
            fields=["student", "student_name", "student_batch_name"],
        )

        # Check which students already have a fee from this structure
        existing = set(
            frappe.db.sql_list(
                """SELECT DISTINCT student FROM `tabFees`
                WHERE fee_structure = %s AND academic_year = %s AND docstatus != 2""",
                (self.fee_structure, self.academic_year),
            )
        )

        self.students = []
        fees_to_generate = 0
        for e in enrollments:
            has_existing = e.student in existing
            self.append("students", {
                "student": e.student,
                "student_name": e.student_name,
                "batch": e.student_batch_name,
                "has_existing_fee": 1 if has_existing else 0,
                "generate": 0 if has_existing else 1,
            })
            if not has_existing:
                fees_to_generate += 1

        self.total_students = len(self.students)
        self.fees_to_generate = fees_to_generate


@frappe.whitelist()
def generate_fees(bulk_fee_generator):
    """Generate Education Fees records for all marked students via Fee Schedule"""
    doc = frappe.get_doc("Bulk Fee Generator", bulk_fee_generator)

    if not doc.fee_structure:
        frappe.throw(_("Fee Structure is required"))

    students_to_process = [s for s in doc.students if s.generate and not s.has_existing_fee]
    if not students_to_process:
        frappe.throw(_("No students selected for fee generation"))

    fee_structure = frappe.get_doc("Fee Structure", doc.fee_structure)
    company = fee_structure.company or frappe.defaults.get_global_default("company")

    created = []
    errors = []

    for student_row in students_to_process:
        try:
            # Get active program enrollment for this student
            enrollment = frappe.db.get_value(
                "Program Enrollment",
                {
                    "student": student_row.student,
                    "program": doc.program,
                    "academic_year": doc.academic_year,
                    "docstatus": 1,
                },
                "name",
            )

            fees_doc = frappe.get_doc({
                "doctype": "Fees",
                "student": student_row.student,
                "student_name": student_row.student_name,
                "program": doc.program,
                "program_enrollment": enrollment,
                "academic_year": doc.academic_year,
                "academic_term": doc.semester,
                "fee_structure": doc.fee_structure,
                "company": company,
                "posting_date": today(),
                "due_date": doc.due_date,
                # Copy fee components from the fee structure
                "components": [
                    {
                        "fees_category": c.fees_category,
                        "description": c.description,
                        "amount": c.amount,
                    }
                    for c in fee_structure.components
                ],
            })

            if doc.due_date:
                fees_doc.custom_due_date = doc.due_date

            fees_doc.insert(ignore_permissions=True)

            if doc.auto_submit:
                fees_doc.submit()

            created.append(fees_doc.name)

        except Exception as e:
            errors.append(f"{student_row.student}: {str(e)}")
            frappe.log_error(
                f"Bulk fee generation error for {student_row.student}: {str(e)}",
                "Bulk Fee Generator"
            )

    return {
        "created": created,
        "errors": errors,
        "message": _("{0} fee records created, {1} errors").format(len(created), len(errors)),
    }
