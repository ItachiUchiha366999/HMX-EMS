# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import re
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Supplier(Document):
    """Supplier - Vendor master for purchase management"""

    def validate(self):
        """Validate supplier data"""
        self.validate_gstin()
        self.validate_pan()
        self.validate_email()

    def validate_gstin(self):
        """Validate GSTIN format"""
        if self.gstin:
            gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
            if not re.match(gstin_pattern, self.gstin):
                frappe.throw(_("Invalid GSTIN format"))

    def validate_pan(self):
        """Validate PAN format"""
        if self.pan:
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            if not re.match(pan_pattern, self.pan):
                frappe.throw(_("Invalid PAN format"))

    def validate_email(self):
        """Validate email format"""
        if self.email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email):
                frappe.throw(_("Invalid email format"))

    def get_outstanding_amount(self):
        """Get outstanding amount for supplier"""
        # This would integrate with purchase invoices when implemented
        return 0


@frappe.whitelist()
def get_supplier_details(supplier):
    """Get supplier details for forms"""
    doc = frappe.get_cached_doc("Supplier", supplier)

    return {
        "supplier_name": doc.supplier_name,
        "supplier_type": doc.supplier_type,
        "supplier_group": doc.supplier_group,
        "payment_terms": doc.payment_terms,
        "default_currency": doc.default_currency,
        "default_price_list": doc.default_price_list,
        "gstin": doc.gstin,
        "credit_limit": doc.credit_limit
    }
