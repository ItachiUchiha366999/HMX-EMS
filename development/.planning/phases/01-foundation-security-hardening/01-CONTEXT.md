# Phase 1: Foundation & Security Hardening - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix backend security vulnerabilities (SQL injection, missing permission checks, N+1 queries), verify cross-app data integrity, create two new Frappe roles, and build the unified Vue 3 portal app shell at `/portal/` with RBAC-driven navigation.

This phase delivers: secure backend + unified Vue app shell that routes and renders based on user's Frappe roles. No portal-specific views are built yet — that's Phases 3–6. This phase builds the foundation every portal module will sit on.

</domain>

<decisions>
## Implementation Decisions

### Vue App Shell Architecture
- **New unified Vue 3 app at `/portal/`** — separate from the existing student portal at `/student_portal/` (which stays unchanged)
- The unified portal is a **custom-designed Frappe desk replacement** — same RBAC model as Frappe desk, but with the project's own UI/design system
- Single URL for all users: `/portal/` — the page content adapts based on the user's Frappe roles (not separate URLs per role)
- After Phases 3–6 complete, the student module from `/student_portal/` will migrate into the unified app; for now both coexist
- Vite base URL: `/portal/` — new Vite config, new build output directory separate from student-portal-spa

### Role-to-Route Mapping (RBAC)
- **Frappe roles drive everything** — the Vue app fetches the user's active Frappe roles on boot; each sidebar item and route has a `roles[]` list; if user has any matching role, the item is visible
- This mirrors exactly how Frappe desk works — same roles, same access model, just a different UI
- **Two new Frappe roles to create**: `University VC` and `University Dean` — used for management dashboard personas in Phase 4
- Multi-role users get a **merged sidebar** showing the union of all permitted items across all their roles — no switcher, no priority hierarchy

### Auth Session Design
- **Pinia store with one-time fetch on app boot** (in `main.js` / app initialization) — fetches user info, roles[], and allowed modules in a single API call
- Re-fetch only on 401 response from any API
- Store contents: `logged_user`, `full_name`, `user_image`, `roles[]`, `allowed_modules[]`
- Custom backend endpoint: `get_session_info()` — returns the above fields; avoids the heavy Frappe boot payload
- Replaces the existing per-route `frappe.auth.get_logged_user` pattern in `student-portal-vue/src/router/index.js`

### Security Fixes (Backend)
- **SQL injection** in `dashboard_engine.py:158-164`: replace f-string filter interpolation with parameterized queries (`frappe.db.sql(..., values)`)
- **Permission checks**: all analytics and dashboard API endpoints must verify `frappe.has_permission()` before returning data — currently missing on several endpoints in `analytics/api.py`
- **N+1 queries** in `executive_dashboard.py`: replace sequential per-department/per-program queries with aggregated SQL using `GROUP BY`

### Cross-App Health Check
- **Health-check API endpoint**: `@frappe.whitelist()` method `university_erp.health_check.run_checks()` — accessible at `/api/method/university_erp.health_check.run_checks`
- Returns JSON: `{"status": "ok"|"degraded"|"critical", "checks": [{"name": str, "status": "pass"|"fail"|"warn", "detail": str, "count": int}]}`
- Only callable by `University Admin` role (permission check at top of function)
- **Four checks to implement**:
  1. **Student ↔ Program Enrollment**: every active Student has at least one Program Enrollment; report count of orphaned students
  2. **Fees ↔ ERPNext Accounts**: every Fee Structure references valid, existing GL Accounts (`receivable_account`, `income_account`); report invalid links
  3. **Employee ↔ Faculty Profile**: every Faculty Profile links to a valid Employee; report broken links
  4. **Academic Year/Term consistency**: at least one Academic Year and one Academic Term exist; dates are non-null; report missing/invalid records

### Claude's Discretion
- Exact Pinia store structure (module split vs flat store)
- Error boundary / loading state design for the app shell
- How the sidebar is data-driven (config array vs router meta vs both)
- Specific aggregation SQL query patterns for N+1 fix

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Security vulnerabilities (exact files to fix)
- `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboard_engine.py` lines 155–170 — SQL injection: f-string filter interpolation to replace with parameterized queries
- `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py` — permission check pattern to audit; missing `frappe.has_permission()` calls
- `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/dashboards/executive_dashboard.py` — N+1 pattern: per-entity loop queries to replace with aggregated SQL

### Existing Vue portal (patterns to reuse / base to build from)
- `student-portal-vue/src/main.js` — app bootstrap pattern; auth init to replace with Pinia
- `student-portal-vue/src/router/index.js` — current per-route auth guard (the pattern to replace); 11 student routes as reference
- `student-portal-vue/src/composables/useAuth.js` — existing auth composable to extend or replace
- `student-portal-vue/src/composables/useFrappe.js` — Frappe API wrapper to reuse
- `student-portal-vue/src/layouts/StudentLayout.vue` — layout pattern to adapt for unified portal
- `student-portal-vue/src/layouts/AdminLayout.vue` — admin layout variant (already exists)
- `student-portal-vue/vite.config.js` — Vite config template; new app needs same structure with different base/outDir

### Backend portal API patterns
- `frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py` — existing whitelisted API pattern for portal methods; student auth pattern (`get_current_student()`) to parallel for faculty/parent

### Requirements driving this phase
- `.planning/REQUIREMENTS.md` — FOUND-01 through FOUND-08 (all 8 Foundation requirements)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `student-portal-vue/src/composables/useFrappe.js` — Frappe API wrapper (fetch, error handling); reuse directly in the new unified app
- `student-portal-vue/src/composables/useAuth.js` — auth composable; extend to support Pinia store + roles
- `student-portal-vue/src/layouts/AdminLayout.vue` — already exists; can serve as base for the unified layout shell
- `student-portal-vue/src/layouts/StudentLayout.vue` — sidebar/nav pattern reference

### Established Patterns
- Frappe whitelisted APIs (`@frappe.whitelist()`) — existing pattern for all backend methods; health check follows same pattern
- Vite build → `public/[spa-name]/` → loaded via Jinja manifest in `www/[page]/index.py` — this pattern exists for student portal; replicate for `/portal/`
- Vue Router `beforeEach` guard — exists in student router; Phase 1 replaces the per-route API call with a Pinia store check

### Integration Points
- New Frappe www page needed: `university_erp/www/portal/index.py` + `index.html` — SPA shell for the unified portal (parallel to `www/student_portal/index.py`)
- New Vite project or new Vite config entry in `student-portal-vue/` for the unified portal build
- New `health_check.py` module in `university_erp/university_erp/` — standalone, callable via API
- Two new Role records in Frappe DB: `University VC`, `University Dean`

</code_context>

<specifics>
## Specific Ideas

- "I want the same features and doctypes like Frappe app but with my own design and UI" — the portal is a full RBAC application, not just a student/faculty view. Think Frappe desk reimagined with custom design.
- The sidebar should dynamically show/hide items based on the user's roles — exactly like Frappe's module menu, but styled per the project's design system.
- No new doctypes — all data already exists; this phase is purely about infrastructure, security, and the app shell scaffold.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation-security-hardening*
*Context gathered: 2026-03-18*
