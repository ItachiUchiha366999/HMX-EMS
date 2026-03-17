# Pitfalls Research

**Domain:** University ERP Dashboards, Analytics & Role-Based Portals (Frappe v15)
**Researched:** 2026-03-17
**Confidence:** HIGH (verified against existing codebase + Frappe security bulletins + community evidence)

## Critical Pitfalls

### Pitfall 1: SQL Injection in Dashboard Custom Query Engine

**What goes wrong:**
The existing `dashboard_engine.py` `_execute_query` method does string replacement on raw SQL: `query.replace("%(from_date)s", f"'{filters['from_date']}'")`. This is textbook SQL injection -- any user-supplied filter value can break out of the string literal and execute arbitrary SQL. Management dashboards with custom query widgets are directly exploitable.

**Why it happens:**
Developers avoid Frappe's parameterized query API (`frappe.db.sql` with `%s` placeholders) because custom dashboard queries need dynamic filter injection. String formatting feels simpler but destroys all SQL safety guarantees.

**How to avoid:**
- Never use string replacement for SQL filter values. Use `frappe.db.sql(query, values_dict, as_dict=True)` with proper `%(param)s` placeholders that MariaDB's connector parameterizes safely.
- Validate all filter inputs against expected types (dates must parse as dates, departments must exist as documents).
- For the custom query widget pattern, build a whitelist of allowed query templates stored in the doctype, never accept raw SQL from the frontend.

**Warning signs:**
- Any `query.replace(` or f-string interpolation into SQL in the analytics module.
- Dashboard widgets that accept a `custom_query` field without parameterization.

**Phase to address:**
Phase 1 (Cross-app verification / foundation). This is a security fix that must happen before any dashboard goes to production. Existing `dashboard_engine.py` needs immediate remediation.

---

### Pitfall 2: Missing Permission Checks on Whitelisted Dashboard APIs

**What goes wrong:**
The `get_executive_dashboard_data()` function in `executive_dashboard.py` is decorated with `@frappe.whitelist()` but performs zero role checks. Any authenticated user (including students and parents) can call it and see total fee collections, outstanding amounts, department performance, and other sensitive financial/management data. The existing student portal APIs correctly check `get_current_student()`, but the dashboard APIs do not follow this pattern.

**Why it happens:**
Frappe's `@frappe.whitelist()` only means "this method can be called via API" -- it does NOT enforce any role-based access. Developers assume the desk UI will restrict access, but Vue SPA portals bypass the desk entirely. The Frappe security bulletin documents multiple CVEs (SQL injection via whitelisted methods, permission bypass on reports) proving this is a systemic pattern.

**How to avoid:**
- Every whitelisted API must start with an explicit role check: `frappe.only_for(["Vice Chancellor", "Registrar", "Finance Officer"])` or a custom permission validator.
- Create a `@require_role(*roles)` decorator that wraps `@frappe.whitelist()` and enforces role membership before executing the function body.
- Never rely on "the UI won't show this button" for security -- all APIs are directly callable.
- For portal APIs specifically, validate that the logged-in user is linked to the expected entity (faculty must be linked to Employee, parent must be linked to Student Guardian).

**Warning signs:**
- Any `@frappe.whitelist()` function without a `frappe.only_for()`, `frappe.has_permission()`, or explicit role check in its first lines.
- Dashboard APIs that return financial or HR data without validating the caller's role.

**Phase to address:**
Phase 1 (Foundation). Establish the permission decorator pattern before building any new APIs. Audit and fix all existing analytics APIs.

---

### Pitfall 3: N+1 Query Problem in Dashboard Data Aggregation

**What goes wrong:**
The `get_department_performance()` function loops through departments and calls `_get_department_student_count()`, `_get_department_faculty_count()`, `_get_department_attendance()`, and `_get_department_pass_rate()` individually for each department. With 10 departments, that is 40+ individual database queries for a single dashboard widget. The `get_enrollment_trend()` function runs 12 separate `frappe.db.count()` calls (one per month). A full dashboard load triggers 60-100+ queries and takes 5-15 seconds on production data.

