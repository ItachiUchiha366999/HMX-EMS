# Phase 1: Foundation & Security Hardening — Research

**Researched:** 2026-03-18
**Domain:** Frappe/Python backend security, Vue 3 / Vite SPA, Frappe www pages, role fixtures
**Confidence:** HIGH — all findings derived from direct code inspection of actual project files

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- New unified Vue 3 app at `/portal/` — separate from the existing `/student_portal/` (which stays unchanged)
- Vite base URL: `/portal/` with new build output directory separate from `student-portal-spa`
- Pinia store with one-time boot fetch: `{logged_user, full_name, user_image, roles[], allowed_modules[]}`
- Custom backend endpoint `get_session_info()` — single call, replaces per-route auth guard
- Two new Frappe roles: `University VC` and `University Dean`
- Merged sidebar showing union of all permitted items — no switcher, no priority hierarchy
- Health-check API: `university_erp.health_check.run_checks` — University Admin only
- Four health checks: Student↔Enrollment, Fees↔GL Accounts, Employee↔Faculty Profile, Academic Year validity
- SQL injection fix: replace f-string interpolation at `dashboard_engine.py:158–164` with parameterized queries
- Permission checks: add `frappe.has_permission()` to all analytics API endpoints currently missing it

### Claude's Discretion
- Exact Pinia store structure (module split vs flat store)
- Error boundary / loading state design for the app shell
- How the sidebar is data-driven (config array vs router meta vs both)
- Specific aggregation SQL query patterns for N+1 fix

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUND-01 | Cross-app data consistency verified (ERPNext ↔ HRMS ↔ Education ↔ university_erp) | Health check module covers all four integration points; exact field names documented below |
| FOUND-02 | SQL injection in dashboard_engine.py fixed with parameterized queries | Exact lines 158–164 identified; exact f-string variables documented; fix pattern shown |
| FOUND-03 | Permission checks on all analytics and dashboard API endpoints | All 8 endpoints in analytics/api.py audited; 6 are missing `frappe.has_permission()` calls |
| FOUND-04 | N+1 query patterns in executive_dashboard.py resolved | Two N+1 loops identified: `get_department_performance` (lines 184–193) and `get_kpi_summary` (lines 284–302); GROUP BY replacement documented |
| FOUND-05 | Unified Vue app shell with role-based routing | Existing Vite config pattern understood; new app structure documented |
| FOUND-06 | Auth guard with cached session — eliminate per-route API call | Current per-route guard identified in router/index.js; Pinia boot pattern documented |
| FOUND-07 | Academic year / semester filter available on all data views | Pinia `allowed_modules[]` and `get_session_info()` can carry active academic year; documented as boot data |
| FOUND-08 | Management role detection added (VC, Registrar, Finance Officer, Dean) | `University VC` and `University Dean` are new; `University Registrar` and `University Finance` already exist in fixtures/role.json |
</phase_requirements>

---

## Summary

Phase 1 has two independent workstreams that can proceed in parallel: (1) backend security fixes and health checks, and (2) the unified Vue 3 portal app shell. Both are well-scoped with clear before/after code states already readable in the codebase.

The backend security work is straightforward: three localized changes to files already identified. The SQL injection is a single function (`_execute_custom_query`, lines 155–171 of dashboard_engine.py). Permission check gaps are present on 6 of 8 endpoints in analytics/api.py. The N+1 pattern appears in two functions in executive_dashboard.py, each iterating over a result set and firing per-row queries.

The Vue app shell work replicates the well-understood `student_portal` pattern but at a higher scope: new Vite config, new `www/portal/index.py` + `index.html`, and a new Vue project (or second Vite entry) that adds Pinia on top of the existing composables. The existing `useFrappe.js`, `AdminLayout.vue`, and layout patterns are directly reusable.

**Primary recommendation:** Execute backend security fixes and health check module as Wave 1. Execute Vue app shell scaffold as Wave 2 (can overlap). Both land before any portal view work begins in Phases 3–6.

---

## 1. Security Fixes — Exact Code Analysis

### 1.1 SQL Injection in dashboard_engine.py

**File:** `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py`

**Method:** `_execute_custom_query(self, widget, filters=None)` — lines 140–171

**Exact injection pattern (lines 155–167):**

```python
# Replace filter placeholders safely  ← comment is misleading — this is NOT safe
if filters:
    if filters.get("from_date"):
        query = query.replace("%(from_date)s", f"'{filters['from_date']}'")   # line 158
    if filters.get("to_date"):
        query = query.replace("%(to_date)s", f"'{filters['to_date']}'")       # line 160
    if filters.get("department"):
        query = query.replace("%(department)s", f"'{filters['department']}'") # line 162
    if filters.get("program"):
        query = query.replace("%(program)s", f"'{filters['program']}'")       # line 164

try:
    result = frappe.db.sql(query, as_dict=True)                               # line 167
```

**Why this is a vulnerability:** All four filter values (`from_date`, `to_date`, `department`, `program`) are interpolated directly into the SQL string via f-strings before being passed to `frappe.db.sql()`. The `widget.custom_query` field contains user-configurable SQL (stored in Custom Dashboard Widget). An attacker who can set filter values — or who controls `widget.custom_query` — can inject arbitrary SQL. No escaping is applied.

**Variables that are tainted:** `filters['from_date']`, `filters['to_date']`, `filters['department']`, `filters['program']` — all come from API caller.

**Parameterized fix pattern (frappe.db.sql with values dict):**

