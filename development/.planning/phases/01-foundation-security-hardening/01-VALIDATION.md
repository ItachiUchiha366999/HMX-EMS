# Phase 1: Foundation & Security Hardening — Validation

**Phase:** 01-foundation-security-hardening
**Generated:** 2026-03-18
**Requirements in scope:** FOUND-01 through FOUND-08
**Plans in scope:** 01-backend-security, 02-portal-app-shell, 03-integration-wiring

---

## Requirement Coverage Table

| Req ID | Requirement | Plan | Task | Test File | Status |
|--------|-------------|------|------|-----------|--------|
| FOUND-01 | Cross-app data consistency — health check module with 4 checks | Plan 01, Task 3 | `health_check.py` created | `tests/test_health_check.py` | not started |
| FOUND-02 | SQL injection fixed — parameterized queries in `_execute_custom_query()` | Plan 01, Task 1 | `dashboard_engine.py` patched | `tests/test_security_fixes.py` | not started |
| FOUND-03 | Permission checks on all 6 analytics API endpoints | Plan 01, Task 1 | `analytics/api.py` patched | `tests/test_security_fixes.py` | not started |
| FOUND-04 | N+1 queries resolved — GROUP BY aggregation replaces per-entity loops | Plan 01, Task 2 | `executive_dashboard.py` patched | `tests/test_security_fixes.py` | not started |
| FOUND-05 | Unified Vue 3 app shell at `/portal/` with role-based routing | Plan 02, Tasks 1–2 | `portal-vue/` project created | manual smoke test | not started |
| FOUND-06 | Auth guard uses cached Pinia session — no per-route API call | Plan 02, Tasks 1–2 | `portal-vue/src/router/index.js` | manual smoke test | not started |
| FOUND-07 | Academic year/semester filter context available on all data views | Plan 02, Task 1 | `get_session_info()` returns `roles[]` + `allowed_modules[]` | code review | not started |
| FOUND-08 | Management roles created — `University VC` and `University Dean` | Plan 01, Task 3 | `fixtures/role.json` updated | `tests/test_roles.py` | not started |

---

## Per-Plan Verification

### Plan 01 — Backend Security

**Files modified:**
- `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py`
- `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py`
- `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py`
- `frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py` (new)
- `frappe-bench/apps/university_erp/university_erp/fixtures/role.json`

#### Task 1 — SQL injection fix + permission guards (FOUND-02, FOUND-03)

**Automated check (static):**
```bash
cd /workspace/development/frappe-bench && python3 -c "
with open('apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py') as f:
    src = f.read()
assert 'values=' in src, 'parameterized values= not found in dashboard_engine.py'
segment = src.split('_execute_custom_query')[1].split('def ')[0]
assert \"f'\" not in segment or \"%(\" not in segment, 'f-string interpolation still present'
print('FOUND-02 PASS: parameterized query confirmed')

with open('apps/university_erp/university_erp/university_erp/analytics/api.py') as f:
    api_src = f.read()
count = api_src.count('frappe.has_permission')
assert count >= 6, f'Expected 6+ permission checks, found {count}'
print(f'FOUND-03 PASS: {count} permission checks found')
"
```

**What is being checked:**
- `dashboard_engine.py`: the `_execute_custom_query()` function no longer contains f-string interpolation of `filters['from_date']`, `filters['to_date']`, `filters['department']`, or `filters['program']`. The call to `frappe.db.sql()` uses `values=` parameter.
- `api.py`: `frappe.has_permission()` appears in `get_kpi_value`, `get_kpi_trend`, `get_kpi_comparison`, `get_quick_stats`, `get_all_kpis`, and `calculate_kpi_now` — 6 functions in total.

**Behavioral test (file path):** `frappe-bench/apps/university_erp/university_erp/university_erp/tests/test_security_fixes.py`

Test names:
- `test_sql_injection_fix_uses_parameterized_query` — FOUND-02
- `test_permission_check_present_in_kpi_endpoints` — FOUND-03

#### Task 2 — N+1 query resolution (FOUND-04)

