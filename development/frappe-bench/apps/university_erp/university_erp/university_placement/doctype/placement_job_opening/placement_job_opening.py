# Copyright (c) 2026, University ERP and contributors
import frappe
from frappe import _
from frappe.model.document import Document


class PlacementJobOpening(Document):
    """Placement Job Opening with eligibility criteria"""

    def validate(self):
        self.validate_dates()

    def validate_dates(self):
        if self.deadline and self.posting_date and self.deadline < self.posting_date:
            frappe.throw(_("Deadline cannot be before posting date"))


@frappe.whitelist()
def check_student_eligibility(job_opening, student):
    """Check if student is eligible for a job opening"""
    job = frappe.get_doc("Placement Job Opening", job_opening)
    student_doc = frappe.get_doc("Student", student)

    # Get student's enrollment
    enrollment = frappe.db.get_value("Program Enrollment", {"student": student, "docstatus": 1}, ["program", "custom_cgpa"], as_dict=True)

    if not enrollment:
        return {"eligible": False, "reason": "No active enrollment found"}

    # Check CGPA
    if job.min_cgpa and (enrollment.custom_cgpa or 0) < job.min_cgpa:
        return {"eligible": False, "reason": f"CGPA {enrollment.custom_cgpa} is below minimum {job.min_cgpa}"}

    # Check eligible programs
    if job.eligible_programs:
        eligible_program_names = [p.program for p in job.eligible_programs]
        if enrollment.program not in eligible_program_names:
            return {"eligible": False, "reason": "Program not eligible for this job"}

    # Check if already applied
    existing = frappe.db.exists("Placement Application", {"job_opening": job_opening, "student": student})
    if existing:
        return {"eligible": False, "reason": "Already applied for this job"}

    return {"eligible": True, "reason": "Eligible to apply"}


@frappe.whitelist()
def get_eligible_students(job_opening):
    """Get list of students eligible for a job opening"""
    job = frappe.get_doc("Placement Job Opening", job_opening)

    conditions = ["pe.docstatus = 1"]
    if job.min_cgpa:
        conditions.append(f"COALESCE(pe.custom_cgpa, 0) >= {job.min_cgpa}")

    if job.eligible_programs:
        programs = ", ".join([f"'{p.program}'" for p in job.eligible_programs])
        conditions.append(f"pe.program IN ({programs})")

    where_clause = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT s.name, s.student_name, pe.program, pe.custom_cgpa
        FROM `tabStudent` s
        JOIN `tabProgram Enrollment` pe ON s.name = pe.student
        WHERE {where_clause}
        AND s.name NOT IN (SELECT student FROM `tabPlacement Application` WHERE job_opening = %s)
        ORDER BY pe.custom_cgpa DESC
    """.format(where_clause=where_clause), (job_opening,), as_dict=True)
