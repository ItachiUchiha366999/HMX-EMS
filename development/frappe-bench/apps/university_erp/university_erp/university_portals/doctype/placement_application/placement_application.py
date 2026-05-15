# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PlacementApplication(Document):
    # Maps the 8 workflow states the placement officer walks through to the
    # `status` Select field that the portal shows the student. Keeps them in
    # lock-step regardless of whether the change came from the workflow engine,
    # a desk save, or the API.
    WORKFLOW_TO_STATUS = {
        "Applied": "Applied",
        "Screening": "Screening",
        "Shortlisted": "Shortlisted",
        "Interview Scheduled": "Interview Scheduled",
        "Offer Received": "Offer Received",
        "Accepted": "Accepted",
        "Rejected": "Rejected",
        "Withdrawn": "Withdrawn",
    }

    def validate(self):
        self.validate_duplicate()
        self.validate_eligibility()
        self.sync_status_with_workflow()

    def sync_status_with_workflow(self):
        """Keep `status` in sync with `workflow_state` so the portal reflects
        the placement officer's progress (Shortlisted → Interview Scheduled →
        Offer Received → Accepted)."""
        ws = getattr(self, "workflow_state", None)
        target = self.WORKFLOW_TO_STATUS.get(ws)
        if target and self.status != target:
            self.status = target

        # Set current_round from interview_round when entering Interview Scheduled
        if ws == "Interview Scheduled" and getattr(self, "interview_round", None) and not self.current_round:
            self.current_round = self.interview_round

    def validate_duplicate(self):
        """Check for duplicate application — by drive when present, else by job_opening.

        `job_opening` is a DB column but isn't in the active doctype meta, so
        accessing `self.job_opening` raises AttributeError. Use getattr + a
        direct DB read as fallback so the duplicate guard works on both new
        and pre-existing rows.
        """
        if self.placement_drive:
            existing = frappe.db.exists("Placement Application", {
                "student": self.student,
                "placement_drive": self.placement_drive,
                "name": ["!=", self.name or ""],
                "status": ["!=", "Withdrawn"],
            })
            if existing:
                frappe.throw(_("You have already applied for this placement drive"))
            return

        # job_opening lives on the row but not on the meta — read it via SQL
        job_opening = getattr(self, "job_opening", None)
        if not job_opening and self.name:
            job_opening = frappe.db.get_value("Placement Application", self.name, "job_opening")
        if not job_opening:
            return  # Direct-job check needs a job_opening; skip if neither path applies

        existing = frappe.db.sql("""
            SELECT name FROM `tabPlacement Application`
            WHERE student=%s AND job_opening=%s AND name != %s AND status != 'Withdrawn'
            LIMIT 1
        """, (self.student, job_opening, self.name or ""))
        if existing:
            frappe.throw(_("You have already applied for this job"))

    def validate_eligibility(self):
        """Validate student eligibility — only enforced when applying through a Placement Drive."""
        if not self.is_new() or not self.placement_drive:
            return
        if not frappe.db.exists("Placement Drive", self.placement_drive):
            return
        drive = frappe.get_doc("Placement Drive", self.placement_drive)
        if hasattr(drive, "is_application_open") and not drive.is_application_open():
            frappe.throw(_("Applications are closed for this placement drive"))
        if getattr(drive, "minimum_cgpa", None):
            profile = frappe.db.get_value("Placement Profile", {"student": self.student}, "cgpa")
            if profile and profile < drive.minimum_cgpa:
                frappe.throw(_("Your CGPA ({0}) does not meet the minimum requirement ({1})").format(
                    profile, drive.minimum_cgpa))

    def on_update(self):
        """Update placement drive statistics if applicable."""
        if self.placement_drive and frappe.db.exists("Placement Drive", self.placement_drive):
            try:
                drive = frappe.get_doc("Placement Drive", self.placement_drive)
                if hasattr(drive, "update_stats"):
                    drive.update_stats()
                    drive.db_update()
            except Exception as e:
                frappe.log_error(message=str(e), title=f"Placement Drive stats update failed for {self.name}")

        if self.status == "Selected":
            frappe.db.set_value("Placement Profile", {"student": self.student}, "status", "Placed")
