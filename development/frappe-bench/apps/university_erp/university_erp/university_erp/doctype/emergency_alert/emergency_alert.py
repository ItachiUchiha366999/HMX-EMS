# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date


class EmergencyAlert(Document):
    def validate(self):
        if not self.initiated_by:
            self.initiated_by = frappe.session.user

    def before_save(self):
        self.calculate_acknowledgment_rate()

    def calculate_acknowledgment_rate(self):
        """Calculate acknowledgment rate percentage"""
        if self.total_recipients and self.total_recipients > 0:
            self.acknowledgment_rate = (self.acknowledgments_received / self.total_recipients) * 100
        else:
            self.acknowledgment_rate = 0

    @frappe.whitelist()
    def broadcast(self):
        """Broadcast emergency alert to all channels"""
        if self.status != "Draft":
            frappe.throw(_("Only draft alerts can be broadcast"))

        self.status = "Active"
        self.broadcast_time = now_datetime()
        self.save()

        # Get target users
        recipients = self.get_recipients()
        self.db_set("total_recipients", len(recipients), update_modified=False)

        # Send through all enabled channels
        from university_erp.university_erp.emergency_broadcast import EmergencyBroadcast

        broadcaster = EmergencyBroadcast(self)

        # Track delivery counts
        sms_count = 0
        push_count = 0
        whatsapp_count = 0
        email_count = 0

        for recipient in recipients:
            if self.send_sms and recipient.get("mobile_no"):
                try:
                    broadcaster.send_sms(recipient)
                    sms_count += 1
                except Exception:
                    pass

            if self.send_push and recipient.get("user"):
                try:
                    broadcaster.send_push(recipient)
                    push_count += 1
                except Exception:
                    pass

            if self.send_whatsapp and recipient.get("mobile_no"):
                try:
                    broadcaster.send_whatsapp(recipient)
                    whatsapp_count += 1
                except Exception:
                    pass

            if self.send_email and recipient.get("email"):
                try:
                    broadcaster.send_email(recipient)
                    email_count += 1
                except Exception:
                    pass

        # Update counts
        self.db_set({
            "sms_sent": sms_count,
            "push_sent": push_count,
            "whatsapp_sent": whatsapp_count,
            "email_sent": email_count
        }, update_modified=False)

        # Send real-time alert to all connected users
        frappe.publish_realtime(
            event="emergency_alert",
            message={
                "alert_id": self.name,
                "alert_type": self.alert_type,
                "severity": self.severity,
                "title": self.title,
                "message": self.message,
                "instructions": self.instructions,
                "play_audio": self.play_audio_alert
            },
            user="all"
        )

        frappe.msgprint(_("Emergency alert broadcast initiated to {0} recipients").format(len(recipients)))

        return {"success": True, "recipients": len(recipients)}

    @frappe.whitelist()
    def resolve(self, notes=None):
        """Mark alert as resolved and send all-clear"""
        if self.status != "Active":
            frappe.throw(_("Only active alerts can be resolved"))

        self.status = "Resolved"
        self.resolved_at = now_datetime()
        self.resolved_by = frappe.session.user
        if notes:
            self.resolution_notes = notes
        self.save()

        # Send all-clear message if provided
        if self.all_clear_message:
            self.send_all_clear()

        # Notify via real-time
        frappe.publish_realtime(
            event="emergency_resolved",
            message={
                "alert_id": self.name,
                "alert_type": self.alert_type,
                "all_clear_message": self.all_clear_message
            },
            user="all"
        )

        frappe.msgprint(_("Emergency alert resolved. All-clear sent."))

        return {"success": True}

    @frappe.whitelist()
    def cancel_alert(self):
        """Cancel the alert"""
        if self.status not in ["Draft", "Active"]:
            frappe.throw(_("Cannot cancel this alert"))

        self.status = "Cancelled"
        self.save()

        if self.status == "Active":
            # Notify users of cancellation
            frappe.publish_realtime(
                event="emergency_cancelled",
                message={
                    "alert_id": self.name,
                    "message": f"Alert '{self.title}' has been cancelled"
                },
                user="all"
            )

        return {"success": True}

    def get_recipients(self):
        """Get list of recipients based on target audience"""
        recipients = []

        if self.target_audience == "All":
            # Get all students, faculty, staff
            recipients.extend(self._get_all_students())
            recipients.extend(self._get_all_faculty())
            recipients.extend(self._get_all_staff())

        elif self.target_audience == "Students":
            recipients = self._get_all_students()

        elif self.target_audience == "Faculty":
            recipients = self._get_all_faculty()

        elif self.target_audience == "Staff":
            recipients = self._get_all_staff()

        elif self.target_audience == "Visitors":
            # Get recent visitors if visitor management exists
            recipients = self._get_visitors()

        elif self.target_audience in ["Specific Buildings", "Specific Zones"]:
            # Location-based targeting (requires location tracking)
            recipients = self._get_by_location()

        return recipients

    def _get_all_students(self):
        """Get all active students"""
        return frappe.db.sql("""
            SELECT s.user, s.student_email_id as email, s.student_mobile_number as mobile_no,
                   CONCAT(s.first_name, ' ', IFNULL(s.last_name, '')) as name, 'Student' as type
            FROM `tabStudent` s
            WHERE s.enabled = 1 AND s.user IS NOT NULL
        """, as_dict=True)

    def _get_all_faculty(self):
        """Get all active faculty"""
        return frappe.db.sql("""
            SELECT i.user, u.email, e.cell_number as mobile_no,
                   e.employee_name as name, 'Faculty' as type
            FROM `tabInstructor` i
            LEFT JOIN `tabUser` u ON u.name = i.user
            LEFT JOIN `tabEmployee` e ON e.user_id = i.user
            WHERE i.user IS NOT NULL
        """, as_dict=True)

    def _get_all_staff(self):
        """Get all active staff"""
        return frappe.db.sql("""
            SELECT e.user_id as user, u.email, e.cell_number as mobile_no,
                   e.employee_name as name, 'Staff' as type
            FROM `tabEmployee` e
            JOIN `tabUser` u ON u.name = e.user_id
            WHERE e.status = 'Active' AND e.user_id IS NOT NULL
        """, as_dict=True)

    def _get_visitors(self):
        """Get visitors (if visitor management exists)"""
        # Check if Visitor doctype exists
        if frappe.db.exists("DocType", "Visitor"):
            return frappe.db.sql("""
                SELECT v.user, v.email, v.mobile_no, v.visitor_name as name, 'Visitor' as type
                FROM `tabVisitor` v
                WHERE v.check_in IS NOT NULL AND v.check_out IS NULL
            """, as_dict=True)
        return []

    def _get_by_location(self):
        """Get users by location (placeholder for location tracking)"""
        # This would integrate with location tracking system
        # For now, returns all users
        recipients = []
        recipients.extend(self._get_all_students())
        recipients.extend(self._get_all_faculty())
        recipients.extend(self._get_all_staff())
        return recipients

    def send_all_clear(self):
        """Send all-clear notification"""
        recipients = self.get_recipients()

        from university_erp.university_erp.emergency_broadcast import EmergencyBroadcast
        broadcaster = EmergencyBroadcast(self)

        for recipient in recipients:
            if recipient.get("user"):
                broadcaster.send_all_clear(recipient)


