# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, now_datetime, getdate, add_days, add_months, get_first_day


class AnalyticsManager:
    """
    Manager class for KPI calculations and analytics operations
    """

    def calculate_kpi(self, kpi_name, filters=None):
        """
        Calculate the value of a KPI

        Args:
            kpi_name: Name of the KPI Definition
            filters: Optional dict with department, program, academic_year filters

        Returns:
            float: Calculated KPI value
        """
        kpi_doc = frappe.get_doc("KPI Definition", kpi_name)

        if kpi_doc.calculation_method == "SQL Query":
            return self._execute_sql_kpi(kpi_doc, filters)
        elif kpi_doc.calculation_method == "Python Method":
            return self._execute_method_kpi(kpi_doc, filters)
        elif kpi_doc.calculation_method == "Formula":
            return self._calculate_formula_kpi(kpi_doc, filters)
        else:
            # Manual Entry - return latest value
            return self._get_latest_kpi_value(kpi_name, filters)

    def _execute_sql_kpi(self, kpi_doc, filters=None):
        """
        Execute SQL query for KPI calculation

        Args:
            kpi_doc: KPI Definition document
            filters: Optional filters

        Returns:
            float: Query result
        """
        if not kpi_doc.sql_query:
            return None

        query = kpi_doc.sql_query

        # Replace filter placeholders
        if filters:
            if filters.get("department"):
                query = query.replace("%(department)s", f"'{filters['department']}'")
            if filters.get("program"):
                query = query.replace("%(program)s", f"'{filters['program']}'")
            if filters.get("academic_year"):
                query = query.replace("%(academic_year)s", f"'{filters['academic_year']}'")

        try:
            result = frappe.db.sql(query)
            if result and result[0]:
                return flt(result[0][0])
        except Exception as e:
            frappe.log_error(f"KPI SQL Error: {str(e)}", "Analytics Manager")

        return None

    def _execute_method_kpi(self, kpi_doc, filters=None):
        """
        Execute Python method for KPI calculation

        Args:
            kpi_doc: KPI Definition document
            filters: Optional filters

        Returns:
            float: Method result
        """
        if not kpi_doc.python_method:
            return None

        try:
            method = frappe.get_attr(kpi_doc.python_method)
            return flt(method(filters))
        except Exception as e:
            frappe.log_error(f"KPI Method Error: {str(e)}", "Analytics Manager")
            return None

    def _calculate_formula_kpi(self, kpi_doc, filters=None):
        """
        Calculate KPI using formula

        Args:
            kpi_doc: KPI Definition document
            filters: Optional filters

        Returns:
            float: Calculated value
        """
        if not kpi_doc.formula:
            return None

        try:
            # Get variables from other KPIs
            formula = kpi_doc.formula
            import re

            # Find all {variable} patterns
            variables = re.findall(r'\{(\w+)\}', formula)

            for var in variables:
                # Try to get value from another KPI
                kpi_value = self._get_latest_kpi_value(var, filters)
                if kpi_value is not None:
                    formula = formula.replace(f"{{{var}}}", str(kpi_value))

            # Safely evaluate the formula
            result = eval(formula)
            return flt(result)
        except Exception as e:
            frappe.log_error(f"KPI Formula Error: {str(e)}", "Analytics Manager")
            return None

    def _get_latest_kpi_value(self, kpi_name, filters=None):
        """
        Get the latest stored KPI value

        Args:
            kpi_name: Name of KPI Definition
            filters: Optional filters

        Returns:
            float: Latest value or None
        """
        filter_conditions = {"kpi": kpi_name}

        if filters:
            if filters.get("department"):
                filter_conditions["department"] = filters["department"]
            if filters.get("program"):
                filter_conditions["program"] = filters["program"]
            if filters.get("academic_year"):
                filter_conditions["academic_year"] = filters["academic_year"]

        latest_value = frappe.db.get_value(
            "KPI Value",
            filter_conditions,
            "value",
            order_by="period_start DESC"
        )

        return flt(latest_value) if latest_value else None

    def store_kpi_value(self, kpi_name, value, period_type, period_start, period_end,
                        filters=None, calculation_source="Auto Calculated"):
        """
        Store a calculated KPI value

        Args:
            kpi_name: Name of KPI Definition
            value: Calculated value
            period_type: Daily/Weekly/Monthly/Quarterly/Yearly
            period_start: Start date of period
            period_end: End date of period
            filters: Optional context filters
            calculation_source: Auto Calculated/Manual Entry/Imported

        Returns:
            str: Name of created KPI Value document
        """
        kpi_doc = frappe.get_doc("KPI Definition", kpi_name)

        kpi_value = frappe.new_doc("KPI Value")
        kpi_value.kpi = kpi_name
        kpi_value.value = flt(value)
        kpi_value.period_type = period_type
        kpi_value.period_start = period_start
        kpi_value.period_end = period_end
        kpi_value.target = kpi_doc.target_value
        kpi_value.calculated_on = now_datetime()
        kpi_value.calculation_source = calculation_source

        if filters:
            kpi_value.department = filters.get("department")
            kpi_value.program = filters.get("program")
            kpi_value.academic_year = filters.get("academic_year")

        kpi_value.insert(ignore_permissions=True)

        return kpi_value.name

    def get_trend_data(self, kpi_name, periods=6, period_type="Monthly", filters=None):
        """
        Get trend data for a KPI over multiple periods

        Args:
            kpi_name: Name of KPI Definition
            periods: Number of periods to fetch
            period_type: Daily/Weekly/Monthly/Quarterly/Yearly
            filters: Optional context filters

        Returns:
            list: List of dicts with period and value
        """
        filter_conditions = {
            "kpi": kpi_name,
            "period_type": period_type
        }

        if filters:
            if filters.get("department"):
                filter_conditions["department"] = filters["department"]
            if filters.get("program"):
                filter_conditions["program"] = filters["program"]
            if filters.get("academic_year"):
                filter_conditions["academic_year"] = filters["academic_year"]

        values = frappe.get_all(
            "KPI Value",
            filters=filter_conditions,
            fields=["period_start", "value", "target", "status"],
            order_by="period_start DESC",
            limit=periods
        )

        # Reverse to get chronological order
        return list(reversed(values))

    def get_comparison_data(self, kpi_name, current_period, previous_period, filters=None):
        """
        Get comparison data between two periods

        Args:
            kpi_name: Name of KPI Definition
            current_period: Dict with start and end dates
            previous_period: Dict with start and end dates
            filters: Optional context filters

        Returns:
            dict: Comparison data with current, previous, and change
        """
        current_value = self._get_period_value(kpi_name, current_period, filters)
        previous_value = self._get_period_value(kpi_name, previous_period, filters)

        change = 0
        change_percent = 0

        if previous_value and flt(previous_value) != 0:
            change = flt(current_value) - flt(previous_value)
            change_percent = (change / flt(previous_value)) * 100

        kpi_doc = frappe.get_doc("KPI Definition", kpi_name)

        return {
            "kpi_name": kpi_name,
            "current_value": current_value,
            "previous_value": previous_value,
            "change": change,
            "change_percent": change_percent,
            "is_positive": (change > 0) == kpi_doc.higher_is_better,
            "status": kpi_doc.get_status(current_value)
        }

    def _get_period_value(self, kpi_name, period, filters=None):
        """
        Get KPI value for a specific period

        Args:
            kpi_name: Name of KPI Definition
            period: Dict with start and end dates
            filters: Optional context filters

        Returns:
            float: Value for the period
        """
        filter_conditions = {
            "kpi": kpi_name,
            "period_start": [">=", period.get("start")],
            "period_end": ["<=", period.get("end")]
        }

        if filters:
            if filters.get("department"):
                filter_conditions["department"] = filters["department"]
            if filters.get("program"):
                filter_conditions["program"] = filters["program"]

        value = frappe.db.get_value(
            "KPI Value",
            filter_conditions,
            "value"
        )

        return flt(value) if value else None

    def calculate_all_kpis(self, period_type="Monthly", filters=None):
        """
        Calculate all active KPIs

        Args:
            period_type: Period type to calculate
            filters: Optional context filters

        Returns:
            list: List of calculated KPIs with values
        """
        from frappe.utils import get_first_day, get_last_day, today

        active_kpis = frappe.get_all(
            "KPI Definition",
            filters={
                "is_active": 1,
                "tracking_frequency": period_type
            },
            pluck="name"
        )

        results = []
        today_date = getdate(today())

        # Calculate period dates
        if period_type == "Daily":
            period_start = today_date
            period_end = today_date
        elif period_type == "Weekly":
            period_start = add_days(today_date, -today_date.weekday())
            period_end = add_days(period_start, 6)
        elif period_type == "Monthly":
            period_start = get_first_day(today_date)
            period_end = get_last_day(today_date)
        elif period_type == "Quarterly":
            quarter = (today_date.month - 1) // 3
            period_start = today_date.replace(month=quarter * 3 + 1, day=1)
            period_end = add_months(period_start, 3)
            period_end = add_days(period_end, -1)
        else:  # Yearly
            period_start = today_date.replace(month=1, day=1)
            period_end = today_date.replace(month=12, day=31)

        for kpi_name in active_kpis:
            try:
                value = self.calculate_kpi(kpi_name, filters)
                if value is not None:
                    self.store_kpi_value(
                        kpi_name=kpi_name,
                        value=value,
                        period_type=period_type,
                        period_start=period_start,
                        period_end=period_end,
                        filters=filters
                    )
                    results.append({
                        "kpi": kpi_name,
                        "value": value,
                        "status": "Success"
                    })
            except Exception as e:
                results.append({
                    "kpi": kpi_name,
                    "value": None,
                    "status": f"Error: {str(e)}"
                })

        return results
