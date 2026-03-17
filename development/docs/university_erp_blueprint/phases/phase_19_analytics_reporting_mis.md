# Phase 19: Analytics, Reporting & Management Information System (MIS)

## Overview

This phase implements a comprehensive analytics and reporting framework including dashboards, custom report builder, scheduled reports, data visualization, KPI tracking, and executive MIS for informed decision-making.

**Duration:** 5 Weeks
**Priority:** High
**Dependencies:** All previous phases (data sources)

## Gap Analysis Reference

From IMPLEMENTATION_GAP_ANALYSIS.md:
- MIS Dashboard: 30% (Basic widgets only)
- Custom Report Builder: 0% (Missing)
- Scheduled Reports: 0% (Missing)
- Data Visualization: 20% (Basic charts)
- KPI Tracking: 0% (Missing)
- Executive Dashboard: 0% (Missing)
- Trend Analysis: 0% (Missing)
- Comparative Reports: 0% (Missing)

---

## 1. Core DocTypes

### 1.1 Dashboard Definition

```json
{
  "doctype": "DocType",
  "name": "Custom Dashboard",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "DASH-.#####",
  "fields": [
    {
      "fieldname": "dashboard_name",
      "fieldtype": "Data",
      "label": "Dashboard Name",
      "reqd": 1,
      "unique": 1
    },
    {
      "fieldname": "dashboard_type",
      "fieldtype": "Select",
      "label": "Dashboard Type",
      "options": "\nExecutive\nAcademic\nFinancial\nAdmissions\nExamination\nFaculty\nStudent\nDepartmental\nCustom",
      "reqd": 1
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "is_public",
      "fieldtype": "Check",
      "label": "Is Public Dashboard"
    },
    {
      "fieldname": "owner_role",
      "fieldtype": "Link",
      "label": "Owner Role",
      "options": "Role"
    },
    {
      "fieldname": "refresh_interval",
      "fieldtype": "Select",
      "label": "Auto Refresh",
      "options": "\nManual\n1 minute\n5 minutes\n15 minutes\n30 minutes\n1 hour",
      "default": "Manual"
    },
    {
      "fieldname": "section_break_filters",
      "fieldtype": "Section Break",
      "label": "Global Filters"
    },
    {
      "fieldname": "enable_date_filter",
      "fieldtype": "Check",
      "label": "Enable Date Filter",
      "default": 1
    },
    {
      "fieldname": "default_date_range",
      "fieldtype": "Select",
      "label": "Default Date Range",
      "options": "\nToday\nThis Week\nThis Month\nThis Quarter\nThis Year\nLast 30 Days\nLast 90 Days\nCustom"
    },
    {
      "fieldname": "enable_department_filter",
      "fieldtype": "Check",
      "label": "Enable Department Filter"
    },
    {
      "fieldname": "enable_program_filter",
      "fieldtype": "Check",
      "label": "Enable Program Filter"
    },
    {
      "fieldname": "section_break_layout",
      "fieldtype": "Section Break",
      "label": "Layout"
    },
    {
      "fieldname": "layout_type",
      "fieldtype": "Select",
      "label": "Layout Type",
      "options": "\nGrid\nFreeform\nTabs",
      "default": "Grid"
    },
    {
      "fieldname": "columns",
      "fieldtype": "Int",
      "label": "Grid Columns",
      "default": 4
    },
    {
      "fieldname": "section_break_widgets",
      "fieldtype": "Section Break",
      "label": "Widgets"
    },
    {
      "fieldname": "widgets",
      "fieldtype": "Table",
      "label": "Widgets",
      "options": "Dashboard Widget"
    },
    {
      "fieldname": "section_break_access",
      "fieldtype": "Section Break",
      "label": "Access Control"
    },
    {
      "fieldname": "allowed_roles",
      "fieldtype": "Table MultiSelect",
      "label": "Allowed Roles",
      "options": "Dashboard Role"
    },
    {
      "fieldname": "allowed_users",
      "fieldtype": "Table MultiSelect",
      "label": "Allowed Users",
      "options": "Dashboard User"
    },
    {
      "fieldname": "section_break_status",
      "fieldtype": "Section Break"
    },
    {
      "fieldname": "is_active",
      "fieldtype": "Check",
      "label": "Is Active",
      "default": 1
    },
    {
      "fieldname": "view_count",
      "fieldtype": "Int",
      "label": "View Count",
      "read_only": 1,
      "default": 0
    }
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Academic Admin", "read": 1, "write": 1, "create": 1}
  ]
}
```

### 1.2 Dashboard Widget (Child Table)

```json
{
  "doctype": "DocType",
  "name": "Dashboard Widget",
  "module": "University ERP",
  "istable": 1,
  "fields": [
    {
      "fieldname": "widget_title",
      "fieldtype": "Data",
      "label": "Widget Title",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "widget_type",
      "fieldtype": "Select",
      "label": "Widget Type",
      "options": "\nNumber Card\nProgress Card\nChart\nTable\nList\nCalendar\nMap\nGauge\nTrend\nComparison",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "data_source",
      "fieldtype": "Select",
      "label": "Data Source",
      "options": "\nReport\nQuery\nMethod\nStatic",
      "reqd": 1
    },
    {
      "fieldname": "report_name",
      "fieldtype": "Link",
      "label": "Report",
      "options": "Report",
      "depends_on": "eval:doc.data_source == 'Report'"
    },
    {
      "fieldname": "custom_query",
      "fieldtype": "Code",
      "label": "SQL Query",
      "depends_on": "eval:doc.data_source == 'Query'",
      "options": "SQL"
    },
    {
      "fieldname": "method_path",
      "fieldtype": "Data",
      "label": "Method Path",
      "depends_on": "eval:doc.data_source == 'Method'"
    },
    {
      "fieldname": "chart_type",
      "fieldtype": "Select",
      "label": "Chart Type",
      "options": "\nBar\nLine\nPie\nDonut\nArea\nScatter\nHeatmap\nFunnel",
      "depends_on": "eval:doc.widget_type == 'Chart'"
    },
    {
      "fieldname": "color",
      "fieldtype": "Color",
      "label": "Primary Color"
    },
    {
      "fieldname": "icon",
      "fieldtype": "Data",
      "label": "Icon",
      "description": "FontAwesome icon class"
    },
    {
      "fieldname": "position_row",
      "fieldtype": "Int",
      "label": "Row",
      "default": 1
    },
    {
      "fieldname": "position_col",
      "fieldtype": "Int",
      "label": "Column",
      "default": 1
    },
    {
      "fieldname": "width",
      "fieldtype": "Int",
      "label": "Width (columns)",
      "default": 1
    },
    {
      "fieldname": "height",
      "fieldtype": "Int",
      "label": "Height (rows)",
      "default": 1
    },
    {
      "fieldname": "drill_down_link",
      "fieldtype": "Data",
      "label": "Drill Down Link",
      "description": "URL to navigate when widget is clicked"
    },
    {
      "fieldname": "comparison_period",
      "fieldtype": "Select",
      "label": "Comparison Period",
      "options": "\nNone\nPrevious Day\nPrevious Week\nPrevious Month\nPrevious Year\nSame Period Last Year"
    }
  ]
}
```

### 1.3 KPI Definition

