# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, date_diff


def get_context(context):
    """Student library page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    from university_erp.www.student_portal.index import get_current_student

    student = get_current_student()
    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "library"
    context.issued_books = get_issued_books(student.name)
    context.borrowing_history = get_borrowing_history(student.name)
    context.library_stats = get_library_stats(student.name)
    context.overdue_books = get_overdue_books(student.name)

    return context


def get_library_member(student):
    """Get library member ID for student - handles different field names"""
    try:
        if not frappe.db.exists("DocType", "Library Member"):
            return None

        # Check what fields exist on Library Member
        meta = frappe.get_meta("Library Member")
        fields = [f.fieldname for f in meta.fields]

        # Try different possible field names
        if "student" in fields:
            member = frappe.db.get_value("Library Member", {"student": student}, "name")
            if member:
                return member

        if "library_member_name" in fields:
            member = frappe.db.get_value("Library Member", {"library_member_name": student}, "name")
            if member:
                return member

        # Try matching by name directly
        if frappe.db.exists("Library Member", student):
            return student

        return None
    except Exception:
        return None


def get_issued_books(student):
    """Get currently issued books"""
    try:
        if not frappe.db.exists("DocType", "Library Transaction"):
            return []

        member = get_library_member(student)
        if not member:
            return []

        today = nowdate()

        # Use actual Library Transaction field names: member, due_date, status, article
        issued = frappe.db.sql("""
            SELECT
                lt.name as transaction_id,
                lt.article,
                la.title as book_title,
                la.author,
                lt.issue_date,
                lt.due_date,
                CASE
                    WHEN lt.due_date < %s THEN 'Overdue'
                    WHEN DATEDIFF(lt.due_date, %s) <= 3 THEN 'Due Soon'
                    ELSE 'Active'
                END as status,
                DATEDIFF(lt.due_date, %s) as days_remaining
            FROM `tabLibrary Transaction` lt
            LEFT JOIN `tabLibrary Article` la ON la.name = lt.article
            WHERE lt.member = %s
            AND lt.status = 'Active'
            ORDER BY lt.due_date ASC
        """, (today, today, today, member), as_dict=1)

        return issued
    except Exception as e:
        frappe.log_error(f"Error getting issued books: {str(e)}")
        return []


def get_overdue_books(student):
    """Get overdue books count and fine"""
    try:
        if not frappe.db.exists("DocType", "Library Transaction"):
            return {"count": 0, "fine": 0}

        member = get_library_member(student)
        if not member:
            return {"count": 0, "fine": 0}

        today = nowdate()

        # Use actual field names: due_date, member, status
        overdue = frappe.db.sql("""
            SELECT
                COUNT(*) as count,
                COALESCE(SUM(
                    CASE
                        WHEN lt.due_date < %s THEN DATEDIFF(%s, lt.due_date) * 5
                        ELSE 0
                    END
                ), 0) as fine
            FROM `tabLibrary Transaction` lt
            WHERE lt.member = %s
            AND lt.status = 'Active'
            AND lt.due_date < %s
        """, (today, today, member, today), as_dict=1)

        return overdue[0] if overdue else {"count": 0, "fine": 0}
    except Exception as e:
        frappe.log_error(f"Error getting overdue books: {str(e)}")
        return {"count": 0, "fine": 0}


def get_borrowing_history(student):
    """Get book borrowing history"""
    try:
        if not frappe.db.exists("DocType", "Library Transaction"):
            return []

        member = get_library_member(student)
        if not member:
            return []

        today = nowdate()

        # Get all transactions (both active and returned) for this member
        history = frappe.db.sql("""
            SELECT
                lt.article,
                la.title as book_title,
                la.author,
                lt.issue_date,
                lt.return_date,
                lt.due_date,
                lt.status,
                DATEDIFF(COALESCE(lt.return_date, %s), lt.issue_date) as days_borrowed
            FROM `tabLibrary Transaction` lt
            LEFT JOIN `tabLibrary Article` la ON la.name = lt.article
            WHERE lt.member = %s
            ORDER BY lt.issue_date DESC
            LIMIT 20
        """, (today, member), as_dict=1)

        return history
    except Exception as e:
        frappe.log_error(f"Error getting borrowing history: {str(e)}")
        return []


def get_library_stats(student):
    """Get library usage statistics"""
    try:
        if not frappe.db.exists("DocType", "Library Transaction"):
            return {"total_borrowed": 0, "currently_issued": 0, "max_allowed": 5}

        member = get_library_member(student)
        if not member:
            return {"total_borrowed": 0, "currently_issued": 0, "max_allowed": 5}

        # Count all transactions (total borrowed)
        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total_borrowed
            FROM `tabLibrary Transaction`
            WHERE member = %s
            AND transaction_type = 'Issue'
        """, member, as_dict=1)

        issued_books = get_issued_books(student)

        # Get max books allowed from Library Member
        max_allowed = frappe.db.get_value("Library Member", member, "max_books") or 5

        return {
            "total_borrowed": stats[0].total_borrowed if stats else 0,
            "currently_issued": len(issued_books),
            "max_allowed": max_allowed
        }
    except Exception as e:
        frappe.log_error(f"Error getting library stats: {str(e)}")
        return {"total_borrowed": 0, "currently_issued": 0, "max_allowed": 5}
