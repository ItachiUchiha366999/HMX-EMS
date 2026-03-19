# Comprehensive API Audit Results

**Generated:** 2026-03-19 14:17:49
**Site:** university.local
**Test User:** Administrator
**Scope:** All @frappe.whitelist() endpoints in university_erp

## Executive Summary

- **Total Endpoints Discovered:** 488
- **GET Endpoints:** 241 (PASS: 77, FAIL: 3, DENIED: 26, NEEDS_ARGS: 135, IMPORT_FAIL: 0)
- **ACTION Endpoints:** 87 (IMPORTABLE: 87, IMPORT_FAIL: 0)
- **OTHER Endpoints:** 160 (IMPORTABLE: 160, IMPORT_FAIL: 0)
- **Total Import Failures:** 0
- **Modules Scanned:** 155

## Endpoint Details by Module

### Faculty Profile (`university_erp.faculty_management.doctype.faculty_profile.faculty_profile`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_faculty_metrics` | GET | NEEDS_ARGS | get_faculty_metrics() missing 1 required positional argument: 'faculty_profile' |
| 2 | `get_faculty_list` | GET | PASS | list |

### Student Feedback (`university_erp.faculty_management.doctype.student_feedback.student_feedback`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_pending_feedback` | GET | NEEDS_ARGS | get_pending_feedback() missing 2 required positional arguments: 'student' and 'academic_term' |
| 2 | `get_feedback_summary` | GET | NEEDS_ARGS | get_feedback_summary() missing 1 required positional argument: 'instructor' |

### Teaching Assignment (`university_erp.faculty_management.doctype.teaching_assignment.teaching_assignment`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_instructor_schedule` | GET | NEEDS_ARGS | get_instructor_schedule() missing 2 required positional arguments: 'instructor' and 'academic_term' |
| 2 | `check_instructor_availability` | GET | NEEDS_ARGS | check_instructor_availability() missing 5 required positional arguments: 'instructor', 'academic_ter |
| 3 | `check_room_availability` | GET | NEEDS_ARGS | check_room_availability() missing 5 required positional arguments: 'room', 'academic_term', 'day', ' |

### Workload Distributor (`university_erp.faculty_management.doctype.workload_distributor.workload_distributor`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_available_faculty` | GET | NEEDS_ARGS | get_available_faculty() missing 1 required positional argument: 'academic_term' |

### Attendance (`university_erp.university_academics.attendance`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `mark_attendance` | ACTION | IMPORTABLE |  |
| 2 | `get_attendance_percentage` | GET | NEEDS_ARGS | get_attendance_percentage() missing 2 required positional arguments: 'student' and 'course' |
| 3 | `check_exam_eligibility` | GET | NEEDS_ARGS | check_exam_eligibility() missing 3 required positional arguments: 'student', 'course', and 'academic |
| 4 | `get_shortage_students` | GET | NEEDS_ARGS | get_shortage_students() missing 2 required positional arguments: 'course' and 'academic_term' |
| 5 | `get_student_attendance_summary` | GET | NEEDS_ARGS | get_student_attendance_summary() missing 2 required positional arguments: 'student' and 'academic_te |

### Cbcs (`university_erp.university_academics.cbcs`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `validate_course_registration` | OTHER | IMPORTABLE |  |
| 2 | `calculate_credits_from_ltp` | GET | NEEDS_ARGS | calculate_credits_from_ltp() missing 3 required positional arguments: 'lecture_hours', 'tutorial_hou |
| 3 | `get_course_types` | GET | PASS | dict |

### Timetable (`university_erp.university_academics.timetable`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_timetable` | GET | NEEDS_ARGS | get_timetable() missing 3 required positional arguments: 'entity_type', 'entity_name', and 'academic |
| 2 | `create_schedule_entry` | ACTION | IMPORTABLE |  |
| 3 | `check_conflicts` | GET | NEEDS_ARGS | check_conflicts() missing 6 required positional arguments: 'instructor', 'room', 'student_group', 'd |

### Merit List (`university_erp.university_admissions.merit_list`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_merit_list` | OTHER | IMPORTABLE |  |
| 2 | `allot_seats_from_merit_list` | OTHER | IMPORTABLE |  |
| 3 | `generate_all_category_merit_lists` | OTHER | IMPORTABLE |  |

### Student Creation (`university_erp.university_admissions.student_creation`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `create_student_from_applicant` | ACTION | IMPORTABLE |  |
| 2 | `create_students_from_merit_list` | ACTION | IMPORTABLE |  |

### Workflow (`university_erp.university_admissions.workflow`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `activate_admission_workflow` | OTHER | IMPORTABLE |  |
| 2 | `apply_workflow_action` | OTHER | IMPORTABLE |  |

### Api (`university_erp.university_erp.accreditation.api`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `calculate_co_attainment` | GET | NEEDS_ARGS | calculate_co_attainment() missing 1 required positional argument: 'course' |
| 2 | `calculate_po_attainment` | GET | NEEDS_ARGS | calculate_po_attainment() missing 1 required positional argument: 'program' |
| 3 | `get_copo_matrix` | GET | NEEDS_ARGS | get_copo_matrix() missing 2 required positional arguments: 'course' and 'program' |
| 4 | `collect_naac_data` | OTHER | IMPORTABLE |  |
| 5 | `collect_naac_metric` | OTHER | IMPORTABLE |  |
| 6 | `generate_ssr` | OTHER | IMPORTABLE |  |
| 7 | `get_accreditation_progress` | GET | NEEDS_ARGS | get_accreditation_progress() missing 1 required positional argument: 'accreditation_cycle' |
| 8 | `get_nirf_summary` | GET | PASS | list |
| 9 | `collect_nirf_data` | OTHER | IMPORTABLE |  |
| 10 | `get_accreditation_dashboard_data` | GET | PASS | dict |

### Attainment Calculator (`university_erp.university_erp.accreditation.attainment_calculator`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `calculate_course_attainment` | GET | NEEDS_ARGS | calculate_course_attainment() missing 1 required positional argument: 'course' |
| 2 | `calculate_program_attainment` | GET | NEEDS_ARGS | calculate_program_attainment() missing 1 required positional argument: 'program' |
| 3 | `get_copo_matrix` | GET | NEEDS_ARGS | get_copo_matrix() missing 2 required positional arguments: 'course' and 'program' |

### Ssr Generator (`university_erp.university_erp.accreditation.ssr_generator`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_ssr` | OTHER | IMPORTABLE |  |

### Api (`university_erp.university_erp.analytics.api`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_dashboard` | GET | NEEDS_ARGS | get_dashboard() missing 1 required positional argument: 'dashboard_name' |
| 2 | `get_available_dashboards` | GET | PASS | list |
| 3 | `get_kpi_value` | GET | NEEDS_ARGS | get_kpi_value() missing 1 required positional argument: 'kpi_name' |
| 4 | `get_kpi_trend` | GET | NEEDS_ARGS | get_kpi_trend() missing 1 required positional argument: 'kpi_name' |
| 5 | `get_kpi_comparison` | GET | NEEDS_ARGS | get_kpi_comparison() missing 5 required positional arguments: 'kpi_name', 'current_start', 'current_ |
| 6 | `get_quick_stats` | GET | PASS | dict |
| 7 | `execute_custom_report` | OTHER | IMPORTABLE |  |
| 8 | `get_all_kpis` | GET | PASS | list |
| 9 | `calculate_kpi_now` | GET | NEEDS_ARGS | calculate_kpi_now() missing 1 required positional argument: 'kpi_name' |

### Executive Dashboard (`university_erp.university_erp.analytics.dashboards.executive_dashboard`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_executive_dashboard_data` | GET | FAIL | (1054, "Unknown column 'department' in 'SELECT'") |

### Payment (`university_erp.university_erp.api.webhooks.payment`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `razorpay_webhook` (guest) | OTHER | IMPORTABLE |  |
| 2 | `payu_webhook` (guest) | OTHER | IMPORTABLE |  |

### Asset Manager (`university_erp.university_erp.asset_manager`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_asset_details` | GET | NEEDS_ARGS | get_asset_details() missing 1 required positional argument: 'asset_name' |
| 2 | `get_depreciation_schedule` | GET | NEEDS_ARGS | get_depreciation_schedule() missing 1 required positional argument: 'asset_name' |
| 3 | `get_assets_by_location` | GET | NEEDS_ARGS | get_assets_by_location() missing 1 required positional argument: 'location' |
| 4 | `get_assets_by_custodian` | GET | NEEDS_ARGS | get_assets_by_custodian() missing 1 required positional argument: 'custodian' |
| 5 | `create_maintenance_schedule` | ACTION | IMPORTABLE |  |
| 6 | `get_maintenance_history` | GET | NEEDS_ARGS | get_maintenance_history() missing 1 required positional argument: 'asset_name' |

### Batch (`university_erp.university_erp.doctype.batch.batch`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_batches_for_item` | GET | NEEDS_ARGS | get_batches_for_item() missing 1 required positional argument: 'item_code' |
| 2 | `create_batch` | ACTION | IMPORTABLE |  |

### Emergency Alert (`university_erp.university_erp.doctype.emergency_alert.emergency_alert`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `broadcast_alert` | OTHER | IMPORTABLE |  |
| 2 | `resolve_alert` | OTHER | IMPORTABLE |  |
| 3 | `cancel_alert` | ACTION | IMPORTABLE |  |
| 4 | `acknowledge` | OTHER | IMPORTABLE |  |
| 5 | `get_active_alerts` | GET | PASS | list |
| 6 | `get_alert_acknowledgments` | GET | NEEDS_ARGS | get_alert_acknowledgments() missing 1 required positional argument: 'alert_name' |
| 7 | `get_unacknowledged_users` | GET | NEEDS_ARGS | get_unacknowledged_users() missing 1 required positional argument: 'alert_name' |
| 8 | `get_emergency_contacts` (guest) | GET | FAIL | ('DocType', 'Website Settings') |
| 9 | `quick_fire_alert` | OTHER | IMPORTABLE |  |
| 10 | `quick_lockdown` | OTHER | IMPORTABLE |  |
| 11 | `quick_evacuation` | OTHER | IMPORTABLE |  |
| 12 | `send_test_alert` | ACTION | IMPORTABLE |  |
| 13 | `get_emergency_dashboard` | GET | PASS | dict |

### Naac Metric (`university_erp.university_erp.doctype.naac_metric.naac_metric`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `collect_metric_data` | OTHER | IMPORTABLE |  |

