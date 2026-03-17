# Phase 20: Accreditation & Compliance (NAAC/NBA) - Task List

## Overview
This phase implements comprehensive accreditation management for Indian higher education including NAAC (National Assessment and Accreditation Council), NBA (National Board of Accreditation), NIRF (National Institutional Ranking Framework), and UGC compliance. Features include automated data collection, criterion-wise documentation, SSR generation, CO-PO attainment calculation, and audit trail management.

**Module**: University ERP
**Total Estimated Tasks**: 130
**Priority**: High
**Status**: Completed (100%)

**Note**: OBE-related DocTypes (Course Outcome, Program Outcome, CO PO Mapping, CO PSO Mapping, CO Assessment Method Link, PO Yearly Attainment) already exist in the `university_obe` module. The accreditation engine classes integrate with the existing OBE module instead of creating duplicate DocTypes.

---

## Section A: Child Table DocTypes

### A1. Accreditation Program Link DocType (Child Table)
- [x] Create accreditation_program_link folder in university_erp/doctype
- [x] Create accreditation_program_link.json with fields:
  - program (Link: Program, reqd, in_list_view)
- [x] Create accreditation_program_link.py controller
- [x] Create __init__.py file

### A2. Accreditation Department Link DocType (Child Table)
- [x] Create accreditation_department_link folder in university_erp/doctype
- [x] Create accreditation_department_link.json with fields:
  - department (Link: Department, reqd, in_list_view)
- [x] Create accreditation_department_link.py controller
- [x] Create __init__.py file

### A3. Accreditation Team Member DocType (Child Table)
- [x] Create accreditation_team_member folder in university_erp/doctype
- [x] Create accreditation_team_member.json with fields:
  - user (Link: User, reqd, in_list_view)
  - member_name (Data, read_only, in_list_view)
  - role (Select: Coordinator/Member/Data Entry/Reviewer, in_list_view)
  - criterion_assigned (Data, in_list_view)
- [x] Create accreditation_team_member.py controller
- [x] Create __init__.py file

### A4. Accreditation Criterion DocType (Child Table)
- [x] Create accreditation_criterion folder in university_erp/doctype
- [x] Create accreditation_criterion.json with fields:
  - criterion_number (Data, in_list_view)
  - criterion_name (Data, in_list_view)
  - weightage (Float, in_list_view)
  - responsible_person (Link: User, in_list_view)
  - data_status (Select: Not Started/In Progress/Completed/Verified, in_list_view)
  - score (Float, in_list_view)
  - max_score (Float)
  - remarks (Small Text)
- [x] Create accreditation_criterion.py controller
- [x] Create __init__.py file

### A5. NAAC Metric Year Data DocType (Child Table)
- [x] Create naac_metric_year_data folder in university_erp/doctype
- [x] Create naac_metric_year_data.json with fields:
  - academic_year (Link: Academic Year, reqd, in_list_view)
  - value (Float, in_list_view)
  - numerator (Float, in_list_view)
  - denominator (Float, in_list_view)
  - remarks (Small Text)
- [x] Create naac_metric_year_data.py controller
- [x] Create __init__.py file

### A6. NAAC Metric Document DocType (Child Table)
- [x] Create naac_metric_document folder in university_erp/doctype
- [x] Create naac_metric_document.json with fields:
  - document_name (Data, reqd, in_list_view)
  - document_type (Select: Supporting/Policy/Report/Certificate, in_list_view)
  - file_url (Attach, reqd, in_list_view)
  - description (Small Text)
- [x] Create naac_metric_document.py controller
- [x] Create __init__.py file

### A7. NAAC Document Checklist Item DocType (Child Table)
- [x] Create naac_document_checklist_item folder in university_erp/doctype
- [x] Create naac_document_checklist_item.json with fields:
  - document_name (Data, reqd, in_list_view)
  - is_mandatory (Check, in_list_view)
  - is_uploaded (Check, in_list_view)
  - uploaded_date (Date)
  - remarks (Small Text)
- [x] Create naac_document_checklist_item.py controller
- [x] Create __init__.py file

### A8. CO PO Mapping DocType (Child Table) - SKIPPED (Existing in university_obe)
- [x] ~~Create co_po_mapping folder~~ - Already exists in university_obe module
- [x] ~~Create co_po_mapping.json~~ - Already exists in university_obe module
- [x] ~~Create co_po_mapping.py controller~~ - Already exists in university_obe module
- [x] ~~Create __init__.py file~~ - Already exists in university_obe module

