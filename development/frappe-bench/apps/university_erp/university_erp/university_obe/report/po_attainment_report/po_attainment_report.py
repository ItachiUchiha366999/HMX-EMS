# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data, filters)
    return columns, data, None, chart, summary


def get_columns(filters):
    return [
        {
            "fieldname": "po_code",
            "label": _("PO/PSO Code"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "po_title",
            "label": _("Title"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "is_pso",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "contributing_courses",
            "label": _("Courses"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "direct_attainment",
            "label": _("Direct (80%)"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        },
        {
            "fieldname": "indirect_attainment",
            "label": _("Indirect (20%)"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        },
        {
            "fieldname": "final_attainment",
            "label": _("Final"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 80
        },
        {
            "fieldname": "target",
            "label": _("Target"),
            "fieldtype": "Percent",
            "width": 80
        },
        {
            "fieldname": "achieved",
            "label": _("Achieved"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "nba_attribute",
            "label": _("NBA Attribute"),
            "fieldtype": "Data",
            "width": 150
        }
    ]


def get_data(filters):
    data = []

    attainment_filters = {"docstatus": 1}
    if filters.get("program"):
        attainment_filters["program"] = filters.get("program")
    if filters.get("academic_year"):
        attainment_filters["academic_year"] = filters.get("academic_year")

    attainments = frappe.get_all(
        "PO Attainment",
        filters=attainment_filters,
        fields=["name", "program"],
        order_by="creation desc",
        limit=1
    )

    if not attainments:
        return data

    att = attainments[0]

    # Get direct PO attainment entries
    direct_entries = {}
    for entry in frappe.get_all(
        "PO Attainment Entry",
        filters={"parent": att.name},
        fields=["program_outcome", "contributing_courses", "attainment_level"]
    ):
        direct_entries[entry.program_outcome] = entry

    # Get final PO attainment entries
    final_entries = frappe.get_all(
        "PO Final Entry",
        filters={"parent": att.name},
        fields=[
            "program_outcome", "po_code", "po_title", "is_pso",
            "direct_attainment", "indirect_attainment",
            "final_attainment", "target_attainment", "achieved"
        ]
    )

    for entry in final_entries:
        # Get NBA attribute from PO
        po = frappe.get_value(
            "Program Outcome",
            entry.program_outcome,
            ["nba_attribute"],
            as_dict=True
        )

        direct = direct_entries.get(entry.program_outcome, {})

        data.append({
            "po_code": entry.po_code,
            "po_title": entry.po_title,
            "is_pso": "PSO" if entry.is_pso else "PO",
            "contributing_courses": direct.contributing_courses if hasattr(direct, 'contributing_courses') else 0,
            "direct_attainment": entry.direct_attainment,
            "indirect_attainment": entry.indirect_attainment,
            "final_attainment": entry.final_attainment,
            "target": entry.target_attainment,
            "achieved": "✓" if entry.achieved else "✗",
            "nba_attribute": po.nba_attribute if po else ""
        })

    # Sort by PO/PSO
    data.sort(key=lambda x: (x["is_pso"] == "PSO", x["po_code"]))

    return data


def get_chart(data):
    if not data:
        return None

    labels = [d["po_code"] for d in data]
    final_values = [d["final_attainment"] for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Attainment Level",
                    "values": final_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data, filters):
    if not data:
        return []

    pos = [d for d in data if d["is_pso"] == "PO"]
    psos = [d for d in data if d["is_pso"] == "PSO"]

    po_achieved = sum(1 for d in pos if d["achieved"] == "✓")
    pso_achieved = sum(1 for d in psos if d["achieved"] == "✓")

    all_achieved = sum(1 for d in data if d["achieved"] == "✓")
    avg_attainment = sum(d["final_attainment"] for d in data) / len(data) if data else 0

    return [
        {
            "value": f"{po_achieved}/{len(pos)}",
            "label": _("POs Achieved"),
            "datatype": "Data",
            "indicator": "green" if po_achieved == len(pos) else "orange"
        },
        {
            "value": f"{pso_achieved}/{len(psos)}" if psos else "N/A",
            "label": _("PSOs Achieved"),
            "datatype": "Data",
            "indicator": "green" if pso_achieved == len(psos) else "orange"
        },
        {
            "value": round(avg_attainment, 2),
            "label": _("Avg Attainment Level"),
            "datatype": "Float"
        },
        {
            "value": round((all_achieved / len(data)) * 100, 1) if data else 0,
            "label": _("Achievement Rate (%)"),
            "datatype": "Percent",
            "indicator": "green" if all_achieved == len(data) else "orange"
        }
    ]
