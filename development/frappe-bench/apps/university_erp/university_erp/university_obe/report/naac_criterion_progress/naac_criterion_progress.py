# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)
    chart = get_chart(data)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {"label": _("Criterion"), "fieldname": "criterion", "fieldtype": "Data", "width": 280},
        {"label": _("Weightage"), "fieldname": "weightage", "fieldtype": "Int", "width": 100},
        {"label": _("Total Metrics"), "fieldname": "total_metrics", "fieldtype": "Int", "width": 110},
        {"label": _("Completed"), "fieldname": "completed", "fieldtype": "Int", "width": 100},
        {"label": _("In Progress"), "fieldname": "in_progress", "fieldtype": "Int", "width": 100},
        {"label": _("Not Started"), "fieldname": "not_started", "fieldtype": "Int", "width": 100},
        {"label": _("Progress %"), "fieldname": "progress", "fieldtype": "Percent", "width": 100},
        {"label": _("Avg Score"), "fieldname": "avg_score", "fieldtype": "Float", "width": 90, "precision": 2}
    ]


def get_data(filters):
    criteria = [
        {"num": "1", "name": "Curricular Aspects", "weightage": 100},
        {"num": "2", "name": "Teaching-Learning and Evaluation", "weightage": 200},
        {"num": "3", "name": "Research, Innovations and Extension", "weightage": 150},
        {"num": "4", "name": "Infrastructure and Learning Resources", "weightage": 100},
        {"num": "5", "name": "Student Support and Progression", "weightage": 100},
        {"num": "6", "name": "Governance, Leadership and Management", "weightage": 100},
        {"num": "7", "name": "Institutional Values and Best Practices", "weightage": 100}
    ]

    data = []
    cycle = filters.get("accreditation_cycle") if filters else None

    for c in criteria:
        metric_filters = {"criterion": ["like", f"{c['num']}.%"]}
        if cycle:
            metric_filters["accreditation_cycle"] = cycle

        metrics = frappe.get_all("NAAC Metric",
            filters=metric_filters,
            fields=["status", "score", "max_score"]
        )

        completed = len([m for m in metrics if m.status in ["Completed", "Verified", "Submitted"]])
        in_progress = len([m for m in metrics if m.status in ["In Progress", "Data Collection"]])
        not_started = len([m for m in metrics if m.status == "Not Started"])

        total = len(metrics)
        progress = (completed / total * 100) if total > 0 else 0

        scores = [flt(m.score) for m in metrics if m.score]
        avg_score = sum(scores) / len(scores) if scores else 0

        data.append({
            "criterion": f"{c['num']}. {c['name']}",
            "weightage": c["weightage"],
            "total_metrics": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "progress": round(progress, 1),
            "avg_score": round(avg_score, 2)
        })

    return data


def get_summary(data):
    total_metrics = sum(d["total_metrics"] for d in data)
    total_completed = sum(d["completed"] for d in data)
    total_in_progress = sum(d["in_progress"] for d in data)
    overall_progress = (total_completed / total_metrics * 100) if total_metrics > 0 else 0

    return [
        {"label": _("Total Metrics"), "value": total_metrics, "indicator": "Blue"},
        {"label": _("Completed"), "value": total_completed, "indicator": "Green"},
        {"label": _("In Progress"), "value": total_in_progress, "indicator": "Orange"},
        {"label": _("Overall Progress"), "value": f"{overall_progress:.1f}%",
         "indicator": "Green" if overall_progress > 80 else "Orange" if overall_progress > 50 else "Red"}
    ]


def get_chart(data):
    return {
        "data": {
            "labels": [d["criterion"].split(". ")[1][:20] for d in data],
            "datasets": [
                {"name": _("Progress %"), "values": [d["progress"] for d in data]}
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }
