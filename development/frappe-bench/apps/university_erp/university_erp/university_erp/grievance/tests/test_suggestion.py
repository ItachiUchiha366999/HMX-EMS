# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate


class TestSuggestion(FrappeTestCase):
    """Test cases for Suggestion DocType"""

    def test_suggestion_creation(self):
        """Test creating a suggestion"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Test Suggestion",
            "description": "This is a test suggestion for improving the campus.",
            "category": "Infrastructure",
            "submitted_by": frappe.session.user,
            "submitted_by_name": "Test User",
            "submission_date": getdate(),
            "status": "Submitted"
        })

        suggestion.insert(ignore_permissions=True)

        self.assertIsNotNone(suggestion.name)
        self.assertEqual(suggestion.status, "Submitted")
        self.assertEqual(suggestion.category, "Infrastructure")

        # Clean up
        suggestion.delete(force=True)

    def test_suggestion_anonymous(self):
        """Test anonymous suggestion submission"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Anonymous Test Suggestion",
            "description": "This is an anonymous test suggestion.",
            "category": "Academic",
            "submitted_by": frappe.session.user,
            "is_anonymous": 1,
            "submission_date": getdate(),
            "status": "Submitted"
        })

        suggestion.insert(ignore_permissions=True)

        self.assertEqual(suggestion.is_anonymous, 1)

        # Clean up
        suggestion.delete(force=True)

    def test_suggestion_voting(self):
        """Test suggestion upvote/downvote functionality"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Voting Test Suggestion",
            "description": "Test suggestion for voting.",
            "category": "Student Life",
            "submitted_by": frappe.session.user,
            "submission_date": getdate(),
            "status": "Submitted",
            "upvotes": 0,
            "downvotes": 0
        })

        suggestion.insert(ignore_permissions=True)

        # Simulate upvotes
        suggestion.upvotes = 10
        suggestion.downvotes = 2
        suggestion.save(ignore_permissions=True)

        self.assertEqual(suggestion.upvotes, 10)
        self.assertEqual(suggestion.downvotes, 2)

        # Clean up
        suggestion.delete(force=True)

    def test_suggestion_approval(self):
        """Test suggestion approval workflow"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Approval Test Suggestion",
            "description": "Test suggestion for approval.",
            "category": "Administrative",
            "submitted_by": frappe.session.user,
            "submission_date": getdate(),
            "status": "Submitted"
        })

        suggestion.insert(ignore_permissions=True)

        # Move through statuses
        suggestion.status = "Under Review"
        suggestion.save(ignore_permissions=True)
        self.assertEqual(suggestion.status, "Under Review")

        suggestion.status = "Approved"
        suggestion.reviewed_by = frappe.session.user
        suggestion.review_date = getdate()
        suggestion.save(ignore_permissions=True)
        self.assertEqual(suggestion.status, "Approved")

        # Clean up
        suggestion.delete(force=True)

    def test_suggestion_rejection(self):
        """Test suggestion rejection"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Rejection Test Suggestion",
            "description": "Test suggestion for rejection.",
            "category": "Other",
            "submitted_by": frappe.session.user,
            "submission_date": getdate(),
            "status": "Submitted"
        })

        suggestion.insert(ignore_permissions=True)

        # Reject the suggestion
        suggestion.status = "Rejected"
        suggestion.reviewed_by = frappe.session.user
        suggestion.review_date = getdate()
        suggestion.review_comments = "Not feasible at this time."
        suggestion.save(ignore_permissions=True)

        self.assertEqual(suggestion.status, "Rejected")
        self.assertIsNotNone(suggestion.review_comments)

        # Clean up
        suggestion.delete(force=True)

    def test_suggestion_implementation(self):
        """Test marking suggestion as implemented"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Implementation Test Suggestion",
            "description": "Test suggestion for implementation.",
            "category": "Academic",
            "submitted_by": frappe.session.user,
            "submission_date": getdate(),
            "status": "Approved"
        })

        suggestion.insert(ignore_permissions=True)

        # Mark as implemented
        suggestion.status = "Implemented"
        suggestion.implementation_date = getdate()
        suggestion.implementation_notes = "Successfully implemented in Spring semester."
        suggestion.save(ignore_permissions=True)

        self.assertEqual(suggestion.status, "Implemented")
        self.assertIsNotNone(suggestion.implementation_date)

        # Clean up
        suggestion.delete(force=True)

    def test_suggestion_with_attachments(self):
        """Test suggestion with attachments"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Attachment Test Suggestion",
            "description": "Test suggestion with attachments.",
            "category": "Infrastructure",
            "submitted_by": frappe.session.user,
            "submission_date": getdate(),
            "status": "Submitted"
        })

        # Add attachment
        suggestion.append("attachments", {
            "file_name": "proposal.pdf",
            "file_url": "/files/proposal.pdf"
        })

        suggestion.insert(ignore_permissions=True)

        self.assertEqual(len(suggestion.attachments), 1)
        self.assertEqual(suggestion.attachments[0].file_name, "proposal.pdf")

        # Clean up
        suggestion.delete(force=True)

    def test_suggestion_categories(self):
        """Test different suggestion categories"""
        categories = ["Academic", "Administrative", "Infrastructure", "Student Life", "Faculty", "Library", "Transport", "Hostel", "Other"]

        for category in categories:
            suggestion = frappe.get_doc({
                "doctype": "Suggestion",
                "title": f"Category Test - {category}",
                "description": f"Test suggestion for {category} category.",
                "category": category,
                "submitted_by": frappe.session.user,
                "submission_date": getdate(),
                "status": "Submitted"
            })

            suggestion.insert(ignore_permissions=True)
            self.assertEqual(suggestion.category, category)
            suggestion.delete(force=True)

    def test_suggestion_priority(self):
        """Test suggestion priority field"""
        suggestion = frappe.get_doc({
            "doctype": "Suggestion",
            "title": "Priority Test Suggestion",
            "description": "Test suggestion with priority.",
            "category": "Academic",
            "submitted_by": frappe.session.user,
            "submission_date": getdate(),
            "status": "Submitted",
            "priority": "High"
        })

        suggestion.insert(ignore_permissions=True)

        self.assertEqual(suggestion.priority, "High")

        # Change priority
        suggestion.priority = "Low"
        suggestion.save(ignore_permissions=True)
        self.assertEqual(suggestion.priority, "Low")

        # Clean up
        suggestion.delete(force=True)
