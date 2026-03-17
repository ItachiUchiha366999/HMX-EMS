# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(filters)
    summary = get_summary(filters)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("Request ID"),
            "fieldtype": "Link",
            "options": "Hostel Maintenance Request",
            "width": 120
        },
        {
            "fieldname": "request_date",
            "label": _("Request Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "building_name",
            "label": _("Building"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "room_number",
            "label": _("Room"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "request_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "priority",
            "label": _("Priority"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "subject",
            "label": _("Subject"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "assigned_to_name",
            "label": _("Assigned To"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "actual_completion",
            "label": _("Completed On"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "days_taken",
            "label": _("Days Taken"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "cost_incurred",
            "label": _("Cost"),
            "fieldtype": "Currency",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = ["mr.docstatus = 1"]
    values = {}

    if filters.get("building"):
        conditions.append("mr.building = %(building)s")
        values["building"] = filters.get("building")

    if filters.get("request_type"):
        conditions.append("mr.request_type = %(request_type)s")
        values["request_type"] = filters.get("request_type")

    if filters.get("priority"):
        conditions.append("mr.priority = %(priority)s")
        values["priority"] = filters.get("priority")

    if filters.get("status"):
        conditions.append("mr.status = %(status)s")
        values["status"] = filters.get("status")

    if filters.get("from_date"):
        conditions.append("mr.request_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("mr.request_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql(f"""
        SELECT
            mr.name,
            mr.request_date,
            mr.building,
            mr.building_name,
            mr.room,
            mr.room_number,
            mr.request_type,
            mr.priority,
            mr.subject,
            mr.status,
            mr.assigned_to,
            e.employee_name as assigned_to_name,
            mr.actual_completion,
            CASE
                WHEN mr.actual_completion IS NOT NULL
                THEN DATEDIFF(mr.actual_completion, mr.request_date)
                ELSE NULL
            END as days_taken,
            mr.cost_incurred
        FROM `tabHostel Maintenance Request` mr
        LEFT JOIN `tabEmployee` e ON mr.assigned_to = e.name
        WHERE {where_clause}
        ORDER BY
            FIELD(mr.priority, 'Urgent', 'High', 'Medium', 'Low'),
            mr.request_date DESC
    """, values, as_dict=True)

    return data


def get_chart(filters):
    conditions = ["docstatus = 1"]
    values = {}

    if filters.get("building"):
        conditions.append("building = %(building)s")
        values["building"] = filters.get("building")

    if filters.get("from_date"):
        conditions.append("request_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("request_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = " AND ".join(conditions)

    # By type chart
    type_data = frappe.db.sql(f"""
        SELECT
            request_type as label,
            COUNT(*) as value
        FROM `tabHostel Maintenance Request`
        WHERE {where_clause}
        GROUP BY request_type
        ORDER BY value DESC
    """, values, as_dict=True)

    if type_data:
        return {
            "data": {
                "labels": [d.label for d in type_data],
                "datasets": [{"values": [d.value for d in type_data]}]
            },
            "type": "bar",
            "colors": ["#5e64ff"],
            "height": 280
        }

    return None


def get_summary(filters):
    conditions = ["docstatus = 1"]
    values = {}

    if filters.get("building"):
        conditions.append("building = %(building)s")
        values["building"] = filters.get("building")

    if filters.get("from_date"):
        conditions.append("request_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("request_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = " AND ".join(conditions)

    stats = frappe.db.sql(f"""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_count,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(COALESCE(cost_incurred, 0)) as total_cost,
            AVG(CASE
                WHEN actual_completion IS NOT NULL
                THEN DATEDIFF(actual_completion, request_date)
            END) as avg_days
        FROM `tabHostel Maintenance Request`
        WHERE {where_clause}
    """, values, as_dict=True)[0]

    return [
        {
            "value": stats.total or 0,
            "label": _("Total Requests"),
            "datatype": "Int"
        },
        {
            "value": stats.completed or 0,
            "label": _("Completed"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": stats.open_count or 0,
            "label": _("Open"),
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": stats.in_progress or 0,
            "label": _("In Progress"),
            "datatype": "Int",
            "indicator": "orange"
        },
        {
            "value": round(stats.avg_days or 0, 1),
            "label": _("Avg Resolution Days"),
            "datatype": "Float"
        },
        {
            "value": stats.total_cost or 0,
            "label": _("Total Cost"),
            "datatype": "Currency"
        }
    ]
