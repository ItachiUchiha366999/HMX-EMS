# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime


class KPIValue(Document):
    def validate(self):
        """Validate KPI value entry"""
        self.validate_dates()
        self.validate_period_type()

    def validate_dates(self):
        """Validate period dates"""
        if getdate(self.period_start) > getdate(self.period_end):
            frappe.throw(_("Period Start cannot be after Period End"))

    def validate_period_type(self):
        """Validate period type matches date range"""
        from frappe.utils import date_diff

        days = date_diff(self.period_end, self.period_start)

        expected_ranges = {
            "Daily": (0, 1),
            "Weekly": (6, 8),
            "Monthly": (27, 32),
            "Quarterly": (89, 93),
            "Yearly": (364, 367)
        }

        if self.period_type in expected_ranges:
            min_days, max_days = expected_ranges[self.period_type]
            if not (min_days <= days <= max_days):
                frappe.msgprint(
                    _("Date range of {0} days may not match {1} period type").format(
                        days, self.period_type
                    ),
                    alert=True
                )

    def before_save(self):
        """Pre-save operations"""
        self.calculate_variance()
        self.determine_status()
        self.set_calculated_metadata()

    def calculate_variance(self):
        """Calculate variance from target"""
        target = self.target

        # Get target from KPI definition if not set
        if not target:
            kpi_doc = frappe.get_doc("KPI Definition", self.kpi)
            target = kpi_doc.target_value

        if target and flt(target) != 0:
            self.variance = ((flt(self.value) - flt(target)) / flt(target)) * 100
        else:
            self.variance = 0

    def determine_status(self):
        """Determine status based on KPI thresholds"""
        kpi_doc = frappe.get_doc("KPI Definition", self.kpi)
        self.status = kpi_doc.get_status(self.value)

    def set_calculated_metadata(self):
        """Set calculation metadata if not already set"""
        if not self.calculated_on:
            self.calculated_on = now_datetime()

        if not self.calculation_source:
            self.calculation_source = "Manual Entry"