### A9. CO PSO Mapping DocType (Child Table) - SKIPPED (Existing in university_obe)
- [x] ~~Create co_pso_mapping folder~~ - Already exists in university_obe module
- [x] ~~Create co_pso_mapping.json~~ - Already exists in university_obe module
- [x] ~~Create co_pso_mapping.py controller~~ - Already exists in university_obe module
- [x] ~~Create __init__.py file~~ - Already exists in university_obe module

### A10. CO Assessment Method Link DocType (Child Table) - SKIPPED (Existing in university_obe)
- [x] ~~Create co_assessment_method_link folder~~ - Already exists in university_obe module
- [x] ~~Create co_assessment_method_link.json~~ - Already exists in university_obe module
- [x] ~~Create co_assessment_method_link.py controller~~ - Already exists in university_obe module
- [x] ~~Create __init__.py file~~ - Already exists in university_obe module

### A11. PO Yearly Attainment DocType (Child Table) - SKIPPED (Existing in university_obe)
- [x] ~~Create po_yearly_attainment folder~~ - Already exists in university_obe module
- [x] ~~Create po_yearly_attainment.json~~ - Already exists in university_obe module
- [x] ~~Create po_yearly_attainment.py controller~~ - Already exists in university_obe module
- [x] ~~Create __init__.py file~~ - Already exists in university_obe module

---

## Section B: Main DocTypes

### B1. Accreditation Cycle DocType
- [x] Create accreditation_cycle folder in university_erp/doctype
- [x] Create accreditation_cycle.json with all fields from spec:
  - accreditation_body (Select: NAAC/NBA/NIRF/UGC/AICTE/Other)
  - cycle_name, cycle_number, assessment_year
  - data_period_start, data_period_end
  - scope_type (Select: Institution/Program/Department Level)
  - programs (Table MultiSelect), departments (Table MultiSelect)
  - Timeline fields (iiqa_submission_date, ssr_submission_deadline, etc.)
  - Coordination fields (coordinator, team_members table)
  - criteria (Table: Accreditation Criterion)
  - Result fields (grade_obtained, cgpa_obtained, validity_period, etc.)
  - status, overall_progress
- [x] Create accreditation_cycle.py controller with:
  - validate() method
  - before_save() method
  - calculate_progress() method
  - get_criterion_summary() method
- [x] Create __init__.py file

### B2. NAAC Metric DocType
- [x] Create naac_metric folder in university_erp/doctype
- [x] Create naac_metric.json with all fields from spec:
  - accreditation_cycle (Link)
  - criterion (Select: 1-7 criteria)
  - metric_number, metric_type, weightage
  - metric_description, data_requirements, formula
  - data_source, calculation_method, report_name
  - year_wise_data (Table), calculated_value, benchmark_value
  - score, max_score
  - documents (Table), document_checklist (Table)
  - narrative, best_practices
  - status, verified_by, verification_date, remarks
- [x] Create naac_metric.py controller with:
  - validate() method
  - calculate_value() method
  - update_status() method
- [x] Create __init__.py file

### B3. Course Outcome DocType - SKIPPED (Existing in university_obe)
- [x] ~~Create course_outcome folder~~ - Already exists in university_obe module
- [x] ~~Create course_outcome.json~~ - Already exists in university_obe module
- [x] ~~Create course_outcome.py controller~~ - Already exists in university_obe module
- [x] ~~Create __init__.py file~~ - Already exists in university_obe module

### B4. Program Outcome DocType - SKIPPED (Existing in university_obe)
- [x] ~~Create program_outcome folder~~ - Already exists in university_obe module
- [x] ~~Create program_outcome.json~~ - Already exists in university_obe module
- [x] ~~Create program_outcome.py controller~~ - Already exists in university_obe module
- [x] ~~Create __init__.py file~~ - Already exists in university_obe module

### B5. NIRF Data DocType
- [x] Create nirf_data folder in university_erp/doctype
- [x] Create nirf_data.json with all fields from spec:
  - ranking_year, category (Select: Overall/University/Engineering/etc.)
  - submission_deadline, submitted_date
  - TLR section fields (ss_student_strength, fsr_faculty_ratio, etc.)
  - RP section fields (pu_publications, qp_quality_publications, etc.)
  - GO section fields (gue_university_exams, gphd_phd_students, etc.)
  - OI section fields (rd_region_diversity, wd_women_diversity, etc.)
  - PR section field (pr_peer_perception)
  - Result fields (total_score, rank_obtained, band, status)
