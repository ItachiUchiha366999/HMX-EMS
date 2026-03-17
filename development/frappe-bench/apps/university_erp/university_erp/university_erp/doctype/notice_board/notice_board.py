# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, getdate


class NoticeBoard(Document):
    def validate(self):
        self.validate_dates()

    def validate_dates(self):
        """Validate publish and expiry dates"""
        if self.expiry_date and getdate(self.expiry_date) < getdate(self.publish_date):
            frappe.throw(_("Expiry date cannot be before publish date"))

    def on_submit(self):
        """Send notifications when notice is submitted"""
        # Only send notifications if publish date is today or earlier
        if getdate(self.publish_date) <= getdate(today()):
            self.send_notifications()

    def on_cancel(self):
        """Handle notice cancellation"""
        pass

    def send_notifications(self):
        """Send notifications through selected channels"""
        target_users = self.get_target_users()

        if not target_users:
            return

        notifications_sent = 0

        # In-app notifications for all
        from university_erp.university_erp.notification_center import NotificationCenter

        for user_info in target_users:
            if user_info.get("user"):
                NotificationCenter.send(
                    user=user_info.get("user"),
                    title=f"New Notice: {self.title}",
                    message=self.title,
                    notification_type="announcement",
                    link=f"/notice-board/{self.name}",
                    category=self.notice_type
                )
                notifications_sent += 1

        # Email notifications
        if self.send_email:
            emails = [u.get("email") for u in target_users if u.get("email")]
            if emails:
                self._send_email_notifications(emails)

        # SMS notifications
        if self.send_sms:
            self._send_sms_notifications(target_users)

        # Push notifications
        if self.send_push:
            self._send_push_notifications(target_users)

        # WhatsApp notifications
        if self.send_whatsapp:
            self._send_whatsapp_notifications(target_users)

        # Update notifications sent count
        self.db_set("notifications_sent", notifications_sent, update_modified=False)

    def get_target_users(self):
        """Get list of target users based on audience type"""
        users = []

        if self.audience_type == "All":
            users = frappe.get_all(
                "User",
                filters={"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]},
                fields=["name as user", "email", "mobile_no"]
            )

        elif self.audience_type == "Students Only":
            students = frappe.get_all(
                "Student",
                filters={"enabled": 1},
                fields=["user", "student_email_id as email", "student_mobile_number as mobile_no"]
            )
            users = [s for s in students if s.user]

        elif self.audience_type == "Faculty Only":
            instructors = frappe.db.sql("""
                SELECT i.user, u.email, e.cell_number as mobile_no
                FROM `tabInstructor` i
                LEFT JOIN `tabUser` u ON u.name = i.user
                LEFT JOIN `tabEmployee` e ON e.user_id = i.user
                WHERE i.user IS NOT NULL
            """, as_dict=True)
            users = instructors

        elif self.audience_type == "Staff Only":
            employees = frappe.db.sql("""
                SELECT e.user_id as user, u.email, e.cell_number as mobile_no
                FROM `tabEmployee` e
                JOIN `tabUser` u ON u.name = e.user_id
                WHERE e.user_id IS NOT NULL AND e.status = 'Active'
            """, as_dict=True)
            users = employees

        elif self.audience_type == "Parents Only":
            guardians = frappe.get_all(
                "Guardian",
                fields=["user", "email_address as email", "mobile_number as mobile_no"]
            )
            users = [g for g in guardians if g.user]

        elif self.audience_type == "Specific Programs":
            target_programs = [p.program for p in self.target_programs]
            if target_programs:
                students = frappe.db.sql("""
                    SELECT DISTINCT s.user, s.student_email_id as email, s.student_mobile_number as mobile_no
                    FROM `tabStudent` s
                    JOIN `tabProgram Enrollment` pe ON pe.student = s.name
                    WHERE pe.program IN %s AND pe.docstatus = 1 AND s.user IS NOT NULL
                """, (target_programs,), as_dict=True)
                users = students

        elif self.audience_type == "Specific Departments":
            target_depts = [d.department for d in self.target_departments]
            if target_depts:
                employees = frappe.db.sql("""
                    SELECT e.user_id as user, u.email, e.cell_number as mobile_no
                    FROM `tabEmployee` e
                    JOIN `tabUser` u ON u.name = e.user_id
                    WHERE e.department IN %s AND e.user_id IS NOT NULL
                """, (target_depts,), as_dict=True)
                users = employees

        return users

    def _send_email_notifications(self, emails):
        """Send email notifications"""
        try:
            frappe.sendmail(
                recipients=emails,
                subject=f"Notice: {self.title}",
                template="notice_board_notification",
                args={
                    "notice": self,
                    "link": frappe.utils.get_url(f"/notice-board/{self.name}")
                },
                reference_doctype="Notice Board",
                reference_name=self.name,
                delayed=True
            )
        except Exception as e:
            frappe.log_error(f"Notice email failed: {str(e)}", "Notice Board")

    def _send_sms_notifications(self, users):
        """Send SMS notifications"""
        try:
            from university_erp.university_integrations.sms_gateway import get_sms_gateway

            gateway = get_sms_gateway()
            message = f"New Notice: {self.title}. Visit portal for details. -University"

            for user in users:
                if user.get("mobile_no"):
                    try:
                        gateway.send_sms(user.mobile_no, message)
                    except Exception:
                        pass

        except Exception as e:
            frappe.log_error(f"Notice SMS failed: {str(e)}", "Notice Board")

    def _send_push_notifications(self, users):
        """Send push notifications"""
        try:
            from university_erp.university_integrations.push_notification import get_push_manager

            manager = get_push_manager()

            for user in users:
                if user.get("user"):
                    try:
                        manager.send_to_user(
                            user=user.user,
                            title=f"New Notice: {self.notice_type}",
                            body=self.title,
                            data={
                                "type": "notice",
                                "notice_id": self.name
                            }
                        )
                    except Exception:
                        pass

        except Exception as e:
            frappe.log_error(f"Notice push failed: {str(e)}", "Notice Board")

    def _send_whatsapp_notifications(self, users):
        """Send WhatsApp notifications"""
        try:
            from university_erp.university_integrations.whatsapp_gateway import get_whatsapp_gateway

            gateway = get_whatsapp_gateway()

            for user in users:
                if user.get("mobile_no"):
                    try:
                        gateway.send_text_message(
                            user.mobile_no,
                            f"*New Notice: {self.notice_type}*\n\n{self.title}\n\nVisit the student portal for details."
                        )
                    except Exception:
                        pass

        except Exception as e:
            frappe.log_error(f"Notice WhatsApp failed: {str(e)}", "Notice Board")

    def increment_view_count(self):
        """Increment view count"""
        self.db_set("views_count", (self.views_count or 0) + 1, update_modified=False)


def is_notice_for_user(notice, user):
    """Check if notice is applicable to user"""
    if notice.audience_type == "All":
        return True

    roles = frappe.get_roles(user)

    if notice.audience_type == "Students Only" and "Student" in roles:
        return True
    if notice.audience_type == "Faculty Only" and ("Instructor" in roles or "Faculty" in roles):
        return True
    if notice.audience_type == "Staff Only" and "Employee" in roles:
        return True
    if notice.audience_type == "Parents Only" and "Guardian" in roles:
        return True

    # Check specific programs
    if notice.audience_type == "Specific Programs":
        student = frappe.db.get_value("Student", {"user": user}, "name")
        if student:
            student_program = frappe.db.get_value(
                "Program Enrollment",
                {"student": student, "docstatus": 1},
                "program"
            )
            target_programs = frappe.get_all(
                "Notice Target Program",
                filters={"parent": notice.name},
                pluck="program"
            )
            if student_program in target_programs:
                return True

    # Check specific departments
    if notice.audience_type == "Specific Departments":
        employee = frappe.db.get_value("Employee", {"user_id": user}, ["department"], as_dict=True)
        if employee:
            target_depts = frappe.get_all(
                "Notice Target Department",
                filters={"parent": notice.name},
                pluck="department"
            )
            if employee.department in target_depts:
                return True

    return False


# ========== API Endpoints ==========

@frappe.whitelist()
def get_notices(notice_type=None, limit=20):
    """Get active notices for current user"""
    user = frappe.session.user

    filters = {
        "docstatus": 1,
        "publish_date": ["<=", today()]
    }

    if notice_type:
        filters["notice_type"] = notice_type

    # Get all active notices
    notices = frappe.get_all(
        "Notice Board",
        filters=filters,
        or_filters=[
            ["expiry_date", "is", "not set"],
            ["expiry_date", ">=", today()]
        ],
        fields=[
            "name", "title", "notice_type", "priority", "publish_date",
            "content", "attachment", "is_pinned", "audience_type", "views_count"
        ],
        order_by="is_pinned desc, priority desc, publish_date desc",
        limit=int(limit)
    )

    # Filter by user applicability
    applicable_notices = []
    for notice in notices:
        notice_doc = frappe._dict(notice)
        notice_doc.name = notice.name  # Ensure name is set

        if is_notice_for_user(notice_doc, user):
            applicable_notices.append(notice)

    return applicable_notices


@frappe.whitelist()
def get_notice_detail(notice_name):
    """Get notice details"""
    notice = frappe.get_doc("Notice Board", notice_name)

    if notice.docstatus != 1:
        frappe.throw(_("Notice not found"))

    if not is_notice_for_user(notice, frappe.session.user):
        frappe.throw(_("You don't have permission to view this notice"))

    # Increment view count
    notice.increment_view_count()

    return notice.as_dict()


@frappe.whitelist()
def get_notice_types():
    """Get list of notice types"""
    return [
        "General", "Academic", "Examination", "Admission",
        "Placement", "Hostel", "Library", "Sports", "Cultural", "Emergency"
    ]
