# Copyright (c) 2026, University ERP and contributors
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class PlacementApplication(Document):
    """Placement Application with status tracking"""

    def validate(self):
        self.validate_eligibility()
        self.validate_duplicate()

    def validate_eligibility(self):
        """Check student eligibility for the job"""
        from university_erp.university_placement.doctype.placement_job_opening.placement_job_opening import check_student_eligibility
        result = check_student_eligibility(self.job_opening, self.student)
        if not result.get("eligible") and result.get("reason") != "Already applied for this job":
            frappe.throw(_(result.get("reason")))

    def validate_duplicate(self):
        """Check for duplicate application"""
        existing = frappe.db.exists("Placement Application", {
            "student": self.student, "job_opening": self.job_opening, "name": ["!=", self.name or ""]
        })
        if existing:
            frappe.throw(_("Student has already applied for this job"))

    def on_update(self):
        """Update company stats when placed"""
        if self.status == "Placed":
            self.placement_date = self.placement_date or nowdate()
            company = frappe.get_doc("Placement Company", self.company)
            company.update_stats()


@frappe.whitelist()
def apply_for_job(job_opening, student):
    """Create a placement application"""
    application = frappe.get_doc({
        "doctype": "Placement Application",
        "student": student,
        "job_opening": job_opening,
        "application_date": nowdate()
    })
    application.insert()
    return {"message": _("Application submitted successfully"), "application": application.name}


@frappe.whitelist()
def update_application_status(application, status, offered_ctc=None, remarks=None):
    """Update application status"""
    app = frappe.get_doc("Placement Application", application)
    app.status = status
    if offered_ctc:
        app.offered_ctc = offered_ctc
    if remarks:
        app.remarks = remarks
    if status == "Placed":
        app.placement_date = nowdate()
    app.save()
    return {"message": _("Status updated successfully")}
