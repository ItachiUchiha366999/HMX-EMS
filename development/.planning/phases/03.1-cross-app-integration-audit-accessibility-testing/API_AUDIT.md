# Faculty API Integration Audit Results

**Generated:** 2026-03-19 13:44:33
**Site:** university.local
**Faculty User:** faculty2@nit.edu (instructor-linked employee)

## Executive Summary

- **Total Endpoints Tested:** 27
- **GET Endpoints:** 19 (0 PASS, 19 FAIL, 0 DEGRADED)
- **ACTION Endpoints:** 8 (8 PASS, 0 FAIL, 0 WARNING)
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
| 1 | get_faculty_dashboard | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 2 | get_today_classes | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 3 | get_weekly_timetable | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 4 | get_students_for_attendance | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 5 | get_announcements | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 6 | get_students_for_grading | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 7 | get_grade_analytics | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 8 | get_student_list | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 9 | get_student_detail | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 10 | get_performance_analytics | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 11 | get_leave_balance | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 12 | get_leave_history | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 13 | get_student_leave_requests | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 14 | get_lms_courses | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 15 | get_lms_course_content | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 16 | get_publications | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |
| 17 | get_copo_matrix | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 18 | get_copo_student_detail | FAIL |  | 0 | N/A | No active faculty profile found for this user |
| 19 | get_workload_summary | FAIL |  | 0 | N/A | PermissionError (faculty user lacks permissions) |

## ACTION Endpoint Results

| # | Endpoint | Validation Check | Status | Notes |
|---|----------|-----------------|--------|-------|
| 1 | submit_attendance | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |
| 2 | save_draft_grade | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |
| 3 | submit_grades | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |
| 4 | apply_leave | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |
| 5 | approve_student_leave | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |
| 6 | reject_student_leave | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |
| 7 | save_lms_content | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |
| 8 | delete_lms_content | PERMISSION_CHECK | PASS | Permission check: No active faculty profile found for this user |

## Cross-App Data Resolution

| Endpoint | Referenced Doctype | Exists in DB? | Records Found? |
|----------|--------------------|---------------|----------------|
| get_faculty_dashboard | ERROR | N/A | No active faculty profile found for this user |
| get_today_classes | Teaching Assignment Schedule | N/A | No active faculty profile found for this user |
| get_leave_balance | Leave Type | N/A | No active faculty profile found for this user |
| get_students_for_grading | Student | N/A | No active faculty profile found for this user |

## Recommendations

### Failed GET Endpoints (need fixing)
- **get_faculty_dashboard**: PermissionError (faculty user lacks permissions)
- **get_today_classes**: PermissionError (faculty user lacks permissions)
- **get_weekly_timetable**: PermissionError (faculty user lacks permissions)
- **get_students_for_attendance**: No active faculty profile found for this user
- **get_announcements**: PermissionError (faculty user lacks permissions)
- **get_students_for_grading**: No active faculty profile found for this user
- **get_grade_analytics**: No active faculty profile found for this user
- **get_student_list**: PermissionError (faculty user lacks permissions)
- **get_student_detail**: No active faculty profile found for this user
- **get_performance_analytics**: No active faculty profile found for this user
- **get_leave_balance**: PermissionError (faculty user lacks permissions)
- **get_leave_history**: PermissionError (faculty user lacks permissions)
- **get_student_leave_requests**: PermissionError (faculty user lacks permissions)
- **get_lms_courses**: PermissionError (faculty user lacks permissions)
- **get_lms_course_content**: No active faculty profile found for this user
- **get_publications**: PermissionError (faculty user lacks permissions)
- **get_copo_matrix**: No active faculty profile found for this user
- **get_copo_student_detail**: No active faculty profile found for this user
- **get_workload_summary**: PermissionError (faculty user lacks permissions)