```json
{
  "doctype": "DocType",
  "name": "KPI Definition",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "KPI-.#####",
  "fields": [
    {
      "fieldname": "kpi_name",
      "fieldtype": "Data",
      "label": "KPI Name",
      "reqd": 1,
      "unique": 1
    },
    {
      "fieldname": "kpi_code",
      "fieldtype": "Data",
      "label": "KPI Code",
      "unique": 1
    },
    {
      "fieldname": "category",
      "fieldtype": "Select",
      "label": "Category",
      "options": "\nAcademic\nAdmissions\nFinancial\nFaculty\nResearch\nInfrastructure\nPlacement\nStudent Services\nGovernance",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "unit",
      "fieldtype": "Data",
      "label": "Unit",
      "description": "e.g., %, count, ratio, INR"
    },
    {
      "fieldname": "section_break_calculation",
      "fieldtype": "Section Break",
      "label": "Calculation"
    },
    {
      "fieldname": "calculation_method",
      "fieldtype": "Select",
      "label": "Calculation Method",
      "options": "\nSQL Query\nPython Method\nFormula\nManual Entry",
      "reqd": 1
    },
    {
      "fieldname": "sql_query",
      "fieldtype": "Code",
      "label": "SQL Query",
      "depends_on": "eval:doc.calculation_method == 'SQL Query'",
      "options": "SQL"
    },
    {
      "fieldname": "python_method",
      "fieldtype": "Data",
      "label": "Python Method Path",
      "depends_on": "eval:doc.calculation_method == 'Python Method'"
    },
    {
      "fieldname": "formula",
      "fieldtype": "Code",
      "label": "Formula",
      "depends_on": "eval:doc.calculation_method == 'Formula'",
      "description": "Use other KPI codes in formula: {KPI_CODE}"
    },
    {
      "fieldname": "section_break_targets",
      "fieldtype": "Section Break",
      "label": "Targets & Thresholds"
    },
    {
      "fieldname": "target_value",
      "fieldtype": "Float",
      "label": "Target Value"
    },
    {
      "fieldname": "minimum_acceptable",
      "fieldtype": "Float",
      "label": "Minimum Acceptable"
    },
    {
      "fieldname": "stretch_target",
      "fieldtype": "Float",
      "label": "Stretch Target"
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "red_threshold",
      "fieldtype": "Float",
      "label": "Red Threshold (<)"
    },
    {
      "fieldname": "yellow_threshold",
      "fieldtype": "Float",
      "label": "Yellow Threshold (<)"
    },
    {
      "fieldname": "green_threshold",
      "fieldtype": "Float",
      "label": "Green Threshold (>=)"
    },
    {
      "fieldname": "higher_is_better",
      "fieldtype": "Check",
      "label": "Higher is Better",
      "default": 1
    },
    {
      "fieldname": "section_break_tracking",
      "fieldtype": "Section Break",
      "label": "Tracking"
    },
    {
      "fieldname": "tracking_frequency",
      "fieldtype": "Select",
      "label": "Tracking Frequency",
      "options": "\nDaily\nWeekly\nMonthly\nQuarterly\nYearly",
      "default": "Monthly"
    },
    {
      "fieldname": "responsible_role",
      "fieldtype": "Link",
      "label": "Responsible Role",
      "options": "Role"
    },
    {
      "fieldname": "data_owner",
      "fieldtype": "Link",
      "label": "Data Owner",
      "options": "User"
    },
    {
      "fieldname": "column_break_3",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "is_active",
      "fieldtype": "Check",
      "label": "Is Active",
      "default": 1
    },
    {
      "fieldname": "show_on_executive_dashboard",
      "fieldtype": "Check",
      "label": "Show on Executive Dashboard"
    },
    {
      "fieldname": "benchmark_source",
      "fieldtype": "Data",
      "label": "Benchmark Source",
      "description": "e.g., NAAC, NBA, Industry Average"
    },
    {
      "fieldname": "benchmark_value",
      "fieldtype": "Float",
      "label": "Benchmark Value"
    }
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Academic Admin", "read": 1}
  ]
}
```

### 1.4 KPI Value

```json
{
  "doctype": "DocType",
  "name": "KPI Value",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "KPIV-.YYYY.MM.-.#####",
  "fields": [
    {
      "fieldname": "kpi",
      "fieldtype": "Link",
      "label": "KPI",
      "options": "KPI Definition",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "period_type",
      "fieldtype": "Select",
      "label": "Period Type",
      "options": "\nDaily\nWeekly\nMonthly\nQuarterly\nYearly",
      "reqd": 1
    },
    {
      "fieldname": "period_start",
      "fieldtype": "Date",
      "label": "Period Start",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "period_end",
      "fieldtype": "Date",
      "label": "Period End",
      "reqd": 1
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "value",
      "fieldtype": "Float",
      "label": "Value",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "target",
      "fieldtype": "Float",
      "label": "Target"
    },
    {
      "fieldname": "variance",
      "fieldtype": "Float",
      "label": "Variance (%)",
      "read_only": 1
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "label": "Status",
      "options": "\nGreen\nYellow\nRed",
      "read_only": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "section_break_context",
      "fieldtype": "Section Break",
      "label": "Context (Optional)"
    },
    {
      "fieldname": "department",
      "fieldtype": "Link",
      "label": "Department",
      "options": "Department"
    },
    {
      "fieldname": "program",
      "fieldtype": "Link",
      "label": "Program",
      "options": "Program"
    },
    {
      "fieldname": "academic_year",
      "fieldtype": "Link",
      "label": "Academic Year",
      "options": "Academic Year"
    },
    {
      "fieldname": "section_break_meta",
      "fieldtype": "Section Break",
      "label": "Metadata"
    },
    {
      "fieldname": "calculated_on",
      "fieldtype": "Datetime",
      "label": "Calculated On",
      "read_only": 1
    },
    {
      "fieldname": "calculation_source",
      "fieldtype": "Select",
      "label": "Source",
      "options": "\nAuto Calculated\nManual Entry\nImported",
      "read_only": 1
    },
    {
      "fieldname": "notes",
      "fieldtype": "Text",
      "label": "Notes/Comments"
    }
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1},
    {"role": "Academic Admin", "read": 1, "write": 1, "create": 1}
  ]
}
```

### 1.5 Scheduled Report