### Nirf Data (`university_erp.university_erp.doctype.nirf_data.nirf_data`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `collect_nirf_data` | OTHER | IMPORTABLE |  |

### Notice Board (`university_erp.university_erp.doctype.notice_board.notice_board`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_notices` | GET | PASS | list |
| 2 | `get_notice_detail` | GET | NEEDS_ARGS | get_notice_detail() missing 1 required positional argument: 'notice_name' |
| 3 | `get_notice_types` | GET | PASS | list |

### Notice View Log (`university_erp.university_erp.doctype.notice_view_log.notice_view_log`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `mark_notice_viewed` | ACTION | IMPORTABLE |  |
| 2 | `get_view_stats` | GET | NEEDS_ARGS | get_view_stats() missing 1 required positional argument: 'notice_name' |

### Notification Preference (`university_erp.university_erp.doctype.notification_preference.notification_preference`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_user_preferences` | GET | PASS | dict |
| 2 | `update_preferences` | ACTION | IMPORTABLE |  |

### Suggestion (`university_erp.university_erp.doctype.suggestion.suggestion`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_top_suggestions` | GET | PASS | list |
| 2 | `get_suggestion_stats` | GET | PASS | dict |

### University Laboratory (`university_erp.university_erp.doctype.university_laboratory.university_laboratory`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_lab_equipment` | GET | NEEDS_ARGS | get_lab_equipment() missing 1 required positional argument: 'lab' |
| 2 | `get_lab_schedule` | GET | NEEDS_ARGS | get_lab_schedule() missing 2 required positional arguments: 'lab' and 'date' |

### Emergency Broadcast (`university_erp.university_erp.emergency_broadcast`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `quick_fire_alert` | OTHER | IMPORTABLE |  |
| 2 | `quick_lockdown` | OTHER | IMPORTABLE |  |
| 3 | `quick_evacuation` | OTHER | IMPORTABLE |  |
| 4 | `send_test_alert` | ACTION | IMPORTABLE |  |
| 5 | `get_emergency_dashboard` | GET | PASS | dict |

### Answer Sheet Manager (`university_erp.university_erp.examination.answer_sheet_manager`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_sheet_by_barcode` | GET | NEEDS_ARGS | get_sheet_by_barcode() missing 1 required positional argument: 'barcode' |
| 2 | `update_sheet_location` | ACTION | IMPORTABLE |  |

### Internal Assessment Manager (`university_erp.university_erp.examination.internal_assessment_manager`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_course_assessments` | GET | NEEDS_ARGS | get_course_assessments() missing 2 required positional arguments: 'course' and 'academic_year' |
| 2 | `record_bulk_scores` | OTHER | IMPORTABLE |  |
| 3 | `get_co_attainment_report` | GET | NEEDS_ARGS | get_co_attainment_report() missing 2 required positional arguments: 'course' and 'academic_year' |

### Online Exam Controller (`university_erp.university_erp.examination.online_exam_controller`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `start_examination` | OTHER | IMPORTABLE |  |
| 2 | `save_exam_answer` | ACTION | IMPORTABLE |  |
| 3 | `submit_examination` | ACTION | IMPORTABLE |  |
| 4 | `report_proctoring_event` | OTHER | IMPORTABLE |  |
| 5 | `get_exam_status` | GET | NEEDS_ARGS | get_exam_status() missing 1 required positional argument: 'attempt_id' |

### Practical Exam Manager (`university_erp.university_erp.examination.practical_exam_manager`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_practical_exams` | GET | PASS | list |
| 2 | `assign_exam_examiners` | OTHER | IMPORTABLE |  |
| 3 | `generate_exam_schedule` | OTHER | IMPORTABLE |  |
| 4 | `get_result_summary` | GET | NEEDS_ARGS | get_result_summary() missing 1 required positional argument: 'practical_exam' |

### Question Paper Generator (`university_erp.university_erp.examination.question_paper_generator`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_paper_from_template` | OTHER | IMPORTABLE |  |
| 2 | `generate_multiple_paper_sets` | OTHER | IMPORTABLE |  |

### Feedback Manager (`university_erp.university_erp.feedback.feedback_manager`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_pending_feedback_forms` | GET | PASS | list |
| 2 | `submit_feedback` | ACTION | IMPORTABLE |  |
| 3 | `get_feedback_analysis` | GET | NEEDS_ARGS | get_feedback_analysis() missing 1 required positional argument: 'feedback_form' |
| 4 | `get_form_questions` | GET | NEEDS_ARGS | get_form_questions() missing 1 required positional argument: 'feedback_form' |

### Grievance Manager (`university_erp.university_erp.grievance.grievance_manager`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_grievance` | ACTION | IMPORTABLE |  |
| 2 | `get_grievance_status` | GET | NEEDS_ARGS | get_grievance_status() missing 1 required positional argument: 'grievance_name' |
| 3 | `add_grievance_response` | OTHER | IMPORTABLE |  |
| 4 | `get_grievance_statistics` | GET | PASS | dict |

### Health Check (`university_erp.university_erp.health_check`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `run_checks` | GET | PASS | dict |

### Inventory Manager (`university_erp.university_erp.inventory_manager`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_item_details` | GET | NEEDS_ARGS | get_item_details() missing 1 required positional argument: 'item_code' |
| 2 | `get_stock_balance` | GET | NEEDS_ARGS | get_stock_balance() missing 1 required positional argument: 'item_code' |
| 3 | `get_warehouse_stock` | GET | NEEDS_ARGS | get_warehouse_stock() missing 1 required positional argument: 'warehouse' |
| 4 | `get_supplier_details` | GET | NEEDS_ARGS | get_supplier_details() missing 1 required positional argument: 'supplier' |
| 5 | `get_items_below_reorder` | GET | PASS | list |
| 6 | `get_item_price` | GET | NEEDS_ARGS | get_item_price() missing 1 required positional argument: 'item_code' |

### Notification Api (`university_erp.university_erp.notification_api`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_notifications` | GET | PASS | dict |
| 2 | `mark_as_read` | ACTION | IMPORTABLE |  |
| 3 | `mark_all_as_read` | ACTION | IMPORTABLE |  |
| 4 | `delete_notification` | ACTION | IMPORTABLE |  |
| 5 | `get_unread_count` | GET | PASS | dict |
| 6 | `subscribe_to_push` | OTHER | IMPORTABLE |  |
| 7 | `unsubscribe_from_push` | OTHER | IMPORTABLE |  |
| 8 | `send_test_notification` | ACTION | IMPORTABLE |  |
| 9 | `get_notification_settings` | GET | PASS | dict |
| 10 | `update_notification_settings` | ACTION | IMPORTABLE |  |

### Notification Center (`university_erp.university_erp.notification_center`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_notifications` | GET | PASS | list |
| 2 | `mark_notification_read` | ACTION | IMPORTABLE |  |
| 3 | `mark_all_notifications_read` | ACTION | IMPORTABLE |  |
| 4 | `get_unread_count` | GET | PASS | int |
| 5 | `delete_notification` | ACTION | IMPORTABLE |  |
| 6 | `send_notification_to_user` | ACTION | IMPORTABLE |  |

### Notification Center (`university_erp.university_erp.page.notification_center.notification_center`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_notification_stats` | GET | PASS | dict |
| 2 | `get_notifications_paginated` | GET | PASS | dict |
| 3 | `bulk_mark_read` | OTHER | IMPORTABLE |  |
| 4 | `bulk_delete` | OTHER | IMPORTABLE |  |

### Role Dashboard (`university_erp.university_erp.page.role_dashboard.role_dashboard`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_role_dashboard_data` | GET | PASS | dict |

### University Dashboard (`university_erp.university_erp.page.university_dashboard.university_dashboard`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_dashboard_data` | GET | FAIL | (1054, "Unknown column 'program' in 'SELECT'") |
| 2 | `get_quick_stats` | GET | PASS | dict |

### Unified Communication (`university_erp.university_erp.unified_communication`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `send_notification` | ACTION | IMPORTABLE |  |
| 2 | `send_notification_to_role` | ACTION | IMPORTABLE |  |

### Answer Sheet (`university_erp.university_examinations.doctype.answer_sheet.answer_sheet`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `bulk_create_answer_sheets` | OTHER | IMPORTABLE |  |
| 2 | `assign_sheets_to_evaluator` | OTHER | IMPORTABLE |  |

### External Examiner (`university_erp.university_examinations.doctype.external_examiner.external_examiner`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_available_examiners` | GET | PASS | list |

### Generated Question Paper (`university_erp.university_examinations.doctype.generated_question_paper.generated_question_paper`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `create_paper_from_template` | ACTION | IMPORTABLE |  |

### Internal Assessment (`university_erp.university_examinations.doctype.internal_assessment.internal_assessment`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_student_assessments` | GET | NEEDS_ARGS | get_student_assessments() missing 1 required positional argument: 'student' |

### Practical Examination (`university_erp.university_examinations.doctype.practical_examination.practical_examination`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_student_practical_result` | GET | NEEDS_ARGS | get_student_practical_result() missing 1 required positional argument: 'student' |

### Hall Ticket (`university_erp.university_examinations.hall_ticket`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_hall_ticket` | OTHER | IMPORTABLE |  |
| 2 | `bulk_generate_hall_tickets` | OTHER | IMPORTABLE |  |
| 3 | `generate_hall_tickets_for_group` | OTHER | IMPORTABLE |  |
| 4 | `verify_hall_ticket` | OTHER | IMPORTABLE |  |

### Result Entry (`university_erp.university_examinations.result_entry`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_students_for_result_entry` | GET | NEEDS_ARGS | get_students_for_result_entry() missing 2 required positional arguments: 'course' and 'academic_term |
| 2 | `save_exam_results` | ACTION | IMPORTABLE |  |
| 3 | `apply_result_moderation` | OTHER | IMPORTABLE |  |
| 4 | `submit_course_results` | ACTION | IMPORTABLE |  |
| 5 | `get_result_statistics` | GET | NEEDS_ARGS | get_result_statistics() missing 3 required positional arguments: 'course', 'academic_term', and 'exa |

### Transcript (`university_erp.university_examinations.transcript`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_transcript` | OTHER | IMPORTABLE |  |
| 2 | `get_student_academic_summary` | GET | NEEDS_ARGS | get_student_academic_summary() missing 1 required positional argument: 'student' |
| 3 | `get_semester_results` | GET | NEEDS_ARGS | get_semester_results() missing 1 required positional argument: 'student' |
| 4 | `verify_transcript` | OTHER | IMPORTABLE |  |

