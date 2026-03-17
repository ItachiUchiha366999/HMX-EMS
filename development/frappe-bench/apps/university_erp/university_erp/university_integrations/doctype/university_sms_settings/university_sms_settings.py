# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re


class UniversitySMSSettings(Document):
    def validate(self):
        self.validate_gateway_credentials()
        self.validate_dlt_settings()

    def validate_dlt_settings(self):
        """Validate DLT compliance settings"""
        if not self.dlt_enabled:
            return

        # Validate DLT Entity ID format (typically 19 digits for India)
        if self.dlt_entity_id:
            if not re.match(r'^\d{10,25}$', self.dlt_entity_id):
                frappe.msgprint(
                    _("DLT Entity ID should be a numeric value (10-25 digits)"),
                    indicator="orange",
                    alert=True
                )

        # Validate DLT Template ID format
        if self.dlt_template_id:
            if not re.match(r'^\d{10,25}$', self.dlt_template_id):
                frappe.msgprint(
                    _("DLT Template ID should be a numeric value (10-25 digits)"),
                    indicator="orange",
                    alert=True
                )

        # Validate DLT Header format (6 characters alphanumeric)
        if self.dlt_header:
            if not re.match(r'^[A-Za-z0-9]{6}$', self.dlt_header):
                frappe.msgprint(
                    _("DLT Header should be exactly 6 alphanumeric characters"),
                    indicator="orange",
                    alert=True
                )

        # Validate templates have DLT Template IDs when DLT is enabled
        for template in self.sms_templates:
            if template.is_active and not template.template_id:
                frappe.msgprint(
                    _("Template '{0}' requires a DLT Template ID when DLT compliance is enabled").format(
                        template.template_name
                    ),
                    indicator="orange",
                    alert=True
                )

    def validate_gateway_credentials(self):
        """Validate that required credentials are set for selected gateway"""
        if not self.sms_gateway or not self.enabled:
            return

        if self.sms_gateway == "MSG91":
            if not self.msg91_auth_key:
                frappe.msgprint(
                    "MSG91 Auth Key is required",
                    indicator="orange",
                    alert=True
                )
        elif self.sms_gateway == "Twilio":
            if not self.twilio_account_sid or not self.twilio_auth_token:
                frappe.msgprint(
                    "Twilio Account SID and Auth Token are required",
                    indicator="orange",
                    alert=True
                )
        elif self.sms_gateway == "Fast2SMS":
            if not self.fast2sms_api_key:
                frappe.msgprint(
                    "Fast2SMS API Key is required",
                    indicator="orange",
                    alert=True
                )

    def get_template(self, event_trigger):
        """Get template by event trigger"""
        for template in self.sms_templates:
            if template.event_trigger == event_trigger and template.is_active:
                return template
        return None

    def reset_daily_count(self):
        """Reset daily SMS count - called by scheduler"""
        self.sms_sent_today = 0
        self.save(ignore_permissions=True)


def reset_sms_daily_count():
    """Scheduler function to reset daily SMS count"""
    settings = frappe.get_single("University SMS Settings")
    settings.reset_daily_count()