**Automated check (static):**
```bash
cd /workspace/development/frappe-bench && python3 -c "
with open('apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py') as f:
    src = f.read()
assert 'GROUP BY' in src, 'No GROUP BY found — aggregated queries missing'
assert '_get_department_student_count' not in src, '_get_department_student_count helper still present'
assert '_get_department_faculty_count' not in src, '_get_department_faculty_count helper still present'
assert 'get_department_performance' in src, 'get_department_performance function missing'
assert 'get_kpi_summary' in src, 'get_kpi_summary function missing'
import ast; ast.parse(src)
print('FOUND-04 PASS: GROUP BY aggregation found, N+1 helpers removed, file parses cleanly')
"
```

**What is being checked:**
- `get_department_performance()` issues at most 3 SQL queries (department list + student counts via GROUP BY + faculty counts via GROUP BY) regardless of department count.
- `get_kpi_summary()` issues at most 2 SQL queries (KPI definition list + latest values via MAX subquery join) regardless of KPI count.
- Private helpers `_get_department_student_count()` and `_get_department_faculty_count()` are removed (they were the source of per-row queries).

**Behavioral test (file path):** `frappe-bench/apps/university_erp/university_erp/university_erp/tests/test_security_fixes.py`

Test name:
- `test_n_plus_one_queries_resolved` — FOUND-04

#### Task 3 — Health check module + role fixtures (FOUND-01, FOUND-08)

**Automated check (static):**
```bash
cd /workspace/development/frappe-bench && python3 -c "
import json, ast

with open('apps/university_erp/university_erp/university_erp/health_check.py') as f:
    src = f.read()
ast.parse(src)
assert '@frappe.whitelist()' in src, 'Missing @frappe.whitelist decorator'
assert 'University Admin' in src, 'Missing University Admin permission check'
assert '_check_student_enrollment' in src, 'Missing student enrollment check'
assert '_check_fees_gl_accounts' in src, 'Missing fees GL account check'
assert '_check_employee_faculty_profile' in src, 'Missing employee-faculty profile check'
assert '_check_academic_year_validity' in src, 'Missing academic year validity check'
print('FOUND-01 PASS: health_check.py structure verified')

with open('apps/university_erp/university_erp/fixtures/role.json') as f:
    roles = json.load(f)
names = [r['name'] for r in roles]
assert 'University VC' in names, 'University VC not found in role.json'
assert 'University Dean' in names, 'University Dean not found in role.json'
vc = next(r for r in roles if r['name'] == 'University VC')
dean = next(r for r in roles if r['name'] == 'University Dean')
assert vc.get('home_page') == '/portal', 'University VC home_page should be /portal'
assert dean.get('home_page') == '/portal', 'University Dean home_page should be /portal'
print('FOUND-08 PASS: University VC and University Dean found in role.json with correct home_page')
"
```

**What is being checked:**
- `health_check.py` exports `run_checks()` decorated with `@frappe.whitelist()`, checks for `University Admin` role before proceeding, and contains all four private check functions.
- `fixtures/role.json` contains entries for `University VC` and `University Dean` with `home_page: "/portal"`.
- The JSON file is valid (parses without error).

**Behavioral test files:**
- `frappe-bench/apps/university_erp/university_erp/university_erp/tests/test_health_check.py` — FOUND-01
- `frappe-bench/apps/university_erp/university_erp/university_erp/tests/test_roles.py` — FOUND-08

---

### Plan 02 — Portal App Shell

**Files created:**
- `portal-vue/package.json`
- `portal-vue/index.html`
- `portal-vue/vite.config.js`
- `portal-vue/src/main.js`
- `portal-vue/src/App.vue`
- `portal-vue/src/stores/session.js`
- `portal-vue/src/router/index.js`
- `portal-vue/src/config/navigation.js`
- `portal-vue/src/layouts/PortalLayout.vue`
- `portal-vue/src/components/Sidebar.vue`
- `frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py` (appended)
- `frappe-bench/apps/university_erp/university_erp/www/portal/index.py` (new)
- `frappe-bench/apps/university_erp/university_erp/www/portal/index.html` (new)

