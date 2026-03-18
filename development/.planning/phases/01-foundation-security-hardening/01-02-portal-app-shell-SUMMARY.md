---
phase: 01-foundation-security-hardening
plan: 02
subsystem: ui
tags: [vue3, vite, pinia, vue-router, portal, spa]

# Dependency graph
requires:
  - phase: 01-foundation-security-hardening/01
    provides: "Security-hardened backend APIs, University VC/Dean roles"
provides:
  - "portal-vue/ standalone Vite project (buildable with npm run build)"
  - "Pinia session store with one-time fetchSession() boot action"
  - "Vue Router with role-aware beforeEach guard (no per-route API calls)"
  - "Sidebar component with role-filtered navigation items"
  - "navigation.js config array driving sidebar and route definitions"
  - "get_session_info() whitelisted backend endpoint returning user/roles/modules"
  - "www/portal/ Frappe page serving the SPA at /portal/"
affects: [phase-01-plan-03, phase-02, phase-03, phase-04, phase-05, phase-06]

# Tech tracking
tech-stack:
  added: [vue-3.4, pinia-2.1, vue-router-4.3, vite-5]
  patterns: [pinia-session-store-boot-fetch, role-filtered-navigation, vite-manifest-frappe-integration]

key-files:
  created:
    - portal-vue/package.json
    - portal-vue/index.html
    - portal-vue/vite.config.js
    - portal-vue/src/main.js
    - portal-vue/src/App.vue
    - portal-vue/src/stores/session.js
    - portal-vue/src/config/navigation.js
    - portal-vue/src/router/index.js
    - portal-vue/src/layouts/PortalLayout.vue
    - portal-vue/src/components/Sidebar.vue
    - frappe-bench/apps/university_erp/university_erp/www/portal/index.py
    - frappe-bench/apps/university_erp/university_erp/www/portal/index.html
  modified:
    - frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py

key-decisions:
  - "Used window.frappe?.csrf_token instead of bare frappe?.csrf_token for explicit global reference"
  - "Build output committed to public/portal/ matching existing student-portal-spa pattern"
  - "Task 1 files were already committed by Plan 01 executor -- Task 2 committed separately"

patterns-established:
  - "Pinia boot pattern: fetchSession() in main.js before app.mount(), guard reads store synchronously"
  - "Role-filtered navigation: navItems config array with roles[], Sidebar filters via computed intersection"
  - "Frappe SPA integration: www/page/index.py reads .vite/manifest.json, injects hashed asset URLs via Jinja"

requirements-completed: [FOUND-05, FOUND-06, FOUND-07, FOUND-08]

# Metrics
duration: 11min
completed: 2026-03-18
---

# Phase 1 Plan 2: Portal App Shell Summary

**Standalone portal-vue/ Vite project with Pinia session store, role-filtered sidebar, Vue Router auth guard, and Frappe www/portal/ SPA mount point**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-18T13:30:32Z
- **Completed:** 2026-03-18T13:41:40Z
- **Tasks:** 2
- **Files modified:** 13

## Accomplishments
- Created portal-vue/ Vite project scaffold (package.json, vite.config.js, index.html) building to public/portal/ with base /assets/university_erp/portal/
- Implemented Pinia session store with single-call fetchSession() at boot, eliminating per-route API calls (addresses the anti-pattern in student-portal-vue)
- Built role-filtered Sidebar component driven by navigation.js config -- multi-role users see union of all permitted nav items
- Created www/portal/ Frappe page with Guest redirect to /login and Vite manifest integration for production asset loading
- Added get_session_info() whitelisted endpoint returning {logged_user, full_name, user_image, roles[], allowed_modules[]}
- Verified Vite build succeeds -- 96.95KB JS + 1.67KB CSS gzipped to 37.77KB + 0.63KB

## Task Commits

Each task was committed atomically:

1. **Task 1: Scaffold portal-vue/ project and backend get_session_info() endpoint** - `75e893c6` (feat) -- Note: committed by Plan 01 executor
2. **Task 2: Vue Router, PortalLayout, Sidebar, and Frappe www page** - `cab11757` (feat)

## Files Created/Modified
- `portal-vue/package.json` - Project manifest with vue, pinia, vue-router, vite dependencies
- `portal-vue/vite.config.js` - Vite config targeting public/portal/ with manifest generation
- `portal-vue/index.html` - Vite entry point for dev server
- `portal-vue/src/main.js` - App bootstrap: Pinia + Router + session fetch before mount
- `portal-vue/src/App.vue` - Minimal root component with RouterView
- `portal-vue/src/stores/session.js` - Pinia store: fetchSession(), isAuthenticated, hasRole, hasAnyRole
- `portal-vue/src/config/navigation.js` - navItems array with path/label/icon/roles for 8 nav entries across all personas
- `portal-vue/src/router/index.js` - Vue Router with createWebHistory('/portal/'), session-based auth guard, placeholder routes
- `portal-vue/src/layouts/PortalLayout.vue` - Flex layout: Sidebar + RouterView content area
- `portal-vue/src/components/Sidebar.vue` - Role-filtered nav links, user info, sign-out
- `frappe-bench/.../university_portals/api/portal_api.py` - Appended get_session_info() returning user/roles/modules
- `frappe-bench/.../www/portal/index.py` - get_context() with Guest redirect and Vite manifest reader
- `frappe-bench/.../www/portal/index.html` - SPA shell with spinner, Jinja asset injection, fallback message

## Decisions Made
- Used `window.frappe?.csrf_token` (explicit global) instead of bare `frappe?.csrf_token` for clarity in the Pinia store
- Committed Vite build output to public/portal/ matching the existing student-portal-spa pattern (build artifacts are tracked in this repo)
- Task 1 files were already committed by the Plan 01 executor (commit 75e893c6) -- this is a deviation from expected atomicity but the content is correct

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1 files already committed by Plan 01 executor**
- **Found during:** Task 1 staging
- **Issue:** All 8 Task 1 files (portal-vue scaffold + portal_api.py changes) were already committed in commit 75e893c6 by the Plan 01 executor, bundled with Plan 01's security fixes
- **Fix:** Verified content matches plan spec exactly, proceeded without re-committing. Task 2 files committed separately as planned.
- **Files modified:** None (already committed)
- **Verification:** git show 75e893c6 --stat confirms all expected files present

---

**Total deviations:** 1 (pre-existing commit from prior plan execution)
**Impact on plan:** No impact on correctness. All files exist with correct content. Only the commit boundary differs from ideal.

## Issues Encountered
- Git index.lock file appeared during initial commit attempts, resolved by removing stale lock file
- Git root is /workspace/ not /workspace/development/ -- required adjusting all git add paths

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- portal-vue/ is ready for Plan 03 (integration wiring: build verification, Frappe routing, endpoint access control)
- Phase 2 (shared component library) can begin adding components into portal-vue/src/components/
- All placeholder routes in router/index.js are ready to be replaced with real views in Phases 3-6

## Self-Check: PASSED

All 13 created files verified present on disk. Both commit hashes (75e893c6, cab11757) verified in git log.

---
*Phase: 01-foundation-security-hardening*
*Completed: 2026-03-18*
