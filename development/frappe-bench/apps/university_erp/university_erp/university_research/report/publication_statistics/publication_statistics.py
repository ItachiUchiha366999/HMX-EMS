# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "name", "label": _("Publication"), "fieldtype": "Link", "options": "Research Publication", "width": 120},
        {"fieldname": "title", "label": _("Title"), "fieldtype": "Data", "width": 250},
        {"fieldname": "publication_type", "label": _("Type"), "fieldtype": "Data", "width": 120},
        {"fieldname": "publication_date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "journal_name", "label": _("Journal/Conference"), "fieldtype": "Data", "width": 150},
        {"fieldname": "indexed", "label": _("Indexed"), "fieldtype": "Data", "width": 100},
        {"fieldname": "impact_factor", "label": _("IF"), "fieldtype": "Float", "width": 70},
        {"fieldname": "citations", "label": _("Citations"), "fieldtype": "Int", "width": 80}
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("publication_type"):
        conditions += " AND publication_type = %(publication_type)s"
        values["publication_type"] = filters.get("publication_type")

    if filters.get("year"):
        conditions += " AND YEAR(publication_date) = %(year)s"
        values["year"] = filters.get("year")

    if filters.get("indexing"):
        if filters.get("indexing") == "Scopus":
            conditions += " AND is_scopus_indexed = 1"
        elif filters.get("indexing") == "WoS":
            conditions += " AND is_wos_indexed = 1"
        elif filters.get("indexing") == "UGC":
            conditions += " AND is_ugc_listed = 1"

    data = frappe.db.sql("""
        SELECT
            name,
            title,
            publication_type,
            publication_date,
            journal_name,
            is_scopus_indexed,
            is_wos_indexed,
            is_ugc_listed,
            impact_factor,
            citations
        FROM `tabResearch Publication`
        WHERE status = 'Published'
        {conditions}
        ORDER BY publication_date DESC
    """.format(conditions=conditions), values, as_dict=True)

    for row in data:
        indexing = []
        if row.get("is_scopus_indexed"):
            indexing.append("Scopus")
        if row.get("is_wos_indexed"):
            indexing.append("WoS")
        if row.get("is_ugc_listed"):
            indexing.append("UGC")
        row["indexed"] = ", ".join(indexing) if indexing else "-"

    return data


def get_chart(data):
    if not data:
        return None

    type_count = {}
    for row in data:
        pub_type = row.get("publication_type") or "Other"
        type_count[pub_type] = type_count.get(pub_type, 0) + 1

    return {
        "data": {
            "labels": list(type_count.keys()),
            "datasets": [{"name": _("Publications"), "values": list(type_count.values())}]
        },
        "type": "pie",
        "colors": ["#5e64ff", "#98d85b", "#ffa00a", "#ff5858", "#743ee2", "#36a2eb"]
    }


def get_summary(data):
    if not data:
        return []

    total = len(data)
    scopus = len([d for d in data if d.get("is_scopus_indexed")])
    wos = len([d for d in data if d.get("is_wos_indexed")])
    total_citations = sum(d.get("citations") or 0 for d in data)

    return [
        {"value": total, "label": _("Total Publications"), "datatype": "Int"},
        {"value": scopus, "label": _("Scopus Indexed"), "datatype": "Int", "indicator": "blue"},
        {"value": wos, "label": _("WoS Indexed"), "datatype": "Int", "indicator": "green"},
        {"value": total_citations, "label": _("Total Citations"), "datatype": "Int"}
    ]