### Bulk Fee Generator (`university_erp.university_finance.doctype.bulk_fee_generator.bulk_fee_generator`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_fees` | OTHER | IMPORTABLE |  |

### Hostel Allocation (`university_erp.university_hostel.doctype.hostel_allocation.hostel_allocation`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_available_rooms` | GET | PASS | list |
| 2 | `vacate_room` | OTHER | IMPORTABLE |  |
| 3 | `transfer_room` | OTHER | IMPORTABLE |  |

### Hostel Attendance (`university_erp.university_hostel.doctype.hostel_attendance.hostel_attendance`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `mark_bulk_attendance` | ACTION | IMPORTABLE |  |
| 2 | `get_hostel_residents` | GET | NEEDS_ARGS | get_hostel_residents() missing 1 required positional argument: 'hostel_building' |
| 3 | `get_attendance_summary` | GET | NEEDS_ARGS | get_attendance_summary() missing 3 required positional arguments: 'hostel_building', 'from_date', an |
| 4 | `get_student_attendance_history` | GET | NEEDS_ARGS | get_student_attendance_history() missing 1 required positional argument: 'student' |

### Hostel Building (`university_erp.university_hostel.doctype.hostel_building.hostel_building`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `recalculate_all_building_stats` | OTHER | IMPORTABLE |  |
| 2 | `get_building_stats` | GET | NEEDS_ARGS | get_building_stats() missing 1 required positional argument: 'building' |
| 3 | `get_building_occupancy` | GET | PASS | list |
| 4 | `get_buildings_by_type` | GET | NEEDS_ARGS | get_buildings_by_type() missing 1 required positional argument: 'hostel_type' |
| 5 | `get_buildings_for_gender` | GET | NEEDS_ARGS | get_buildings_for_gender() missing 1 required positional argument: 'gender' |

### Hostel Bulk Attendance (`university_erp.university_hostel.doctype.hostel_bulk_attendance.hostel_bulk_attendance`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_residents_for_attendance` | GET | NEEDS_ARGS | get_residents_for_attendance() missing 1 required positional argument: 'building' |
| 2 | `mark_bulk_attendance` | ACTION | IMPORTABLE |  |
| 3 | `get_attendance_status` | GET | NEEDS_ARGS | get_attendance_status() missing 3 required positional arguments: 'building', 'attendance_date', and  |
| 4 | `get_building_attendance_summary` | GET | NEEDS_ARGS | get_building_attendance_summary() missing 3 required positional arguments: 'building', 'from_date',  |

### Hostel Maintenance Request (`university_erp.university_hostel.doctype.hostel_maintenance_request.hostel_maintenance_request`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_open_requests` | GET | PASS | list |
| 2 | `assign_request` | OTHER | IMPORTABLE |  |
| 3 | `complete_request` | OTHER | IMPORTABLE |  |
| 4 | `get_request_summary` | GET | PASS | dict |
| 5 | `get_pending_requests_for_room` | GET | NEEDS_ARGS | get_pending_requests_for_room() missing 1 required positional argument: 'room' |

### Hostel Mess (`university_erp.university_hostel.doctype.hostel_mess.hostel_mess`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_mess_menu` | GET | NEEDS_ARGS | get_mess_menu() missing 1 required positional argument: 'mess' |
| 2 | `get_today_menu` | GET | NEEDS_ARGS | get_today_menu() missing 1 required positional argument: 'mess' |

### Hostel Room (`university_erp.university_hostel.doctype.hostel_room.hostel_room`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_available_rooms` | GET | PASS | list |
| 2 | `get_room_occupants` | GET | NEEDS_ARGS | get_room_occupants() missing 1 required positional argument: 'room' |
| 3 | `set_maintenance_status` | ACTION | IMPORTABLE |  |

### Hostel Visitor (`university_erp.university_hostel.doctype.hostel_visitor.hostel_visitor`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `check_in_visitor` | GET | NEEDS_ARGS | check_in_visitor() missing 5 required positional arguments: 'visitor_name', 'visitor_mobile', 'stude |
| 2 | `check_out_visitor` | GET | NEEDS_ARGS | check_out_visitor() missing 1 required positional argument: 'visitor_id' |
| 3 | `deny_visitor` | OTHER | IMPORTABLE |  |
| 4 | `get_active_visitors` | GET | PASS | list |
| 5 | `get_visitor_log` | GET | PASS | list |
| 6 | `auto_checkout_visitors` | OTHER | IMPORTABLE |  |

### Mess Menu (`university_erp.university_hostel.doctype.mess_menu.mess_menu`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_today_menu` | GET | PASS | list |
| 2 | `get_week_menu` | GET | NEEDS_ARGS | get_week_menu() missing 1 required positional argument: 'mess' |
| 3 | `publish_menu` | OTHER | IMPORTABLE |  |
| 4 | `archive_menu` | OTHER | IMPORTABLE |  |

### Biometric Integration (`university_erp.university_integrations.biometric_integration`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `sync_attendance` | OTHER | IMPORTABLE |  |
| 2 | `process_attendance_logs` | OTHER | IMPORTABLE |  |
| 3 | `get_device_users` | GET | NEEDS_ARGS | get_device_users() missing 1 required positional argument: 'device_name' |
| 4 | `sync_users_to_device` | OTHER | IMPORTABLE |  |
| 5 | `clear_device_attendance` | OTHER | IMPORTABLE |  |
| 6 | `get_unprocessed_logs_count` | GET | PASS | int |
| 7 | `link_biometric_user` | OTHER | IMPORTABLE |  |

### Certificate Generator (`university_erp.university_integrations.certificate_generator`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_certificate` | OTHER | IMPORTABLE |  |
| 2 | `approve_certificate` | ACTION | IMPORTABLE |  |
| 3 | `verify_certificate` (guest) | OTHER | IMPORTABLE |  |
| 4 | `bulk_generate_certificates` | OTHER | IMPORTABLE |  |
| 5 | `get_certificate_templates` | GET | PASS | list |
| 6 | `preview_certificate` | OTHER | IMPORTABLE |  |

### Digilocker Integration (`university_erp.university_integrations.digilocker_integration`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `issue_certificate_to_digilocker` | OTHER | IMPORTABLE |  |
| 2 | `verify_digilocker_document` | OTHER | IMPORTABLE |  |
| 3 | `pull_digilocker_document` | OTHER | IMPORTABLE |  |
| 4 | `digilocker_callback` (guest) | OTHER | IMPORTABLE |  |
| 5 | `issue_certificate_request_to_digilocker` | OTHER | IMPORTABLE |  |
| 6 | `get_student_digilocker_documents` | GET | NEEDS_ARGS | get_student_digilocker_documents() missing 1 required positional argument: 'student' |
| 7 | `test_digilocker_connection` | OTHER | IMPORTABLE |  |

### Biometric Device (`university_erp.university_integrations.doctype.biometric_device.biometric_device`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `test_device_connection` | OTHER | IMPORTABLE |  |
| 2 | `manual_sync` | OTHER | IMPORTABLE |  |

### Certificate Request (`university_erp.university_integrations.doctype.certificate_request.certificate_request`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_pending_approvals` | GET | PASS | list |
| 2 | `bulk_approve` | OTHER | IMPORTABLE |  |

### Email Queue Extended (`university_erp.university_integrations.doctype.email_queue_extended.email_queue_extended`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `send_priority_email` | ACTION | IMPORTABLE |  |
| 2 | `get_email_queue_status` | GET | PASS | dict |

### Payment Gateway Settings (`university_erp.university_integrations.doctype.payment_gateway_settings.payment_gateway_settings`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `test_gateway_connection` | OTHER | IMPORTABLE |  |

### Payment Transaction (`university_erp.university_integrations.doctype.payment_transaction.payment_transaction`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_transaction_status` | GET | NEEDS_ARGS | get_transaction_status() missing 1 required positional argument: 'transaction_name' |
| 2 | `get_student_transactions` | GET | NEEDS_ARGS | get_student_transactions() missing 1 required positional argument: 'student' |

### Push Notification Settings (`university_erp.university_integrations.doctype.push_notification_settings.push_notification_settings`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `test_push_connection` | OTHER | IMPORTABLE |  |

### Sms Queue (`university_erp.university_integrations.doctype.sms_queue.sms_queue`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `queue_sms` | OTHER | IMPORTABLE |  |
| 2 | `cancel_queued_sms` | ACTION | IMPORTABLE |  |
| 3 | `get_queue_status` | GET | PASS | dict |

### Whatsapp Settings (`university_erp.university_integrations.doctype.whatsapp_settings.whatsapp_settings`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `test_whatsapp_connection` | OTHER | IMPORTABLE |  |

### Firebase Admin (`university_erp.university_integrations.firebase_admin`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `send_push_notification` | ACTION | IMPORTABLE |  |
| 2 | `send_push_to_role` | ACTION | IMPORTABLE |  |
| 3 | `register_device_token` | OTHER | IMPORTABLE |  |
| 4 | `unregister_device_token` | OTHER | IMPORTABLE |  |
| 5 | `subscribe_user_to_topic` | OTHER | IMPORTABLE |  |
| 6 | `unsubscribe_user_from_topic` | OTHER | IMPORTABLE |  |

### Payment Gateway (`university_erp.university_integrations.payment_gateway`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `initiate_payment` | OTHER | IMPORTABLE |  |
| 2 | `verify_payment` | OTHER | IMPORTABLE |  |
| 3 | `process_refund` | OTHER | IMPORTABLE |  |
| 4 | `payment_callback` (guest) | OTHER | IMPORTABLE |  |
| 5 | `razorpay_webhook` (guest) | OTHER | IMPORTABLE |  |
| 6 | `get_payment_status` | GET | NEEDS_ARGS | get_payment_status() missing 1 required positional argument: 'transaction_name' |

### Push Notification (`university_erp.university_integrations.push_notification`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `register_device_token` | OTHER | IMPORTABLE |  |
| 2 | `unregister_device_token` | OTHER | IMPORTABLE |  |
| 3 | `send_push_notification` | ACTION | IMPORTABLE |  |
| 4 | `send_push_to_topic` | ACTION | IMPORTABLE |  |
| 5 | `subscribe_to_topic` | OTHER | IMPORTABLE |  |
| 6 | `unsubscribe_from_topic` | OTHER | IMPORTABLE |  |

