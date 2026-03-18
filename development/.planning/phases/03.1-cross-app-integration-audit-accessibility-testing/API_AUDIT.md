# Faculty API Integration Audit Results

**Generated:** 2026-03-18 23:46:10
**Site:** university.local
**Faculty User:** faculty2@nit.edu (instructor-linked employee)

## Executive Summary

- **Total Endpoints Tested:** 27
- **GET Endpoints:** 19 (0 PASS, 19 FAIL, 0 DEGRADED)
- **ACTION Endpoints:** 8 (0 PASS, 8 FAIL, 0 WARNING)
- **Cross-App Checks:** 4

## Endpoint Discovery

Discovered **27** @frappe.whitelist() endpoints programmatically from faculty_api.py source.

**GET endpoints:**
- `get_faculty_dashboard`
- `get_today_classes`
- `get_weekly_timetable`
- `get_students_for_attendance`
- `get_announcements`
- `get_students_for_grading`
- `get_grade_analytics`
- `get_student_list`
- `get_student_detail`
- `get_performance_analytics`
- `get_leave_balance`
- `get_leave_history`
- `get_student_leave_requests`
- `get_lms_courses`
- `get_lms_course_content`
- `get_publications`
- `get_copo_matrix`
- `get_copo_student_detail`
- `get_workload_summary`

**ACTION endpoints:**
- `submit_attendance`
- `save_draft_grade`
- `submit_grades`
- `apply_leave`
- `approve_student_leave`
- `reject_student_leave`
- `save_lms_content`
- `delete_lms_content`

## GET Endpoint Results

| # | Endpoint | Status | Response Type | Data Size | Cross-App Check | Notes |
|---|----------|--------|---------------|-----------|-----------------|-------|
| 1 | get_faculty_dashboard | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 2 | get_today_classes | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 3 | get_weekly_timetable | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 4 | get_students_for_attendance | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 5 | get_announcements | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 6 | get_students_for_grading | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 7 | get_grade_analytics | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 8 | get_student_list | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 9 | get_student_detail | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 10 | get_performance_analytics | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 11 | get_leave_balance | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 12 | get_leave_history | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 13 | get_student_leave_requests | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 14 | get_lms_courses | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 15 | get_lms_course_content | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 16 | get_publications | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 17 | get_copo_matrix | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 18 | get_copo_student_detail | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 19 | get_workload_summary | FAIL |  | 0 | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |

## ACTION Endpoint Results

| # | Endpoint | Validation Check | Status | Notes |
|---|----------|-----------------|--------|-------|
| 1 | submit_attendance | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 2 | save_draft_grade | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 3 | submit_grades | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 4 | apply_leave | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 5 | approve_student_leave | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 6 | reject_student_leave | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 7 | save_lms_content | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| 8 | delete_lms_content | ERROR | FAIL | Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |

## Cross-App Data Resolution

| Endpoint | Referenced Doctype | Exists in DB? | Records Found? |
|----------|--------------------|---------------|----------------|
| get_faculty_dashboard | ERROR | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| get_today_classes | Teaching Assignment Schedule | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| get_leave_balance | Leave Type | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |
| get_students_for_grading | Student | N/A | (1054, "Unknown column 'custom_is_faculty' in 'WHERE'") |

## Recommendations

### Failed GET Endpoints (need fixing)
- **get_faculty_dashboard**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_today_classes**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_weekly_timetable**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_students_for_attendance**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_announcements**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_students_for_grading**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_grade_analytics**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_student_list**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_student_detail**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_performance_analytics**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_leave_balance**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_leave_history**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_student_leave_requests**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_lms_courses**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_lms_course_content**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_publications**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_copo_matrix**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_copo_student_detail**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **get_workload_summary**: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")

### Failed ACTION Endpoints (need fixing)
- **submit_attendance**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **save_draft_grade**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **submit_grades**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **apply_leave**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **approve_student_leave**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **reject_student_leave**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **save_lms_content**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
- **delete_lms_content**: Unexpected error: (1054, "Unknown column 'custom_is_faculty' in 'WHERE'")
