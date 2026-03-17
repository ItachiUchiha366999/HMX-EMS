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
        {"label": _("Parameter"), "fieldname": "parameter", "fieldtype": "Data", "width": 250},
        {"label": _("Category"), "fieldname": "category", "fieldtype": "Data", "width": 80},
        {"label": _("Weightage %"), "fieldname": "weightage", "fieldtype": "Percent", "width": 100},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Float", "width": 100, "precision": 2},
        {"label": _("Score"), "fieldname": "score", "fieldtype": "Float", "width": 100, "precision": 2},
        {"label": _("Max Score"), "fieldname": "max_score", "fieldtype": "Float", "width": 100, "precision": 2}
    ]


def get_data(filters):
    conditions = {}
    if filters and filters.get("ranking_year"):
        conditions["ranking_year"] = filters.get("ranking_year")
    if filters and filters.get("category"):
        conditions["category"] = filters.get("category")

    nirf_data = frappe.get_all("NIRF Data",
        filters=conditions,
        fields=["*"],
        order_by="ranking_year desc",
        limit=1
    )

    if not nirf_data:
        return []

    nirf = nirf_data[0]

    data = [
        # TLR Parameters (30%)
        {"parameter": "Student Strength (SS)", "category": "TLR", "weightage": 7.5,
         "value": nirf.ss_student_strength or 0, "score": 0, "max_score": 7.5},
        {"parameter": "Faculty-Student Ratio (FSR)", "category": "TLR", "weightage": 7.5,
         "value": nirf.fsr_faculty_ratio or 0, "score": 0, "max_score": 7.5},
        {"parameter": "Faculty with PhD (FQE)", "category": "TLR", "weightage": 7.5,
         "value": nirf.fqe_faculty_qualification or 0, "score": 0, "max_score": 7.5},
        {"parameter": "Financial Resources (FRU)", "category": "TLR", "weightage": 7.5,
         "value": nirf.fru_financial_resources or 0, "score": 0, "max_score": 7.5},

        # RP Parameters (30%)
        {"parameter": "Publications (PU)", "category": "RP", "weightage": 7.5,
         "value": nirf.pu_publications or 0, "score": 0, "max_score": 7.5},
        {"parameter": "Quality Publications (QP)", "category": "RP", "weightage": 7.5,
         "value": nirf.qp_quality_publications or 0, "score": 0, "max_score": 7.5},
        {"parameter": "IPR/Patents", "category": "RP", "weightage": 7.5,
         "value": nirf.ipr_patents or 0, "score": 0, "max_score": 7.5},
        {"parameter": "Funded Projects (FPPP)", "category": "RP", "weightage": 7.5,
         "value": nirf.fppp_projects or 0, "score": 0, "max_score": 7.5},

        # GO Parameters (20%)
        {"parameter": "University Exam Results (GUE)", "category": "GO", "weightage": 6.67,
         "value": nirf.gue_university_exams or 0, "score": 0, "max_score": 6.67},
        {"parameter": "PhD Students (GPHD)", "category": "GO", "weightage": 6.67,
         "value": nirf.gphd_phd_students or 0, "score": 0, "max_score": 6.67},
        {"parameter": "Median Salary (GMS)", "category": "GO", "weightage": 6.66,
         "value": nirf.gms_median_salary or 0, "score": 0, "max_score": 6.66},

        # OI Parameters (10%)
        {"parameter": "Region Diversity (RD)", "category": "OI", "weightage": 2.5,
         "value": nirf.rd_region_diversity or 0, "score": 0, "max_score": 2.5},
        {"parameter": "Women Diversity (WD)", "category": "OI", "weightage": 2.5,
         "value": nirf.wd_women_diversity or 0, "score": 0, "max_score": 2.5},
        {"parameter": "Economically Backward (ESCS)", "category": "OI", "weightage": 2.5,
         "value": nirf.escs_economically_backward or 0, "score": 0, "max_score": 2.5},
        {"parameter": "Facilities for Disabled (PCS)", "category": "OI", "weightage": 2.5,
         "value": nirf.pcs_facilities_disabled or 0, "score": 0, "max_score": 2.5},

        # Perception (10%)
        {"parameter": "Peer Perception", "category": "PR", "weightage": 10,
         "value": nirf.pr_peer_perception or 0, "score": flt(nirf.pr_score), "max_score": 10}
    ]

    # Calculate scores based on category totals from NIRF Data
    tlr_score = flt(nirf.tlr_score)
    rp_score = flt(nirf.rp_score)
    go_score = flt(nirf.go_score)
    oi_score = flt(nirf.oi_score)

    # Distribute scores proportionally
    for row in data:
        if row["category"] == "TLR":
            row["score"] = round(tlr_score / 4, 2) if row["value"] > 0 else 0
        elif row["category"] == "RP":
            row["score"] = round(rp_score / 4, 2) if row["value"] > 0 else 0
        elif row["category"] == "GO":
            row["score"] = round(go_score / 3, 2) if row["value"] > 0 else 0
        elif row["category"] == "OI":
            row["score"] = round(oi_score / 4, 2) if row["value"] > 0 else 0

    return data


def get_chart(data):
    if not data:
        return None

    categories = ["TLR", "RP", "GO", "OI", "PR"]
    category_scores = {}

    for cat in categories:
        category_scores[cat] = sum(d["score"] for d in data if d["category"] == cat)

    return {
        "data": {
            "labels": categories,
            "datasets": [
                {"name": _("Score"), "values": [category_scores.get(c, 0) for c in categories]},
                {"name": _("Max Score"), "values": [30, 30, 20, 10, 10]}
            ]
        },
        "type": "bar",
        "colors": ["#3182ce", "#e2e8f0"]
    }


def get_summary(data):
    if not data:
        return []

    total_score = sum(d["score"] for d in data)
    max_score = sum(d["max_score"] for d in data)
    completion = (total_score / max_score * 100) if max_score > 0 else 0

    return [
        {"label": _("Total Score"), "value": round(total_score, 2), "indicator": "Blue"},
        {"label": _("Max Score"), "value": round(max_score, 2), "indicator": "Grey"},
        {"label": _("Completion"), "value": f"{completion:.1f}%",
         "indicator": "Green" if completion > 70 else "Orange" if completion > 40 else "Red"}
    ]