```json
{
  "doctype": "DocType",
  "name": "Scheduled Report",
  "module": "University ERP",
  "fields": [
    {
      "fieldname": "report_name",
      "fieldtype": "Data",
      "label": "Report Name",
      "reqd": 1
    },
    {
      "fieldname": "report",
      "fieldtype": "Link",
      "label": "Report",
      "options": "Report",
      "reqd": 1
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "is_enabled",
      "fieldtype": "Check",
      "label": "Enabled",
      "default": 1
    },
    {
      "fieldname": "section_break_schedule",
      "fieldtype": "Section Break",
      "label": "Schedule"
    },
    {
      "fieldname": "frequency",
      "fieldtype": "Select",
      "label": "Frequency",
      "options": "\nDaily\nWeekly\nMonthly\nQuarterly",
      "reqd": 1
    },
    {
      "fieldname": "day_of_week",
      "fieldtype": "Select",
      "label": "Day of Week",
      "options": "\nMonday\nTuesday\nWednesday\nThursday\nFriday\nSaturday\nSunday",
      "depends_on": "eval:doc.frequency == 'Weekly'"
    },
    {
      "fieldname": "day_of_month",
      "fieldtype": "Int",
      "label": "Day of Month",
      "depends_on": "eval:in_list(['Monthly', 'Quarterly'], doc.frequency)"
    },
    {
      "fieldname": "time_of_day",
      "fieldtype": "Time",
      "label": "Time",
      "reqd": 1
    },
    {
      "fieldname": "column_break_2",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "timezone",
      "fieldtype": "Select",
      "label": "Timezone",
      "options": "\nAsia/Kolkata\nUTC",
      "default": "Asia/Kolkata"
    },
    {
      "fieldname": "section_break_filters",
      "fieldtype": "Section Break",
      "label": "Report Filters"
    },
    {
      "fieldname": "filters",
      "fieldtype": "Code",
      "label": "Filters (JSON)",
      "options": "JSON"
    },
    {
      "fieldname": "dynamic_filters",
      "fieldtype": "Check",
      "label": "Use Dynamic Date Filters",
      "description": "Auto-adjust date filters based on schedule frequency"
    },
    {
      "fieldname": "section_break_output",
      "fieldtype": "Section Break",
      "label": "Output"
    },
    {
      "fieldname": "output_format",
      "fieldtype": "Select",
      "label": "Output Format",
      "options": "\nPDF\nExcel\nCSV\nHTML",
      "default": "PDF"
    },
    {
      "fieldname": "include_charts",
      "fieldtype": "Check",
      "label": "Include Charts",
      "default": 1
    },
    {
      "fieldname": "section_break_delivery",
      "fieldtype": "Section Break",
      "label": "Delivery"
    },
    {
      "fieldname": "delivery_method",
      "fieldtype": "Select",
      "label": "Delivery Method",
      "options": "\nEmail\nFile Storage\nBoth",
      "default": "Email"
    },
    {
      "fieldname": "recipients",
      "fieldtype": "Table",
      "label": "Email Recipients",
      "options": "Scheduled Report Recipient"
    },
    {
      "fieldname": "storage_folder",
      "fieldtype": "Data",
      "label": "Storage Folder Path",
      "depends_on": "eval:in_list(['File Storage', 'Both'], doc.delivery_method)"
    },
    {
      "fieldname": "section_break_status",
      "fieldtype": "Section Break",
      "label": "Status"
    },
    {
      "fieldname": "last_run",
      "fieldtype": "Datetime",
      "label": "Last Run",
      "read_only": 1
    },
    {
      "fieldname": "last_run_status",
      "fieldtype": "Select",
      "label": "Last Run Status",
      "options": "\nSuccess\nFailed\nPartial",
      "read_only": 1
    },
    {
      "fieldname": "next_run",
      "fieldtype": "Datetime",
      "label": "Next Scheduled Run",
      "read_only": 1
    },
    {
      "fieldname": "run_count",
      "fieldtype": "Int",
      "label": "Total Runs",
      "read_only": 1,
      "default": 0
    }
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Academic Admin", "read": 1, "write": 1, "create": 1}
  ]
}
```

### 1.6 Custom Report Builder

```json
{
  "doctype": "DocType",
  "name": "Custom Report Definition",
  "module": "University ERP",
  "naming_rule": "Expression",
  "autoname": "CRD-.#####",
  "fields": [
    {
      "fieldname": "report_title",
      "fieldtype": "Data",
      "label": "Report Title",
      "reqd": 1
    },
    {
      "fieldname": "report_type",
      "fieldtype": "Select",
      "label": "Report Type",
      "options": "\nTabular\nSummary\nMatrix\nPivot\nChart Only",
      "reqd": 1
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "primary_doctype",
      "fieldtype": "Link",
      "label": "Primary DocType",
      "options": "DocType",
      "reqd": 1
    },
    {
      "fieldname": "is_public",
      "fieldtype": "Check",
      "label": "Is Public"
    },
    {
      "fieldname": "section_break_fields",
      "fieldtype": "Section Break",
      "label": "Fields"
    },
    {
      "fieldname": "columns",
      "fieldtype": "Table",
      "label": "Columns",
      "options": "Report Column Definition"
    },
    {
      "fieldname": "section_break_joins",
      "fieldtype": "Section Break",
      "label": "Related Tables"
    },
    {
      "fieldname": "joins",
      "fieldtype": "Table",
      "label": "Joins",
      "options": "Report Join Definition"
    },
    {
      "fieldname": "section_break_filters",
      "fieldtype": "Section Break",
      "label": "Filters"
    },
    {
      "fieldname": "filters",
      "fieldtype": "Table",
      "label": "Filters",
      "options": "Report Filter Definition"
    },
    {
      "fieldname": "section_break_grouping",
      "fieldtype": "Section Break",
      "label": "Grouping & Aggregation"
    },
    {
      "fieldname": "group_by_fields",
      "fieldtype": "Small Text",
      "label": "Group By Fields",
      "description": "Comma-separated field names"
    },
    {
      "fieldname": "having_clause",
      "fieldtype": "Data",
      "label": "Having Clause"
    },
    {
      "fieldname": "section_break_sorting",
      "fieldtype": "Section Break",
      "label": "Sorting"
    },
    {
      "fieldname": "sort_by",
      "fieldtype": "Data",
      "label": "Sort By"
    },
    {
      "fieldname": "sort_order",
      "fieldtype": "Select",
      "label": "Sort Order",
      "options": "\nASC\nDESC",
      "default": "ASC"
    },
    {
      "fieldname": "row_limit",
      "fieldtype": "Int",
      "label": "Row Limit",
      "default": 1000
    },
    {
      "fieldname": "section_break_visualization",
      "fieldtype": "Section Break",
      "label": "Visualization"
    },
    {
      "fieldname": "include_chart",
      "fieldtype": "Check",
      "label": "Include Chart"
    },
    {
      "fieldname": "chart_type",
      "fieldtype": "Select",
      "label": "Chart Type",
      "options": "\nBar\nLine\nPie\nDonut\nArea",
      "depends_on": "include_chart"
    },
    {
      "fieldname": "chart_config",
      "fieldtype": "Code",
      "label": "Chart Configuration",
      "options": "JSON",
      "depends_on": "include_chart"
    },
    {
      "fieldname": "section_break_access",
      "fieldtype": "Section Break",
      "label": "Access"
    },
    {
      "fieldname": "allowed_roles",
      "fieldtype": "Table MultiSelect",
      "label": "Allowed Roles",
      "options": "Report Access Role"
    }
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Report Manager", "read": 1, "write": 1, "create": 1}
  ]
}
```

---

## 2. Analytics Engine

### 2.1 Analytics Manager Class

