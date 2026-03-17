# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, add_months, getdate, nowdate, get_first_day, get_last_day


def execute(filters=None):
    """Execute communication analytics report"""
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(filters)
    report_summary = get_report_summary(filters)

    return columns, data, None, chart, report_summary


def get_columns(filters):
    """Get report columns based on report type"""
    report_type = filters.get("report_type", "summary")

    if report_type == "summary":
        return [
            {"fieldname": "channel", "label": _("Channel"), "fieldtype": "Data", "width": 120},
            {"fieldname": "total_sent", "label": _("Total Sent"), "fieldtype": "Int", "width": 100},
            {"fieldname": "successful", "label": _("Successful"), "fieldtype": "Int", "width": 100},
            {"fieldname": "failed", "label": _("Failed"), "fieldtype": "Int", "width": 100},
            {"fieldname": "success_rate", "label": _("Success Rate %"), "fieldtype": "Percent", "width": 120},
            {"fieldname": "pending", "label": _("Pending"), "fieldtype": "Int", "width": 100}
        ]
    elif report_type == "daily":
        return [
            {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 120},
            {"fieldname": "emails_sent", "label": _("Emails"), "fieldtype": "Int", "width": 100},
            {"fieldname": "sms_sent", "label": _("SMS"), "fieldtype": "Int", "width": 100},
            {"fieldname": "whatsapp_sent", "label": _("WhatsApp"), "fieldtype": "Int", "width": 100},
            {"fieldname": "push_sent", "label": _("Push"), "fieldtype": "Int", "width": 100},
            {"fieldname": "total", "label": _("Total"), "fieldtype": "Int", "width": 100}
        ]
    elif report_type == "category":
        return [
            {"fieldname": "category", "label": _("Category"), "fieldtype": "Data", "width": 150},
            {"fieldname": "email_count", "label": _("Email"), "fieldtype": "Int", "width": 100},
            {"fieldname": "sms_count", "label": _("SMS"), "fieldtype": "Int", "width": 100},
            {"fieldname": "whatsapp_count", "label": _("WhatsApp"), "fieldtype": "Int", "width": 100},
            {"fieldname": "total", "label": _("Total"), "fieldtype": "Int", "width": 100},
            {"fieldname": "percentage", "label": _("% of Total"), "fieldtype": "Percent", "width": 100}
        ]
    else:  # template_usage
        return [
            {"fieldname": "template_name", "label": _("Template"), "fieldtype": "Data", "width": 200},
            {"fieldname": "channel", "label": _("Channel"), "fieldtype": "Data", "width": 100},
            {"fieldname": "usage_count", "label": _("Usage Count"), "fieldtype": "Int", "width": 100},
            {"fieldname": "success_count", "label": _("Successful"), "fieldtype": "Int", "width": 100},
            {"fieldname": "fail_count", "label": _("Failed"), "fieldtype": "Int", "width": 100},
            {"fieldname": "last_used", "label": _("Last Used"), "fieldtype": "Datetime", "width": 150}
        ]


def get_data(filters):
    """Get report data based on filters"""
    report_type = filters.get("report_type", "summary")
    from_date = filters.get("from_date") or add_days(nowdate(), -30)
    to_date = filters.get("to_date") or nowdate()

    if report_type == "summary":
        return get_summary_data(from_date, to_date)
    elif report_type == "daily":
        return get_daily_data(from_date, to_date)
    elif report_type == "category":
        return get_category_data(from_date, to_date)
    else:
        return get_template_usage_data(from_date, to_date)


