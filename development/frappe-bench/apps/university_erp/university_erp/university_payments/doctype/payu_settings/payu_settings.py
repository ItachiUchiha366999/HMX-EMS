# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import hashlib


class PayUSettings(Document):
    def validate(self):
        if self.enabled:
            self.validate_credentials()

    def validate_credentials(self):
        """Validate PayU credentials"""
        if not self.merchant_key or not self.merchant_salt:
            frappe.throw(_("Merchant Key and Merchant Salt are required when PayU is enabled"))

    def get_payment_url(self):
        """Get PayU payment URL based on mode"""
        if self.test_mode:
            return self.test_url or "https://test.payu.in/_payment"
        return self.production_url or "https://secure.payu.in/_payment"

    def get_merchant_salt(self):
        """Get merchant salt for hash generation"""
        return self.get_password('merchant_salt')

    def get_merchant_salt_v2(self):
        """Get merchant salt v2 if available"""
        return self.get_password('merchant_salt_v2') if self.merchant_salt_v2 else None

    def generate_hash(self, params):
        """Generate PayU hash for payment request"""
        hash_string = "|".join([
            params.get("key", ""),
            params.get("txnid", ""),
            params.get("amount", ""),
            params.get("productinfo", ""),
            params.get("firstname", ""),
            params.get("email", ""),
            params.get("udf1", ""),
            params.get("udf2", ""),
            params.get("udf3", ""),
            params.get("udf4", ""),
            params.get("udf5", ""),
            "",  # udf6
            "",  # udf7
            "",  # udf8
            "",  # udf9
            "",  # udf10
            self.get_merchant_salt()
        ])

        return hashlib.sha512(hash_string.encode()).hexdigest().lower()

    def verify_response_hash(self, params):
        """Verify PayU response hash"""
        # Reverse hash calculation for verification
        hash_string = "|".join([
            self.get_merchant_salt(),
            params.get("status", ""),
            "",  # udf10
            "",  # udf9
            "",  # udf8
            "",  # udf7
            "",  # udf6
            params.get("udf5", ""),
            params.get("udf4", ""),
            params.get("udf3", ""),
            params.get("udf2", ""),
            params.get("udf1", ""),
            params.get("email", ""),
            params.get("firstname", ""),
            params.get("productinfo", ""),
            params.get("amount", ""),
            params.get("txnid", ""),
            params.get("key", "")
        ])

        calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest().lower()
        return calculated_hash == params.get("hash", "")


def get_payu_settings():
    """Get PayU settings singleton"""
    settings = frappe.get_single("PayU Settings")
    if not settings.enabled:
        frappe.throw(_("PayU payment gateway is not enabled"))
    return settings