def acknowledge_alert(alert_name, user=None, location=None, status="Safe"):
    """Record acknowledgment of emergency alert"""
    user = user or frappe.session.user

    # Check if already acknowledged
    existing = frappe.db.exists("Emergency Acknowledgment", {
        "emergency_alert": alert_name,
        "user": user
    })

    if existing:
        return {"success": True, "message": "Already acknowledged"}

    # Create acknowledgment
    ack = frappe.get_doc({
        "doctype": "Emergency Acknowledgment",
        "emergency_alert": alert_name,
        "user": user,
        "status": status,
        "location": location,
        "acknowledged_at": now_datetime()
    })
    ack.insert(ignore_permissions=True)

    # Update alert count
    alert = frappe.get_doc("Emergency Alert", alert_name)
    alert.db_set("acknowledgments_received", alert.acknowledgments_received + 1, update_modified=False)

    return {"success": True, "acknowledgment": ack.name}


# ========== API Endpoints ==========

@frappe.whitelist()
def broadcast_alert(alert_name):
    """Broadcast emergency alert - API endpoint"""
    alert = frappe.get_doc("Emergency Alert", alert_name)
    return alert.broadcast()


@frappe.whitelist()
def resolve_alert(alert_name, notes=None):
    """Resolve emergency alert - API endpoint"""
    alert = frappe.get_doc("Emergency Alert", alert_name)
    return alert.resolve(notes)


