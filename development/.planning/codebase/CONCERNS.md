# Codebase Concerns

**Analysis Date:** 2026-03-17

## Tech Debt

**Broad Exception Handling Without Logging:**
- Issue: Multiple scripts use bare `except Exception` blocks with silent passes or minimal logging, masking real errors.
- Files:
  - `populate_student_portal_data.py` (lines 211, 229)
  - `create_student_portal_data.py` (line 78)
- Impact: Failures in test data creation silently continue, leading to incomplete data without indication. Duplicate data attempts are silently ignored, making debugging difficult.
- Fix approach: Replace bare `except Exception: pass` with specific exception types; add structured logging to indicate skipped operations.

**Hardcoded Credentials in Data Creation Scripts:**
- Issue: Database credentials, site names, and admin passwords are hardcoded in installer and initialization scripts.
- Files:
  - `installer.py` (lines 214, 229: hardcoded `--db-root-password=123`)
  - `create_student_portal_data.py` (line 21: hardcoded student ID `EDU-STU-2026-00002`)
  - `populate_student_portal_data.py` (line 22: hardcoded student ID)
- Impact: Security risk if scripts are committed with credentials; test data is tightly coupled to specific IDs making scripts non-reusable.
- Fix approach: Extract credentials to environment variables or config files; parameterize student IDs for data generation scripts.

**Missing Error Context in API Endpoints:**
- Issue: API endpoints in `portal_api.py` throw generic PermissionError without context on what permission is missing.
- Files: `university_erp/university_portals/api/portal_api.py` (lines 23, 41, 67, etc.)
- Impact: Client-side debugging is difficult; frontend catches generic errors without understanding the root cause.
- Fix approach: Include permission names and required roles in error messages; add audit logging for permission denials.

**Unvalidated External API Calls:**
- Issue: The `useFrappe.js` composable handles HTTP errors but doesn't validate response structure before returning.
- Files: `student-portal-vue/src/composables/useFrappe.js` (line 20)
- Impact: Malformed API responses could cause frontend crashes; no schema validation of portal API responses.
- Fix approach: Implement response schema validation using a library like Zod or Yup; add specific error handling for different response types.

**Database Query Injection Vulnerabilities:**
- Issue: Raw SQL with string concatenation in `api.py` for course schedule calendar view.
- Files: `education/education/api.py` (lines 273-275: format string with conditions variable)
- Impact: Risk of SQL injection if filters are not properly sanitized by Frappe framework.
- Fix approach: Use parameterized queries exclusively; audit all raw SQL usage for injection risks.

## Known Bugs

**Silent Duplicate Data Creation:**
- Symptoms: Multiple test data creation scripts may create duplicate records if run multiple times without checking all uniqueness constraints.
- Files:
  - `create_student_portal_data.py` (lines 109-122: checks course existence but not all records)
  - `populate_student_portal_data.py` (lines 211-212: bare except suppresses duplicate key errors)
- Trigger: Running any create script twice without clearing records first.
- Workaround: Always drop/clear test data before re-running scripts; use unique constraints on student IDs and dates.

**Incomplete Library Transaction Creation:**
- Symptoms: Library transactions are skipped with warning message instead of proper implementation.
- Files: `populate_student_portal_data.py` (line 385)
- Trigger: Any call to `create_library_records()` function.
- Workaround: Library functionality is incomplete; requires Item DocType setup not yet implemented.

**Missing Assessment Plan Fallback:**
- Symptoms: Assessment result creation creates assessment plans on the fly if none exist, creating test data pollution.
- Files: `create_student_portal_data.py` (lines 335-337)
- Trigger: When creating assessment results without pre-existing plans.
- Workaround: Pre-create all assessment plans before running data creation scripts.

## Security Considerations

**Ignore Permissions in Data Creation:**
- Risk: Scripts use `ignore_permissions=True` extensively, bypassing Frappe's permission model during data creation.
- Files:
  - `create_student_portal_data.py` (lines 66, 117, 148, 198)
  - `populate_student_portal_data.py` (lines 98, 138, 170, 245, 276)
  - `installer.py` (not using ignore_permissions but uses subprocess as root)
  - `portal_api.py` (line 155)
- Current mitigation: Scripts are meant for development/testing only but no clear separation from production.
- Recommendations:
  - Never run these scripts in production
  - Mark scripts with warnings about development-only use
  - Implement proper seed data management system with permission checks
  - Use Frappe's built-in data import mechanisms for production data

