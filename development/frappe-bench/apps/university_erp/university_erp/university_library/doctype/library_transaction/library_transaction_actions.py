"""Server-side helpers for Library Transaction desk-side actions:

- ensure_member(student): auto-create a Library Member for a Student if missing.
- issue_article(article, student, due_in_days): create a submitted Library Transaction.
- return_article(transaction, return_date): mark returned + auto-create fine if overdue.
"""

import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate, date_diff


@frappe.whitelist(methods=["POST"])
def ensure_member(student):
    """Find or create a Library Member for the given Student. Returns the member name."""
    if not frappe.db.exists("Student", student):
        frappe.throw(_("Student {0} not found").format(student))

    existing = frappe.db.get_value("Library Member", {"student": student}, "name")
    if existing:
        return {"name": existing, "created": False}

    student_doc = frappe.db.get_value(
        "Student", student,
        ["student_name", "student_email_id", "student_mobile_number"],
        as_dict=True,
    )
    member = frappe.get_doc({
        "doctype": "Library Member",
        "member_type": "Student",
        "student": student,
        "member_name": student_doc.student_name,
        "email": student_doc.student_email_id,
        "mobile": student_doc.student_mobile_number,
        "membership_date": nowdate(),
        "expiry_date": add_days(nowdate(), 365),
        "status": "Active",
        "max_books": 5,
    })
    member.flags.ignore_permissions = True
    member.flags.ignore_mandatory = True
    member.insert(ignore_permissions=True)
    return {"name": member.name, "created": True}


@frappe.whitelist(methods=["GET"])
def list_borrowable_articles(query=None):
    """Return Library Articles with at least one available copy.

    Optional `query` filters by title / author / isbn (LIKE match).
    """
    where = ["la.docstatus = 0", "la.status = 'Available'", "la.available_copies > 0"]
    args = []
    if query:
        where.append("(la.title LIKE %s OR la.author LIKE %s OR la.isbn LIKE %s)")
        like = f"%{query}%"
        args.extend([like, like, like])

    return frappe.db.sql(f"""
        SELECT la.name, la.title, la.author, la.publisher, la.isbn, la.category, la.subject,
               la.available_copies, la.total_copies, la.shelf_location
        FROM `tabLibrary Article` la
        WHERE {' AND '.join(where)}
        ORDER BY la.title
        LIMIT 50
    """, args, as_dict=True)


@frappe.whitelist(methods=["POST"])
def issue_article(article, student, due_in_days=14):
    """Issue a Library Article to a Student.

    - Auto-creates Library Member if missing.
    - Creates + submits a Library Transaction with type=Issue, status=Issued.
    - Decrements article's available_copies and increments issued_copies.
    """
    roles = set(frappe.get_roles(frappe.session.user))
    if not (roles & {"University Librarian", "University Admin", "System Manager", "Administrator"}):
        frappe.throw(_("You don't have permission to issue books"), frappe.PermissionError)

    if not frappe.db.exists("Library Article", article):
        frappe.throw(_("Article {0} not found").format(article))

    art = frappe.db.get_value(
        "Library Article", article,
        ["title", "available_copies", "issued_copies", "total_copies", "status"],
        as_dict=True,
    )
    if (art.available_copies or 0) <= 0:
        frappe.throw(_("Article {0} has no available copies").format(article))

    member_resp = ensure_member(student=student)
    member = member_resp["name"]
    member_doc = frappe.db.get_value(
        "Library Member", member,
        ["member_name", "max_books", "current_borrowed", "outstanding_fines"],
        as_dict=True,
    )
    if (member_doc.outstanding_fines or 0) > 0:
        frappe.throw(_("Member has outstanding fines: ₹{0}. Settle before issuing more books.").format(member_doc.outstanding_fines))
    if (member_doc.current_borrowed or 0) >= (member_doc.max_books or 5):
        frappe.throw(_("Member has reached the borrowing limit ({0}).").format(member_doc.max_books))

    today = nowdate()
    due_date = add_days(today, int(due_in_days or 14))

    txn = frappe.get_doc({
        "doctype": "Library Transaction",
        "transaction_type": "Issue",
        "article": article,
        "article_title": art.title,
        "member": member,
        "member_name": member_doc.member_name,
        "transaction_date": today,
        "issue_date": today,
        "due_date": due_date,
        "status": "Issued",
    })
    txn.flags.ignore_permissions = True
    txn.flags.ignore_mandatory = True
    txn.insert(ignore_permissions=True)
    try:
        txn.submit()
    except Exception as e:
        frappe.log_error(message=str(e), title=f"Library Transaction submit failed for {txn.name}")

    # Update article counters
    frappe.db.set_value("Library Article", article, "available_copies",
                        max((art.available_copies or 0) - 1, 0), update_modified=False)
    frappe.db.set_value("Library Article", article, "issued_copies",
                        (art.issued_copies or 0) + 1, update_modified=False)
    if (art.available_copies or 0) - 1 == 0:
        frappe.db.set_value("Library Article", article, "status", "Issued", update_modified=False)

    # Update member counters
    frappe.db.set_value("Library Member", member, "current_borrowed",
                        (member_doc.current_borrowed or 0) + 1, update_modified=False)
    frappe.db.set_value("Library Member", member, "available_quota",
                        max((member_doc.max_books or 5) - ((member_doc.current_borrowed or 0) + 1), 0),
                        update_modified=False)

    return {
        "transaction": txn.name,
        "member": member,
        "member_created": member_resp["created"],
        "article": article,
        "article_title": art.title,
        "issue_date": today,
        "due_date": due_date,
    }