### Sms Gateway (`university_erp.university_integrations.sms_gateway`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `send_sms` | ACTION | IMPORTABLE |  |
| 2 | `send_bulk_sms` | ACTION | IMPORTABLE |  |
| 3 | `test_sms_gateway` | OTHER | IMPORTABLE |  |

### Whatsapp Gateway (`university_erp.university_integrations.whatsapp_gateway`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `send_whatsapp_template` | ACTION | IMPORTABLE |  |
| 2 | `send_whatsapp_message` | ACTION | IMPORTABLE |  |
| 3 | `send_whatsapp_media` | ACTION | IMPORTABLE |  |
| 4 | `whatsapp_webhook` (guest) | OTHER | IMPORTABLE |  |
| 5 | `get_whatsapp_templates` | GET | PASS | dict |
| 6 | `sync_whatsapp_templates` | OTHER | IMPORTABLE |  |
| 7 | `create_whatsapp_template_on_provider` | ACTION | IMPORTABLE |  |

### Asset (`university_erp.university_inventory.doctype.asset.asset`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `make_asset_movement` | OTHER | IMPORTABLE |  |
| 2 | `dispose_asset` | OTHER | IMPORTABLE |  |
| 3 | `scrap_asset` | OTHER | IMPORTABLE |  |
| 4 | `get_assets_due_for_depreciation` | GET | PASS | list |
| 5 | `get_assets_due_for_maintenance` | GET | PASS | list |

### Asset Maintenance (`university_erp.university_inventory.doctype.asset_maintenance.asset_maintenance`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `start_maintenance` | OTHER | IMPORTABLE |  |
| 2 | `complete_maintenance` | OTHER | IMPORTABLE |  |
| 3 | `get_pending_maintenance` | GET | PASS | list |

### Inventory Item (`university_erp.university_inventory.doctype.inventory_item.inventory_item`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_item_details` | GET | NEEDS_ARGS | get_item_details() missing 1 required positional argument: 'item_code' |
| 2 | `get_items_below_reorder_level` | GET | PASS | list |
| 3 | `update_item_stock_info` | ACTION | IMPORTABLE |  |

### Inventory Item Group (`university_erp.university_inventory.doctype.inventory_item_group.inventory_item_group`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_children` | GET | NEEDS_ARGS | get_children() missing 1 required positional argument: 'doctype' |
| 2 | `add_node` | OTHER | IMPORTABLE |  |

### Lab Consumable Issue (`university_erp.university_inventory.doctype.lab_consumable_issue.lab_consumable_issue`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_lab_consumable_summary` | GET | NEEDS_ARGS | get_lab_consumable_summary() missing 3 required positional arguments: 'lab', 'from_date', and 'to_da |

### Lab Equipment (`university_erp.university_inventory.doctype.lab_equipment.lab_equipment`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `check_equipment_availability` | GET | NEEDS_ARGS | check_equipment_availability() missing 4 required positional arguments: 'equipment', 'booking_date', |
| 2 | `get_equipment_due_for_calibration` | GET | PASS | list |

### Lab Equipment Booking (`university_erp.university_inventory.doctype.lab_equipment_booking.lab_equipment_booking`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `start_usage` | OTHER | IMPORTABLE |  |
| 2 | `end_usage` | OTHER | IMPORTABLE |  |
| 3 | `get_equipment_bookings` | GET | NEEDS_ARGS | get_equipment_bookings() missing 3 required positional arguments: 'equipment', 'from_date', and 'to_ |

### Material Request (`university_erp.university_inventory.doctype.material_request.material_request`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `make_purchase_order` | OTHER | IMPORTABLE |  |
| 2 | `make_stock_entry` | OTHER | IMPORTABLE |  |

### Purchase Order (`university_erp.university_inventory.doctype.purchase_order.purchase_order`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `make_stock_entry` | OTHER | IMPORTABLE |  |
| 2 | `close_or_unclose_purchase_order` | OTHER | IMPORTABLE |  |

### Purchase Receipt (`university_erp.university_inventory.doctype.purchase_receipt.purchase_receipt`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `make_purchase_receipt` | OTHER | IMPORTABLE |  |
| 2 | `make_purchase_return` | OTHER | IMPORTABLE |  |

### Stock Entry (`university_erp.university_inventory.doctype.stock_entry.stock_entry`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_items_from_purchase_order` | GET | NEEDS_ARGS | get_items_from_purchase_order() missing 1 required positional argument: 'purchase_order' |
| 2 | `get_items_from_material_request` | GET | NEEDS_ARGS | get_items_from_material_request() missing 1 required positional argument: 'material_request' |
| 3 | `make_stock_entry` | OTHER | IMPORTABLE |  |

### Stock Ledger Entry (`university_erp.university_inventory.doctype.stock_ledger_entry.stock_ledger_entry`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_item_stock_by_warehouse` | GET | NEEDS_ARGS | get_item_stock_by_warehouse() missing 1 required positional argument: 'item_code' |

### Stock Reconciliation (`university_erp.university_inventory.doctype.stock_reconciliation.stock_reconciliation`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_items_for_reconciliation` | GET | PASS | list |

### Supplier (`university_erp.university_inventory.doctype.supplier.supplier`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_supplier_details` | GET | NEEDS_ARGS | get_supplier_details() missing 1 required positional argument: 'supplier' |

### Supplier Group (`university_erp.university_inventory.doctype.supplier_group.supplier_group`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_children` | GET | NEEDS_ARGS | get_children() missing 1 required positional argument: 'doctype' |

### Warehouse (`university_erp.university_inventory.doctype.warehouse.warehouse`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_children` | GET | NEEDS_ARGS | get_children() missing 1 required positional argument: 'doctype' |
| 2 | `add_node` | OTHER | IMPORTABLE |  |
| 3 | `get_warehouse_stock` | GET | NEEDS_ARGS | get_warehouse_stock() missing 1 required positional argument: 'warehouse' |

### Book Reservation (`university_erp.university_library.doctype.book_reservation.book_reservation`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `reserve_book` | OTHER | IMPORTABLE |  |
| 2 | `cancel_reservation` | ACTION | IMPORTABLE |  |
| 3 | `notify_available_reservations` | OTHER | IMPORTABLE |  |

### Library Article (`university_erp.university_library.doctype.library_article.library_article`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `search_catalog` | GET | NEEDS_ARGS | search_catalog() missing 1 required positional argument: 'query' |
| 2 | `get_article_availability` | GET | NEEDS_ARGS | get_article_availability() missing 1 required positional argument: 'article' |

### Library Fine (`university_erp.university_library.doctype.library_fine.library_fine`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `pay_fine` | OTHER | IMPORTABLE |  |
| 2 | `waive_fine` | OTHER | IMPORTABLE |  |

### Library Member (`university_erp.university_library.doctype.library_member.library_member`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_member_status` | GET | NEEDS_ARGS | get_member_status() missing 1 required positional argument: 'member' |
| 2 | `create_member_from_student` | ACTION | IMPORTABLE |  |

### Library Transaction (`university_erp.university_library.doctype.library_transaction.library_transaction`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `issue_book` | OTHER | IMPORTABLE |  |
| 2 | `return_book` | OTHER | IMPORTABLE |  |

### Assignment Submission (`university_erp.university_lms.doctype.assignment_submission.assignment_submission`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_assignment` | ACTION | IMPORTABLE |  |
| 2 | `grade_submission` | OTHER | IMPORTABLE |  |

### Lms Assignment (`university_erp.university_lms.doctype.lms_assignment.lms_assignment`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_student_assignments` | GET | PASS | list |

### Lms Content (`university_erp.university_lms.doctype.lms_content.lms_content`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_course_content` | GET | NEEDS_ARGS | get_course_content() missing 1 required positional argument: 'lms_course' |

### Lms Content Progress (`university_erp.university_lms.doctype.lms_content_progress.lms_content_progress`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `track_content_progress` | OTHER | IMPORTABLE |  |
| 2 | `get_course_progress` | GET | NEEDS_ARGS | get_course_progress() missing 2 required positional arguments: 'lms_course' and 'student' |
| 3 | `mark_content_complete` | ACTION | IMPORTABLE |  |

### Lms Course (`university_erp.university_lms.doctype.lms_course.lms_course`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_available_courses` | GET | PASS | list |
| 2 | `enroll_student` | OTHER | IMPORTABLE |  |

### Lms Discussion (`university_erp.university_lms.doctype.lms_discussion.lms_discussion`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_course_discussions` | GET | NEEDS_ARGS | get_course_discussions() missing 1 required positional argument: 'lms_course' |
| 2 | `add_discussion_reply` | OTHER | IMPORTABLE |  |
| 3 | `increment_view_count` | OTHER | IMPORTABLE |  |

### Lms Quiz (`university_erp.university_lms.doctype.lms_quiz.lms_quiz`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_available_quizzes` | GET | PASS | list |
| 2 | `start_quiz` | OTHER | IMPORTABLE |  |
| 3 | `submit_quiz` | ACTION | IMPORTABLE |  |
| 4 | `get_quiz_results` | GET | NEEDS_ARGS | get_quiz_results() missing 1 required positional argument: 'attempt_name' |

### Accreditation Cycle (`university_erp.university_obe.doctype.accreditation_cycle.accreditation_cycle`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_accreditation_progress` | GET | NEEDS_ARGS | get_accreditation_progress() missing 1 required positional argument: 'accreditation_cycle' |

### Assessment Rubric (`university_erp.university_obe.doctype.assessment_rubric.assessment_rubric`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_rubric_level` | GET | NEEDS_ARGS | get_rubric_level() missing 2 required positional arguments: 'rubric_name' and 'percentage' |

### Co Attainment (`university_erp.university_obe.doctype.co_attainment.co_attainment`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `calculate_co_attainment` | GET | NEEDS_ARGS | calculate_co_attainment() missing 2 required positional arguments: 'course' and 'academic_term' |
| 2 | `get_co_attainment_summary` | GET | PASS | list |
| 3 | `populate_cos_for_attainment` | OTHER | IMPORTABLE |  |

### Co Po Mapping (`university_erp.university_obe.doctype.co_po_mapping.co_po_mapping`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `generate_mapping_matrix` | OTHER | IMPORTABLE |  |
| 2 | `get_co_po_matrix` | GET | PASS | dict |
| 3 | `get_po_coverage` | GET | NEEDS_ARGS | get_po_coverage() missing 1 required positional argument: 'program' |