**Student Data Exposure in Portal API:**
- Risk: `get_student_profile()` returns full `student.as_dict()` including potentially sensitive fields (marks, phone, address).
- Files: `portal_api.py` (line 293)
- Current mitigation: Frappe permission system gate-keeps access.
- Recommendations:
  - Explicitly whitelist which fields should be returned instead of entire document
  - Add field-level permissions audit
  - Log all profile access attempts for audit trail

**CSRF Token Handling in SPA:**
- Risk: CSRF token is extracted from cookies via regex pattern matching which could be brittle.
- Files: `student-portal-vue/src/composables/useFrappe.js` (lines 5-8)
- Current mitigation: Token is sent in X-Frappe-CSRF-Token header.
- Recommendations:
  - Use Frappe's native CSRF token mechanism or expose it via API endpoint
  - Implement proper SPA cookie/CSRF integration testing

**Fee Payment Creation Without Validation:**
- Risk: `create_payment_request()` allows student to create payment requests without validating payment gateway configuration.
- Files: `portal_api.py` (lines 142-162)
- Current mitigation: Permission checks are in place.
- Recommendations:
  - Validate payment gateway is configured before allowing request creation
  - Verify fee amount hasn't changed since student viewed the page
  - Add rate limiting to prevent spam requests

## Performance Bottlenecks

**N+1 Query Problem in Data Creation:**
- Problem: Creating 120+ attendance records in loop makes individual `frappe.get_doc()` and `insert()` calls (lines 59-66 in `create_attendance_final.py`).
- Files: `create_attendance_final.py`, `create_student_portal_data.py`
- Cause: Inserting one record at a time without batch operations.
- Improvement path: Use Frappe's batch insert or prepare bulk insert SQL to reduce round-trips from ~120 to 1-2.

**Dashboard API Returns Full Document Trees:**
- Problem: `get_student_dashboard()` likely fetches all related documents without pagination or field limiting.
- Files: `portal_api.py` (lines 27-29)
- Cause: Generic get_dashboard_data functions return entire related document structures.
- Improvement path: Implement explicit field selection and pagination; cache dashboard data with short TTL.

**Unrestricted Query Results in Library/Attendance:**
- Problem: `get_issued_books()` and `get_monthly_attendance()` likely fetch all historical records.
- Files: `portal_api.py` (lines 247-250)
- Cause: No limit or date range restriction on historical queries.
- Improvement path: Add configurable limits (e.g., last 50 books, current semester attendance).

**Frontend Loads All Categories/Types:**
- Problem: SPA fetches all available certificate types, grievance categories, fee structures without filtering.
- Files: `portal_api.py` (lines 316, 336, 216)
- Cause: No query pagination or filtering implemented.
- Improvement path: Add pagination, search, and filtering to these list endpoints.

## Fragile Areas

**Test Data Scripts with No Version Management:**
- Files: `create_student_portal_data.py`, `populate_student_portal_data.py`, `create_attendance_final.py`
- Why fragile: These scripts reference hard-coded field names and document structures that change when the education app schema changes. No migration system.
- Safe modification:
  - Add schema version checks at script start
  - Make field mappings configurable
  - Implement a seed data management system
- Test coverage: Scripts have no automated tests; running manually is error-prone.

**Portal API Assumes Document Structure:**
- Files: `portal_api.py` (especially lines 174-180, 290-297)
- Why fragile: Hardcoded field references like `student.get("custom_cgpa")` break if field names change.
- Safe modification:
  - Add schema validation/documentation for Student doctype expected fields
  - Use safe accessors with defaults throughout
  - Add integration tests that verify API response structure
- Test coverage: No tests for API response structure; fields can disappear without detection.

**Hardcoded Student ID in Multiple Places:**
- Files:
  - `create_student_portal_data.py` (line 36)
  - `create_attendance_final.py` (line 21)
  - `populate_student_portal_data.py` (line 22)
- Why fragile: If this student is deleted, data creation scripts fail silently.
- Safe modification:
  - Make student selection parameterized (command-line arg or config)
  - Add student creation as first step if not exists
  - Use findByEmail or similar flexible lookup instead of hard ID

