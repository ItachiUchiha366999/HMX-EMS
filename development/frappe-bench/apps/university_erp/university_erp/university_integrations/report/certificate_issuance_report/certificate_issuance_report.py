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
            "label": _("Request ID"),
            "fieldtype": "Link",
            "options": "Certificate Request",
            "width": 130
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
            "width": 150
        },
        {
            "fieldname": "program",
            "label": _("Program"),
            "fieldtype": "Link",
            "options": "Program",
            "width": 120
        },
        {
            "fieldname": "certificate_template",
            "label": _("Certificate Type"),
            "fieldtype": "Link",
            "options": "Certificate Template",
            "width": 150
        },
        {
            "fieldname": "request_date",
            "label": _("Request Date"),
            "fieldtype": "Date",
            "width": 110
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "certificate_number",
            "label": _("Certificate No."),
            "fieldtype": "Data",
            "width": 140
        },
        {
            "fieldname": "issue_date",
            "label": _("Issue Date"),
            "fieldtype": "Date",
            "width": 110
        },
        {
            "fieldname": "approved_by",
            "label": _("Approved By"),
            "fieldtype": "Link",
            "options": "User",
            "width": 120
        },
        {
            "fieldname": "purpose",
            "label": _("Purpose"),
            "fieldtype": "Data",
            "width": 150
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            cr.name,
            cr.student,
            cr.student_name,
            cr.program,
            cr.certificate_template,
            cr.request_date,
            cr.status,
            cr.certificate_number,
            cr.issue_date,
            cr.approved_by,
            SUBSTRING(cr.purpose, 1, 50) as purpose
        FROM `tabCertificate Request` cr
        WHERE 1=1 {conditions}
        ORDER BY cr.request_date DESC
    """.format(conditions=conditions), filters, as_dict=1)

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND cr.request_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND cr.request_date <= %(to_date)s"

    if filters.get("status"):
        conditions += " AND cr.status = %(status)s"

    if filters.get("certificate_template"):
        conditions += " AND cr.certificate_template = %(certificate_template)s"

    if filters.get("student"):
        conditions += " AND cr.student = %(student)s"

    if filters.get("program"):
        conditions += " AND cr.program = %(program)s"

    return conditions


def get_chart(data, filters):
    if not data:
        return None

    # Group by certificate type
    type_counts = {}
    for row in data:
        cert_type = row.get("certificate_template") or "Unknown"
        type_counts[cert_type] = type_counts.get(cert_type, 0) + 1

    # Sort by count and take top 10
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "data": {
            "labels": [t[0] for t in sorted_types],
            "datasets": [
                {
                    "name": _("Certificates"),
                    "values": [t[1] for t in sorted_types]
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data):
    if not data:
        return []

    total = len(data)
    pending = len([d for d in data if d.get("status") == "Pending"])
    approved = len([d for d in data if d.get("status") == "Approved"])
    generated = len([d for d in data if d.get("status") == "Generated"])
    issued = len([d for d in data if d.get("status") == "Issued"])
    rejected = len([d for d in data if d.get("status") == "Rejected"])

    completion_rate = ((generated + issued) / total * 100) if total > 0 else 0

    return [
        {
            "value": total,
            "label": _("Total Requests"),
            "datatype": "Int"
        },
        {
            "value": pending,
            "label": _("Pending"),
            "datatype": "Int",
            "indicator": "orange"
        },
        {
            "value": approved,
            "label": _("Approved"),
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": generated,
            "label": _("Generated"),
            "datatype": "Int",
            "indicator": "purple"
        },
        {
            "value": issued,
            "label": _("Issued"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": rejected,
            "label": _("Rejected"),
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": flt(completion_rate, 2),
            "label": _("Completion Rate (%)"),
            "datatype": "Percent",
            "indicator": "green" if completion_rate >= 80 else "orange"
        }
    ]
