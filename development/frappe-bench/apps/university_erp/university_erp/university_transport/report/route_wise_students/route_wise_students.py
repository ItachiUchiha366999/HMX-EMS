# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data, filters)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "route", "label": _("Route"), "fieldtype": "Link", "options": "Transport Route", "width": 150},
        {"fieldname": "route_name", "label": _("Route Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "student", "label": _("Student"), "fieldtype": "Link", "options": "Student", "width": 120},
        {"fieldname": "student_name", "label": _("Student Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "program", "label": _("Program"), "fieldtype": "Link", "options": "Program", "width": 120},
        {"fieldname": "pickup_stop", "label": _("Pickup Stop"), "fieldtype": "Data", "width": 120},
        {"fieldname": "pickup_time", "label": _("Pickup Time"), "fieldtype": "Time", "width": 100},
        {"fieldname": "monthly_fare", "label": _("Monthly Fare"), "fieldtype": "Currency", "width": 100}
    ]


def get_data(filters):
    conditions = ["ta.status = 'Active'", "ta.docstatus = 1"]
    values = []

    if filters.get("route"):
        conditions.append("ta.route = %s")
        values.append(filters.get("route"))

    if filters.get("academic_year"):
        conditions.append("ta.academic_year = %s")
        values.append(filters.get("academic_year"))

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(f"""
        SELECT
            ta.route,
            tr.route_name,
            ta.student,
            ta.student_name,
            ta.program,
            ta.pickup_stop,
            ta.pickup_time,
            ta.monthly_fare
        FROM `tabTransport Allocation` ta
        JOIN `tabTransport Route` tr ON ta.route = tr.name
        WHERE {where_clause}
        ORDER BY tr.route_name, ta.pickup_time
    """, values, as_dict=True)


def get_chart(data):
    if not data:
        return None

    # Group by route
    route_counts = {}
    for row in data:
        route = row.route_name
        route_counts[route] = route_counts.get(route, 0) + 1

    return {
        "data": {
            "labels": list(route_counts.keys()),
            "datasets": [{"values": list(route_counts.values())}]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data, filters):
    if not data:
        return []

    total_students = len(data)
    total_fare = sum(d.monthly_fare or 0 for d in data)
    unique_routes = len(set(d.route for d in data))

    return [
        {"value": total_students, "label": _("Total Students"), "datatype": "Int"},
        {"value": unique_routes, "label": _("Routes"), "datatype": "Int"},
        {"value": total_fare, "label": _("Monthly Revenue"), "datatype": "Currency"}
    ]
