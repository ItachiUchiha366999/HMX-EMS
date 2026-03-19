# Copyright (c) 2026, University ERP and contributors
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
            "fieldname": "building",
            "label": _("Building"),
            "fieldtype": "Link",
            "options": "Hostel Building",
            "width": 150
        },
        {
            "fieldname": "building_name",
            "label": _("Building Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "hostel_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "warden",
            "label": _("Warden"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "fieldname": "total_rooms",
            "label": _("Rooms"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "total_capacity",
            "label": _("Capacity"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "occupied",
            "label": _("Occupied"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "available",
            "label": _("Available"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "occupancy_rate",
            "label": _("Occupancy %"),
            "fieldtype": "Percent",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = []
    values = []

    if filters.get("hostel_type"):
        conditions.append("hb.hostel_type = %s")
        values.append(filters.get("hostel_type"))

    if filters.get("building"):
        conditions.append("hb.name = %s")
        values.append(filters.get("building"))

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    return frappe.db.sql("""
        SELECT
            hb.name as building,
            hb.building_name,
            hb.hostel_type,
            hb.warden,
            COUNT(DISTINCT hr.name) as total_rooms,
            COALESCE(SUM(hr.capacity), 0) as total_capacity,
            COUNT(ha.name) as occupied,
            (COALESCE(SUM(hr.capacity), 0) - COUNT(ha.name)) as available,
            CASE
                WHEN SUM(hr.capacity) > 0
                THEN ROUND(COUNT(ha.name) / SUM(hr.capacity) * 100, 2)
                ELSE 0
            END as occupancy_rate
        FROM `tabHostel Building` hb
        LEFT JOIN `tabHostel Room` hr
            ON hr.hostel_building = hb.name AND hr.status != 'Under Maintenance'
        LEFT JOIN `tabHostel Allocation` ha
            ON ha.room = hr.name AND ha.status = 'Active' AND ha.docstatus = 1
        {where_clause}
        GROUP BY hb.name
        ORDER BY hb.building_name
    """.format(where_clause=where_clause), values, as_dict=True)


def get_chart(data):
    if not data:
        return None

    labels = [d.building_name for d in data]
    occupied = [d.occupied or 0 for d in data]
    available = [d.available or 0 for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Occupied"), "values": occupied},
                {"name": _("Available"), "values": available}
            ]
        },
        "type": "bar",
        "colors": ["#fc4f51", "#98d85b"],
        "barOptions": {"stacked": 1}
    }


def get_summary(data):
    if not data:
        return []

    total_capacity = sum(d.total_capacity or 0 for d in data)
    total_occupied = sum(d.occupied or 0 for d in data)
    total_available = sum(d.available or 0 for d in data)
    avg_occupancy = (total_occupied / total_capacity * 100) if total_capacity else 0

    return [
        {
            "value": len(data),
            "label": _("Total Buildings"),
            "datatype": "Int"
        },
        {
            "value": total_capacity,
            "label": _("Total Capacity"),
            "datatype": "Int"
        },
        {
            "value": total_occupied,
            "label": _("Total Occupied"),
            "datatype": "Int",
            "indicator": "red" if total_occupied > total_capacity * 0.9 else "green"
        },
        {
            "value": total_available,
            "label": _("Total Available"),
            "datatype": "Int",
            "indicator": "green" if total_available > 0 else "red"
        },
        {
            "value": round(avg_occupancy, 2),
            "label": _("Avg Occupancy %"),
            "datatype": "Percent"
        }
    ]
