# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
    return columns, data, None, chart


def get_columns(filters):
    """Generate dynamic columns based on POs"""
    columns = [
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
            "width": 300
        },
        {
            "fieldname": "bloom_level",
            "label": _("Bloom Level"),
            "fieldtype": "Data",
            "width": 100
        }
    ]

    # Get POs for the selected program/course
    if filters.get("program"):
        pos = frappe.get_all(
            "Program Outcome",
            filters={"program": filters.get("program"), "status": "Active"},
            fields=["po_code", "is_pso"],
            order_by="is_pso, po_number"
        )

        for po in pos:
            columns.append({
                "fieldname": po.po_code.lower().replace(" ", "_"),
                "label": po.po_code,
                "fieldtype": "Data",
                "width": 80
            })

    # Add average column
    columns.append({
        "fieldname": "avg_correlation",
        "label": _("Avg"),
        "fieldtype": "Float",
        "precision": 2,
        "width": 80
    })

    return columns


def get_data(filters):
    """Get CO-PO mapping data"""
    data = []

    if not filters.get("course") or not filters.get("program"):
        return data

    # Get the CO-PO mapping
    mapping_filters = {
        "course": filters.get("course"),
        "program": filters.get("program"),
        "docstatus": 1
    }
    if filters.get("academic_term"):
        mapping_filters["academic_term"] = filters.get("academic_term")

    mappings = frappe.get_all(
        "CO PO Mapping",
        filters=mapping_filters,
        fields=["name"],
        order_by="creation desc",
        limit=1
    )

    if not mappings:
        return data

    mapping = mappings[0]

    # Get COs for the course
    cos = frappe.get_all(
        "Course Outcome",
        filters={"course": filters.get("course"), "status": "Active"},
        fields=["name", "co_code", "co_statement", "bloom_level"],
        order_by="co_number"
    )

    # Get POs for the program
    pos = frappe.get_all(
        "Program Outcome",
        filters={"program": filters.get("program"), "status": "Active"},
        fields=["name", "po_code"],
        order_by="is_pso, po_number"
    )

    # Get mapping entries
    entries = frappe.get_all(
        "CO PO Mapping Entry",
        filters={"parent": mapping.name},
        fields=["course_outcome", "program_outcome", "correlation_level"]
    )

    # Build lookup
    mapping_lookup = {}
    for entry in entries:
        key = (entry.course_outcome, entry.program_outcome)
        try:
            level = int(str(entry.correlation_level).split(" ")[0])
        except (ValueError, IndexError):
            level = 0
        mapping_lookup[key] = level

    # Build data rows
    for co in cos:
        row = {
            "co_code": co.co_code,
            "co_statement": co.co_statement[:100] + "..." if len(co.co_statement or "") > 100 else co.co_statement,
            "bloom_level": co.bloom_level
        }

        total_correlation = 0
        count = 0

        for po in pos:
            key = (co.name, po.name)
            level = mapping_lookup.get(key, 0)
            field_name = po.po_code.lower().replace(" ", "_")
            row[field_name] = level if level > 0 else "-"

            if level > 0:
                total_correlation += level
                count += 1

        row["avg_correlation"] = round(total_correlation / count, 2) if count > 0 else 0
        data.append(row)

    return data


def get_chart(data, filters):
    """Generate chart for CO-PO distribution"""
    if not data:
        return None

    # Count correlations by level
    strong = 0  # Level 3
    moderate = 0  # Level 2
    weak = 0  # Level 1

    for row in data:
        for key, value in row.items():
            if key not in ["co_code", "co_statement", "bloom_level", "avg_correlation"]:
                if value == 3:
                    strong += 1
                elif value == 2:
                    moderate += 1
                elif value == 1:
                    weak += 1

    return {
        "data": {
            "labels": ["Strong (3)", "Moderate (2)", "Weak (1)"],
            "datasets": [
                {
                    "name": "Correlations",
                    "values": [strong, moderate, weak]
                }
            ]
        },
        "type": "bar",
        "colors": ["#28a745", "#ffc107", "#dc3545"]
    }