### Course Outcome (`university_erp.university_obe.doctype.course_outcome.course_outcome`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_course_outcomes` | GET | NEEDS_ARGS | get_course_outcomes() missing 1 required positional argument: 'course' |
| 2 | `get_bloom_taxonomy` | GET | PASS | dict |
| 3 | `get_co_statistics` | GET | NEEDS_ARGS | get_co_statistics() missing 1 required positional argument: 'course' |

### Obe Survey (`university_erp.university_obe.doctype.obe_survey.obe_survey`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_survey_form` (guest) | GET | NEEDS_ARGS | get_survey_form() missing 2 required positional arguments: 'survey_type' and 'program' |
| 2 | `submit_survey` (guest) | ACTION | IMPORTABLE |  |
| 3 | `get_survey_statistics` | GET | PASS | dict |

### Po Attainment (`university_erp.university_obe.doctype.po_attainment.po_attainment`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `calculate_po_attainment` | GET | NEEDS_ARGS | calculate_po_attainment() missing 2 required positional arguments: 'program' and 'academic_year' |
| 2 | `get_po_attainment_summary` | GET | PASS | list |
| 3 | `generate_attainment_report` | OTHER | IMPORTABLE |  |

### Program Educational Objective (`university_erp.university_obe.doctype.program_educational_objective.program_educational_objective`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_program_peos` | GET | NEEDS_ARGS | get_program_peos() missing 1 required positional argument: 'program' |

### Program Outcome (`university_erp.university_obe.doctype.program_outcome.program_outcome`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_program_outcomes` | GET | NEEDS_ARGS | get_program_outcomes() missing 1 required positional argument: 'program' |
| 2 | `get_nba_graduate_attributes` | GET | PASS | list |

### Survey Template (`university_erp.university_obe.doctype.survey_template.survey_template`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_survey_templates` | GET | PASS | list |

### Co Po Mapping Matrix (`university_erp.university_obe.report.co_po_mapping_matrix.co_po_mapping_matrix`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_program_courses` | GET | NEEDS_ARGS | get_program_courses() missing 6 required positional arguments: 'doctype', 'txt', 'searchfield', 'sta |

### Bank Reconciliation (`university_erp.university_payments.bank_reconciliation`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_reconciliation_data` | GET | NEEDS_ARGS | get_reconciliation_data() missing 3 required positional arguments: 'bank_account', 'from_date', and  |
| 2 | `perform_reconciliation` | OTHER | IMPORTABLE |  |
| 3 | `import_bank_statement` | OTHER | IMPORTABLE |  |
| 4 | `get_supported_banks` | GET | PASS | list |
| 5 | `manual_reconcile` | OTHER | IMPORTABLE |  |
| 6 | `unreconcile_transaction` | OTHER | IMPORTABLE |  |
| 7 | `auto_reconcile` | OTHER | IMPORTABLE |  |
| 8 | `import_statement_data` | OTHER | IMPORTABLE |  |

### Fee Refund (`university_erp.university_payments.doctype.fee_refund.fee_refund`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_for_approval` | ACTION | IMPORTABLE |  |
| 2 | `approve_refund` | ACTION | IMPORTABLE |  |
| 3 | `reject_refund` | ACTION | IMPORTABLE |  |
| 4 | `get_refund_summary` | GET | PASS | _dict |

### Payment Order (`university_erp.university_payments.doctype.payment_order.payment_order`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_payment_order_status` | GET | NEEDS_ARGS | get_payment_order_status() missing 1 required positional argument: 'payment_order_name' |
| 2 | `cancel_payment_order` | ACTION | IMPORTABLE |  |

### Payment Gateway (`university_erp.university_payments.payment_gateway`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `create_fee_payment_order` | ACTION | IMPORTABLE |  |
| 2 | `verify_and_process_payment` | OTHER | IMPORTABLE |  |
| 3 | `get_payment_status` | GET | NEEDS_ARGS | get_payment_status() missing 1 required positional argument: 'payment_order_name' |
| 4 | `retry_payment` | OTHER | IMPORTABLE |  |
| 5 | `download_receipt` | OTHER | IMPORTABLE |  |

### Payu Callback (`university_erp.university_payments.webhooks.payu_callback`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `payu_success` (guest) | OTHER | IMPORTABLE |  |
| 2 | `payu_failure` (guest) | OTHER | IMPORTABLE |  |
| 3 | `payu_cancel` (guest) | OTHER | IMPORTABLE |  |

### Razorpay Webhook (`university_erp.university_payments.webhooks.razorpay_webhook`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `handle_razorpay_webhook` (guest) | OTHER | IMPORTABLE |  |

### Placement Application (`university_erp.university_placement.doctype.placement_application.placement_application`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `apply_for_job` | OTHER | IMPORTABLE |  |
| 2 | `update_application_status` | ACTION | IMPORTABLE |  |

### Placement Company (`university_erp.university_placement.doctype.placement_company.placement_company`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_company_placements` | GET | NEEDS_ARGS | get_company_placements() missing 1 required positional argument: 'company' |

### Placement Drive (`university_erp.university_placement.doctype.placement_drive.placement_drive`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `register_for_drive` | OTHER | IMPORTABLE |  |
| 2 | `get_drive_applicants` | GET | NEEDS_ARGS | get_drive_applicants() missing 1 required positional argument: 'drive' |
| 3 | `update_round_status` | ACTION | IMPORTABLE |  |
| 4 | `bulk_update_applicant_status` | OTHER | IMPORTABLE |  |

### Placement Job Opening (`university_erp.university_placement.doctype.placement_job_opening.placement_job_opening`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `check_student_eligibility` | GET | NEEDS_ARGS | check_student_eligibility() missing 2 required positional arguments: 'job_opening' and 'student' |
| 2 | `get_eligible_students` | GET | NEEDS_ARGS | get_eligible_students() missing 1 required positional argument: 'job_opening' |

### Student Resume (`university_erp.university_placement.doctype.student_resume.student_resume`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_for_verification` | ACTION | IMPORTABLE |  |
| 2 | `verify_resume` | OTHER | IMPORTABLE |  |
| 3 | `get_resume_for_student` | GET | NEEDS_ARGS | get_resume_for_student() missing 1 required positional argument: 'student' |
| 4 | `search_resumes` | GET | PASS | list |
| 5 | `generate_resume_pdf` | OTHER | IMPORTABLE |  |

### Faculty Api (`university_erp.university_portals.api.faculty_api`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_faculty_dashboard` | GET | DENIED | PermissionError even as Administrator |
| 2 | `get_today_classes` | GET | DENIED | PermissionError even as Administrator |
| 3 | `get_weekly_timetable` | GET | DENIED | PermissionError even as Administrator |
| 4 | `get_students_for_attendance` | GET | NEEDS_ARGS | get_students_for_attendance() missing 1 required positional argument: 'course_schedule' |
| 5 | `submit_attendance` | ACTION | IMPORTABLE |  |
| 6 | `get_announcements` | GET | DENIED | PermissionError even as Administrator |
| 7 | `get_students_for_grading` | GET | NEEDS_ARGS | get_students_for_grading() missing 2 required positional arguments: 'course' and 'assessment_plan' |
| 8 | `save_draft_grade` | ACTION | IMPORTABLE |  |
| 9 | `submit_grades` | ACTION | IMPORTABLE |  |
| 10 | `get_grade_analytics` | GET | NEEDS_ARGS | get_grade_analytics() missing 2 required positional arguments: 'course' and 'assessment_plan' |
| 11 | `get_student_list` | GET | DENIED | PermissionError even as Administrator |
| 12 | `get_student_detail` | GET | NEEDS_ARGS | get_student_detail() missing 2 required positional arguments: 'student' and 'course' |
| 13 | `get_performance_analytics` | GET | NEEDS_ARGS | get_performance_analytics() missing 1 required positional argument: 'course' |
| 14 | `get_leave_balance` | GET | DENIED | PermissionError even as Administrator |
| 15 | `apply_leave` | OTHER | IMPORTABLE |  |
| 16 | `get_leave_history` | GET | DENIED | PermissionError even as Administrator |
| 17 | `get_student_leave_requests` | GET | DENIED | PermissionError even as Administrator |
| 18 | `approve_student_leave` | ACTION | IMPORTABLE |  |
| 19 | `reject_student_leave` | ACTION | IMPORTABLE |  |
| 20 | `get_lms_courses` | GET | DENIED | PermissionError even as Administrator |
| 21 | `get_lms_course_content` | GET | NEEDS_ARGS | get_lms_course_content() missing 1 required positional argument: 'course' |
| 22 | `save_lms_content` | ACTION | IMPORTABLE |  |
| 23 | `delete_lms_content` | ACTION | IMPORTABLE |  |
| 24 | `get_publications` | GET | DENIED | PermissionError even as Administrator |
| 25 | `get_copo_matrix` | GET | NEEDS_ARGS | get_copo_matrix() missing 1 required positional argument: 'course' |
| 26 | `get_copo_student_detail` | GET | NEEDS_ARGS | get_copo_student_detail() missing 2 required positional arguments: 'course' and 'co' |
| 27 | `get_workload_summary` | GET | DENIED | PermissionError even as Administrator |

### Portal Api (`university_erp.university_portals.api.portal_api`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_student_dashboard` | GET | DENIED | PermissionError even as Administrator |
| 2 | `get_student_timetable` | GET | DENIED | PermissionError even as Administrator |
| 3 | `get_student_results` | GET | DENIED | PermissionError even as Administrator |
| 4 | `get_student_attendance_details` | GET | DENIED | PermissionError even as Administrator |
| 5 | `request_certificate` | OTHER | IMPORTABLE |  |
| 6 | `submit_grievance` | ACTION | IMPORTABLE |  |
| 7 | `update_student_profile` | ACTION | IMPORTABLE |  |
| 8 | `create_payment_request` | ACTION | IMPORTABLE |  |
| 9 | `get_logged_student` | GET | DENIED | PermissionError even as Administrator |
| 10 | `get_student_academics` | GET | DENIED | PermissionError even as Administrator |
| 11 | `get_student_fees` | GET | DENIED | PermissionError even as Administrator |
| 12 | `get_student_library` | GET | DENIED | PermissionError even as Administrator |
| 13 | `get_student_notifications` | GET | DENIED | PermissionError even as Administrator |
| 14 | `get_student_profile` | GET | DENIED | PermissionError even as Administrator |
| 15 | `get_student_grievances` | GET | DENIED | PermissionError even as Administrator |
| 16 | `get_student_certificates` | GET | DENIED | PermissionError even as Administrator |
| 17 | `get_student_hostel` | GET | DENIED | PermissionError even as Administrator |
| 18 | `submit_maintenance_request` | ACTION | IMPORTABLE |  |
| 19 | `get_student_transport` | GET | DENIED | PermissionError even as Administrator |
| 20 | `get_faculty_dashboard` | GET | PASS_NO_DATA | No module named 'university_erp.university_portals.www.faculty_portal' |
| 21 | `mark_attendance` | ACTION | IMPORTABLE |  |
| 22 | `submit_assessment_results` | ACTION | IMPORTABLE |  |
| 23 | `approve_leave_request` | ACTION | IMPORTABLE |  |
| 24 | `get_parent_dashboard` | GET | DENIED | PermissionError even as Administrator |
| 25 | `get_child_details` | GET | NEEDS_ARGS | get_child_details() missing 1 required positional argument: 'student' |
| 26 | `send_message_to_faculty` | ACTION | IMPORTABLE |  |
| 27 | `get_portal_redirect` (guest) | GET | PASS | dict |
| 28 | `get_session_info` | GET | PASS | dict |

