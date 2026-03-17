# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

"""
University ERP API v1
RESTful API endpoints for external integrations
"""

import frappe
from frappe import _
import functools
import hashlib
import hmac


API_VERSION = "1.0.0"


class APIError(Exception):
    """Base API Error"""
    def __init__(self, message, status_code=400, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "API_ERROR"
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Authentication failed"""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, 401, "AUTH_ERROR")


class AuthorizationError(APIError):
    """Authorization failed"""
    def __init__(self, message="You don't have permission to access this resource"):
        super().__init__(message, 403, "FORBIDDEN")


class NotFoundError(APIError):
    """Resource not found"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404, "NOT_FOUND")


class ValidationError(APIError):
    """Validation failed"""
    def __init__(self, message="Validation failed"):
        super().__init__(message, 422, "VALIDATION_ERROR")


def validate_api_key(api_key):
    """Validate API key and return associated user"""
    if not api_key:
        raise AuthenticationError("API key is required")

    # Check if API key exists and is valid
    api_user = frappe.db.get_value(
        "API Key",
        {"api_key": api_key, "enabled": 1},
        ["user", "name"],
        as_dict=True
    )

    if not api_user:
        raise AuthenticationError("Invalid or disabled API key")

    return api_user.user


def api_handler(allowed_methods=None, require_auth=True, allowed_roles=None):
    """
    Decorator for API endpoints

    Args:
        allowed_methods: List of allowed HTTP methods
        require_auth: Whether authentication is required
        allowed_roles: List of roles that can access this endpoint
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Check HTTP method
                if allowed_methods:
                    if frappe.request.method not in allowed_methods:
                        raise APIError(
                            f"Method {frappe.request.method} not allowed",
                            405,
                            "METHOD_NOT_ALLOWED"
                        )

                # Authentication
                if require_auth:
                    api_key = frappe.get_request_header("X-API-Key")

                    if api_key:
                        user = validate_api_key(api_key)
                        frappe.set_user(user)
                    elif frappe.session.user == "Guest":
                        raise AuthenticationError()

                # Role-based authorization
                if allowed_roles:
                    user_roles = frappe.get_roles()
                    if not any(role in user_roles for role in allowed_roles):
                        raise AuthorizationError()

                # Call the actual function
                result = func(*args, **kwargs)

                return {
                    "success": True,
                    "data": result,
                    "api_version": API_VERSION
                }

            except APIError as e:
                frappe.local.response["http_status_code"] = e.status_code
                return {
                    "success": False,
                    "error": {
                        "code": e.error_code,
                        "message": e.message
                    },
                    "api_version": API_VERSION
                }

            except frappe.DoesNotExistError:
                frappe.local.response["http_status_code"] = 404
                return {
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Resource not found"
                    },
                    "api_version": API_VERSION
                }

            except frappe.PermissionError:
                frappe.local.response["http_status_code"] = 403
                return {
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Permission denied"
                    },
                    "api_version": API_VERSION
                }

            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "API Error")
                frappe.local.response["http_status_code"] = 500
                return {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": str(e) if frappe.conf.developer_mode else "Internal server error"
                    },
                    "api_version": API_VERSION
                }

        return wrapper
    return decorator


def paginate(query_func, page=1, page_size=20, max_page_size=100):
    """
    Paginate query results

    Args:
        query_func: Function that returns list of items
        page: Current page number (1-indexed)
        page_size: Items per page
        max_page_size: Maximum allowed page size
    """
    page = max(1, int(page))
    page_size = min(max(1, int(page_size)), max_page_size)

    offset = (page - 1) * page_size
    items = query_func(limit=page_size, offset=offset)

    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "offset": offset
        }
    }


def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature using HMAC-SHA256"""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
