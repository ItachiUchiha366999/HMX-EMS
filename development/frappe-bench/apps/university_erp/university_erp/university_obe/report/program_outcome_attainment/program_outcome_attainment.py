# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {"label": _("PO Code"), "fieldname": "po_code", "fieldtype": "Data", "width": 100},
        {"label": _("PO Title"), "fieldname": "po_title", "fieldtype": "Data", "width": 200},
        {"label": _("NBA Attribute"), "fieldname": "nba_attribute", "fieldtype": "Data", "width": 150},
        {"label": _("Target %"), "fieldname": "target", "fieldtype": "Percent", "width": 100},
        {"label": _("Current %"), "fieldname": "current", "fieldtype": "Percent", "width": 100},
        {"label": _("Gap"), "fieldname": "gap", "fieldtype": "Float", "width": 80, "precision": 2},
        {"label": _("Contributing COs"), "fieldname": "contributing_cos", "fieldtype": "Int", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100}
    ]


def get_data(filters):
    conditions = {"status": "Active"}

    if filters and filters.get("program"):
        conditions["program"] = filters.get("program")

    pos = frappe.get_all("Program Outcome",
        filters=conditions,
        fields=["name", "po_code", "po_number", "po_title", "nba_attribute",
                "target_attainment", "current_attainment", "program"],
        order_by="po_number"
    )

    data = []
    for po in pos:
        target = flt(po.target_attainment) or 60
        current = flt(po.current_attainment)
        gap = max(0, target - current)

        # Count contributing COs
        contributing_cos = frappe.db.sql("""
            SELECT COUNT(DISTINCT cpe.course_outcome)
            FROM `tabCO PO Mapping Entry` cpe
            JOIN `tabCO PO Mapping` cpm ON cpe.parent = cpm.name
            WHERE cpe.program_outcome = %s
            AND cpm.docstatus = 1
        """, po.name)[0][0] or 0

        status = "Achieved" if current >= target else "Not Achieved"

        data.append({
            "po_code": po.po_code or f"PO{po.po_number}",
            "po_title": po.po_title,
            "nba_attribute": po.nba_attribute or "-",
            "target": target,
            "current": current,
            "gap": gap,
            "contributing_cos": contributing_cos,
            "status": status
        })

    return data


def get_chart(data):
    if not data:
        return None

    return {
        "data": {
            "labels": [d.get("po_code") for d in data],
            "datasets": [
                {"name": _("Target"), "values": [d.get("target", 0) for d in data]},
                {"name": _("Current Attainment"), "values": [d.get("current", 0) for d in data]}
            ]
        },
        "type": "bar",
        "colors": ["#808080", "#2563eb"]
    }


def get_summary(data):
    if not data:
        return []

    total_pos = len(data)
    achieved = sum(1 for d in data if d["status"] == "Achieved")
    avg_attainment = sum(d["current"] for d in data) / total_pos if total_pos > 0 else 0

    return [
        {"label": _("Total POs"), "value": total_pos, "indicator": "Blue"},
        {"label": _("Achieved"), "value": achieved, "indicator": "Green"},
        {"label": _("Not Achieved"), "value": total_pos - achieved, "indicator": "Red"},
        {"label": _("Avg Attainment"), "value": f"{avg_attainment:.1f}%", "indicator": "Blue"}
    ]
