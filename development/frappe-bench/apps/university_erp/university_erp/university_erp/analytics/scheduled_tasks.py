# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Scheduled Tasks for Analytics Module

These tasks are registered in hooks.py and run at specified intervals.
"""

import frappe
from frappe.utils import now_datetime, add_months, getdate


def run_scheduled_reports():
    """
    Run scheduled reports that are due (Daily task)

    This task checks for any scheduled reports that need to be executed
    and generates/sends them according to their configuration.
    """
    from university_erp.university_erp.analytics.report_scheduler import ReportScheduler

    try:
        scheduler = ReportScheduler()
        results = scheduler.run_scheduled_reports()

        if results:
            frappe.logger().info(f"Executed {len(results)} scheduled reports")
            for result in results:
                if result.get("status") == "Failed":
                    frappe.log_error(
                        f"Scheduled report failed: {result.get('report')} - {result.get('error')}",
                        "Scheduled Report Error"
                    )
    except Exception as e:
        frappe.log_error(f"Error running scheduled reports: {str(e)}", "Report Scheduler Error")


def calculate_daily_kpis():
    """
    Calculate daily KPIs (Daily task)

    This task calculates all active KPIs that are tracked daily.
    """
    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

    try:
        manager = AnalyticsManager()
        results = manager.calculate_all_kpis(period_type="Daily")

        success_count = sum(1 for r in results if r.get("status") == "Success")
        frappe.logger().info(f"Calculated {success_count}/{len(results)} daily KPIs")
    except Exception as e:
        frappe.log_error(f"Error calculating daily KPIs: {str(e)}", "KPI Calculation Error")


def calculate_weekly_kpis():
    """
    Calculate weekly KPIs (Weekly task - runs on Sundays)

    This task calculates all active KPIs that are tracked weekly.
    """
    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager
    from frappe.utils import today

    # Only run on Sundays
    today_date = getdate(today())
    if today_date.weekday() != 6:  # 6 = Sunday
        return

    try:
        manager = AnalyticsManager()
        results = manager.calculate_all_kpis(period_type="Weekly")

        success_count = sum(1 for r in results if r.get("status") == "Success")
        frappe.logger().info(f"Calculated {success_count}/{len(results)} weekly KPIs")
    except Exception as e:
        frappe.log_error(f"Error calculating weekly KPIs: {str(e)}", "KPI Calculation Error")


def calculate_monthly_kpis():
    """
    Calculate monthly KPIs (Monthly task - runs on 1st of each month)

    This task calculates all active KPIs that are tracked monthly.
    """
    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager
    from frappe.utils import today

    # Only run on the 1st of the month
    today_date = getdate(today())
    if today_date.day != 1:
        return

    try:
        manager = AnalyticsManager()
        results = manager.calculate_all_kpis(period_type="Monthly")

        success_count = sum(1 for r in results if r.get("status") == "Success")
        frappe.logger().info(f"Calculated {success_count}/{len(results)} monthly KPIs")
    except Exception as e:
        frappe.log_error(f"Error calculating monthly KPIs: {str(e)}", "KPI Calculation Error")


def calculate_quarterly_kpis():
    """
    Calculate quarterly KPIs (Monthly task - runs on 1st of quarter months)

    This task calculates all active KPIs that are tracked quarterly.
    """
    from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager
    from frappe.utils import today

    # Only run on the 1st of January, April, July, October
    today_date = getdate(today())
    if today_date.day != 1 or today_date.month not in [1, 4, 7, 10]:
        return

    try:
        manager = AnalyticsManager()
        results = manager.calculate_all_kpis(period_type="Quarterly")

        success_count = sum(1 for r in results if r.get("status") == "Success")
        frappe.logger().info(f"Calculated {success_count}/{len(results)} quarterly KPIs")
    except Exception as e:
        frappe.log_error(f"Error calculating quarterly KPIs: {str(e)}", "KPI Calculation Error")


def cleanup_old_kpi_values():
    """
    Clean up old KPI values (Monthly task)

    This task removes KPI values older than the configured retention period
    to prevent database bloat.
    """
    from frappe.utils import today, add_months

    # Retention period: 24 months for daily, 60 months for others
    retention_config = {
        "Daily": 24,
        "Weekly": 36,
        "Monthly": 60,
        "Quarterly": 120,
        "Yearly": 240
    }

    try:
        total_deleted = 0

        for period_type, months in retention_config.items():
            cutoff_date = add_months(getdate(today()), -months)

            deleted = frappe.db.delete(
                "KPI Value",
                {
                    "period_type": period_type,
                    "period_end": ["<", cutoff_date]
                }
            )

            if deleted:
                total_deleted += deleted

        if total_deleted:
            frappe.logger().info(f"Cleaned up {total_deleted} old KPI values")

    except Exception as e:
        frappe.log_error(f"Error cleaning up KPI values: {str(e)}", "KPI Cleanup Error")


def update_dashboard_statistics():
    """
    Update dashboard view statistics (Daily task)

    This task aggregates dashboard usage statistics for analytics.
    """
    try:
        # Get dashboards with high view counts
        popular_dashboards = frappe.get_all(
            "Custom Dashboard",
            filters={"is_active": 1},
            fields=["name", "dashboard_name", "view_count"],
            order_by="view_count DESC",
            limit=10
        )

        if popular_dashboards:
            frappe.logger().info(
                f"Top dashboard: {popular_dashboards[0]['dashboard_name']} "
                f"with {popular_dashboards[0]['view_count']} views"
            )

    except Exception as e:
        frappe.log_error(f"Error updating dashboard statistics: {str(e)}", "Dashboard Stats Error")


def check_kpi_alerts():
    """
    Check for KPI threshold breaches and send alerts (Daily task)

    This task checks KPI values against thresholds and sends
    notifications to responsible users when thresholds are breached.
    """
    try:
        # Get KPIs with red status
        red_kpis = frappe.db.sql("""
            SELECT DISTINCT
                kv.kpi,
                kd.kpi_name,
                kd.responsible_role,
                kd.data_owner,
                kv.value,
                kv.status,
                kd.target_value
            FROM `tabKPI Value` kv
            INNER JOIN `tabKPI Definition` kd ON kv.kpi = kd.name
            WHERE kv.status = 'Red'
            AND kd.is_active = 1
            AND kv.period_start = (
                SELECT MAX(period_start)
                FROM `tabKPI Value`
                WHERE kpi = kv.kpi
            )
        """, as_dict=True)

        for kpi in red_kpis:
            # Send notification to data owner
            if kpi.get("data_owner"):
                _send_kpi_alert(kpi)

        if red_kpis:
            frappe.logger().info(f"Sent alerts for {len(red_kpis)} KPIs in red status")

    except Exception as e:
        frappe.log_error(f"Error checking KPI alerts: {str(e)}", "KPI Alert Error")


def _send_kpi_alert(kpi):
    """
    Send KPI alert notification

    Args:
        kpi: Dict with KPI information
    """
    try:
        subject = f"KPI Alert: {kpi['kpi_name']} is in Red Status"
        message = f"""
        <p>Dear User,</p>

        <p>The following KPI has breached its threshold and requires attention:</p>

        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>KPI Name</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{kpi['kpi_name']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Current Value</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{kpi['value']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Target Value</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{kpi['target_value']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd; color: red;"><strong>Red</strong></td>
            </tr>
        </table>

        <p>Please take necessary action to address this issue.</p>

        <p>Best regards,<br>University ERP Analytics</p>
        """

        frappe.sendmail(
            recipients=[kpi["data_owner"]],
            subject=subject,
            message=message
        )

    except Exception as e:
        frappe.log_error(f"Error sending KPI alert: {str(e)}", "KPI Alert Email Error")
