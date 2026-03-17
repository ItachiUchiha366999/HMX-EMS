# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Emergency Broadcast System
Multi-channel emergency notification system for campus safety.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


class EmergencyBroadcast:
    """Handle multi-channel emergency broadcasting"""

    SEVERITY_COLORS = {
        "Critical": "#e74c3c",
        "High": "#e67e22",
        "Medium": "#f39c12",
        "Low": "#3498db"
    }

    ALERT_ICONS = {
        "Fire": "fire",
        "Medical Emergency": "heart",
        "Security Threat": "shield",
        "Natural Disaster": "cloud-rain",
        "Evacuation": "sign-out",
        "Lockdown": "lock",
        "Utility Failure": "plug",
        "Weather Alert": "cloud",
        "Accident": "exclamation-triangle",
        "Other": "bell"
    }

    def __init__(self, alert):
        """Initialize with Emergency Alert document"""
        self.alert = alert
        self.severity_color = self.SEVERITY_COLORS.get(alert.severity, "#666")
        self.alert_icon = self.ALERT_ICONS.get(alert.alert_type, "bell")

    def send_sms(self, recipient):
        """Send emergency SMS"""
        try:
            from university_erp.university_integrations.sms_gateway import get_sms_gateway

            gateway = get_sms_gateway()

            # Format emergency SMS
            message = f"EMERGENCY ALERT: {self.alert.alert_type.upper()}\n"
            message += f"{self.alert.title}\n"
            message += f"{self.alert.message[:100]}"  # Truncate for SMS

            if self.alert.instructions:
                message += f"\nInstructions: {self.alert.instructions[:50]}"

            message += f"\n-{frappe.db.get_single_value('System Settings', 'system_name') or 'University'}"

            gateway.send_sms(recipient.get("mobile_no"), message)

            return {"success": True}

        except Exception as e:
            frappe.log_error(f"Emergency SMS failed: {str(e)}", "Emergency Broadcast")
            return {"success": False, "error": str(e)}

    def send_push(self, recipient):
        """Send emergency push notification"""
        try:
            from university_erp.university_integrations.push_notification import get_push_manager

            manager = get_push_manager()

            result = manager.send_to_user(
                user=recipient.get("user"),
                title=f"EMERGENCY: {self.alert.alert_type}",
                body=self.alert.title,
                data={
                    "type": "emergency",
                    "alert_id": self.alert.name,
                    "severity": self.alert.severity,
                    "alert_type": self.alert.alert_type,
                    "require_ack": self.alert.require_acknowledgment
                },
                click_action=f"/emergency-alert/{self.alert.name}"
            )

            return result

        except Exception as e:
            frappe.log_error(f"Emergency push failed: {str(e)}", "Emergency Broadcast")
            return {"success": False, "error": str(e)}

    def send_whatsapp(self, recipient):
        """Send emergency WhatsApp message"""
        try:
            from university_erp.university_integrations.whatsapp_gateway import get_whatsapp_gateway

            gateway = get_whatsapp_gateway()

            # Format emergency WhatsApp message
            message = f"*EMERGENCY ALERT: {self.alert.alert_type.upper()}*\n\n"
            message += f"*{self.alert.title}*\n\n"
            message += f"{self.alert.message}\n\n"

            if self.alert.instructions:
                message += f"*Safety Instructions:*\n{self.alert.instructions}\n\n"

            if self.alert.affected_buildings:
                message += f"*Affected Areas:* {self.alert.affected_buildings}\n"

            message += f"\nStay safe and follow instructions from authorities."

            gateway.send_text_message(recipient.get("mobile_no"), message)

            return {"success": True}

        except Exception as e:
            frappe.log_error(f"Emergency WhatsApp failed: {str(e)}", "Emergency Broadcast")
            return {"success": False, "error": str(e)}

    def send_email(self, recipient):
        """Send emergency email"""
        try:
            frappe.sendmail(
                recipients=[recipient.get("email")],
                subject=f"EMERGENCY ALERT: {self.alert.alert_type} - {self.alert.title}",
                template="emergency_alert",
                args={
                    "alert": self.alert,
                    "recipient_name": recipient.get("name", ""),
                    "severity_color": self.severity_color,
                    "acknowledge_link": frappe.utils.get_url(f"/api/method/university_erp.university_erp.doctype.emergency_alert.emergency_alert.acknowledge?alert_name={self.alert.name}")
                },
                now=True  # Send immediately, don't queue
            )

            return {"success": True}

        except Exception as e:
            frappe.log_error(f"Emergency email failed: {str(e)}", "Emergency Broadcast")
            return {"success": False, "error": str(e)}

    def send_all_clear(self, recipient):
        """Send all-clear notification"""
        from university_erp.university_erp.notification_center import NotificationCenter

        if recipient.get("user"):
            NotificationCenter.send(
                user=recipient.get("user"),
                title=f"ALL CLEAR: {self.alert.alert_type}",
                message=self.alert.all_clear_message or f"The {self.alert.alert_type.lower()} emergency has been resolved.",
                notification_type="success",
                category="Emergency",
                priority="High",
                link=f"/emergency-alert/{self.alert.name}"
            )


# ========== Quick Broadcast Functions ==========