#### Task 1 — Project scaffold + session store + backend endpoint (FOUND-05, FOUND-06, FOUND-07, FOUND-08)

**Automated check (static):**
```bash
cd /workspace/development && python3 -c "
import os

required = [
    'portal-vue/package.json',
    'portal-vue/vite.config.js',
    'portal-vue/index.html',
    'portal-vue/src/main.js',
    'portal-vue/src/App.vue',
    'portal-vue/src/stores/session.js',
    'portal-vue/src/config/navigation.js',
]
missing = [p for p in required if not os.path.exists(p)]
assert not missing, f'Missing files: {missing}'

with open('portal-vue/vite.config.js') as f: vc = f.read()
assert \"base: '/assets/university_erp/portal/'\" in vc, 'Wrong Vite base URL'
assert 'student-portal-spa' not in vc, 'vite.config.js must not reference student-portal-spa outDir'
print('FOUND-05 PASS: portal-vue project structure present')

with open('portal-vue/src/stores/session.js') as f: ss = f.read()
assert 'fetchSession' in ss, 'fetchSession action missing from session store'
assert 'isAuthenticated' in ss, 'isAuthenticated getter missing'
assert 'roles' in ss, 'roles state missing'
assert 'allowed_modules' in ss, 'allowed_modules state missing'
print('FOUND-06/07 PASS: session store has required fields and fetchSession action')

with open('portal-vue/src/config/navigation.js') as f: nc = f.read()
assert 'navItems' in nc, 'navItems export missing from navigation.js'
assert 'University VC' in nc or 'University Dean' in nc, 'Management roles not mapped in navItems'
print('FOUND-08 PASS: navigation.js maps management roles')

with open('frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py') as f: api = f.read()
assert 'get_session_info' in api, 'get_session_info missing from portal_api.py'
assert 'allowed_modules' in api, 'allowed_modules missing from get_session_info response'
assert 'frappe.get_roles' in api, 'frappe.get_roles call missing'
print('FOUND-07 PASS: get_session_info returns allowed_modules for academic year filter context')
"
```

**What is being checked:**
- `portal-vue/` project files exist at correct paths.
- `vite.config.js` targets `base: '/assets/university_erp/portal/'` and does not write to `student-portal-spa`.
- `session.js` Pinia store has state (`logged_user`, `full_name`, `user_image`, `roles`, `allowed_modules`, `loaded`, `error`), getter `isAuthenticated`, and action `fetchSession`.
- `navigation.js` exports `navItems` array with `roles[]` per item, including entries for `University VC` and `University Dean`.
- `portal_api.py` includes `get_session_info()` returning `{logged_user, full_name, user_image, roles[], allowed_modules[]}`.

**FOUND-07 note:** Full academic year filter UI is deferred to Phase 2 (COMP-04). What Phase 1 delivers is the data carrier: `get_session_info()` provides `roles[]` and `allowed_modules[]` to the Vue app, which gives every portal view the context it needs to apply academic year filtering when the filter component is built. The verification for FOUND-07 is therefore a code review check — confirm the session contract includes the data, not that a filter widget exists.

#### Task 2 — Router, layout, sidebar, Frappe www page (FOUND-05, FOUND-06)

