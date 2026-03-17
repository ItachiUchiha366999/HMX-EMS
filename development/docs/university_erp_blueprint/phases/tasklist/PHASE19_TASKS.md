# Phase 19: Analytics, Reporting & MIS - Task List

## Overview
This phase implements a comprehensive analytics and reporting framework including dashboards, custom report builder, scheduled reports, data visualization, KPI tracking, and executive MIS for informed decision-making.

**Module**: University ERP
**Total Estimated Tasks**: 114
**Priority**: High (Analytics & Reporting)
**Status**: Completed (100%)

---

## Section A: Child Table DocTypes

### A1. Dashboard Widget DocType (Child Table)
- [x] Create dashboard_widget folder in university_erp/doctype
- [x] Create dashboard_widget.json with fields:
  - widget_title (Data, reqd, in_list_view)
  - widget_type (Select: Number Card/Progress Card/Chart/Table/List/Calendar/Map/Gauge/Trend/Comparison, reqd, in_list_view)
  - data_source (Select: Report/Query/Method/Static, reqd)
  - report_name (Link: Report, depends_on data_source)
  - custom_query (Code: SQL, depends_on data_source)
  - method_path (Data, depends_on data_source)
  - chart_type (Select: Bar/Line/Pie/Donut/Area/Scatter/Heatmap/Funnel)
  - color (Color)
  - icon (Data)
  - position_row (Int)
  - position_col (Int)
  - width (Int)
  - height (Int)
  - drill_down_link (Data)
  - comparison_period (Select)
- [x] Create dashboard_widget.py controller
- [x] Create __init__.py file

### A2. Dashboard Role DocType (Child Table)
- [x] Create dashboard_role folder in university_erp/doctype
- [x] Create dashboard_role.json with fields:
  - role (Link: Role, reqd, in_list_view)
- [x] Create dashboard_role.py controller
- [x] Create __init__.py file

### A3. Dashboard User DocType (Child Table)
- [x] Create dashboard_user folder in university_erp/doctype
- [x] Create dashboard_user.json with fields:
  - user (Link: User, reqd, in_list_view)
- [x] Create dashboard_user.py controller
- [x] Create __init__.py file

### A4. Scheduled Report Recipient DocType (Child Table)
- [x] Create scheduled_report_recipient folder in university_erp/doctype
- [x] Create scheduled_report_recipient.json with fields:
  - email (Data, reqd, in_list_view)
  - user (Link: User)
  - cc (Check)
- [x] Create scheduled_report_recipient.py controller
- [x] Create __init__.py file

### A5. Report Column Definition DocType (Child Table)
- [x] Create report_column_definition folder in university_erp/doctype
- [x] Create report_column_definition.json with fields:
  - field_name (Data, reqd, in_list_view)
  - field_label (Data, reqd, in_list_view)
  - field_type (Select: Data/Int/Float/Currency/Date/Link, in_list_view)
  - width (Int)
  - link_to (Data)
  - aggregation (Select: None/Sum/Avg/Count/Min/Max)
  - format (Data)
- [x] Create report_column_definition.py controller
- [x] Create __init__.py file

### A6. Report Join Definition DocType (Child Table)
- [x] Create report_join_definition folder in university_erp/doctype
- [x] Create report_join_definition.json with fields:
  - doctype (Link: DocType, reqd, in_list_view)
  - join_type (Select: INNER/LEFT/RIGHT, in_list_view)
  - join_field (Data, reqd)
  - parent_field (Data, reqd)
- [x] Create report_join_definition.py controller
- [x] Create __init__.py file

### A7. Report Filter Definition DocType (Child Table)
- [x] Create report_filter_definition folder in university_erp/doctype
- [x] Create report_filter_definition.json with fields:
  - field_name (Data, reqd, in_list_view)
  - field_label (Data, reqd, in_list_view)
  - field_type (Select: Data/Link/Date/Select, in_list_view)
  - link_to (Data)
  - options (Text)
  - default_value (Data)
  - is_mandatory (Check)
- [x] Create report_filter_definition.py controller
- [x] Create __init__.py file

---

## Section B: Main DocTypes

