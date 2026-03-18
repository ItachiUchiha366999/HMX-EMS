# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Analytics API Endpoints

Provides whitelisted API methods for dashboard and KPI access.
"""

import json
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_dashboard(dashboard_name, filters=None):
    """
    Get dashboard data

    Args:
        dashboard_name: Name of Custom Dashboard
        filters: Optional JSON string or dict with filters

    Returns:
        dict: Dashboard data with widgets
    """
    if isinstance(filters, str):
        filters = json.loads(filters)

    from university_erp.university_erp.analytics.dashboard_engine import DashboardEngine

    engine = DashboardEngine()
    return engine.get_dashboard_data(dashboard_name, filters)


@frappe.whitelist()
def get_available_dashboards():
    """
    Get list of dashboards available to current user

    Returns:
        list: Available dashboards
    """
    from university_erp.university_erp.analytics.dashboard_engine import DashboardEngine

    engine = DashboardEngine()
    return engine.get_available_dashboards()


@frappe.whitelist()
def get_kpi_value(kpi_name, filters=None):
    """
    Get current value of a KPI

    Args:
        kpi_name: Name of KPI Definition
        filters: Optional JSON string or dict with filters

    Returns:
        dict: KPI value with status
    """
    if not frappe.has_permission("KPI Definition", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    if isinstance(filters, str):
        filters = json.loads(filters)

    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

    manager = AnalyticsManager()
    value = manager.calculate_kpi(kpi_name, filters)

    kpi_doc = frappe.get_doc("KPI Definition", kpi_name)

    return {
        "kpi_name": kpi_name,
        "value": value,
        "target": kpi_doc.target_value,
        "unit": kpi_doc.unit,
        "status": kpi_doc.get_status(value),
        "variance": kpi_doc.get_variance(value)
    }


@frappe.whitelist()
def get_kpi_trend(kpi_name, periods=6, period_type="Monthly", filters=None):
    """
    Get trend data for a KPI

    Args:
        kpi_name: Name of KPI Definition
        periods: Number of periods to fetch
        period_type: Daily/Weekly/Monthly/Quarterly/Yearly
        filters: Optional JSON string or dict with filters

    Returns:
        list: Trend data points
    """
    if not frappe.has_permission("KPI Definition", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    if isinstance(filters, str):
        filters = json.loads(filters)

    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

    manager = AnalyticsManager()
    return manager.get_trend_data(kpi_name, int(periods), period_type, filters)


@frappe.whitelist()
def get_kpi_comparison(kpi_name, current_start, current_end, previous_start, previous_end, filters=None):
    """
    Get comparison data between two periods

    Args:
        kpi_name: Name of KPI Definition
        current_start: Current period start date
        current_end: Current period end date
        previous_start: Previous period start date
        previous_end: Previous period end date
        filters: Optional JSON string or dict with filters

    Returns:
        dict: Comparison data
    """
    if not frappe.has_permission("KPI Definition", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    if isinstance(filters, str):
        filters = json.loads(filters)

    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

    manager = AnalyticsManager()

    current_period = {"start": current_start, "end": current_end}
    previous_period = {"start": previous_start, "end": previous_end}

    return manager.get_comparison_data(kpi_name, current_period, previous_period, filters)


@frappe.whitelist()
def get_quick_stats():
    """
    Get quick statistics for the current user's dashboard

    Returns:
        dict: Quick stats including counts and key metrics
    """
    if not frappe.has_permission("Custom Dashboard", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    from university_erp.university_erp.analytics.dashboards.executive_dashboard import (
        get_overview_metrics
    )

    return get_overview_metrics()


@frappe.whitelist()
def execute_custom_report(report_name, filters=None):
    """
    Execute a custom report definition

    Args:
        report_name: Name of Custom Report Definition
        filters: Optional JSON string or dict with filters

    Returns:
        dict: Report data with columns and rows
    """
    if isinstance(filters, str):
        filters = json.loads(filters)

    report_doc = frappe.get_doc("Custom Report Definition", report_name)

    if not report_doc.has_access():
        frappe.throw(_("You don't have access to this report"))

    result = report_doc.execute(filters)

    # Include chart if configured
    if report_doc.include_chart:
        result["chart"] = report_doc.generate_chart(result.get("data", []))

    return result


@frappe.whitelist()
def get_all_kpis(category=None, active_only=True):
    """
    Get list of all KPIs

    Args:
        category: Optional category filter
        active_only: Only return active KPIs

    Returns:
        list: KPI definitions with current values
    """
    if not frappe.has_permission("KPI Definition", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    filters = {}

    if category:
        filters["category"] = category
    if active_only:
        filters["is_active"] = 1

    kpis = frappe.get_all(
        "KPI Definition",
        filters=filters,
        fields=[
            "name", "kpi_name", "kpi_code", "category", "description",
            "unit", "target_value", "tracking_frequency", "higher_is_better"
        ]
    )

    # Add latest values
    for kpi in kpis:
        latest = frappe.db.get_value(
            "KPI Value",
            {"kpi": kpi["name"]},
            ["value", "status", "period_start"],
            order_by="period_start DESC"
        )

        if latest:
            kpi["current_value"] = latest[0]
            kpi["status"] = latest[1]
            kpi["last_updated"] = latest[2]
        else:
            kpi["current_value"] = None
            kpi["status"] = None
            kpi["last_updated"] = None

    return kpis


@frappe.whitelist()
def calculate_kpi_now(kpi_name, store_value=False, filters=None):
    """
    Calculate a KPI value immediately

    Args:
        kpi_name: Name of KPI Definition
        store_value: Whether to store the calculated value
        filters: Optional JSON string or dict with filters

    Returns:
        dict: Calculated value and status
    """
    if not frappe.has_permission("KPI Definition", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    if isinstance(filters, str):
        filters = json.loads(filters)

    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager
    from frappe.utils import today, get_first_day, get_last_day

    manager = AnalyticsManager()
    value = manager.calculate_kpi(kpi_name, filters)

    kpi_doc = frappe.get_doc("KPI Definition", kpi_name)

    result = {
        "kpi_name": kpi_name,
        "value": value,
        "target": kpi_doc.target_value,
        "status": kpi_doc.get_status(value),
        "variance": kpi_doc.get_variance(value)
    }

    if store_value and value is not None:
        today_date = frappe.utils.getdate(today())
        period_start = get_first_day(today_date)
        period_end = get_last_day(today_date)

        kpi_value_name = manager.store_kpi_value(
            kpi_name=kpi_name,
            value=value,
            period_type=kpi_doc.tracking_frequency,
            period_start=period_start,
            period_end=period_end,
            filters=filters
        )
        result["stored_as"] = kpi_value_name

    return result
