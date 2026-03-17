# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class Suggestion(Document):
    """
    Suggestion Box DocType for collecting improvement suggestions

    Features:
    - Anonymous submission support
    - Voting/upvoting system
    - Review and approval workflow
    - Implementation tracking
    """

    def validate(self):
        """Validate suggestion"""
        self.validate_status_transition()

    def before_save(self):
        """Actions before saving"""
        if self.has_value_changed("status"):
            self._handle_status_change()

    def validate_status_transition(self):
        """Validate status transitions"""
        if not self.get_doc_before_save():
            return

        old_status = self.get_doc_before_save().status
        new_status = self.status

        # Define valid transitions
        valid_transitions = {
            "New": ["Under Review", "Rejected"],
            "Under Review": ["Approved", "Rejected", "Deferred"],
            "Approved": ["In Implementation", "Deferred"],
            "In Implementation": ["Implemented", "Deferred"],
            "Rejected": ["Under Review"],  # Can be reconsidered
            "Deferred": ["Under Review", "Approved"],
            "Implemented": []  # Final state
        }

        if new_status != old_status:
            if new_status not in valid_transitions.get(old_status, []):
                frappe.throw(
                    _("Cannot change status from {0} to {1}").format(old_status, new_status)
                )

    def _handle_status_change(self):
        """Handle side effects of status changes"""
        if self.status == "Under Review":
            self.reviewed_by = frappe.session.user
            self.review_date = today()
        elif self.status == "Approved":
            if not self.reviewed_by:
                self.reviewed_by = frappe.session.user
                self.review_date = today()
        elif self.status == "Implemented":
            self._notify_submitter_implementation()

    def _notify_submitter_implementation(self):
        """Notify submitter when suggestion is implemented"""
        if self.is_anonymous:
            return

        # Get submitter email
        email = None
        if self.owner and self.owner != "Administrator":
            email = frappe.db.get_value("User", self.owner, "email")

        if email:
            try:
                frappe.sendmail(
                    recipients=[email],
                    subject=_("Your Suggestion Has Been Implemented - {0}").format(self.name),
                    template="suggestion_implemented",
                    args={
                        "suggestion": self
                    },
                    delayed=True
                )
            except Exception:
                frappe.log_error("Failed to send suggestion implementation notification")

    @frappe.whitelist()
    def upvote(self):
        """Upvote the suggestion"""
        # Check if user has already voted
        user = frappe.session.user
        voted_key = f"suggestion_vote_{self.name}_{user}"

        if frappe.cache().get(voted_key):
            frappe.throw(_("You have already voted for this suggestion"))

        self.votes = (self.votes or 0) + 1
        self.save()

        # Mark user as voted (cache for 30 days)
        frappe.cache().set(voted_key, True, expires_in_sec=30 * 24 * 60 * 60)

        return self.votes

    @frappe.whitelist()
    def approve(self, review_comments=None, priority=None, feasibility=None):
        """Approve the suggestion"""
        if self.status not in ["New", "Under Review", "Deferred"]:
            frappe.throw(_("Cannot approve suggestion in current status"))

        self.status = "Approved"
        self.reviewed_by = frappe.session.user
        self.review_date = today()

        if review_comments:
            self.review_comments = review_comments
        if priority:
            self.priority = priority
        if feasibility:
            self.feasibility = feasibility

        self.save()
        return self.status

    @frappe.whitelist()
    def reject(self, reason):
        """Reject the suggestion"""
        if not reason:
            frappe.throw(_("Please provide a reason for rejection"))

        self.status = "Rejected"
        self.reviewed_by = frappe.session.user
        self.review_date = today()
        self.review_comments = reason

        self.save()
        return self.status

    @frappe.whitelist()
    def defer(self, reason=None):
        """Defer the suggestion for later consideration"""
        self.status = "Deferred"
        if reason:
            self.review_comments = (self.review_comments or "") + f"\n\nDeferred: {reason}"

        self.save()
        return self.status

    @frappe.whitelist()
    def start_implementation(self, assigned_to, target_date=None, implementation_plan=None):
        """Start implementation of approved suggestion"""
        if self.status != "Approved":
            frappe.throw(_("Only approved suggestions can be implemented"))

        self.status = "In Implementation"
        self.assigned_to = assigned_to
        if target_date:
            self.target_date = target_date
        if implementation_plan:
            self.implementation_plan = implementation_plan

        self.save()
        return self.status

    @frappe.whitelist()
    def mark_implemented(self, implementation_status=None):
        """Mark suggestion as implemented"""
        if self.status != "In Implementation":
            frappe.throw(_("Only suggestions in implementation can be marked as implemented"))

        self.status = "Implemented"
        if implementation_status:
            self.implementation_status = implementation_status

        self.save()
        return self.status

    @frappe.whitelist()
    def update_implementation_status(self, status_update):
        """Update implementation progress"""
        if self.status != "In Implementation":
            frappe.throw(_("Can only update status for suggestions in implementation"))

        self.implementation_status = status_update
        self.save()


# API endpoints

@frappe.whitelist()
def get_top_suggestions(limit=10, category=None):
    """Get top voted suggestions"""
    filters = {"status": ["in", ["New", "Under Review", "Approved"]]}
    if category:
        filters["category"] = category

    return frappe.get_all("Suggestion",
        filters=filters,
        fields=["name", "subject", "category", "votes", "status"],
        order_by="votes desc",
        limit_page_length=limit
    )


@frappe.whitelist()
def get_suggestion_stats():
    """Get suggestion statistics"""
    stats = {}

    # Total by status
    status_counts = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabSuggestion`
        GROUP BY status
    """, as_dict=True)
    stats["by_status"] = {s.status: s.count for s in status_counts}

    # Total by category
    category_counts = frappe.db.sql("""
        SELECT category, COUNT(*) as count
        FROM `tabSuggestion`
        GROUP BY category
        ORDER BY count DESC
    """, as_dict=True)
    stats["by_category"] = category_counts[:5]

    # Implementation rate
    total = frappe.db.count("Suggestion")
    implemented = frappe.db.count("Suggestion", {"status": "Implemented"})
    stats["implementation_rate"] = (implemented / total * 100) if total > 0 else 0

    return stats