**Conditional DocType Existence Checks:**
- Files: `portal_api.py` (multiple checks like line 355)
- Why fragile: Features silently degrade if optional doctypes don't exist; no indication to frontend.
- Safe modification:
  - Return explicit feature flags instead of null data
  - Log missing doctypes at startup
  - Add configuration system for optional modules

## Scaling Limits

**Single-Student Test Data:**
- Current capacity: Scripts create data for single hardcoded student ID only.
- Limit: Cannot test multi-student scenarios or course load balancing.
- Scaling path: Parameterize student/course creation; create fixture factory for bulk student enrollment.

**Attendance Array Generation:**
- Current capacity: 120-day attendance loop creates 84-96 records (weekdays only).
- Limit: Course-wise attendance calculations will be slow with years of data.
- Scaling path: Pre-compute monthly/semester summaries; implement time-range queries with indexes.

**Portal API Response Size:**
- Current capacity: No pagination on historical data (books, fees, grievances).
- Limit: Students with years of data will download MB of records per page load.
- Scaling path: Implement cursor-based pagination; add GraphQL-style field selection.

## Dependencies at Risk

**Frappe Framework Tight Coupling:**
- Risk: Education app and portal code depend on Frappe doctype structure and API patterns that may change between versions.
- Files: All files in `education/`, `university_erp/`, test data scripts
- Impact: Frappe framework updates may require rewriting large portions of code.
- Migration plan:
  - Create abstraction layer for Frappe operations (repository pattern)
  - Add integration tests that verify with actual Frappe instance
  - Plan for annual framework upgrade reviews

**Hardcoded Date Logic:**
- Risk: Scripts hardcode date offsets (e.g., `add_days(today, -120)` for attendance).
- Files: `create_attendance_final.py` (line 39), `populate_student_portal_data.py` (lines 182-187)
- Impact: Scripts become stale as time advances; test data stops being realistic.
- Migration plan: Use configurable date ranges; implement time-relative data generation.

## Missing Critical Features

**No Audit Trail for Data Changes:**
- Problem: Portal API allows profile updates, fee operations, and grievance submissions with no audit log.
- Blocks: Cannot investigate student data changes or track who made modifications.
- Implementation path: Wrap all data modification APIs with audit logging middleware.

**No Rate Limiting on Student APIs:**
- Problem: Students can spam certificate requests, maintenance requests, or grievances.
- Blocks: DOS risk; no protection against abuse.
- Implementation path: Add per-user rate limiting to all whitelist() endpoints; use Redis for distributed rate limiting.

**Incomplete Multi-Role Support:**
- Problem: Portal code only handles Student role; no faculty/admin portal endpoints.
- Blocks: Cannot build faculty dashboard or admin management pages using portal API.
- Implementation path: Extend portal API with role detection; implement factory pattern for role-specific APIs.

**No Offline Support:**
- Problem: SPA requires network for every page; no caching/offline mode.
- Blocks: Students in low-connectivity areas experience poor UX.
- Implementation path: Implement Service Worker with offline cache strategy for read-only pages.

## Test Coverage Gaps

**Untested Test Data Scripts:**
- What's not tested: No automated tests for data creation scripts.
- Files: `create_student_portal_data.py`, `populate_student_portal_data.py`, `create_attendance_final.py`
- Risk: Scripts may create malformed data; silent failures mask bugs.
- Priority: High - Should have integration tests that verify all created records have valid data.

**No Portal API Integration Tests:**
- What's not tested: API endpoints have no tests for happy path, edge cases, or permission boundaries.
- Files: `portal_api.py`
- Risk: API breaks silently when underlying data structure changes.
- Priority: High - Need integration test suite covering all @whitelist() endpoints.

**Frontend Component State Management Untested:**
- What's not tested: Vue components don't have unit tests for loading states, error handling, data binding.
- Files: `student-portal-vue/src/views/*.vue`
- Risk: UI can break without detection.
- Priority: Medium - Should have snapshot tests at minimum.

**No Permission Boundary Tests:**
- What's not tested: No tests verifying students cannot access other students' data.
- Files: All of `portal_api.py`
- Risk: Critical security hole could exist undetected.
- Priority: Critical - Must add security tests verifying permission checks work.

**Database Migration Path Untested:**
- What's not tested: Schema changes not tested against live data.
- Files: All doctype migrations
- Risk: Database updates could fail on production instance.
- Priority: High - Need migration validation tests before any schema changes.

---

*Concerns audit: 2026-03-17*
