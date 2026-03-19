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
            "fieldname": "room",
            "label": _("Room"),
            "fieldtype": "Link",
            "options": "Hostel Room",
            "width": 120
        },
        {
            "fieldname": "building_name",
            "label": _("Building"),
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
            "fieldname": "floor",
            "label": _("Floor"),
            "fieldtype": "Int",
            "width": 60
        },
        {
            "fieldname": "room_type",
            "label": _("Room Type"),
            "fieldtype": "Data",
            "width": 90
        },
        {
            "fieldname": "capacity",
            "label": _("Capacity"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "occupied_beds",
            "label": _("Occupied"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "available_beds",
            "label": _("Available"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "rent_per_month",
            "label": _("Rent/Month"),
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "fieldname": "amenities",
            "label": _("Amenities"),
            "fieldtype": "Data",
            "width": 150
        }
    ]


def get_data(filters):
    conditions = []
    values = []

    if filters.get("hostel_building"):
        conditions.append("hr.hostel_building = %s")
        values.append(filters.get("hostel_building"))

    if filters.get("hostel_type"):
        conditions.append("hb.hostel_type = %s")
        values.append(filters.get("hostel_type"))

    if filters.get("room_type"):
        conditions.append("hr.room_type = %s")
        values.append(filters.get("room_type"))

    if filters.get("status"):
        conditions.append("hr.status = %s")
        values.append(filters.get("status"))

    if filters.get("only_available"):
        conditions.append("hr.status != 'Under Maintenance'")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    having_clause = "HAVING available_beds > 0" if filters.get("only_available") else ""

    data = frappe.db.sql("""
        SELECT
            hr.name as room,
            hr.room_number,
            hb.building_name,
            hb.hostel_type,
            hr.floor,
            hr.room_type,
            hr.capacity,
            COUNT(ha.name) as occupied_beds,
            (hr.capacity - COUNT(ha.name)) as available_beds,
            hr.status,
            hr.rent_per_month,
            hr.has_attached_bathroom,
            hr.has_ac,
            hr.has_balcony,
            hr.has_study_table,
            hr.has_wardrobe,
            hr.has_hot_water
        FROM `tabHostel Room` hr
        JOIN `tabHostel Building` hb ON hr.hostel_building = hb.name
        LEFT JOIN `tabHostel Allocation` ha
            ON ha.room = hr.name AND ha.status = 'Active' AND ha.docstatus = 1
        {where_clause}
        GROUP BY hr.name
        {having_clause}
        ORDER BY hb.building_name, hr.floor, hr.room_number
    """.format(having_clause=having_clause, where_clause=where_clause), values, as_dict=True)

    # Format amenities
    for row in data:
        amenities = []
        if row.has_attached_bathroom:
            amenities.append("Bath")
        if row.has_ac:
            amenities.append("AC")
        if row.has_balcony:
            amenities.append("Balcony")
        if row.has_hot_water:
            amenities.append("Hot Water")

        row["amenities"] = ", ".join(amenities) if amenities else "-"

    return data


def get_chart(data):
    if not data:
        return None

    # Group by status
    status_counts = {}
    for row in data:
        status = row.status
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [{"values": list(status_counts.values())}]
        },
        "type": "pie",
        "colors": ["#98d85b", "#ffa00a", "#fc4f51", "#7575ff"]
    }


def get_summary(data):
    if not data:
        return []

    total_rooms = len(data)
    total_capacity = sum(d.capacity or 0 for d in data)
    total_available = sum(d.available_beds or 0 for d in data)
    available_rooms = sum(1 for d in data if d.available_beds > 0 and d.status != "Under Maintenance")

    return [
        {
            "value": total_rooms,
            "label": _("Total Rooms"),
            "datatype": "Int"
        },
        {
            "value": available_rooms,
            "label": _("Rooms with Vacancy"),
            "datatype": "Int",
            "indicator": "green" if available_rooms > 0 else "red"
        },
        {
            "value": total_capacity,
            "label": _("Total Beds"),
            "datatype": "Int"
        },
        {
            "value": total_available,
            "label": _("Available Beds"),
            "datatype": "Int",
            "indicator": "green" if total_available > 0 else "red"
        }
    ]