@frappe.whitelist(methods=["POST"])
def return_article(transaction, return_date=None, fine_per_day=5):
    """Mark a Library Transaction as returned. Auto-create Library Fine if overdue."""
    roles = set(frappe.get_roles(frappe.session.user))
    if not (roles & {"University Librarian", "University Admin", "System Manager", "Administrator"}):
        frappe.throw(_("You don't have permission to mark returns"), frappe.PermissionError)

    if not frappe.db.exists("Library Transaction", transaction):
        frappe.throw(_("Transaction {0} not found").format(transaction))

    txn = frappe.db.get_value(
        "Library Transaction", transaction,
        ["name", "article", "member", "due_date", "status", "docstatus", "return_date"],
        as_dict=True,
    )
    if txn.status == "Returned" or txn.return_date:
        frappe.throw(_("Transaction {0} already marked returned").format(transaction))
    if txn.docstatus != 1:
        frappe.throw(_("Transaction must be submitted to mark return"))

    return_date = return_date or nowdate()
    overdue_days = max(date_diff(return_date, txn.due_date), 0) if txn.due_date else 0

    fine_amount = overdue_days * float(fine_per_day or 5)
    fine_name = None

    if overdue_days > 0:
        fine = frappe.get_doc({
            "doctype": "Library Fine",
            "member": txn.member,
            "article": txn.article,
            "transaction": txn.name,
            "fine_date": return_date,
            "fine_amount": fine_amount,
            "status": "Unpaid",
            "reason": f"Overdue return ({overdue_days} day{'s' if overdue_days != 1 else ''})",
        })
        fine.flags.ignore_permissions = True
        fine.flags.ignore_mandatory = True
        fine.insert(ignore_permissions=True)
        try:
            fine.submit()
        except Exception:
            pass
        fine_name = fine.name

        # Update member outstanding_fines
        member_outstanding = frappe.db.get_value("Library Member", txn.member, "outstanding_fines") or 0
        frappe.db.set_value("Library Member", txn.member, "outstanding_fines",
                            float(member_outstanding) + fine_amount, update_modified=False)

    # Update the transaction
    frappe.db.set_value("Library Transaction", transaction, {
        "return_date": return_date,
        "status": "Returned",
        "is_overdue": 1 if overdue_days > 0 else 0,
        "overdue_days": overdue_days,
        "fine_amount": fine_amount,
        "fine_reference": fine_name,
    }, update_modified=False)

    # Update article + member counters
    art = frappe.db.get_value("Library Article", txn.article,
                              ["available_copies", "issued_copies", "total_copies"], as_dict=True)
    frappe.db.set_value("Library Article", txn.article, "available_copies",
                        (art.available_copies or 0) + 1, update_modified=False)
    frappe.db.set_value("Library Article", txn.article, "issued_copies",
                        max((art.issued_copies or 0) - 1, 0), update_modified=False)
    if (art.available_copies or 0) + 1 > 0:
        frappe.db.set_value("Library Article", txn.article, "status", "Available", update_modified=False)

    cur = frappe.db.get_value("Library Member", txn.member, ["current_borrowed", "max_books"], as_dict=True)
    frappe.db.set_value("Library Member", txn.member, "current_borrowed",
                        max((cur.current_borrowed or 0) - 1, 0), update_modified=False)
    frappe.db.set_value("Library Member", txn.member, "available_quota",
                        (cur.max_books or 5) - max((cur.current_borrowed or 0) - 1, 0),
                        update_modified=False)

    return {
        "transaction": transaction,
        "return_date": return_date,
        "overdue_days": overdue_days,
        "fine_amount": fine_amount,
        "fine_name": fine_name,
    }
