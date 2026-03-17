# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import json


class PushNotificationSettings(Document):
    def validate(self):
        if self.enabled:
            self.validate_provider_settings()

    def validate_provider_settings(self):
        """Validate required fields for selected provider"""
        if self.provider == "Firebase Cloud Messaging":
            if not self.firebase_project_id:
                frappe.throw(_("Firebase Project ID is required"))
            if not self.firebase_server_key and not self.firebase_service_account:
                frappe.throw(_("Either Server Key or Service Account JSON is required for Firebase"))

            # Validate service account JSON
            if self.firebase_service_account:
                try:
                    json.loads(self.firebase_service_account)
                except json.JSONDecodeError:
                    frappe.throw(_("Invalid Service Account JSON format"))

        elif self.provider == "OneSignal":
            if not self.onesignal_app_id:
                frappe.throw(_("OneSignal App ID is required"))
            if not self.onesignal_api_key:
                frappe.throw(_("OneSignal REST API Key is required"))

    def test_connection(self):
        """Test push notification provider connection"""
        if not self.enabled:
            return {"success": False, "error": "Push notifications are not enabled"}

        try:
            if self.provider == "Firebase Cloud Messaging":
                return self._test_firebase_connection()
            elif self.provider == "OneSignal":
                return self._test_onesignal_connection()
            else:
                return {"success": False, "error": "Provider not configured"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_firebase_connection(self):
        """Test Firebase FCM connection"""
        import requests

        url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": f"key={self.get_password('firebase_server_key')}",
            "Content-Type": "application/json"
        }

        # Send a dry run request
        payload = {
            "dry_run": True,
            "to": "test_token",
            "notification": {
                "title": "Test",
                "body": "Connection test"
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            return {"success": True, "message": "Firebase connection successful"}
        else:
            return {"success": False, "error": response.json().get("error", "Connection failed")}

    def _test_onesignal_connection(self):
        """Test OneSignal connection"""
        import requests

        url = f"https://onesignal.com/api/v1/apps/{self.onesignal_app_id}"
        headers = {
            "Authorization": f"Basic {self.get_password('onesignal_api_key')}"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            app_name = response.json().get("name", "Unknown")
            return {"success": True, "message": f"Connected to: {app_name}"}
        else:
            return {"success": False, "error": "Connection failed"}


def get_push_settings():
    """Get Push Notification settings singleton"""
    settings = frappe.get_single("Push Notification Settings")
    if not settings.enabled:
        frappe.throw(_("Push notifications are not enabled"))
    return settings


@frappe.whitelist()
def test_push_connection():
    """Test push notification connection - API endpoint"""
    settings = frappe.get_single("Push Notification Settings")
    return settings.test_connection()
