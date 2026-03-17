# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_years


class LibraryMember(Document):
    """Library Member with borrowing limits and fine tracking"""

    def validate(self):
        self.set_member_details()
        self.set_expiry_date()
        self.update_borrowing_status()

    def set_member_details(self):
        """Set member details from linked student/employee"""
        if self.member_type == "Student" and self.student:
            student = frappe.get_doc("Student", self.student)
            self.member_name = student.student_name
            self.email = student.student_email_id
            self.mobile = student.student_mobile_number
        elif self.member_type in ["Faculty", "Staff"] and self.employee:
            employee = frappe.get_doc("Employee", self.employee)
            self.member_name = employee.employee_name
            self.email = employee.personal_email or employee.company_email
            self.mobile = employee.cell_number

    def set_expiry_date(self):
        """Set default expiry date based on member type"""
        if not self.expiry_date:
            years = 1 if self.member_type == "Student" else 3
            self.expiry_date = add_years(self.membership_date, years)

    def update_borrowing_status(self):
        """Update current borrowed count and available quota"""
        if not self.name:
            self.current_borrowed = 0
            self.available_quota = self.max_books
            return

        self.current_borrowed = frappe.db.count(
            "Library Transaction",
            {"member": self.name, "transaction_type": "Issue", "status": "Active"}
        )
        self.available_quota = max(0, self.max_books - self.current_borrowed)

        # Update fines
        fines = frappe.db.sql("""
            SELECT
                COALESCE(SUM(fine_amount), 0) as total,
                COALESCE(SUM(CASE WHEN status != 'Paid' THEN fine_amount ELSE 0 END), 0) as outstanding
            FROM `tabLibrary Fine`
            WHERE member = %s
        """, (self.name,), as_dict=True)[0]

        self.total_fines = fines.total
        self.outstanding_fines = fines.outstanding


@frappe.whitelist()
def get_member_status(member):
    """Get comprehensive member status"""
    member_doc = frappe.get_doc("Library Member", member)
    member_doc.update_borrowing_status()
    member_doc.save(ignore_permissions=True)

    # Get currently borrowed books
    borrowed_books = frappe.db.sql("""
        SELECT
            lt.name as transaction,
            lt.article,
            la.title,
            la.author,
            lt.issue_date,
            lt.due_date,
            DATEDIFF(CURDATE(), lt.due_date) as overdue_days
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Article` la ON lt.article = la.name
        WHERE lt.member = %s
        AND lt.transaction_type = 'Issue'
        AND lt.status = 'Active'
        ORDER BY lt.due_date
    """, (member,), as_dict=True)

    # Get pending reservations
    reservations = frappe.get_all(
        "Book Reservation",
        filters={"member": member, "status": "Pending"},
        fields=["name", "article", "reservation_date", "expected_available_date"]
    )

    # Get unpaid fines
    unpaid_fines = frappe.get_all(
        "Library Fine",
        filters={"member": member, "status": ["!=", "Paid"]},
        fields=["name", "fine_amount", "fine_date", "reason"]
    )

    return {
        "member": member_doc.as_dict(),
        "can_borrow": member_doc.available_quota > 0 and member_doc.status == "Active" and member_doc.outstanding_fines == 0,
        "borrowed_books": borrowed_books,
        "overdue_count": sum(1 for b in borrowed_books if b.overdue_days and b.overdue_days > 0),
        "reservations": reservations,
        "unpaid_fines": unpaid_fines
    }


@frappe.whitelist()
def create_member_from_student(student):
    """Create library member from student"""
    if frappe.db.exists("Library Member", {"student": student}):
        frappe.throw(_("Library member already exists for this student"))

    student_doc = frappe.get_doc("Student", student)

    member = frappe.get_doc({
        "doctype": "Library Member",
        "member_type": "Student",
        "student": student,
        "member_name": student_doc.student_name,
        "email": student_doc.student_email_id,
        "mobile": student_doc.student_mobile_number,
        "max_books": 5
    })
    member.insert()

    return member.name
