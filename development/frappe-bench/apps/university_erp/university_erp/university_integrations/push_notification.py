# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Push Notification Manager
Supports: Firebase Cloud Messaging (FCM), OneSignal
"""

import frappe
from frappe import _
import requests
import json


class PushNotificationManager:
    """Manage push notifications across platforms"""

    def __init__(self):
        self.settings = frappe.get_single("Push Notification Settings")

        if not self.settings.enabled:
            frappe.throw(_("Push notifications are not enabled"))

        self.provider = self.settings.provider

    def send_to_user(self, user, title, body, data=None, image=None, click_action=None):
        """
        Send push notification to a user (all their devices)

        Args:
            user: User ID/email
            title: Notification title
            body: Notification body
            data: Additional data payload (dict)
            image: Image URL for rich notification
            click_action: URL/action on notification click

        Returns:
            dict with success status and results per device
        """
        from university_erp.university_integrations.doctype.user_device_token.user_device_token import get_user_tokens

        tokens = get_user_tokens(user)

        if not tokens:
            return {"success": False, "error": "No device tokens found for user"}

        results = []
        for token_info in tokens:
            result = self.send_to_token(
                token=token_info.token,
                title=title,
                body=body,
                data=data,
                image=image,
                click_action=click_action,
                platform=token_info.platform,
                user=user
            )
            results.append({
                "device": token_info.device_name or token_info.platform,
                "success": result.get("success", False),
                "message_id": result.get("message_id")
            })

        success_count = sum(1 for r in results if r["success"])

        return {
            "success": success_count > 0,
            "total_devices": len(tokens),
            "successful": success_count,
            "results": results
        }

    def send_to_token(self, token, title, body, data=None, image=None, click_action=None, platform="android", user=None):
        """
        Send push notification to a specific device token

        Args:
            token: Device push token
            title: Notification title
            body: Notification body
            data: Additional data payload
            image: Image URL
            click_action: Click action URL
            platform: Device platform (android/ios/web)
            user: User for logging

        Returns:
            dict with success, message_id, log
        """
        from university_erp.university_integrations.doctype.push_notification_log.push_notification_log import (
            create_push_log, mark_log_sent, mark_log_failed
        )

        # Create log entry
        log = create_push_log(
            user=user,
            platform=platform,
            title=title,
            body=body,
            data=json.dumps(data) if data else None,
            image_url=image,
            click_action=click_action
        )

        if self.settings.test_mode:
            mark_log_sent(log.name, f"test_{frappe.generate_hash(length=8)}")
            return {
                "success": True,
                "message_id": f"test_{frappe.generate_hash(length=8)}",
                "log": log.name,
                "test_mode": True
            }

        # Route to provider
        if self.provider == "Firebase Cloud Messaging":
            result = self._send_fcm(token, title, body, data, image, click_action, platform)
        elif self.provider == "OneSignal":
            result = self._send_onesignal_token(token, title, body, data, image)
        else:
            result = {"success": False, "error": f"Unknown provider: {self.provider}"}

        # Update log
        if result.get("success"):
            mark_log_sent(log.name, result.get("message_id"))
        else:
            mark_log_failed(log.name, result.get("error", "Unknown error"))

        return {
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "log": log.name,
            "error": result.get("error")
        }

    def send_to_topic(self, topic, title, body, data=None, image=None, click_action=None):
        """
        Send push notification to a topic (subscribers)

        Args:
            topic: Topic name (e.g., 'announcements', 'emergency')
            title: Notification title
            body: Notification body
            data: Additional data payload
            image: Image URL
            click_action: Click action

        Returns:
            dict with success, message_id, log
        """
        from university_erp.university_integrations.doctype.push_notification_log.push_notification_log import (
            create_push_log, mark_log_sent, mark_log_failed
        )

        log = create_push_log(
            platform="topic",
            title=title,
            body=body,
            data=json.dumps(data) if data else None,
            topic=topic
        )

        if self.settings.test_mode:
            mark_log_sent(log.name, f"test_topic_{frappe.generate_hash(length=8)}")
            return {"success": True, "test_mode": True, "log": log.name}

        if self.provider == "Firebase Cloud Messaging":
            result = self._send_fcm_topic(topic, title, body, data, image, click_action)
        elif self.provider == "OneSignal":
            result = self._send_onesignal_segment(topic, title, body, data, image)
        else:
            result = {"success": False, "error": f"Unknown provider: {self.provider}"}

        if result.get("success"):
            mark_log_sent(log.name, result.get("message_id"))
        else:
            mark_log_failed(log.name, result.get("error", "Unknown error"))

        return {
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "log": log.name
        }

    def send_to_role(self, role, title, body, data=None, image=None):
        """Send push notification to all users with a role"""
        users = frappe.get_all(
            "Has Role",
            filters={"role": role, "parenttype": "User"},
            pluck="parent"
        )

        results = []
        for user in users:
            if user not in ["Administrator", "Guest"]:
                result = self.send_to_user(user, title, body, data, image)
                results.append({"user": user, **result})

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count > 0,
            "total_users": len(results),
            "successful": success_count,
            "results": results
        }

    # ========== Firebase Cloud Messaging ==========

    def _send_fcm(self, token, title, body, data, image, click_action, platform):
        """Send notification via Firebase Cloud Messaging"""
        url = "https://fcm.googleapis.com/fcm/send"

        headers = {
            "Authorization": f"key={self.settings.get_password('firebase_server_key')}",
            "Content-Type": "application/json"
        }

        notification = {
            "title": title,
            "body": body
        }

        if image:
            notification["image"] = image

        if self.settings.notification_sound:
            notification["sound"] = self.settings.notification_sound

        if self.settings.default_icon_url:
            notification["icon"] = self.settings.default_icon_url

        payload = {
            "to": token,
            "notification": notification,
            "data": data or {},
            "priority": "high",
            "time_to_live": self.settings.ttl_seconds or 86400
        }

        if click_action:
            notification["click_action"] = click_action

        # Platform-specific options
        if platform == "ios":
            payload["apns"] = {
                "payload": {
                    "aps": {
                        "sound": "default",
                        "badge": 1
                    }
                }
            }
        elif platform == "android":
            payload["android"] = {
                "priority": "high",
                "notification": {
                    "sound": "default",
                    "notification_priority": "PRIORITY_HIGH"
                }
            }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if result.get("success", 0) > 0:
                message_id = result.get("results", [{}])[0].get("message_id")
                return {"success": True, "message_id": message_id}
            else:
                error = result.get("results", [{}])[0].get("error", "Unknown FCM error")
                return {"success": False, "error": error}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_fcm_topic(self, topic, title, body, data, image, click_action):
        """Send FCM notification to a topic"""
        url = "https://fcm.googleapis.com/fcm/send"

        headers = {
            "Authorization": f"key={self.settings.get_password('firebase_server_key')}",
            "Content-Type": "application/json"
        }

        notification = {"title": title, "body": body}
        if image:
            notification["image"] = image
        if click_action:
            notification["click_action"] = click_action

        payload = {
            "to": f"/topics/{topic}",
            "notification": notification,
            "data": data or {},
            "priority": "high"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if "message_id" in result:
                return {"success": True, "message_id": result.get("message_id")}
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== OneSignal ==========

    def _send_onesignal_token(self, token, title, body, data, image):
        """Send notification via OneSignal to specific player ID"""
        url = "https://onesignal.com/api/v1/notifications"

        headers = {
            "Authorization": f"Basic {self.settings.get_password('onesignal_api_key')}",
            "Content-Type": "application/json"
        }

        payload = {
            "app_id": self.settings.onesignal_app_id,
            "include_player_ids": [token],
            "headings": {"en": title},
            "contents": {"en": body},
            "data": data or {}
        }

        if image:
            payload["big_picture"] = image

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if result.get("id"):
                return {"success": True, "message_id": result.get("id")}
            else:
                errors = result.get("errors", ["Unknown error"])
                return {"success": False, "error": str(errors)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_onesignal_segment(self, segment, title, body, data, image):
        """Send OneSignal notification to a segment"""
        url = "https://onesignal.com/api/v1/notifications"

        headers = {
            "Authorization": f"Basic {self.settings.get_password('onesignal_api_key')}",
            "Content-Type": "application/json"
        }

        payload = {
            "app_id": self.settings.onesignal_app_id,
            "included_segments": [segment],
            "headings": {"en": title},
            "contents": {"en": body},
            "data": data or {}
        }

        if image:
            payload["big_picture"] = image

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()

            if result.get("id"):
                return {"success": True, "message_id": result.get("id")}
            else:
                errors = result.get("errors", ["Unknown error"])
                return {"success": False, "error": str(errors)}

        except Exception as e:
            return {"success": False, "error": str(e)}


# ========== Factory ==========

def get_push_manager():
    """Get configured push notification manager"""
    return PushNotificationManager()


# ========== API Endpoints ==========

@frappe.whitelist()
def register_device_token(token, platform, device_id=None, device_name=None, app_version=None):
    """Register device token for push notifications"""
    user = frappe.session.user

    if user == "Guest":
        frappe.throw(_("Login required to register device"))

    # Check if token exists for this user
    existing = frappe.db.get_value(
        "User Device Token",
        {"user": user, "token": token},
        "name"
    )

    if existing:
        # Update existing
        frappe.db.set_value("User Device Token", existing, {
            "active": 1,
            "platform": platform,
            "device_id": device_id,
            "device_name": device_name,
            "app_version": app_version,
            "last_used": frappe.utils.now_datetime()
        })
        return {"success": True, "action": "updated", "token_id": existing}
    else:
        # Create new
        try:
            doc = frappe.get_doc({
                "doctype": "User Device Token",
                "user": user,
                "token": token,
                "platform": platform,
                "device_id": device_id,
                "device_name": device_name,
                "app_version": app_version,
                "active": 1
            })
            doc.insert(ignore_permissions=True)
            return {"success": True, "action": "created", "token_id": doc.name}
        except frappe.DuplicateEntryError:
            return {"success": True, "action": "updated"}


@frappe.whitelist()
def unregister_device_token(token):
    """Unregister device token"""
    user = frappe.session.user

    token_name = frappe.db.get_value(
        "User Device Token",
        {"user": user, "token": token},
        "name"
    )

    if token_name:
        frappe.db.set_value("User Device Token", token_name, "active", 0)
        return {"success": True}

    return {"success": False, "error": "Token not found"}


@frappe.whitelist()
def send_push_notification(user, title, body, data=None):
    """Send push notification to a user - API endpoint"""
    if isinstance(data, str):
        data = json.loads(data)

    manager = get_push_manager()
    return manager.send_to_user(user, title, body, data)


@frappe.whitelist()
def send_push_to_topic(topic, title, body, data=None):
    """Send push notification to a topic - API endpoint"""
    if isinstance(data, str):
        data = json.loads(data)

    manager = get_push_manager()
    return manager.send_to_topic(topic, title, body, data)


@frappe.whitelist()
def subscribe_to_topic(token, topic):
    """Subscribe device token to a topic (FCM only)"""
    settings = frappe.get_single("Push Notification Settings")

    if settings.provider != "Firebase Cloud Messaging":
        return {"success": False, "error": "Topic subscription only supported for FCM"}

    url = f"https://iid.googleapis.com/iid/v1/{token}/rel/topics/{topic}"
    headers = {
        "Authorization": f"key={settings.get_password('firebase_server_key')}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return {"success": True}
        else:
            return {"success": False, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def unsubscribe_from_topic(token, topic):
    """Unsubscribe device token from a topic (FCM only)"""
    settings = frappe.get_single("Push Notification Settings")

    if settings.provider != "Firebase Cloud Messaging":
        return {"success": False, "error": "Topic subscription only supported for FCM"}

    url = f"https://iid.googleapis.com/iid/v1:batchRemove"
    headers = {
        "Authorization": f"key={settings.get_password('firebase_server_key')}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": f"/topics/{topic}",
        "registration_tokens": [token]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            return {"success": True}
        else:
            return {"success": False, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}
