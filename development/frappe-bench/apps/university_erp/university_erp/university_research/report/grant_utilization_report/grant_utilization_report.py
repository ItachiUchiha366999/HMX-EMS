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
        {"fieldname": "name", "label": _("Grant"), "fieldtype": "Link", "options": "Research Grant", "width": 120},
        {"fieldname": "grant_title", "label": _("Title"), "fieldtype": "Data", "width": 200},
        {"fieldname": "funding_agency", "label": _("Agency"), "fieldtype": "Data", "width": 120},
        {"fieldname": "grant_type", "label": _("Type"), "fieldtype": "Data", "width": 100},
        {"fieldname": "sanctioned_amount", "label": _("Sanctioned"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "disbursed_amount", "label": _("Disbursed"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "utilized_amount", "label": _("Utilized"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "balance", "label": _("Balance"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "utilization_percent", "label": _("Util %"), "fieldtype": "Percent", "width": 80},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100}
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("funding_agency"):
        conditions += " AND funding_agency = %(funding_agency)s"
        values["funding_agency"] = filters.get("funding_agency")

    if filters.get("grant_type"):
        conditions += " AND grant_type = %(grant_type)s"
        values["grant_type"] = filters.get("grant_type")

    if filters.get("status"):
        conditions += " AND status = %(status)s"
        values["status"] = filters.get("status")

    data = frappe.db.sql("""
        SELECT
            name,
            grant_title,
            funding_agency,
            grant_type,
            sanctioned_amount,
            disbursed_amount,
            utilized_amount,
            status
        FROM `tabResearch Grant`
        WHERE docstatus < 2
        {conditions}
        ORDER BY sanctioned_amount DESC
    """.format(conditions=conditions), values, as_dict=True)

    for row in data:
        row["balance"] = (row.get("disbursed_amount") or 0) - (row.get("utilized_amount") or 0)
        disbursed = row.get("disbursed_amount") or 0
        utilized = row.get("utilized_amount") or 0
        row["utilization_percent"] = (utilized / disbursed * 100) if disbursed else 0

    return data


def get_chart(data):
    if not data:
        return None

    # By funding agency
    agency_amounts = {}
    for row in data:
        agency = row.get("funding_agency") or "Other"
        agency_amounts[agency] = agency_amounts.get(agency, 0) + (row.get("sanctioned_amount") or 0)

    # Get top 5 agencies
    sorted_agencies = sorted(agency_amounts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "data": {
            "labels": [a[0] for a in sorted_agencies],
            "datasets": [{"name": _("Amount"), "values": [a[1] for a in sorted_agencies]}]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data):
    if not data:
        return []

    total_grants = len(data)
    total_sanctioned = sum(d.get("sanctioned_amount") or 0 for d in data)
    total_disbursed = sum(d.get("disbursed_amount") or 0 for d in data)
    total_utilized = sum(d.get("utilized_amount") or 0 for d in data)
    overall_util = (total_utilized / total_disbursed * 100) if total_disbursed else 0

    return [
        {"value": total_grants, "label": _("Total Grants"), "datatype": "Int"},
        {"value": total_sanctioned, "label": _("Total Sanctioned"), "datatype": "Currency"},
        {"value": total_disbursed, "label": _("Total Disbursed"), "datatype": "Currency"},
        {"value": round(overall_util, 2), "label": _("Utilization %"), "datatype": "Percent"}
    ]