### Attendance (`university_erp.university_portals.www.faculty-portal.attendance`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `mark_attendance` | ACTION | IMPORTABLE |  |
| 2 | `get_student_group_students` | GET | NEEDS_ARGS | get_student_group_students() missing 1 required positional argument: 'student_group' |
| 3 | `get_pending_attendance` | GET | PASS_NO_DATA | No module named 'university_erp.university_portals.www.faculty_portal' |

### Classes (`university_erp.university_portals.www.faculty-portal.classes`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_class_schedule` | GET | PASS_NO_DATA | No module named 'university_erp.university_portals.www.faculty_portal' |

### Grades (`university_erp.university_portals.www.faculty-portal.grades`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_assessment_results` | ACTION | IMPORTABLE |  |

### Certificates (`university_erp.university_portals.www.student-portal.certificates`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `request_certificate` | OTHER | IMPORTABLE |  |

### Fees (`university_erp.university_portals.www.student-portal.fees`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `initiate_fee_payment` | OTHER | IMPORTABLE |  |

### Grievances (`university_erp.university_portals.www.student-portal.grievances`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_grievance` | ACTION | IMPORTABLE |  |
| 2 | `add_grievance_comment` | OTHER | IMPORTABLE |  |

### Profile (`university_erp.university_portals.www.student-portal.profile`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `update_student_profile` | ACTION | IMPORTABLE |  |
| 2 | `update_profile_image` | ACTION | IMPORTABLE |  |

### Research Grant (`university_erp.university_research.doctype.research_grant.research_grant`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_grant_summary` | GET | PASS | dict |

### Research Project (`university_erp.university_research.doctype.research_project.research_project`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_active_projects` | GET | PASS | list |

### Research Publication (`university_erp.university_research.doctype.research_publication.research_publication`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_faculty_publications` | GET | PASS | list |

### Lifecycle (`university_erp.university_student_info.lifecycle`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `transition_student_status` | OTHER | IMPORTABLE |  |
| 2 | `get_student_status_history` | GET | NEEDS_ARGS | get_student_status_history() missing 1 required positional argument: 'student_name' |
| 3 | `get_allowed_status_transitions` | GET | NEEDS_ARGS | get_allowed_status_transitions() missing 1 required positional argument: 'student_name' |

### Transport Allocation (`university_erp.university_transport.doctype.transport_allocation.transport_allocation`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_route_students` | GET | NEEDS_ARGS | get_route_students() missing 1 required positional argument: 'route' |
| 2 | `get_route_capacity` | GET | NEEDS_ARGS | get_route_capacity() missing 1 required positional argument: 'route' |

### Transport Route (`university_erp.university_transport.doctype.transport_route.transport_route`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_route_stops` | GET | NEEDS_ARGS | get_route_stops() missing 1 required positional argument: 'route' |
| 2 | `get_active_routes` | GET | PASS | list |
| 3 | `get_route_schedule` | GET | NEEDS_ARGS | get_route_schedule() missing 1 required positional argument: 'route' |

### Transport Trip Log (`university_erp.university_transport.doctype.transport_trip_log.transport_trip_log`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `start_trip` | OTHER | IMPORTABLE |  |
| 2 | `complete_trip` | OTHER | IMPORTABLE |  |
| 3 | `get_daily_trips` | GET | PASS | list |

### Transport Vehicle (`university_erp.university_transport.doctype.transport_vehicle.transport_vehicle`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_available_vehicles` | GET | PASS | list |
| 2 | `get_vehicles_needing_attention` | GET | PASS | list |

### Classes (`university_erp.www.faculty-portal.classes`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_class_schedule` | GET | PASS_NO_DATA | No module named 'university_erp.university_portals.www.faculty_portal' |

### Grades (`university_erp.www.faculty-portal.grades`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_assessment_results` | ACTION | IMPORTABLE |  |

### Index (`university_erp.www.student-portal.feedback.index`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_feedback_form_questions` | GET | NEEDS_ARGS | get_feedback_form_questions() missing 1 required positional argument: 'form_name' |
| 2 | `submit_feedback` | ACTION | IMPORTABLE |  |

### Index (`university_erp.www.student-portal.grievances.index`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_grievance` | ACTION | IMPORTABLE |  |
| 2 | `get_grievance_details` | GET | NEEDS_ARGS | get_grievance_details() missing 1 required positional argument: 'grievance_id' |
| 3 | `add_grievance_response` | OTHER | IMPORTABLE |  |

### Certificates (`university_erp.www.student_portal.certificates`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `request_certificate` | OTHER | IMPORTABLE |  |

### Exams (`university_erp.www.student_portal.exams`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `download_hall_ticket` | OTHER | IMPORTABLE |  |

### Fees (`university_erp.www.student_portal.fees`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `initiate_fee_payment` | OTHER | IMPORTABLE |  |

### Grievances (`university_erp.www.student_portal.grievances`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `submit_grievance` | ACTION | IMPORTABLE |  |
| 2 | `add_grievance_comment` | OTHER | IMPORTABLE |  |

### Profile (`university_erp.www.student_portal.profile`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `update_student_profile` | ACTION | IMPORTABLE |  |
| 2 | `update_profile_image` | ACTION | IMPORTABLE |  |

### Index (`university_erp.www_old.library.index`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `search_books` (guest) | GET | NEEDS_ARGS | search_books() missing 1 required positional argument: 'query' |
| 2 | `reserve_book` | OTHER | IMPORTABLE |  |

### Index (`university_erp.www_old.placement.index`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `apply_for_job` | OTHER | IMPORTABLE |  |
| 2 | `withdraw_application` | OTHER | IMPORTABLE |  |
| 3 | `register_for_drive` | OTHER | IMPORTABLE |  |

### Index (`university_erp.www_old.student-portal.index`)

| # | Endpoint | Type | Status | Response/Error |
|---|----------|------|--------|----------------|
| 1 | `get_student_dashboard_data` | GET | PASS_NO_DATA | No student record found |

## Endpoints Needing Specific Arguments

These GET endpoints require arguments that cannot be auto-guessed.

