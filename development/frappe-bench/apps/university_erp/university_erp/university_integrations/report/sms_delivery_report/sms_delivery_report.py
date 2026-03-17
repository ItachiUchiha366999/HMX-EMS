# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data, filters)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("SMS Log ID"),
            "fieldtype": "Link",
            "options": "SMS Log",
            "width": 120
        },
        {
            "fieldname": "recipient",
            "label": _("Recipient"),
            "fieldtype": "Data",
            "width": 130
        },
        {
            "fieldname": "message",
            "label": _("Message"),
            "fieldtype": "Data",
            "width": 250
        },
        {
            "fieldname": "sms_gateway",
            "label": _("Gateway"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "sent_on",
            "label": _("Sent On"),
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "message_id",
            "label": _("Message ID"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "error_message",
            "label": _("Error"),
            "fieldtype": "Data",
            "width": 200
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            name,
            recipient,
            SUBSTRING(message, 1, 100) as message,
            sms_gateway,
            sent_on,
            status,
            message_id,
            error_message
        FROM `tabSMS Log`
        WHERE 1=1 {conditions}
        ORDER BY sent_on DESC
    """.format(conditions=conditions), filters, as_dict=1)

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND DATE(sent_on) >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND DATE(sent_on) <= %(to_date)s"

    if filters.get("status"):
        conditions += " AND status = %(status)s"

    if filters.get("sms_gateway"):
        conditions += " AND sms_gateway = %(sms_gateway)s"

    if filters.get("recipient"):
        conditions += " AND recipient LIKE %(recipient)s"
        filters["recipient"] = f"%{filters['recipient']}%"

    return conditions


def get_chart(data, filters):
    if not data:
        return None

    # Group by status
    status_counts = {}
    for row in data:
        status = row.get("status") or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [
                {
                    "name": _("SMS Count"),
                    "values": list(status_counts.values())
                }
            ]
        },
        "type": "pie",
        "colors": ["#28a745", "#ffc107", "#17a2b8", "#dc3545"]
    }


def get_summary(data):
    if not data:
        return []

    total = len(data)
    sent = len([d for d in data if d.get("status") == "Sent"])
    delivered = len([d for d in data if d.get("status") == "Delivered"])
    failed = len([d for d in data if d.get("status") == "Failed"])
    queued = len([d for d in data if d.get("status") == "Queued"])

    delivery_rate = (delivered / total * 100) if total > 0 else 0

    return [
        {
            "value": total,
            "label": _("Total SMS"),
            "datatype": "Int"
        },
        {
            "value": sent,
            "label": _("Sent"),
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": delivered,
            "label": _("Delivered"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": failed,
            "label": _("Failed"),
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": queued,
            "label": _("Queued"),
            "datatype": "Int",
            "indicator": "orange"
        },
        {
            "value": flt(delivery_rate, 2),
            "label": _("Delivery Rate (%)"),
            "datatype": "Percent",
            "indicator": "green" if delivery_rate >= 90 else "orange"
        }
    ]