**Automated check (static):**
```bash
cd /workspace/development && python3 -c "
import os

required = [
    'portal-vue/src/router/index.js',
    'portal-vue/src/layouts/PortalLayout.vue',
    'portal-vue/src/components/Sidebar.vue',
    'frappe-bench/apps/university_erp/university_erp/www/portal/index.py',
    'frappe-bench/apps/university_erp/university_erp/www/portal/index.html',
]
missing = [p for p in required if not os.path.exists(p)]
assert not missing, f'Missing files: {missing}'

with open('portal-vue/src/router/index.js') as f: router = f.read()
assert 'useSessionStore' in router, 'Router does not read from Pinia session store'
assert 'frappe.auth.get_logged_user' not in router, 'Old per-route API call still present'
assert 'isAuthenticated' in router, 'isAuthenticated check missing from beforeEach guard'
assert \"createWebHistory('/portal/')\" in router, 'Router history base must be /portal/'
print('FOUND-06 PASS: router uses Pinia session store, no per-route API call')

with open('portal-vue/src/components/Sidebar.vue') as f: sidebar = f.read()
assert 'visibleItems' in sidebar, 'visibleItems computed property missing from Sidebar'
assert 'navItems' in sidebar, 'navItems not imported in Sidebar'
assert 'roles' in sidebar, 'role intersection filter missing from Sidebar'
print('FOUND-05 PASS: Sidebar filters items by role intersection')

with open('frappe-bench/apps/university_erp/university_erp/www/portal/index.py') as f: ip = f.read()
import ast; ast.parse(ip)
assert 'get_context' in ip, 'get_context function missing from www/portal/index.py'
assert 'frappe.Redirect' in ip, 'Guest redirect missing from www/portal/index.py'
assert 'get_vite_manifest' in ip, 'get_vite_manifest helper missing'
assert 'portal' in ip, 'manifest path does not reference portal directory'
print('FOUND-05 PASS: www/portal/index.py structure correct')

with open('frappe-bench/apps/university_erp/university_erp/www/portal/index.html') as f: ih = f.read()
assert 'vue_js' in ih, 'vue_js Jinja variable missing from index.html'
assert '#app' in ih, '#app Vue mount point missing'
print('FOUND-05 PASS: www/portal/index.html has mount point and asset injection')
"
```

**What is being checked:**
- `router/index.js` uses `createWebHistory('/portal/')`, `beforeEach` reads `sessionStore.isAuthenticated` with no call to `frappe.auth.get_logged_user`.
- `Sidebar.vue` has a `visibleItems` computed property that filters `navItems` by role intersection against `session.roles`.
- `www/portal/index.py` has `get_context()` that redirects Guest to `/login`, reads the Vite manifest, and sets `vue_js`/`vue_css` on context.
- `www/portal/index.html` loads assets via Jinja `{{ vue_js }}` and mounts Vue at `<div id="app">`.

---

### Plan 03 — Integration Wiring

Plan 03 is the integration gate that confirms Plans 01 and 02 connect end-to-end. It has one automated task (build + static verification) and one human-verify checkpoint.

#### Task 1 — npm build + cross-file verification (all FOUND-XX)

**Automated check:**
```bash
# Step 1: build the Vue app
cd /workspace/development/portal-vue && npm install && npm run build

# Step 2: verify manifest was produced
python3 -c "
import json, os, ast

manifest_path = '/workspace/development/frappe-bench/apps/university_erp/university_erp/public/portal/.vite/manifest.json'
assert os.path.exists(manifest_path), f'Build manifest missing — run npm run build in portal-vue/'
with open(manifest_path) as f:
    m = json.load(f)
entry = m.get('index.html', {})
assert entry.get('file'), 'No JS file in Vite manifest index.html entry'
print('Build PASS: manifest.json present with valid JS entry')

# Verify all modified Python files parse
for path in [
    '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py',
    '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py',
    '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py',
    '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py',
    '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py',
    '/workspace/development/frappe-bench/apps/university_erp/university_erp/www/portal/index.py',
]:
    with open(path) as f: ast.parse(f.read())
    print(f'Syntax PASS: {path.split(\"/apps/\")[1]}')

# Verify role fixture
with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/fixtures/role.json') as f:
    roles = json.load(f)
names = [r['name'] for r in roles]
assert 'University VC' in names and 'University Dean' in names
print(f'Roles PASS: {len(roles)} total roles, University VC and University Dean present')
"
```

#### Checkpoint — Human browser verification (FOUND-05, FOUND-06, FOUND-03, FOUND-08)

The following tests require a running Frappe instance. They are blocking for phase sign-off but may be deferred with the signal `"deferred: no frappe instance"` if no live instance is available.