### B1. Custom Dashboard DocType
- [x] Create custom_dashboard folder in university_erp/doctype
- [x] Create custom_dashboard.json with fields:
  - dashboard_name (Data, reqd, unique)
  - dashboard_type (Select: Executive/Academic/Financial/Admissions/Examination/Faculty/Student/Departmental/Custom, reqd)
  - description (Text)
  - is_public (Check)
  - owner_role (Link: Role)
  - refresh_interval (Select: Manual/1 minute/5 minutes/15 minutes/30 minutes/1 hour)
  - enable_date_filter (Check)
  - default_date_range (Select)
  - enable_department_filter (Check)
  - enable_program_filter (Check)
  - layout_type (Select: Grid/Freeform/Tabs)
  - columns (Int)
  - widgets (Table: Dashboard Widget)
  - allowed_roles (Table MultiSelect: Dashboard Role)
  - allowed_users (Table MultiSelect: Dashboard User)
  - is_active (Check)
  - view_count (Int, read_only)
- [x] Create custom_dashboard.py controller with:
  - validate() method
  - before_save() method
  - get_dashboard_data() method
  - has_access() method
  - increment_view_count() method
- [x] Create __init__.py file

### B2. KPI Definition DocType
- [x] Create kpi_definition folder in university_erp/doctype
- [x] Create kpi_definition.json with fields:
  - kpi_name (Data, reqd, unique)
  - kpi_code (Data, unique)
  - category (Select: Academic/Admissions/Financial/Faculty/Research/Infrastructure/Placement/Student Services/Governance, reqd)
  - description (Text)
  - unit (Data)
  - calculation_method (Select: SQL Query/Python Method/Formula/Manual Entry, reqd)
  - sql_query (Code: SQL)
  - python_method (Data)
  - formula (Code)
  - target_value (Float)
  - minimum_acceptable (Float)
  - stretch_target (Float)
  - red_threshold (Float)
  - yellow_threshold (Float)
  - green_threshold (Float)
  - higher_is_better (Check)
  - tracking_frequency (Select: Daily/Weekly/Monthly/Quarterly/Yearly)
  - responsible_role (Link: Role)
  - data_owner (Link: User)
  - is_active (Check)
  - show_on_executive_dashboard (Check)
  - benchmark_source (Data)
  - benchmark_value (Float)
- [x] Create kpi_definition.py controller with:
  - validate() method
  - validate_calculation_method() method
  - validate_thresholds() method
  - set_kpi_code() method
  - calculate_value() method
  - get_status() method
  - get_variance() method
- [x] Create __init__.py file

### B3. KPI Value DocType
- [x] Create kpi_value folder in university_erp/doctype
- [x] Create kpi_value.json with fields:
  - kpi (Link: KPI Definition, reqd, in_list_view)
  - period_type (Select: Daily/Weekly/Monthly/Quarterly/Yearly, reqd)
  - period_start (Date, reqd, in_list_view)
  - period_end (Date, reqd)
  - value (Float, reqd, in_list_view)
  - target (Float)
  - variance (Float, read_only)
  - status (Select: Green/Yellow/Red, read_only, in_list_view)
  - department (Link: Department)
  - program (Link: Program)
  - academic_year (Link: Academic Year)
  - calculated_on (Datetime, read_only)
  - calculation_source (Select: Auto Calculated/Manual Entry/Imported, read_only)
  - notes (Text)
- [x] Create kpi_value.py controller with:
  - validate() method
  - validate_dates() method
  - validate_period_type() method
  - before_save() method
  - calculate_variance() method
  - determine_status() method
- [x] Create __init__.py file

### B4. Scheduled Report DocType
- [x] Create scheduled_report folder in university_erp/doctype
- [x] Create scheduled_report.json with fields:
  - report_name (Data, reqd)
  - report (Link: Report, reqd)
  - description (Text)
  - is_enabled (Check)
  - frequency (Select: Daily/Weekly/Monthly/Quarterly, reqd)
  - day_of_week (Select: Monday-Sunday)
  - day_of_month (Int)
  - time_of_day (Time, reqd)
  - timezone (Select: Asia/Kolkata/UTC)
  - filters (Code: JSON)
  - dynamic_filters (Check)
  - output_format (Select: PDF/Excel/CSV/HTML)
  - include_charts (Check)
  - delivery_method (Select: Email/File Storage/Both)
  - recipients (Table: Scheduled Report Recipient)
  - storage_folder (Data)
  - last_run (Datetime, read_only)
  - last_run_status (Select: Success/Failed/Partial, read_only)
  - next_run (Datetime, read_only)
  - run_count (Int, read_only)
