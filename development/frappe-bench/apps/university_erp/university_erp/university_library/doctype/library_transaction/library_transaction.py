# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days, date_diff


class LibraryTransaction(Document):
    """Library Transaction for issue/return/renew operations"""

    def validate(self):
        if self.transaction_type == "Issue":
            self.validate_issue()
        elif self.transaction_type == "Return":
            self.validate_return()
        elif self.transaction_type == "Renew":
            self.validate_renew()

    def validate_issue(self):
        """Validate issue transaction"""
        # Check article availability
        article = frappe.get_doc("Library Article", self.article)
        if article.available_copies <= 0:
            frappe.throw(_("No copies available for {0}").format(article.title))

        # Check member eligibility
        member = frappe.get_doc("Library Member", self.member)
        if member.status != "Active":
            frappe.throw(_("Member {0} is not active").format(member.member_name))

        if member.available_quota <= 0:
            frappe.throw(_("Member has reached maximum borrowing limit"))

        if member.outstanding_fines > 0:
            frappe.throw(_("Member has outstanding fines of {0}").format(member.outstanding_fines))

        # Set dates
        self.issue_date = self.transaction_date
        category = frappe.get_doc("Library Category", article.category)
        self.due_date = add_days(self.issue_date, category.max_issue_days)
        self.status = "Active"

    def validate_return(self):
        """Validate return transaction"""
        self.return_date = self.transaction_date
        self.status = "Returned"
        self.calculate_fine()

    def validate_renew(self):
        """Validate renew transaction"""
        # Get original issue
        original = frappe.db.get_value(
            "Library Transaction",
            {"article": self.article, "member": self.member, "status": "Active"},
            ["issue_date", "due_date"]
        )
        if not original:
            frappe.throw(_("No active issue found for this article"))

        self.issue_date = original[0]
        article = frappe.get_doc("Library Article", self.article)
        category = frappe.get_doc("Library Category", article.category)
        self.due_date = add_days(getdate(nowdate()), category.max_issue_days)
        self.status = "Active"

    def calculate_fine(self):
        """Calculate overdue fine"""
        if not self.return_date or not self.due_date:
            return

        overdue_days = date_diff(self.return_date, self.due_date)
        if overdue_days > 0:
            self.is_overdue = 1
            self.overdue_days = overdue_days

            # Get fine per day from settings (default Rs. 5)
            fine_per_day = frappe.db.get_single_value(
                "University Settings", "library_fine_per_day"
            ) or 5

            self.fine_amount = overdue_days * fine_per_day

    def on_update(self):
        """Update article and member status"""
        if self.transaction_type == "Issue":
            self.update_on_issue()
        elif self.transaction_type == "Return":
            self.update_on_return()

    def update_on_issue(self):
        """Update article and member on issue"""
        article = frappe.get_doc("Library Article", self.article)
        article.update_availability()
        article.set_status()
        article.save(ignore_permissions=True)

        member = frappe.get_doc("Library Member", self.member)
        member.update_borrowing_status()
        member.save(ignore_permissions=True)

    def update_on_return(self):
        """Update article and member on return"""
        article = frappe.get_doc("Library Article", self.article)
        article.update_availability()
        article.set_status()
        article.save(ignore_permissions=True)

        member = frappe.get_doc("Library Member", self.member)
        member.update_borrowing_status()
        member.save(ignore_permissions=True)

        # Create fine if overdue
        if self.fine_amount > 0:
            self.create_fine()

    def create_fine(self):
        """Create library fine record"""
        fine = frappe.get_doc({
            "doctype": "Library Fine",
            "member": self.member,
            "article": self.article,
            "transaction": self.name,
            "fine_date": self.return_date,
            "fine_amount": self.fine_amount,
            "reason": f"Overdue by {self.overdue_days} days"
        })
        fine.insert(ignore_permissions=True)
        self.db_set("fine_reference", fine.name)


@frappe.whitelist()
def issue_book(article, member):
    """Issue a book to a member"""
    transaction = frappe.get_doc({
        "doctype": "Library Transaction",
        "transaction_type": "Issue",
        "article": article,
        "member": member,
        "transaction_date": nowdate()
    })
    transaction.insert()

    return {
        "message": _("Book issued successfully"),
        "transaction": transaction.name,
        "due_date": transaction.due_date
    }


@frappe.whitelist()
def return_book(article, member):
    """Return a book"""
    # Find active issue
    active_issue = frappe.db.get_value(
        "Library Transaction",
        {"article": article, "member": member, "status": "Active", "transaction_type": "Issue"},
        "name"
    )

    if not active_issue:
        frappe.throw(_("No active issue found for this article and member"))

    # Update existing transaction to returned
    transaction = frappe.get_doc("Library Transaction", active_issue)
    transaction.transaction_type = "Return"
    transaction.return_date = nowdate()
    transaction.status = "Returned"
    transaction.calculate_fine()
    transaction.save()

    result = {
        "message": _("Book returned successfully"),
        "transaction": transaction.name
    }

    if transaction.fine_amount > 0:
        result["fine_amount"] = transaction.fine_amount
        result["overdue_days"] = transaction.overdue_days

    return result
