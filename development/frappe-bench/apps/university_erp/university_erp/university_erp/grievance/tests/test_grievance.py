# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days, now_datetime


class TestGrievance(FrappeTestCase):
    """Test cases for Grievance DocType"""

    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        super().setUpClass()
        cls.create_test_grievance_type()

    @classmethod
    def create_test_grievance_type(cls):
        """Create a test grievance type if not exists"""
        if not frappe.db.exists("Grievance Type", "Test Academic Issue"):
            grievance_type = frappe.get_doc({
                "doctype": "Grievance Type",
                "grievance_type_name": "Test Academic Issue",
                "category": "Academic",
                "sla_days": 7,
                "priority": "Medium",
                "is_active": 1,
                "description": "Test grievance type for unit tests"
            })
            grievance_type.insert(ignore_permissions=True)

    def test_grievance_creation(self):
        """Test creating a grievance"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Test Grievance Subject",
            "description": "This is a test grievance description.",
            "category": "Academic",
            "grievance_type": "Test Academic Issue",
            "status": "Draft"
        })
        grievance.insert(ignore_permissions=True)

        self.assertIsNotNone(grievance.name)
        self.assertEqual(grievance.status, "Draft")
        self.assertEqual(grievance.category, "Academic")

        # Clean up
        grievance.delete(force=True)

    def test_grievance_submission(self):
        """Test submitting a grievance sets correct status"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Test Submission Grievance",
            "description": "Testing submission flow.",
            "category": "Administrative",
            "status": "Draft"
        })
        grievance.insert(ignore_permissions=True)

        # Submit the grievance
        grievance.status = "Submitted"
        grievance.submission_date = getdate()
        grievance.save(ignore_permissions=True)

        self.assertEqual(grievance.status, "Submitted")
        self.assertIsNotNone(grievance.submission_date)

        # Clean up
        grievance.delete(force=True)

    def test_grievance_sla_calculation(self):
        """Test SLA expected resolution date calculation"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Test SLA Grievance",
            "description": "Testing SLA calculation.",
            "category": "Academic",
            "grievance_type": "Test Academic Issue",
            "status": "Draft"
        })
        grievance.insert(ignore_permissions=True)

        # Set submission date and calculate SLA
        grievance.submission_date = getdate()
        grievance.status = "Submitted"

        # Get SLA days from grievance type
        sla_days = frappe.db.get_value("Grievance Type", "Test Academic Issue", "sla_days") or 7
        grievance.expected_resolution_date = add_days(grievance.submission_date, sla_days)
        grievance.save(ignore_permissions=True)

        self.assertIsNotNone(grievance.expected_resolution_date)
        expected = add_days(getdate(), sla_days)
        self.assertEqual(grievance.expected_resolution_date, expected)

        # Clean up
        grievance.delete(force=True)

    def test_grievance_anonymous_submission(self):
        """Test anonymous grievance submission"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Anonymous Test Grievance",
            "description": "Testing anonymous submission.",
            "category": "Other",
            "is_anonymous": 1,
            "status": "Submitted",
            "submission_date": getdate()
        })
        grievance.insert(ignore_permissions=True)

        self.assertEqual(grievance.is_anonymous, 1)

        # Clean up
        grievance.delete(force=True)

    def test_grievance_escalation_log(self):
        """Test adding escalation log to grievance"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Escalation Test Grievance",
            "description": "Testing escalation log.",
            "category": "Financial",
            "status": "Submitted",
            "submission_date": getdate()
        })
        grievance.insert(ignore_permissions=True)

        # Add escalation log
        grievance.append("escalation_log", {
            "from_level": 1,
            "to_level": 2,
            "escalated_at": now_datetime(),
            "escalated_by": frappe.session.user,
            "reason": "SLA breach - automated escalation"
        })
        grievance.escalation_level = 2
        grievance.status = "Escalated"
        grievance.save(ignore_permissions=True)

        self.assertEqual(len(grievance.escalation_log), 1)
        self.assertEqual(grievance.escalation_level, 2)
        self.assertEqual(grievance.status, "Escalated")

        # Clean up
        grievance.delete(force=True)

    def test_grievance_resolution(self):
        """Test resolving a grievance"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Resolution Test Grievance",
            "description": "Testing resolution flow.",
            "category": "Academic",
            "status": "In Progress",
            "submission_date": getdate()
        })
        grievance.insert(ignore_permissions=True)

        # Resolve the grievance
        grievance.status = "Resolved"
        grievance.resolution_date = getdate()
        grievance.resolution_summary = "Issue has been addressed by the academic department."
        grievance.resolved_by = frappe.session.user
        grievance.save(ignore_permissions=True)

        self.assertEqual(grievance.status, "Resolved")
        self.assertIsNotNone(grievance.resolution_date)
        self.assertIsNotNone(grievance.resolution_summary)

        # Clean up
        grievance.delete(force=True)

    def test_grievance_days_open_calculation(self):
        """Test days open calculation"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Days Open Test",
            "description": "Testing days open calculation.",
            "category": "Infrastructure",
            "status": "Submitted",
            "submission_date": add_days(getdate(), -5)  # 5 days ago
        })
        grievance.insert(ignore_permissions=True)

        # Calculate days open
        if grievance.submission_date:
            from frappe.utils import date_diff
            grievance.days_open = date_diff(getdate(), grievance.submission_date)
            grievance.save(ignore_permissions=True)

        self.assertEqual(grievance.days_open, 5)

        # Clean up
        grievance.delete(force=True)

    def test_grievance_communication(self):
        """Test adding communication to grievance"""
        grievance = frappe.get_doc({
            "doctype": "Grievance",
            "complainant": frappe.session.user,
            "complainant_type": "Student",
            "complainant_name": "Test Student",
            "subject": "Communication Test",
            "description": "Testing communication log.",
            "category": "Academic",
            "status": "Under Review",
            "submission_date": getdate()
        })
        grievance.insert(ignore_permissions=True)

        # Add communication
        grievance.append("communications", {
            "communication_type": "Response",
            "message": "We are looking into your concern.",
            "timestamp": now_datetime(),
            "sent_by": frappe.session.user
        })
        grievance.save(ignore_permissions=True)

        self.assertEqual(len(grievance.communications), 1)
        self.assertEqual(grievance.communications[0].communication_type, "Response")

        # Clean up
        grievance.delete(force=True)


class TestGrievanceType(FrappeTestCase):
    """Test cases for Grievance Type DocType"""

    def test_grievance_type_creation(self):
        """Test creating a grievance type"""
        if frappe.db.exists("Grievance Type", "Unit Test Type"):
            frappe.delete_doc("Grievance Type", "Unit Test Type", force=True)

        grievance_type = frappe.get_doc({
            "doctype": "Grievance Type",
            "grievance_type_name": "Unit Test Type",
            "category": "Academic",
            "sla_days": 5,
            "priority": "High",
            "is_active": 1
        })
        grievance_type.insert(ignore_permissions=True)

        self.assertIsNotNone(grievance_type.name)
        self.assertEqual(grievance_type.sla_days, 5)

        # Clean up
        grievance_type.delete(force=True)

    def test_grievance_type_escalation_rules(self):
        """Test adding escalation rules to grievance type"""
        if frappe.db.exists("Grievance Type", "Escalation Test Type"):
            frappe.delete_doc("Grievance Type", "Escalation Test Type", force=True)

        grievance_type = frappe.get_doc({
            "doctype": "Grievance Type",
            "grievance_type_name": "Escalation Test Type",
            "category": "Administrative",
            "sla_days": 3,
            "priority": "Urgent",
            "is_active": 1
        })

        # Add escalation rules
        grievance_type.append("escalation_rules", {
            "level": 1,
            "assignee": frappe.session.user,
            "days_before_escalation": 2,
            "auto_escalate_on_sla_breach": 1
        })
        grievance_type.append("escalation_rules", {
            "level": 2,
            "assignee": frappe.session.user,
            "days_before_escalation": 1,
            "auto_escalate_on_sla_breach": 1
        })

        grievance_type.insert(ignore_permissions=True)

        self.assertEqual(len(grievance_type.escalation_rules), 2)

        # Clean up
        grievance_type.delete(force=True)


class TestGrievanceCommittee(FrappeTestCase):
    """Test cases for Grievance Committee DocType"""

    def test_committee_creation(self):
        """Test creating a grievance committee"""
        if frappe.db.exists("Grievance Committee", "Test Committee"):
            frappe.delete_doc("Grievance Committee", "Test Committee", force=True)

        committee = frappe.get_doc({
            "doctype": "Grievance Committee",
            "committee_name": "Test Committee",
            "is_active": 1,
            "description": "Test committee for unit tests"
        })

        # Add members
        committee.append("members", {
            "user": frappe.session.user,
            "member_name": "Test Member",
            "role_in_committee": "Chairperson"
        })

        # Add categories
        committee.append("categories_handled", {
            "category": "Academic"
        })

        committee.insert(ignore_permissions=True)

        self.assertIsNotNone(committee.name)
        self.assertEqual(len(committee.members), 1)
        self.assertEqual(len(committee.categories_handled), 1)

        # Clean up
        committee.delete(force=True)