```python
# Source: frappe.db.sql() signature — frappe uses MySQLdb-style %(name)s placeholders
values = {}
if filters:
    if filters.get("from_date"):
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        values["to_date"] = filters["to_date"]
    if filters.get("department"):
        values["department"] = filters["department"]
    if filters.get("program"):
        values["program"] = filters["program"]

try:
    result = frappe.db.sql(query, values=values, as_dict=True)
```

**Critical constraint:** The query must already contain `%(from_date)s`, `%(to_date)s`, `%(department)s`, `%(program)s` as named placeholders (not the inline f-string replacements). The `custom_query` field is supposed to use these placeholders — the old code was replacing them with literal strings, which destroyed the parameterization. The fix restores the intended parameterized form by passing `values` dict directly to `frappe.db.sql()`.

**Additional validation to add:** Validate that `widget.custom_query` does not contain multiple statements (semicolons) or forbidden keywords (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `TRUNCATE`) since it is user-stored SQL.

### 1.2 Missing Permission Checks in analytics/api.py

**File:** `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py`

**All 8 endpoints audited:**

| Endpoint | Has Permission Check | What to Add |
|----------|---------------------|-------------|
| `get_dashboard(dashboard_name, filters)` | Partial — `dashboard.has_access()` is called inside `DashboardEngine.get_dashboard_data()` | Adequate — permission is checked on the dashboard doc itself before data is returned |
| `get_available_dashboards()` | Partial — same `has_access()` per dashboard inside engine | Adequate — filtered to accessible dashboards |
| `get_kpi_value(kpi_name, filters)` | MISSING | Add `frappe.has_permission("KPI Definition", "read", kpi_name, throw=True)` before `AnalyticsManager()` call |
| `get_kpi_trend(kpi_name, periods, period_type, filters)` | MISSING | Add `frappe.has_permission("KPI Definition", "read", kpi_name, throw=True)` |
| `get_kpi_comparison(kpi_name, ...)` | MISSING | Add `frappe.has_permission("KPI Definition", "read", kpi_name, throw=True)` |
| `get_quick_stats()` | MISSING | Add role check — this calls `get_overview_metrics()` which returns institution-wide data; should require at least one management role: `frappe.only_for(["University Admin", "University VC", "University Registrar", "University Finance", "University Dean"])` |
| `execute_custom_report(report_name, filters)` | Present — `report_doc.has_access()` is called | Adequate |
| `get_all_kpis(category, active_only)` | MISSING — no check before `frappe.get_all("KPI Definition")` then per-KPI `frappe.db.get_value("KPI Value")` | Add `frappe.only_for(["University Admin", "University VC", "University Dean", "University Registrar", "University Finance"])` |
| `calculate_kpi_now(kpi_name, store_value, filters)` | MISSING — no check before computing and optionally writing to KPI Value | Add `frappe.has_permission("KPI Definition", "write", kpi_name, throw=True)` (write because `store_value` can create records) |

**Summary of endpoints needing fixes:** `get_kpi_value`, `get_kpi_trend`, `get_kpi_comparison`, `get_quick_stats`, `get_all_kpis`, `calculate_kpi_now` — 6 of 8 endpoints.

**Standard Frappe permission check pattern:**

```python
# Source: Frappe Framework — frappe.has_permission()
# Option A: Check and throw automatically
frappe.has_permission("DocType Name", "read", doc_name, throw=True)

# Option B: Role-based guard (for computed data not tied to a single doc)
frappe.only_for(["University Admin", "University VC"])
# raises frappe.PermissionError if user has none of these roles

# Option C: Manual check
if not frappe.has_permission("KPI Definition", "read", kpi_name):
    frappe.throw(_("Not permitted"), frappe.PermissionError)
```

### 1.3 N+1 Queries in executive_dashboard.py

**File:** `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py`

**N+1 Pattern 1: `get_department_performance()` (lines 180–194)**

```python
departments = frappe.get_all("Department", fields=["name"])      # Query 1: get all depts

for dept in departments[:10]:                                     # Loop — up to 10 iterations
    dept_data = {
        "department": dept["name"],
        "students": _get_department_student_count(dept["name"]),  # Query per dept
        "faculty": _get_department_faculty_count(dept["name"]),   # Query per dept
        "attendance_rate": _get_department_attendance(dept["name"]), # Mock (no query now)
        "pass_rate": _get_department_pass_rate(dept["name"])         # Mock (no query now)
    }
```

Query count: 1 (dept list) + up to 10×2 = **up to 21 queries** for 10 departments.

The helper functions:
- `_get_department_student_count(department)` — `frappe.db.count("Student", {"department": department})`
- `_get_department_faculty_count(department)` — `frappe.db.count("Instructor", {"department": department})`

**Aggregated replacement:**

```python
# Single query replacing up to 20 per-dept queries
student_counts = frappe.db.sql("""
    SELECT department, COUNT(*) AS student_count
    FROM `tabStudent`
    WHERE department IS NOT NULL
    GROUP BY department
""", as_dict=True)
# Build dict: {dept_name: count}

faculty_counts = frappe.db.sql("""
    SELECT department, COUNT(*) AS faculty_count
    FROM `tabInstructor`
    WHERE department IS NOT NULL
    GROUP BY department
""", as_dict=True)
# Build dict: {dept_name: count}

# Then merge into departments list (no per-dept queries)
```

Total queries: 3 (dept list + 2 aggregations) regardless of department count.

**N+1 Pattern 2: `get_kpi_summary()` (lines 274–302)**

```python
kpi_definitions = frappe.get_all("KPI Definition", ...)          # Query 1: get KPI list

for kpi_def in kpi_definitions[:8]:                              # Loop — up to 8 iterations
    latest_value = frappe.db.get_value(                          # Query per KPI
        "KPI Value",
        {"kpi": kpi_def["name"]},
        ["value", "status", "variance"],
        order_by="period_start DESC"
    )
```

