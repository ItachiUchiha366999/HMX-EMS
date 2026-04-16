---
phase: 01-foundation-security-hardening
plan: 03
type: execute
wave: 2
depends_on:
  - 01-foundation-security-hardening/01-backend-security-PLAN.md
  - 01-foundation-security-hardening/02-portal-app-shell-PLAN.md
files_modified:
  - frappe-bench/apps/university_erp/university_erp/www/portal/index.py
autonomous: false
requirements:
  - FOUND-01
  - FOUND-02
  - FOUND-03
  - FOUND-04
  - FOUND-05
  - FOUND-06
  - FOUND-07
  - FOUND-08

must_haves:
  truths:
    - "Visiting /portal/ as Guest redirects to the Frappe login page with redirect-to parameter"
    - "A logged-in University Admin user can visit /portal/ and see a sidebar with System Health link"
    - "A logged-in University Faculty user sees My Teaching / Mark Attendance / Enter Grades in sidebar, NOT System Health"
    - "GET /api/method/university_erp.university_erp.health_check.run_checks as University Admin returns JSON with exactly 4 check entries"
    - "Calling a KPI endpoint (e.g. get_kpi_value) as a non-admin user returns a permission error, not data"
    - "University VC and University Dean roles exist in the Frappe Role list after bench migrate"
  artifacts:
    - path: "frappe-bench/apps/university_erp/university_erp/www/portal/index.py"
      provides: "Verified SPA mount with correct manifest path"
      contains: "get_context"
    - path: "frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py"
      provides: "Live-callable health check module"
      exports: ["run_checks"]
  key_links:
    - from: "/portal/ URL"
      to: "www/portal/index.py get_context()"
      via: "Frappe www page routing by directory name"
      pattern: "www/portal"
    - from: "www/portal/index.py"
      to: "public/portal/.vite/manifest.json"
      via: "get_vite_manifest() reading built assets"
      pattern: "manifest.json"
    - from: "Vite build output"
      to: "Frappe static file serving"
      via: "/assets/university_erp/portal/ URL path"
      pattern: "/assets/university_erp/portal/"
---

<objective>
Wire Plans 01 and 02 together: build the Vue app, verify Frappe routes the /portal/ URL correctly, confirm the health-check endpoint is callable, confirm role-based sidebar filtering works with real Frappe roles, and run the full integration smoke test.

Purpose: Plans 01 and 02 create isolated pieces. This plan confirms they connect: the built JS lands where Frappe serves it, the www page loads the correct manifest, the backend endpoints enforce access, and the sidebar filters correctly for different user types.

Output:
- npm build artifacts in public/portal/
- Confirmed /portal/ Frappe routing
- Verified health-check API response
- Verified RBAC filtering in the sidebar
- Human-verified browser check that the full flow works end-to-end
</objective>

<execution_context>
@/workspace/development/.claude/get-shit-done/workflows/execute-plan.md
@/workspace/development/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/workspace/development/.planning/ROADMAP.md
@/workspace/development/.planning/REQUIREMENTS.md
@/workspace/development/.planning/phases/01-foundation-security-hardening/01-CONTEXT.md
@/workspace/development/.planning/phases/01-foundation-security-hardening/01-RESEARCH.md

<interfaces>
<!-- Key integration points confirmed during planning -->

Frappe www page routing convention:
  - File: university_erp/www/portal/index.py
  - URL served at: /portal  and /portal/<subpath>
  - No explicit registration needed — Frappe scans www/ directories automatically
  - The SPA handles sub-paths via Vue Router's createWebHistory('/portal/')

Vite build → Frappe asset serving:
  - Vite outDir: university_erp/public/portal/
  - Frappe serves from: /assets/university_erp/portal/
  - manifest.json location: public/portal/.vite/manifest.json
  - Manifest entry key: "index.html"

Health check endpoint:
  - Module path: university_erp.university_erp.health_check.run_checks
  - URL: GET /api/method/university_erp.university_erp.health_check.run_checks
  - Auth required: "University Admin" role

Analytics permission check:
  - URL to test: GET /api/method/university_erp.university_erp.analytics.api.get_kpi_value?kpi_name=test
  - Expected for non-admin: 403 or frappe.PermissionError

Role fixture sync:
  - bench command: bench --site [site] migrate
  - OR: bench --site [site] reload-doc Role
  - Verify: Role list in Frappe desk shows "University VC" and "University Dean"