def quick_broadcast(alert_type, title, message, severity="High", channels=None):
    """
    Quick emergency broadcast without creating a document first

    Args:
        alert_type: Type of alert (Fire, Medical Emergency, etc.)
        title: Alert title
        message: Alert message
        severity: Alert severity (Critical/High/Medium/Low)
        channels: List of channels ['sms', 'push', 'whatsapp', 'email'] or None for all

    Returns:
        Emergency Alert document name
    """
    channels = channels or ["sms", "push", "whatsapp", "email"]

    alert = frappe.get_doc({
        "doctype": "Emergency Alert",
        "alert_type": alert_type,
        "title": title,
        "message": message,
        "severity": severity,
        "target_audience": "All",
        "send_sms": "sms" in channels,
        "send_push": "push" in channels,
        "send_whatsapp": "whatsapp" in channels,
        "send_email": "email" in channels
    })
    alert.insert()
    alert.broadcast()

    return alert.name


def send_fire_alert(location, details=None):
    """Quick fire alert"""
    return quick_broadcast(
        alert_type="Fire",
        title=f"Fire Alert - {location}",
        message=details or f"Fire reported at {location}. Please evacuate immediately using nearest exit.",
        severity="Critical"
    )


def send_lockdown_alert(reason=None):
    """Quick lockdown alert"""
    return quick_broadcast(
        alert_type="Lockdown",
        title="LOCKDOWN - Shelter in Place",
        message=reason or "Campus lockdown in effect. Stay where you are, lock doors, stay away from windows.",
        severity="Critical"
    )


def send_evacuation_alert(locations=None, assembly_point=None):
    """Quick evacuation alert"""
    message = "Evacuation order in effect."
    if locations:
        message += f" Evacuate: {locations}."
    if assembly_point:
        message += f" Proceed to: {assembly_point}."

    return quick_broadcast(
        alert_type="Evacuation",
        title="EVACUATION - Leave Building Now",
        message=message,
        severity="High"
    )


def send_weather_alert(weather_type, details):
    """Quick weather alert"""
    return quick_broadcast(
        alert_type="Weather Alert",
        title=f"Weather Alert - {weather_type}",
        message=details,
        severity="Medium"
    )


# ========== API Endpoints ==========

@frappe.whitelist()
def quick_fire_alert(location, details=None):
    """API endpoint for quick fire alert"""
    if not frappe.has_permission("Emergency Alert", "create"):
        frappe.throw(_("Not authorized"))

    return send_fire_alert(location, details)


@frappe.whitelist()
def quick_lockdown(reason=None):
    """API endpoint for quick lockdown alert"""
    if not frappe.has_permission("Emergency Alert", "create"):
        frappe.throw(_("Not authorized"))

    return send_lockdown_alert(reason)


@frappe.whitelist()
def quick_evacuation(locations=None, assembly_point=None):
    """API endpoint for quick evacuation alert"""
    if not frappe.has_permission("Emergency Alert", "create"):
        frappe.throw(_("Not authorized"))

    return send_evacuation_alert(locations, assembly_point)


@frappe.whitelist()
def send_test_alert():
    """Send a test emergency alert (test mode only)"""
    if not frappe.has_permission("Emergency Alert", "create"):
        frappe.throw(_("Not authorized"))

    alert = frappe.get_doc({
        "doctype": "Emergency Alert",
        "alert_type": "Other",
        "title": "TEST - Emergency Alert System Test",
        "message": "This is a TEST of the emergency alert system. No action required.",
        "severity": "Low",
        "target_audience": "All",
        "send_sms": 0,
        "send_push": 1,
        "send_whatsapp": 0,
        "send_email": 0
    })
    alert.insert()

    # Only send to current user
    frappe.publish_realtime(
        event="emergency_alert",
        message={
            "alert_id": alert.name,
            "alert_type": "Other",
            "severity": "Low",
            "title": alert.title,
            "message": alert.message,
            "is_test": True
        },
        user=frappe.session.user
    )

    return {"success": True, "alert": alert.name, "message": "Test alert sent"}


# ========== Dashboard Data ==========

@frappe.whitelist()
def get_emergency_dashboard():
    """Get emergency dashboard data"""
    active_alerts = frappe.get_all(
        "Emergency Alert",
        filters={"status": "Active"},
        fields=["name", "alert_type", "severity", "title", "broadcast_time",
                "total_recipients", "acknowledgments_received"],
        order_by="broadcast_time desc"
    )

    # Recent resolved
    recent_resolved = frappe.get_all(
        "Emergency Alert",
        filters={"status": "Resolved"},
        fields=["name", "alert_type", "severity", "title", "resolved_at"],
        order_by="resolved_at desc",
        limit=5
    )

    # Stats
    stats = {
        "active_count": len(active_alerts),
        "total_today": frappe.db.count("Emergency Alert", {
            "broadcast_time": [">=", frappe.utils.today()]
        }),
        "total_this_month": frappe.db.count("Emergency Alert", {
            "broadcast_time": [">=", frappe.utils.add_months(frappe.utils.today(), -1)]
        })
    }

    return {
        "active_alerts": active_alerts,
        "recent_resolved": recent_resolved,
        "stats": stats
    }
