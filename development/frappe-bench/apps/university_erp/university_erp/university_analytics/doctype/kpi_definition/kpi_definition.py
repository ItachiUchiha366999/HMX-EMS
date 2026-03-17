# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class KPIDefinition(Document):
    def validate(self):
        """Validate KPI definition"""
        self.validate_calculation_method()
        self.validate_thresholds()
        self.set_kpi_code()

    def validate_calculation_method(self):
        """Validate that calculation method has required fields"""
        if self.calculation_method == "SQL Query" and not self.sql_query:
            frappe.throw(_("SQL Query is required when Calculation Method is SQL Query"))

        if self.calculation_method == "Python Method" and not self.python_method:
            frappe.throw(_("Python Method is required when Calculation Method is Python Method"))

        if self.calculation_method == "Formula" and not self.formula:
            frappe.throw(_("Formula is required when Calculation Method is Formula"))

    def validate_thresholds(self):
        """Validate threshold values are in correct order"""
        if self.higher_is_better:
            # For higher_is_better: red < yellow < green
            if self.red_threshold and self.yellow_threshold:
                if flt(self.red_threshold) >= flt(self.yellow_threshold):
                    frappe.throw(
                        _("Red threshold must be less than Yellow threshold when Higher is Better")
                    )
            if self.yellow_threshold and self.green_threshold:
                if flt(self.yellow_threshold) >= flt(self.green_threshold):
                    frappe.throw(
                        _("Yellow threshold must be less than Green threshold when Higher is Better")
                    )
        else:
            # For lower_is_better: green < yellow < red
            if self.green_threshold and self.yellow_threshold:
                if flt(self.green_threshold) >= flt(self.yellow_threshold):
                    frappe.throw(
                        _("Green threshold must be less than Yellow threshold when Lower is Better")
                    )
            if self.yellow_threshold and self.red_threshold:
                if flt(self.yellow_threshold) >= flt(self.red_threshold):
                    frappe.throw(
                        _("Yellow threshold must be less than Red threshold when Lower is Better")
                    )

    def set_kpi_code(self):
        """Auto-generate KPI code if not set"""
        if not self.kpi_code:
            # Generate code from category and name
            category_prefix = (self.category[:3] if self.category else "GEN").upper()
            name_abbr = "".join(word[0] for word in self.kpi_name.split()[:3]).upper()
            self.kpi_code = f"{category_prefix}-{name_abbr}"

    def calculate_value(self, filters=None):
        """
        Calculate the current value of this KPI

        Args:
            filters: Optional filters like department, program, academic_year

        Returns:
            float: Calculated KPI value
        """
        from university_erp.university_erp.analytics.analytics_manager import AnalyticsManager

        manager = AnalyticsManager()
        return manager.calculate_kpi(self.name, filters)

    def get_status(self, value):
        """
        Determine status (Green/Yellow/Red) based on value

        Args:
            value: The KPI value to evaluate

        Returns:
            str: Status string ('Green', 'Yellow', or 'Red')
        """
        if value is None:
            return "Red"

        value = flt(value)

        if self.higher_is_better:
            if self.green_threshold and value >= flt(self.green_threshold):
                return "Green"
            elif self.yellow_threshold and value >= flt(self.yellow_threshold):
                return "Yellow"
            else:
                return "Red"
        else:
            if self.green_threshold and value <= flt(self.green_threshold):
                return "Green"
            elif self.yellow_threshold and value <= flt(self.yellow_threshold):
                return "Yellow"
            else:
                return "Red"

    def get_variance(self, value):
        """
        Calculate variance from target

        Args:
            value: The current KPI value

        Returns:
            float: Variance percentage from target
        """
        if not self.target_value or flt(self.target_value) == 0:
            return 0

        return ((flt(value) - flt(self.target_value)) / flt(self.target_value)) * 100
