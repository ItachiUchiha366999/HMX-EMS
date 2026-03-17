# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class BiometricDevice(Document):
    def validate(self):
        self.validate_ip_address()

    def validate_ip_address(self):
        """Basic IP address validation"""
        if self.ip_address:
            parts = self.ip_address.split(".")
            if len(parts) != 4:
                frappe.throw(_("Invalid IP address format"))
            for part in parts:
                if not part.isdigit() or not 0 <= int(part) <= 255:
                    frappe.throw(_("Invalid IP address"))

    @frappe.whitelist()
    def test_connection(self):
        """Test connection to the biometric device"""
        from university_erp.university_integrations.biometric_integration import get_biometric_device

        try:
            device_handler = get_biometric_device(self.name)
            if device_handler.connect():
                device_handler.disconnect()
                return {"success": True, "message": "Connection successful"}
            else:
                return {"success": False, "message": "Connection failed"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @frappe.whitelist()
    def sync_now(self):
        """Manually trigger sync"""
        from university_erp.university_integrations.biometric_integration import sync_attendance

        result = sync_attendance(self.name)
        return result


@frappe.whitelist()
def test_device_connection(device_name):
    """Test connection to biometric device"""
    device = frappe.get_doc("Biometric Device", device_name)
    return device.test_connection()


@frappe.whitelist()
def manual_sync(device_name):
    """Manually trigger sync for a device"""
    device = frappe.get_doc("Biometric Device", device_name)
    return device.sync_now()