```python
# university_erp/university_erp/analytics/analytics_manager.py

import frappe
from frappe import _
from frappe.utils import now_datetime, today, add_days, add_months, getdate
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

class AnalyticsManager:
    """
    Core analytics engine for data processing and calculations
    """

    @staticmethod
    def calculate_kpi(kpi_name: str, period_start: str = None,
                     period_end: str = None, context: Dict = None) -> float:
        """
        Calculate KPI value

        Args:
            kpi_name: KPI Definition name
            period_start: Start date
            period_end: End date
            context: Optional filters (department, program, etc.)

        Returns:
            Calculated KPI value
        """
        kpi = frappe.get_doc("KPI Definition", kpi_name)

        if kpi.calculation_method == "SQL Query":
            value = AnalyticsManager._execute_sql_kpi(kpi, period_start, period_end, context)
        elif kpi.calculation_method == "Python Method":
            value = AnalyticsManager._execute_method_kpi(kpi, period_start, period_end, context)
        elif kpi.calculation_method == "Formula":
            value = AnalyticsManager._calculate_formula_kpi(kpi, period_start, period_end, context)
        else:
            # Manual entry - get latest value
            value = frappe.db.get_value("KPI Value",
                {"kpi": kpi_name, "period_end": ["<=", period_end or today()]},
                "value",
                order_by="period_end desc"
            ) or 0

        return value

    @staticmethod
    def _execute_sql_kpi(kpi, period_start: str, period_end: str,
                        context: Dict = None) -> float:
        """Execute SQL-based KPI"""
        query = kpi.sql_query

        # Replace placeholders
        query = query.replace("{period_start}", f"'{period_start}'") if period_start else query
        query = query.replace("{period_end}", f"'{period_end}'") if period_end else query

        if context:
            for key, value in context.items():
                query = query.replace(f"{{{key}}}", f"'{value}'")

        try:
            result = frappe.db.sql(query)
            return float(result[0][0]) if result and result[0][0] else 0
        except Exception as e:
            frappe.log_error(f"KPI SQL Error: {str(e)}", "KPI Calculation")
            return 0

    @staticmethod
    def _execute_method_kpi(kpi, period_start: str, period_end: str,
                           context: Dict = None) -> float:
        """Execute Python method-based KPI"""
        try:
            method = frappe.get_attr(kpi.python_method)
            return method(period_start, period_end, context)
        except Exception as e:
            frappe.log_error(f"KPI Method Error: {str(e)}", "KPI Calculation")
            return 0

    @staticmethod
    def _calculate_formula_kpi(kpi, period_start: str, period_end: str,
                              context: Dict = None) -> float:
        """Calculate formula-based KPI using other KPIs"""
        formula = kpi.formula

        # Find all KPI references in formula
        import re
        kpi_refs = re.findall(r'\{([A-Z0-9_]+)\}', formula)

        for ref in kpi_refs:
            ref_kpi = frappe.db.get_value("KPI Definition", {"kpi_code": ref}, "name")
            if ref_kpi:
                ref_value = AnalyticsManager.calculate_kpi(ref_kpi, period_start, period_end, context)
                formula = formula.replace(f"{{{ref}}}", str(ref_value))

        try:
            return eval(formula)
        except Exception as e:
            frappe.log_error(f"KPI Formula Error: {str(e)}", "KPI Calculation")
            return 0

    @staticmethod
    def store_kpi_value(kpi_name: str, value: float, period_type: str,
                       period_start: str, period_end: str,
                       context: Dict = None):
        """
        Store calculated KPI value
        """
        kpi = frappe.get_doc("KPI Definition", kpi_name)

        # Check for existing value
        existing = frappe.db.get_value("KPI Value", {
            "kpi": kpi_name,
            "period_start": period_start,
            "period_end": period_end,
            "department": context.get("department") if context else None,
            "program": context.get("program") if context else None
        })

        if existing:
            kpi_value = frappe.get_doc("KPI Value", existing)
        else:
            kpi_value = frappe.new_doc("KPI Value")
            kpi_value.kpi = kpi_name
            kpi_value.period_type = period_type
            kpi_value.period_start = period_start
            kpi_value.period_end = period_end

        kpi_value.value = value
        kpi_value.target = kpi.target_value
        kpi_value.calculated_on = now_datetime()
        kpi_value.calculation_source = "Auto Calculated"

        # Calculate variance
        if kpi.target_value:
            kpi_value.variance = ((value - kpi.target_value) / kpi.target_value) * 100

        # Determine status
        if kpi.higher_is_better:
            if value >= kpi.green_threshold:
                kpi_value.status = "Green"
            elif value >= kpi.yellow_threshold:
                kpi_value.status = "Yellow"
            else:
                kpi_value.status = "Red"
        else:
            if value <= kpi.green_threshold:
                kpi_value.status = "Green"
            elif value <= kpi.yellow_threshold:
                kpi_value.status = "Yellow"
            else:
                kpi_value.status = "Red"

        # Set context
        if context:
            kpi_value.department = context.get("department")
            kpi_value.program = context.get("program")
            kpi_value.academic_year = context.get("academic_year")

        kpi_value.save()
        return kpi_value.name

    @staticmethod
    def get_trend_data(kpi_name: str, periods: int = 12,
                      period_type: str = "Monthly") -> List[Dict]:
        """
        Get trend data for a KPI

        Args:
            kpi_name: KPI Definition name
            periods: Number of periods to fetch
            period_type: Daily, Weekly, Monthly, Quarterly, Yearly

        Returns:
            List of {period, value, target, status}
        """
        values = frappe.get_all("KPI Value",
            filters={
                "kpi": kpi_name,
                "period_type": period_type
            },
            fields=["period_start", "period_end", "value", "target", "status", "variance"],
            order_by="period_start desc",
            limit=periods
        )

        # Reverse to get chronological order
        return list(reversed(values))

    @staticmethod
    def get_comparison_data(kpi_name: str, period_start: str, period_end: str,
                           comparison_type: str = "YoY") -> Dict:
        """
        Get comparison data for a KPI

        Args:
            kpi_name: KPI name
            period_start: Current period start
            period_end: Current period end
            comparison_type: YoY (Year over Year), MoM (Month over Month), QoQ

        Returns:
            Comparison data dictionary
        """
        current_value = AnalyticsManager.calculate_kpi(kpi_name, period_start, period_end)

        # Calculate comparison period
        if comparison_type == "YoY":
            comp_start = add_months(getdate(period_start), -12)
            comp_end = add_months(getdate(period_end), -12)
        elif comparison_type == "MoM":
            comp_start = add_months(getdate(period_start), -1)
            comp_end = add_months(getdate(period_end), -1)
        elif comparison_type == "QoQ":
            comp_start = add_months(getdate(period_start), -3)
            comp_end = add_months(getdate(period_end), -3)
        else:
            comp_start = comp_end = None

        previous_value = 0
        if comp_start and comp_end:
            previous_value = AnalyticsManager.calculate_kpi(kpi_name, str(comp_start), str(comp_end))

        change = current_value - previous_value
        change_percent = ((change / previous_value) * 100) if previous_value else 0

        return {
            "current_value": current_value,
            "previous_value": previous_value,
            "change": change,
            "change_percent": round(change_percent, 2),
            "comparison_period": f"{comp_start} to {comp_end}"
        }


class DashboardEngine:
    """
    Engine for rendering dashboards and widgets
    """

    @staticmethod
    def get_dashboard_data(dashboard_name: str, filters: Dict = None) -> Dict:
        """
        Get all data for a dashboard

        Args:
            dashboard_name: Dashboard name
            filters: Global filters

        Returns:
            Dashboard data with all widget data
        """
        dashboard = frappe.get_doc("Custom Dashboard", dashboard_name)

        # Increment view count
        frappe.db.set_value("Custom Dashboard", dashboard_name, "view_count",
                          (dashboard.view_count or 0) + 1)

        widgets_data = []
        for widget in dashboard.widgets:
            widget_data = DashboardEngine.get_widget_data(widget, filters)
            widgets_data.append({
                "title": widget.widget_title,
                "type": widget.widget_type,
                "chart_type": widget.chart_type,
                "position": {"row": widget.position_row, "col": widget.position_col},
                "size": {"width": widget.width, "height": widget.height},
                "color": widget.color,
                "icon": widget.icon,
                "drill_down": widget.drill_down_link,
                "data": widget_data
            })

        return {
            "dashboard": {
                "name": dashboard.dashboard_name,
                "type": dashboard.dashboard_type,
                "layout": dashboard.layout_type,
                "columns": dashboard.columns,
                "refresh_interval": dashboard.refresh_interval
            },
            "filters": {
                "date_enabled": dashboard.enable_date_filter,
                "department_enabled": dashboard.enable_department_filter,
                "program_enabled": dashboard.enable_program_filter
            },
            "widgets": widgets_data
        }

    @staticmethod
    def get_widget_data(widget, filters: Dict = None) -> Any:
        """
        Get data for a single widget

        Args:
            widget: Dashboard Widget row
            filters: Applied filters

        Returns:
            Widget data
        """
        if widget.data_source == "Report":
            return DashboardEngine._get_report_data(widget.report_name, filters)
        elif widget.data_source == "Query":
            return DashboardEngine._execute_query(widget.custom_query, filters)
        elif widget.data_source == "Method":
            return DashboardEngine._execute_method(widget.method_path, filters)
        else:
            return None

    @staticmethod
    def _get_report_data(report_name: str, filters: Dict = None) -> Dict:
        """Execute a report and return data"""
        try:
            from frappe.desk.query_report import run
            result = run(report_name, filters=filters or {})
            return {
                "columns": result.get("columns", []),
                "data": result.get("result", [])[:100],  # Limit rows for widgets
                "chart": result.get("chart")
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _execute_query(query: str, filters: Dict = None) -> List:
        """Execute custom SQL query"""
        try:
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.replace(f":{key}", f"'{value}'")

            return frappe.db.sql(query, as_dict=True)
        except Exception as e:
            return [{"error": str(e)}]

    @staticmethod
    def _execute_method(method_path: str, filters: Dict = None) -> Any:
        """Execute Python method"""
        try:
            method = frappe.get_attr(method_path)
            return method(filters)
        except Exception as e:
            return {"error": str(e)}


class ReportScheduler:
    """
    Handles scheduled report generation and delivery
    """

    @staticmethod
    def run_scheduled_reports():
        """
        Run all due scheduled reports (called by scheduler)
        """
        now = now_datetime()

        due_reports = frappe.get_all("Scheduled Report",
            filters={
                "is_enabled": 1,
                "next_run": ["<=", now]
            },
            fields=["name"]
        )

        for report in due_reports:
            ReportScheduler.execute_report(report.name)

    @staticmethod
    def execute_report(scheduled_report_name: str):
        """
        Execute a scheduled report
        """
        sr = frappe.get_doc("Scheduled Report", scheduled_report_name)

        try:
            # Prepare filters
            filters = json.loads(sr.filters) if sr.filters else {}

            if sr.dynamic_filters:
                filters = ReportScheduler._apply_dynamic_filters(filters, sr.frequency)

            # Generate report
            from frappe.desk.query_report import run
            result = run(sr.report, filters=filters)

            # Generate output file
            file_path = ReportScheduler._generate_output(sr, result)

            # Deliver report
            if sr.delivery_method in ["Email", "Both"]:
                ReportScheduler._send_email(sr, file_path)

            if sr.delivery_method in ["File Storage", "Both"] and sr.storage_folder:
                ReportScheduler._store_file(sr, file_path)

            # Update status
            sr.last_run = now_datetime()
            sr.last_run_status = "Success"
            sr.run_count = (sr.run_count or 0) + 1

        except Exception as e:
            sr.last_run = now_datetime()
            sr.last_run_status = "Failed"
            frappe.log_error(f"Scheduled Report Error: {str(e)}", sr.name)

        # Calculate next run
        sr.next_run = ReportScheduler._calculate_next_run(sr)
        sr.save()

    @staticmethod
    def _apply_dynamic_filters(filters: Dict, frequency: str) -> Dict:
        """Apply dynamic date filters based on frequency"""
        today_date = getdate(today())

        if frequency == "Daily":
            filters["from_date"] = add_days(today_date, -1)
            filters["to_date"] = add_days(today_date, -1)
        elif frequency == "Weekly":
            filters["from_date"] = add_days(today_date, -7)
            filters["to_date"] = add_days(today_date, -1)
        elif frequency == "Monthly":
            filters["from_date"] = add_months(today_date, -1)
            filters["to_date"] = add_days(today_date, -1)
        elif frequency == "Quarterly":
            filters["from_date"] = add_months(today_date, -3)
            filters["to_date"] = add_days(today_date, -1)

        return filters

    @staticmethod
    def _generate_output(sr, result) -> str:
        """Generate report output file"""
        from frappe.utils.pdf import get_pdf
        from frappe.utils.xlsxutils import make_xlsx

        filename = f"{sr.report_name}_{today()}"

        if sr.output_format == "PDF":
            html = frappe.render_template("templates/reports/report_pdf.html", {
                "title": sr.report_name,
                "columns": result.get("columns", []),
                "data": result.get("result", []),
                "chart": result.get("chart") if sr.include_charts else None
            })
            content = get_pdf(html)
            file_path = f"/tmp/{filename}.pdf"
            with open(file_path, "wb") as f:
                f.write(content)

        elif sr.output_format == "Excel":
            content = make_xlsx(result.get("result", []), sr.report_name)
            file_path = f"/tmp/{filename}.xlsx"
            content.save(file_path)

        elif sr.output_format == "CSV":
            import csv
            file_path = f"/tmp/{filename}.csv"
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                # Write headers
                writer.writerow([c.get("label") for c in result.get("columns", [])])
                # Write data
                for row in result.get("result", []):
                    if isinstance(row, dict):
                        writer.writerow(row.values())
                    else:
                        writer.writerow(row)

        else:  # HTML
            file_path = f"/tmp/{filename}.html"
            html = frappe.render_template("templates/reports/report_html.html", {
                "title": sr.report_name,
                "columns": result.get("columns", []),
                "data": result.get("result", [])
            })
            with open(file_path, "w") as f:
                f.write(html)

        return file_path

    @staticmethod
    def _send_email(sr, file_path: str):
        """Send report via email"""
        recipients = [r.email for r in sr.recipients if r.email]

        if recipients:
            frappe.sendmail(
                recipients=recipients,
                subject=f"Scheduled Report: {sr.report_name} - {today()}",
                message=f"Please find attached the scheduled report: {sr.report_name}",
                attachments=[{
                    "fname": file_path.split("/")[-1],
                    "fcontent": open(file_path, "rb").read()
                }]
            )

    @staticmethod
    def _store_file(sr, file_path: str):
        """Store report file"""
        import shutil
        dest_path = f"{sr.storage_folder}/{file_path.split('/')[-1]}"
        shutil.copy(file_path, dest_path)

    @staticmethod
    def _calculate_next_run(sr) -> datetime:
        """Calculate next scheduled run time"""
        from frappe.utils import get_datetime

        base_time = get_datetime(f"{today()} {sr.time_of_day}")

        if sr.frequency == "Daily":
            return base_time + timedelta(days=1)
        elif sr.frequency == "Weekly":
            days_ahead = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"].index(sr.day_of_week)
            current_day = base_time.weekday()
            days_until = (days_ahead - current_day + 7) % 7 or 7
            return base_time + timedelta(days=days_until)
        elif sr.frequency == "Monthly":
            next_month = add_months(base_time, 1)
            return next_month.replace(day=min(sr.day_of_month, 28))
        elif sr.frequency == "Quarterly":
            next_quarter = add_months(base_time, 3)
            return next_quarter.replace(day=min(sr.day_of_month, 28))

        return base_time + timedelta(days=1)
```

