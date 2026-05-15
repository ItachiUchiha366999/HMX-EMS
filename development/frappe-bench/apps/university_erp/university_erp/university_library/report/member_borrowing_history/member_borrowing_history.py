# Copyright (c) 2026, University ERP and contributors
import frappe
from frappe import _


def execute(filters=None):
    columns = [
        {"fieldname": "transaction", "label": _("Transaction"), "fieldtype": "Link", "options": "Library Transaction", "width": 120},
        {"fieldname": "article", "label": _("Article"), "fieldtype": "Link", "options": "Library Article", "width": 120},
        {"fieldname": "title", "label": _("Title"), "fieldtype": "Data", "width": 200},
        {"fieldname": "transaction_type", "label": _("Type"), "fieldtype": "Data", "width": 80},
        {"fieldname": "issue_date", "label": _("Issue Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "return_date", "label": _("Return Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 80},
        {"fieldname": "fine_amount", "label": _("Fine"), "fieldtype": "Currency", "width": 80}
    ]

    filters = filters or {}
    if not filters.get("member"):
        return columns, [], None, None, [{"value": 0, "label": _("Please select a member"), "datatype": "Data"}]

    conditions = ["lt.member = %s"]
    values = [filters.get("member")]

    if filters.get("from_date"):
        conditions.append("lt.transaction_date >= %s")
        values.append(filters.get("from_date"))

    if filters.get("to_date"):
        conditions.append("lt.transaction_date <= %s")
        values.append(filters.get("to_date"))

    if filters.get("transaction_type"):
        conditions.append("lt.transaction_type = %s")
        values.append(filters.get("transaction_type"))

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql(f"""
        SELECT lt.name as transaction, lt.article, la.title, lt.transaction_type, lt.issue_date, lt.due_date, lt.return_date, lt.status, lt.fine_amount
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Article` la ON lt.article = la.name
        WHERE {where_clause}
        ORDER BY lt.transaction_date DESC
    """, tuple(values), as_dict=True)

    summary = [
        {"value": len(data), "label": _("Total Transactions"), "datatype": "Int"},
        {"value": sum(1 for d in data if d.status == "Active"), "label": _("Currently Borrowed"), "datatype": "Int"},
        {"value": sum(d.fine_amount or 0 for d in data), "label": _("Total Fines"), "datatype": "Currency"}
    ]

    return columns, data, None, None, summary
