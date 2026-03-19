# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LibraryArticle(Document):
    """Library Article (Book/Journal) with availability tracking"""

    def validate(self):
        self.update_availability()
        self.set_status()

    def update_availability(self):
        """Update available copies based on issued and reserved"""
        if not self.name:
            self.available_copies = self.total_copies
            self.issued_copies = 0
            self.reserved_copies = 0
            return

        # Count active issues
        self.issued_copies = frappe.db.count(
            "Library Transaction",
            {"article": self.name, "transaction_type": "Issue", "status": "Active"}
        )

        # Count active reservations
        self.reserved_copies = frappe.db.count(
            "Book Reservation",
            {"article": self.name, "status": "Pending"}
        )

        self.available_copies = max(
            0, self.total_copies - self.issued_copies - self.reserved_copies
        )

    def set_status(self):
        """Set article status based on availability"""
        if self.available_copies == 0 and self.issued_copies > 0:
            self.status = "All Issued"
        elif self.available_copies < self.total_copies:
            self.status = "Partially Available"
        elif self.reserved_copies > 0:
            self.status = "Reserved"
        else:
            self.status = "Available"


@frappe.whitelist()
def search_catalog(query, category=None, subject=None, limit=50):
    """Search library catalog"""
    conditions = ["(title LIKE %s OR author LIKE %s OR isbn LIKE %s OR keywords LIKE %s)"]
    values = [f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]

    if category:
        conditions.append("category = %s")
        values.append(category)

    if subject:
        conditions.append("subject = %s")
        values.append(subject)

    where_clause = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT
            name,
            title,
            author,
            isbn,
            category,
            subject,
            publisher,
            year_of_publication,
            total_copies,
            available_copies,
            status,
            shelf_location,
            image
        FROM `tabLibrary Article`
        WHERE {where_clause}
        ORDER BY title
        LIMIT %s
    """.format(where_clause=where_clause), values + [limit], as_dict=True)


@frappe.whitelist()
def get_article_availability(article):
    """Get detailed availability info for an article"""
    article_doc = frappe.get_doc("Library Article", article)

    # Get current issues
    current_issues = frappe.db.sql("""
        SELECT
            lt.name,
            lt.member,
            lm.member_name,
            lt.issue_date,
            lt.due_date,
            DATEDIFF(CURDATE(), lt.due_date) as overdue_days
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Member` lm ON lt.member = lm.name
        WHERE lt.article = %s
        AND lt.transaction_type = 'Issue'
        AND lt.status = 'Active'
    """, (article,), as_dict=True)

    # Get reservations
    reservations = frappe.db.sql("""
        SELECT
            br.name,
            br.member,
            lm.member_name,
            br.reservation_date,
            br.expected_available_date
        FROM `tabBook Reservation` br
        JOIN `tabLibrary Member` lm ON br.member = lm.name
        WHERE br.article = %s
        AND br.status = 'Pending'
        ORDER BY br.reservation_date
    """, (article,), as_dict=True)

    return {
        "article": article_doc.as_dict(),
        "total_copies": article_doc.total_copies,
        "available_copies": article_doc.available_copies,
        "issued_copies": article_doc.issued_copies,
        "reserved_copies": article_doc.reserved_copies,
        "current_issues": current_issues,
        "reservations": reservations
    }
