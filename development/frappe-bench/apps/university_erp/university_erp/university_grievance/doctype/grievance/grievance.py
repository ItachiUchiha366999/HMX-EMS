# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_days, date_diff, today, getdate


class Grievance(Document):
    """
    Grievance DocType for managing student/staff grievances

    Features:
    - Anonymous submission support
    - SLA tracking and escalation
    - Communication logging
    - Resolution workflow
    - Satisfaction feedback
    """

    def validate(self):
        """Validate grievance data"""
        self.validate_submitter_details()
        self.validate_anonymous_submission()
        self.set_category_from_type()
        self.update_sla_status()

    def before_save(self):
        """Actions before saving"""
        self.calculate_days_open()
        if self.status == "Submitted" and not self.expected_resolution_date:
            self.set_expected_resolution_date()

    def on_update(self):
        """Actions after update"""
        self.notify_on_status_change()

    def validate_submitter_details(self):
        """Validate that submitter details are provided when not anonymous"""
        if self.is_anonymous:
            return

        if not self.submitted_by_type:
            frappe.throw(_("Please specify who is submitting this grievance"))

        # Check if corresponding link field is filled based on submitted_by_type
        if self.submitted_by_type == "Student" and not self.student:
            frappe.throw(_("Please select the student submitting this grievance"))
        elif self.submitted_by_type == "Faculty" and not self.faculty:
            frappe.throw(_("Please select the faculty member submitting this grievance"))

    def validate_anonymous_submission(self):
        """Check if anonymous submission is allowed for this grievance type"""
        if self.is_anonymous and self.grievance_type:
            gtype = frappe.get_cached_doc("Grievance Type", self.grievance_type)
            if not gtype.allow_anonymous:
                frappe.throw(_("Anonymous submission is not allowed for this grievance type"))

    def set_category_from_type(self):
        """Auto-set category from grievance type if not specified"""
        if self.grievance_type and not self.category:
            gtype = frappe.get_cached_doc("Grievance Type", self.grievance_type)
            self.category = gtype.category

    def set_expected_resolution_date(self):
        """Set expected resolution date based on grievance type SLA"""
        if self.grievance_type:
            gtype = frappe.get_cached_doc("Grievance Type", self.grievance_type)
            self.expected_resolution_date = gtype.get_default_sla_date()

    def update_sla_status(self):
        """Update SLA status based on expected resolution date"""
        if not self.expected_resolution_date:
            return

        if self.status in ["Resolved", "Closed"]:
            # Check if resolved within SLA
            if self.resolution_date:
                resolution_date = getdate(self.resolution_date)
                expected_date = getdate(self.expected_resolution_date)
                if resolution_date <= expected_date:
                    self.sla_status = "Within SLA"
                else:
                    self.sla_status = "Breached"
            return

        days_to_sla = date_diff(self.expected_resolution_date, today())

        if days_to_sla < 0:
            self.sla_status = "Breached"
        elif days_to_sla <= 2:
            self.sla_status = "At Risk"
        else:
            self.sla_status = "Within SLA"

    def calculate_days_open(self):
        """Calculate how many days the grievance has been open"""
        if self.status in ["Resolved", "Closed"]:
            if self.resolution_date:
                self.days_open = date_diff(getdate(self.resolution_date), getdate(self.creation))
            return

        self.days_open = date_diff(today(), getdate(self.creation))

    def notify_on_status_change(self):
        """Send notifications when status changes"""
        if not self.has_value_changed("status"):
            return

        old_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
        new_status = self.status

        # Don't notify for draft status
        if new_status == "Draft":
            return

        # Send notification based on status
        if new_status == "Assigned":
            self._notify_assignee()
        elif new_status == "Resolved":
            self._notify_complainant_resolution()
        elif new_status == "Escalated":
            self._notify_escalation()

    def _notify_assignee(self):
        """Notify the assigned user/committee"""
        assignee = self.assigned_to
        if not assignee and self.assigned_committee:
            # Get committee chairperson
            committee = frappe.get_doc("Grievance Committee", self.assigned_committee)
            assignee = committee.chairperson

        if assignee:
            frappe.publish_realtime(
                event="grievance_assigned",
                message={
                    "grievance": self.name,
                    "subject": self.subject
                },
                user=assignee
            )

    def _notify_complainant_resolution(self):
        """Notify complainant when grievance is resolved"""
        if self.is_anonymous:
            return

        email = self._get_complainant_email()
        if email:
            try:
                frappe.sendmail(
                    recipients=[email],
                    subject=_("Grievance Resolved - {0}").format(self.name),
                    template="grievance_resolved",
                    args={
                        "grievance": self,
                        "resolution_notes": self.resolution_notes
                    },
                    delayed=True
                )
            except Exception:
                frappe.log_error("Failed to send grievance resolution email")

    def _notify_escalation(self):
        """Notify about escalation"""
        if self.assigned_to:
            frappe.publish_realtime(
                event="grievance_escalated",
                message={
                    "grievance": self.name,
                    "level": self.current_escalation_level
                },
                user=self.assigned_to
            )

    def _get_complainant_email(self):
        """Get complainant's email address"""
        if self.contact_email:
            return self.contact_email

        if self.student:
            return frappe.db.get_value("Student", self.student, "student_email_id")
        elif self.faculty:
            return frappe.db.get_value("Instructor", self.faculty, "email")
        elif self.employee:
            return frappe.db.get_value("Employee", self.employee, "company_email")

        return None

    @frappe.whitelist()
    def submit_grievance(self):
        """Submit the grievance for review"""
        if self.status != "Draft":
            frappe.throw(_("Only draft grievances can be submitted"))

        self.status = "Submitted"
        self.save()

        # Auto-assign if configured
        self._auto_assign()

        # Log communication
        self.append("communications", {
            "communication_type": "System",
            "message": _("Grievance submitted for review"),
            "timestamp": now_datetime(),
            "sent_by": frappe.session.user
        })
        self.save()

        return self.name

    def _auto_assign(self):
        """Auto-assign grievance based on type configuration"""
        if not self.grievance_type:
            return

        gtype = frappe.get_doc("Grievance Type", self.grievance_type)

        if gtype.default_committee:
            self.assigned_committee = gtype.default_committee
            self.status = "Assigned"
        elif gtype.default_assignee:
            self.assigned_to = gtype.default_assignee
            self.status = "Assigned"

        if self.status == "Assigned":
            self.assignment_date = now_datetime()

    @frappe.whitelist()
    def escalate(self, reason=None):
        """Escalate grievance to next level"""
        if not self.grievance_type:
            frappe.throw(_("Cannot escalate without grievance type"))

        gtype = frappe.get_doc("Grievance Type", self.grievance_type)
        next_level = (self.current_escalation_level or 1) + 1

        # Get next assignee from escalation matrix
        next_assignee = gtype.get_escalation_assignee(next_level)
        if not next_assignee:
            frappe.throw(_("No escalation path defined for level {0}").format(next_level))

        # Log escalation
        self.append("escalation_history", {
            "from_level": self.current_escalation_level,
            "to_level": next_level,
            "escalated_at": now_datetime(),
            "escalated_by": frappe.session.user,
            "reason": reason,
            "previous_assignee": self.assigned_to,
            "new_assignee": next_assignee
        })

        # Update assignment
        self.current_escalation_level = next_level
        self.assigned_to = next_assignee
        self.status = "Escalated"

        # Log communication
        self.append("communications", {
            "communication_type": "System",
            "message": _("Grievance escalated to level {0}. Reason: {1}").format(
                next_level, reason or "Not specified"
            ),
            "timestamp": now_datetime()
        })

        self.save()
        return self.current_escalation_level

    @frappe.whitelist()
    def resolve(self, resolution_notes, resolution_type, actions=None):
        """Resolve the grievance"""
        self.resolution_notes = resolution_notes
        self.resolution_type = resolution_type
        self.resolved_by = frappe.session.user
        self.resolution_date = now_datetime()
        self.status = "Resolved"

        # Add actions taken
        if actions:
            for action in actions:
                self.append("action_taken", {
                    "action_description": action.get("description"),
                    "action_date": action.get("date") or today(),
                    "taken_by": action.get("taken_by") or frappe.session.user
                })

        # Log communication
        self.append("communications", {
            "communication_type": "System",
            "message": _("Grievance resolved: {0}").format(resolution_type),
            "timestamp": now_datetime()
        })

        self.save()
        return self.name

    @frappe.whitelist()
    def reopen(self, reason):
        """Reopen a resolved grievance"""
        if self.status not in ["Resolved", "Closed"]:
            frappe.throw(_("Only resolved or closed grievances can be reopened"))

        self.reopened_count = (self.reopened_count or 0) + 1
        self.status = "Reopened"
        self.satisfaction_rating = None
        self.satisfaction_feedback = None

        # Log communication
        self.append("communications", {
            "communication_type": "System",
            "message": _("Grievance reopened. Reason: {0}").format(reason),
            "timestamp": now_datetime()
        })

        self.save()
        return self.name

    @frappe.whitelist()
    def add_communication(self, message, communication_type="Response"):
        """Add a communication entry"""
        self.append("communications", {
            "communication_type": communication_type,
            "message": message,
            "timestamp": now_datetime(),
            "sent_by": frappe.session.user
        })
        self.save()

    @frappe.whitelist()
    def record_satisfaction(self, rating, feedback=None):
        """Record complainant satisfaction after resolution"""
        self.satisfaction_rating = rating
        self.satisfaction_feedback = feedback

        if rating >= 4:
            self.status = "Closed"
        else:
            # Low satisfaction might trigger review
            self.append("communications", {
                "communication_type": "System",
                "message": _("Low satisfaction rating ({0}/5) recorded. Review may be required.").format(rating),
                "timestamp": now_datetime()
            })

        self.save()