| Module | Endpoint | Error |
|--------|----------|-------|
| `university_erp.faculty_management.doctype.faculty_profile.faculty_profile` | `get_faculty_metrics` | get_faculty_metrics() missing 1 required positional argument: 'faculty_profile' |
| `university_erp.faculty_management.doctype.student_feedback.student_feedback` | `get_pending_feedback` | get_pending_feedback() missing 2 required positional arguments: 'student' and 'academic_term' |
| `university_erp.faculty_management.doctype.student_feedback.student_feedback` | `get_feedback_summary` | get_feedback_summary() missing 1 required positional argument: 'instructor' |
| `university_erp.faculty_management.doctype.teaching_assignment.teaching_assignment` | `get_instructor_schedule` | get_instructor_schedule() missing 2 required positional arguments: 'instructor' and 'academic_term' |
| `university_erp.faculty_management.doctype.teaching_assignment.teaching_assignment` | `check_instructor_availability` | check_instructor_availability() missing 5 required positional arguments: 'instructor', 'academic_term', 'day', 'start_ti |
| `university_erp.faculty_management.doctype.teaching_assignment.teaching_assignment` | `check_room_availability` | check_room_availability() missing 5 required positional arguments: 'room', 'academic_term', 'day', 'start_time', and 'en |
| `university_erp.faculty_management.doctype.workload_distributor.workload_distributor` | `get_available_faculty` | get_available_faculty() missing 1 required positional argument: 'academic_term' |
| `university_erp.university_academics.attendance` | `get_attendance_percentage` | get_attendance_percentage() missing 2 required positional arguments: 'student' and 'course' |
| `university_erp.university_academics.attendance` | `check_exam_eligibility` | check_exam_eligibility() missing 3 required positional arguments: 'student', 'course', and 'academic_term' |
| `university_erp.university_academics.attendance` | `get_shortage_students` | get_shortage_students() missing 2 required positional arguments: 'course' and 'academic_term' |
| `university_erp.university_academics.attendance` | `get_student_attendance_summary` | get_student_attendance_summary() missing 2 required positional arguments: 'student' and 'academic_term' |
| `university_erp.university_academics.cbcs` | `calculate_credits_from_ltp` | calculate_credits_from_ltp() missing 3 required positional arguments: 'lecture_hours', 'tutorial_hours', and 'practical_ |
| `university_erp.university_academics.timetable` | `get_timetable` | get_timetable() missing 3 required positional arguments: 'entity_type', 'entity_name', and 'academic_term' |
| `university_erp.university_academics.timetable` | `check_conflicts` | check_conflicts() missing 6 required positional arguments: 'instructor', 'room', 'student_group', 'day', 'slot', and 'ac |
| `university_erp.university_erp.asset_manager` | `get_asset_details` | get_asset_details() missing 1 required positional argument: 'asset_name' |
| `university_erp.university_erp.asset_manager` | `get_depreciation_schedule` | get_depreciation_schedule() missing 1 required positional argument: 'asset_name' |
| `university_erp.university_erp.asset_manager` | `get_assets_by_location` | get_assets_by_location() missing 1 required positional argument: 'location' |
| `university_erp.university_erp.asset_manager` | `get_assets_by_custodian` | get_assets_by_custodian() missing 1 required positional argument: 'custodian' |
| `university_erp.university_erp.asset_manager` | `get_maintenance_history` | get_maintenance_history() missing 1 required positional argument: 'asset_name' |
| `university_erp.university_erp.inventory_manager` | `get_item_details` | get_item_details() missing 1 required positional argument: 'item_code' |
| `university_erp.university_erp.inventory_manager` | `get_stock_balance` | get_stock_balance() missing 1 required positional argument: 'item_code' |
| `university_erp.university_erp.inventory_manager` | `get_warehouse_stock` | get_warehouse_stock() missing 1 required positional argument: 'warehouse' |
| `university_erp.university_erp.inventory_manager` | `get_supplier_details` | get_supplier_details() missing 1 required positional argument: 'supplier' |
| `university_erp.university_erp.inventory_manager` | `get_item_price` | get_item_price() missing 1 required positional argument: 'item_code' |
| `university_erp.university_erp.accreditation.api` | `calculate_co_attainment` | calculate_co_attainment() missing 1 required positional argument: 'course' |
| `university_erp.university_erp.accreditation.api` | `calculate_po_attainment` | calculate_po_attainment() missing 1 required positional argument: 'program' |
| `university_erp.university_erp.accreditation.api` | `get_copo_matrix` | get_copo_matrix() missing 2 required positional arguments: 'course' and 'program' |
| `university_erp.university_erp.accreditation.api` | `get_accreditation_progress` | get_accreditation_progress() missing 1 required positional argument: 'accreditation_cycle' |
| `university_erp.university_erp.accreditation.attainment_calculator` | `calculate_course_attainment` | calculate_course_attainment() missing 1 required positional argument: 'course' |
| `university_erp.university_erp.accreditation.attainment_calculator` | `calculate_program_attainment` | calculate_program_attainment() missing 1 required positional argument: 'program' |
| `university_erp.university_erp.accreditation.attainment_calculator` | `get_copo_matrix` | get_copo_matrix() missing 2 required positional arguments: 'course' and 'program' |
| `university_erp.university_erp.analytics.api` | `get_dashboard` | get_dashboard() missing 1 required positional argument: 'dashboard_name' |
| `university_erp.university_erp.analytics.api` | `get_kpi_value` | get_kpi_value() missing 1 required positional argument: 'kpi_name' |
| `university_erp.university_erp.analytics.api` | `get_kpi_trend` | get_kpi_trend() missing 1 required positional argument: 'kpi_name' |
| `university_erp.university_erp.analytics.api` | `get_kpi_comparison` | get_kpi_comparison() missing 5 required positional arguments: 'kpi_name', 'current_start', 'current_end', 'previous_star |
| `university_erp.university_erp.analytics.api` | `calculate_kpi_now` | calculate_kpi_now() missing 1 required positional argument: 'kpi_name' |
| `university_erp.university_erp.doctype.batch.batch` | `get_batches_for_item` | get_batches_for_item() missing 1 required positional argument: 'item_code' |
| `university_erp.university_erp.doctype.emergency_alert.emergency_alert` | `get_alert_acknowledgments` | get_alert_acknowledgments() missing 1 required positional argument: 'alert_name' |
| `university_erp.university_erp.doctype.emergency_alert.emergency_alert` | `get_unacknowledged_users` | get_unacknowledged_users() missing 1 required positional argument: 'alert_name' |
| `university_erp.university_erp.doctype.notice_board.notice_board` | `get_notice_detail` | get_notice_detail() missing 1 required positional argument: 'notice_name' |
| `university_erp.university_erp.doctype.notice_view_log.notice_view_log` | `get_view_stats` | get_view_stats() missing 1 required positional argument: 'notice_name' |
| `university_erp.university_erp.doctype.university_laboratory.university_laboratory` | `get_lab_equipment` | get_lab_equipment() missing 1 required positional argument: 'lab' |
| `university_erp.university_erp.doctype.university_laboratory.university_laboratory` | `get_lab_schedule` | get_lab_schedule() missing 2 required positional arguments: 'lab' and 'date' |
| `university_erp.university_erp.examination.answer_sheet_manager` | `get_sheet_by_barcode` | get_sheet_by_barcode() missing 1 required positional argument: 'barcode' |
| `university_erp.university_erp.examination.internal_assessment_manager` | `get_course_assessments` | get_course_assessments() missing 2 required positional arguments: 'course' and 'academic_year' |
| `university_erp.university_erp.examination.internal_assessment_manager` | `get_co_attainment_report` | get_co_attainment_report() missing 2 required positional arguments: 'course' and 'academic_year' |
| `university_erp.university_erp.examination.online_exam_controller` | `get_exam_status` | get_exam_status() missing 1 required positional argument: 'attempt_id' |
| `university_erp.university_erp.examination.practical_exam_manager` | `get_result_summary` | get_result_summary() missing 1 required positional argument: 'practical_exam' |
| `university_erp.university_erp.feedback.feedback_manager` | `get_feedback_analysis` | get_feedback_analysis() missing 1 required positional argument: 'feedback_form' |
| `university_erp.university_erp.feedback.feedback_manager` | `get_form_questions` | get_form_questions() missing 1 required positional argument: 'feedback_form' |
| `university_erp.university_erp.grievance.grievance_manager` | `get_grievance_status` | get_grievance_status() missing 1 required positional argument: 'grievance_name' |
| `university_erp.university_examinations.result_entry` | `get_students_for_result_entry` | get_students_for_result_entry() missing 2 required positional arguments: 'course' and 'academic_term' |
| `university_erp.university_examinations.result_entry` | `get_result_statistics` | get_result_statistics() missing 3 required positional arguments: 'course', 'academic_term', and 'exam_type' |
| `university_erp.university_examinations.transcript` | `get_student_academic_summary` | get_student_academic_summary() missing 1 required positional argument: 'student' |
| `university_erp.university_examinations.transcript` | `get_semester_results` | get_semester_results() missing 1 required positional argument: 'student' |
| `university_erp.university_examinations.doctype.internal_assessment.internal_assessment` | `get_student_assessments` | get_student_assessments() missing 1 required positional argument: 'student' |
| `university_erp.university_examinations.doctype.practical_examination.practical_examination` | `get_student_practical_result` | get_student_practical_result() missing 1 required positional argument: 'student' |
| `university_erp.university_hostel.doctype.hostel_attendance.hostel_attendance` | `get_hostel_residents` | get_hostel_residents() missing 1 required positional argument: 'hostel_building' |
| `university_erp.university_hostel.doctype.hostel_attendance.hostel_attendance` | `get_attendance_summary` | get_attendance_summary() missing 3 required positional arguments: 'hostel_building', 'from_date', and 'to_date' |
| `university_erp.university_hostel.doctype.hostel_attendance.hostel_attendance` | `get_student_attendance_history` | get_student_attendance_history() missing 1 required positional argument: 'student' |
| `university_erp.university_hostel.doctype.hostel_building.hostel_building` | `get_building_stats` | get_building_stats() missing 1 required positional argument: 'building' |
| `university_erp.university_hostel.doctype.hostel_building.hostel_building` | `get_buildings_by_type` | get_buildings_by_type() missing 1 required positional argument: 'hostel_type' |
| `university_erp.university_hostel.doctype.hostel_building.hostel_building` | `get_buildings_for_gender` | get_buildings_for_gender() missing 1 required positional argument: 'gender' |
| `university_erp.university_hostel.doctype.hostel_bulk_attendance.hostel_bulk_attendance` | `get_residents_for_attendance` | get_residents_for_attendance() missing 1 required positional argument: 'building' |
| `university_erp.university_hostel.doctype.hostel_bulk_attendance.hostel_bulk_attendance` | `get_attendance_status` | get_attendance_status() missing 3 required positional arguments: 'building', 'attendance_date', and 'attendance_type' |
| `university_erp.university_hostel.doctype.hostel_bulk_attendance.hostel_bulk_attendance` | `get_building_attendance_summary` | get_building_attendance_summary() missing 3 required positional arguments: 'building', 'from_date', and 'to_date' |
| `university_erp.university_hostel.doctype.hostel_maintenance_request.hostel_maintenance_request` | `get_pending_requests_for_room` | get_pending_requests_for_room() missing 1 required positional argument: 'room' |
| `university_erp.university_hostel.doctype.hostel_mess.hostel_mess` | `get_mess_menu` | get_mess_menu() missing 1 required positional argument: 'mess' |
| `university_erp.university_hostel.doctype.hostel_mess.hostel_mess` | `get_today_menu` | get_today_menu() missing 1 required positional argument: 'mess' |
| `university_erp.university_hostel.doctype.hostel_room.hostel_room` | `get_room_occupants` | get_room_occupants() missing 1 required positional argument: 'room' |
| `university_erp.university_hostel.doctype.hostel_visitor.hostel_visitor` | `check_in_visitor` | check_in_visitor() missing 5 required positional arguments: 'visitor_name', 'visitor_mobile', 'student', 'building', and |
| `university_erp.university_hostel.doctype.hostel_visitor.hostel_visitor` | `check_out_visitor` | check_out_visitor() missing 1 required positional argument: 'visitor_id' |
| `university_erp.university_hostel.doctype.mess_menu.mess_menu` | `get_week_menu` | get_week_menu() missing 1 required positional argument: 'mess' |
| `university_erp.university_integrations.biometric_integration` | `get_device_users` | get_device_users() missing 1 required positional argument: 'device_name' |
| `university_erp.university_integrations.digilocker_integration` | `get_student_digilocker_documents` | get_student_digilocker_documents() missing 1 required positional argument: 'student' |
| `university_erp.university_integrations.payment_gateway` | `get_payment_status` | get_payment_status() missing 1 required positional argument: 'transaction_name' |
| `university_erp.university_integrations.doctype.payment_transaction.payment_transaction` | `get_transaction_status` | get_transaction_status() missing 1 required positional argument: 'transaction_name' |
| `university_erp.university_integrations.doctype.payment_transaction.payment_transaction` | `get_student_transactions` | get_student_transactions() missing 1 required positional argument: 'student' |
| `university_erp.university_inventory.doctype.inventory_item.inventory_item` | `get_item_details` | get_item_details() missing 1 required positional argument: 'item_code' |
| `university_erp.university_inventory.doctype.inventory_item_group.inventory_item_group` | `get_children` | get_children() missing 1 required positional argument: 'doctype' |
| `university_erp.university_inventory.doctype.lab_consumable_issue.lab_consumable_issue` | `get_lab_consumable_summary` | get_lab_consumable_summary() missing 3 required positional arguments: 'lab', 'from_date', and 'to_date' |
| `university_erp.university_inventory.doctype.lab_equipment.lab_equipment` | `check_equipment_availability` | check_equipment_availability() missing 4 required positional arguments: 'equipment', 'booking_date', 'start_time', and ' |
| `university_erp.university_inventory.doctype.lab_equipment_booking.lab_equipment_booking` | `get_equipment_bookings` | get_equipment_bookings() missing 3 required positional arguments: 'equipment', 'from_date', and 'to_date' |
| `university_erp.university_inventory.doctype.stock_entry.stock_entry` | `get_items_from_purchase_order` | get_items_from_purchase_order() missing 1 required positional argument: 'purchase_order' |
| `university_erp.university_inventory.doctype.stock_entry.stock_entry` | `get_items_from_material_request` | get_items_from_material_request() missing 1 required positional argument: 'material_request' |
| `university_erp.university_inventory.doctype.stock_ledger_entry.stock_ledger_entry` | `get_item_stock_by_warehouse` | get_item_stock_by_warehouse() missing 1 required positional argument: 'item_code' |
| `university_erp.university_inventory.doctype.supplier.supplier` | `get_supplier_details` | get_supplier_details() missing 1 required positional argument: 'supplier' |
| `university_erp.university_inventory.doctype.supplier_group.supplier_group` | `get_children` | get_children() missing 1 required positional argument: 'doctype' |
| `university_erp.university_inventory.doctype.warehouse.warehouse` | `get_children` | get_children() missing 1 required positional argument: 'doctype' |
| `university_erp.university_inventory.doctype.warehouse.warehouse` | `get_warehouse_stock` | get_warehouse_stock() missing 1 required positional argument: 'warehouse' |
| `university_erp.university_library.doctype.library_article.library_article` | `search_catalog` | search_catalog() missing 1 required positional argument: 'query' |
| `university_erp.university_library.doctype.library_article.library_article` | `get_article_availability` | get_article_availability() missing 1 required positional argument: 'article' |
| `university_erp.university_library.doctype.library_member.library_member` | `get_member_status` | get_member_status() missing 1 required positional argument: 'member' |
| `university_erp.university_lms.doctype.lms_content.lms_content` | `get_course_content` | get_course_content() missing 1 required positional argument: 'lms_course' |
| `university_erp.university_lms.doctype.lms_content_progress.lms_content_progress` | `get_course_progress` | get_course_progress() missing 2 required positional arguments: 'lms_course' and 'student' |
| `university_erp.university_lms.doctype.lms_discussion.lms_discussion` | `get_course_discussions` | get_course_discussions() missing 1 required positional argument: 'lms_course' |
| `university_erp.university_lms.doctype.lms_quiz.lms_quiz` | `get_quiz_results` | get_quiz_results() missing 1 required positional argument: 'attempt_name' |
| `university_erp.university_obe.doctype.accreditation_cycle.accreditation_cycle` | `get_accreditation_progress` | get_accreditation_progress() missing 1 required positional argument: 'accreditation_cycle' |
| `university_erp.university_obe.doctype.assessment_rubric.assessment_rubric` | `get_rubric_level` | get_rubric_level() missing 2 required positional arguments: 'rubric_name' and 'percentage' |
| `university_erp.university_obe.doctype.course_outcome.course_outcome` | `get_course_outcomes` | get_course_outcomes() missing 1 required positional argument: 'course' |
| `university_erp.university_obe.doctype.course_outcome.course_outcome` | `get_co_statistics` | get_co_statistics() missing 1 required positional argument: 'course' |
| `university_erp.university_obe.doctype.co_attainment.co_attainment` | `calculate_co_attainment` | calculate_co_attainment() missing 2 required positional arguments: 'course' and 'academic_term' |
| `university_erp.university_obe.doctype.co_po_mapping.co_po_mapping` | `get_po_coverage` | get_po_coverage() missing 1 required positional argument: 'program' |
| `university_erp.university_obe.doctype.obe_survey.obe_survey` | `get_survey_form` | get_survey_form() missing 2 required positional arguments: 'survey_type' and 'program' |
| `university_erp.university_obe.doctype.po_attainment.po_attainment` | `calculate_po_attainment` | calculate_po_attainment() missing 2 required positional arguments: 'program' and 'academic_year' |
| `university_erp.university_obe.doctype.program_educational_objective.program_educational_objective` | `get_program_peos` | get_program_peos() missing 1 required positional argument: 'program' |
| `university_erp.university_obe.doctype.program_outcome.program_outcome` | `get_program_outcomes` | get_program_outcomes() missing 1 required positional argument: 'program' |
| `university_erp.university_obe.report.co_po_mapping_matrix.co_po_mapping_matrix` | `get_program_courses` | get_program_courses() missing 6 required positional arguments: 'doctype', 'txt', 'searchfield', 'start', 'page_len', and |
| `university_erp.university_payments.bank_reconciliation` | `get_reconciliation_data` | get_reconciliation_data() missing 3 required positional arguments: 'bank_account', 'from_date', and 'to_date' |
| `university_erp.university_payments.payment_gateway` | `get_payment_status` | get_payment_status() missing 1 required positional argument: 'payment_order_name' |
| `university_erp.university_payments.doctype.payment_order.payment_order` | `get_payment_order_status` | get_payment_order_status() missing 1 required positional argument: 'payment_order_name' |
| `university_erp.university_placement.doctype.placement_company.placement_company` | `get_company_placements` | get_company_placements() missing 1 required positional argument: 'company' |
| `university_erp.university_placement.doctype.placement_drive.placement_drive` | `get_drive_applicants` | get_drive_applicants() missing 1 required positional argument: 'drive' |
| `university_erp.university_placement.doctype.placement_job_opening.placement_job_opening` | `check_student_eligibility` | check_student_eligibility() missing 2 required positional arguments: 'job_opening' and 'student' |
| `university_erp.university_placement.doctype.placement_job_opening.placement_job_opening` | `get_eligible_students` | get_eligible_students() missing 1 required positional argument: 'job_opening' |
| `university_erp.university_placement.doctype.student_resume.student_resume` | `get_resume_for_student` | get_resume_for_student() missing 1 required positional argument: 'student' |
| `university_erp.university_portals.api.faculty_api` | `get_students_for_attendance` | get_students_for_attendance() missing 1 required positional argument: 'course_schedule' |
| `university_erp.university_portals.api.faculty_api` | `get_students_for_grading` | get_students_for_grading() missing 2 required positional arguments: 'course' and 'assessment_plan' |
| `university_erp.university_portals.api.faculty_api` | `get_grade_analytics` | get_grade_analytics() missing 2 required positional arguments: 'course' and 'assessment_plan' |
| `university_erp.university_portals.api.faculty_api` | `get_student_detail` | get_student_detail() missing 2 required positional arguments: 'student' and 'course' |
| `university_erp.university_portals.api.faculty_api` | `get_performance_analytics` | get_performance_analytics() missing 1 required positional argument: 'course' |
| `university_erp.university_portals.api.faculty_api` | `get_lms_course_content` | get_lms_course_content() missing 1 required positional argument: 'course' |
| `university_erp.university_portals.api.faculty_api` | `get_copo_matrix` | get_copo_matrix() missing 1 required positional argument: 'course' |
| `university_erp.university_portals.api.faculty_api` | `get_copo_student_detail` | get_copo_student_detail() missing 2 required positional arguments: 'course' and 'co' |
| `university_erp.university_portals.api.portal_api` | `get_child_details` | get_child_details() missing 1 required positional argument: 'student' |
| `university_erp.university_portals.www.faculty-portal.attendance` | `get_student_group_students` | get_student_group_students() missing 1 required positional argument: 'student_group' |
| `university_erp.university_student_info.lifecycle` | `get_student_status_history` | get_student_status_history() missing 1 required positional argument: 'student_name' |
| `university_erp.university_student_info.lifecycle` | `get_allowed_status_transitions` | get_allowed_status_transitions() missing 1 required positional argument: 'student_name' |
| `university_erp.university_transport.doctype.transport_allocation.transport_allocation` | `get_route_students` | get_route_students() missing 1 required positional argument: 'route' |
| `university_erp.university_transport.doctype.transport_allocation.transport_allocation` | `get_route_capacity` | get_route_capacity() missing 1 required positional argument: 'route' |
| `university_erp.university_transport.doctype.transport_route.transport_route` | `get_route_stops` | get_route_stops() missing 1 required positional argument: 'route' |
| `university_erp.university_transport.doctype.transport_route.transport_route` | `get_route_schedule` | get_route_schedule() missing 1 required positional argument: 'route' |
| `university_erp.www.student-portal.feedback.index` | `get_feedback_form_questions` | get_feedback_form_questions() missing 1 required positional argument: 'form_name' |
| `university_erp.www.student-portal.grievances.index` | `get_grievance_details` | get_grievance_details() missing 1 required positional argument: 'grievance_id' |
| `university_erp.www_old.library.index` | `search_books` | search_books() missing 1 required positional argument: 'query' |