- [x] Create scheduled_report.py controller with:
  - validate() method
  - validate_schedule() method
  - validate_recipients() method
  - validate_filters() method
  - before_save() method
  - execute_report() method
  - calculate_next_run() method
  - send_report() method
- [x] Create __init__.py file

### B5. Custom Report Definition DocType
- [x] Create custom_report_definition folder in university_erp/doctype
- [x] Create custom_report_definition.json with fields:
  - report_title (Data, reqd)
  - report_type (Select: Tabular/Summary/Matrix/Pivot/Chart Only, reqd)
  - description (Text)
  - primary_doctype (Link: DocType, reqd)
  - is_public (Check)
  - columns (Table: Report Column Definition)
  - joins (Table: Report Join Definition)
  - filters (Table: Report Filter Definition)
  - group_by_fields (Small Text)
  - having_clause (Data)
  - sort_by (Data)
  - sort_order (Select: ASC/DESC)
  - row_limit (Int)
  - include_chart (Check)
  - chart_type (Select: Bar/Line/Pie/Donut/Area)
  - chart_config (Code: JSON)
  - allowed_roles (Table MultiSelect: Report Access Role)
- [x] Create custom_report_definition.py controller with:
  - validate() method
  - validate_columns() method
  - validate_chart_config() method
  - build_query() method
  - execute() method
  - generate_chart() method
  - has_access() method
- [x] Create __init__.py file

### B6. Report Access Role DocType (Link Table)
- [x] Create report_access_role folder in university_erp/doctype
- [x] Create report_access_role.json with fields:
  - role (Link: Role, reqd, in_list_view)
- [x] Create report_access_role.py controller
- [x] Create __init__.py file

---

## Section C: Analytics Engine

### C1. Analytics Manager Class
- [x] Create analytics folder in university_erp/university_erp
- [x] Create __init__.py file
- [x] Create analytics_manager.py with AnalyticsManager class:
  - calculate_kpi() method
  - _execute_sql_kpi() method
  - _execute_method_kpi() method
  - _calculate_formula_kpi() method
  - _get_latest_kpi_value() method
  - store_kpi_value() method
  - get_trend_data() method
  - get_comparison_data() method
  - _get_period_value() method
  - calculate_all_kpis() method

### C2. Dashboard Engine Class
- [x] Create dashboard_engine.py with DashboardEngine class:
  - get_dashboard_data() method
  - get_widget_data() method
  - _get_report_data() method
  - _execute_query() method
  - _execute_method() method
  - _get_static_data() method
  - _format_widget_data() method
  - _calculate_trend() method
  - get_available_dashboards() method

### C3. Report Scheduler Class
- [x] Create report_scheduler.py with ReportScheduler class:
  - run_scheduled_reports() method
  - execute_report() method
  - _apply_dynamic_filters() method
  - _generate_output() method
  - _generate_excel() method
  - _generate_csv() method
  - _generate_html() method
  - _generate_pdf() method
  - _send_email() method
  - _store_file() method
  - _calculate_next_run() method

---

## Section D: KPI Methods

### D1. Academic KPIs
- [x] Create kpis folder in university_erp/analytics
- [x] Create __init__.py file
- [x] Create academic_kpis.py with methods:
  - student_pass_percentage()
  - average_cgpa()
  - student_attendance_rate()
  - faculty_student_ratio()
  - course_completion_rate()

### D2. Financial KPIs
- [x] Create financial_kpis.py with methods:
  - fee_collection_rate()
  - revenue_per_student()
  - outstanding_fees_percentage()
  - scholarship_utilization()

### D3. Admission KPIs
- [x] Create admission_kpis.py with methods:
  - admission_conversion_rate()
  - seat_fill_rate()
  - average_application_processing_time()
  - application_rejection_rate()

---

## Section E: Dashboards & Reports

### E1. Executive Dashboard
- [x] Create dashboards folder in university_erp/analytics
- [x] Create __init__.py file
- [x] Create executive_dashboard.py with methods:
  - get_executive_dashboard_data()
  - get_overview_metrics()
  - get_enrollment_trend()
  - get_financial_summary()
  - get_department_performance()
  - get_alerts()
  - get_kpi_summary()