def get_summary_data(from_date, to_date):
    """Get channel-wise summary"""
    data = []

    # Email stats from Communication doctype
    email_stats = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN sent_or_received = 'Sent' AND status = 'Linked' THEN 1 ELSE 0 END) as successful,
            SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as pending
        FROM `tabCommunication`
        WHERE communication_type = 'Communication'
        AND communication_medium = 'Email'
        AND DATE(creation) BETWEEN %s AND %s
    """, (from_date, to_date), as_dict=True)[0]

    if email_stats.total:
        data.append({
            "channel": "Email",
            "total_sent": email_stats.total or 0,
            "successful": email_stats.successful or 0,
            "failed": (email_stats.total or 0) - (email_stats.successful or 0) - (email_stats.pending or 0),
            "success_rate": round((email_stats.successful or 0) / email_stats.total * 100, 1) if email_stats.total else 0,
            "pending": email_stats.pending or 0
        })

    # SMS stats
    if frappe.db.table_exists("tabSMS Log"):
        sms_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Sent' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'Queued' THEN 1 ELSE 0 END) as pending
            FROM `tabSMS Log`
            WHERE DATE(creation) BETWEEN %s AND %s
        """, (from_date, to_date), as_dict=True)[0]

        if sms_stats.total:
            data.append({
                "channel": "SMS",
                "total_sent": sms_stats.total or 0,
                "successful": sms_stats.successful or 0,
                "failed": sms_stats.failed or 0,
                "success_rate": round((sms_stats.successful or 0) / sms_stats.total * 100, 1) if sms_stats.total else 0,
                "pending": sms_stats.pending or 0
            })

    # WhatsApp stats
    if frappe.db.table_exists("tabWhatsApp Log"):
        wa_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status IN ('Sent', 'Delivered', 'Read') THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status IN ('Queued', 'Pending') THEN 1 ELSE 0 END) as pending
            FROM `tabWhatsApp Log`
            WHERE direction = 'Outgoing'
            AND DATE(creation) BETWEEN %s AND %s
        """, (from_date, to_date), as_dict=True)[0]

        if wa_stats.total:
            data.append({
                "channel": "WhatsApp",
                "total_sent": wa_stats.total or 0,
                "successful": wa_stats.successful or 0,
                "failed": wa_stats.failed or 0,
                "success_rate": round((wa_stats.successful or 0) / wa_stats.total * 100, 1) if wa_stats.total else 0,
                "pending": wa_stats.pending or 0
            })

    # In-App notifications
    if frappe.db.table_exists("tabUser Notification"):
        inapp_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN `read` = 1 THEN 1 ELSE 0 END) as read_count
            FROM `tabUser Notification`
            WHERE DATE(creation) BETWEEN %s AND %s
        """, (from_date, to_date), as_dict=True)[0]

        if inapp_stats.total:
            data.append({
                "channel": "In-App",
                "total_sent": inapp_stats.total or 0,
                "successful": inapp_stats.total or 0,  # All in-app are considered delivered
                "failed": 0,
                "success_rate": 100.0,
                "pending": 0
            })

    return data


def get_daily_data(from_date, to_date):
    """Get day-wise communication breakdown"""
    data = []

    # Generate date range
    current_date = getdate(from_date)
    end_date = getdate(to_date)

    while current_date <= end_date:
        date_str = str(current_date)

        row = {
            "date": current_date,
            "emails_sent": 0,
            "sms_sent": 0,
            "whatsapp_sent": 0,
            "push_sent": 0,
            "total": 0
        }

        # Emails
        row["emails_sent"] = frappe.db.count(
            "Communication",
            filters={
                "communication_type": "Communication",
                "communication_medium": "Email",
                "creation": ["between", [f"{date_str} 00:00:00", f"{date_str} 23:59:59"]]
            }
        ) or 0

        # SMS
        if frappe.db.table_exists("tabSMS Log"):
            row["sms_sent"] = frappe.db.count(
                "SMS Log",
                filters={"creation": ["between", [f"{date_str} 00:00:00", f"{date_str} 23:59:59"]]}
            ) or 0

        # WhatsApp
        if frappe.db.table_exists("tabWhatsApp Log"):
            row["whatsapp_sent"] = frappe.db.count(
                "WhatsApp Log",
                filters={
                    "direction": "Outgoing",
                    "creation": ["between", [f"{date_str} 00:00:00", f"{date_str} 23:59:59"]]
                }
            ) or 0

        row["total"] = row["emails_sent"] + row["sms_sent"] + row["whatsapp_sent"] + row["push_sent"]

        if row["total"] > 0:  # Only include days with activity
            data.append(row)

        current_date = add_days(current_date, 1)

    return data


