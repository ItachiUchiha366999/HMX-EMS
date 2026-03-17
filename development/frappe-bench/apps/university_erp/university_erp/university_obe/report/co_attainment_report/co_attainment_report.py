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
            "fieldname": "co_code",
            "label": _("CO Code"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "co_statement",
            "label": _("CO Statement"),
            "fieldtype": "Data",
            "width": 250
        },
        {
            "fieldname": "bloom_level",
            "label": _("Bloom Level"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "direct_attainment",
            "label": _("Direct (70%)"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        },
        {
            "fieldname": "indirect_attainment",
            "label": _("Indirect (30%)"),
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
            "fieldname": "gap",
            "label": _("Gap"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 80
        }
    ]


def get_data(filters):
    data = []

    attainment_filters = {"docstatus": 1}
    if filters.get("course"):
        attainment_filters["course"] = filters.get("course")
    if filters.get("academic_term"):
        attainment_filters["academic_term"] = filters.get("academic_term")
    if filters.get("academic_year"):
        attainment_filters["academic_year"] = filters.get("academic_year")

    attainments = frappe.get_all(
        "CO Attainment",
        filters=attainment_filters,
        fields=["name", "course"],
        order_by="creation desc"
    )

    if not attainments:
        return data

    # Get the most recent attainment for each course
    seen_courses = set()
    for att in attainments:
        if att.course in seen_courses:
            continue
        seen_courses.add(att.course)

        # Get final attainment entries
        entries = frappe.get_all(
            "CO Final Attainment",
            filters={"parent": att.name},
            fields=[
                "course_outcome", "co_code", "co_statement",
                "direct_attainment", "indirect_attainment",
                "final_attainment", "target_attainment", "achieved", "gap"
            ]
        )

        for entry in entries:
            # Get bloom level from CO
            co = frappe.get_value(
                "Course Outcome",
                entry.course_outcome,
                ["bloom_level"],
                as_dict=True
            )

            data.append({
                "co_code": entry.co_code,
                "co_statement": entry.co_statement[:80] + "..." if len(entry.co_statement or "") > 80 else entry.co_statement,
                "bloom_level": co.bloom_level if co else "",
                "direct_attainment": entry.direct_attainment,
                "indirect_attainment": entry.indirect_attainment,
                "final_attainment": entry.final_attainment,
                "target": entry.target_attainment,
                "achieved": "✓" if entry.achieved else "✗",
                "gap": entry.gap
            })

    return data


def get_chart(data):
    if not data:
        return None

    labels = [d["co_code"] for d in data]
    final_values = [d["final_attainment"] for d in data]
    target_values = [d["target"] / 100 * 3 for d in data]  # Convert percent to level

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Attainment",
                    "values": final_values
                },
                {
                    "name": "Target",
                    "values": target_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#28a745"]
    }


def get_summary(data):
    if not data:
        return []

    total_cos = len(data)
    achieved = sum(1 for d in data if d["achieved"] == "✓")
    avg_attainment = sum(d["final_attainment"] for d in data) / total_cos if total_cos > 0 else 0

    return [
        {
            "value": total_cos,
            "label": _("Total COs"),
            "datatype": "Int"
        },
        {
            "value": achieved,
            "label": _("COs Achieved"),
            "datatype": "Int",
            "indicator": "green" if achieved == total_cos else "orange"
        },
        {
            "value": round(avg_attainment, 2),
            "label": _("Avg Attainment Level"),
            "datatype": "Float"
        },
        {
            "value": round((achieved / total_cos) * 100, 1) if total_cos > 0 else 0,
            "label": _("Achievement Rate (%)"),
            "datatype": "Percent",
            "indicator": "green" if achieved == total_cos else "orange"
        }
    ]
