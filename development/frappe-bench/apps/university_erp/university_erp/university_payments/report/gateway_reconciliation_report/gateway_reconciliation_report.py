"""
Gateway Reconciliation Report

Compares payment gateway records with internal payment entries to identify discrepancies.
"""
import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    """Execute the report"""
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)

    return columns, data, None, None, summary


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "payment_order",
            "label": _("Payment Order"),
            "fieldtype": "Link",
            "options": "Payment Order",
            "width": 150
        },
        {
            "fieldname": "payment_gateway",
            "label": _("Gateway"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "gateway_order_id",
            "label": _("Gateway Order ID"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "gateway_payment_id",
            "label": _("Gateway Payment ID"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "order_amount",
            "label": _("Order Amount"),
            "fieldtype": "Currency",
            "options": "currency",
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
            "fieldname": "entry_amount",
            "label": _("Entry Amount"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "difference",
            "label": _("Difference"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "reconciliation_status",
            "label": _("Reconciliation"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "creation",
            "label": _("Date"),
            "fieldtype": "Datetime",
            "width": 150
        }
    ]


def get_data(filters):
    """Get report data"""
    conditions = get_conditions(filters)

    # Get all payment orders
    data = frappe.db.sql("""
        SELECT
            po.name as payment_order,
            po.payment_gateway,
            po.gateway_order_id,
            po.gateway_payment_id,
            po.amount as order_amount,
            po.payment_entry,
            pe.paid_amount as entry_amount,
            po.status,
            po.creation
        FROM `tabPayment Order` po
        LEFT JOIN `tabPayment Entry` pe ON pe.name = po.payment_entry
        WHERE 1=1
        {conditions}
        ORDER BY po.creation DESC
    """.format(conditions=conditions), filters, as_dict=True)

    # Calculate differences and reconciliation status
    for row in data:
        row.entry_amount = flt(row.entry_amount)
        row.order_amount = flt(row.order_amount)
        row.difference = row.order_amount - row.entry_amount

        # Determine reconciliation status
        if row.status == "Completed":
            if row.payment_entry and abs(row.difference) < 0.01:
                row.reconciliation_status = "Matched"
            elif row.payment_entry and abs(row.difference) >= 0.01:
                row.reconciliation_status = "Amount Mismatch"
            else:
                row.reconciliation_status = "Missing Entry"
        elif row.status == "Failed":
            row.reconciliation_status = "Failed Payment"
        elif row.status == "Pending":
            row.reconciliation_status = "Pending"
        elif row.status == "Refunded":
            row.reconciliation_status = "Refunded"
        else:
            row.reconciliation_status = "Unknown"

    # Apply reconciliation filter
    if filters.get("reconciliation_status"):
        data = [r for r in data if r.reconciliation_status == filters.get("reconciliation_status")]

    return data


def get_conditions(filters):
    """Build SQL conditions from filters"""
    conditions = []

    if filters.get("from_date"):
        conditions.append("AND po.creation >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("AND po.creation <= %(to_date)s")

    if filters.get("payment_gateway"):
        conditions.append("AND po.payment_gateway = %(payment_gateway)s")

    if filters.get("status"):
        conditions.append("AND po.status = %(status)s")

    return " ".join(conditions)


def get_summary(data):
    """Generate summary statistics"""
    if not data:
        return []

    total_orders = len(data)
    matched = sum(1 for r in data if r.reconciliation_status == "Matched")
    mismatched = sum(1 for r in data if r.reconciliation_status == "Amount Mismatch")
    missing = sum(1 for r in data if r.reconciliation_status == "Missing Entry")
    failed = sum(1 for r in data if r.reconciliation_status == "Failed Payment")
    pending = sum(1 for r in data if r.reconciliation_status == "Pending")

    total_amount = sum(flt(r.order_amount) for r in data if r.status == "Completed")
    total_difference = sum(abs(flt(r.difference)) for r in data if r.reconciliation_status == "Amount Mismatch")

    return [
        {
            "value": total_orders,
            "indicator": "Blue",
            "label": _("Total Orders"),
            "datatype": "Int"
        },
        {
            "value": matched,
            "indicator": "Green",
            "label": _("Matched"),
            "datatype": "Int"
        },
        {
            "value": mismatched,
            "indicator": "Orange",
            "label": _("Amount Mismatch"),
            "datatype": "Int"
        },
        {
            "value": missing,
            "indicator": "Red",
            "label": _("Missing Entry"),
            "datatype": "Int"
        },
        {
            "value": pending,
            "indicator": "Yellow",
            "label": _("Pending"),
            "datatype": "Int"
        },
        {
            "value": total_amount,
            "indicator": "Green",
            "label": _("Total Completed Amount"),
            "datatype": "Currency",
            "currency": "INR"
        },
        {
            "value": total_difference,
            "indicator": "Red",
            "label": _("Total Discrepancy"),
            "datatype": "Currency",
            "currency": "INR"
        }
    ]