def get_category_data(from_date, to_date):
    """Get category-wise communication breakdown"""
    categories = {
        "Fee & Payments": {"email": 0, "sms": 0, "whatsapp": 0},
        "Academic": {"email": 0, "sms": 0, "whatsapp": 0},
        "Library": {"email": 0, "sms": 0, "whatsapp": 0},
        "Placement": {"email": 0, "sms": 0, "whatsapp": 0},
        "Emergency": {"email": 0, "sms": 0, "whatsapp": 0},
        "General": {"email": 0, "sms": 0, "whatsapp": 0}
    }

    # Get from User Notification if available
    if frappe.db.table_exists("tabUser Notification"):
        cat_stats = frappe.db.sql("""
            SELECT category, COUNT(*) as count
            FROM `tabUser Notification`
            WHERE DATE(creation) BETWEEN %s AND %s
            GROUP BY category
        """, (from_date, to_date), as_dict=True)

        for stat in cat_stats:
            cat = stat.category or "General"
            if cat in categories:
                categories[cat]["email"] += stat.count

    # Calculate totals and percentages
    data = []
    grand_total = sum(
        cat["email"] + cat["sms"] + cat["whatsapp"]
        for cat in categories.values()
    )

    for cat_name, counts in categories.items():
        total = counts["email"] + counts["sms"] + counts["whatsapp"]
        if total > 0 or True:  # Show all categories
            data.append({
                "category": cat_name,
                "email_count": counts["email"],
                "sms_count": counts["sms"],
                "whatsapp_count": counts["whatsapp"],
                "total": total,
                "percentage": round(total / grand_total * 100, 1) if grand_total else 0
            })

    return data


def get_template_usage_data(from_date, to_date):
    """Get template usage statistics"""
    data = []

    # Notification templates
    if frappe.db.table_exists("tabNotification Template"):
        templates = frappe.get_all(
            "Notification Template",
            fields=["name", "template_name", "send_email", "send_sms"]
        )

        for template in templates:
            channel = "Email" if template.send_email else ("SMS" if template.send_sms else "Mixed")

            # Count usage from User Notification (notification_type stores template reference)
            usage_count = frappe.db.count(
                "User Notification",
                filters={
                    "notification_type": template.name,
                    "creation": ["between", [from_date, to_date]]
                }
            ) if frappe.db.table_exists("tabUser Notification") else 0

            if usage_count > 0:
                data.append({
                    "template_name": template.template_name or template.name,
                    "channel": channel,
                    "usage_count": usage_count,
                    "success_count": usage_count,
                    "fail_count": 0,
                    "last_used": frappe.db.get_value(
                        "User Notification",
                        filters={"notification_type": template.name},
                        fieldname="creation",
                        order_by="creation desc"
                    ) if frappe.db.table_exists("tabUser Notification") else None
                })

    # WhatsApp templates
    if frappe.db.table_exists("tabWhatsApp Log"):
        wa_templates = frappe.db.sql("""
            SELECT
                template_name,
                COUNT(*) as usage_count,
                SUM(CASE WHEN status IN ('Sent', 'Delivered', 'Read') THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as fail_count,
                MAX(creation) as last_used
            FROM `tabWhatsApp Log`
            WHERE template_name IS NOT NULL
            AND DATE(creation) BETWEEN %s AND %s
            GROUP BY template_name
            ORDER BY usage_count DESC
        """, (from_date, to_date), as_dict=True)

        for t in wa_templates:
            data.append({
                "template_name": t.template_name,
                "channel": "WhatsApp",
                "usage_count": t.usage_count,
                "success_count": t.success_count,
                "fail_count": t.fail_count,
                "last_used": t.last_used
            })

    return data


def get_chart_data(filters):
    """Get chart data for visualization"""
    report_type = filters.get("report_type", "summary")
    from_date = filters.get("from_date") or add_days(nowdate(), -30)
    to_date = filters.get("to_date") or nowdate()

    if report_type == "summary":
        data = get_summary_data(from_date, to_date)
        return {
            "data": {
                "labels": [d["channel"] for d in data],
                "datasets": [
                    {
                        "name": _("Successful"),
                        "values": [d["successful"] for d in data]
                    },
                    {
                        "name": _("Failed"),
                        "values": [d["failed"] for d in data]
                    }
                ]
            },
            "type": "bar",
            "colors": ["#28a745", "#dc3545"]
        }
    elif report_type == "daily":
        data = get_daily_data(from_date, to_date)
        return {
            "data": {
                "labels": [str(d["date"]) for d in data],
                "datasets": [
                    {"name": _("Email"), "values": [d["emails_sent"] for d in data]},
                    {"name": _("SMS"), "values": [d["sms_sent"] for d in data]},
                    {"name": _("WhatsApp"), "values": [d["whatsapp_sent"] for d in data]}
                ]
            },
            "type": "line",
            "colors": ["#007bff", "#28a745", "#25D366"]
        }
    else:
        return None


