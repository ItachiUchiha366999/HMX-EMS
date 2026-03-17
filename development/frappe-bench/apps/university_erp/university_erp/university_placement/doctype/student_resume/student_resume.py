# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class StudentResume(Document):
    """Student Resume for placement applications"""

    def validate(self):
        self.update_last_updated()
        self.populate_education_from_student()

    def update_last_updated(self):
        """Update last updated timestamp"""
        self.last_updated = now_datetime()

    def populate_education_from_student(self):
        """Auto-populate current education from student record"""
        if not self.education and self.student:
            student = frappe.get_doc("Student", self.student)
            # Add current program as education entry
            if student.program:
                program_doc = frappe.get_doc("Program", student.program)
                self.append("education", {
                    "qualification": program_doc.program_name,
                    "institution": frappe.db.get_single_value("System Settings", "company") or "University",
                    "year_of_passing": None,  # Current student
                    "percentage_cgpa": str(student.get("cgpa", "")) if student.get("cgpa") else None
                })

    def on_update(self):
        if self.status == "Verified" and not self.verification_date:
            self.db_set("verified_by", frappe.session.user, update_modified=False)
            self.db_set("verification_date", today(), update_modified=False)


@frappe.whitelist()
def submit_for_verification(resume):
    """Submit resume for verification"""
    doc = frappe.get_doc("Student Resume", resume)
    if doc.status == "Draft":
        doc.status = "Submitted"
        doc.save()
        return {"message": _("Resume submitted for verification")}
    else:
        frappe.throw(_("Resume can only be submitted from Draft status"))


@frappe.whitelist()
def verify_resume(resume, action, remarks=None):
    """Verify or reject a resume"""
    doc = frappe.get_doc("Student Resume", resume)

    if doc.status != "Submitted":
        frappe.throw(_("Only submitted resumes can be verified"))

    if action == "approve":
        doc.status = "Verified"
        doc.verified_by = frappe.session.user
        doc.verification_date = today()
    elif action == "reject":
        doc.status = "Rejected"

    doc.save()
    return {"message": _("Resume {0}").format(action + "d")}


@frappe.whitelist()
def get_resume_for_student(student):
    """Get or create resume for a student"""
    resume = frappe.db.exists("Student Resume", {"student": student})
    if resume:
        return frappe.get_doc("Student Resume", resume)
    else:
        # Create new resume
        doc = frappe.get_doc({
            "doctype": "Student Resume",
            "student": student
        })
        doc.insert()
        return doc


@frappe.whitelist()
def search_resumes(query=None, program=None, skills=None, min_cgpa=None, limit=50):
    """Search resumes with filters"""
    filters = {"status": "Verified"}

    if program:
        filters["program"] = program

    resumes = frappe.get_all("Student Resume",
        filters=filters,
        fields=["name", "student", "student_name", "program", "email", "phone"],
        limit=int(limit)
    )

    # Filter by skills if specified
    if skills:
        import json
        if isinstance(skills, str):
            skills = json.loads(skills)

        filtered_resumes = []
        for resume in resumes:
            resume_skills = frappe.get_all("Resume Skill",
                filters={"parent": resume.name},
                pluck="skill_name"
            )
            if any(skill.lower() in [s.lower() for s in resume_skills] for skill in skills):
                filtered_resumes.append(resume)
        resumes = filtered_resumes

    # Filter by CGPA if specified
    if min_cgpa:
        filtered_resumes = []
        for resume in resumes:
            student = frappe.get_doc("Student", resume.student)
            if student.get("cgpa", 0) >= float(min_cgpa):
                filtered_resumes.append(resume)
        resumes = filtered_resumes

    return resumes


@frappe.whitelist()
def generate_resume_pdf(resume):
    """Generate PDF version of resume"""
    doc = frappe.get_doc("Student Resume", resume)

    # Get print format
    html = frappe.get_print("Student Resume", resume, print_format="Standard")

    # Generate PDF
    from frappe.utils.pdf import get_pdf
    pdf = get_pdf(html)

    return pdf
