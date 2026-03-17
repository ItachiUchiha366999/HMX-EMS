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
        {
            "label": _("Feedback Form"),
            "fieldname": "feedback_form",
            "fieldtype": "Link",
            "options": "Feedback Form",
            "width": 200
        },
        {
            "label": _("Form Type"),
            "fieldname": "form_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Academic Term"),
            "fieldname": "academic_term",
            "fieldtype": "Link",
            "options": "Academic Term",
            "width": 120
        },
        {
            "label": _("Responses"),
            "fieldname": "response_count",
            "fieldtype": "Int",
            "width": 90
        },
        {
            "label": _("Target"),
            "fieldname": "target_count",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Response Rate"),
            "fieldname": "response_rate",
            "fieldtype": "Percent",
            "width": 110
        },
        {
            "label": _("Avg Score"),
            "fieldname": "avg_score",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("NPS"),
            "fieldname": "nps",
            "fieldtype": "Float",
            "width": 80,
            "precision": 1
        },
        {
            "label": _("Promoters"),
            "fieldname": "promoters",
            "fieldtype": "Int",
            "width": 90
        },
        {
            "label": _("Passives"),
            "fieldname": "passives",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": _("Detractors"),
            "fieldname": "detractors",
            "fieldtype": "Int",
            "width": 90
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql(f"""
        SELECT
            ff.name as feedback_form,
            ff.title as form_title,
            ff.form_type,
            ff.academic_term,
            ff.target_responses as target_count,
            COUNT(fr.name) as response_count,
            AVG(fr.overall_score) as avg_score,
            SUM(CASE WHEN fr.nps_category = 'Promoter' THEN 1 ELSE 0 END) as promoters,
            SUM(CASE WHEN fr.nps_category = 'Passive' THEN 1 ELSE 0 END) as passives,
            SUM(CASE WHEN fr.nps_category = 'Detractor' THEN 1 ELSE 0 END) as detractors
        FROM `tabFeedback Form` ff
        LEFT JOIN `tabFeedback Response` fr ON fr.feedback_form = ff.name
            AND fr.status IN ('Valid', 'Submitted')
        WHERE 1=1
        {conditions}
        GROUP BY ff.name, ff.title, ff.form_type, ff.academic_term, ff.target_responses
        ORDER BY ff.creation DESC
    """, as_dict=True)

    # Calculate derived fields
    for row in data:
        # Response rate
        if row.target_count and row.target_count > 0:
            row.response_rate = (row.response_count / row.target_count) * 100
        else:
            row.response_rate = 0

        # NPS calculation
        total = row.promoters + row.passives + row.detractors
        if total > 0:
            row.nps = ((row.promoters - row.detractors) / total) * 100
        else:
            row.nps = 0

    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("feedback_form"):
        conditions += f" AND ff.name = '{filters.get('feedback_form')}'"
    if filters.get("form_type"):
        conditions += f" AND ff.form_type = '{filters.get('form_type')}'"
    if filters.get("academic_term"):
        conditions += f" AND ff.academic_term = '{filters.get('academic_term')}'"
    if filters.get("from_date"):
        conditions += f" AND ff.creation >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND ff.creation <= '{filters.get('to_date')}'"

    return conditions


def get_chart(data):
    if not data or len(data) == 0:
        return None

    # Show top 10 forms by response count
    top_data = sorted(data, key=lambda x: x.response_count or 0, reverse=True)[:10]

    return {
        "data": {
            "labels": [d.form_title[:25] if d.get("form_title") else d.feedback_form[:25] for d in top_data],
            "datasets": [
                {
                    "name": _("Avg Score (%)"),
                    "values": [flt(d.avg_score, 1) for d in top_data]
                },
                {
                    "name": _("Response Rate (%)"),
                    "values": [flt(d.response_rate, 1) for d in top_data]
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#28a745"]
    }


def get_summary(data):
    if not data:
        return []

    total_responses = sum(d.response_count or 0 for d in data)
    total_target = sum(d.target_count or 0 for d in data if d.target_count)
    avg_score = sum(d.avg_score or 0 for d in data if d.avg_score) / len([d for d in data if d.avg_score]) if any(d.avg_score for d in data) else 0
    total_promoters = sum(d.promoters or 0 for d in data)
    total_detractors = sum(d.detractors or 0 for d in data)
    total_passives = sum(d.passives or 0 for d in data)

    overall_nps = 0
    total_nps_responses = total_promoters + total_passives + total_detractors
    if total_nps_responses > 0:
        overall_nps = ((total_promoters - total_detractors) / total_nps_responses) * 100

    overall_response_rate = (total_responses / total_target * 100) if total_target > 0 else 0

    return [
        {
            "value": len(data),
            "indicator": "Blue",
            "label": _("Total Forms"),
            "datatype": "Int"
        },
        {
            "value": total_responses,
            "indicator": "Green",
            "label": _("Total Responses"),
            "datatype": "Int"
        },
        {
            "value": flt(overall_response_rate, 1),
            "indicator": "Green" if overall_response_rate >= 70 else "Orange" if overall_response_rate >= 50 else "Red",
            "label": _("Overall Response Rate (%)"),
            "datatype": "Percent"
        },
        {
            "value": flt(avg_score, 1),
            "indicator": "Green" if avg_score >= 80 else "Orange" if avg_score >= 60 else "Red",
            "label": _("Average Score (%)"),
            "datatype": "Percent"
        },
        {
            "value": flt(overall_nps, 1),
            "indicator": "Green" if overall_nps >= 50 else "Orange" if overall_nps >= 0 else "Red",
            "label": _("Overall NPS"),
            "datatype": "Float"
        }
    ]
