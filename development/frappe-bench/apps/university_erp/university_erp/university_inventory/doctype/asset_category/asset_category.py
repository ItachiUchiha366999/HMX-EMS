# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class AssetCategory(Document):
    """Asset Category - Defines depreciation settings and accounts for assets"""

    def validate(self):
        """Validate asset category settings"""
        self.validate_depreciation_settings()
        self.validate_accounts()

    def validate_depreciation_settings(self):
        """Validate depreciation configuration"""
        if self.depreciation_method:
            if self.depreciation_method in ["Straight Line", "Double Declining Balance"]:
                if not self.total_number_of_depreciations:
                    frappe.throw(_("Total Number of Depreciations is required for {0} method").format(
                        self.depreciation_method
                    ))

            if self.depreciation_method == "Written Down Value":
                if flt(self.rate_of_depreciation) <= 0:
                    frappe.throw(_("Rate of Depreciation is required for Written Down Value method"))

            if self.frequency_of_depreciation and self.frequency_of_depreciation <= 0:
                frappe.throw(_("Frequency of Depreciation must be greater than 0"))

    def validate_accounts(self):
        """Validate account configurations"""
        if self.is_cwip_enabled and not self.cwip_account:
            frappe.throw(_("Capital Work in Progress Account is required when CWIP is enabled"))

    def get_depreciation_rate(self):
        """Calculate depreciation rate based on method"""
        if self.depreciation_method == "Written Down Value":
            return flt(self.rate_of_depreciation)
        elif self.depreciation_method == "Double Declining Balance":
            if self.total_number_of_depreciations:
                useful_life_years = (self.total_number_of_depreciations * self.frequency_of_depreciation) / 12
                if useful_life_years > 0:
                    return (2 / useful_life_years) * 100
        elif self.depreciation_method == "Straight Line":
            if self.total_number_of_depreciations:
                return 100 / self.total_number_of_depreciations
        return 0
