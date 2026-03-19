# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "label": _("Category"),
            "fieldname": "category",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Total"),
            "fieldname": "total",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Open"),
            "fieldname": "open",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Resolved"),
            "fieldname": "resolved",
            "fieldtype": "Int",
            "width": 90
        },
        {
            "label": _("Avg Days"),
            "fieldname": "avg_days",
            "fieldtype": "Float",
            "width": 90,
            "precision": 1
        },
        {
            "label": _("SLA Compliance %"),
            "fieldname": "sla_compliance",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": _("Avg Satisfaction"),
            "fieldname": "satisfaction",
            "fieldtype": "Float",
            "width": 110,
            "precision": 1
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            category,
            COUNT(*) as total,
            SUM(CASE WHEN status NOT IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as open,
            SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved,
            AVG(CASE WHEN resolution_date IS NOT NULL
                THEN TIMESTAMPDIFF(DAY, creation, resolution_date) END) as avg_days,
            AVG(CASE WHEN status IN ('Resolved', 'Closed') AND sla_status != 'Breached'
                THEN 100 ELSE 0 END) as sla_compliance,
            AVG(satisfaction_rating) as satisfaction
        FROM `tabGrievance`
        WHERE 1=1 {conditions}
        GROUP BY category
        ORDER BY total DESC
    """.format(conditions=conditions), as_dict=True)

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += f" AND creation >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND creation <= '{filters.get('to_date')}'"
    if filters.get("category"):
        conditions += f" AND category = '{filters.get('category')}'"
    if filters.get("grievance_type"):
        conditions += f" AND grievance_type = '{filters.get('grievance_type')}'"
    if filters.get("status"):
        conditions += f" AND status = '{filters.get('status')}'"

    return conditions


def get_chart(data):
    if not data:
        return None

    return {
        "data": {
            "labels": [d.category for d in data],
            "datasets": [
                {
                    "name": _("Total"),
                    "values": [d.total for d in data]
                },
                {
                    "name": _("Open"),
                    "values": [d.open for d in data]
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#ff5858"]
    }


def get_summary(data):
    if not data:
        return []

    total = sum(d.total for d in data)
    open_count = sum(d.open for d in data)
    satisfaction_scores = [d.satisfaction for d in data if d.satisfaction]
    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0

    return [
        {
            "label": _("Total Grievances"),
            "value": total,
            "indicator": "Blue"
        },
        {
            "label": _("Open"),
            "value": open_count,
            "indicator": "Orange" if open_count > 10 else "Green"
        },
        {
            "label": _("Avg Satisfaction"),
            "value": f"{avg_satisfaction:.1f}/5",
            "indicator": "Green" if avg_satisfaction >= 4 else "Red"
        }
    ]
