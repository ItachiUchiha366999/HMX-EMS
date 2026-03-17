#!/usr/bin/env python3
"""Test library page context"""

import frappe


def run():
    frappe.set_user("student@test.edu")

    print("=" * 70)
    print("TESTING LIBRARY PAGE CONTEXT")
    print("=" * 70)

    from university_erp.www.student_portal.library import get_context

    ctx = frappe._dict()
    get_context(ctx)

    print(f"\nStudent: {ctx.student.student_name}")
    print(f"Active page: {ctx.active_page}")

    print(f"\nLibrary Stats:")
    print(f"  Total Borrowed: {ctx.library_stats['total_borrowed']}")
    print(f"  Currently Issued: {ctx.library_stats['currently_issued']}")
    print(f"  Max Allowed: {ctx.library_stats['max_allowed']}")

    print(f"\nOverdue Books:")
    print(f"  Count: {ctx.overdue_books['count']}")
    print(f"  Fine: Rs. {ctx.overdue_books['fine']}")

    print(f"\nCurrently Issued Books: {len(ctx.issued_books)}")
    for book in ctx.issued_books:
        print(f"  - {book.book_title}")
        print(f"    Author: {book.author}")
        print(f"    Issue Date: {book.issue_date}")
        print(f"    Due Date: {book.due_date}")
        print(f"    Status: {book.status}")
        print(f"    Days Remaining: {book.days_remaining}")

    print(f"\nBorrowing History: {len(ctx.borrowing_history)} transactions")
    for hist in ctx.borrowing_history[:5]:
        print(f"  - {hist.book_title}")
        print(f"    Issued: {hist.issue_date}, Returned: {hist.return_date or 'Not yet'}")
        print(f"    Status: {hist.status}")

    print("\n" + "=" * 70)
