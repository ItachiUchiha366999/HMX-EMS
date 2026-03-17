# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, date_diff


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "equipment",
            "label": _("Equipment"),
            "fieldtype": "Link",
            "options": "Lab Equipment",
            "width": 120
        },
        {
            "fieldname": "equipment_name",
            "label": _("Equipment Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "lab",
            "label": _("Laboratory"),
            "fieldtype": "Link",
            "options": "University Laboratory",
            "width": 120
        },
        {
            "fieldname": "equipment_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "total_bookings",
            "label": _("Total Bookings"),
            "fieldtype": "Int",
            "width": 110
        },
        {
            "fieldname": "completed_bookings",
            "label": _("Completed"),
            "fieldtype": "Int",
            "width": 90
        },
        {
            "fieldname": "total_hours",
            "label": _("Total Hours"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "avg_hours_per_booking",
            "label": _("Avg Hours/Booking"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "utilization_percent",
            "label": _("Utilization %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "status",
            "label": _("Current Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    # Get equipment with booking statistics
    data = frappe.db.sql("""
        SELECT
            le.name as equipment,
            le.equipment_name,
            le.lab,
            le.equipment_type,
            le.status,
            COUNT(leb.name) as total_bookings,
            SUM(CASE WHEN leb.status = 'Completed' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(COALESCE(leb.duration_hours, 0)) as total_hours
        FROM `tabLab Equipment` le
        LEFT JOIN `tabLab Equipment Booking` leb ON leb.equipment = le.name
            AND leb.docstatus < 2
            {date_conditions}
        WHERE 1=1
        {conditions}
        GROUP BY le.name
        ORDER BY total_hours DESC
    """.format(
        conditions=conditions,
        date_conditions=get_date_conditions(filters)
    ), {
        "lab": filters.get("lab"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date")
    }, as_dict=True)

    # Calculate utilization percentage
    # Assuming 8 working hours per day
    if filters.get("from_date") and filters.get("to_date"):
        total_days = date_diff(filters.get("to_date"), filters.get("from_date")) + 1
        max_hours = total_days * 8  # 8 hours per day

        for row in data:
            row["avg_hours_per_booking"] = (
                flt(row["total_hours"]) / row["total_bookings"]
                if row["total_bookings"] else 0
            )
            row["utilization_percent"] = (
                (flt(row["total_hours"]) / max_hours) * 100
                if max_hours > 0 else 0
            )
    else:
        for row in data:
            row["avg_hours_per_booking"] = (
                flt(row["total_hours"]) / row["total_bookings"]
                if row["total_bookings"] else 0
            )
            row["utilization_percent"] = 0

    return data


def get_conditions(filters):
    conditions = []

    if filters.get("lab"):
        conditions.append("AND le.lab = %(lab)s")

    return " ".join(conditions)


def get_date_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("AND leb.booking_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("AND leb.booking_date <= %(to_date)s")

    return " ".join(conditions)
