# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "asset_code",
            "label": _("Asset Code"),
            "fieldtype": "Link",
            "options": "Asset",
            "width": 120
        },
        {
            "fieldname": "asset_name",
            "label": _("Asset Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "asset_category",
            "label": _("Category"),
            "fieldtype": "Link",
            "options": "Asset Category",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "University Department",
            "width": 120
        },
        {
            "fieldname": "location",
            "label": _("Location"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        {
            "fieldname": "custodian",
            "label": _("Custodian"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "fieldname": "purchase_date",
            "label": _("Purchase Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "gross_purchase_amount",
            "label": _("Purchase Value"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "total_depreciation",
            "label": _("Depreciation"),
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "fieldname": "asset_value",
            "label": _("Current Value"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "depreciation_method",
            "label": _("Dep. Method"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            a.name as asset_code,
            a.asset_name,
            a.asset_category,
            a.status,
            a.department,
            a.location,
            a.custodian,
            a.purchase_date,
            a.gross_purchase_amount,
            a.total_depreciation,
            a.asset_value,
            a.depreciation_method
        FROM `tabAsset` a
        WHERE a.docstatus = 1
        {conditions}
        ORDER BY a.asset_category, a.asset_name
    """.format(conditions=conditions), {
        "asset_category": filters.get("asset_category"),
        "department": filters.get("department"),
        "status": filters.get("status"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date")
    }, as_dict=True)

    return data


def get_conditions(filters):
    conditions = []

    if filters.get("asset_category"):
        conditions.append("AND a.asset_category = %(asset_category)s")

    if filters.get("department"):
        conditions.append("AND a.department = %(department)s")

    if filters.get("status"):
        conditions.append("AND a.status = %(status)s")

    if filters.get("from_date"):
        conditions.append("AND a.purchase_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("AND a.purchase_date <= %(to_date)s")

    return " ".join(conditions)
