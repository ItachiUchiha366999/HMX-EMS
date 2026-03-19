# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
    """Library OPAC Portal context"""
    context.no_cache = 1
    context.title = _("Library Catalog")

    # Get search parameters
    search_query = frappe.form_dict.get("q", "")
    category = frappe.form_dict.get("category", "")
    subject = frappe.form_dict.get("subject", "")
    page = int(frappe.form_dict.get("page", 1))
    page_size = 20

    # Get categories and subjects for filters
    context.categories = frappe.get_all("Library Category",
        fields=["name", "category_name"],
        order_by="category_name"
    )

    context.subjects = frappe.get_all("Library Subject",
        fields=["name", "subject_name"],
        order_by="subject_name"
    )

    # Build search conditions
    conditions = ["la.docstatus < 2"]
    values = {}

    if search_query:
        conditions.append("(la.title LIKE %(search)s OR la.authors LIKE %(search)s OR la.isbn LIKE %(search)s)")
        values["search"] = f"%{search_query}%"

    if category:
        conditions.append("la.category = %(category)s")
        values["category"] = category

    if subject:
        conditions.append("la.subject = %(subject)s")
        values["subject"] = subject

    where_clause = " AND ".join(conditions)

    # Get total count
    total_count = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabLibrary Article` la
        WHERE {where_clause}
    """.format(where_clause=where_clause), values)[0][0]

    # Calculate pagination
    context.total_pages = (total_count + page_size - 1) // page_size
    context.current_page = page
    context.has_prev = page > 1
    context.has_next = page < context.total_pages
    offset = (page - 1) * page_size

    # Get articles
    context.articles = frappe.db.sql("""
        SELECT
            la.name,
            la.title,
            la.article_type,
            la.authors,
            la.publisher,
            la.publication_year,
            la.isbn,
            la.total_copies,
            la.available_count,
            la.cover_image,
            lc.category_name,
            ls.subject_name
        FROM `tabLibrary Article` la
        LEFT JOIN `tabLibrary Category` lc ON la.category = lc.name
        LEFT JOIN `tabLibrary Subject` ls ON la.subject = ls.name
        WHERE {where_clause}
        ORDER BY la.title
        LIMIT %(limit)s OFFSET %(offset)s
    """.format(where_clause=where_clause), {**values, "limit": page_size, "offset": offset}, as_dict=True)

    # Check if user is logged in and has library membership
    context.is_logged_in = frappe.session.user != "Guest"
    context.member = None

    if context.is_logged_in:
        # Check for student or employee membership
        student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
        if student:
            context.member = frappe.db.get_value("Library Member",
                {"student": student}, ["name", "member_name", "max_books"], as_dict=True)

        if not context.member:
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if employee:
                context.member = frappe.db.get_value("Library Member",
                    {"employee": employee}, ["name", "member_name", "max_books"], as_dict=True)

        # Get borrowed books count
        if context.member:
            context.books_borrowed = frappe.db.sql("""
                SELECT COUNT(*) FROM `tabLibrary Transaction` lt
                WHERE lt.library_member = %s
                AND lt.type = 'Issue'
                AND lt.docstatus = 1
                AND lt.name NOT IN (
                    SELECT issue_reference FROM `tabLibrary Transaction`
                    WHERE type = 'Return' AND docstatus = 1 AND issue_reference IS NOT NULL
                )
            """, (context.member.name,))[0][0]

    context.search_query = search_query
    context.selected_category = category
    context.selected_subject = subject


@frappe.whitelist(allow_guest=True)
def search_books(query, category=None, subject=None, page=1):
    """API endpoint for AJAX search"""
    conditions = ["la.docstatus < 2"]
    values = {}

    if query:
        conditions.append("(la.title LIKE %(search)s OR la.authors LIKE %(search)s)")
        values["search"] = f"%{query}%"

    if category:
        conditions.append("la.category = %(category)s")
        values["category"] = category

    if subject:
        conditions.append("la.subject = %(subject)s")
        values["subject"] = subject

    where_clause = " AND ".join(conditions)
    page_size = 20
    offset = (int(page) - 1) * page_size

    articles = frappe.db.sql("""
        SELECT
            la.name,
            la.title,
            la.authors,
            la.available_count,
            la.total_copies
        FROM `tabLibrary Article` la
        WHERE {where_clause}
        ORDER BY la.title
        LIMIT %(limit)s OFFSET %(offset)s
    """.format(where_clause=where_clause), {**values, "limit": page_size, "offset": offset}, as_dict=True)

    return articles


@frappe.whitelist()
def reserve_book(article):
    """Reserve a book for the current user"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to reserve books"))

    # Get library member
    student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    member = None

    if student:
        member = frappe.db.get_value("Library Member", {"student": student}, "name")

    if not member:
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if employee:
            member = frappe.db.get_value("Library Member", {"employee": employee}, "name")

    if not member:
        frappe.throw(_("You don't have a library membership"))

    # Check if already reserved
    existing = frappe.db.exists("Book Reservation", {
        "library_member": member,
        "article": article,
        "status": ["in", ["Pending", "Ready"]]
    })

    if existing:
        frappe.throw(_("You already have a reservation for this book"))

    # Create reservation
    reservation = frappe.get_doc({
        "doctype": "Book Reservation",
        "library_member": member,
        "article": article,
        "status": "Pending"
    })
    reservation.insert()

    return {"message": _("Book reserved successfully"), "reservation": reservation.name}
