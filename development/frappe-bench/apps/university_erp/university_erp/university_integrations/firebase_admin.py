# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Firebase Cloud Messaging (FCM) Integration for Push Notifications
Supports FCM HTTP v1 API for sending push notifications to mobile apps
"""

import frappe
from frappe import _
import json


class FirebaseAdmin:
    """Firebase Admin SDK wrapper for push notifications"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern for Firebase Admin instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.settings = None
            self.app = None
            self._initialized = True

    def initialize(self):
        """Initialize Firebase Admin SDK with credentials"""
        if self.app:
            return True

        try:
            self.settings = frappe.get_single("Firebase Settings")

            if not self.settings.enabled:
                return False

            # Check for firebase-admin library
            try:
                import firebase_admin
                from firebase_admin import credentials
            except ImportError:
                frappe.log_error(
                    "firebase-admin library not installed. "
                    "Install with: pip install firebase-admin",
                    "Firebase Integration"
                )
                return False

            # Initialize with service account
            if self.settings.service_account_json:
                cred_dict = json.loads(self.settings.get_password("service_account_json"))
                cred = credentials.Certificate(cred_dict)
            else:
                frappe.log_error(
                    "Firebase service account JSON not configured",
                    "Firebase Integration"
                )
                return False

            # Initialize app
            try:
                self.app = firebase_admin.get_app()
            except ValueError:
                self.app = firebase_admin.initialize_app(cred)

            return True

        except Exception as e:
            frappe.log_error(f"Firebase initialization failed: {str(e)}", "Firebase Integration")
            return False

    def send_push_notification(self, token, title, body, data=None, image=None):
        """
        Send push notification to a single device

        Args:
            token: FCM device token
            title: Notification title
            body: Notification body
            data: Optional data payload (dict)
            image: Optional image URL

        Returns:
            dict: Result with success status and message_id
        """
        if not self.initialize():
            return {"success": False, "error": "Firebase not initialized"}

        try:
            from firebase_admin import messaging

            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image
            )

            # Build message
            message = messaging.Message(
                notification=notification,
                data=data or {},
                token=token
            )

            # Send
            response = messaging.send(message)

            # Log success
            self._log_push(token, title, body, "Sent", response)

            return {
                "success": True,
                "message_id": response
            }

        except Exception as e:
            error_msg = str(e)
            self._log_push(token, title, body, "Failed", error_message=error_msg)
            return {"success": False, "error": error_msg}

    def send_multicast(self, tokens, title, body, data=None, image=None):
        """
        Send push notification to multiple devices

        Args:
            tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Optional data payload (dict)
            image: Optional image URL

        Returns:
            dict: Result with success count and failure count
        """
        if not self.initialize():
            return {"success": False, "error": "Firebase not initialized"}

        if not tokens:
            return {"success": False, "error": "No tokens provided"}

        try:
            from firebase_admin import messaging

            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image
            )

            # Build multicast message
            message = messaging.MulticastMessage(
                notification=notification,
                data=data or {},
                tokens=tokens
            )

            # Send
            response = messaging.send_each_for_multicast(message)

            # Process results
            success_count = response.success_count
            failure_count = response.failure_count

            # Handle failed tokens
            failed_tokens = []
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    failed_tokens.append({
                        "token": tokens[idx],
                        "error": str(resp.exception)
                    })

            return {
                "success": True,
                "success_count": success_count,
                "failure_count": failure_count,
                "failed_tokens": failed_tokens
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_to_topic(self, topic, title, body, data=None, image=None):
        """
        Send push notification to a topic

        Args:
            topic: Topic name (e.g., 'all_students', 'fee_reminders')
            title: Notification title
            body: Notification body
            data: Optional data payload (dict)
            image: Optional image URL

        Returns:
            dict: Result with success status
        """
        if not self.initialize():
            return {"success": False, "error": "Firebase not initialized"}

        try:
            from firebase_admin import messaging

            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image
            )

            # Build message
            message = messaging.Message(
                notification=notification,
                data=data or {},
                topic=topic
            )

            # Send
            response = messaging.send(message)

            return {
                "success": True,
                "message_id": response
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def subscribe_to_topic(self, tokens, topic):
        """
        Subscribe devices to a topic

        Args:
            tokens: List of FCM device tokens
            topic: Topic name

        Returns:
            dict: Result with success count
        """
        if not self.initialize():
            return {"success": False, "error": "Firebase not initialized"}

        try:
            from firebase_admin import messaging

            response = messaging.subscribe_to_topic(tokens, topic)

            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def unsubscribe_from_topic(self, tokens, topic):
        """
        Unsubscribe devices from a topic

        Args:
            tokens: List of FCM device tokens
            topic: Topic name

        Returns:
            dict: Result with success count
        """
        if not self.initialize():
            return {"success": False, "error": "Firebase not initialized"}

        try:
            from firebase_admin import messaging

            response = messaging.unsubscribe_from_topic(tokens, topic)

            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _log_push(self, token, title, body, status, message_id=None, error_message=None):
        """Log push notification attempt"""
        try:
            if frappe.db.table_exists("tabPush Notification Log"):
                frappe.get_doc({
                    "doctype": "Push Notification Log",
                    "device_token": token[:50] + "..." if len(token) > 50 else token,
                    "title": title,
                    "body": body[:200] if body else "",
                    "status": status,
                    "message_id": message_id,
                    "error_message": error_message
                }).insert(ignore_permissions=True)
        except Exception:
            pass  # Don't fail if logging fails


# ========== Factory Function ==========

def get_firebase_admin():
    """Get Firebase Admin singleton instance"""
    return FirebaseAdmin()


# ========== API Endpoints ==========

@frappe.whitelist()
def send_push_notification(user, title, body, data=None):
    """
    Send push notification to a user

    Args:
        user: User email/ID
        title: Notification title
        body: Notification body
        data: Optional JSON data payload

    Returns:
        dict: Result of push notification attempt
    """
    # Get user's FCM token
    token = get_user_fcm_token(user)

    if not token:
        return {"success": False, "error": "User has no registered device"}

    if isinstance(data, str):
        data = json.loads(data)

    firebase = get_firebase_admin()
    return firebase.send_push_notification(token, title, body, data)


@frappe.whitelist()
def send_push_to_role(role, title, body, data=None):
    """
    Send push notification to all users with a specific role

    Args:
        role: Role name
        title: Notification title
        body: Notification body
        data: Optional JSON data payload

    Returns:
        dict: Result with success and failure counts
    """
    # Get all users with the role
    users = frappe.get_all(
        "Has Role",
        filters={"role": role, "parenttype": "User"},
        pluck="parent"
    )

    if not users:
        return {"success": False, "error": f"No users found with role: {role}"}

    # Get tokens for all users
    tokens = []
    for user in users:
        token = get_user_fcm_token(user)
        if token:
            tokens.append(token)

    if not tokens:
        return {"success": False, "error": "No devices registered for users with this role"}

    if isinstance(data, str):
        data = json.loads(data)

    firebase = get_firebase_admin()
    return firebase.send_multicast(tokens, title, body, data)


@frappe.whitelist()
def register_device_token(token, device_type=None, device_name=None):
    """
    Register a device token for the current user

    Args:
        token: FCM device token
        device_type: Optional device type (android, ios, web)
        device_name: Optional device name

    Returns:
        dict: Registration result
    """
    user = frappe.session.user

    if not token:
        return {"success": False, "error": "Token is required"}

    try:
        # Check if token already exists
        existing = frappe.db.exists("User Device Token", {"token": token})

        if existing:
            # Update existing token
            frappe.db.set_value("User Device Token", existing, {
                "user": user,
                "device_type": device_type,
                "device_name": device_name,
                "last_active": frappe.utils.now()
            })
        else:
            # Create new token record
            if frappe.db.table_exists("tabUser Device Token"):
                frappe.get_doc({
                    "doctype": "User Device Token",
                    "user": user,
                    "token": token,
                    "device_type": device_type,
                    "device_name": device_name,
                    "is_active": 1
                }).insert(ignore_permissions=True)
            else:
                # Fallback to User Settings
                frappe.db.set_value("User", user, "push_token", token)

        frappe.db.commit()
        return {"success": True, "message": "Device registered successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def unregister_device_token(token):
    """
    Unregister a device token

    Args:
        token: FCM device token

    Returns:
        dict: Unregistration result
    """
    user = frappe.session.user

    try:
        if frappe.db.table_exists("tabUser Device Token"):
            frappe.db.delete("User Device Token", {"token": token, "user": user})
        else:
            current_token = frappe.db.get_value("User", user, "push_token")
            if current_token == token:
                frappe.db.set_value("User", user, "push_token", None)

        frappe.db.commit()
        return {"success": True, "message": "Device unregistered successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_fcm_token(user):
    """Get FCM token for a user"""
    # Try User Device Token first
    if frappe.db.table_exists("tabUser Device Token"):
        token = frappe.db.get_value(
            "User Device Token",
            {"user": user, "is_active": 1},
            "token",
            order_by="last_active desc"
        )
        if token:
            return token

    # Fallback to User field
    return frappe.db.get_value("User", user, "push_token")


def get_all_user_tokens(user):
    """Get all FCM tokens for a user (multiple devices)"""
    tokens = []

    if frappe.db.table_exists("tabUser Device Token"):
        tokens = frappe.get_all(
            "User Device Token",
            filters={"user": user, "is_active": 1},
            pluck="token"
        )

    if not tokens:
        token = frappe.db.get_value("User", user, "push_token")
        if token:
            tokens = [token]

    return tokens


# ========== Topic Management ==========

@frappe.whitelist()
def subscribe_user_to_topic(topic):
    """Subscribe current user's devices to a topic"""
    user = frappe.session.user
    tokens = get_all_user_tokens(user)

    if not tokens:
        return {"success": False, "error": "No devices registered"}

    firebase = get_firebase_admin()
    return firebase.subscribe_to_topic(tokens, topic)


@frappe.whitelist()
def unsubscribe_user_from_topic(topic):
    """Unsubscribe current user's devices from a topic"""
    user = frappe.session.user
    tokens = get_all_user_tokens(user)

    if not tokens:
        return {"success": False, "error": "No devices registered"}

    firebase = get_firebase_admin()
    return firebase.unsubscribe_from_topic(tokens, topic)


# ========== Batch Operations ==========

def send_push_to_students(program=None, batch=None, title=None, body=None, data=None):
    """
    Send push notification to students

    Args:
        program: Optional program filter
        batch: Optional batch filter
        title: Notification title
        body: Notification body
        data: Optional data payload

    Returns:
        dict: Result with counts
    """
    filters = {"enabled": 1}

    # Get students
    students = frappe.get_all(
        "Student",
        filters=filters,
        fields=["user"]
    )

    # Get tokens
    tokens = []
    for student in students:
        if student.user:
            user_tokens = get_all_user_tokens(student.user)
            tokens.extend(user_tokens)

    if not tokens:
        return {"success": False, "error": "No registered devices found"}

    # Send in batches of 500 (FCM limit)
    firebase = get_firebase_admin()
    total_success = 0
    total_failure = 0

    for i in range(0, len(tokens), 500):
        batch_tokens = tokens[i:i+500]
        result = firebase.send_multicast(batch_tokens, title, body, data)

        if result.get("success"):
            total_success += result.get("success_count", 0)
            total_failure += result.get("failure_count", 0)

    return {
        "success": True,
        "total_devices": len(tokens),
        "success_count": total_success,
        "failure_count": total_failure
    }


def send_emergency_push(title, body, data=None):
    """
    Send emergency push notification to all users

    Args:
        title: Emergency notification title
        body: Emergency notification body
        data: Optional data payload

    Returns:
        dict: Result
    """
    firebase = get_firebase_admin()

    # Use topic for emergency broadcasts
    result = firebase.send_to_topic("emergency_alerts", title, body, data)

    return result