@frappe.whitelist()
def cancel_alert(alert_name):
    """Cancel emergency alert - API endpoint"""
    alert = frappe.get_doc("Emergency Alert", alert_name)
    return alert.cancel_alert()


@frappe.whitelist()
def acknowledge(alert_name, location=None, status="Safe"):
    """Acknowledge emergency alert - API endpoint"""
    return acknowledge_alert(alert_name, frappe.session.user, location, status)


@frappe.whitelist()
def get_active_alerts():
    """Get all active emergency alerts"""
    alerts = frappe.get_all(
        "Emergency Alert",
        filters={"status": "Active"},
        fields=[
            "name", "alert_type", "severity", "title", "message",
            "instructions", "broadcast_time", "expires_at",
            "require_acknowledgment", "affected_buildings", "affected_zones"
        ],
        order_by="severity desc, broadcast_time desc"
    )

    # Check if user has acknowledged each alert
    user = frappe.session.user
    for alert in alerts:
        alert["acknowledged"] = frappe.db.exists("Emergency Acknowledgment", {
            "emergency_alert": alert.name,
            "user": user
        })

    return alerts


@frappe.whitelist()
def get_alert_acknowledgments(alert_name, status=None):
    """Get acknowledgments for an alert"""
    filters = {"emergency_alert": alert_name}
    if status:
        filters["status"] = status

    return frappe.get_all(
        "Emergency Acknowledgment",
        filters=filters,
        fields=["user", "status", "location", "acknowledged_at", "notes"],
        order_by="acknowledged_at desc"
    )


@frappe.whitelist()
def get_unacknowledged_users(alert_name):
    """Get users who haven't acknowledged the alert"""
    alert = frappe.get_doc("Emergency Alert", alert_name)
    recipients = alert.get_recipients()

    acknowledged = frappe.get_all(
        "Emergency Acknowledgment",
        filters={"emergency_alert": alert_name},
        pluck="user"
    )

    unacknowledged = [r for r in recipients if r.get("user") not in acknowledged]

    return {
        "total_recipients": len(recipients),
        "acknowledged": len(acknowledged),
        "unacknowledged_count": len(unacknowledged),
        "unacknowledged_users": unacknowledged
    }


@frappe.whitelist(allow_guest=True)
def get_emergency_contacts():
    """Get emergency contact numbers for the university"""
    # Try to get from University Settings or a dedicated settings doc
    contacts = {
        "police": "100",
        "fire": "101",
        "ambulance": "102"
    }

    # Check for University Settings DocType
    if frappe.db.exists("DocType", "University Settings"):
        try:
            settings = frappe.get_single("University Settings")
            if hasattr(settings, "campus_security_phone"):
                contacts["campus_security"] = settings.campus_security_phone
            if hasattr(settings, "control_room_phone"):
                contacts["control_room"] = settings.control_room_phone
            if hasattr(settings, "medical_center_phone"):
                contacts["medical_center"] = settings.medical_center_phone
        except Exception:
            pass

    # Fallback: check Push Notification Settings or other settings
    if "campus_security" not in contacts:
        # Try to get from custom fields or website settings
        campus_security = frappe.db.get_single_value(
            "Website Settings", "campus_security_phone"
        ) if frappe.db.has_column("Website Settings", "campus_security_phone") else None

        if campus_security:
            contacts["campus_security"] = campus_security

    return contacts


@frappe.whitelist()
def quick_fire_alert(title=None, message=None, instructions=None):
    """Quick method to create and broadcast a fire alert"""
    alert = frappe.get_doc({
        "doctype": "Emergency Alert",
        "alert_type": "Fire",
        "severity": "Critical",
        "title": title or "FIRE ALERT - Evacuate Immediately",
        "message": message or "A fire has been reported on campus. Please evacuate immediately using the nearest fire exit.",
        "instructions": instructions or "1. Stay calm\n2. Use stairs, not elevators\n3. Proceed to designated assembly points\n4. Do not re-enter building until all-clear is given",
        "send_sms": 1,
        "send_push": 1,
        "send_email": 1,
        "play_audio_alert": 1,
        "require_acknowledgment": 1,
        "target_audience": "All"
    })
    alert.insert(ignore_permissions=True)
    alert.broadcast()
    return {"success": True, "alert": alert.name}


