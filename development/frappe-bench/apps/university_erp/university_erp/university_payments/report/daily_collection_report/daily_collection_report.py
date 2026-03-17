"""
Daily Collection Report

Shows daily fee collections with payment gateway breakdown.
"""
import frappe
from frappe import _
from frappe.utils import getdate, add_days, flt


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
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "payment_entry",
            "label": _("Receipt No"),
            "fieldtype": "Link",
            "options": "Payment Entry",
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
            "fieldname": "fees",
            "label": _("Fee Reference"),
            "fieldtype": "Link",
            "options": "Fees",
            "width": 150
        },
        {
            "fieldname": "payment_gateway",
            "label": _("Gateway"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "gateway_payment_id",
            "label": _("Transaction ID"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    """Get report data"""
    conditions = get_conditions(filters)

    # Get payment orders with related data
    data = frappe.db.sql("""
        SELECT
            pe.posting_date,
            pe.name as payment_entry,
            po.student,
            s.student_name,
            po.reference_name as fees,
            po.payment_gateway,
            po.gateway_payment_id,
            po.amount,
            po.status,
            pe.company
        FROM `tabPayment Order` po
        INNER JOIN `tabPayment Entry` pe ON pe.name = po.payment_entry
        LEFT JOIN `tabStudent` s ON s.name = po.student
        WHERE po.status = 'Completed'
        AND po.reference_doctype = 'Fees'
        {conditions}
        ORDER BY pe.posting_date DESC, pe.name DESC
    """.format(conditions=conditions), filters, as_dict=True)

    return data


def get_conditions(filters):
    """Build SQL conditions from filters"""
    conditions = []

    if filters.get("from_date"):
        conditions.append("AND pe.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("AND pe.posting_date <= %(to_date)s")

    if filters.get("payment_gateway"):
        conditions.append("AND po.payment_gateway = %(payment_gateway)s")

    if filters.get("company"):
        conditions.append("AND pe.company = %(company)s")

    return " ".join(conditions)


def get_chart(data):
    """Generate chart data"""
    if not data:
        return None

    # Group by date and gateway
    date_gateway_totals = {}
    gateways = set()

    for row in data:
        date_str = str(row.posting_date)
        gateway = row.payment_gateway or "Unknown"
        gateways.add(gateway)

        if date_str not in date_gateway_totals:
            date_gateway_totals[date_str] = {}

        if gateway not in date_gateway_totals[date_str]:
            date_gateway_totals[date_str][gateway] = 0

        date_gateway_totals[date_str][gateway] += flt(row.amount)

    # Sort dates
    sorted_dates = sorted(date_gateway_totals.keys())

    # Build datasets
    datasets = []
    for gateway in sorted(gateways):
        values = [date_gateway_totals[d].get(gateway, 0) for d in sorted_dates]
        datasets.append({
            "name": gateway,
            "values": values
        })

    return {
        "data": {
            "labels": sorted_dates,
            "datasets": datasets
        },
        "type": "bar",
        "colors": ["#2490ef", "#48bb78"],
        "barOptions": {
            "stacked": True
        }
    }


def get_summary(data):
    """Generate summary statistics"""
    if not data:
        return []

    total_amount = sum(flt(row.amount) for row in data)
    transaction_count = len(data)

    # Gateway breakdown
    gateway_totals = {}
    for row in data:
        gateway = row.payment_gateway or "Unknown"
        if gateway not in gateway_totals:
            gateway_totals[gateway] = 0
        gateway_totals[gateway] += flt(row.amount)

    summary = [
        {
            "value": total_amount,
            "indicator": "Green",
            "label": _("Total Collection"),
            "datatype": "Currency",
            "currency": "INR"
        },
        {
            "value": transaction_count,
            "indicator": "Blue",
            "label": _("Total Transactions"),
            "datatype": "Int"
        }
    ]

    for gateway, amount in gateway_totals.items():
        summary.append({
            "value": amount,
            "indicator": "Orange",
            "label": _(f"{gateway} Collection"),
            "datatype": "Currency",
            "currency": "INR"
        })

    return summary