- [x] Create nirf_data.py controller with:
  - validate() method
  - calculate_total_score() method
  - collect_data() method
- [x] Create __init__.py file

---

## Section C: Accreditation Engine Classes

### C1. CO-PO Attainment Calculator
- [x] Create accreditation folder in university_erp/university_erp
- [x] Create __init__.py file
- [x] Create attainment_calculator.py with COPOAttainmentCalculator class:
  - __init__() method
  - _get_current_academic_year() method
  - _get_course_outcomes() method - Integrates with university_obe Course Outcome
  - calculate_direct_attainment() method
  - _get_co_assessment_data() method
  - calculate_indirect_attainment() method
  - _get_co_survey_data() method
  - calculate_overall_attainment() method
  - calculate_po_attainment() method - Integrates with university_obe Program Outcome
- [x] Add calculate_course_attainment() API function
- [x] Add calculate_program_attainment() API function

### C2. NAAC Data Collector
- [x] Create naac_data_collector.py with NAACDataCollector class:
  - __init__() method
  - collect_all_metrics() method
  - _collect_criterion_1() method (Curricular Aspects)
  - _collect_criterion_2() method (Teaching-Learning)
  - _collect_criterion_3() method (Research & Extension)
  - _collect_criterion_4() method (Infrastructure)
  - _collect_criterion_5() method (Student Support)
  - _collect_criterion_6() method (Governance)
  - _collect_criterion_7() method (Institutional Values)
  - Individual metric methods for each criterion
  - _get_assessment_years() helper method

### C3. SSR Generator
- [x] Create ssr_generator.py with SSRGenerator class:
  - __init__() method
  - _load_all_metrics() method
  - generate_ssr() method
  - _generate_executive_summary() method
  - _generate_institutional_profile() method
  - _generate_all_criteria() method
  - _generate_criterion() method
  - _get_criterion_name() method
  - _generate_evaluative_report() method
  - _generate_declaration() method
  - _generate_annexures() method
  - _get_institution_details() method
  - _generate_pdf() method
  - _save_html() method
  - Helper methods for sections

---

## Section D: Reports

### D1. CO-PO Attainment Report
- [x] Create co_po_attainment folder in university_erp/report
- [x] Create co_po_attainment.json with filters:
  - course (Link: Course)
  - program (Link: Program)
  - academic_year (Link: Academic Year)
- [x] Create co_po_attainment.py with:
  - execute() function
  - get_columns() function
  - get_data() function
  - get_chart() function
- [x] Create co_po_attainment.js with filters

### D2. NAAC Criterion Progress Report
- [x] Create naac_criterion_progress folder in university_erp/report
- [x] Create naac_criterion_progress.json with filters:
  - accreditation_cycle (Link: Accreditation Cycle)
  - criterion (Select)
- [x] Create naac_criterion_progress.py with:
  - execute() function
  - get_columns() function
  - get_data() function
  - get_summary() function
  - get_chart() function
- [x] Create naac_criterion_progress.js with filters

### D3. Program Outcome Attainment Report
- [x] Create program_outcome_attainment folder in university_erp/report
- [x] Create program_outcome_attainment.json with filters:
  - program (Link: Program)
  - academic_year (Link: Academic Year)
- [x] Create program_outcome_attainment.py with:
  - execute() function
  - get_columns() function
  - get_data() function
  - get_chart() function
- [x] Create program_outcome_attainment.js with filters

### D4. NIRF Parameter Report
- [x] Create nirf_parameter_report folder in university_erp/report
- [x] Create nirf_parameter_report.json with filters:
  - ranking_year (Data)
  - category (Select)
- [x] Create nirf_parameter_report.py with:
  - execute() function
  - get_columns() function
  - get_data() function
  - get_chart() function
  - get_summary() function
- [x] Create nirf_parameter_report.js with filters

---

## Section E: Templates & Workspace

### E1. SSR Template
- [x] SSR generation implemented within ssr_generator.py
  - Executive Summary section
  - Institutional Profile section
  - Criteria 1-7 sections
  - Evaluative Report section
  - Declaration section
  - Annexures section

### E2. Accreditation Workspace
- [x] Create accreditation_compliance workspace folder
- [x] Create accreditation_compliance.json with:
  - Shortcuts for Accreditation Cycle, NAAC Metric, NIRF Data
  - Links to existing OBE module (Course Outcome, Program Outcome, CO PO Mapping)
  - Report shortcuts (CO-PO Attainment, NAAC Progress, PO Attainment, NIRF Parameters)