### E2. Student Performance Report
- [x] Create report folder: student_performance_analysis
- [x] Create student_performance_analysis.json with filters:
  - program (Link)
  - academic_year (Link)
  - department (Link)
- [x] Create student_performance_analysis.py with:
  - get_columns() function
  - get_data() function
  - get_chart() function
  - get_summary() function
- [x] Create student_performance_analysis.js with filters

### E3. MIS Workspace
- [x] Create analytics_mis workspace folder
- [x] Create analytics_mis.json with:
  - Shortcuts for Dashboards, KPIs, Reports
  - Links by category
  - Report shortcuts

---

## Section F: API & Scheduled Tasks

### F1. API Endpoints
- [x] Create api.py in university_erp/analytics with:
  - get_dashboard() API endpoint
  - get_available_dashboards() API endpoint
  - get_kpi_value() API endpoint
  - get_kpi_trend() API endpoint
  - get_kpi_comparison() API endpoint
  - get_quick_stats() API endpoint
  - execute_custom_report() API endpoint
  - get_all_kpis() API endpoint
  - calculate_kpi_now() API endpoint

### F2. Scheduled Tasks & Hooks
- [x] Create scheduled_tasks.py in university_erp/analytics with:
  - run_scheduled_reports() (daily)
  - calculate_daily_kpis() (daily)
  - calculate_weekly_kpis() (weekly)
  - calculate_monthly_kpis() (monthly)
  - calculate_quarterly_kpis() (monthly)
  - cleanup_old_kpi_values() (monthly)
  - update_dashboard_statistics() (daily)
  - check_kpi_alerts() (daily)
- [x] Update hooks.py with scheduler_events

---

## Section G: Testing

### G1. Unit Tests
- [x] Create tests folder in university_erp/analytics
- [x] Create __init__.py file
- [x] Create test_kpi_definition.py with:
  - TestKPIDefinition class
  - TestKPIValue class
- [x] Create test_custom_dashboard.py with:
  - TestCustomDashboard class
  - TestScheduledReport class
- [x] Create test_analytics_manager.py with:
  - TestAnalyticsManager class
  - TestDashboardEngine class
  - TestKPICalculationMethods class

---

## Summary

| Section | Total Tasks | Completed | Pending |
|---------|-------------|-----------|---------|
| A. Child Table DocTypes | 28 | 28 | 0 |
| B. Main DocTypes | 24 | 24 | 0 |
| C. Analytics Engine | 12 | 12 | 0 |
| D. KPI Methods | 15 | 15 | 0 |
| E. Dashboards & Reports | 16 | 16 | 0 |
| F. API & Scheduled Tasks | 12 | 12 | 0 |
| G. Testing | 7 | 7 | 0 |
| **Total** | **114** | **114** | **0** |

**Completion: 100%**

---

## Implementation Notes

### Files Created:
1. **Child Tables (7)**:
   - dashboard_widget, dashboard_role, dashboard_user
   - scheduled_report_recipient
   - report_column_definition, report_join_definition, report_filter_definition

2. **Main DocTypes (6)**:
   - custom_dashboard, kpi_definition, kpi_value
   - scheduled_report, custom_report_definition
   - report_access_role

3. **Analytics Engine (3 files)**:
   - analytics_manager.py
   - dashboard_engine.py
   - report_scheduler.py

4. **KPI Methods (3 files)**:
   - academic_kpis.py
   - financial_kpis.py
   - admission_kpis.py

5. **Dashboards (1 file)**:
   - executive_dashboard.py

6. **Reports (1)**:
   - Student Performance Analysis

7. **Workspace (1)**:
   - analytics_mis.json

8. **API (2 files)**:
   - api.py
   - scheduled_tasks.py

9. **Tests (3 files)**:
   - test_kpi_definition.py (includes TestKPIValue)
   - test_custom_dashboard.py (includes TestScheduledReport)
   - test_analytics_manager.py (includes TestDashboardEngine, TestKPICalculationMethods)

---

**Created**: 2026-01-15
**Status**: Completed (100%)
**Last Updated**: 2026-01-15