Query count: 1 + up to 8 = **up to 9 queries**.

**Aggregated replacement:**

```python
# Get latest KPI Value per KPI in one query using MAX(period_start) subquery
latest_values = frappe.db.sql("""
    SELECT kv.kpi, kv.value, kv.status, kv.variance
    FROM `tabKPI Value` kv
    INNER JOIN (
        SELECT kpi, MAX(period_start) AS latest_period
        FROM `tabKPI Value`
        GROUP BY kpi
    ) latest ON kv.kpi = latest.kpi AND kv.period_start = latest.latest_period
    WHERE kv.kpi IN %(kpi_names)s
""", values={"kpi_names": tuple(kpi_names)}, as_dict=True)
```

Total queries: 2 (KPI list + single aggregated value fetch) regardless of KPI count.

**Also note:** `get_enrollment_trend()` (lines 83–104) has a 12-iteration loop calling `frappe.db.count("Student", ...)` per month — 12 queries. This is also an N+1 and should be replaced with a single GROUP BY DATE query, but it is less critical than the department loop since the loop body is simpler. Flag as medium priority.

---

## 2. Vue App Shell — Existing Patterns

### 2.1 Vite Config

**Current config** (`student-portal-vue/vite.config.js`):

```javascript
export default defineConfig({
  plugins: [vue()],
  base: '/assets/university_erp/student-portal-spa/',
  build: {
    outDir: path.resolve(__dirname, '../frappe-bench/apps/university_erp/university_erp/public/student-portal-spa'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'index.html'),
    },
  },
})
```

**Key decisions:**
- `base`: controls the public URL prefix that Vite embeds in all asset references (JS/CSS imports)
- `outDir`: absolute path into the Frappe app's `public/` directory — this is where `bench build` will serve assets from
- `manifest: true`: required so `www/portal/index.py` can read hashed filenames (the existing `get_vite_manifest()` pattern depends on this)

**New unified portal app config** (what it should be):

```javascript
// portal-vue/vite.config.js (new separate project, OR second entry in student-portal-vue)
export default defineConfig({
  plugins: [vue()],
  base: '/assets/university_erp/portal-spa/',
  build: {
    outDir: path.resolve(__dirname, '../frappe-bench/apps/university_erp/university_erp/public/portal-spa'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'index.html'),
    },
  },
})
```

**Decision for planner:** The decision is whether to create a second standalone project (e.g., `portal-vue/`) at repo root, or add a second Vite config/entry to the existing `student-portal-vue/`. The standalone project approach is cleaner and avoids entangling build pipelines. The existing project uses Tailwind, which the new app will also need.

**Current package versions** (from `student-portal-vue/package.json`):
- `vue`: `^3.5.24`
- `vue-router`: `^4.6.4`
- `vite`: `^7.2.4`
- `@vitejs/plugin-vue`: `^6.0.1`
- `tailwindcss`: `^3.4.17`

Pinia (`^2.x`) must be added as a dependency in the new project. It is not in the existing `student-portal-vue`.

### 2.2 Auth Guard Pattern (Current — to Replace)

**Current pattern** (`student-portal-vue/src/router/index.js`, lines 67–81):

```javascript
router.beforeEach(async (to) => {
  try {
    const res = await fetch('/api/method/frappe.auth.get_logged_user', {
      headers: { 'Accept': 'application/json' },
    })
    const data = await res.json()
    if (!res.ok || data.message === 'Guest') {
      window.location.href = `/login?redirect-to=/student_portal${to.fullPath}`
      return false
    }
  } catch {
    window.location.href = '/login?redirect-to=/student_portal/'
    return false
  }
})
```

**Problems with this pattern:**
1. Every route change fires one API call — a user navigating 10 pages makes 10 auth calls
2. No caching — even within the same page load
3. No role information — only checks if logged in, not what the user can access

**Replacement pattern with Pinia:**

```javascript
// stores/session.js (Pinia store)
import { defineStore } from 'pinia'

export const useSessionStore = defineStore('session', {
  state: () => ({
    user: null,
    full_name: null,
    user_image: null,
    roles: [],
    allowed_modules: [],
    loaded: false,
  }),
  actions: {
    async boot() {
      if (this.loaded) return
      const res = await fetch('/api/method/university_erp.university_erp.portal.session.get_session_info', {
        headers: { 'Accept': 'application/json' },
      })
      if (res.status === 401 || res.status === 403) {
        window.location.href = '/login?redirect-to=/portal/'
        return
      }
      const data = await res.json()
      Object.assign(this.$state, data.message)
      this.loaded = true
    },
    hasRole(role) {
      return this.roles.includes(role)
    },
    hasAnyRole(roles) {
      return roles.some(r => this.roles.includes(r))
    }
  }
})

// main.js — boot once before mounting
const app = createApp(App)
app.use(router)
app.use(pinia)

const session = useSessionStore()
await session.boot()  // Single API call at startup
app.mount('#app')

// router/index.js — guard is now a cheap synchronous check
router.beforeEach((to) => {
  const session = useSessionStore()
  if (!session.user || session.user === 'Guest') {
    window.location.href = '/login?redirect-to=/portal' + to.fullPath
    return false
  }
  if (to.meta.roles && !session.hasAnyRole(to.meta.roles)) {
    return { name: 'unauthorized' }
  }
})
```

### 2.3 Layout Structure

