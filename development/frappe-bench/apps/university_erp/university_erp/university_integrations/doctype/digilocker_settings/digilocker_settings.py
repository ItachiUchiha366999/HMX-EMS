# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url


class DigiLockerSettings(Document):
    def validate(self):
        self.set_urls()

    def set_urls(self):
        """Set callback and verify URLs"""
        base_url = get_url()
        self.callback_url = f"{base_url}/api/method/university_erp.university_integrations.digilocker_integration.digilocker_callback"
        self.verify_url = f"{base_url}/api/method/university_erp.university_integrations.digilocker_integration.verify_digilocker_document"

    def get_document_type_config(self, doc_type):
        """Get document type configuration"""
        for dt in self.document_types:
            if dt.document_type == doc_type and dt.is_enabled:
                return dt
        return None
