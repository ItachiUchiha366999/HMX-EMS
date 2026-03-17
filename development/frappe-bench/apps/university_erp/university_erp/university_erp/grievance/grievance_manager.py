# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Grievance Manager Module

This module provides the GrievanceManager class for handling grievance operations
including submission, assignment, escalation, resolution, and SLA tracking.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, date_diff, today, getdate
from datetime import datetime
from typing import Dict, List, Optional


class GrievanceManager:
    """
    Manager class for handling grievance operations

    Features:
    - Grievance submission with auto-assignment
    - Escalation workflow management
    - SLA tracking and breach handling
    - Communication logging
    - Resolution workflow
    - Statistics and reporting
    """

    @staticmethod
    def submit_grievance(data: Dict) -> str:
        """
        Submit a new grievance

        Args:
            data: Grievance data dictionary containing:
                - subject (str): Subject of the grievance
                - grievance_type (str): Link to Grievance Type
                - category (str): Category of grievance
                - priority (str): Priority level
                - description (str): Detailed description
                - is_anonymous (bool): Whether submission is anonymous
                - submitted_by_type (str): Type of submitter
                - student/faculty/guardian (str): Submitter reference
                - contact_email (str): Contact email
                - contact_phone (str): Contact phone
                - incident_date (str): Date of incident
                - incident_location (str): Location of incident
                - attachments (list): List of attachment dicts

        Returns:
            str: Grievance name/ID
        """
        grievance = frappe.new_doc("Grievance")

        # Set basic fields
        grievance.subject = data.get("subject")
        grievance.grievance_type = data.get("grievance_type")
        grievance.category = data.get("category")
        grievance.priority = data.get("priority", "Medium")
        grievance.description = data.get("description")
        grievance.is_anonymous = data.get("is_anonymous", False)
        grievance.submitted_by_type = data.get("submitted_by_type")

        # Set submitter details (if not anonymous)
        if not grievance.is_anonymous:
            if data.get("student"):
                grievance.student = data.get("student")
            elif data.get("faculty"):
                grievance.faculty = data.get("faculty")
            elif data.get("guardian"):
                grievance.guardian = data.get("guardian")
            elif data.get("employee"):
                grievance.employee = data.get("employee")

            grievance.contact_email = data.get("contact_email")
            grievance.contact_phone = data.get("contact_phone")

        # Set incident details
        grievance.against_person = data.get("against_person")
        grievance.incident_date = data.get("incident_date")
        grievance.incident_location = data.get("incident_location")
        grievance.witnesses = data.get("witnesses")
        grievance.department = data.get("department")

        # Get SLA from grievance type
        if grievance.grievance_type:
            gtype = frappe.get_doc("Grievance Type", grievance.grievance_type)
            grievance.expected_resolution_date = add_days(today(), gtype.sla_days or 7)

        grievance.status = "Submitted"
        grievance.insert()

        # Handle attachments
        for attachment in data.get("attachments", []):
            grievance.append("attachments", {
                "file_name": attachment.get("file_name"),
                "file_url": attachment.get("file_url"),
                "description": attachment.get("description")
            })

        if data.get("attachments"):
            grievance.save()

        # Auto-assign based on grievance type
        GrievanceManager.auto_assign(grievance.name)

        # Send acknowledgment
        GrievanceManager.send_acknowledgment(grievance.name)

        return grievance.name

    @staticmethod
    def auto_assign(grievance_name: str):
        """
        Auto-assign grievance based on type configuration

        Args:
            grievance_name: Name of the grievance to assign
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        if not grievance.grievance_type:
            return

        gtype = frappe.get_doc("Grievance Type", grievance.grievance_type)

        if gtype.default_committee:
            grievance.assigned_committee = gtype.default_committee
            grievance.status = "Assigned"
        elif gtype.default_assignee:
            grievance.assigned_to = gtype.default_assignee
            grievance.status = "Assigned"

        if grievance.status == "Assigned":
            grievance.assignment_date = now_datetime()

            # Log assignment
            grievance.append("communications", {
                "communication_type": "System",
                "message": _("Grievance auto-assigned to {0}").format(
                    grievance.assigned_to or grievance.assigned_committee
                ),
                "timestamp": now_datetime()
            })

        grievance.save()

    @staticmethod
    def send_acknowledgment(grievance_name: str):
        """
        Send acknowledgment to grievance submitter

        Args:
            grievance_name: Name of the grievance
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        if grievance.is_anonymous:
            return  # Can't send to anonymous

        recipient = GrievanceManager._get_complainant_email(grievance)

        if recipient:
            try:
                frappe.sendmail(
                    recipients=[recipient],
                    subject=_("Grievance Submitted - {0}").format(grievance.name),
                    template="grievance_acknowledgment",
                    args={
                        "grievance": grievance,
                        "tracking_id": grievance.name,
                        "expected_resolution": grievance.expected_resolution_date
                    },
                    delayed=True
                )
            except Exception:
                frappe.log_error("Failed to send grievance acknowledgment email")

    @staticmethod
    def add_response(grievance_name: str, message: str,
                    response_type: str = "Response", attachments: list = None):
        """
        Add a response/communication to grievance

        Args:
            grievance_name: Name of the grievance
            message: Response message
            response_type: Type of communication
            attachments: List of attachment dicts
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        grievance.append("communications", {
            "communication_type": response_type,
            "message": message,
            "timestamp": now_datetime(),
            "sent_by": frappe.session.user
        })

        # Add attachments if any
        if attachments:
            for att in attachments:
                grievance.append("attachments", att)

        grievance.save()

        # Notify complainant if not anonymous
        if not grievance.is_anonymous:
            GrievanceManager._notify_complainant(grievance, message)

    @staticmethod
    def escalate(grievance_name: str, reason: str = None) -> int:
        """
        Escalate grievance to next level

        Args:
            grievance_name: Name of the grievance
            reason: Reason for escalation

        Returns:
            int: New escalation level
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        if not grievance.grievance_type:
            frappe.throw(_("Cannot escalate without grievance type"))

        gtype = frappe.get_doc("Grievance Type", grievance.grievance_type)
        current_level = grievance.current_escalation_level or 1
        next_level = current_level + 1

        # Find escalation rule for next level
        next_assignee = None
        for rule in gtype.escalation_matrix:
            if rule.level == next_level:
                next_assignee = rule.assignee
                break

        if not next_assignee:
            frappe.throw(_("No escalation path defined for level {0}").format(next_level))

        # Log escalation
        grievance.append("escalation_history", {
            "from_level": current_level,
            "to_level": next_level,
            "escalated_at": now_datetime(),
            "escalated_by": frappe.session.user,
            "reason": reason,
            "previous_assignee": grievance.assigned_to,
            "new_assignee": next_assignee
        })

        grievance.current_escalation_level = next_level
        grievance.assigned_to = next_assignee
        grievance.status = "Escalated"
        grievance.save()

        # Notify new assignee
        GrievanceManager._notify_escalation(grievance, reason)

        return grievance.current_escalation_level

    @staticmethod
    def resolve(grievance_name: str, resolution_notes: str,
               resolution_type: str, actions: list = None) -> str:
        """
        Resolve a grievance

        Args:
            grievance_name: Name of the grievance
            resolution_notes: Notes on how it was resolved
            resolution_type: Type of resolution
            actions: List of action dicts

        Returns:
            str: Grievance name
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        grievance.resolution_notes = resolution_notes
        grievance.resolution_type = resolution_type
        grievance.resolved_by = frappe.session.user
        grievance.resolution_date = now_datetime()
        grievance.status = "Resolved"

        # Add actions taken
        if actions:
            for action in actions:
                grievance.append("action_taken", {
                    "action_description": action.get("description"),
                    "action_date": action.get("date") or today(),
                    "taken_by": action.get("taken_by") or frappe.session.user
                })

        grievance.save()

        # Notify complainant
        if not grievance.is_anonymous:
            GrievanceManager._notify_resolution(grievance)

        return grievance.name

    @staticmethod
    def reopen(grievance_name: str, reason: str) -> str:
        """
        Reopen a resolved grievance

        Args:
            grievance_name: Name of the grievance
            reason: Reason for reopening

        Returns:
            str: Grievance name
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        if grievance.status not in ["Resolved", "Closed"]:
            frappe.throw(_("Only resolved or closed grievances can be reopened"))

        grievance.reopened_count = (grievance.reopened_count or 0) + 1
        grievance.status = "Reopened"

        grievance.append("communications", {
            "communication_type": "System",
            "message": _("Grievance reopened. Reason: {0}").format(reason),
            "timestamp": now_datetime()
        })

        # Reset resolution fields
        grievance.satisfaction_rating = None
        grievance.satisfaction_feedback = None

        grievance.save()

        return grievance.name

    @staticmethod
    def record_satisfaction(grievance_name: str, rating: int, feedback: str = None):
        """
        Record complainant satisfaction after resolution

        Args:
            grievance_name: Name of the grievance
            rating: Satisfaction rating (1-5)
            feedback: Optional feedback text
        """
        grievance = frappe.get_doc("Grievance", grievance_name)

        grievance.satisfaction_rating = rating
        grievance.satisfaction_feedback = feedback

        if rating >= 4:
            grievance.status = "Closed"
        else:
            # Low satisfaction might trigger review
            grievance.append("communications", {
                "communication_type": "System",
                "message": _("Low satisfaction rating ({0}/5) recorded. Review may be required.").format(rating),
                "timestamp": now_datetime()
            })

        grievance.save()

    @staticmethod
    def check_sla_status():
        """
        Check SLA status for all open grievances (scheduled job)

        Updates SLA status and auto-escalates if configured
        """
        open_grievances = frappe.get_all("Grievance",
            filters={
                "status": ["in", ["Submitted", "Under Review", "Assigned", "In Progress", "Escalated", "Reopened"]]
            },
            fields=["name", "expected_resolution_date", "grievance_type", "current_escalation_level"]
        )

        for g in open_grievances:
            if not g.expected_resolution_date:
                continue

            days_to_sla = date_diff(g.expected_resolution_date, today())

            if days_to_sla < 0:
                # SLA Breached
                frappe.db.set_value("Grievance", g.name, "sla_status", "Breached")

                # Auto-escalate if configured
                if g.grievance_type:
                    try:
                        gtype = frappe.get_cached_doc("Grievance Type", g.grievance_type)
                        auto_escalate = any(
                            r.auto_escalate_on_sla_breach
                            for r in gtype.escalation_matrix
                            if r.level == (g.current_escalation_level or 1) + 1
                        )

                        if auto_escalate:
                            GrievanceManager.escalate(g.name, "Auto-escalated due to SLA breach")
                    except Exception:
                        frappe.log_error(f"Failed to auto-escalate grievance {g.name}")

            elif days_to_sla <= 2:
                # At Risk
                frappe.db.set_value("Grievance", g.name, "sla_status", "At Risk")
            else:
                frappe.db.set_value("Grievance", g.name, "sla_status", "Within SLA")

            # Update days open
            creation_date = frappe.db.get_value("Grievance", g.name, "creation")
            if creation_date:
                days_open = date_diff(today(), getdate(creation_date))
                frappe.db.set_value("Grievance", g.name, "days_open", days_open)

    @staticmethod
    def get_grievance_stats(filters: Dict = None) -> Dict:
        """
        Get grievance statistics

        Args:
            filters: Optional filters for statistics

        Returns:
            Dict with statistics including totals, by status, by category, etc.
        """
        base_filters = filters or {}

        total = frappe.db.count("Grievance", base_filters)

        status_counts = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabGrievance`
            GROUP BY status
        """, as_dict=True)

        category_counts = frappe.db.sql("""
            SELECT category, COUNT(*) as count
            FROM `tabGrievance`
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        """, as_dict=True)

        avg_resolution_time = frappe.db.sql("""
            SELECT AVG(TIMESTAMPDIFF(DAY, creation, resolution_date)) as avg_days
            FROM `tabGrievance`
            WHERE resolution_date IS NOT NULL
        """)[0][0] or 0

        sla_compliance = frappe.db.sql("""
            SELECT
                CASE WHEN COUNT(*) > 0
                    THEN SUM(CASE WHEN sla_status != 'Breached' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
                    ELSE 0 END as compliance
            FROM `tabGrievance`
            WHERE status IN ('Resolved', 'Closed')
        """)[0][0] or 0

        return {
            "total": total,
            "by_status": {s.status: s.count for s in status_counts},
            "by_category": category_counts,
            "avg_resolution_days": round(avg_resolution_time, 1),
            "sla_compliance_percent": round(sla_compliance, 1)
        }

    @staticmethod
    def _get_complainant_email(grievance) -> Optional[str]:
        """Get complainant's email address"""
        if grievance.contact_email:
            return grievance.contact_email

        if grievance.student:
            return frappe.db.get_value("Student", grievance.student, "student_email_id")
        elif grievance.faculty:
            return frappe.db.get_value("Instructor", grievance.faculty, "email")
        elif grievance.employee:
            return frappe.db.get_value("Employee", grievance.employee, "company_email")

        return None

    @staticmethod
    def _notify_complainant(grievance, message):
        """Send notification to complainant"""
        recipient = GrievanceManager._get_complainant_email(grievance)

        if recipient:
            try:
                frappe.sendmail(
                    recipients=[recipient],
                    subject=_("Update on Grievance - {0}").format(grievance.name),
                    template="grievance_update",
                    args={"grievance": grievance, "update_message": message},
                    delayed=True
                )
            except Exception:
                frappe.log_error("Failed to send grievance update email")

    @staticmethod
    def _notify_resolution(grievance):
        """Notify complainant of resolution"""
        recipient = GrievanceManager._get_complainant_email(grievance)

        if recipient:
            try:
                frappe.sendmail(
                    recipients=[recipient],
                    subject=_("Grievance Resolved - {0}").format(grievance.name),
                    template="grievance_resolved",
                    args={
                        "grievance": grievance,
                        "feedback_link": f"/grievance-feedback?grievance={grievance.name}"
                    },
                    delayed=True
                )
            except Exception:
                frappe.log_error("Failed to send grievance resolution email")

    @staticmethod
    def _notify_escalation(grievance, reason):
        """Notify about escalation"""
        if grievance.assigned_to:
            try:
                frappe.sendmail(
                    recipients=[grievance.assigned_to],
                    subject=_("Grievance Escalated - {0}").format(grievance.name),
                    template="grievance_escalation",
                    args={
                        "grievance": grievance,
                        "reason": reason
                    },
                    delayed=True
                )
            except Exception:
                frappe.log_error("Failed to send grievance escalation email")


# Scheduled Jobs

def daily_sla_check():
    """Daily job to check SLA status"""
    GrievanceManager.check_sla_status()


def send_pending_reminders():
    """Send reminders for pending grievances at risk"""
    pending = frappe.get_all("Grievance",
        filters={
            "status": ["in", ["Assigned", "In Progress"]],
            "sla_status": "At Risk"
        },
        fields=["name", "assigned_to", "subject"]
    )

    for g in pending:
        if g.assigned_to:
            try:
                frappe.sendmail(
                    recipients=[g.assigned_to],
                    subject=_("Reminder: Grievance {0} requires attention").format(g.name),
                    template="grievance_reminder",
                    args={"grievance_name": g.name, "subject": g.subject},
                    delayed=True
                )
            except Exception:
                frappe.log_error(f"Failed to send reminder for grievance {g.name}")


# API Endpoints

@frappe.whitelist()
def submit_grievance(data):
    """API to submit a new grievance"""
    import json
    if isinstance(data, str):
        data = json.loads(data)
    return GrievanceManager.submit_grievance(data)


@frappe.whitelist()
def get_grievance_status(grievance_name):
    """API to get grievance status"""
    grievance = frappe.get_doc("Grievance", grievance_name)

    # Check permission
    if not frappe.has_permission("Grievance", "read", grievance):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    return {
        "name": grievance.name,
        "subject": grievance.subject,
        "status": grievance.status,
        "sla_status": grievance.sla_status,
        "assigned_to": grievance.assigned_to,
        "expected_resolution_date": grievance.expected_resolution_date,
        "days_open": grievance.days_open
    }


@frappe.whitelist()
def add_grievance_response(grievance_name, message, response_type="Response"):
    """API to add a response to grievance"""
    GrievanceManager.add_response(grievance_name, message, response_type)
    return {"status": "success"}


@frappe.whitelist()
def get_grievance_statistics():
    """API to get grievance statistics"""
    return GrievanceManager.get_grievance_stats()