def get_report_summary(filters):
    """Get report summary cards"""
    from_date = filters.get("from_date") or add_days(nowdate(), -30)
    to_date = filters.get("to_date") or nowdate()

    summary_data = get_summary_data(from_date, to_date)

    total_sent = sum(d["total_sent"] for d in summary_data)
    total_successful = sum(d["successful"] for d in summary_data)
    total_failed = sum(d["failed"] for d in summary_data)

    return [
        {
            "value": total_sent,
            "label": _("Total Messages"),
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": total_successful,
            "label": _("Delivered"),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "value": total_failed,
            "label": _("Failed"),
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": round(total_successful / total_sent * 100, 1) if total_sent else 0,
            "label": _("Success Rate"),
            "datatype": "Percent",
            "indicator": "green" if (total_successful / total_sent * 100 if total_sent else 0) > 90 else "orange"
        }
    ]


# ========== Scheduled Report Functions ==========

def generate_weekly_communication_report():
    """Generate and email weekly communication report - scheduled task"""
    from_date = add_days(nowdate(), -7)
    to_date = add_days(nowdate(), -1)

    filters = {
        "report_type": "summary",
        "from_date": from_date,
        "to_date": to_date
    }

    columns, data, _, _, summary = execute(filters)

    # Build HTML report
    html = _build_report_html("Weekly Communication Report", from_date, to_date, data, summary)

    # Get recipients
    recipients = get_report_recipients("weekly")

    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=f"Weekly Communication Report ({from_date} to {to_date})",
            message=html,
            delayed=True
        )

        frappe.log_error(
            f"Weekly communication report sent to {len(recipients)} recipients",
            "Communication Report"
        )


def generate_monthly_communication_report():
    """Generate and email monthly communication report - scheduled task"""
    today = getdate(nowdate())
    from_date = get_first_day(add_months(today, -1))
    to_date = get_last_day(add_months(today, -1))

    filters = {
        "report_type": "summary",
        "from_date": from_date,
        "to_date": to_date
    }

    columns, data, _, _, summary = execute(filters)

    # Build HTML report
    html = _build_report_html("Monthly Communication Report", from_date, to_date, data, summary)

    # Get recipients
    recipients = get_report_recipients("monthly")

    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=f"Monthly Communication Report - {frappe.utils.format_date(from_date, 'MMMM YYYY')}",
            message=html,
            delayed=True
        )

        frappe.log_error(
            f"Monthly communication report sent to {len(recipients)} recipients",
            "Communication Report"
        )


def get_report_recipients(frequency):
    """Get email recipients for reports based on frequency"""
    # Get from settings or return system managers
    recipients = []

    # Try to get from University ERP Settings
    try:
        settings = frappe.get_single("University ERP Settings")
        if frequency == "weekly" and settings.get("weekly_report_recipients"):
            recipients = [r.strip() for r in settings.weekly_report_recipients.split(",")]
        elif frequency == "monthly" and settings.get("monthly_report_recipients"):
            recipients = [r.strip() for r in settings.monthly_report_recipients.split(",")]
    except Exception:
        pass

    # Fallback to system managers
    if not recipients:
        recipients = frappe.get_all(
            "Has Role",
            filters={"role": "System Manager", "parenttype": "User"},
            pluck="parent"
        )

    return recipients


def _build_report_html(title, from_date, to_date, data, summary):
    """Build HTML report content"""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .summary {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .summary-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; min-width: 120px; }}
            .summary-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .summary-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #007bff; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .success {{ color: #28a745; }}
            .danger {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>Period: {frappe.utils.format_date(from_date)} to {frappe.utils.format_date(to_date)}</p>

        <div class="summary">
    """

    for s in summary:
        indicator_class = "success" if s.get("indicator") == "green" else ("danger" if s.get("indicator") == "red" else "")
        html += f"""
            <div class="summary-card">
                <div class="summary-value {indicator_class}">{s['value']}{'%' if s.get('datatype') == 'Percent' else ''}</div>
                <div class="summary-label">{s['label']}</div>
            </div>
        """

    html += """
        </div>

        <h2>Channel Breakdown</h2>
        <table>
            <tr>
                <th>Channel</th>
                <th>Total Sent</th>
                <th>Successful</th>
                <th>Failed</th>
                <th>Success Rate</th>
            </tr>
    """

    for row in data:
        html += f"""
            <tr>
                <td>{row.get('channel', '')}</td>
                <td>{row.get('total_sent', 0)}</td>
                <td class="success">{row.get('successful', 0)}</td>
                <td class="danger">{row.get('failed', 0)}</td>
                <td>{row.get('success_rate', 0)}%</td>
            </tr>
        """

    html += """
        </table>

        <p style="margin-top: 30px; color: #666; font-size: 12px;">
            This is an automated report generated by University ERP Communication System.
        </p>
    </body>
    </html>
    """

    return html
