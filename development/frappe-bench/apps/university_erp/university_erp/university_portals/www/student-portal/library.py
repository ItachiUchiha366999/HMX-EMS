# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, date_diff


def get_context(context):
    """Student library page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.university_portals.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.issued_books = get_issued_books(student.name)
    context.borrowing_history = get_borrowing_history(student.name)
    context.library_stats = get_library_stats(student.name)
    context.overdue_books = get_overdue_books(student.name)

    return context


def get_issued_books(student):
    """Get currently issued books"""
    # Get library member ID
    member = frappe.db.get_value("Library Member", {"student": student}, "name")
    if not member:
        return []

    issued = frappe.db.sql("""
        SELECT
            lt.name as transaction_id,
            lt.article,
            la.article_name as book_title,
            la.author,
            lt.date as issue_date,
            lt.return_date as due_date,
            CASE
                WHEN lt.return_date < %s THEN 'Overdue'
                WHEN DATEDIFF(lt.return_date, %s) <= 3 THEN 'Due Soon'
                ELSE 'Active'
            END as status,
            DATEDIFF(lt.return_date, %s) as days_remaining
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Article` la ON la.name = lt.article
        WHERE lt.library_member = %s
        AND lt.type = 'Issue'
        AND lt.docstatus = 1
        AND NOT EXISTS (
            SELECT 1 FROM `tabLibrary Transaction` rt
            WHERE rt.article = lt.article
            AND rt.library_member = lt.library_member
            AND rt.type = 'Return'
            AND rt.date > lt.date
            AND rt.docstatus = 1
        )
        ORDER BY lt.return_date ASC
    """, (nowdate(), nowdate(), nowdate(), member), as_dict=1)

    return issued


def get_overdue_books(student):
    """Get overdue books count and fine"""
    member = frappe.db.get_value("Library Member", {"student": student}, "name")
    if not member:
        return {"count": 0, "fine": 0}

    overdue = frappe.db.sql("""
        SELECT
            COUNT(*) as count,
            COALESCE(SUM(
                CASE
                    WHEN lt.return_date < %s THEN DATEDIFF(%s, lt.return_date) * 5
                    ELSE 0
                END
            ), 0) as fine
        FROM `tabLibrary Transaction` lt
        WHERE lt.library_member = %s
        AND lt.type = 'Issue'
        AND lt.docstatus = 1
        AND lt.return_date < %s
        AND NOT EXISTS (
            SELECT 1 FROM `tabLibrary Transaction` rt
            WHERE rt.article = lt.article
            AND rt.library_member = lt.library_member
            AND rt.type = 'Return'
            AND rt.date > lt.date
            AND rt.docstatus = 1
        )
    """, (nowdate(), nowdate(), member, nowdate()), as_dict=1)

    return overdue[0] if overdue else {"count": 0, "fine": 0}


def get_borrowing_history(student):
    """Get book borrowing history"""
    member = frappe.db.get_value("Library Member", {"student": student}, "name")
    if not member:
        return []

    history = frappe.db.sql("""
        SELECT
            lt.article,
            la.article_name as book_title,
            la.author,
            lt.date as issue_date,
            rt.date as return_date,
            DATEDIFF(COALESCE(rt.date, %s), lt.date) as days_borrowed
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Article` la ON la.name = lt.article
        LEFT JOIN `tabLibrary Transaction` rt ON rt.article = lt.article
            AND rt.library_member = lt.library_member
            AND rt.type = 'Return'
            AND rt.date > lt.date
            AND rt.docstatus = 1
        WHERE lt.library_member = %s
        AND lt.type = 'Issue'
        AND lt.docstatus = 1
        ORDER BY lt.date DESC
        LIMIT 20
    """, (nowdate(), member), as_dict=1)

    return history


def get_library_stats(student):
    """Get library usage statistics"""
    member = frappe.db.get_value("Library Member", {"student": student}, "name")
    if not member:
        return {"total_borrowed": 0, "currently_issued": 0, "max_allowed": 5}

    stats = frappe.db.sql("""
        SELECT
            COUNT(*) as total_borrowed
        FROM `tabLibrary Transaction`
        WHERE library_member = %s
        AND type = 'Issue'
        AND docstatus = 1
    """, member, as_dict=1)

    issued_books = len(get_issued_books(student))

    return {
        "total_borrowed": stats[0].total_borrowed if stats else 0,
        "currently_issued": issued_books,
        "max_allowed": 5  # This could be fetched from library settings
    }
