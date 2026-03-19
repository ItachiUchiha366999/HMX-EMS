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
            "label": _("ID"),
            "fieldtype": "Link",
            "options": "Hostel Visitor",
            "width": 100
        },
        {
            "fieldname": "visit_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "visitor_name",
            "label": _("Visitor Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "visitor_mobile",
            "label": _("Mobile"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "relationship",
            "label": _("Relationship"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "student_name",
            "label": _("Student"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "building_name",
            "label": _("Building"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "check_in_time",
            "label": _("Check In"),
            "fieldtype": "Time",
            "width": 80
        },
        {
            "fieldname": "check_out_time",
            "label": _("Check Out"),
            "fieldtype": "Time",
            "width": 80
        },
        {
            "fieldname": "duration",
            "label": _("Duration"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "purpose",
            "label": _("Purpose"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = ["1=1"]
    values = {}

    if filters.get("building"):
        conditions.append("building = %(building)s")
        values["building"] = filters.get("building")

    if filters.get("student"):
        conditions.append("student = %(student)s")
        values["student"] = filters.get("student")

    if filters.get("relationship"):
        conditions.append("relationship = %(relationship)s")
        values["relationship"] = filters.get("relationship")

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters.get("status")

    if filters.get("from_date"):
        conditions.append("visit_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("visit_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql("""
        SELECT
            name,
            visit_date,
            visitor_name,
            visitor_mobile,
            relationship,
            student,
            student_name,
            building,
            building_name,
            check_in_time,
            check_out_time,
            duration,
            purpose,
            status
        FROM `tabHostel Visitor`
        WHERE {where_clause}
        ORDER BY visit_date DESC, check_in_time DESC
    """.format(where_clause=where_clause), values, as_dict=True)

    return data


def get_chart(filters):
    conditions = ["1=1"]
    values = {}

    if filters.get("building"):
        conditions.append("building = %(building)s")
        values["building"] = filters.get("building")

    if filters.get("from_date"):
        conditions.append("visit_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("visit_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = " AND ".join(conditions)

    # By relationship chart
    rel_data = frappe.db.sql("""
        SELECT
            relationship as label,
            COUNT(*) as value
        FROM `tabHostel Visitor`
        WHERE {where_clause}
        GROUP BY relationship
        ORDER BY value DESC
    """.format(where_clause=where_clause), values, as_dict=True)

    if rel_data:
        return {
            "data": {
                "labels": [d.label for d in rel_data],
                "datasets": [{"values": [d.value for d in rel_data]}]
            },
            "type": "pie",
            "colors": ["#5e64ff", "#ff5858", "#ffc107", "#28a745", "#17a2b8", "#6c757d"],
            "height": 280
        }

    return None


def get_summary(filters):
    conditions = ["1=1"]
    values = {}

    if filters.get("building"):
        conditions.append("building = %(building)s")
        values["building"] = filters.get("building")

    if filters.get("from_date"):
        conditions.append("visit_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("visit_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = " AND ".join(conditions)

    stats = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Checked In' THEN 1 ELSE 0 END) as checked_in,
            SUM(CASE WHEN status = 'Checked Out' THEN 1 ELSE 0 END) as checked_out,
            SUM(CASE WHEN status = 'Denied' THEN 1 ELSE 0 END) as denied,
            COUNT(DISTINCT student) as unique_students,
            COUNT(DISTINCT visitor_mobile) as unique_visitors
        FROM `tabHostel Visitor`
        WHERE {where_clause}
    """.format(where_clause=where_clause), values, as_dict=True)[0]

    return [
        {
            "value": stats.total or 0,
            "label": _("Total Visits"),
            "datatype": "Int"
        },
        {
            "value": stats.checked_in or 0,
            "label": _("Currently In"),
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": stats.checked_out or 0,
            "label": _("Checked Out"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": stats.denied or 0,
            "label": _("Denied"),
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": stats.unique_students or 0,
            "label": _("Students Visited"),
            "datatype": "Int"
        },
        {
            "value": stats.unique_visitors or 0,
            "label": _("Unique Visitors"),
            "datatype": "Int"
        }
    ]