---

## 3. Pre-built KPIs

### 3.1 Academic KPIs

```python
# university_erp/university_erp/analytics/kpis/academic_kpis.py

import frappe

def student_pass_percentage(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate overall student pass percentage"""
    filters = {"docstatus": 1}
    if context and context.get("program"):
        filters["program"] = context["program"]

    total = frappe.db.count("Assessment Result", filters)
    passed = frappe.db.count("Assessment Result", {**filters, "grade": ["not in", ["F", "Fail"]]})

    return (passed / total * 100) if total > 0 else 0


def average_cgpa(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate average CGPA across students"""
    filters = {}
    if context and context.get("program"):
        filters["program"] = context["program"]

    result = frappe.db.sql("""
        SELECT AVG(cgpa) FROM `tabStudent CGPA`
        WHERE academic_year = (SELECT name FROM `tabAcademic Year` WHERE is_default = 1)
    """)

    return float(result[0][0]) if result and result[0][0] else 0


def student_attendance_rate(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate average student attendance rate"""
    total = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabStudent Attendance`
        WHERE attendance_date BETWEEN %s AND %s
    """, (period_start, period_end))[0][0] or 0

    present = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabStudent Attendance`
        WHERE attendance_date BETWEEN %s AND %s
        AND status = 'Present'
    """, (period_start, period_end))[0][0] or 0

    return (present / total * 100) if total > 0 else 0