**Why it happens:**
Frappe's ORM (`frappe.get_all`, `frappe.db.count`) is convenient for single-record operations but encourages looping patterns. Dashboard developers think in "get data for each item" rather than "get all data in one query with GROUP BY."

**How to avoid:**
- Replace per-department loops with single aggregation queries: `SELECT department, COUNT(*) FROM tabStudent GROUP BY department`.
- Replace per-month count loops with: `SELECT DATE_FORMAT(creation, '%Y-%m') as month, COUNT(*) FROM tabStudent WHERE creation >= %s GROUP BY month`.
- Use `frappe.db.sql()` for dashboard aggregations instead of `frappe.db.count()` in loops.
- Set a query budget: a dashboard endpoint should execute fewer than 15 database queries total. Log query counts during development.
- Cache aggregated results in Redis with `frappe.cache().set_value()` with a TTL of 5-15 minutes -- management dashboards do not need sub-second freshness.

**Warning signs:**
- Dashboard page load times exceeding 2 seconds.
- MariaDB slow query log showing many identical queries with different WHERE values.
- `frappe.db.count()` or `frappe.get_all()` inside a for-loop in any analytics module.

**Phase to address:**
Phase 2 (Dashboard implementation). Establish the aggregation-first query pattern from the start. Retrofit existing `executive_dashboard.py` queries.

---

### Pitfall 4: Vue SPA Auth Guard Calls API on Every Route Change

**What goes wrong:**
The existing student portal router calls `fetch('/api/method/frappe.auth.get_logged_user')` on EVERY route navigation via `router.beforeEach`. This means navigating between 5 tabs fires 5 HTTP requests just for auth checking, adding 200-500ms latency per navigation. When the portal scales to faculty/HOD/parent roles with more pages, this becomes a noticeable stutter.

**Why it happens:**
The pattern was reasonable for a small student portal (11 pages, single role). But it does not cache the auth state -- each navigation re-verifies. There is also no CSRF token refresh mechanism; the token is read from cookies once but can expire during long sessions.

**How to avoid:**
- Cache the auth result in a reactive store (Pinia or a composable ref) with a TTL (e.g., 5 minutes). Only re-verify on TTL expiry, 401/403 responses, or explicit refresh.
- Move the auth check to an Axios/fetch interceptor that handles 401 globally, rather than a route guard that fires on every navigation.
- For CSRF tokens: implement a token refresh mechanism that re-reads the cookie before each POST, or catches 403 CSRF errors and retries with a fresh token.
- For role-based routing: fetch the user's roles ONCE on app load, store them, and use route meta fields to gate access client-side (with server-side enforcement as the real security layer).

**Warning signs:**
- Network tab showing `get_logged_user` calls on every page transition.
- Users reporting "flash" or delay when switching portal tabs.
- CSRF token errors after users leave their browser idle for 30+ minutes.

**Phase to address:**
Phase 2 (Portal unification). Refactor the auth pattern when building the unified multi-role Vue app. The existing student portal pattern should not be replicated.

---

### Pitfall 5: Cross-App Data Inconsistency (Education Override Conflicts)

**What goes wrong:**
The university_erp app has 6 class overrides for Education app doctypes (Student, Program, Course, AssessmentResult, Fees, Applicant) plus hook integrations for Employee and Department. When building dashboards that aggregate across ERPNext, HRMS, and Education data, the overridden fields and custom behaviors cause silent data mismatches. For example: a faculty count from HRMS's Employee doctype may not match the count from Education's Instructor doctype because the override changes how departments are linked. Fee totals from the Fees doctype override may calculate differently than ERPNext's Accounts module expects.

**Why it happens:**
Frappe's multi-app architecture allows any app to override any doctype's class. But there is no contract enforcement -- overrides can change field names, add validation that rejects previously valid data, or alter linked document relationships. Dashboard queries that join across these boundaries hit silent inconsistencies.

