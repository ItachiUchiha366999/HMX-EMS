# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re


class WhatsAppTemplate(Document):
    def validate(self):
        self.validate_body_text()
        self.validate_footer_text()
        self.extract_variables()

    def validate_body_text(self):
        """Validate body text requirements"""
        if not self.body_text:
            frappe.throw(_("Body text is required"))

        if len(self.body_text) > 1024:
            frappe.throw(_("Body text cannot exceed 1024 characters"))

    def validate_footer_text(self):
        """Validate footer text length"""
        if self.footer_text and len(self.footer_text) > 60:
            frappe.throw(_("Footer text cannot exceed 60 characters"))

    def extract_variables(self):
        """Extract and document variables from template"""
        variables = []

        # Extract from header
        if self.header_type == "Text" and self.header_text:
            header_vars = re.findall(r'\{\{(\d+)\}\}', self.header_text)
            for var in header_vars:
                variables.append(f"header_{{{{var}}}}")

        # Extract from body
        body_vars = re.findall(r'\{\{(\d+)\}\}', self.body_text or "")
        for var in body_vars:
            variables.append(f"body_{{{{{var}}}}}")

        # Extract button variables
        for button in self.buttons or []:
            if button.button_url:
                url_vars = re.findall(r'\{\{(\d+)\}\}', button.button_url)
                for var in url_vars:
                    variables.append(f"button_url_{{{{{var}}}}}")

        self.available_variables = ", ".join(variables) if variables else "No variables"

    def get_template_for_sending(self, params=None):
        """
        Get template structure for WhatsApp API

        Args:
            params: dict with 'header', 'body', 'button' lists of values

        Returns:
            dict suitable for WhatsApp API
        """
        params = params or {}
        components = []

        # Header component
        if self.header_type != "None":
            header_component = {"type": "header"}

            if self.header_type == "Text":
                header_params = params.get("header", [])
                if header_params:
                    header_component["parameters"] = [
                        {"type": "text", "text": str(p)} for p in header_params
                    ]
            elif self.header_type in ["Image", "Document", "Video"]:
                media_url = params.get("header_media") or self.header_media_url
                if media_url:
                    media_type = self.header_type.lower()
                    header_component["parameters"] = [{
                        "type": media_type,
                        media_type: {"link": media_url}
                    }]

            if header_component.get("parameters"):
                components.append(header_component)

        # Body component
        body_params = params.get("body", [])
        if body_params:
            components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in body_params]
            })

        # Button components
        button_params = params.get("buttons", [])
        for idx, button_param in enumerate(button_params):
            components.append({
                "type": "button",
                "sub_type": "url",
                "index": str(idx),
                "parameters": [{"type": "text", "text": str(button_param)}]
            })

        return {
            "name": self.meta_template_id or self.template_key,
            "language": {"code": self.language or "en"},
            "components": components
        }


def get_template(template_key):
    """Get WhatsApp template by key"""
    if frappe.db.exists("WhatsApp Template", template_key):
        return frappe.get_doc("WhatsApp Template", template_key)
    frappe.throw(_("WhatsApp template not found: {0}").format(template_key))