**StudentLayout.vue — sidebar pattern:**
- Hard-coded `router-link` items: Dashboard, Academics, Finance, Examinations, Library, Hostel, Transport, Placement, Notifications, Grievances
- User info block at bottom shows `student?.student_name`, `student?.program`, avatar
- Mobile: fixed bottom nav bar with 5 items + "More" button that opens sidebar
- Sidebar collapses on mobile; always visible on desktop (`lg:static`)
- Active state: `.sidebar-active` class via `active-class` prop (`background rgba(19,91,236,0.1)`, `color: #135bec`, `border-right: 3px solid #135bec`)

**AdminLayout.vue — sidebar pattern:**
- Hard-coded `router-link` items grouped under "Main", "Management", "System" section headers
- User info at bottom is currently hard-coded (no `useAuth`)
- Same mobile responsive pattern as StudentLayout

**What changes for the unified portal:**
1. Sidebar items become **data-driven** — an array of `{ label, icon, route, roles[] }` objects, filtered to those where `session.hasAnyRole(item.roles)` is true
2. User info block reads from Pinia `useSessionStore()` — `full_name`, `user_image` — not role-specific composables
3. Section grouping can still exist but groups are also dynamically filtered (e.g., "Management" section only renders if user has a management role)
4. The mobile bottom nav shows the top 4 permitted items (determined at render time from filtered sidebar)

**Reusable from existing layouts:**
- The responsive sidebar open/close logic (`isSidebarOpen`, `isMobile`, `handleResize`, `router.afterEach`) — copy verbatim
- The `.sidebar-active` CSS class definition
- The mobile backdrop overlay pattern
- The mobile bottom nav pattern

### 2.4 Frappe www Page Pattern

**How the student portal www page works:**

1. File structure:
   ```
   www/
   └── student_portal/
       ├── index.py    ← Python context provider (get_context)
       └── index.html  ← Jinja template (SPA shell)
   ```

2. `index.py::get_context(context)` does three things:
   - Checks `frappe.session.user == "Guest"` → redirect to login with `frappe.Redirect`
   - Calls `get_current_student()` — verifies user has a Student record
   - Reads Vite manifest to inject hashed JS/CSS filenames into template context

3. `index.html` is a minimal SPA shell:
   - Loads fonts (Lexend, Material Symbols)
   - Conditionally includes `{{ vue_css }}` and `{{ vue_js }}` from manifest
   - Has `<div id="app"></div>` mount point
   - Shows spinner CSS while Vue mounts

4. The URL `/student_portal` maps to `www/student_portal/index.html` via Frappe's www routing.

**Pattern for new `/portal/` page:**

```
www/
└── portal/
    ├── __init__.py   ← empty, marks as package
    ├── index.py      ← get_context(): auth check (any non-Guest), Vite manifest read
    └── index.html    ← SPA shell (same structure, different title)
```

**Key difference:** The portal `index.py` must NOT check for Student specifically — it must allow any authenticated user (student, faculty, admin, VC, etc.). The only check is `frappe.session.user != "Guest"`.

```python
def get_context(context):
    """SPA shell for the unified Vue 3 portal"""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to=/portal{frappe.local.request.path.replace('/portal', '') or '/'}"
        )
        raise frappe.Redirect

    context.no_cache = 1
    context.show_sidebar = False

    manifest = get_vite_manifest()  # reads public/portal-spa/.vite/manifest.json
    context.vue_js = manifest.get("js", "")
    context.vue_css = manifest.get("css", "")
    return context
```

**URL routing note:** Frappe serves `www/portal/index.html` at `/portal`. Vue Router uses `createWebHistory('/portal/')` so all sub-paths (`/portal/dashboard`, `/portal/academics`) are handled by the SPA without a server round-trip. The `www/portal/index.py` only handles the initial page load.

---

## 3. Health Check — Exact Field Names

### Student ↔ Program Enrollment

**Doctypes:** `Student` (from `education` app), `Program Enrollment` (from `education` app)

**Link field on Program Enrollment:** `student` (Link → Student)

**Active enrollment filter:** `docstatus = 1` (submitted)

**Check query:**

```python
# Students with NO submitted Program Enrollment
orphaned = frappe.db.sql("""
    SELECT s.name, s.student_name
    FROM `tabStudent` s
    WHERE NOT EXISTS (
        SELECT 1 FROM `tabProgram Enrollment` pe
        WHERE pe.student = s.name AND pe.docstatus = 1
    )
""", as_dict=True)
# Count = len(orphaned)
# Status: pass if 0, warn if 1-10, fail if >10
```

**Program Enrollment key fields confirmed:**
- `student` (Link → Student)
- `program` (Link → Program)
- `academic_year` (Link → Academic Year)
- `enrollment_date` (Date)
- `docstatus` (0=Draft, 1=Submitted, 2=Cancelled)

### Fees ↔ GL Accounts

**Doctype:** `Fee Structure` (from `education` app)

**GL Account fields confirmed:**
- `receivable_account` (Link → Account)
- `income_account` (Link → Account)

**Check query:**

```python
# Fee Structures with missing or invalid GL account links
invalid_fees = frappe.db.sql("""
    SELECT fs.name,
           fs.receivable_account,
           fs.income_account
    FROM `tabFee Structure` fs
    WHERE fs.docstatus != 2
    AND (
        fs.receivable_account IS NULL OR fs.receivable_account = ''
        OR fs.income_account IS NULL OR fs.income_account = ''
        OR NOT EXISTS (SELECT 1 FROM `tabAccount` a WHERE a.name = fs.receivable_account)
        OR NOT EXISTS (SELECT 1 FROM `tabAccount` a WHERE a.name = fs.income_account)
    )
""", as_dict=True)
```

