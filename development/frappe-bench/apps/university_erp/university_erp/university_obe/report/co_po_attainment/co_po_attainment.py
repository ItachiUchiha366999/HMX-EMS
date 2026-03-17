# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)

    return columns, data, None, chart


def get_columns(filters):
    columns = [
        {"label": _("Course Outcome"), "fieldname": "co_code", "fieldtype": "Data", "width": 100},
        {"label": _("CO Statement"), "fieldname": "co_statement", "fieldtype": "Data", "width": 300},
        {"label": _("Bloom's Level"), "fieldname": "bloom_level", "fieldtype": "Data", "width": 100},
        {"label": _("Target %"), "fieldname": "target", "fieldtype": "Percent", "width": 90},
        {"label": _("Current %"), "fieldname": "current", "fieldtype": "Percent", "width": 90},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100}
    ]

    # Add PO columns if program filter is set
    if filters and filters.get("program"):
        pos = frappe.get_all("Program Outcome",
            filters={"program": filters.get("program"), "status": "Active"},
            fields=["po_code", "po_number"],
            order_by="po_number"
        )
        for po in pos:
            columns.append({
                "label": po.po_code or f"PO{po.po_number}",
                "fieldname": (po.po_code or f"PO{po.po_number}").lower().replace(" ", "_"),
                "fieldtype": "Data",
                "width": 60
            })

    return columns


def get_data(filters):
    conditions = {"status": "Active"}

    if filters and filters.get("course"):
        conditions["course"] = filters.get("course")

    # Get Course Outcomes
    cos = frappe.get_all("Course Outcome",
        filters=conditions,
        fields=["name", "co_code", "co_number", "co_statement", "bloom_level",
                "target_attainment", "current_attainment", "course"],
        order_by="co_number"
    )

    data = []
    for co in cos:
        target = flt(co.target_attainment) or 60
        current = flt(co.current_attainment)

        status = "Achieved" if current >= target else "Not Achieved"

        row = {
            "co_code": co.co_code or f"CO{co.co_number}",
            "co_statement": co.co_statement[:100] + "..." if len(co.co_statement or "") > 100 else co.co_statement,
            "bloom_level": co.bloom_level,
            "target": target,
            "current": current,
            "status": status
        }

        # Add CO-PO mapping values if program filter is set
        if filters and filters.get("program"):
            # Get CO-PO Mapping for this CO
            mappings = frappe.get_all("CO PO Mapping",
                filters={
                    "course": co.course,
                    "program": filters.get("program"),
                    "docstatus": 1
                },
                fields=["name"]
            )

            if mappings:
                # Get mapping entries
                entries = frappe.get_all("CO PO Mapping Entry",
                    filters={
                        "parent": mappings[0].name,
                        "course_outcome": co.name
                    },
                    fields=["program_outcome", "correlation_level"]
                )

                for entry in entries:
                    po = frappe.get_doc("Program Outcome", entry.program_outcome)
                    po_key = (po.po_code or f"PO{po.po_number}").lower().replace(" ", "_")
                    row[po_key] = entry.correlation_level or "-"

        data.append(row)

    return data


def get_chart(data, filters):
    if not data:
        return None

    return {
        "data": {
            "labels": [d.get("co_code") for d in data],
            "datasets": [
                {"name": _("Target"), "values": [d.get("target", 0) for d in data]},
                {"name": _("Current Attainment"), "values": [d.get("current", 0) for d in data]}
            ]
        },
        "type": "bar",
        "colors": ["#808080", "#28a745"]
    }