**How to avoid:**
- Run a cross-app verification phase BEFORE building any dashboard views. For each doctype used in dashboards, verify: (a) what app owns it, (b) what overrides exist, (c) what fields are added/modified, (d) do link fields point to consistent targets.
- Create a `data_verification.py` script that runs COUNT and SUM comparisons across related doctypes (e.g., sum of Fees.paid_amount vs sum of Payment Entry amounts for fee category).
- Document every cross-app doctype dependency in a matrix. When an override changes, the matrix shows which dashboards are affected.
- For faculty data specifically: decide whether "faculty" means Employee with designation=Faculty or Instructor in Education, and use ONE canonical query everywhere.

**Warning signs:**
- Dashboard showing different numbers than Frappe desk list views for the same doctype.
- Faculty count changing depending on whether you query Employee or Instructor.
- Fee collection totals not matching between the dashboard and the Accounts module.

**Phase to address:**
Phase 1 (Cross-app verification). This is explicitly called out in PROJECT.md as a prerequisite. Do not skip it -- dashboards built on inconsistent data erode trust permanently.

---

### Pitfall 6: Parent Portal Leaking Other Students' Data

**What goes wrong:**
When building parent portal APIs, developers fetch student data using the student name/ID from the request parameters. If the API does not verify that the requesting parent is actually the guardian of that specific student, any parent can view any student's grades, attendance, fees, and hostel status by changing the student ID in the API call. This is an IDOR (Insecure Direct Object Reference) vulnerability.

**Why it happens:**
The student portal avoids this because `get_current_student()` ties the session user to their own student record. But parent-to-student is a many-to-many relationship (one parent can have multiple children, one student can have multiple guardians). Developers pass the student ID as a parameter for flexibility, forgetting to verify the parent-student link.

**How to avoid:**
- Every parent portal API must: (1) get the logged-in user, (2) find the Student Guardian records linked to that user, (3) verify the requested student ID is in that guardian's linked students list, (4) only then return data.
- Create a `get_guardian_students(user)` utility that returns the list of student IDs a parent can access. Use this as a filter on ALL parent queries.
- Never accept a raw student ID from the frontend without verifying the relationship.
- Write integration tests that explicitly test: "Parent A cannot see Student B's data when Student B is not their child."

**Warning signs:**
- Parent portal APIs that accept `student_id` as a parameter without cross-referencing Student Guardian.
- Any API where changing a URL parameter reveals different students' data.
- Missing test cases for cross-parent data isolation.

**Phase to address:**
Phase 3 (Parent portal). Build the guardian verification utility first, before any parent-facing API.

---

### Pitfall 7: Report Export Crashes on Large Datasets

**What goes wrong:**
Exporting dashboards or drill-down reports to PDF/Excel loads the entire result set into memory on the server, converts it, and streams the response. For a "all students fee status" report across 5000+ students with 20+ columns, this can consume 500MB+ of worker memory, causing the Gunicorn worker to be OOM-killed. The response times out (Frappe default: 300s), the user sees a blank error, and retries make it worse.

**Why it happens:**
Frappe's built-in report export uses `frappe.utils.xlsxutils` which builds the entire workbook in memory. PDF generation via wkhtmltopdf or weasyprint renders the full HTML first. Neither approach streams. Developers test with 50 rows and ship, then production hits 5000+ rows.

**How to avoid:**
- Implement export as a background job: the user clicks "Export", gets a toast saying "Your report is being prepared", and receives a download link via notification or email when ready.
- Use `frappe.enqueue()` for any export expected to exceed 1000 rows.
- For Excel: use openpyxl's write-only mode which streams rows to disk instead of building in memory.
- For PDF: paginate the report and generate pages sequentially, or use a chunked HTML-to-PDF approach.
- Set hard limits: dashboard exports cap at 10,000 rows with a "use filters to narrow results" message. Full data dumps go through a separate bulk export path.

