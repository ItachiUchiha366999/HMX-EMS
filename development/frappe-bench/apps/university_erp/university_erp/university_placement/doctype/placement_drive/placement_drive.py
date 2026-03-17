# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate


class PlacementDrive(Document):
    """Placement Drive for managing campus recruitment drives"""

    def validate(self):
        self.validate_dates()
        self.validate_registration_dates()
        self.copy_eligibility_from_job()

    def validate_dates(self):
        """Validate drive dates"""
        if self.drive_end_date and getdate(self.drive_end_date) < getdate(self.drive_date):
            frappe.throw(_("Drive End Date cannot be before Drive Start Date"))

    def validate_registration_dates(self):
        """Validate registration period"""
        if self.registration_start and self.registration_end:
            if self.registration_end < self.registration_start:
                frappe.throw(_("Registration End cannot be before Registration Start"))

    def copy_eligibility_from_job(self):
        """Copy eligibility criteria from job opening if not set"""
        if self.job_opening and not self.eligible_programs:
            job = frappe.get_doc("Placement Job Opening", self.job_opening)
            if job.eligible_programs:
                self.eligible_programs = []
                for prog in job.eligible_programs:
                    self.append("eligible_programs", {
                        "program": prog.program
                    })
            if not self.minimum_cgpa:
                self.minimum_cgpa = job.minimum_cgpa
            if not self.maximum_backlogs:
                self.maximum_backlogs = job.maximum_backlogs

    def on_update(self):
        self.update_statistics()

    def update_statistics(self):
        """Update drive statistics from applications"""
        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total_registered,
                SUM(CASE WHEN status IN ('Shortlisted', 'Selected', 'Offer Accepted') THEN 1 ELSE 0 END) as total_shortlisted,
                SUM(CASE WHEN status = 'Offer Accepted' THEN 1 ELSE 0 END) as total_placed
            FROM `tabPlacement Application`
            WHERE placement_drive = %s
        """, (self.name,), as_dict=True)[0]

        self.db_set("total_registered", stats.total_registered or 0, update_modified=False)
        self.db_set("total_shortlisted", stats.total_shortlisted or 0, update_modified=False)
        self.db_set("total_placed", stats.total_placed or 0, update_modified=False)

        if stats.total_registered:
            percentage = (stats.total_placed or 0) / stats.total_registered * 100
            self.db_set("placement_percentage", percentage, update_modified=False)


@frappe.whitelist()
def register_for_drive(drive, student):
    """Register a student for a placement drive"""
    drive_doc = frappe.get_doc("Placement Drive", drive)

    # Check if registration is open
    if drive_doc.status not in ["Scheduled", "Registration Open"]:
        frappe.throw(_("Registration is not open for this drive"))

    # Check registration period
    current_time = now_datetime()
    if drive_doc.registration_start and current_time < drive_doc.registration_start:
        frappe.throw(_("Registration has not started yet"))
    if drive_doc.registration_end and current_time > drive_doc.registration_end:
        frappe.throw(_("Registration period has ended"))

    # Check max registrations
    if drive_doc.max_registrations > 0:
        current_count = frappe.db.count("Placement Application", {"placement_drive": drive})
        if current_count >= drive_doc.max_registrations:
            frappe.throw(_("Maximum registration limit reached for this drive"))

    # Check if already registered
    existing = frappe.db.exists("Placement Application", {
        "placement_drive": drive,
        "student": student
    })
    if existing:
        frappe.throw(_("Student is already registered for this drive"))

    # Check eligibility
    student_doc = frappe.get_doc("Student", student)

    # Check CGPA
    if drive_doc.minimum_cgpa and student_doc.get("cgpa", 0) < drive_doc.minimum_cgpa:
        frappe.throw(_("Student does not meet minimum CGPA requirement"))

    # Check backlogs
    if drive_doc.maximum_backlogs is not None:
        backlogs = student_doc.get("active_backlogs", 0)
        if backlogs > drive_doc.maximum_backlogs:
            frappe.throw(_("Student has more backlogs than allowed"))

    # Create application
    application = frappe.get_doc({
        "doctype": "Placement Application",
        "student": student,
        "job_opening": drive_doc.job_opening,
        "placement_drive": drive,
        "application_date": frappe.utils.today(),
        "status": "Applied"
    })
    application.insert()

    # Update drive statistics
    drive_doc.update_statistics()

    return application.name


@frappe.whitelist()
def get_drive_applicants(drive, status=None):
    """Get all applicants for a drive"""
    filters = {"placement_drive": drive}
    if status:
        filters["status"] = status

    return frappe.get_all("Placement Application",
        filters=filters,
        fields=["name", "student", "student_name", "program", "status",
                "application_date", "current_round"],
        order_by="application_date asc"
    )


@frappe.whitelist()
def update_round_status(drive, round_number, status):
    """Update status of a specific round"""
    drive_doc = frappe.get_doc("Placement Drive", drive)

    for round_row in drive_doc.rounds:
        if round_row.round_number == int(round_number):
            round_row.status = status
            break

    drive_doc.save()
    return {"message": _("Round status updated successfully")}


@frappe.whitelist()
def bulk_update_applicant_status(drive, applicants, status, round_number=None):
    """Bulk update applicant status"""
    import json
    if isinstance(applicants, str):
        applicants = json.loads(applicants)

    updated = 0
    for applicant in applicants:
        app = frappe.get_doc("Placement Application", applicant)
        app.status = status
        if round_number:
            app.current_round = int(round_number)
        app.save()
        updated += 1

    # Update drive statistics
    drive_doc = frappe.get_doc("Placement Drive", drive)
    drive_doc.update_statistics()

    return {"message": _("{0} applicants updated").format(updated)}