## Guest-Accessible Endpoints

These endpoints allow unauthenticated access (allow_guest=True).

| Module | Endpoint | Type |
|--------|----------|------|
| `university_erp.university_erp.api.webhooks.payment` | `razorpay_webhook` | OTHER |
| `university_erp.university_erp.api.webhooks.payment` | `payu_webhook` | OTHER |
| `university_erp.university_erp.doctype.emergency_alert.emergency_alert` | `get_emergency_contacts` | GET |
| `university_erp.university_integrations.certificate_generator` | `verify_certificate` | OTHER |
| `university_erp.university_integrations.digilocker_integration` | `digilocker_callback` | OTHER |
| `university_erp.university_integrations.payment_gateway` | `payment_callback` | OTHER |
| `university_erp.university_integrations.payment_gateway` | `razorpay_webhook` | OTHER |
| `university_erp.university_integrations.whatsapp_gateway` | `whatsapp_webhook` | OTHER |
| `university_erp.university_obe.doctype.obe_survey.obe_survey` | `get_survey_form` | GET |
| `university_erp.university_obe.doctype.obe_survey.obe_survey` | `submit_survey` | ACTION |
| `university_erp.university_payments.webhooks.payu_callback` | `payu_success` | OTHER |
| `university_erp.university_payments.webhooks.payu_callback` | `payu_failure` | OTHER |
| `university_erp.university_payments.webhooks.payu_callback` | `payu_cancel` | OTHER |
| `university_erp.university_payments.webhooks.razorpay_webhook` | `handle_razorpay_webhook` | OTHER |
| `university_erp.university_portals.api.portal_api` | `get_portal_redirect` | GET |
| `university_erp.www_old.library.index` | `search_books` | GET |
