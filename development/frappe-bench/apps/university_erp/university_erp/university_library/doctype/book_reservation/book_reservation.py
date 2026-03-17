# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, now_datetime


class BookReservation(Document):
    """Book Reservation with notification"""

    def validate(self):
        self.validate_duplicate()
        self.validate_member()
        self.set_dates()

    def validate_duplicate(self):
        """Check for existing pending reservation"""
        existing = frappe.db.exists(
            "Book Reservation",
            {
                "article": self.article,
                "member": self.member,
                "status": "Pending",
                "name": ["!=", self.name or ""]
            }
        )
        if existing:
            frappe.throw(_("You already have a pending reservation for this book"))

    def validate_member(self):
        """Check member eligibility"""
        member = frappe.get_doc("Library Member", self.member)
        if member.status != "Active":
            frappe.throw(_("Member is not active"))

        if member.outstanding_fines > 0:
            frappe.throw(_("Member has outstanding fines"))

    def set_dates(self):
        """Set expected dates"""
        if not self.expected_available_date:
            # Get earliest due date for this article
            earliest_due = frappe.db.get_value(
                "Library Transaction",
                {"article": self.article, "status": "Active"},
                "due_date",
                order_by="due_date asc"
            )
            self.expected_available_date = earliest_due or add_days(nowdate(), 7)

        if not self.expiry_date:
            self.expiry_date = add_days(self.reservation_date, 30)

    def on_update(self):
        """Update article reservation count"""
        article = frappe.get_doc("Library Article", self.article)
        article.update_availability()
        article.set_status()
        article.save(ignore_permissions=True)


@frappe.whitelist()
def reserve_book(article, member):
    """Create a book reservation"""
    # Check if book is available
    article_doc = frappe.get_doc("Library Article", article)
    if article_doc.available_copies > 0:
        frappe.throw(_("Book is currently available. No need to reserve."))

    reservation = frappe.get_doc({
        "doctype": "Book Reservation",
        "article": article,
        "member": member,
        "reservation_date": nowdate()
    })
    reservation.insert()

    return {
        "message": _("Book reserved successfully"),
        "reservation": reservation.name,
        "expected_date": reservation.expected_available_date
    }


@frappe.whitelist()
def cancel_reservation(reservation):
    """Cancel a reservation"""
    res = frappe.get_doc("Book Reservation", reservation)

    if res.status != "Pending":
        frappe.throw(_("Only pending reservations can be cancelled"))

    res.status = "Cancelled"
    res.save()

    return {"message": _("Reservation cancelled")}


@frappe.whitelist()
def notify_available_reservations():
    """Notify members when reserved books become available (scheduled job)"""
    # Get pending reservations for available books
    reservations = frappe.db.sql("""
        SELECT
            br.name,
            br.member,
            br.article,
            la.title,
            lm.email,
            lm.member_name
        FROM `tabBook Reservation` br
        JOIN `tabLibrary Article` la ON br.article = la.name
        JOIN `tabLibrary Member` lm ON br.member = lm.name
        WHERE br.status = 'Pending'
        AND br.notified = 0
        AND la.available_copies > 0
        ORDER BY br.reservation_date
    """, as_dict=True)

    for res in reservations:
        # Update reservation status
        frappe.db.set_value("Book Reservation", res.name, {
            "status": "Available",
            "notified": 1,
            "notification_date": now_datetime()
        })

        # Send email notification
        if res.email:
            frappe.sendmail(
                recipients=[res.email],
                subject=_("Reserved Book Available - {0}").format(res.title),
                message=_("""
                    Dear {0},

                    The book "{1}" that you reserved is now available.

                    Please visit the library to collect it within 3 days,
                    after which the reservation will expire.

                    Regards,
                    University Library
                """).format(res.member_name, res.title)
            )

    return {"notified": len(reservations)}
