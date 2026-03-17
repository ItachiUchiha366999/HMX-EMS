# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class NoticeViewLog(Document):
    pass


def log_notice_view(notice_name, user=None):
    """Log a notice view"""
    user = user or frappe.session.user

    # Check if already viewed recently (within last hour)
    recent_view = frappe.db.exists("Notice View Log", {
        "notice": notice_name,
        "user": user,
        "viewed_at": [">=", frappe.utils.add_to_date(now_datetime(), hours=-1)]
    })

    if recent_view:
        return None

    # Detect device type from user agent
    device_type = "Desktop"
    user_agent = ""
    if frappe.request:
        user_agent = frappe.request.headers.get("User-Agent", "")
        ua_lower = user_agent.lower()
        if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            device_type = "Mobile"
        elif "tablet" in ua_lower or "ipad" in ua_lower:
            device_type = "Tablet"

    log = frappe.get_doc({
        "doctype": "Notice View Log",
        "notice": notice_name,
        "user": user,
        "viewed_at": now_datetime(),
        "device_type": device_type,
        "ip_address": frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None,
        "user_agent": user_agent[:500] if user_agent else None
    })
    log.insert(ignore_permissions=True)

    # Update notice view count
    frappe.db.sql("""
        UPDATE `tabNotice Board`
        SET views_count = COALESCE(views_count, 0) + 1
        WHERE name = %s
    """, notice_name)

    return log.name


def get_notice_view_stats(notice_name):
    """Get view statistics for a notice"""
    total_views = frappe.db.count("Notice View Log", {"notice": notice_name})

    unique_viewers = frappe.db.sql("""
        SELECT COUNT(DISTINCT user) FROM `tabNotice View Log`
        WHERE notice = %s
    """, notice_name)[0][0]

    device_breakdown = frappe.db.sql("""
        SELECT device_type, COUNT(*) as count
        FROM `tabNotice View Log`
        WHERE notice = %s
        GROUP BY device_type
    """, notice_name, as_dict=True)

    daily_views = frappe.db.sql("""
        SELECT DATE(viewed_at) as date, COUNT(*) as count
        FROM `tabNotice View Log`
        WHERE notice = %s
        GROUP BY DATE(viewed_at)
        ORDER BY date DESC
        LIMIT 7
    """, notice_name, as_dict=True)

    return {
        "total_views": total_views,
        "unique_viewers": unique_viewers,
        "device_breakdown": {d.device_type: d.count for d in device_breakdown},
        "daily_views": daily_views
    }


# API Endpoints
@frappe.whitelist()
def mark_notice_viewed(notice_name):
    """Mark notice as viewed by current user"""
    return log_notice_view(notice_name, frappe.session.user)


@frappe.whitelist()
def get_view_stats(notice_name):
    """Get notice view statistics"""
    return get_notice_view_stats(notice_name)