**Warning signs:**
- Gunicorn worker processes consuming >500MB RSS memory.
- Export requests timing out after 5 minutes.
- Users clicking "Export" multiple times because nothing appears to happen (each click spawns another memory-heavy process).

**Phase to address:**
Phase 4 (Export & scheduled reports). Design the async export pattern from the start rather than retrofitting synchronous exports.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Mock data fallbacks in dashboard functions | Dashboard renders even without real data | Mock data ships to production, masks real data issues, VC sees fake numbers | Only during development with a feature flag that ERRORS in production instead of falling back to mocks |
| `frappe.db.sql()` with raw SQL everywhere | Fast to write, full SQL flexibility | No permission filtering, no audit trail, bypasses Frappe's ORM security layer | Only for read-only aggregations in verified, permission-gated functions |
| Single monolithic dashboard API returning all widgets | Simple frontend -- one API call loads everything | One slow widget blocks the entire dashboard render; one error crashes everything | Never for production dashboards. Use per-widget APIs with parallel frontend fetches |
| Hardcoded role names in API checks | Quick permission enforcement | Role names change, new roles get missed, impossible to configure per-institution | Only for v1 MVP. Move to configurable role-permission mapping for v2 |
| Skipping Redis caching for dashboard data | Simpler code, always-fresh data | Every dashboard view hits the database; 10 concurrent users = 1000 queries/minute | Never for management dashboards. Cache with 5-15 min TTL from day one |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Education app Student doctype | Querying `tabStudent` directly without accounting for custom fields added by university_erp override | Always use `frappe.get_all("Student", fields=[...])` with explicit field lists; verify override class adds expected fields |
| HRMS Employee as Faculty | Assuming all Employees are faculty; querying Employee without designation/department filters | Filter by `designation` or a custom `is_faculty` field; cross-reference with Education Instructor doctype |
| ERPNext Fees vs Accounts | Assuming Fees.paid_amount equals what Accounts module reports as revenue | Verify the fee-to-journal-entry link; use Fees for student-facing views, GL Entry for finance dashboards |
| Frappe session in Vue SPA | Assuming `frappe.session.user` is available in the SPA JavaScript context | In Vue SPAs, you have NO access to Frappe's client-side session object. Auth state must come from API calls. Use cookie-based session + explicit API verification |
| CSRF token lifecycle | Reading CSRF token once at app load and assuming it persists | CSRF token rotates on session refresh. Re-read from cookie before each POST request. Handle 403 by refreshing token and retrying once |
| Frappe real-time (Socket.io) | Trying to use `frappe.realtime` in Vue SPA for live dashboard updates | Frappe's realtime requires the desk app's Socket.io setup. For Vue SPAs, connect to Socket.io directly using the same session cookie, or poll instead |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| COUNT(*) on unindexed tables | Dashboard KPI cards take 3-5 seconds to load | Add indexes on `creation`, `modified`, `department`, `academic_year` for all frequently-counted doctypes | >50,000 records in a single doctype (Student, Fees, Attendance) |
| Loading all chart data points without aggregation | Trend charts request raw records and aggregate in JS | Aggregate in SQL with GROUP BY; send only the chart-ready labels+values | >10,000 raw records per chart |
| Full table scan for "today's" data | "Fee collection today" queries scan all Fees records | Add composite index on (docstatus, posting_date); ensure WHERE clauses use indexed columns | >100,000 Fees records over multiple years |
| Rendering all dashboard widgets synchronously | Page blocks until slowest widget responds | Load widget data in parallel (Promise.all); render skeleton/shimmer for each widget independently | >5 widgets per dashboard, any widget taking >1 second |
| No pagination on drill-down reports | Clicking "View all students in department" loads 2000+ rows at once | Server-side pagination with limit/offset; virtual scrolling on frontend | >500 rows in any drill-down view |
| MariaDB `innodb_buffer_pool_size` too small | All queries are slow, not just dashboard queries | Set to 70-80% of available RAM in Docker container; verify with `SHOW VARIABLES LIKE 'innodb_buffer_pool_size'` | When database size exceeds buffer pool size (typically >1GB data) |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| `@frappe.whitelist()` without role check on dashboard APIs | Any authenticated user (student, parent) can see management financial data | Add `frappe.only_for()` or custom role decorator to EVERY dashboard endpoint |
| Accepting student/employee IDs from frontend without ownership verification | IDOR: parents see other students' data; faculty see other departments' data | Always verify requester-to-entity relationship server-side before returning data |
| String interpolation in SQL queries (existing in dashboard_engine.py) | Full SQL injection -- attacker can read/modify any data in the database | Use parameterized queries exclusively; audit all `query.replace()` patterns |
| Using `frappe.get_doc()` in APIs without `frappe.has_permission()` | Document-level permissions bypassed; sensitive doctypes exposed | Call `frappe.has_permission(doctype, "read", doc_name)` before returning document data |
| Exposing raw error messages to frontend | Stack traces reveal table names, file paths, SQL queries to attackers | Catch exceptions in API layer; return generic error messages; log details server-side only |
| Not rate-limiting dashboard/export APIs | Denial of service via repeated heavy dashboard loads; memory exhaustion | Implement rate limiting per user per endpoint (Frappe's rate_limit decorator or custom middleware) |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Dashboard shows stale cached data with no indication | VC makes decisions on data that is 15 minutes old without knowing | Show "Last updated: X minutes ago" timestamp on every dashboard; add manual refresh button |
| Export button with no progress feedback | User clicks export, nothing happens for 30 seconds, clicks again (spawning duplicate jobs) | Show immediate "Preparing your report..." spinner; disable button; use background job with progress notification |
| All dashboard data loads before any widget renders | User stares at blank page for 5 seconds | Render widget skeletons immediately; load each widget independently; show data as it arrives |
| Role-based portal with no fallback for missing data | Faculty with no courses assigned sees empty dashboard with no explanation | Show contextual empty states: "No courses assigned for this semester. Contact your HOD." |
| Drill-down navigation loses filter context | User filters by department, drills into a student, presses back, filters are gone | Persist filter state in URL query parameters; restore on back navigation |
| Charts with too many data points on mobile | 12-month trend chart is unreadable on phone screen | Responsive chart configs: show 6 months on mobile, 12 on desktop; use horizontal scroll for tables |

## "Looks Done But Isn't" Checklist

- [ ] **Dashboard permissions:** Verify that a Student-role user CANNOT call any management dashboard API. Test with `curl` using a student session cookie.
- [ ] **Parent data isolation:** Verify Parent A cannot access Student B's data by changing the student parameter in API calls.
- [ ] **Faculty department scoping:** Verify faculty can only see their own department's data, not other departments.
- [ ] **HOD elevation:** Verify HOD sees only their department's faculty/students, not the entire university (unless explicitly granted).
- [ ] **CSRF on POST exports:** Verify that export/download endpoints require a valid CSRF token and fail without it.
- [ ] **Dashboard under load:** Load test with 20 concurrent dashboard viewers. Verify response times stay under 3 seconds and no worker crashes.
- [ ] **Export with 5000+ rows:** Test PDF and Excel export with realistic data volumes. Verify worker memory stays under 300MB.
- [ ] **Session expiry in SPA:** Leave the portal idle for 2+ hours, then navigate. Verify graceful redirect to login, not a cryptic error.
- [ ] **Mobile dashboard rendering:** Verify all charts and tables are usable on a 375px-wide viewport.
- [ ] **Cross-app data consistency:** Verify student count on dashboard matches `frappe.db.count("Student")` from the desk. Same for fee totals.
- [ ] **Mock data removal:** Search codebase for mock/fallback data. Verify NONE ships to production -- it should throw errors instead.
- [ ] **SQL injection audit:** Search all analytics Python files for `query.replace(`, f-string SQL, or string concatenation in SQL. Zero results required.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| SQL injection in dashboard engine | HIGH | Immediate hotfix to parameterize all queries; audit all query paths; check DB for evidence of exploitation; rotate all credentials if breach suspected |
| Permission bypass on dashboard APIs | MEDIUM | Add role checks to all endpoints; audit access logs for unauthorized dashboard access; revoke any sessions of non-authorized users |
| N+1 query performance | LOW | Rewrite queries incrementally per-widget; add Redis caching as immediate band-aid; no data loss involved |
| Parent data leak (IDOR) | HIGH | Patch APIs immediately; audit access logs to identify if cross-student data was accessed; notify affected users per compliance requirements |
| Export OOM crashes | MEDIUM | Switch to background job pattern; add row limits as immediate stopgap; increase container memory as temporary mitigation |
| Cross-app data inconsistency | MEDIUM | Run verification scripts; document known discrepancies; add reconciliation checks to scheduled tasks; dashboards show "data as of" caveat |
| Vue SPA auth race condition | LOW | Implement cached auth check; add global 401 interceptor; minimal user impact during fix |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| SQL injection in dashboard engine | Phase 1: Foundation/Verification | Zero instances of string interpolation in SQL across all analytics code |
| Missing permission checks | Phase 1: Foundation/Verification | Every `@frappe.whitelist()` in analytics has a corresponding role check; automated test suite for permission enforcement |
| N+1 query patterns | Phase 2: Dashboard Implementation | Dashboard load fires <15 DB queries total; response time <2 seconds with production-scale data |
| Vue SPA auth overhead | Phase 2: Portal Unification | Auth check fires once on app load and on 401, not on every route change; measure with network tab |
| Cross-app data inconsistency | Phase 1: Cross-App Verification | Verification script runs green; student/faculty/fee counts match across all query paths |
| Parent data isolation (IDOR) | Phase 3: Parent Portal | Integration tests prove Parent A cannot access Student B's data; penetration test pass |
| Report export crashes | Phase 4: Export & Reports | Export of 5000-row report completes in <60 seconds via background job; worker memory stays under 300MB |
| Mock data in production | Phase 1: Foundation | CI check that fails if mock/fallback data patterns exist outside of test files |
| Dashboard render blocking | Phase 2: Dashboard Frontend | Each widget loads independently; skeleton UI shows within 200ms of page load |
| Stale cache without indication | Phase 2: Dashboard Frontend | Every dashboard shows "Last updated" timestamp; manual refresh button present |

## Sources

- [ERPNext Performance Tuning Wiki](https://github.com/frappe/erpnext/wiki/ERPNext-Performance-Tuning) -- database tuning, indexing, query optimization
- [Scaling ERPNext: Query Optimization Techniques](https://medium.com/@abdelwahab.00964/scaling-erpnext-query-optimization-techniques-for-high-performance-frappe-apps-6aa4b6bb5b20) -- frappe.db.sql patterns, aggregation
- [Frappe Security Bulletin](https://frappe.io/security-bulletin) -- CVEs for SQL injection, permission bypass in whitelisted methods
- [Frappe Forum: Permission Bypass Bug](https://discuss.frappe.io/t/bug-user-can-view-data-even-when-they-dont-have-permission/43843) -- report view URL manipulation bypassing permissions
- [MariaDB Slow Queries in Frappe Cloud](https://docs.frappe.io/cloud/faq/mariadb-slow-queries-in-your-site) -- slow query detection
- [DB Performance Tuning - Frappe Cloud Docs](https://docs.frappe.io/cloud/performance-tuning) -- innodb_buffer_pool_size, monitoring
- Existing codebase analysis: `dashboard_engine.py` (SQL injection), `executive_dashboard.py` (N+1 queries, missing permissions), `portal_api.py` (auth patterns), `useAuth.js` / `useFrappe.js` (CSRF handling, auth guard)

---
*Pitfalls research for: University ERP Dashboards, Analytics & Role-Based Portals*
*Researched: 2026-03-17*
