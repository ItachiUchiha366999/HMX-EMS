# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, date_diff


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns(filters):
    return [
        {
            "label": _("Category"),
            "fieldname": "category",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Grievance Type"),
            "fieldname": "grievance_type",
            "fieldtype": "Link",
            "options": "Grievance Type",
            "width": 150
        },
        {
            "label": _("Total"),
            "fieldname": "total_count",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Resolved"),
            "fieldname": "resolved_count",
            "fieldtype": "Int",
            "width": 90
        },
        {
            "label": _("Within SLA"),
            "fieldname": "within_sla_count",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("At Risk"),
            "fieldname": "at_risk_count",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Breached"),
            "fieldname": "breached_count",
            "fieldtype": "Int",
            "width": 90
        },
        {
            "label": _("SLA Compliance"),
            "fieldname": "sla_compliance_rate",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": _("Avg Resolution (Days)"),
            "fieldname": "avg_resolution_days",
            "fieldtype": "Float",
            "width": 140,
            "precision": 1
        },
        {
            "label": _("SLA Target (Days)"),
            "fieldname": "sla_target_days",
            "fieldtype": "Int",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    # Get grievance data grouped by category and type
    data = frappe.db.sql("""
        SELECT
            g.category,
            g.grievance_type,
            gt.sla_days as sla_target_days,
            COUNT(*) as total_count,
            SUM(CASE WHEN g.status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved_count,
            SUM(CASE WHEN g.sla_status = 'Within SLA' THEN 1 ELSE 0 END) as within_sla_count,
            SUM(CASE WHEN g.sla_status = 'At Risk' THEN 1 ELSE 0 END) as at_risk_count,
            SUM(CASE WHEN g.sla_status = 'Breached' THEN 1 ELSE 0 END) as breached_count,
            AVG(CASE
                WHEN g.status IN ('Resolved', 'Closed') AND g.resolution_date IS NOT NULL
                THEN DATEDIFF(g.resolution_date, g.creation)
                ELSE NULL
            END) as avg_resolution_days
        FROM `tabGrievance` g
        LEFT JOIN `tabGrievance Type` gt ON g.grievance_type = gt.name
        WHERE g.creation IS NOT NULL
        {conditions}
        GROUP BY g.category, g.grievance_type, gt.sla_days
        ORDER BY g.category, g.grievance_type
    """.format(conditions=conditions), filters, as_dict=True)

    # Calculate SLA compliance rate
    for row in data:
        total_with_sla = (row.within_sla_count or 0) + (row.at_risk_count or 0) + (row.breached_count or 0)
        if total_with_sla > 0:
            row.sla_compliance_rate = ((row.within_sla_count or 0) / total_with_sla) * 100
        else:
            row.sla_compliance_rate = 100  # No SLA tracked = compliant

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND g.creation >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND g.creation <= %(to_date)s"
    if filters.get("category"):
        conditions += " AND g.category = %(category)s"
    if filters.get("grievance_type"):
        conditions += " AND g.grievance_type = %(grievance_type)s"
    if filters.get("assigned_to"):
        conditions += " AND g.assigned_to = %(assigned_to)s"
    if filters.get("sla_status"):
        conditions += " AND g.sla_status = %(sla_status)s"

    return conditions


def get_chart(data, filters):
    if not data or len(data) == 0:
        return None

    # Aggregate by category for chart
    category_data = {}
    for row in data:
        category = row.category or "Uncategorized"
        if category not in category_data:
            category_data[category] = {
                "within_sla": 0,
                "at_risk": 0,
                "breached": 0
            }
        category_data[category]["within_sla"] += row.within_sla_count or 0
        category_data[category]["at_risk"] += row.at_risk_count or 0
        category_data[category]["breached"] += row.breached_count or 0

    labels = list(category_data.keys())[:10]  # Top 10 categories

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": _("Within SLA"),
                    "values": [category_data[cat]["within_sla"] for cat in labels]
                },
                {
                    "name": _("At Risk"),
                    "values": [category_data[cat]["at_risk"] for cat in labels]
                },
                {
                    "name": _("Breached"),
                    "values": [category_data[cat]["breached"] for cat in labels]
                }
            ]
        },
        "type": "bar",
        "colors": ["#28a745", "#ffc107", "#dc3545"],
        "barOptions": {
            "stacked": 1
        }
    }


def get_summary(data):
    if not data:
        return []

    total_grievances = sum(d.total_count or 0 for d in data)
    total_resolved = sum(d.resolved_count or 0 for d in data)
    total_within_sla = sum(d.within_sla_count or 0 for d in data)
    total_at_risk = sum(d.at_risk_count or 0 for d in data)
    total_breached = sum(d.breached_count or 0 for d in data)

    total_with_sla = total_within_sla + total_at_risk + total_breached
    overall_compliance = (total_within_sla / total_with_sla * 100) if total_with_sla > 0 else 100

    resolution_times = [d.avg_resolution_days for d in data if d.avg_resolution_days is not None]
    avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0

    resolution_rate = (total_resolved / total_grievances * 100) if total_grievances > 0 else 0

    return [
        {
            "value": total_grievances,
            "indicator": "Blue",
            "label": _("Total Grievances"),
            "datatype": "Int"
        },
        {
            "value": total_resolved,
            "indicator": "Green",
            "label": _("Resolved"),
            "datatype": "Int"
        },
        {
            "value": flt(resolution_rate, 1),
            "indicator": "Green" if resolution_rate >= 80 else "Orange" if resolution_rate >= 60 else "Red",
            "label": _("Resolution Rate (%)"),
            "datatype": "Percent"
        },
        {
            "value": flt(overall_compliance, 1),
            "indicator": "Green" if overall_compliance >= 90 else "Orange" if overall_compliance >= 70 else "Red",
            "label": _("SLA Compliance (%)"),
            "datatype": "Percent"
        },
        {
            "value": total_breached,
            "indicator": "Red" if total_breached > 0 else "Green",
            "label": _("SLA Breached"),
            "datatype": "Int"
        },
        {
            "value": flt(avg_resolution, 1),
            "indicator": "Blue",
            "label": _("Avg Resolution (Days)"),
            "datatype": "Float"
        }
    ]