@frappe.whitelist()
def quick_lockdown(title=None, message=None, instructions=None):
    """Quick method to create and broadcast a lockdown alert"""
    alert = frappe.get_doc({
        "doctype": "Emergency Alert",
        "alert_type": "Lockdown",
        "severity": "Critical",
        "title": title or "LOCKDOWN - Secure in Place",
        "message": message or "The campus is under lockdown. Please secure yourself immediately.",
        "instructions": instructions or "1. Lock all doors and windows\n2. Turn off lights\n3. Stay away from windows\n4. Silence phones\n5. Wait for all-clear announcement",
        "send_sms": 1,
        "send_push": 1,
        "send_email": 1,
        "play_audio_alert": 1,
        "require_acknowledgment": 1,
        "target_audience": "All"
    })
    alert.insert(ignore_permissions=True)
    alert.broadcast()
    return {"success": True, "alert": alert.name}


@frappe.whitelist()
def quick_evacuation(title=None, message=None, instructions=None, buildings=None):
    """Quick method to create and broadcast an evacuation alert"""
    alert = frappe.get_doc({
        "doctype": "Emergency Alert",
        "alert_type": "Evacuation",
        "severity": "Critical",
        "title": title or "EVACUATION REQUIRED",
        "message": message or "Please evacuate the building immediately. Proceed to designated assembly areas.",
        "instructions": instructions or "1. Leave all belongings\n2. Use nearest emergency exit\n3. Do not use elevators\n4. Assist others if possible\n5. Proceed to assembly point",
        "affected_buildings": buildings,
        "send_sms": 1,
        "send_push": 1,
        "send_email": 1,
        "play_audio_alert": 1,
        "require_acknowledgment": 1,
        "target_audience": "All"
    })
    alert.insert(ignore_permissions=True)
    alert.broadcast()
    return {"success": True, "alert": alert.name}


@frappe.whitelist()
def send_test_alert():
    """Send a test emergency alert (does not broadcast)"""
    user = frappe.session.user

    frappe.publish_realtime(
        event="emergency_alert",
        message={
            "alert_id": "TEST-" + frappe.generate_hash(length=8),
            "alert_type": "Test Alert",
            "severity": "Low",
            "title": "TEST ALERT - This is a test",
            "message": "This is a test of the emergency alert system. No action is required.",
            "instructions": "This is only a test. In an actual emergency, follow the instructions provided.",
            "play_audio": False
        },
        user=user
    )

    return {"success": True, "message": "Test alert sent to current user"}


@frappe.whitelist()
def get_emergency_dashboard():
    """Get emergency dashboard statistics"""
    # Active alerts
    active_alerts = frappe.db.count("Emergency Alert", {"status": "Active"})

    # Alerts today
    today = frappe.utils.today()
    alerts_today = frappe.db.count("Emergency Alert", {
        "creation": [">=", today]
    })

    # Recent alerts
    recent_alerts = frappe.get_all(
        "Emergency Alert",
        filters={},
        fields=["name", "alert_type", "severity", "status", "title", "broadcast_time"],
        order_by="creation desc",
        limit=5
    )

    # Acknowledgment stats for active alerts
    acknowledgment_stats = []
    active = frappe.get_all("Emergency Alert", filters={"status": "Active"}, pluck="name")
    for alert_name in active:
        alert = frappe.get_doc("Emergency Alert", alert_name)
        acknowledgment_stats.append({
            "name": alert_name,
            "title": alert.title,
            "total": alert.total_recipients or 0,
            "acknowledged": alert.acknowledgments_received or 0,
            "rate": alert.acknowledgment_rate or 0
        })

    return {
        "active_alerts": active_alerts,
        "alerts_today": alerts_today,
        "recent_alerts": recent_alerts,
        "acknowledgment_stats": acknowledgment_stats
    }
