# Copyright (c) 2026, University ERP and contributors
import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "transaction", "label": _("Transaction"), "fieldtype": "Link", "options": "Library Transaction", "width": 120},
        {"fieldname": "article", "label": _("Article"), "fieldtype": "Link", "options": "Library Article", "width": 120},
        {"fieldname": "title", "label": _("Title"), "fieldtype": "Data", "width": 200},
        {"fieldname": "member", "label": _("Member"), "fieldtype": "Link", "options": "Library Member", "width": 120},
        {"fieldname": "member_name", "label": _("Member Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "issue_date", "label": _("Issue Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "overdue_days", "label": _("Overdue Days"), "fieldtype": "Int", "width": 100},
        {"fieldname": "estimated_fine", "label": _("Est. Fine"), "fieldtype": "Currency", "width": 100}
    ]


def get_data(filters):
    fine_per_day = frappe.db.get_single_value("University Settings", "library_fine_per_day") or 5

    return frappe.db.sql(f"""
        SELECT
            lt.name as transaction,
            lt.article,
            la.title,
            lt.member,
            lm.member_name,
            lt.issue_date,
            lt.due_date,
            DATEDIFF(CURDATE(), lt.due_date) as overdue_days,
            DATEDIFF(CURDATE(), lt.due_date) * {fine_per_day} as estimated_fine
        FROM `tabLibrary Transaction` lt
        JOIN `tabLibrary Article` la ON lt.article = la.name
        JOIN `tabLibrary Member` lm ON lt.member = lm.name
        WHERE lt.transaction_type = 'Issue'
        AND lt.status = 'Active'
        AND lt.due_date < %s
        ORDER BY overdue_days DESC
    """, (nowdate(),), as_dict=True)


def get_chart(data):
    if not data:
        return None

    # Group by overdue range
    ranges = {"1-7 days": 0, "8-14 days": 0, "15-30 days": 0, "30+ days": 0}
    for d in data:
        if d.overdue_days <= 7:
            ranges["1-7 days"] += 1
        elif d.overdue_days <= 14:
            ranges["8-14 days"] += 1
        elif d.overdue_days <= 30:
            ranges["15-30 days"] += 1
        else:
            ranges["30+ days"] += 1

    return {
        "data": {"labels": list(ranges.keys()), "datasets": [{"values": list(ranges.values())}]},
        "type": "pie",
        "colors": ["#98d85b", "#ffa00a", "#fc4f51", "#7575ff"]
    }


def get_summary(data):
    if not data:
        return []

    total_overdue = len(data)
    total_fine = sum(d.estimated_fine for d in data)
    max_overdue = max(d.overdue_days for d in data) if data else 0

    return [
        {"value": total_overdue, "label": _("Overdue Books"), "datatype": "Int", "indicator": "red"},
        {"value": total_fine, "label": _("Total Estimated Fines"), "datatype": "Currency"},
        {"value": max_overdue, "label": _("Max Overdue Days"), "datatype": "Int"}
    ]