Frappe bench location: /workspace/development/frappe-bench
Site name: check `ls frappe-bench/sites/` — commonly "university.local" or similar
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Build Vue app and verify Frappe integration points</name>
  <files>
    frappe-bench/apps/university_erp/university_erp/www/portal/index.py
  </files>
  <action>
    Run the following verification sequence. Fix any issues found before proceeding to the checkpoint.

    **Step 1 — Install dependencies and build portal-vue:**
    ```bash
    cd /workspace/development/portal-vue
    npm install
    npm run build
    ```
    Expected: build succeeds, `frappe-bench/apps/university_erp/university_erp/public/portal/` is created with:
    - `.vite/manifest.json`
    - `assets/index-[hash].js`
    - `assets/index-[hash].css` (if any)

    If build fails: check for missing `node_modules`, Vue/Pinia version conflicts. The package.json specifies exact versions that were available at project creation time.

    **Step 2 — Verify manifest.json is readable:**
    ```bash
    python3 -c "
    import json
    with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/public/portal/.vite/manifest.json') as f:
        m = json.load(f)
    entry = m.get('index.html', {})
    print('JS entry:', entry.get('file'))
    print('CSS:', entry.get('css', []))
    assert entry.get('file'), 'No JS entry in manifest'
    print('PASS: manifest.json is valid and has JS entry')
    "
    ```

    **Step 3 — Verify Python files all parse cleanly:**
    ```bash
    python3 -c "
    import ast
    files = [
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/www/portal/index.py',
    ]
    for path in files:
        with open(path) as f:
            ast.parse(f.read())
        print(f'PASS: {path.split(\"/apps/\")[1]}')
    "
    ```

    **Step 4 — Verify fixtures/role.json is valid JSON with new roles:**
    ```bash
    python3 -c "
    import json
    with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/fixtures/role.json') as f:
        roles = json.load(f)
    names = [r['name'] for r in roles]
    assert 'University VC' in names, 'University VC missing'
    assert 'University Dean' in names, 'University Dean missing'
    print(f'PASS: {len(roles)} roles in fixture, including University VC and University Dean')
    "
    ```

    **Step 5 — Verify security fixes are in place:**
    ```bash
    python3 -c "
    with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py') as f:
        src = f.read()

    # Check that the vulnerable pattern is gone
    # The f-string interpolation was: f\"'{filters['from_date']}'\"
    assert \"f\"'\" not in src.split('_execute_custom_query')[1].split('def _execute_method')[0], 'f-string interpolation still in _execute_custom_query!'
    assert 'values=' in src, 'Parameterized query (values=) not found'

    with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py') as f:
        api = f.read()
    count = api.count('frappe.has_permission')
    assert count >= 6, f'Expected 6+ permission checks, found {count}'

    with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py') as f:
        dash = f.read()
    assert 'GROUP BY' in dash, 'Aggregated GROUP BY queries not found'
    assert '_get_department_student_count' not in dash, 'N+1 helper still referenced'

    print('PASS: All security fixes verified')
    "
    ```

    **Step 6 — Verify portal-vue structure is complete:**
    ```bash
    python3 -c "
    import os
    required = [
        '/workspace/development/portal-vue/package.json',
        '/workspace/development/portal-vue/vite.config.js',
        '/workspace/development/portal-vue/index.html',
        '/workspace/development/portal-vue/src/main.js',
        '/workspace/development/portal-vue/src/App.vue',
        '/workspace/development/portal-vue/src/stores/session.js',
        '/workspace/development/portal-vue/src/router/index.js',
        '/workspace/development/portal-vue/src/config/navigation.js',
        '/workspace/development/portal-vue/src/layouts/PortalLayout.vue',
        '/workspace/development/portal-vue/src/components/Sidebar.vue',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/www/portal/index.py',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/www/portal/index.html',
        '/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py',
    ]
    missing = [p for p in required if not os.path.exists(p)]
    if missing:
        for p in missing: print(f'MISSING: {p}')
        raise AssertionError(f'{len(missing)} required files missing')
    print(f'PASS: All {len(required)} required files present')
    "
    ```

    If any step fails, fix the issue before continuing to the checkpoint. The most likely issues are:
    - npm build fails: missing dependency version → update package.json versions, re-run npm install
    - Python syntax error: fix the file identified by ast.parse()
    - Missing file: create the file as specified in Plan 01 or 02

    **Note on www/portal/index.py:** If the Vite build output path or manifest structure differs from what get_vite_manifest() expects, update the path in index.py to match actual output. The path is:
    `frappe.get_app_path("university_erp", "public", "portal", ".vite", "manifest.json")`
    This resolves to: `frappe-bench/apps/university_erp/university_erp/public/portal/.vite/manifest.json`
  </action>
  <verify>
    <automated>cd /workspace/development && python3 -c "
