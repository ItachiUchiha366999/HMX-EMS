# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns(filters):
    return [
        {
            "fieldname": "program",
            "label": _("Program"),
            "fieldtype": "Link",
            "options": "Program",
            "width": 150
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "academic_year",
            "label": _("Academic Year"),
            "fieldtype": "Link",
            "options": "Academic Year",
            "width": 120
        },
        {
            "fieldname": "total_pos",
            "label": _("Total POs"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "pos_achieved",
            "label": _("POs Met"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "total_psos",
            "label": _("Total PSOs"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "psos_achieved",
            "label": _("PSOs Met"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "overall_attainment",
            "label": _("Attainment"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "nba_compliance",
            "label": _("NBA Score"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "naac_compliance",
            "label": _("NAAC Score"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    data = []

    attainment_filters = {"docstatus": 1}
    if filters.get("program"):
        attainment_filters["program"] = filters.get("program")
    if filters.get("academic_year"):
        attainment_filters["academic_year"] = filters.get("academic_year")
    if filters.get("department"):
        attainment_filters["department"] = filters.get("department")

    attainments = frappe.get_all(
        "PO Attainment",
        filters=attainment_filters,
        fields=[
            "name", "program", "program_name", "department", "academic_year",
            "total_pos", "pos_achieved", "total_psos", "psos_achieved",
            "overall_attainment", "nba_compliance_score", "naac_compliance_score"
        ],
        order_by="program, academic_year desc"
    )

    for att in attainments:
        # Determine status based on compliance
        if att.nba_compliance_score >= 80 and att.naac_compliance_score >= 80:
            status = "Excellent"
        elif att.nba_compliance_score >= 60 and att.naac_compliance_score >= 60:
            status = "Good"
        elif att.nba_compliance_score >= 40:
            status = "Needs Improvement"
        else:
            status = "Critical"

        data.append({
            "program": att.program,
            "department": att.department,
            "academic_year": att.academic_year,
            "total_pos": att.total_pos,
            "pos_achieved": att.pos_achieved,
            "total_psos": att.total_psos,
            "psos_achieved": att.psos_achieved,
            "overall_attainment": att.overall_attainment,
            "nba_compliance": att.nba_compliance_score,
            "naac_compliance": att.naac_compliance_score,
            "status": status
        })

    return data


def get_chart(data):
    if not data:
        return None

    labels = [f"{d['program']} ({d['academic_year']})" for d in data]
    nba_values = [d["nba_compliance"] for d in data]
    naac_values = [d["naac_compliance"] for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "NBA Compliance",
                    "values": nba_values
                },
                {
                    "name": "NAAC Compliance",
                    "values": naac_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#28a745"]
    }


def get_summary(data):
    if not data:
        return []

    total_programs = len(data)
    excellent = sum(1 for d in data if d["status"] == "Excellent")
    good = sum(1 for d in data if d["status"] == "Good")
    needs_improvement = sum(1 for d in data if d["status"] == "Needs Improvement")
    critical = sum(1 for d in data if d["status"] == "Critical")

    avg_nba = sum(d["nba_compliance"] for d in data) / total_programs if total_programs > 0 else 0
    avg_naac = sum(d["naac_compliance"] for d in data) / total_programs if total_programs > 0 else 0

    return [
        {
            "value": total_programs,
            "label": _("Total Programs"),
            "datatype": "Int"
        },
        {
            "value": excellent,
            "label": _("Excellent"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": good,
            "label": _("Good"),
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": needs_improvement + critical,
            "label": _("Need Attention"),
            "datatype": "Int",
            "indicator": "orange" if needs_improvement > critical else "red"
        },
        {
            "value": round(avg_nba, 1),
            "label": _("Avg NBA Score (%)"),
            "datatype": "Percent"
        },
        {
            "value": round(avg_naac, 1),
            "label": _("Avg NAAC Score (%)"),
            "datatype": "Percent"
        }
    ]