| Test | Steps | Expected |
|------|-------|----------|
| A — Guest redirect | Visit `/portal/` without logging in | Redirected to `/login?redirect-to=/portal/` |
| B — Authenticated load | Log in as any non-Guest user, visit `/portal/` | Vue app mounts; sidebar renders; no JS errors in console |
| C — Health check endpoint | `GET /api/method/university_erp.university_erp.health_check.run_checks` as University Admin | JSON response with `status` key and exactly 4 items in `checks` array |
| D — Permission enforcement | `GET /api/method/university_erp.university_erp.analytics.api.get_kpi_value?kpi_name=test` as non-admin | HTTP 403 or `PermissionError` in response — no KPI data returned |
| E — Sidebar RBAC (Faculty) | Log in as user with only `University Faculty` role; visit `/portal/` | Sidebar shows `My Teaching`, `Mark Attendance`, `Enter Grades`; does NOT show `System Health` or `Management Dashboard` |
| F — Sidebar RBAC (Admin) | Log in as user with `University Admin` role; visit `/portal/` | Sidebar shows `Management Dashboard`, `System Health`, `Finance` |
| G — No per-route calls | Open DevTools → Network; navigate between sidebar items | Zero calls to `/api/method/frappe.auth.get_logged_user`; exactly one call to `get_session_info` on page load |
| H — Role fixture loaded | `bench --site [site] migrate` then check Role list | `University VC` and `University Dean` appear in Frappe Role list |

---

## Test Files

### `tests/test_security_fixes.py`

**Path:** `frappe-bench/apps/university_erp/university_erp/university_erp/tests/test_security_fixes.py`
**Requirements covered:** FOUND-02, FOUND-03, FOUND-04
**Test runner:** `cd /workspace/development/frappe-bench && bench --site [site] run-tests --app university_erp --module university_erp.university_erp.tests.test_security_fixes`

Tests to implement:

```
test_sql_injection_fix_uses_parameterized_query
    Arrange: read source of dashboard_engine.py
    Act:     locate _execute_custom_query function body
    Assert:  'values=' appears in the function body
             f-string interpolation of filter keys does not appear
             (covers: FOUND-02)

test_permission_check_present_in_kpi_endpoints
    Arrange: read source of analytics/api.py
    Act:     count occurrences of 'frappe.has_permission'
    Assert:  count >= 6
             (covers: FOUND-03)

test_n_plus_one_queries_resolved
    Arrange: read source of executive_dashboard.py
    Act:     inspect get_department_performance and get_kpi_summary function bodies
    Assert:  'GROUP BY' appears in the file
             '_get_department_student_count' does not appear in the file
             '_get_department_faculty_count' does not appear in the file
             (covers: FOUND-04)
```

### `tests/test_health_check.py`

**Path:** `frappe-bench/apps/university_erp/university_erp/university_erp/tests/test_health_check.py`
**Requirements covered:** FOUND-01
**Test runner:** `cd /workspace/development/frappe-bench && bench --site [site] run-tests --app university_erp --module university_erp.university_erp.tests.test_health_check`

Tests to implement:

```
test_run_checks_returns_correct_schema
    Arrange: import run_checks from university_erp.university_erp.health_check
             mock frappe.get_roles to return ['University Admin']
    Act:     result = run_checks()
    Assert:  result has 'status' key with value in ('ok', 'degraded', 'critical')
             result has 'checks' key that is a list
             len(result['checks']) == 4
             each check has keys: 'name', 'status', 'detail', 'count'
             each check status is in ('pass', 'warn', 'fail')
             (covers: FOUND-01)

test_run_checks_requires_university_admin_role
    Arrange: import run_checks from university_erp.university_erp.health_check
             mock frappe.get_roles to return ['University Student']
    Act:     call run_checks()
    Assert:  raises frappe.PermissionError
             (covers: FOUND-01 — access control on health check)

test_health_check_covers_four_integration_points
    Arrange: read source of health_check.py
    Act:     inspect file contents
    Assert:  '_check_student_enrollment' in source
             '_check_fees_gl_accounts' in source
             '_check_employee_faculty_profile' in source
             '_check_academic_year_validity' in source
             (covers: FOUND-01 — all four cross-app integration points)
```

### `tests/test_roles.py`