### Employee ↔ Faculty Profile

**Doctype:** `Faculty Profile` (from `university_erp/faculty_management` module)

**Employee link field confirmed:** `employee` (Link → Employee)

**Check query:**

```python
# Faculty Profiles where linked Employee does not exist
broken_faculty = frappe.db.sql("""
    SELECT fp.name, fp.employee, fp.employee_name
    FROM `tabFaculty Profile` fp
    WHERE fp.employee IS NOT NULL AND fp.employee != ''
    AND NOT EXISTS (
        SELECT 1 FROM `tabEmployee` e WHERE e.name = fp.employee
    )
""", as_dict=True)
```

**Additional check:** Faculty Profiles with NULL employee (never linked):

```python
unlinked_faculty = frappe.db.sql("""
    SELECT COUNT(*) AS cnt FROM `tabFaculty Profile`
    WHERE employee IS NULL OR employee = ''
""", as_dict=True)
```

### Academic Year / Term Validity

**Academic Year fields confirmed:**
- `academic_year_name` (Data) — the display name
- `year_start_date` (Date)
- `year_end_date` (Date)

**Academic Term fields confirmed:**
- `term_name` (Data)
- `academic_year` (Link → Academic Year)
- `term_start_date` (Date)
- `term_end_date` (Date)

**Check logic:**

```python
# Check 1: At least one Academic Year exists
year_count = frappe.db.count("Academic Year", {})
if year_count == 0:
    # fail: no academic years configured

# Check 2: No Academic Year with null dates
bad_years = frappe.db.sql("""
    SELECT name FROM `tabAcademic Year`
    WHERE year_start_date IS NULL OR year_end_date IS NULL
    OR year_end_date <= year_start_date
""", as_dict=True)

# Check 3: At least one Academic Term exists
term_count = frappe.db.count("Academic Term", {})
if term_count == 0:
    # warn: no terms configured (not a hard failure)

# Check 4: No Academic Term with null dates
bad_terms = frappe.db.sql("""
    SELECT name FROM `tabAcademic Term`
    WHERE term_start_date IS NULL OR term_end_date IS NULL
    OR term_end_date <= term_start_date
""", as_dict=True)
```

### Health Check Module Structure

**File location:** `frappe-bench/apps/university_erp/university_erp/university_erp/health_check.py`

**Return schema (locked):**
```python
{
    "status": "ok" | "degraded" | "critical",
    "checks": [
        {
            "name": str,      # e.g., "Student-Enrollment Integrity"
            "status": "pass" | "warn" | "fail",
            "detail": str,    # human-readable message
            "count": int      # number of affected records
        }
    ]
}
```

**Status rollup logic:**
- `ok`: all checks are `pass`
- `degraded`: at least one `warn`, no `fail`
- `critical`: at least one `fail`

---

## 4. Roles — Creation Pattern

### Existing Role Fixture

**File:** `frappe-bench/apps/university_erp/university_erp/fixtures/role.json`

**Existing roles confirmed** (from direct file read):
- `University Admin` — `home_page: /app/university-home`, `desk_access: 1`
- `University Registrar` — `home_page: /app/admissions`, `desk_access: 1`
- `University Finance` — `home_page: /app/university-finance`, `desk_access: 1`
- `University HR Admin` — `home_page: /app/university-hr`, `desk_access: 1`
- `University HOD` — `home_page: /app/department-dashboard`, `desk_access: 1`
- `University Exam Cell` — `home_page: /app/examinations`, `desk_access: 1`
- `University Faculty` — `home_page: /app/faculty-dashboard`, `desk_access: 1`
- `University Student` — `home_page: /student_portal`, `desk_access: 0`
- `University Librarian` — `desk_access: 1`
- `University Warden` — `desk_access: 1`
- `University Placement Officer` — `desk_access: 1`

**Two roles NOT yet in fixture:** `University VC` and `University Dean`

### How Fixtures Work

In `hooks.py` line 61:
```python
fixtures = [
    {"dt": "Role", "filters": [["name", "like", "University%"]]},
    ...
]
```

The filter `["name", "like", "University%"]` means **any Role whose name starts with "University"** is exported/imported by `bench export-fixtures` / `bench import-fixtures`. Adding entries to `fixtures/role.json` is sufficient — no changes to `hooks.py` needed.

### New Role Entry Template

Copy the pattern from existing entries. For `University VC` and `University Dean`:

```json
{
  "desk_access": 1,
  "disabled": 0,
  "docstatus": 0,
  "doctype": "Role",
  "home_page": "/portal",
  "is_custom": 0,
  "name": "University VC",
  "restrict_to_domain": "",
  "role_name": "University VC",
  "search_bar": 1,
  "two_factor_auth": 0
}
```

```json
{
  "desk_access": 1,
  "disabled": 0,
  "docstatus": 0,
  "doctype": "Role",
  "home_page": "/portal",
  "is_custom": 0,
  "name": "University Dean",
  "restrict_to_domain": "",
  "role_name": "University Dean",
  "search_bar": 1,
  "two_factor_auth": 0
}
```

**`home_page` set to `/portal`** — when these users log in to Frappe desk, they redirect to the unified portal. This is consistent with `University Student` using `/student_portal` as `home_page`.

**desk_access: 1** — management roles need Frappe desk access for admin operations. VC and Dean should have desk access.

### Installation

After adding to `fixtures/role.json`, the roles are created via:
```bash
bench --site [sitename] import-fixtures --app university_erp
```

Or on fresh install they are applied automatically via `bench install-app`.

---