import os, json, ast

# Build output
manifest_path = 'frappe-bench/apps/university_erp/university_erp/public/portal/.vite/manifest.json'
assert os.path.exists(manifest_path), f'Build manifest missing at {manifest_path} — run npm run build in portal-vue/'
with open(manifest_path) as f:
    m = json.load(f)
assert m.get('index.html', {}).get('file'), 'No JS file entry in manifest'

# All Python files parse
for path in [
    'frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py',
    'frappe-bench/apps/university_erp/university_erp/www/portal/index.py',
    'frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py',
]:
    with open(path) as f: ast.parse(f.read())

# Role fixture
with open('frappe-bench/apps/university_erp/university_erp/fixtures/role.json') as f:
    roles = json.load(f)
names = [r['name'] for r in roles]
assert 'University VC' in names and 'University Dean' in names

print('PASS: Build artifacts, Python syntax, role fixtures all verified')
"
    </automated>
  </verify>
  <done>
    - npm run build succeeds in portal-vue/
    - public/portal/.vite/manifest.json exists with a valid index.html entry
    - All 6 modified Python files parse without syntax errors
    - fixtures/role.json contains University VC and University Dean
    - All 13 required files exist at their expected paths
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
    Plan 01 completed: SQL injection fix, permission guards on 6 endpoints, N+1 resolution, health_check.py, two new roles in fixtures.
    Plan 02 completed: portal-vue/ project, Pinia session store, Vue Router with boot-time auth guard, Sidebar with role-filtered nav, get_session_info() backend endpoint, www/portal/ Frappe page.
    Task 1 of this plan completed: npm build succeeded, all files verified.
  </what-built>
  <how-to-verify>
    Run these tests in order. Each has a specific expected outcome.

    **Test A — Frappe routing (requires running Frappe instance):**
    1. In a browser, visit `/portal` without being logged in
    2. Expected: redirected to `/login?redirect-to=/portal/` (or similar)
    3. Log in as any non-Guest user
    4. Expected: redirected back to `/portal/` and the Vue app loads (spinning loader or sidebar visible)

    If Frappe is not running locally, skip Test A and confirm the file structure is correct instead:
    ```bash
    ls -la /workspace/development/frappe-bench/apps/university_erp/university_erp/www/portal/
    # Expected: index.py and index.html
    ```

    **Test B — Health check endpoint (requires running Frappe + University Admin user):**
    ```bash
    # Substitute your site name and admin credentials
    curl -s \
      --cookie "sid=YOUR_ADMIN_SESSION_SID" \
      "http://localhost:8000/api/method/university_erp.university_erp.health_check.run_checks" \
      | python3 -m json.tool
    ```
    Expected response structure:
    ```json
    {
      "message": {
        "status": "ok",
        "checks": [
          {"name": "Student \u2194 Program Enrollment", "status": "pass", ...},
          {"name": "Fees \u2194 GL Accounts", "status": "pass", ...},
          {"name": "Employee \u2194 Faculty Profile", "status": "pass", ...},
          {"name": "Academic Year / Term Validity", "status": "pass", ...}
        ]
      }
    }
    ```
    Exactly 4 items in `checks`. Overall `status` is "ok", "degraded", or "critical".

    **Test C — Permission enforcement on analytics API:**
    ```bash
    # Call get_kpi_value as a non-admin user (or unauthenticated)
    curl -s \
      "http://localhost:8000/api/method/university_erp.university_erp.analytics.api.get_kpi_value?kpi_name=test"
    ```
    Expected: HTTP 403 or `{"exc_type": "PermissionError", ...}` — NOT actual KPI data.

    **Test D — Role fixtures (requires running Frappe):**
    ```bash
    cd /workspace/development/frappe-bench
    bench --site $(ls sites/ | grep -v apps | head -1) migrate
    # Then verify:
    bench --site $(ls sites/ | grep -v apps | head -1) execute frappe.get_list --args "['Role', {'filters': [['name', 'like', 'University%']]}]"
    ```
    Expected: list includes "University VC" and "University Dean".

    **Test E — Sidebar role filtering (browser test, requires Vue app loaded):**
    1. Log in as a user with ONLY the "University Faculty" role
    2. Visit /portal/
    3. Expected sidebar items: "My Teaching", "Mark Attendance", "Enter Grades" (NOT "System Health", NOT "Management Dashboard")
    4. Log in as a user with "University Admin" role
    5. Expected sidebar items: includes "Management Dashboard" AND "System Health" AND "Finance"

    **Test F — No per-route API calls (browser DevTools):**
    1. Open browser DevTools → Network tab
    2. Visit /portal/ (logged in)
    3. Navigate to different sidebar items
    4. Expected: zero calls to `/api/method/frappe.auth.get_logged_user` (the old pattern)
    5. One call to `get_session_info` on initial page load only

    If Frappe is not running, Tests B/C/D/E/F require manual deferral. In that case, confirm code correctness by reviewing:
    - health_check.py has @frappe.whitelist() and "University Admin" check
    - api.py has frappe.has_permission() in all 6 listed functions
    - router/index.js has NO frappe.auth.get_logged_user call
    - Sidebar.vue visibleItems filters by roles intersection
  </how-to-verify>
  <resume-signal>
    Type one of:
    - "approved" — all tests passed, phase complete
    - "partial: [describe what passed]" — some tests passed, list what failed
    - "issues: [describe]" — specific issues found, Claude will fix and re-verify
    - "deferred: no frappe instance" — browser tests skipped, code review confirms correctness
  </resume-signal>