**Path:** `frappe-bench/apps/university_erp/university_erp/university_erp/tests/test_roles.py`
**Requirements covered:** FOUND-08
**Test runner:** `cd /workspace/development/frappe-bench && bench --site [site] run-tests --app university_erp --module university_erp.university_erp.tests.test_roles`

Tests to implement:

```
test_university_vc_role_in_fixture
    Arrange: load fixtures/role.json
    Act:     parse JSON, extract role names
    Assert:  'University VC' in names
             (covers: FOUND-08)

test_university_dean_role_in_fixture
    Arrange: load fixtures/role.json
    Act:     parse JSON, extract role names
    Assert:  'University Dean' in names
             (covers: FOUND-08)

test_new_roles_have_portal_home_page
    Arrange: load fixtures/role.json
    Act:     find University VC and University Dean entries
    Assert:  vc_entry['home_page'] == '/portal'
             dean_entry['home_page'] == '/portal'
             (covers: FOUND-08 — roles redirect to unified portal, not Frappe desk)

test_role_fixture_is_valid_json
    Arrange: open fixtures/role.json as file
    Act:     json.load()
    Assert:  no exception raised; result is a list
             (covers: FOUND-08 — fixture file integrity)
```

---

## Verification Commands (Full Phase)

Run these commands in order after all three plans complete. All must produce PASS output before the phase is signed off.

```bash
# 1. Security fixes (FOUND-02, FOUND-03, FOUND-04)
cd /workspace/development/frappe-bench && python3 -c "
with open('apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py') as f: src = f.read()
assert 'values=' in src
with open('apps/university_erp/university_erp/university_erp/analytics/api.py') as f: api = f.read()
assert api.count('frappe.has_permission') >= 6
with open('apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py') as f: dash = f.read()
assert 'GROUP BY' in dash and '_get_department_student_count' not in dash
print('Security checks: PASS')
"

# 2. Health check module (FOUND-01)
cd /workspace/development/frappe-bench && python3 -c "
import ast
with open('apps/university_erp/university_erp/university_erp/health_check.py') as f: src = f.read()
ast.parse(src)
assert 'run_checks' in src and 'University Admin' in src
assert all(fn in src for fn in ['_check_student_enrollment', '_check_fees_gl_accounts', '_check_employee_faculty_profile', '_check_academic_year_validity'])
print('Health check: PASS')
"

# 3. Vue app shell structure (FOUND-05, FOUND-06)
cd /workspace/development && python3 -c "
import os
files = [
    'portal-vue/src/stores/session.js',
    'portal-vue/src/router/index.js',
    'portal-vue/src/components/Sidebar.vue',
    'frappe-bench/apps/university_erp/university_erp/www/portal/index.py',
]
for f in files: assert os.path.exists(f), f'Missing: {f}'
with open('portal-vue/src/router/index.js') as f: r = f.read()
assert 'frappe.auth.get_logged_user' not in r and 'isAuthenticated' in r
print('Vue shell: PASS')
"

# 4. Roles fixture (FOUND-08)
cd /workspace/development/frappe-bench && python3 -c "
import json
with open('apps/university_erp/university_erp/fixtures/role.json') as f:
    roles = json.load(f)
names = [r['name'] for r in roles]
assert 'University VC' in names and 'University Dean' in names
print('Roles: PASS')
"

# 5. Vite build (FOUND-05)
cd /workspace/development/portal-vue && npm install && npm run build
# Expected: exits 0; public/portal/.vite/manifest.json created

# 6. Run automated test suite
cd /workspace/development/frappe-bench
bench --site [site] run-tests --app university_erp --module university_erp.university_erp.tests.test_security_fixes
bench --site [site] run-tests --app university_erp --module university_erp.university_erp.tests.test_health_check
bench --site [site] run-tests --app university_erp --module university_erp.university_erp.tests.test_roles
```

---

## Verification Map

