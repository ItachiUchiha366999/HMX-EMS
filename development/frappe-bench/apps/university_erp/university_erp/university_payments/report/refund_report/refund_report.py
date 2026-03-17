"""
Refund Report

Shows all fee refunds with status tracking and amount analysis.
"""
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    """Execute the report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "name",
            "label": _("Refund ID"),
            "fieldtype": "Link",
            "options": "Fee Refund",
            "width": 150
        },
        {
            "fieldname": "fees",
            "label": _("Fee Reference"),
            "fieldtype": "Link",
            "options": "Fees",
            "width": 150
        },
        {
            "fieldname": "student",
            "label": _("Student"),
            "fieldtype": "Link",
            "options": "Student",
            "width": 120
        },
        {
            "fieldname": "student_name",
            "label": _("Student Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "refund_amount",
            "label": _("Refund Amount"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "reason",
            "label": _("Reason"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "refund_mode",
            "label": _("Refund Mode"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "payment_entry",
            "label": _("Payment Entry"),
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": 150
        },
        {
            "fieldname": "creation",
            "label": _("Requested On"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "approved_by",
            "label": _("Approved By"),
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "fieldname": "processed_date",
            "label": _("Processed On"),
            "fieldtype": "Date",
            "width": 100
        }
    ]


def get_data(filters):
    """Get report data"""
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            fr.name,
            fr.fees,
            fr.student,
            fr.student_name,
            fr.refund_amount,
            fr.reason,
            fr.status,
            fr.refund_mode,
            fr.payment_entry,
            fr.creation,
            fr.approved_by,
            fr.processed_date
        FROM `tabFee Refund` fr
        WHERE 1=1
        {conditions}
        ORDER BY fr.creation DESC
    """.format(conditions=conditions), filters, as_dict=True)

    return data


def get_conditions(filters):
    """Build SQL conditions from filters"""
    conditions = []

    if filters.get("from_date"):
        conditions.append("AND fr.creation >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("AND fr.creation <= %(to_date)s")

    if filters.get("status"):
        conditions.append("AND fr.status = %(status)s")

    if filters.get("reason"):
        conditions.append("AND fr.reason = %(reason)s")

    if filters.get("student"):
        conditions.append("AND fr.student = %(student)s")

    return " ".join(conditions)


def get_chart(data):
    """Generate chart data"""
    if not data:
        return None

    # Group by status
    status_totals = {}
    for row in data:
        status = row.status or "Unknown"
        if status not in status_totals:
            status_totals[status] = 0
        status_totals[status] += flt(row.refund_amount)

    return {
        "data": {
            "labels": list(status_totals.keys()),
            "datasets": [{
                "name": "Refund Amount",
                "values": list(status_totals.values())
            }]
        },
        "type": "pie",
        "colors": ["#48bb78", "#ecc94b", "#f56565", "#4299e1"]
    }


def get_summary(data):
    """Generate summary statistics"""
    if not data:
        return []

    total_refunds = len(data)
    total_amount = sum(flt(r.refund_amount) for r in data)

    # Status breakdown
    pending = sum(flt(r.refund_amount) for r in data if r.status == "Pending")
    approved = sum(flt(r.refund_amount) for r in data if r.status == "Approved")
    processed = sum(flt(r.refund_amount) for r in data if r.status == "Processed")
    rejected = sum(flt(r.refund_amount) for r in data if r.status == "Rejected")

    pending_count = sum(1 for r in data if r.status == "Pending")
    approved_count = sum(1 for r in data if r.status == "Approved")
    processed_count = sum(1 for r in data if r.status == "Processed")
    rejected_count = sum(1 for r in data if r.status == "Rejected")

    return [
        {
            "value": total_refunds,
            "indicator": "Blue",
            "label": _("Total Refunds"),
            "datatype": "Int"
        },
        {
            "value": total_amount,
            "indicator": "Blue",
            "label": _("Total Amount"),
            "datatype": "Currency",
            "currency": "INR"
        },
        {
            "value": pending_count,
            "indicator": "Yellow",
            "label": _("Pending"),
            "datatype": "Int"
        },
        {
            "value": approved_count,
            "indicator": "Orange",
            "label": _("Approved (Awaiting Processing)"),
            "datatype": "Int"
        },
        {
            "value": processed_count,
            "indicator": "Green",
            "label": _("Processed"),
            "datatype": "Int"
        },
        {
            "value": rejected_count,
            "indicator": "Red",
            "label": _("Rejected"),
            "datatype": "Int"
        },
        {
            "value": processed,
            "indicator": "Green",
            "label": _("Processed Amount"),
            "datatype": "Currency",
            "currency": "INR"
        }
    ]