def faculty_student_ratio(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate faculty to student ratio"""
    students = frappe.db.count("Student", {"enabled": 1})
    faculty = frappe.db.count("Faculty Member", {"status": "Active"})

    return (students / faculty) if faculty > 0 else 0


def course_completion_rate(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate course completion rate"""
    total_enrollments = frappe.db.count("Course Enrollment", {
        "enrollment_date": ["between", [period_start, period_end]]
    })

    completed = frappe.db.count("Course Enrollment", {
        "enrollment_date": ["between", [period_start, period_end]],
        "status": "Completed"
    })

    return (completed / total_enrollments * 100) if total_enrollments > 0 else 0
```

### 3.2 Financial KPIs

```python
# university_erp/university_erp/analytics/kpis/financial_kpis.py

import frappe

def fee_collection_rate(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate fee collection rate"""
    total_due = frappe.db.sql("""
        SELECT SUM(grand_total) FROM `tabFees`
        WHERE due_date BETWEEN %s AND %s
    """, (period_start, period_end))[0][0] or 0

    collected = frappe.db.sql("""
        SELECT SUM(paid_amount) FROM `tabFees`
        WHERE due_date BETWEEN %s AND %s
    """, (period_start, period_end))[0][0] or 0

    return (collected / total_due * 100) if total_due > 0 else 0


def revenue_per_student(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate average revenue per student"""
    total_revenue = frappe.db.sql("""
        SELECT SUM(paid_amount) FROM `tabFees`
        WHERE posting_date BETWEEN %s AND %s
    """, (period_start, period_end))[0][0] or 0

    students = frappe.db.count("Student", {"enabled": 1})

    return (total_revenue / students) if students > 0 else 0


def outstanding_fees_percentage(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate outstanding fees percentage"""
    total = frappe.db.sql("""
        SELECT SUM(grand_total) FROM `tabFees`
        WHERE due_date <= %s
    """, period_end)[0][0] or 0

    outstanding = frappe.db.sql("""
        SELECT SUM(outstanding_amount) FROM `tabFees`
        WHERE due_date <= %s AND outstanding_amount > 0
    """, period_end)[0][0] or 0

    return (outstanding / total * 100) if total > 0 else 0


def scholarship_utilization(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate scholarship fund utilization"""
    allocated = frappe.db.sql("""
        SELECT SUM(allocated_amount) FROM `tabScholarship`
        WHERE academic_year = (SELECT name FROM `tabAcademic Year` WHERE is_default = 1)
    """)[0][0] or 0

    disbursed = frappe.db.sql("""
        SELECT SUM(amount) FROM `tabScholarship Award`
        WHERE posting_date BETWEEN %s AND %s AND docstatus = 1
    """, (period_start, period_end))[0][0] or 0

    return (disbursed / allocated * 100) if allocated > 0 else 0
```

### 3.3 Admission KPIs

```python
# university_erp/university_erp/analytics/kpis/admission_kpis.py

import frappe

def admission_conversion_rate(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate admission conversion rate (applications to admissions)"""
    applications = frappe.db.count("Student Applicant", {
        "application_date": ["between", [period_start, period_end]]
    })

    admissions = frappe.db.count("Student Applicant", {
        "application_date": ["between", [period_start, period_end]],
        "application_status": "Approved"
    })

    return (admissions / applications * 100) if applications > 0 else 0


def seat_fill_rate(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate seat fill rate across programs"""
    total_seats = frappe.db.sql("""
        SELECT SUM(max_strength) FROM `tabProgram`
        WHERE is_published = 1
    """)[0][0] or 0

    enrolled = frappe.db.count("Program Enrollment", {
        "enrollment_date": ["between", [period_start, period_end]]
    })

    return (enrolled / total_seats * 100) if total_seats > 0 else 0


def average_application_processing_time(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate average application processing time in days"""
    result = frappe.db.sql("""
        SELECT AVG(DATEDIFF(modified, application_date))
        FROM `tabStudent Applicant`
        WHERE application_date BETWEEN %s AND %s
        AND application_status IN ('Approved', 'Rejected')
    """, (period_start, period_end))

    return float(result[0][0]) if result and result[0][0] else 0


def application_rejection_rate(period_start: str, period_end: str, context: dict = None) -> float:
    """Calculate application rejection rate"""
    total = frappe.db.count("Student Applicant", {
        "application_date": ["between", [period_start, period_end]],
        "application_status": ["in", ["Approved", "Rejected"]]
    })

    rejected = frappe.db.count("Student Applicant", {
        "application_date": ["between", [period_start, period_end]],
        "application_status": "Rejected"
    })

    return (rejected / total * 100) if total > 0 else 0
```

---

## 4. Pre-built Dashboards

### 4.1 Executive Dashboard Data

```python
# university_erp/university_erp/analytics/dashboards/executive_dashboard.py

import frappe
from frappe.utils import today, add_months, getdate

def get_executive_dashboard_data(filters: dict = None) -> dict:
    """
    Get data for executive dashboard
    """
    period_end = today()
    period_start = add_months(getdate(period_end), -1)

    return {
        "overview": get_overview_metrics(period_start, period_end),
        "enrollment_trend": get_enrollment_trend(),
        "financial_summary": get_financial_summary(period_start, period_end),
        "department_performance": get_department_performance(),
        "recent_alerts": get_alerts(),
        "kpi_summary": get_kpi_summary()
    }


def get_overview_metrics(period_start: str, period_end: str) -> dict:
    """Get high-level overview metrics"""
    return {
        "total_students": frappe.db.count("Student", {"enabled": 1}),
        "total_faculty": frappe.db.count("Faculty Member", {"status": "Active"}),
        "total_programs": frappe.db.count("Program", {"is_published": 1}),
        "total_courses": frappe.db.count("Course", {"is_published": 1}),
        "active_applications": frappe.db.count("Student Applicant", {
            "application_status": ["in", ["Applied", "Under Review"]]
        }),
        "fee_collection_today": frappe.db.sql("""
            SELECT SUM(paid_amount) FROM `tabPayment Entry`
            WHERE posting_date = %s AND docstatus = 1
        """, today())[0][0] or 0
    }


def get_enrollment_trend() -> list:
    """Get enrollment trend for last 12 months"""
    return frappe.db.sql("""
        SELECT
            DATE_FORMAT(enrollment_date, '%%Y-%%m') as month,
            COUNT(*) as count
        FROM `tabProgram Enrollment`
        WHERE enrollment_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(enrollment_date, '%%Y-%%m')
        ORDER BY month
    """, as_dict=True)


def get_financial_summary(period_start: str, period_end: str) -> dict:
    """Get financial summary"""
    total_fees = frappe.db.sql("""
        SELECT SUM(grand_total) FROM `tabFees`
        WHERE due_date BETWEEN %s AND %s
    """, (period_start, period_end))[0][0] or 0

    collected = frappe.db.sql("""
        SELECT SUM(paid_amount) FROM `tabFees`
        WHERE posting_date BETWEEN %s AND %s
    """, (period_start, period_end))[0][0] or 0

    return {
        "total_fees_due": total_fees,
        "collected": collected,
        "outstanding": total_fees - collected,
        "collection_rate": (collected / total_fees * 100) if total_fees > 0 else 0
    }


def get_department_performance() -> list:
    """Get department-wise performance metrics"""
    return frappe.db.sql("""
        SELECT
            d.department_name,
            COUNT(DISTINCT s.name) as students,
            COUNT(DISTINCT f.name) as faculty,
            AVG(ar.percentage) as avg_score
        FROM `tabDepartment` d
        LEFT JOIN `tabStudent` s ON s.department = d.name AND s.enabled = 1
        LEFT JOIN `tabFaculty Member` f ON f.department = d.name AND f.status = 'Active'
        LEFT JOIN `tabAssessment Result` ar ON ar.program IN (
            SELECT name FROM `tabProgram` WHERE department = d.name
        )
        GROUP BY d.name, d.department_name
        ORDER BY students DESC
        LIMIT 10
    """, as_dict=True)


def get_alerts() -> list:
    """Get system alerts and notifications"""
    alerts = []

    # Fee collection alert
    overdue_fees = frappe.db.count("Fees", {
        "outstanding_amount": [">", 0],
        "due_date": ["<", today()]
    })
    if overdue_fees > 0:
        alerts.append({
            "type": "warning",
            "title": "Overdue Fees",
            "message": f"{overdue_fees} students have overdue fees",
            "link": "/app/fees?outstanding_amount=%3E0"
        })

    # Attendance alert
    low_attendance = frappe.db.sql("""
        SELECT COUNT(DISTINCT student) FROM `tabStudent Attendance`
        WHERE attendance_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY student
        HAVING SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*) < 0.75
    """)[0][0] if frappe.db.sql("""
        SELECT COUNT(DISTINCT student) FROM `tabStudent Attendance`
        WHERE attendance_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY student
        HAVING SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*) < 0.75
    """) else 0

    if low_attendance > 0:
        alerts.append({
            "type": "info",
            "title": "Low Attendance",
            "message": f"{low_attendance} students have attendance below 75%",
            "link": "/app/query-report/Student%20Attendance%20Summary"
        })

    # Grievance alert
    pending_grievances = frappe.db.count("Grievance", {
        "status": ["not in", ["Resolved", "Closed"]],
        "sla_status": "Breached"
    })
    if pending_grievances > 0:
        alerts.append({
            "type": "danger",
            "title": "SLA Breached Grievances",
            "message": f"{pending_grievances} grievances have breached SLA",
            "link": "/app/grievance?sla_status=Breached"
        })

    return alerts


def get_kpi_summary() -> list:
    """Get summary of key KPIs"""
    kpis = frappe.get_all("KPI Definition",
        filters={"show_on_executive_dashboard": 1, "is_active": 1},
        fields=["name", "kpi_name", "category", "unit"]
    )

    summary = []
    for kpi in kpis:
        latest = frappe.db.get_value("KPI Value",
            {"kpi": kpi.name},
            ["value", "target", "status", "variance"],
            order_by="period_end desc",
            as_dict=True
        )

        if latest:
            summary.append({
                "name": kpi.kpi_name,
                "category": kpi.category,
                "value": latest.value,
                "unit": kpi.unit,
                "target": latest.target,
                "status": latest.status,
                "variance": latest.variance
            })

    return summary
```

---

## 5. Report Templates

### 5.1 Student Performance Report

```python
# university_erp/university_erp/analytics/report/student_performance_analysis/student_performance_analysis.py

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary

def get_columns():
    return [
        {"label": "Student", "fieldname": "student_name", "fieldtype": "Data", "width": 180},
        {"label": "Program", "fieldname": "program", "fieldtype": "Link", "options": "Program", "width": 150},
        {"label": "Semester", "fieldname": "semester", "fieldtype": "Int", "width": 80},
        {"label": "SGPA", "fieldname": "sgpa", "fieldtype": "Float", "width": 80},
        {"label": "CGPA", "fieldname": "cgpa", "fieldtype": "Float", "width": 80},
        {"label": "Credits Earned", "fieldname": "credits", "fieldtype": "Int", "width": 110},
        {"label": "Attendance %", "fieldname": "attendance", "fieldtype": "Percent", "width": 110},
        {"label": "Backlogs", "fieldname": "backlogs", "fieldtype": "Int", "width": 80},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100}
    ]

def get_data(filters):
    conditions = ""
    if filters.get("program"):
        conditions += f" AND pe.program = '{filters.get('program')}'"
    if filters.get("academic_year"):
        conditions += f" AND pe.academic_year = '{filters.get('academic_year')}'"
    if filters.get("department"):
        conditions += f" AND p.department = '{filters.get('department')}'"

    return frappe.db.sql(f"""
        SELECT
            s.name as student,
            s.student_name,
            pe.program,
            pe.current_semester as semester,
            COALESCE(sc.sgpa, 0) as sgpa,
            COALESCE(sc.cgpa, 0) as cgpa,
            COALESCE(sc.total_credits, 0) as credits,
            COALESCE(
                (SELECT SUM(CASE WHEN sa.status = 'Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
                 FROM `tabStudent Attendance` sa
                 WHERE sa.student = s.name
                 AND sa.attendance_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)),
            0) as attendance,
            COALESCE(
                (SELECT COUNT(*)
                 FROM `tabAssessment Result` ar
                 WHERE ar.student = s.name AND ar.grade IN ('F', 'Fail')),
            0) as backlogs,
            CASE
                WHEN sc.cgpa >= 8 THEN 'Excellent'
                WHEN sc.cgpa >= 6 THEN 'Good'
                WHEN sc.cgpa >= 5 THEN 'Average'
                ELSE 'At Risk'
            END as status
        FROM `tabStudent` s
        JOIN `tabProgram Enrollment` pe ON pe.student = s.name
        JOIN `tabProgram` p ON p.name = pe.program
        LEFT JOIN `tabStudent CGPA` sc ON sc.student = s.name
        WHERE s.enabled = 1
        {conditions}
        ORDER BY sc.cgpa DESC
    """, as_dict=True)

def get_chart(data):
    # Distribution chart
    excellent = len([d for d in data if d.status == "Excellent"])
    good = len([d for d in data if d.status == "Good"])
    average = len([d for d in data if d.status == "Average"])
    at_risk = len([d for d in data if d.status == "At Risk"])

    return {
        "data": {
            "labels": ["Excellent", "Good", "Average", "At Risk"],
            "datasets": [{"values": [excellent, good, average, at_risk]}]
        },
        "type": "pie",
        "colors": ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
    }

def get_summary(data):
    if not data:
        return []

    avg_cgpa = sum(d.cgpa or 0 for d in data) / len(data)
    avg_attendance = sum(d.attendance or 0 for d in data) / len(data)
    at_risk_count = len([d for d in data if d.status == "At Risk"])

    return [
        {"label": "Total Students", "value": len(data), "indicator": "Blue"},
        {"label": "Average CGPA", "value": f"{avg_cgpa:.2f}", "indicator": "Green" if avg_cgpa >= 7 else "Orange"},
        {"label": "Average Attendance", "value": f"{avg_attendance:.1f}%", "indicator": "Green" if avg_attendance >= 75 else "Red"},
        {"label": "At Risk Students", "value": at_risk_count, "indicator": "Red" if at_risk_count > 10 else "Green"}
    ]
```

---

## 6. API Endpoints

### 6.1 Analytics API

```python
# university_erp/university_erp/analytics/api.py

import frappe
from frappe import _
from university_erp.university_erp.analytics.analytics_manager import (
    AnalyticsManager, DashboardEngine
)

@frappe.whitelist()
def get_dashboard(dashboard_name: str, filters: str = None):
    """API to get dashboard data"""
    filter_dict = frappe.parse_json(filters) if filters else {}
    return DashboardEngine.get_dashboard_data(dashboard_name, filter_dict)


@frappe.whitelist()
def get_kpi_value(kpi_name: str, period_start: str = None,
                 period_end: str = None, context: str = None):
    """API to get KPI value"""
    context_dict = frappe.parse_json(context) if context else {}
    value = AnalyticsManager.calculate_kpi(kpi_name, period_start, period_end, context_dict)
    return {"kpi": kpi_name, "value": value}


@frappe.whitelist()
def get_kpi_trend(kpi_name: str, periods: int = 12, period_type: str = "Monthly"):
    """API to get KPI trend data"""
    return AnalyticsManager.get_trend_data(kpi_name, int(periods), period_type)


@frappe.whitelist()
def get_kpi_comparison(kpi_name: str, period_start: str, period_end: str,
                      comparison_type: str = "YoY"):
    """API to get KPI comparison data"""
    return AnalyticsManager.get_comparison_data(kpi_name, period_start, period_end, comparison_type)


@frappe.whitelist()
def get_quick_stats():
    """API to get quick statistics for header widgets"""
    return {
        "students": frappe.db.count("Student", {"enabled": 1}),
        "faculty": frappe.db.count("Faculty Member", {"status": "Active"}),
        "courses": frappe.db.count("Course", {"is_published": 1}),
        "applications": frappe.db.count("Student Applicant", {
            "application_status": ["in", ["Applied", "Under Review"]]
        })
    }


@frappe.whitelist()
def execute_custom_report(report_definition: str, filters: str = None):
    """API to execute a custom report definition"""
    from university_erp.university_erp.analytics.custom_report_builder import build_and_execute

    filter_dict = frappe.parse_json(filters) if filters else {}
    return build_and_execute(report_definition, filter_dict)
```

---

## 7. Implementation Checklist

### Week 1: Core Analytics
- [ ] Create KPI Definition DocType
- [ ] Create KPI Value DocType
- [ ] Implement AnalyticsManager class
- [ ] Create KPI calculation methods
- [ ] Build KPI storage mechanism
- [ ] Implement trend analysis
- [ ] Create comparison calculations

### Week 2: Dashboard System
- [ ] Create Custom Dashboard DocType
- [ ] Create Dashboard Widget child table
- [ ] Implement DashboardEngine class
- [ ] Build widget data fetchers
- [ ] Create dashboard rendering API
- [ ] Implement dashboard filters
- [ ] Add auto-refresh functionality

### Week 3: Scheduled Reports
- [ ] Create Scheduled Report DocType
- [ ] Implement ReportScheduler class
- [ ] Build output generation (PDF, Excel, CSV)
- [ ] Create email delivery
- [ ] Implement file storage
- [ ] Add scheduler jobs
- [ ] Create report history tracking

### Week 4: Custom Report Builder
- [ ] Create Custom Report Definition DocType
- [ ] Build report builder interface
- [ ] Implement query builder
- [ ] Add join support
- [ ] Create filter builder
- [ ] Implement aggregations
- [ ] Add visualization options

### Week 5: Pre-built Reports & Integration
- [ ] Create Academic KPIs
- [ ] Create Financial KPIs
- [ ] Create Admission KPIs
- [ ] Build Executive Dashboard
- [ ] Create Student Performance Report
- [ ] Implement portal integration
- [ ] Add API documentation

---

## 8. Sample KPI Configurations

### 8.1 Academic KPIs

| KPI Name | Calculation | Target | Tracking |
|----------|-------------|--------|----------|
| Student Pass Rate | SQL Query | 85% | Monthly |
| Average CGPA | SQL Query | 7.0 | Semester |
| Faculty-Student Ratio | Formula | 1:20 | Yearly |
| Course Completion Rate | Python Method | 90% | Semester |
| Research Publications | SQL Query | 50 | Yearly |

### 8.2 Financial KPIs

| KPI Name | Calculation | Target | Tracking |
|----------|-------------|--------|----------|
| Fee Collection Rate | SQL Query | 95% | Monthly |
| Revenue Per Student | Formula | ₹1,00,000 | Yearly |
| Outstanding Fees % | SQL Query | <5% | Monthly |
| Scholarship Utilization | SQL Query | 100% | Yearly |

### 8.3 Operational KPIs

| KPI Name | Calculation | Target | Tracking |
|----------|-------------|--------|----------|
| Grievance Resolution Time | SQL Query | 7 days | Monthly |
| Feedback Response Rate | SQL Query | 80% | Semester |
| System Uptime | External API | 99.9% | Daily |
| Support Ticket Resolution | SQL Query | 24 hours | Weekly |