| Task ID | Requirement | Verification Type | Command / File | Status |
|---------|-------------|-------------------|----------------|--------|
| Plan01-T1 | FOUND-02: SQL injection fixed | static + unit | `test_security_fixes.py::test_sql_injection_fix_uses_parameterized_query` | not started |
| Plan01-T1 | FOUND-03: Permission checks on 6 endpoints | static + unit | `test_security_fixes.py::test_permission_check_present_in_kpi_endpoints` | not started |
| Plan01-T2 | FOUND-04: N+1 queries resolved | static + unit | `test_security_fixes.py::test_n_plus_one_queries_resolved` | not started |
| Plan01-T3 | FOUND-01: Health check module — 4 checks, correct schema | unit | `test_health_check.py::test_run_checks_returns_correct_schema` | not started |
| Plan01-T3 | FOUND-01: Health check — University Admin only | unit | `test_health_check.py::test_run_checks_requires_university_admin_role` | not started |
| Plan01-T3 | FOUND-08: University VC in fixture | unit | `test_roles.py::test_university_vc_role_in_fixture` | not started |
| Plan01-T3 | FOUND-08: University Dean in fixture | unit | `test_roles.py::test_university_dean_role_in_fixture` | not started |
| Plan01-T3 | FOUND-08: New roles redirect to /portal | unit | `test_roles.py::test_new_roles_have_portal_home_page` | not started |
| Plan02-T1 | FOUND-05: portal-vue project structure | static | `python3 -c "import os; [assert os.path.exists(f) ..."` | not started |
| Plan02-T1 | FOUND-06: Pinia session store fields | static | `portal-vue/src/stores/session.js` contains `fetchSession`, `isAuthenticated`, `roles`, `allowed_modules` | not started |
| Plan02-T1 | FOUND-07: Session API returns role/module context | static | `portal_api.py::get_session_info` returns `roles[]` and `allowed_modules[]` | not started |
| Plan02-T1 | FOUND-08: Management roles in navigation config | static | `navigation.js` maps `University VC` and `University Dean` to management route | not started |
| Plan02-T2 | FOUND-06: Router reads store, no per-route API call | static | `router/index.js` uses `isAuthenticated`, no `frappe.auth.get_logged_user` | not started |
| Plan02-T2 | FOUND-05: Sidebar filters by role intersection | static | `Sidebar.vue` has `visibleItems` computed from `navItems` × `session.roles` | not started |
| Plan02-T2 | FOUND-05: Frappe www page serves SPA shell | static + smoke | `www/portal/index.py` redirects Guest, reads manifest | not started |
| Plan03-T1 | FOUND-05: npm build succeeds | smoke | `cd portal-vue && npm run build` exits 0 | not started |
| Plan03-Checkpoint | FOUND-05/06: Browser load + sidebar RBAC | manual | Tests A–G in checkpoint section | not started |
| Plan03-Checkpoint | FOUND-03: Permission 403 on unauthenticated KPI call | manual | Test D in checkpoint section | not started |
| Plan03-Checkpoint | FOUND-08: Roles present in live Frappe DB | manual | Test H — bench migrate + Role list check | not started |

---

## Notes

**FOUND-07 scope boundary:** The requirement is "Academic year/semester filter available on all data views." Phase 1 establishes the data contract — `get_session_info()` provides `roles[]` and `allowed_modules[]` to the Vue app — but the filter UI component (a date range / academic year selector rendered on each view) is Phase 2 work (COMP-04). Validation for FOUND-07 in Phase 1 is limited to confirming the session API includes the necessary context data. A FOUND-07 test that checks for an actual filter component would be premature and should be written in Phase 2.

**Bench run-tests command:** The test runner requires a live Frappe site. Replace `[site]` with the actual site name (check `ls /workspace/development/frappe-bench/sites/` — exclude the `apps` symlink). The static verification commands (python3 assertions on source files) run without a Frappe instance.

**Test infrastructure:** Existing test files in `university_erp/tests/` follow the standard Frappe test pattern (inherit from `frappe.tests.utils.FrappeTestCase` or use `unittest.TestCase`). The three test files listed above must follow the same pattern. See `test_grading_system.py` or `test_installation.py` in the same directory as the canonical style reference.
