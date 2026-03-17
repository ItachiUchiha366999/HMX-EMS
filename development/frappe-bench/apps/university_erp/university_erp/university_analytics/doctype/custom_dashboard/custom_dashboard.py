# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint


class CustomDashboard(Document):
    def validate(self):
        """Validate dashboard configuration"""
        self.validate_columns()
        self.validate_widget_positions()

    def validate_columns(self):
        """Ensure columns is a valid positive number"""
        if self.columns and cint(self.columns) < 1:
            frappe.throw("Columns must be at least 1")
        if self.columns and cint(self.columns) > 12:
            frappe.throw("Columns cannot exceed 12")

    def validate_widget_positions(self):
        """Validate widget positions are within grid bounds"""
        if not self.widgets:
            return

        for widget in self.widgets:
            if widget.position_col and cint(widget.position_col) > cint(self.columns):
                frappe.throw(
                    f"Widget '{widget.widget_title}' column position exceeds dashboard columns"
                )

    def before_save(self):
        """Pre-save operations"""
        if not self.owner_role and not self.is_public:
            self.owner_role = "System Manager"

    def get_dashboard_data(self, filters=None):
        """
        Get data for all widgets in the dashboard

        Args:
            filters: Optional dict with date_range, department, program filters

        Returns:
            dict: Widget data keyed by widget name
        """
        from university_erp.university_erp.analytics.dashboard_engine import DashboardEngine

        engine = DashboardEngine()
        return engine.get_dashboard_data(self.name, filters)

    def increment_view_count(self):
        """Increment the view count for this dashboard"""
        frappe.db.set_value(
            "Custom Dashboard",
            self.name,
            "view_count",
            cint(self.view_count) + 1,
            update_modified=False
        )

    def has_access(self, user=None):
        """
        Check if a user has access to this dashboard

        Args:
            user: User to check access for. Defaults to current user.

        Returns:
            bool: True if user has access
        """
        if not user:
            user = frappe.session.user

        if user == "Administrator":
            return True

        if self.is_public:
            return True

        # Check user-specific access
        if self.allowed_users:
            for allowed_user in self.allowed_users:
                if allowed_user.user == user:
                    return True

        # Check role-based access
        if self.allowed_roles:
            user_roles = frappe.get_roles(user)
            for allowed_role in self.allowed_roles:
                if allowed_role.role in user_roles:
                    return True

        # Check owner role
        if self.owner_role:
            user_roles = frappe.get_roles(user)
            if self.owner_role in user_roles:
                return True

        return False
