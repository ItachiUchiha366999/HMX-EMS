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
        {"fieldname": "vehicle", "label": _("Vehicle"), "fieldtype": "Link", "options": "Transport Vehicle", "width": 120},
        {"fieldname": "vehicle_type", "label": _("Type"), "fieldtype": "Data", "width": 90},
        {"fieldname": "seating_capacity", "label": _("Capacity"), "fieldtype": "Int", "width": 80},
        {"fieldname": "route", "label": _("Assigned Route"), "fieldtype": "Link", "options": "Transport Route", "width": 150},
        {"fieldname": "students_allocated", "label": _("Students"), "fieldtype": "Int", "width": 80},
        {"fieldname": "utilization", "label": _("Utilization %"), "fieldtype": "Percent", "width": 100},
        {"fieldname": "trips_count", "label": _("Trips"), "fieldtype": "Int", "width": 80},
        {"fieldname": "total_distance", "label": _("Distance (km)"), "fieldtype": "Float", "width": 100},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100}
    ]


def get_data(filters):
    conditions = []
    values = []

    if filters.get("vehicle_type"):
        conditions.append("tv.vehicle_type = %s")
        values.append(filters.get("vehicle_type"))

    if filters.get("status"):
        conditions.append("tv.status = %s")
        values.append(filters.get("status"))

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    vehicles = frappe.db.sql("""
        SELECT
            tv.name as vehicle,
            tv.vehicle_type,
            tv.seating_capacity,
            tv.status,
            tr.name as route,
            tr.route_name
        FROM `tabTransport Vehicle` tv
        LEFT JOIN `tabTransport Route` tr ON tr.assigned_vehicle = tv.name
        {where_clause}
        ORDER BY tv.vehicle_type, tv.name
    """.format(where_clause=where_clause), values, as_dict=True)

    # Add student count and trip stats for each vehicle
    for vehicle in vehicles:
        # Count students allocated via route
        if vehicle.route:
            vehicle["students_allocated"] = frappe.db.count(
                "Transport Allocation",
                {"route": vehicle.route, "status": "Active", "docstatus": 1}
            )
        else:
            vehicle["students_allocated"] = 0

        # Calculate utilization
        if vehicle.seating_capacity > 0:
            vehicle["utilization"] = round(
                vehicle["students_allocated"] / vehicle.seating_capacity * 100, 2
            )
        else:
            vehicle["utilization"] = 0

        # Get trip statistics
        trip_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as trips_count,
                COALESCE(SUM(distance_covered), 0) as total_distance
            FROM `tabTransport Trip Log`
            WHERE vehicle = %s
            AND trip_date BETWEEN %s AND %s
        """, (vehicle.vehicle,
              filters.get("from_date") or "2000-01-01",
              filters.get("to_date") or frappe.utils.nowdate()), as_dict=True)[0]

        vehicle["trips_count"] = trip_stats.trips_count
        vehicle["total_distance"] = trip_stats.total_distance

    return vehicles


def get_chart(data):
    if not data:
        return None

    labels = [d.vehicle for d in data[:10]]  # Top 10
    utilization = [d.utilization or 0 for d in data[:10]]

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Utilization %"), "values": utilization}]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data):
    if not data:
        return []

    total_vehicles = len(data)
    active_vehicles = sum(1 for d in data if d.status == "Available" or d.status == "In Service")
    avg_utilization = sum(d.utilization or 0 for d in data) / total_vehicles if total_vehicles else 0
    total_students = sum(d.students_allocated or 0 for d in data)

    return [
        {"value": total_vehicles, "label": _("Total Vehicles"), "datatype": "Int"},
        {"value": active_vehicles, "label": _("Active Vehicles"), "datatype": "Int"},
        {"value": round(avg_utilization, 2), "label": _("Avg Utilization %"), "datatype": "Percent"},
        {"value": total_students, "label": _("Total Students"), "datatype": "Int"}
    ]