## 5. Requirements Coverage (FOUND-01 through FOUND-08)

| Req | Description | Implementation | File(s) |
|-----|-------------|----------------|---------|
| FOUND-01 | Cross-app data consistency verified | `health_check.py` module with 4 checks covering Education↔ERPNext (fee GL accounts), Education↔university_erp (Student↔Enrollment, Faculty Profile↔Employee), Education internal (Academic Year/Term dates) | New file: `university_erp/university_erp/health_check.py` |
| FOUND-02 | SQL injection fixed | Replace f-string interpolation at lines 158–164 with `frappe.db.sql(query, values=values)` | `university_erp/university_erp/analytics/dashboard_engine.py` |
| FOUND-03 | Permission checks on analytics endpoints | Add `frappe.has_permission()` or `frappe.only_for()` to 6 endpoints in analytics/api.py | `university_erp/university_erp/analytics/api.py` |
| FOUND-04 | N+1 queries resolved | Replace `get_department_performance()` loop (21 queries → 3) and `get_kpi_summary()` loop (9 queries → 2) with GROUP BY aggregations | `university_erp/university_erp/analytics/dashboards/executive_dashboard.py` |
| FOUND-05 | Unified Vue app shell | New `portal-vue/` project with Pinia-driven RBAC routing; new `www/portal/index.py` + `index.html` | New directory: `portal-vue/`; new: `www/portal/` |
| FOUND-06 | Auth guard with cached session | Pinia `useSessionStore` with `boot()` called once in `main.js`; `router.beforeEach` reads store (no API call per route) | `portal-vue/src/stores/session.js`, `portal-vue/src/router/index.js`, `portal-vue/src/main.js` |
| FOUND-07 | Academic year/semester filter on all views | `get_session_info()` can return `active_academic_year` as a convenience field; or Pinia store exposes a setter; full filter components are Phase 2 (COMP-04) but the data source is established here | `university_erp/university_erp/portal/session.py` |
| FOUND-08 | Management role detection | `University Registrar` and `University Finance` already exist in fixtures; add `University VC` and `University Dean` to `fixtures/role.json`; `get_session_info()` returns full roles array so Vue can detect any management role | `fixtures/role.json`, `portal/session.py` |

---

## 6. Standard Stack

### Backend (Frappe/Python)

| Component | Version | Notes |
|-----------|---------|-------|
| Frappe | 15.x (installed) | `frappe.has_permission()`, `frappe.only_for()`, `frappe.db.sql(values=...)` all available |
| Python | 3.11 (confirmed from `__pycache__/*.cpython-311.pyc`) | |
| MariaDB | running (frappe-bench active) | Named placeholder syntax: `%(name)s` |

### Frontend (New Portal App)

| Package | Version | Purpose |
|---------|---------|---------|
| vue | ^3.5.24 | Core framework (same as existing portal) |
| vue-router | ^4.6.4 | SPA routing |
| pinia | ^2.x | State management — new addition |
| vite | ^7.2.4 | Build tool (same as existing portal) |
| @vitejs/plugin-vue | ^6.0.1 | Vue SFC support |
| tailwindcss | ^3.4.17 | Styling (same as existing portal) |

**Installation for new project:**
```bash
npm create vite@latest portal-vue -- --template vue
cd portal-vue
npm install vue-router pinia
npm install -D tailwindcss postcss autoprefixer @vitejs/plugin-vue
npx tailwindcss init -p
```

---

## 7. Architecture Patterns

### Recommended Project Structure (New Portal Vue App)

```
portal-vue/
├── index.html               # SPA entry (Vite input)
├── vite.config.js           # base: '/assets/university_erp/portal-spa/'
├── package.json
├── tailwind.config.js
├── src/
│   ├── main.js              # createApp + pinia + router; await session.boot()
│   ├── App.vue              # RouterView only
│   ├── stores/
│   │   └── session.js       # useSessionStore (Pinia) — user, roles, allowed_modules
│   ├── composables/
│   │   └── useFrappe.js     # Copy from student-portal-vue (reuse verbatim)
│   ├── router/
│   │   └── index.js         # createWebHistory('/portal/'); meta.roles on each route
│   ├── layouts/
│   │   └── PortalLayout.vue # Unified layout: data-driven sidebar, reads session store
│   ├── views/
│   │   ├── Dashboard.vue    # Role-aware dashboard (Phase 1: scaffold only)
│   │   └── Unauthorized.vue # Shown when user has no permitted routes
│   └── config/
│       └── navigation.js    # Sidebar items: [{label, icon, route, roles:[]}]
```

### Backend Module Structure

```
university_erp/university_erp/
├── health_check.py                      # NEW: run_checks() whitelisted endpoint
└── portal/                              # NEW module
    ├── __init__.py
    └── session.py                       # NEW: get_session_info() whitelisted endpoint

university_erp/www/
└── portal/                              # NEW www page
    ├── __init__.py
    ├── index.py                         # get_context(): auth check + manifest read
    └── index.html                       # SPA shell (mirrors student_portal/index.html)
```

### `get_session_info()` Endpoint Contract

**File:** `university_erp/university_erp/portal/session.py`

```python
@frappe.whitelist()
def get_session_info():
    """Single boot call for the unified portal SPA"""
    if frappe.session.user == "Guest":
        frappe.throw("Not logged in", frappe.AuthenticationError)

    user_doc = frappe.get_doc("User", frappe.session.user)

    roles = [r.role for r in user_doc.roles]

    # Determine allowed_modules based on roles
    # (simple mapping — refined in Phase 4)
    allowed_modules = _get_allowed_modules(roles)

    return {
        "logged_user": frappe.session.user,
        "full_name": user_doc.full_name,
        "user_image": user_doc.user_image,
        "roles": roles,
        "allowed_modules": allowed_modules,
    }
```

