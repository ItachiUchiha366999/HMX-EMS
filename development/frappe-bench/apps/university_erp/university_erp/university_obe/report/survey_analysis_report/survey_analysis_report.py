# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
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
            "fieldname": "total_responses",
            "label": _("Responses"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "avg_rating",
            "label": _("Avg Rating (1-5)"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 120
        },
        {
            "fieldname": "attainment_percent",
            "label": _("Attainment %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "attainment_level",
            "label": _("Attainment Level"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 120
        },
        {
            "fieldname": "rating_5",
            "label": _("Rating 5"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "rating_4",
            "label": _("Rating 4"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "rating_3",
            "label": _("Rating 3"),
            "fieldtype": "Int",
            "width": 80
        },
        {
            "fieldname": "rating_1_2",
            "label": _("Rating 1-2"),
            "fieldtype": "Int",
            "width": 80
        }
    ]


def get_data(filters):
    data = []

    survey_filters = {"status": ["in", ["Submitted", "Verified"]]}
    if filters.get("program"):
        survey_filters["program"] = filters.get("program")
    if filters.get("survey_type"):
        survey_filters["survey_type"] = filters.get("survey_type")
    if filters.get("academic_year"):
        survey_filters["academic_year"] = filters.get("academic_year")

    surveys = frappe.get_all(
        "OBE Survey",
        filters=survey_filters,
        fields=["name"]
    )

    if not surveys:
        return data

    # Get all PO ratings from these surveys
    survey_names = [s.name for s in surveys]

    # Build PO-wise statistics
    po_stats = {}

    for survey_name in survey_names:
        ratings = frappe.get_all(
            "Survey PO Rating",
            filters={"parent": survey_name},
            fields=["program_outcome", "po_code", "rating"]
        )

        for r in ratings:
            po_key = r.program_outcome
            if po_key not in po_stats:
                # Get PO details
                po = frappe.get_value(
                    "Program Outcome",
                    r.program_outcome,
                    ["po_code", "po_title"],
                    as_dict=True
                )
                po_stats[po_key] = {
                    "po_code": po.po_code if po else r.po_code,
                    "po_title": po.po_title if po else "",
                    "ratings": [],
                    "rating_distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
                }

            if r.rating:
                rating_value = int(r.rating * 5) if r.rating <= 1 else int(r.rating)
                rating_value = min(5, max(1, rating_value))
                po_stats[po_key]["ratings"].append(rating_value)
                po_stats[po_key]["rating_distribution"][rating_value] += 1

    # Calculate statistics for each PO
    for po_key, stats in po_stats.items():
        if not stats["ratings"]:
            continue

        total_responses = len(stats["ratings"])
        avg_rating = sum(stats["ratings"]) / total_responses
        attainment_percent = (avg_rating / 5) * 100
        attainment_level = get_attainment_level(attainment_percent)

        dist = stats["rating_distribution"]

        data.append({
            "po_code": stats["po_code"],
            "po_title": stats["po_title"],
            "total_responses": total_responses,
            "avg_rating": round(avg_rating, 2),
            "attainment_percent": round(attainment_percent, 1),
            "attainment_level": attainment_level,
            "rating_5": dist[5],
            "rating_4": dist[4],
            "rating_3": dist[3],
            "rating_1_2": dist[1] + dist[2]
        })

    # Sort by PO code
    data.sort(key=lambda x: x["po_code"])

    return data


def get_attainment_level(percentage):
    """Convert percentage to attainment level (0-3)"""
    if percentage >= 70:
        return 3
    elif percentage >= 60:
        return 2
    elif percentage >= 50:
        return 1
    else:
        return 0


def get_chart(data, filters):
    if not data:
        return None

    labels = [d["po_code"] for d in data]
    values = [d["avg_rating"] for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Average Rating",
                    "values": values
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }


def get_summary(data, filters):
    if not data:
        return []

    # Get overall survey statistics
    survey_filters = {"status": ["in", ["Submitted", "Verified"]]}
    if filters.get("program"):
        survey_filters["program"] = filters.get("program")
    if filters.get("survey_type"):
        survey_filters["survey_type"] = filters.get("survey_type")
    if filters.get("academic_year"):
        survey_filters["academic_year"] = filters.get("academic_year")

    surveys = frappe.get_all(
        "OBE Survey",
        filters=survey_filters,
        fields=["overall_satisfaction", "program_relevance", "employability_rating"]
    )

    total_surveys = len(surveys)
    avg_satisfaction = sum(s.overall_satisfaction or 0 for s in surveys) / total_surveys if total_surveys > 0 else 0
    avg_relevance = sum(s.program_relevance or 0 for s in surveys) / total_surveys if total_surveys > 0 else 0
    avg_employability = sum(s.employability_rating or 0 for s in surveys) / total_surveys if total_surveys > 0 else 0

    # Overall PO rating
    total_responses = sum(d["total_responses"] for d in data)
    overall_avg = sum(d["avg_rating"] * d["total_responses"] for d in data) / total_responses if total_responses > 0 else 0

    return [
        {
            "value": total_surveys,
            "label": _("Total Surveys"),
            "datatype": "Int"
        },
        {
            "value": round(overall_avg, 2),
            "label": _("Avg PO Rating (1-5)"),
            "datatype": "Float",
            "indicator": "green" if overall_avg >= 3.5 else "orange"
        },
        {
            "value": round(avg_satisfaction * 20, 1),  # Convert to percentage
            "label": _("Overall Satisfaction (%)"),
            "datatype": "Percent"
        },
        {
            "value": round(avg_relevance * 20, 1),
            "label": _("Program Relevance (%)"),
            "datatype": "Percent"
        },
        {
            "value": round(avg_employability * 20, 1),
            "label": _("Employability (%)"),
            "datatype": "Percent"
        }
    ]