</task>

</tasks>

<verification>
Phase 1 is complete when ALL of the following are true:

**Security (FOUND-02, FOUND-03, FOUND-04):**
```bash
python3 -c "
with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py') as f: src = f.read()
assert 'values=' in src and 'f-string' not in src.split('_execute_custom_query')[1].split('def _')[0]

with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py') as f: api = f.read()
assert api.count('frappe.has_permission') >= 6

with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py') as f: dash = f.read()
assert 'GROUP BY' in dash and '_get_department_student_count' not in dash
print('Security checks: PASS')
"
```

**Cross-app integrity (FOUND-01):**
```bash
python3 -c "
with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py') as f: hc = f.read()
assert 'run_checks' in hc and 'University Admin' in hc
assert all(fn in hc for fn in ['_check_student_enrollment', '_check_fees_gl_accounts', '_check_employee_faculty_profile', '_check_academic_year_validity'])
print('Health check: PASS')
"
```

**Vue app shell (FOUND-05, FOUND-06):**
```bash
python3 -c "
import os
files = [
    '/workspace/development/portal-vue/src/stores/session.js',
    '/workspace/development/portal-vue/src/router/index.js',
    '/workspace/development/portal-vue/src/components/Sidebar.vue',
    '/workspace/development/frappe-bench/apps/university_erp/university_erp/www/portal/index.py',
]
for f in files: assert os.path.exists(f), f'Missing: {f}'

with open('/workspace/development/portal-vue/src/router/index.js') as f: r = f.read()
assert 'frappe.auth.get_logged_user' not in r, 'Old auth pattern present'
assert 'isAuthenticated' in r

print('Vue shell: PASS')
"
```

**Roles (FOUND-08):**
```bash
python3 -c "
import json
with open('/workspace/development/frappe-bench/apps/university_erp/university_erp/fixtures/role.json') as f:
    roles = json.load(f)
names = [r['name'] for r in roles]
assert 'University VC' in names and 'University Dean' in names
print('Roles: PASS')
"
```
</verification>

<success_criteria>
Phase 1 Foundation & Security Hardening is complete when:

1. **FOUND-01 (Cross-app integrity):** health_check.run_checks() endpoint exists, callable by University Admin, returns {status, checks[4]}
2. **FOUND-02 (SQL injection):** dashboard_engine.py _execute_custom_query() uses values= dict, zero f-string interpolation of filter values
3. **FOUND-03 (Permission checks):** 6 analytics API endpoints call frappe.has_permission() before returning data
4. **FOUND-04 (N+1 queries):** get_department_performance() and get_kpi_summary() each issue ≤ 3 queries via GROUP BY aggregation
5. **FOUND-05 (Vue app shell):** portal-vue/ buildable project exists with router, Pinia store, layout, sidebar
6. **FOUND-06 (Cached auth):** beforeEach guard reads Pinia session store (populated once at boot), no per-route API call
7. **FOUND-07 (Academic year filter):** allowed_modules[] and roles[] in session store provide the context for academic year filter (Phase 2 will build the filter UI using this data)
8. **FOUND-08 (Management roles):** University VC and University Dean in fixtures/role.json; navigation.js maps them to management routes
</success_criteria>

<output>
After completion, create `/workspace/development/.planning/phases/01-foundation-security-hardening/01-03-integration-wiring-SUMMARY.md` with:
- npm build result (success/failure, any warnings)
- Which verification tests ran and their outcomes
- Which browser tests were completed vs deferred (no Frappe instance)
- Any issues found during integration and how they were resolved
- Final phase status for each FOUND-XX requirement
</output>