---

## Section F: API Endpoints & Scheduled Tasks

### F1. API Endpoints
- [x] Create api.py in university_erp/accreditation:
  - calculate_co_attainment() API
  - calculate_po_attainment() API
  - get_copo_matrix() API
  - collect_naac_data() API
  - generate_ssr() API
  - get_accreditation_dashboard() API
  - get_criterion_progress() API
  - get_naac_metrics() API
  - get_nirf_data() API
  - update_metric_status() API

### F2. Scheduled Tasks
- [x] Create scheduled_tasks.py in university_erp/accreditation:
  - daily_attainment_update (daily)
  - weekly_naac_data_collection (weekly)
  - monthly_progress_notification (monthly)
  - check_deadline_reminders (daily)

### F3. Hooks Configuration
- [x] Update hooks.py with scheduler_events for Phase 20
  - Added daily: daily_attainment_update, check_deadline_reminders
  - Added weekly: weekly_naac_data_collection
  - Added monthly: monthly_progress_notification

---

## Section G: Testing

### G1. Unit Tests
- [x] Create tests folder in university_erp/accreditation
- [x] Create __init__.py file
- [x] Create test_accreditation_cycle.py with tests for:
  - Accreditation Cycle creation
  - Progress calculation
  - Criterion management
  - NAAC Metric tests
  - NIRF Data tests
- [x] Create test_attainment_calculator.py with tests for:
  - Direct attainment calculation
  - Indirect attainment calculation
  - Overall attainment calculation
  - PO attainment from COs
  - CO-PO matrix generation
- [x] Create test_naac_data_collector.py with tests for:
  - All 7 criteria data collection
  - Student, faculty, research data collection
  - Data validation
- [x] Create test_ssr_generator.py with tests for:
  - SSR generation in HTML/JSON formats
  - Executive summary generation
  - Criteria generation
  - Completeness validation
- [x] Create test_api.py with tests for:
  - All API endpoints
  - Permission checks

---

## Summary

| Section | Total Tasks | Completed | Pending |
|---------|-------------|-----------|---------|
| A. Child Table DocTypes | 44 | 44 | 0 |
| B. Main DocTypes | 20 | 20 | 0 |
| C. Accreditation Engine | 20 | 20 | 0 |
| D. Reports | 16 | 16 | 0 |
| E. Templates & Workspace | 4 | 4 | 0 |
| F. API & Scheduled Tasks | 12 | 12 | 0 |
| G. Testing | 14 | 14 | 0 |
| **Total** | **130** | **130** | **0** |

**Completion: 100%**

---

## Implementation Notes

### Files Created:
1. **Child Tables (7 new + 4 existing in university_obe)**:
   - accreditation_program_link, accreditation_department_link
   - accreditation_team_member, accreditation_criterion
   - naac_metric_year_data, naac_metric_document, naac_document_checklist_item
   - (Existing in university_obe: co_po_mapping, co_pso_mapping, co_assessment_method_link, po_yearly_attainment)

2. **Main DocTypes (3 new + 2 existing in university_obe)**:
   - accreditation_cycle, naac_metric, nirf_data
   - (Existing in university_obe: course_outcome, program_outcome)

3. **Engine Classes (3)**:
   - attainment_calculator.py (COPOAttainmentCalculator) - Integrates with university_obe
   - naac_data_collector.py (NAACDataCollector)
   - ssr_generator.py (SSRGenerator)

4. **Reports (4)**:
   - CO-PO Attainment Report
   - NAAC Criterion Progress Report
   - Program Outcome Attainment Report
   - NIRF Parameter Report

5. **Workspace (1)**:
   - accreditation_compliance (links to both new and existing OBE DocTypes)

6. **API & Tasks (2)**:
   - api.py (10 API endpoints)
   - scheduled_tasks.py (4 scheduled tasks)

7. **Tests (5)**:
   - test_accreditation_cycle.py
   - test_attainment_calculator.py
   - test_naac_data_collector.py
   - test_ssr_generator.py
   - test_api.py

### Integration with Existing Modules:
- **university_obe**: Course Outcome, Program Outcome, CO PO Mapping are used directly
- **university_erp.analytics**: Integrates with KPI system for accreditation metrics
- **education**: Uses Student, Program, Course DocTypes

---

**Created**: 2026-01-15
**Status**: Completed (100%)
**Last Updated**: 2026-01-15