---

## 8. Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| SQL parameterization | Custom escaping/sanitization | `frappe.db.sql(query, values=dict)` — MySQLdb handles escaping |
| Permission checks | Custom role comparison logic | `frappe.has_permission()` and `frappe.only_for()` — built into Frappe |
| Role fixture loading | Custom install script | `fixtures/role.json` + `hooks.py` fixtures filter — Frappe handles import |
| Session/cookie handling in Vue | Custom fetch wrapper | Existing `useFrappe.js` already handles CSRF token from cookie |
| Vite manifest parsing | Custom asset pipeline | Existing `get_vite_manifest()` in `www/student_portal/index.py` — copy verbatim |
| Vue Router history mode | Custom URL rewriting | `createWebHistory('/portal/')` — Vue Router handles it; Frappe www page serves the SPA shell for the base URL |

---

## 9. Common Pitfalls

### Pitfall 1: Frappe www Routing vs Vue Router Conflict

**What goes wrong:** If a user navigates directly to `/portal/dashboard` (not via SPA), Frappe tries to find `www/portal/dashboard/index.py` — which doesn't exist — and returns 404.

**Why it happens:** Frappe's www router handles each path segment independently. Only `/portal` maps to `www/portal/index.py`.

**How to avoid:** Vue Router must use `createWebHistory('/portal/')`. The SPA shell at `www/portal/index.html` renders regardless of sub-path because Frappe falls through to the parent `www/portal/index.py` for unknown sub-paths **only if** Frappe is configured to do so. **Actual fix:** Add a catch-all in `www/portal/index.py` by also handling subpath requests, OR configure Frappe to serve the SPA shell for all `/portal/*` paths. The existing `student_portal` gets around this by having the SPA use `createWebHistory('/student_portal/')` — same pattern works for `/portal/`.

**Warning sign:** Direct URL navigation to `/portal/dashboard` returns Frappe 404.

**Safe default:** Tell users to always navigate via the app, or add a `no_cache` setting that serves the SPA shell for all `/portal/` routes. Frappe's www page for `student_portal` serves for `/student_portal` only — verify this works for sub-paths in the dev environment before finalizing.

### Pitfall 2: Pinia Async Boot Blocks Mount

**What goes wrong:** `await session.boot()` in `main.js` before `app.mount()` means if the API call hangs or fails, the app never mounts.

**How to avoid:** Set a timeout on the boot call. If the API call fails with 401/403, redirect to login. If it fails for any other reason (network timeout, 500), mount the app in a degraded state with an error message rather than blocking forever.

### Pitfall 3: `frappe.db.sql` with Named Placeholder When Query Has No Matching Placeholders

**What goes wrong:** If `values={"from_date": "2026-01-01"}` is passed but the query string contains no `%(from_date)s`, MySQLdb raises a TypeError rather than ignoring unused values.

**How to avoid:** The fix in `dashboard_engine.py` must only pass values for placeholders that actually exist in the query. Filter `values` dict to only keys whose placeholder appears in the query string.

### Pitfall 4: Role JSON Fixture Not Loaded After Adding New Entries

**What goes wrong:** Adding entries to `fixtures/role.json` does not automatically create them in the database. They must be imported.

**How to avoid:** The implementation task must include `bench --site [site] import-fixtures --app university_erp` as a verification step, or create the roles programmatically in `setup/install.py` and call `bench --site [site] execute university_erp.setup.install.create_roles` during verification.

### Pitfall 5: N+1 Fix Uses IN Clause with Empty Tuple

**What goes wrong:** If `kpi_definitions` returns an empty list, `tuple(kpi_names)` is `()`, and `WHERE kpi IN ()` is invalid SQL in MySQL/MariaDB.

**How to avoid:** Guard the aggregated query with an early return if the list is empty:
```python
if not kpi_names:
    return []
```

### Pitfall 6: `get_kpi_summary()` MAX/subquery Returns Multiple Rows Per KPI

**What goes wrong:** If multiple KPI Value records share the same `period_start` for the same KPI (possible if stored multiple times on the same day), the subquery join returns multiple rows per KPI.

**How to avoid:** Use `LIMIT 1` per KPI or use `ORDER BY period_start DESC LIMIT 1` in a correlated subquery instead of a join. Alternatively, add `MIN(kv.name)` as tiebreaker in the GROUP BY.

---

## 10. Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (Python 3.11 + Frappe test runner) |
| Config file | `frappe-bench/apps/university_erp/university_erp/tests/` directory exists |
| Quick run command | `cd frappe-bench && bench --site [site] run-tests --app university_erp --module university_erp.university_erp.tests` |
| Full suite command | `bench --site [site] run-tests --app university_erp` |

Existing test files found in `university_erp/tests/`:
- `test_grading_system.py`
- `test_installation.py`
- `test_override_course.py`
- `test_override_program.py`
- `test_override_student.py`
- `test_university_department.py`

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| FOUND-02 | SQL injection fix: parameterized query does not allow injection | unit | Test `_execute_custom_query` with a malicious filter value — confirm SQL executes safely |
| FOUND-03 | Permission checks: unauthenticated call to `get_kpi_value` raises PermissionError | unit | Call endpoint as Guest or low-privilege user; assert `frappe.PermissionError` |
| FOUND-04 | N+1 fix: `get_department_performance` fires ≤ 3 queries | unit | Use `frappe.db.sql` query counter or mock and assert call count |
| FOUND-01 | Health checks: `run_checks()` returns valid schema | unit | Call `run_checks()` directly; assert return shape matches documented schema |
| FOUND-05/06 | Vue app boots and loads session — verified manually | smoke | Manual: open `/portal/` in browser; confirm Pinia store populated, sidebar renders |
| FOUND-08 | `University VC` and `University Dean` roles exist post-fixture-import | integration | `frappe.db.exists("Role", "University VC")` → True |

### Wave 0 Gaps

- [ ] `university_erp/university_erp/tests/test_security_fixes.py` — covers FOUND-02, FOUND-03, FOUND-04
- [ ] `university_erp/university_erp/tests/test_health_check.py` — covers FOUND-01
- [ ] `university_erp/university_erp/tests/test_roles.py` — covers FOUND-08

---

## 11. Implementation Risks

### Risk 1: `custom_query` Field Stores Old-Style Placeholders

**Issue:** Existing Widget records in the DB may have stored queries with `%(from_date)s` placeholders already. The fix preserves these — that's correct. But if some widgets stored queries that have already been run with the unsafe replacement (i.e., they contain literal date strings instead of placeholders), the parameterized fix won't break anything but also won't sanitize historical data.

**Mitigation:** The fix is purely additive/corrective for new executions. No data migration needed.

### Risk 2: Vue Router History Mode and Frappe www Sub-Path Handling

**Issue:** Frappe's www router may not automatically fall through to `www/portal/index.py` for sub-paths like `/portal/academics`. This needs verification in the dev environment.

**Mitigation:** Test `/portal/academics` direct navigation on first build. If 404, add a Frappe `website_redirects` or override the 404 handler to serve the SPA shell for `/portal/*`.

### Risk 3: Pinia Not Yet in `student-portal-vue` — New Project Scope

**Issue:** The decision is whether to add a second Vite project or extend the existing one. If creating a new project, it must be set up from scratch and wired into the Frappe build pipeline.

**Mitigation:** Create a standalone `portal-vue/` project at the repo root. The existing `student-portal-vue/` is not modified. The new project copies `useFrappe.js` and layout patterns. Build is run independently: `cd portal-vue && npm run build`.

### Risk 4: `University VC` Role Name Conflict

**Issue:** Frappe Role names must be unique globally. If another app (ERPNext, HRMS) already has a Role named "University VC" or "University Dean", the fixture import will fail or silently overwrite.

**Mitigation:** Check `frappe.db.exists("Role", "University VC")` before adding to fixtures. These are custom names prefixed with "University" — very unlikely to conflict. Low risk.

### Risk 5: `get_all_kpis` N+1 in analytics/api.py

**Issue:** `get_all_kpis()` (lines 198–225) also has an N+1 pattern — it fetches all KPIs then fires one `frappe.db.get_value("KPI Value", ...)` per KPI. This was not in the locked decisions but is in the same file as the permission check work.

**Mitigation:** Fix the N+1 in `get_all_kpis()` in the same task as the permission check work (same file, adjacent lines). Use the same GROUP BY / subquery pattern as `get_kpi_summary()`.

---

## Sources

### Primary (HIGH confidence — direct file reads)

All findings derived from direct reads of files in the repository. No external sources needed.

| File | What Was Inspected |
|------|-------------------|
| `analytics/dashboard_engine.py` lines 140–171 | SQL injection: exact variable names, exact lines |
| `analytics/api.py` full file | All 8 endpoints, permission check presence/absence |
| `analytics/dashboards/executive_dashboard.py` full file | N+1 loops: exact functions, line numbers, helper calls |
| `student-portal-vue/vite.config.js` | Exact base/outDir values |
| `student-portal-vue/src/router/index.js` | Exact auth guard pattern |
| `student-portal-vue/src/composables/useAuth.js` | Existing auth composable |
| `student-portal-vue/src/composables/useFrappe.js` | API wrapper pattern |
| `student-portal-vue/src/layouts/StudentLayout.vue` | Sidebar structure |
| `student-portal-vue/src/layouts/AdminLayout.vue` | Admin layout variant |
| `student-portal-vue/package.json` | Exact package versions |
| `www/student_portal/index.py` | www page pattern (get_context, manifest read) |
| `www/student_portal/index.html` | SPA shell template structure |
| `university_portals/api/portal_api.py` | Whitelist pattern, student auth pattern |
| `fixtures/role.json` | All existing roles, exact JSON structure |
| `hooks.py` | Fixture filter pattern |
| `education/doctype/fee_structure/fee_structure.json` | `receivable_account`, `income_account` field names |
| `education/doctype/academic_year/academic_year.json` | `year_start_date`, `year_end_date` field names |
| `education/doctype/academic_term/academic_term.json` | `term_start_date`, `term_end_date` field names |
| `education/doctype/program_enrollment/program_enrollment.json` | `student` link field |
| `faculty_management/doctype/faculty_profile/faculty_profile.json` | `employee` link field |
| `.planning/REQUIREMENTS.md` | FOUND-01 through FOUND-08 |
| `.planning/config.json` | `nyquist_validation: true` |

## Metadata

**Confidence breakdown:**
- Security fixes (SQL injection, permission checks, N+1): HIGH — exact lines read, exact pattern identified
- Vue app shell structure: HIGH — existing patterns read; Pinia pattern is well-established Vue 3 practice
- Health check field names: HIGH — all doctype JSONs read directly
- Role fixture pattern: HIGH — `fixtures/role.json` and `hooks.py` both read

**Research date:** 2026-03-18
**Valid until:** 2026-04-17 (30 days — all findings are from local codebase, not external sources)
