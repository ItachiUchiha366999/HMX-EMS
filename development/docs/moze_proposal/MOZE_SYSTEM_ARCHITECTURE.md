# G.S. MOZE Educational Trust — University ERP System Architecture
## Comprehensive Enterprise Architecture Document

**Document Version:** 2.0
**Platform:** Frappe v16 + ERPNext + HRMS + Frappe Education + university_erp (custom app)
**Frontend:** portal-vue — Vue 3.5 SPA (unified portal for all non-admin roles)
**Date:** March 2026
**Prepared For:** G.S. MOZE Educational Trust, Pune, Maharashtra

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [Two-Tier Architecture: The Core Design Principle](#2-two-tier-architecture-the-core-design-principle)
3. [Portal-Vue: The Unified Frontend](#3-portal-vue-the-unified-frontend)
4. [Role-Based Access Control (RBAC)](#4-role-based-access-control-rbac)
5. [Backend Modular Architecture](#5-backend-modular-architecture)
6. [API Layer: Portal-First Design](#6-api-layer-portal-first-design)
7. [Data Flow Between Modules](#7-data-flow-between-modules)
8. [Company-Based Multi-Tenant Architecture](#8-company-based-multi-tenant-architecture)
9. [Improvements Over Default ERPNext](#9-improvements-over-default-erpnext)
10. [Infrastructure and Deployment](#10-infrastructure-and-deployment)
11. [Regulatory Compliance Architecture](#11-regulatory-compliance-architecture)
12. [Security Architecture](#12-security-architecture)

---

## 1. Executive Overview

### 1.1 Trust Profile

| Dimension            | Detail                                                                |
|----------------------|-----------------------------------------------------------------------|
| Client               | G.S. MOZE Educational Trust                                           |
| Headquarters         | Pune, Maharashtra, India                                              |
| Campuses             | 13 physical campuses                                                  |
| Institutes           | 19 institutes (each a Frappe Company entity)                         |
| Students             | ~25,000 active                                                        |
| Staff (all types)    | ~1,500–2,000 employees                                                |
| Regulatory Bodies    | AICTE, SPPU, NCTE, PCI, State Board, NAAC, NBA, DPDP, UDISE+         |
| Languages            | Marathi + English (bilingual UI)                                      |

### 1.2 Institute Types

```
G.S. MOZE Educational Trust
├── Engineering Colleges (AICTE / SPPU)          — 4-year B.E./M.E./MBA programs
├── Pharmacy Colleges (PCI / SPPU)               — B.Pharm, M.Pharm, D.Pharm
├── Arts, Commerce & Science Colleges (SPPU)     — BA, BCom, BSc, MA, MCom, MSc
├── B.Ed / M.Ed Colleges (NCTE / SPPU)           — Teacher education programs
├── D.Ed Institutes (NCTE / State Board)         — Diploma in Education (2-year)
├── Junior Colleges (State Board)                — HSC (11th–12th Std)
└── Schools (CBSE / SSC State Board)             — Primary + Secondary (K–10)
```

### 1.3 Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                               │
│                                                                          │
│  ┌────────────────────────────────────────────────────┐  ┌────────────┐ │
│  │           portal-vue  (Vue 3.5 SPA)                │  │   Frappe   │ │
│  │    https://erp.moze.edu.in/portal/                 │  │    Desk    │ │
│  │                                                    │  │  /app/     │ │
│  │  Faculty · HOD · Student · Parent · Management     │  │            │ │
│  │  Finance · Registrar · Placement · Alumni          │  │ System     │ │
│  │                                                    │  │ Admins     │ │
│  │  ALL non-admin users — one codebase, role routing  │  │ ONLY       │ │
│  └────────────────────────────────────────────────────┘  └────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                         APPLICATION LAYER                                │
│  university_erp (custom app)  — 17 modules, ~204 DocTypes               │
│  university_portals/api/      — portal_api.py, faculty_api.py           │
│  Frappe Education             — Programs, Courses, Students              │
│  ERPNext                      — Accounts, HR base                        │
│  HRMS                         — Payroll, Leave, Attendance               │
├─────────────────────────────────────────────────────────────────────────┤
│                         FRAMEWORK LAYER                                  │
│  Frappe v16 — ORM, Auth, Workflow, REST API, Scheduler, PDF             │
├─────────────────────────────────────────────────────────────────────────┤
│                         DATA LAYER                                       │
│  MariaDB 10.6+  │  Redis (Cache / Queue / SocketIO pub-sub)             │
├─────────────────────────────────────────────────────────────────────────┤
│                         INFRASTRUCTURE LAYER                             │
│  Nginx (Reverse Proxy + Static Assets)  │  Supervisor (Processes)       │
│  Docker / Frappe Bench                  │  S3-compatible (File Storage)  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Two-Tier Architecture: The Core Design Principle

### 2.1 Architectural Split

This platform deliberately departs from the traditional ERPNext model where all users — staff, faculty, students, and administrators alike — work inside Frappe Desk. MOZE ERP uses a hard two-tier split:

```
┌───────────────────────────────────────────────────────────────────┐
│                         TIER 1                                    │
│                   FRAPPE DESK  (/app/)                            │
│                                                                   │
│  Audience: System administrators ONLY                             │
│  Access:   System Manager role  +  Education Manager role        │
│                                                                   │
│  Responsibilities:                                                │
│  • DocType configuration and custom field management             │
│  • Workflow definition and fixture management                    │
│  • System health, scheduler monitoring, error logs               │
│  • HRMS payroll processing (back-office staff only)              │
│  • ERPNext GL ledger reconciliation (finance back-office)        │
│  • User account creation, role assignment                        │
│  • Frappe site maintenance and migrations                        │
│                                                                   │
│  Who does NOT use Desk:                                           │
│  Students, Faculty, HODs, Principals, Registrars, Parents,       │
│  Finance Officers, Placement Officers, Library Staff, any        │
│  user with a University* role — NONE of them use /app/           │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                         TIER 2                                    │
│              PORTAL-VUE  (/portal/)                               │
│                                                                   │
│  Audience: Everyone else — all 25,000 students, ~2,000 faculty,  │
│            HODs, Registrars, Finance Officers, Management, etc.   │
│                                                                   │
│  Technology: Vue 3.5 SPA — single codebase, role-based routing   │
│  URL:        https://erp.moze.edu.in/portal/                     │
│                                                                   │
│  One portal, many faces — role determines what you see:          │
│  • University Faculty   → Faculty dashboard + teaching tools     │
│  • University HOD       → Faculty view + dept management layer   │
│  • University Student   → Academic data, fees, exams, services   │
│  • University Admin     → Management dashboards, system health   │
│  • University VC/Dean   → Cross-institute analytics              │
│  • University Finance   → Fee collection, reconciliation         │
│  • University Parent    → Ward's data (attendance, fees, grades) │
│  • University Registrar → Admissions, enrollment, merit lists    │
│  • University Alumni    → Alumni services and connections        │
└───────────────────────────────────────────────────────────────────┘
```

### 2.2 Why This Split Matters

**For MOZE specifically:** The trust operates 19 institutes with 25,000 students. Frappe Desk was designed for ERP power-users — its generic list/form/report paradigm is appropriate for system administration but inappropriate for students looking up their timetable or faculty marking attendance. Building purpose-built views for each role in portal-vue provides:

- Appropriate information density per role (a student does not need to see GL entries)
- Mobile-first design for students (Desk is desktop-centric)
- Zero accidental modification of data structures by non-admin users
- Role-specific UX flows that would be impossible to achieve in generic Desk workspaces
- A single consistent design system across all user types

**For MOZE's 19 companies:** Every institute's users share the same portal-vue frontend. The company filter (enforced in both the Vue router guards AND the Python backend) ensures that a faculty member at GSMCOE Balewadi and a faculty member at PG MOZE Wagholi use identical UI code — what differs is the data that the backend returns, scoped to their respective companies.

### 2.3 Authentication and Login Flow

```
User navigates to any MOZE ERP URL
             │
             ▼
   www/portal/index.py  (Frappe serves the SPA shell)
             │
   ┌─────────▼──────────┐
   │  Guest user?        │──Yes──► Redirect to /login?redirect-to=/portal/
   └─────────┬──────────┘
             │ No (authenticated)
             ▼
   Serve portal/index.html (Vite-built SPA shell)
             │
             ▼
   Vue app boots: main.js
             │
   sessionStore.fetchSession()  ← ONE API call before mount
   /api/method/university_erp.university_portals.api.portal_api.get_session_info
             │
   Session store populated:
   { logged_user, full_name, user_image, roles[], allowed_modules[] }
             │
             ▼
   app.mount('#app')
             │
             ▼
   Vue Router beforeEach guard:
   ├── sessionStore.isAuthenticated? No  → window.location = /login
   └── Yes → resolve route
             │
             ▼
   Role-filtered navigation rendered
   User lands on their role-appropriate home route
```

**Boot session enrichment** (`university_erp/boot.py::boot_session`):

On every Frappe login, the following is injected into the client-side boot object (available as `window.frappe.*`):
- `university_settings` — grading scale, attendance thresholds, minimum passing grade
- `university_roles` — filtered list of `University*` prefixed roles for the user
- `current_academic_year` — the active academic year name
- `payment_settings` — enabled gateways (Razorpay / PayU), non-sensitive config only
- `csrf_token` — reused by useFrappe.js for all subsequent API calls

### 2.4 Serving the Portal SPA

The portal is a Frappe `www` page at `university_erp/www/portal/index.py`. It:

1. Rejects Guest users with a redirect to Frappe's `/login` page (passing `redirect-to=/portal/` so post-login navigation returns to the portal)
2. Reads the Vite build manifest (`public/portal/.vite/manifest.json`) to resolve content-hashed asset filenames
3. Passes the resolved JS and CSS paths into the Jinja context (`context.vue_js`, `context.vue_css`)
4. Renders `www/portal/index.html` — a minimal shell that loads the Vue bundle

Vue Router is configured with `createWebHistory('/portal/')` so all sub-paths (`/portal/faculty`, `/portal/student`, etc.) resolve to this single entry point. Deep-link support is provided by a Frappe website route rule:

```python
# hooks.py
website_route_rules = [
    {"from_route": "/portal/<path:app_path>", "to_route": "portal"},
]
```

---

## 3. Portal-Vue: The Unified Frontend

### 3.1 Technical Stack

| Component     | Technology             | Version  | Purpose                                              |
|---------------|------------------------|----------|------------------------------------------------------|
| Framework     | Vue                    | 3.5      | Reactive component model                             |
| Router        | Vue Router             | 4.6      | Client-side routing with history mode                |
| State         | Pinia                  | 2        | Session store, shared state across components        |
| Build         | Vite                   | 5        | Dev server + production builds (output: public/portal/) |
| Tables        | TanStack Table         | 8.x      | Headless data tables (grade grid, student lists)     |
| Charts        | ApexCharts + vue3-apexcharts | 5.x | Attendance charts, analytics panels                  |
| PDF export    | jsPDF + jsPDF-autotable | 4.x     | Client-side PDF generation for reports               |
| Excel export  | ExcelJS                | 4.x      | Grade exports, attendance sheets                     |
| Testing       | Vitest + @vue/test-utils + vitest-axe | 3.x | Unit tests + WCAG 2.1 AA accessibility checks |

**Source location:** `/workspace/development/portal-vue/`
**Build output:** `university_erp/public/portal/` (served at `/assets/university_erp/portal/`)

### 3.2 Application Boot Sequence

```
1. Frappe serves www/portal/index.html (SPA shell)
2. Browser loads hashed JS bundle from /assets/university_erp/portal/assets/
3. main.js executes:
   a. createApp(App)
   b. createPinia() → app.use(pinia)
   c. app.use(router)
   d. sessionStore.fetchSession()  ← awaited BEFORE mount
      → GET /api/method/…portal_api.get_session_info
      → Populates: logged_user, full_name, user_image, roles[], allowed_modules[]
      → Fallback: reads window.frappe.session if API fails (page context injection)
   e. app.mount('#app')
4. Vue Router resolves the current URL path
5. beforeEach guard checks sessionStore.isAuthenticated
6. PortalLayout renders: Sidebar + <RouterView />
7. Sidebar renders navigation items filtered by session roles
8. Route component loads (lazy-imported)
```

The one-time session fetch (step 3d) is the only unconditional API call. All subsequent data fetching is driven by component lifecycle hooks and user interactions. There are no per-route session checks — the store is the source of truth for the lifetime of the SPA session.

### 3.3 Component Tree

```
App.vue
└── RouterView
    └── PortalLayout.vue  (shell: sidebar + main content area)
        ├── <a href="#main-content" class="skip-to-content">  ← WCAG 2.1 AA
        ├── Sidebar.vue
        │   ├── Institute logo
        │   ├── User avatar + full name (from sessionStore)
        │   ├── Navigation items  (filtered by sessionStore.roles)
        │   │   └── config/navigation.js  ← single source of truth
        │   └── Logout link
        │
        └── <main id="main-content">
            └── <RouterView />  ← active route component
```

**Shared components** (`src/components/shared/`):

| Component           | Technology basis  | Usage                                              |
|---------------------|-------------------|----------------------------------------------------|
| KpiCard             | CSS Grid          | Metric tiles on all dashboards                     |
| ChartWrapper        | ApexCharts        | Attendance gauges, grade distributions, analytics  |
| DataTable           | TanStack Table    | Grade grids, student lists, leave history          |
| FilterBar           | Vue reactive      | Course/term/batch filter controls                  |
| NotificationPanel   | Frappe SocketIO   | Real-time notice board overlay                     |
| ReportViewer        | DataTable + export | Tabular reports with PDF/Excel download           |
| SkeletonLoader      | CSS animation     | Loading state placeholder for async data           |
| ToastNotification   | useToast composable | Success/error transient messages                 |

**Faculty components** (`src/components/faculty/`):

| Component              | Route                     | Purpose                                          |
|------------------------|---------------------------|--------------------------------------------------|
| FacultyDashboard.vue   | /faculty                  | KPI cards, today's timetable, quick actions      |
| FacultyTeaching.vue    | /faculty/teaching         | Tabbed: Timetable, Attendance, Grades, Students  |
| FacultyWork.vue        | /faculty/work             | Leave, LMS, Research, OBE, Workload              |
| FacultyNotices.vue     | /faculty/notices          | Notice board, announcement publisher             |
| TimetableGrid.vue      | (child)                   | Full weekly timetable, slot-based grid           |
| TimetableToday.vue     | (child)                   | Today's classes card with quick-mark link        |
| AttendanceMarker.vue   | (child)                   | Per-session student attendance submission        |
| FacultyGradeGrid.vue   | (child)                   | TanStack Table grade entry + draft/submit flow   |
| GradeAnalyticsPanel.vue| (child)                   | ApexCharts grade distribution charts             |
| StudentListView.vue    | (child)                   | Paginated student list with detail panel         |
| StudentDetailPanel.vue | (child)                   | Per-student profile, attendance, grades          |
| PerformanceAnalytics.vue| (child)                  | Class-level performance over time                |
| LeaveBalanceCards.vue  | (child)                   | Leave type balances from HRMS                    |
| LeaveApplyForm.vue     | (child)                   | Leave application submission form                |
| StudentLeaveQueue.vue  | (child)                   | HOD leave approval queue                         |
| LmsCourseList.vue      | (child)                   | Assigned LMS courses list                        |
| LmsContentManager.vue  | (child)                   | Module/content/assignment management             |
| LmsContentForm.vue     | (child)                   | Create/edit LMS content item                     |
| ResearchPublications.vue| (child)                  | Faculty publication list and entry               |
| ObeAttainment.vue      | (child)                   | CO-PO attainment matrix view                     |
| WorkloadSummary.vue    | (child)                   | Teaching hours vs. norm, course-wise breakdown   |
| TabLayout.vue          | (child)                   | Reusable tab container for FacultyWork           |

### 3.4 Route Table

| Route            | Component              | Allowed Roles                                           | Phase Status   |
|------------------|------------------------|---------------------------------------------------------|----------------|
| /faculty         | FacultyDashboard       | University Faculty, University HOD                      | Complete       |
| /faculty/teaching| FacultyTeaching        | University Faculty, University HOD                      | Complete       |
| /faculty/work    | FacultyWork            | University Faculty, University HOD                      | Complete       |
| /faculty/notices | FacultyNotices         | University Faculty, University HOD                      | Complete       |
| /hod             | ComingSoon             | University HOD                                          | Phase 6        |
| /management      | ComingSoon             | University Admin, University VC, University Dean, University Registrar | Phase 4 |
| /student         | ComingSoon             | University Student                                      | Phase 03.2     |
| /finance         | ComingSoon             | University Finance, University Admin                    | Phase 4        |
| /admin/health    | ComingSoon             | University Admin                                        | Phase 4        |

Legacy redirect aliases (from pre-refactor routes):
```
/faculty/attendance  →  /faculty/teaching?tab=attendance
/faculty/grades      →  /faculty/teaching?tab=grades
```

### 3.5 Navigation Configuration

`src/config/navigation.js` is the **single source of truth** for both sidebar rendering and route-level role metadata. Each nav item declares which Frappe roles grant access:

```js
// Multi-role users see the UNION of all items their roles permit.
{ path: '/faculty',     roles: ['University Faculty', 'University HOD'] }
{ path: '/hod',         roles: ['University HOD'] }
{ path: '/management',  roles: ['University Admin', 'University VC', 'University Dean', 'University Registrar'] }
{ path: '/student',     roles: ['University Student'] }
{ path: '/finance',     roles: ['University Finance', 'University Admin'] }
{ path: '/admin/health',roles: ['University Admin'] }
```

The Sidebar component filters `navItems` using `sessionStore.hasAnyRole(item.roles)`. A HOD user sees both `/faculty/*` items (teaching duties) AND `/hod` (department oversight). This role-union behavior is by design — HODs are faculty with additional management scope.

### 3.6 Composables (API and Utility Layer)

All Frappe backend communication goes through composables. No component calls `fetch()` directly.

#### useFrappe.js — Base API client

Wraps all `@frappe.whitelist` calls with:
- CSRF token injection (`X-Frappe-CSRF-Token` from `window.frappe.csrf_token` or cookie)
- `credentials: 'same-origin'` (session cookie forwarding)
- 401 handling → redirects to `/login?redirect-to=/portal/`
- 403 handling → throws `'Permission denied'` (component shows error, no redirect)
- Frappe exception extraction (`data.exc` / `data._server_messages`)
- `loading` and `error` reactive refs for component UI state

```
useFrappe().call(method, params, options)    — POST by default, GET with options.method
useFrappe().getList(doctype, queryOptions)  — wraps frappe.client.get_list
```

#### useFacultyApi.js — Faculty domain API (27 endpoints)

Delegates all calls to `university_erp.university_portals.api.faculty_api.*`:

| Category     | Endpoints (count) | Examples                                         |
|--------------|-------------------|--------------------------------------------------|
| Dashboard    | 3                 | getDashboard, getTodayClasses, getWeeklyTimetable|
| Attendance   | 2                 | getStudentsForAttendance, submitAttendance        |
| Grades       | 6                 | getStudentsForGrading, saveDraftGrade, submitGrades, getGradeAnalytics, getStudentList, getStudentDetail |
| Performance  | 2                 | getPerformanceAnalytics, getAnnouncements        |
| Leave        | 6                 | getLeaveBalance, applyLeave, getLeaveHistory, getStudentLeaveRequests, approveStudentLeave, rejectStudentLeave |
| LMS          | 4                 | getLmsCourses, getLmsCourseContent, saveLmsContent, deleteLmsContent |
| Research+OBE | 3                 | getPublications, getCopoMatrix, getCopoStudentDetail |
| Workload     | 1                 | getWorkloadSummary                               |

#### Other composables

| Composable        | Purpose                                                        |
|-------------------|----------------------------------------------------------------|
| useExportPdf.js   | jsPDF + jsPDF-autotable — client-side PDF generation          |
| useExportExcel.js | ExcelJS — client-side XLSX generation                         |
| useReportRunner.js| Generic report fetch + format for ReportViewer component      |
| useThemeColors.js | Reads CSS custom properties (`--primary`, `--success`, etc.) for ApexCharts |
| useToast.js       | Transient toast notification queue (success / error / info)   |

### 3.7 Theming and Accessibility

**Theme:** CSS custom properties define all design tokens. Dark mode is toggled via `data-theme="dark"` on the root element. No Frappe Desk CSS bleeds into the portal — the SPA has its own scoped stylesheet.

```css
/* Core tokens (light mode defaults) */
--primary: #4F46E5
--success: #16A34A
--error:   #DC2626
--bg-surface, --bg-page, --font-family, --radius-md, etc.
```

**Accessibility (WCAG 2.1 AA):**
- `PortalLayout.vue` includes a skip-to-content link (`href="#main-content"`) that appears on keyboard focus
- All shared components are tested with `vitest-axe` (axe-core) for WCAG 2.1 AA compliance
- `<main id="main-content">` is the landmark target for the skip link
- Color tokens are validated for 4.5:1 contrast ratio (text against backgrounds)

### 3.8 Faculty Dashboard Layout (Implemented)

```
┌──────────────────────────────────────────────────────────────────────┐
│  MOZE ERP  [Faculty: Dr. Suresh Patil · GSMCOE Balewadi]  [🔔]      │
├──────────────────┬───────────────────────────────────────────────────┤
│                  │                                                    │
│  Dashboard       │   Good morning, Dr. Patil!  |  AY: 2025-26 Even  │
│  Teaching        │                                                    │
│  My Work         │  ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  Notices         │  │ Today's    │ │  Pending   │ │   Leave    │    │
│  ─────────────   │  │ Classes: 3 │ │ Attendance │ │  Balance   │    │
│  Dept Overview   │  │            │ │  42 stud.  │ │  CL: 8    │    │
│  (HOD only)      │  └────────────┘ └────────────┘ └────────────┘    │
│                  │                                                    │
│                  │  TODAY'S TIMETABLE                                 │
│                  │  ┌─────────────────────────────────────────────┐  │
│                  │  │ 09:00  Data Structures   Room 204  Div A    │  │
│                  │  │ 11:00  DBMS              Room 106  Div B    │  │
│                  │  │ 14:00  DBMS Lab          Lab 3    Group 3  │  │
│                  │  └─────────────────────────────────────────────┘  │
│                  │                                                    │
│                  │  QUICK ACTIONS                                     │
│                  │  [Mark Attendance]  [Enter Grades]  [Apply Leave] │
└──────────────────┴───────────────────────────────────────────────────┘
```

**FacultyTeaching.vue** uses a tab layout for:
- **Timetable** — full weekly grid (TimetableGrid) + today card (TimetableToday)
- **Attendance** — course schedule selector → AttendanceMarker (per-student checkboxes, bulk submit)
- **Grades** — assessment plan selector → FacultyGradeGrid (inline edit, draft save, bulk submit) + GradeAnalyticsPanel
- **Students** — StudentListView with StudentDetailPanel sidebar

**FacultyWork.vue** uses TabLayout for:
- **Leave** — LeaveBalanceCards + LeaveApplyForm + leave history DataTable + StudentLeaveQueue (HOD only)
- **LMS** — LmsCourseList → LmsContentManager → LmsContentForm
- **Research** — ResearchPublications (DataTable with add/view)
- **OBE** — ObeAttainment (CO-PO matrix, attainment percentages)
- **Workload** — WorkloadSummary (weekly hours chart, course-wise breakdown)

### 3.9 Development Phases for portal-vue

| Phase   | Description                                             | Status      |
|---------|---------------------------------------------------------|-------------|
| Phase 1 | Foundation: Vite project, Pinia session, PortalLayout, shared components | Complete |
| Phase 2 | Shared components: KpiCard, ChartWrapper, DataTable, FilterBar, etc. | Complete |
| Phase 3 | Faculty Portal: FacultyDashboard, FacultyTeaching, FacultyWork, FacultyNotices — full 27-endpoint API | Complete |
| Phase 03.1 | Cross-app integration audit, SQL security, API permission matrix, a11y testing | Complete |
| Phase 03.2 | Student Portal Recreation — 11 student views replacing Jinja templates | In progress |
| Phase 03.3 | ERPNext Accounts Fork — student-centric fee and finance terminology | Planned |
| Phase 4 | Management Dashboards — VC, Registrar, Finance Officer, Dean views | Planned |
| Phase 5 | Parent Portal                                           | Planned     |
| Phase 6 | HOD Portal (/hod) — department management layer         | Planned     |
| Phase 7 | Scheduled Reports, cross-portal polish, PWA service worker | Planned  |

---

## 4. Role-Based Access Control (RBAC)

### 4.1 Two Layers of Role Enforcement

RBAC in this system operates at two distinct and complementary layers:

**Layer 1 — Vue Router (frontend, UX enforcement)**
- `router.beforeEach` checks `sessionStore.isAuthenticated` on every navigation
- `Sidebar.vue` renders only nav items where `sessionStore.hasAnyRole(item.roles)` is true
- Route components may additionally use `sessionStore.hasRole(role)` to show/hide sub-sections (e.g., StudentLeaveQueue only visible to HOD within FacultyWork)

**Layer 2 — Frappe backend (authoritative enforcement)**
- Every `@frappe.whitelist` endpoint checks `frappe.get_roles()` or uses permission hooks
- `has_permission` callbacks enforce document-level access (own record only for students)
- `permission_query_conditions` inject SQL WHERE clauses into list queries
- Company-based User Permissions filter institute data at the ORM level

Frontend role guards are a UX convenience. The backend is the authoritative security boundary. A user who manually navigates to `/portal/hod` without the HOD role will see placeholder UI, but any API calls will be rejected by the backend with 403.

### 4.2 Role Taxonomy

All custom roles are prefixed with `University` to distinguish them from ERPNext base roles. Frappe's fixture system exports and imports these roles:

```python
# hooks.py fixtures
{"dt": "Role", "filters": [["name", "like", "University%"]]}
```

```
TRUST LEVEL
└── University Trust Admin         (cross-institute, read-only analytics)

INSTITUTE LEVEL (per institute)
├── University Principal           (institute head — full institute view)
├── University VC                  (Vice Chancellor — trust-level academic head)
├── University Dean                (Dean — faculty/academic management)
├── University Registrar           (academics + admissions for institute)
└── University Admin               (operational admin — all modules)

ACADEMIC MANAGEMENT
├── University HOD                 (department-scoped management + faculty duties)
├── University Faculty             (own courses + students)
└── University Lab Assistant       (lab bookings, equipment)

STUDENT SERVICES
├── University Admissions Officer  (application processing, merit lists)
├── University Examinations Staff  (hall tickets, results, schedules)
├── University Hostel Warden       (hostel allocation, attendance)
├── University Transport Manager   (route, vehicle, allocation)
├── University Library Staff       (issue/return, fines)
└── University Placement Officer   (drives, companies, student matching)

HR / PAYROLL
├── University HR Manager          (employee records, org structure)
└── University HR User             (limited HR tasks)

FINANCE
├── University Accounts Manager    (full finance: GL, fee, reconciliation)
└── University Finance             (fee posting, payment verification)

STUDENTS / PORTAL USERS
├── University Student             (own data only — portal /student)
├── University Parent              (ward's data via portal /parent)
└── University Alumni              (alumni portal access)

SYSTEM (Frappe Desk only)
├── System Manager                 (full Frappe Desk access)
└── Education Manager              (ERPNext Education super-role)
```

### 4.3 Portal Role Routing

When a user with multiple roles lands on `/portal/`, the Sidebar shows the union of all their permitted nav items. For role-specific home routes:

```
University Faculty (only)     → /portal/faculty
University HOD                → /portal/faculty + /portal/hod (both visible)
University Student            → /portal/student
University Admin / VC / Dean  → /portal/management
University Finance            → /portal/finance
University Registrar          → /portal/management
University Parent             → /portal/parent  (Phase 5)
University Alumni             → /portal/alumni  (Phase 7)
```

### 4.4 RBAC Matrix: Modules vs. Roles

The matrix uses: **F** = Full CRUD, **R** = Read Only, **L** = Limited (own records), **-** = No access

| Module                  | Sys Mgr | Principal | Registrar | Admin | HOD | Faculty | Exams Staff | Finance  | HR Mgr | Student |
|-------------------------|---------|-----------|-----------|-------|-----|---------|-------------|----------|--------|---------|
| University Admissions   | F       | F         | F         | F     | R   | -       | -           | R        | -      | L       |
| University Student Info | F       | F         | F         | F     | R   | R       | R           | R        | R      | L       |
| University Academics    | F       | F         | F         | F     | F   | L       | R           | -        | -      | R       |
| University Examinations | F       | F         | F         | R     | R   | L       | F           | -        | -      | R       |
| University Finance      | F       | R         | R         | R     | -   | -       | -           | F        | -      | L       |
| Faculty Management      | F       | R         | R         | R     | F   | L       | -           | -        | F      | -       |
| University Hostel       | F       | R         | R         | F     | -   | -       | -           | R        | -      | R       |
| University Transport    | F       | R         | R         | F     | -   | -       | -           | R        | -      | R       |
| University Library      | F       | R         | R         | R     | -   | R       | -           | -        | -      | L       |
| University Placement    | F       | R         | R         | R     | -   | R       | -           | -        | -      | L       |
| University LMS          | F       | R         | R         | R     | R   | F       | -           | -        | -      | R       |
| University Research     | F       | R         | R         | R     | F   | F       | -           | R        | -      | -       |
| University OBE          | F       | R         | R         | R     | F   | F       | R           | -        | -      | -       |
| University Analytics    | F       | R         | R         | R     | R   | -       | -           | R        | R      | -       |
| University Grievance    | F       | R         | R         | F     | R   | R       | -           | -        | -      | L       |
| University Integrations | F       | -         | -         | F     | -   | -       | -           | R        | -      | -       |
| University Payments     | F       | R         | R         | R     | -   | -       | -           | F        | -      | L       |
| University Inventory    | F       | R         | R         | F     | F   | R       | -           | R        | -      | -       |
| University Portals      | F       | R         | R         | F     | -   | -       | -           | -        | -      | L       |
| University Notifications| F       | F         | F         | F     | F   | F       | F           | F        | F      | R       |

**Legend:** L for Student = own record only; L for Faculty = courses they teach; HOD L = own department

### 4.5 Row-Level Security (Backend)

Frappe enforces row-level security through hooks defined in `hooks.py`:

```python
permission_query_conditions = {
    "Student": "university_erp.overrides.student.get_permission_query_conditions",
}

has_permission = {
    "Student": "university_erp.overrides.student.has_permission",
}
```

`get_permission_query_conditions` injects SQL WHERE clauses into list queries:

```
Role: University Student  → WHERE `tabStudent`.`user` = "{current_user}"
Role: University Faculty  → (no SQL filter, dept-level check at API endpoint)
Role: University Admin    → no restriction
Role: System Manager      → no restriction
```

`has_permission` performs document-level checks when a form (or portal API) accesses a specific record:

```
University Student → doc.user == frappe.session.user  (own record only)
University Faculty → allowed if student is in faculty's assigned student groups
University HOD     → allowed for all students in HOD's department
University Admin   → always True
```

### 4.6 Company-Field Based Institute Isolation

Every DocType carrying institute-specific data has a `company` field linking to the Frappe `Company` entity. The 19 institutes map 1:1 to 19 Company documents.

**Isolation is enforced at three levels:**

1. **User-Company Assignment**: Each user is assigned to one or more companies via `User Permission` with `Allow` for `Company`. Frappe automatically applies company filter in list queries.

2. **Default Company in User**: Each user has a `default_company` set during onboarding. New documents default to this company.

3. **Portal API enforcement**: Every endpoint in `faculty_api.py` and `portal_api.py` resolves the current user's Employee or Student record — which is already company-scoped — before querying any data.

```
Trust Admin:    allowed_companies = ["MOZE Trust", ALL 19 institutes]
Principal A:    allowed_companies = ["MOZE Engineering College Pune"]
HOD (Dept CS):  allowed_companies = ["MOZE Engineering College Pune"]
                + department filter = "Computer Science"
Faculty member: allowed_companies = [their institute]
                + teaching assignment filter = their assigned courses only
```

---

## 5. Backend Modular Architecture

### 5.1 Module Organization

```
university_erp/
│
├── university_erp/          ← Core module (cross-cutting concerns)
│   ├── doctype/
│   │   ├── university_settings/     ← Singleton config DocType
│   │   ├── university_department/   ← Extended department
│   │   ├── notice_board/            ← Announcements
│   │   ├── emergency_alert/         ← Emergency broadcast
│   │   ├── user_notification/       ← Per-user notifications
│   │   ├── notification_template/   ← Jinja-based templates
│   │   ├── naac_metric/             ← NAAC data collection
│   │   ├── accreditation_cycle/     ← NAAC/NBA cycle management
│   │   └── proctoring_snapshot/     ← Online exam proctoring
│   ├── api/v1/              ← Versioned REST API (X-API-Key, external)
│   │   ├── student.py       ← External student data endpoints
│   │   ├── faculty.py       ← External faculty data endpoints
│   │   └── admin.py         ← External admin dashboard endpoints
│   ├── examination/         ← Exam business logic (Python classes)
│   ├── analytics/           ← KPI calculation, MIS reports
│   ├── accreditation/       ← NAAC data collection, SSR generation
│   ├── grievance/           ← Grievance workflow, SLA tracking
│   └── feedback/            ← Student/faculty feedback management
│
├── university_portals/      ← PORTAL API LAYER (serves portal-vue)
│   └── api/
│       ├── portal_api.py    ← Session info, student portal, parent portal
│       └── faculty_api.py   ← 27 faculty endpoints (all FacultyWork/Teaching)
│
├── university_academics/    ← Timetable, CBCS, course registration
├── university_admissions/   ← Admission cycle, merit list, seat matrix
├── university_student_info/ ← Extended student records, alumni
├── university_examinations/ ← Hall tickets, exam schedule, question bank
├── faculty_management/      ← Teaching assignments, workload, publications
├── university_hostel/       ← Room allocation, mess, maintenance
├── university_transport/    ← Routes, vehicles, student allocation
├── university_library/      ← Articles, transactions, fines, reservations
├── university_placement/    ← Companies, drives, job openings, applications
├── university_lms/          ← Courses, modules, assignments, quizzes
├── university_research/     ← Research projects, grants, publications
├── university_obe/          ← Course outcomes, POs, CO-PO mapping, attainment
├── university_integrations/ ← External system connectors
├── university_payments/     ← Razorpay/PayU, GL posting, reconciliation
├── university_analytics/    ← Custom dashboards, KPI definitions, MIS
├── university_grievance/    ← Student grievances, SLA tracking
├── university_feedback/     ← Student-faculty feedback surveys
└── university_inventory/    ← Lab equipment, assets, consumables
```

### 5.2 Override Architecture (Extending Base Apps)

The custom app overrides 6 core Frappe Education DocType classes:

```
hooks.py::override_doctype_class = {
    "Student"           → UniversityStudent (adds CGPA, enrollment no., category cert.)
    "Program"           → UniversityProgram (adds regulatory board, accreditation data)
    "Course"            → UniversityCourse  (adds credit hours, OBE linkage)
    "Assessment Result" → UniversityAssessmentResult (grade points, CBCS credits)
    "Fees"              → UniversityFees    (GL integration, payment gateway trigger)
    "Student Applicant" → UniversityApplicant (merit ranking, category validation)
}
```

**Document Event hooks** wire into ERPNext/HRMS lifecycle events:

```
Fees.on_submit       → GL entry creation + payment gateway order creation
Leave Application    → notify affected course schedule (replacement faculty)
Employee.on_update   → sync faculty profile if Instructor linked
Department.on_update → propagate OBE/department head changes
Student.validate     → enrollment number uniqueness, category certificate check
```

### 5.3 Module Dependency Graph

```
                         ┌─────────────────┐
                         │  Frappe Core v16 │
                         └────────┬────────┘
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
            ┌──────────┐  ┌──────────────┐  ┌────────┐
            │ ERPNext  │  │Frappe Eductn.│  │  HRMS  │
            │(Accounts)│  │(Students,    │  │(Payroll│
            │          │  │ Programs,    │  │ Leave, │
            └────┬─────┘  │ Courses,     │  │ Attend)│
                 │        │ Grades)      │  └───┬────┘
                 │        └──────┬───────┘      │
                 └───────────────┼──────────────┘
                                 │
                  ┌──────────────▼──────────────────────────┐
                  │       university_erp (custom app)         │
                  └──────────────┬──────────────────────────┘
                                 │
                                 ├── university_portals/api/   ← PORTAL API BRIDGE
                                 │   ├── portal_api.py         (session, student, parent)
                                 │   └── faculty_api.py        (27 faculty endpoints)
                                 │
          ┌──────────────────────┼──────────────────────────┐
          │                      │                           │
   ┌──────▼─────┐        ┌───────▼──────┐         ┌────────▼──────┐
   │ ACADEMICS  │        │  ADMISSIONS  │         │   FINANCE     │
   │ - CBCS     │        │ - Cycles     │         │ - Fees        │
   │ - Timetbl. │        │ - Merit List │         │ - Payments    │
   │ - OBE      │        │ - Seat Matrix│         │ - GL Posting  │
   └──────┬─────┘        └───────┬──────┘         └────────┬──────┘
          │                      │                          │
          │         ┌────────────▼─────────────┐           │
          └────────►│    STUDENT INFO (Core)    │◄──────────┘
                     │  - Student (extended)    │
                     │  - Program Enrollment    │
                     │  - Student Status Log    │
                     └────────────┬─────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
      ┌──────▼──────┐    ┌────────▼──────┐   ┌───────▼──────────┐
      │EXAMINATIONS │    │ FACULTY MGMT  │   │  portal-vue SPA  │
      │ - Schedule  │    │ - Assignments │   │  (all user roles) │
      │ - Hall Tick.│    │ - Workload    │   │  /portal/         │
      │ - Online    │    │ - Publications│   │                  │
      │ - Practical │    │ - Leave sync  │   │  Consumes:       │
      └──────┬──────┘    └────────┬──────┘   │  portal_api.py   │
             │                    │          │  faculty_api.py  │
      ┌──────▼──────────────────────────────▼────┐
      │               INTEGRATIONS LAYER           │
      │  SMS (MSG91) │ WhatsApp │ Razorpay │ PayU  │
      │  DigiLocker  │ Biometric│ Firebase │ Email │
      └──────────────┬───────────────────────────-─┘
                     │
      ┌──────────────▼──────────────────┐
      │          ANALYTICS / MIS        │
      │  KPI Definitions │ Dashboards   │
      │  Scheduled Reports │ NAAC Data  │
      └─────────────────────────────────┘
```

### 5.4 Scheduled Tasks Architecture

| Frequency    | Task                                              | Module              |
|--------------|---------------------------------------------------|---------------------|
| Every 5 min  | Auto-submit expired online exams                 | University Exams    |
| Daily 8 AM   | Assignment deadline reminders                    | University LMS      |
| Daily        | Fee due reminders + overdue notices              | University Finance  |
| Daily        | Library overdue notices + reservation expiry     | University Library  |
| Daily        | CGPA recalculation (batch)                       | University Academics|
| Daily        | Attendance threshold violations check            | University Academics|
| Daily        | Auto bank reconciliation (Razorpay/PayU)         | University Payments |
| Daily        | WhatsApp daily counter reset                     | University Integr.  |
| Daily        | Low stock / maintenance due / calibration due    | University Inventory|
| Daily        | NAAC attainment update                           | Accreditation       |
| Daily        | Grievance SLA check + escalation reminders       | University Grievance|
| Weekly       | Attendance warning to parents (WhatsApp/SMS)     | University Academics|
| Weekly       | Placement drive updates to eligible students     | University Placement|
| Weekly       | Communication analytics report                   | University Analytics|
| Monthly      | Monthly MIS report generation                    | University Analytics|
| Monthly      | Asset depreciation posting                        | University Inventory|
| Monthly      | KPI quarterly aggregation                        | University Analytics|

---

## 6. API Layer: Portal-First Design

### 6.1 API Architecture Overview

The API layer has two distinct tiers that map to the two user tiers:

```
                    TIER 1: PORTAL API (session-based, for portal-vue)
                    ─────────────────────────────────────────────────
portal-vue SPA
(browser, same origin)
        │
        │  Session cookie (Frappe auth)
        │  X-Frappe-CSRF-Token (from window.frappe.csrf_token)
        │
        ▼
 /api/method/university_erp.university_portals.api.portal_api.*
 /api/method/university_erp.university_portals.api.faculty_api.*
        │
        ▼
 @frappe.whitelist endpoints
 (role check via frappe.get_roles, company scope via Employee/Student record)


                    TIER 2: VERSIONED REST API (key-based, for external)
                    ──────────────────────────────────────────────────────
External clients
(mobile app, 3rd party integrations, ERP bridges)
        │
        │  X-API-Key header
        │
        ▼
 /api/method/university_erp.university_erp.api.v1.student.*
 /api/method/university_erp.university_erp.api.v1.faculty.*
 /api/method/university_erp.university_erp.api.v1.admin.*
        │
        ▼
 @api_handler decorator
 (API key validation, role check, standardized JSON envelope)


                    TIER 0: FRAPPE STANDARD API (admin/system use only)
                    ──────────────────────────────────────────────────────
Frappe Desk (System Manager users only)
        │
        │  Session cookie
        │
        ▼
 /api/resource/*   (standard Frappe CRUD — all DocTypes)
```

### 6.2 Portal API Design (`university_portals/api/`)

Portal API endpoints are designed around user roles and tasks, not around DocTypes. A single endpoint returns everything a portal view needs in one call, avoiding the N+1 request problem of generic REST.

**portal_api.py** — 28 endpoints total:

*Session:*
| Endpoint | Method | Description |
|---|---|---|
| `get_session_info` | GET | Logged user, full name, avatar, roles[], allowed_modules[] — called once at SPA boot |

*Student portal (13 GET + 5 mutations):*
| Endpoint | Method | Description |
|---|---|---|
| `get_student_dashboard` | GET | KPIs, today's classes, announcements — single boot call for student home |
| `get_student_timetable` | GET | Weekly timetable (week_start param) |
| `get_student_results` | GET | Assessment results + CGPA |
| `get_student_attendance` | GET | Attendance per course + aggregate |
| `get_student_fees` | GET | Fee schedule, outstanding, payment history |
| `get_student_profile` | GET | Extended student profile fields |
| `get_student_notices` | GET | Notice board filtered to student's institute/program |
| `get_hall_ticket` | GET | Hall ticket data for exam downloads |
| `get_student_library` | GET | Issued books, fines, membership status |
| `get_student_hostel` | GET | Room allocation, mess menu |
| `get_student_transport` | GET | Allocated route and stop |
| `get_student_placement` | GET | Upcoming drives, applications |
| `get_student_lms_courses` | GET | Enrolled LMS courses and progress |
| `submit_course_registration` | POST | Course registration for CBCS electives |
| `pay_fee_initiate` | POST | Create payment gateway order (Razorpay/PayU) |
| `submit_grievance` | POST | File a grievance |
| `update_student_profile` | POST | Update contact info, emergency contact |
| `update_notification_preferences` | POST | Configure push/email/SMS preferences |

*Parent portal (3 endpoints):*
| Endpoint | Method | Description |
|---|---|---|
| `get_parent_dashboard` | GET | Ward's KPIs (attendance, fees, grades summary) |
| `get_parent_ward_detail` | GET | Full ward profile and data |
| `submit_parent_feedback` | POST | Submit feedback on portal experience |

**faculty_api.py** — 27 endpoints across 8 functional categories (documented in section 3.6).

### 6.3 Portal API Request/Response Pattern

```
portal-vue component
        │
useFacultyApi.getDashboard()
        │
useFrappe.call('university_erp.university_portals.api.faculty_api.get_faculty_dashboard', {}, {method: 'GET'})
        │
        ▼
GET /api/method/university_erp.university_portals.api.faculty_api.get_faculty_dashboard
Headers:
  X-Frappe-CSRF-Token: <from window.frappe.csrf_token>
  Accept: application/json
Credentials: same-origin (session cookie forwarded)
        │
        ▼ Frappe backend
faculty_api.get_faculty_dashboard()
├── get_current_faculty()  → maps session user → Employee record
├── Query Teaching Assignments (company-scoped via employee.department)
├── Query today's Course Schedule slots
├── Aggregate leave balance from HRMS
└── Return structured dict
        │
        ▼
{ "message": { "faculty": {...}, "kpis": {...}, "today_classes": [...], "recent_notices": [...] } }
        │
        ▼
useFrappe.handleResponse() extracts data.message
        │
        ▼
Component reactive data updated → Vue re-renders
```

**Error handling in the response chain:**

```
HTTP 401 → useFrappe redirects to /login?redirect-to=/portal/
HTTP 403 → useFrappe throws 'Permission denied' → component shows error state
HTTP 500 → useFrappe extracts data._server_messages or data.exc → error toast
data.exc → thrown as Error (Frappe exception serialized as string)
```

### 6.4 Versioned REST API (External Integrations)

All endpoints in `api/v1/` follow the `@api_handler` decorator pattern:

```
Request → HTTP method check → API key validation (X-API-Key header)
        → role-based authorization (allowed_roles list)
        → business logic execution
        → standardized JSON response envelope
        → error handling with HTTP status codes
```

**Response envelope:**

```json
{
  "success": true,
  "data": { "..." },
  "api_version": "1.0.0"
}

{
  "success": false,
  "error": {
    "code": "NOT_FOUND | FORBIDDEN | VALIDATION_ERROR | INTERNAL_ERROR",
    "message": "Human-readable description"
  },
  "api_version": "1.0.0"
}
```

**External API endpoint catalogue:**

*Student endpoints (`/api/method/university_erp.university_erp.api.v1.student.*`):*

| Endpoint           | Method | Roles                  | Description                         |
|--------------------|--------|------------------------|-------------------------------------|
| `get_profile`      | GET    | Student, Sys Mgr       | Student profile data                |
| `get_enrollments`  | GET    | Student, Sys Mgr       | Program enrollments (current/past)  |
| `get_attendance`   | GET    | Student, Sys Mgr       | Attendance records + summary        |
| `get_fees`         | GET    | Student, Accounts User | Fee schedule + outstanding          |
| `get_results`      | GET    | Student, Sys Mgr       | Assessment results + CGPA           |
| `get_timetable`    | GET    | Student, Sys Mgr       | Today's / weekly timetable          |
| `get_library_status` | GET  | Student, Sys Mgr       | Issued books, fines, membership     |
| `get_hostel_details` | GET  | Student, Sys Mgr       | Room allocation details             |

*Faculty endpoints (`/api/method/university_erp.university_erp.api.v1.faculty.*`):*

| Endpoint               | Method | Roles                | Description                      |
|------------------------|--------|----------------------|----------------------------------|
| `get_profile`          | GET    | Instructor, Sys Mgr  | Faculty profile + employee link  |
| `get_teaching_schedule`| GET    | Instructor, Sys Mgr  | Daily or weekly class schedule   |
| `get_assigned_courses` | GET    | Instructor, Sys Mgr  | All courses with student groups  |
| `get_leave_balance`    | GET    | Instructor, HR Mgr   | Leave balances from HRMS         |
| `mark_attendance`      | POST   | Instructor, Sys Mgr  | Bulk student attendance posting  |
| `get_student_list`     | GET    | Instructor, Sys Mgr  | Students in assigned groups      |

*Admin endpoints (`/api/method/university_erp.university_erp.api.v1.admin.*`):*

| Endpoint              | Method | Roles                   | Description                     |
|-----------------------|--------|-------------------------|---------------------------------|
| `get_dashboard_stats` | GET    | Sys Mgr, Edu Mgr        | Combined stats (students+finance)|
| `get_student_stats`   | GET    | Sys Mgr, Edu Mgr        | Student count by program/batch  |
| `get_faculty_stats`   | GET    | Sys Mgr, HR Mgr         | Faculty count by department     |
| `get_finance_stats`   | GET    | Sys Mgr, Accounts Mgr   | Collection + outstanding totals |
| `get_admission_stats` | GET    | Sys Mgr, Edu Mgr        | Applicant pipeline by status    |
| `get_system_health`   | GET    | Sys Mgr                 | Queue status, error counts      |
| `send_bulk_notification`| POST | Sys Mgr                 | Template-based mass notification|

### 6.5 Webhook Architecture

Inbound webhooks for payment gateways:

```
POST /api/method/university_erp.university_payments.webhooks.razorpay_webhook.handle_razorpay_webhook
POST /api/method/university_erp.university_payments.webhooks.payu_callback.payu_success
POST /api/method/university_erp.university_payments.webhooks.payu_callback.payu_failure
```

**Webhook processing pipeline:**

```
Razorpay/PayU webhook POST
        │
        ▼
HMAC-SHA256 signature verification
        │
        ▼
Create/Update Payment Transaction DocType
        │
        ▼
Update Fees document (outstanding_amount)
        │
        ▼
Create GL entries (on_fees_submit hook)
        │
        ▼
Log to Payment Webhook Log DocType
        │
        ▼
Trigger notification (receipt SMS/WhatsApp + portal real-time update)
```

### 6.6 External Integration Middleware

```
SMSGateway (university_integrations/sms_gateway.py)
├── Provider: MSG91
├── Features: template rendering, queue-based sending, delivery tracking
└── Hook: daily queue flush + delivery status poll

WhatsAppGateway (university_integrations/whatsapp_gateway.py)
├── Provider: WhatsApp Business API (Meta)
├── Features: template messages (approved), daily counter reset
└── Webhook: incoming message handling

PaymentGateway (university_payments/payment_gateway.py)
├── Providers: Razorpay SDK, PayU
├── Unified interface: create_order(), verify_payment(), refund()
└── GL Integration: automatic journal entry on payment confirmation

DigiLockerIntegration (university_integrations/digilocker_integration.py)
├── Purpose: verify academic certificates, ID documents
└── API: DigiLocker Sandbox/Production OAuth2 flow

BiometricIntegration (university_integrations/biometric_integration.py)
├── Purpose: employee attendance from biometric devices
└── Sync: scheduled pull from device API → HRMS Attendance

CertificateGenerator (university_integrations/certificate_generator.py)
├── Purpose: digital certificates (bonafide, TC, degree marksheet)
└── Output: PDF generation via Frappe's Jinja + WeasyPrint
```

---

## 7. Data Flow Between Modules

### 7.1 Student Lifecycle: End-to-End Flow

```
ADMISSIONS → STUDENT CREATION → ENROLLMENT → ACADEMICS → EXAMS → RESULTS → PLACEMENT
     │                │               │            │          │        │
     └── FINANCE ─────┘               └── HOSTEL   └── LMS    │        │
                      │                   TRANSPORT            │        │
                      └── LIBRARY ─────────────────────────────┘        │
                                                                         └── ALUMNI
```

All data generated in this lifecycle is surfaced to the student through the portal-vue `/student` route (Phase 03.2). At each stage, the relevant `portal_api.py` endpoint provides a precomposed view of that data — not raw DocType records.

#### Stage 1: Admission

```
Student Applicant (Education DocType — extended by UniversityApplicant)
        │ (filled via admissions web form or Admissions Officer in portal)
        ▼
Admission Cycle (university_admissions)
├── Seat Matrix — category-wise seats per program per company
├── Admission Criteria — merit calculation rules
└── Merit List — ranked applicants (auto-generated by Python)
        │
        │ Applicant Status → "Admitted"
        ▼
Student Creation (university_admissions/student_creation.py)
├── Creates Student DocType from Student Applicant
├── Assigns: custom_enrollment_number, custom_category
├── Creates User account (portal login credentials)
├── Triggers: SMS notification (admission confirmation)
└── Sends: WhatsApp welcome message with portal URL
```

#### Stage 2: Student Registration

```
Student (Education DocType — extended by UniversityStudent)
├── Fields added via Custom Fields (83 in custom_field.json):
│   ├── custom_enrollment_number (unique, format: YYYY/DPT/NNN)
│   ├── custom_cgpa (auto-calculated on Assessment Result submit)
│   ├── custom_student_status (Active/On Leave/Graduated/Expelled)
│   ├── custom_category (General/OBC/SC/ST/EWS)
│   └── custom_category_certificate (file attachment)
│
└── Linked records created:
    ├── Library Member (university_library)
    ├── User account → role: University Student
    └── Parent portal link (via guardian email) → role: University Parent
```

#### Stage 3: Program Enrollment

```
Program Enrollment (Education DocType)
├── Links: Student → Program → Academic Year → Academic Term
├── Batch assignment (Student Batch)
├── Course Enrollment (per course in the program curriculum)
│   └── CBCS: Course Registration (elective selection via portal)
└── Fee Schedule trigger:
        │
        ▼
Fees DocType (Education — extended by UniversityFees)
├── grand_total = sum of fee components
├── on_submit →
│   ├── GL entry (Debit: Student Receivable, Credit: Fee Income)
│   ├── Payment gateway order creation (if online payment enabled)
│   └── SMS/WhatsApp notification to student + guardian
└── Portal surface: portal_api.get_student_fees()
```

#### Stage 4: Academic Activity

```
Course Schedule → portal_api.get_student_timetable()  → portal /student timetable view
        │
        │ (Faculty marks attendance in portal /faculty/teaching?tab=attendance)
        │ faculty_api.submit_attendance()
        ▼
Student Attendance (Education DocType)
├── Aggregated daily per student per course
├── Scheduled task: check_attendance_thresholds (daily)
│   └── If below 75% → notify student + parent (WhatsApp)
└── Portal surface: portal_api.get_student_attendance()

LMS Activity:
Course Schedule → LMS Course Module → LMS Content → LMS Assignment
        │
        │ Faculty manages via portal /faculty/work?tab=lms
        │ faculty_api.saveLmsContent()
        ▼
Assignment Submission → LMS Quiz → Quiz Attempt
        └── Grade feeds into Assessment Plan
```

#### Stage 5: Examinations

```
Exam Schedule (university_examinations)
        │
        ▼
Hall Ticket (university_examinations)
├── Generated per student per exam schedule
├── Validation: fee clearance check (outstanding_amount == 0)
├── Validation: min attendance check (≥ 75%)
├── Contains: exam centre, seat number, timetable
└── Download via portal: portal_api.get_hall_ticket()

Online Examination (university_erp/doctype/online_examination)
├── OnlineExamController manages:
│   ├── validate_access (eligibility check)
│   ├── start_exam (timer start, attempt record)
│   ├── save_answer (auto-save every 30 sec)
│   ├── submit_exam (final submission)
│   └── proctoring (Proctoring Snapshot DocType)
└── Auto-submit cron: every 5 min (expired exams)
```

#### Stage 6: Results and OBE

```
Assessment Plan (Education) → Assessment Result (extended by UniversityAssessmentResult)
├── Fields added:
│   ├── custom_grade_points (O=10, A+=9, A=8.5, B+=8...)
│   ├── custom_credits (from Course.credit_hours)
│   └── custom_cbcs_grade
│
├── Faculty enters grades via portal /faculty/teaching?tab=grades
│   faculty_api.saveDraftGrade() → faculty_api.submitGrades()
│
├── on_submit trigger:
│   ├── update_student_cgpa() — recalculates Student.custom_cgpa
│   └── OBE: CO Attainment calculation
│           │
│           ▼
│       CO Attainment (university_obe)
│       ├── Direct attainment (from assessment results)
│       ├── Indirect attainment (from OBE Survey)
│       └── CO-PO mapping → PO Attainment
│
└── Portal surface: portal_api.get_student_results()
```

#### Stage 7: Finance Intersection

```
Finance runs in parallel across the lifecycle:

Admission     → Application Fee (Fees DocType, company = admitting institute)
Enrollment    → Tuition + other fee categories (Fees DocType)
Hostel        → Hostel fees (Fees with hostel component)
Transport     → Transport fees (Fees with transport component)
Library Fine  → Library Fine → payment via portal
Exam          → Exam fee (optional, pre-exam hall ticket check)

All payments flow through:
portal_api.pay_fee_initiate()
        │
        ▼
PaymentGateway.create_order() (Razorpay/PayU)
        │  (user completes payment in gateway UI)
        ▼
Webhook → Payment Transaction DocType
        │
        ▼
Fees.outstanding_amount update
        │
        ▼
GL Entry (Journal Entry in ERPNext Accounts)
├── Debit: Student Receivable (company-specific)
└── Credit: Fee Income Account (institute's chart of accounts)
```

#### Stage 8: Placement to Alumni

```
Student Resume (university_placement)
└── eligibility: CGPA threshold + active enrollment

Placement Drive (university_placement)
├── Placement Company → Placement Job Opening
├── Placement Round (screening stages)
└── Placement Application (student applies via portal)
        │
        │ Application status: "Placed"
        ▼
Student Status → "Graduated" / "Alumni"
University Alumni (university_student_info)
└── alumni portal access granted (role: University Alumni)
```

### 7.2 HR / Faculty Data Flow

```
Employee (HRMS)
        │ (linked via custom_is_faculty=1 flag)
        ▼
get_current_faculty() in faculty_api.py
├── maps frappe.session.user → Employee record
└── Employee.department → company scope for all subsequent queries

Employee (HRMS) ←→ Instructor (Education)
        │ (linked via Teaching Assignment)
        ▼
Teaching Assignment (faculty_management)
├── Course + Student Group + Academic Term
├── Workload calculation (Teaching Assignment Schedule)
└── Approval workflow (Teaching Assignment Approval Workflow)
        │
        ▼
faculty_api.getDashboard() / getTodayClasses() / getWeeklyTimetable()
        │
        ▼
portal-vue FacultyDashboard / FacultyTeaching / TimetableGrid

Leave Application (HRMS)
        │ on_submit hook (faculty_management/leave_events.py)
        ▼
Leave Affected Course (faculty_management)
├── Identifies courses impacted by leave dates
├── Triggers: find replacement via Temporary Teaching Assignment
└── Notifies: affected student groups + HOD
        │
        ▼
faculty_api.getLeaveBalance() / applyLeave()
        │
        ▼
portal-vue LeaveBalanceCards / LeaveApplyForm
```

---

## 8. Company-Based Multi-Tenant Architecture

### 8.1 The 19-Company Model

MOZE Trust operates a **single Frappe site** with **19 Company entities** — one per institute. This is distinct from multi-site deployment (which would require separate MariaDB databases).

```
frappe site: moze.edu.in (single MariaDB database)
│
├── Company: MOZE Educational Trust (parent — trust-level)
│
├── Company: MOZE College of Engineering, Pune
├── Company: MOZE College of Pharmacy, Pune
├── Company: MOZE College of Arts Commerce Science
├── Company: MOZE B.Ed College
├── Company: MOZE D.Ed Institute
├── Company: MOZE Junior College (Pune)
├── Company: MOZE Junior College (Baramati)
│   ... (12 more institutes)
└── Company: MOZE School of Excellence
```

Each company has its own:
- **Chart of Accounts** (Accounts module)
- **Cost Centers** (for inter-department P&L)
- **Bank Accounts** (Razorpay/PayU settlement accounts)
- **Fiscal Year** (April–March, common across all, but ledgers are separated)
- **HR Policies** (leave allocation rules may differ by institute type)

### 8.2 Company Scope in portal-vue

Portal-vue does not implement company selection UI. Company scope is derived from the backend:

1. **Faculty:** `get_current_faculty()` resolves `frappe.session.user → Employee → department`. The department's company determines which data the faculty member sees. All `faculty_api.*` queries are scoped to this employee's company automatically.

2. **Student:** `portal_api.get_student_dashboard()` resolves `frappe.session.user → Student → program_enrollment → company`. All student queries are scoped to this company.

3. **Management/Admin users:** For users with cross-company permissions, `User Permission` records with `Apply to All` allow the portal API to return aggregated data. The portal-vue management dashboard (Phase 4) will support an institute selector for drilling down.

```
Faculty: Dr. Patil at GSMCOE Balewadi
→ same portal-vue URL: https://erp.moze.edu.in/portal/faculty
→ faculty_api.getDashboard() resolves Employee → GSMCOE Balewadi company
→ returns: Teaching Assignments, Course Schedules filtered to GSMCOE Balewadi

Faculty: Dr. Kulkarni at PG MOZE Wagholi
→ same portal-vue URL: https://erp.moze.edu.in/portal/faculty
→ faculty_api.getDashboard() resolves Employee → PG MOZE Wagholi company
→ returns: Teaching Assignments, Course Schedules filtered to PG MOZE Wagholi

IDENTICAL Vue.js code. Different data. Company isolation is backend-enforced.
```

### 8.3 Data Isolation Model

```
EVERY core university DocType carries a `company` field:

Fees
├── company = "MOZE College of Engineering, Pune"
└── student = "STU-2024-ENG-00123"

Program Enrollment
├── company = "MOZE College of Pharmacy, Pune"
└── program = "B.Pharm"

Hostel Allocation
├── company = "MOZE College of Engineering, Pune"
├── hostel_building = "Boys Hostel Block A"
└── student = "STU-2024-ENG-00123"

Placement Drive
├── company = "MOZE College of Engineering, Pune"
└── eligible_programs = [B.E. Comp, B.E. IT, B.E. Mech]
```

### 8.4 User Permission Enforcement

```
User: registrar@mozeeng.edu.in
├── Role: University Registrar
├── User Permission: Company = MOZE College of Engineering, Pune (Allow)
└── Effect: Portal management views auto-filtered to this company

User: trust_cfo@moze.edu.in
├── Role: University Finance
├── User Permissions: Company = ALL 19 (via "Apply to All" flag)
└── Effect: Finance dashboard shows consolidated data across all institutes

User: student@mozeeng.edu.in
├── Role: University Student
├── User Permission: Company = MOZE College of Engineering, Pune
└── Additional: has_permission() → own Student record only
```

### 8.5 Trust-Level Cross-Company Reporting

Trust management (Phase 4 management dashboard in portal-vue) needs cross-institute analytics:

```
KPI Definition (university_analytics)
├── kpi_code: "TOTAL_STUDENTS_TRUST"
├── calculation_method: "SQL"
└── query: "SELECT COUNT(*) FROM `tabStudent` WHERE enabled=1"
    (No company filter — trust-level aggregation, requires Trust Admin role)

Scheduled Report (university_analytics)
├── schedule: Monthly
├── recipients: trust management emails
├── company_filter: NULL (all companies)
└── output: PDF emailed automatically

Custom Dashboard (university_analytics)
├── dashboard_name: "Trust MIS Dashboard"
├── allowed_roles: ["University Trust Admin", "System Manager"]
└── widgets:
    ├── Students by institute (bar chart, GROUP BY company)
    ├── Fee collection by institute (stacked bar)
    └── Faculty strength (count by company + department)
```

### 8.6 Inter-Company Resource Sharing

| Scenario                          | Mechanism                              |
|-----------------------------------|----------------------------------------|
| Shared faculty (2 institutes)     | Teaching Assignment with company field for each assignment |
| Shared library (central library)  | Library Article with company = Trust; access from all |
| Trust-level procurement           | Purchase Order on Trust Company; assets transferred |
| Transport routes serving multiple | Transport Route linked to Trust Company |
| Consolidated payroll              | HRMS salary processed per company, consolidated report at trust |

---

## 9. Improvements Over Default ERPNext

### 9.1 What Default ERPNext/Education Cannot Do

| Limitation (default)                         | university_erp Solution                                           |
|----------------------------------------------|-------------------------------------------------------------------|
| No unified non-admin portal                  | portal-vue: Vue 3.5 SPA at /portal/ for ALL non-admin roles      |
| All staff use generic Frappe Desk            | Two-tier: Desk for admins only, purpose-built portal for everyone else |
| No admission cycle / merit list              | Admission Cycle, Merit List, Seat Matrix DocTypes                 |
| No CBCS credit system                        | Course.credit_hours + Assessment Result grade points (O/A+/A/B+) |
| No enrollment number management              | custom_enrollment_number with format + uniqueness validation      |
| No CGPA auto-calculation                     | UniversityStudent.calculate_cgpa() + scheduled recalculation      |
| No hall ticket generation                    | Hall Ticket DocType with fee + attendance pre-validation          |
| No online examination                        | Online Examination + OnlineExamController + proctoring snapshots  |
| No practical examination                     | Practical Examination + Practical Exam Slot + External Examiner   |
| No question bank                             | Question Bank + auto question paper generation                    |
| No hostel management                         | 12 hostel DocTypes (building → room → allocation → attendance)    |
| No transport management                      | Transport Route, Vehicle, Allocation, Trip Log                    |
| No library fine + reservation system         | Library Fine, Book Reservation (beyond basic ERPNext Library)     |
| No placement management                      | Placement Company, Drive, Job Opening, Application, Resume        |
| No OBE / CO-PO mapping                       | 25+ OBE DocTypes covering CO, PO, PEO, attainment calculation     |
| No NAAC/NBA compliance tracking              | NAAC Metric, Accreditation Cycle, SSR Generator, 7-criterion data |
| No payment gateway integration               | Unified PaymentGateway class (Razorpay + PayU), webhook handlers  |
| No SMS / WhatsApp notification layer         | SMSGateway (MSG91), WhatsAppGateway, template management          |
| No DigiLocker integration                    | DigiLocker OAuth2 flow, document issuance + verification          |
| No biometric attendance sync                 | BiometricDevice DocType, scheduled sync to HRMS Attendance        |
| No digital certificate generation            | CertificateTemplate + PDF generation (bonafide, TC, marksheet)    |
| No teaching workload management              | Teaching Assignment + Workload Distributor + leave impact tracking |
| No faculty grade entry portal                | portal-vue FacultyGradeGrid (TanStack Table, draft/submit)        |
| No emergency alert system                    | Emergency Alert DocType, broadcast to all active users            |
| No multi-level notification center           | User Notification + Notification Template + preference management  |
| No research management                       | Research Project, Grant, Publication tracking                     |
| No LMS (beyond basic)                        | LMS Course, Module, Assignment, Quiz, Discussion, Rubric          |
| No grievance management                      | Grievance DocType + SLA tracking + escalation + resolution flow   |
| No student feedback on faculty               | Student Feedback DocType, anonymous option, analytics             |
| No inventory / lab equipment management      | Lab Equipment, Booking, Asset, Maintenance tracking               |
| No multi-company student data                | Company field on all DocTypes + user permission enforcement       |
| No trust-level MIS                           | Custom Dashboard + KPI Definition + Scheduled Report system       |
| ERPNext modules irrelevant to university     | `block_modules` in hooks.py removes Manufacturing, Stock, CRM etc.|
| No bilingual (Marathi) UI                    | Translation framework hooks in university_erp/translations/       |
| No accessibility-tested portal               | portal-vue: vitest-axe WCAG 2.1 AA tests on all shared components |

### 9.2 Custom Fields Added to Base DocTypes

`custom_field.json` (83 custom fields) extends base Education DocTypes:

**Student extensions:**

| Field Name                  | Type        | Purpose                                |
|-----------------------------|-------------|----------------------------------------|
| custom_enrollment_number    | Data        | Unique institute enrollment number     |
| custom_cgpa                 | Float       | Auto-calculated CGPA (10-point scale)  |
| custom_student_status       | Select      | Active/Graduated/Alumni/On Leave etc.  |
| custom_category             | Select      | General/SC/ST/OBC/EWS                  |
| custom_category_certificate | Attach      | Category certificate upload            |
| custom_aadhaar_number       | Data        | DPDP-compliant (masked storage)        |
| custom_abc_id               | Data        | Academic Bank of Credits ID (NEP 2020) |
| custom_digilocker_id        | Data        | DigiLocker account linkage             |
| custom_parent_mobile        | Data        | For WhatsApp parent notifications      |
| custom_blood_group          | Select      | Emergency medical info                 |

**Course extensions:**

| Field Name              | Type    | Purpose                               |
|-------------------------|---------|---------------------------------------|
| custom_credit_hours     | Float   | CBCS credits (L+T+P format)           |
| custom_course_type      | Select  | Core/Elective/Open Elective/Audit      |
| custom_lab_required     | Check   | Triggers lab booking requirement       |
| custom_practical_marks  | Int     | Max practical marks for hall ticket    |
| custom_theory_marks     | Int     | Max theory marks                       |

**Program extensions:**

| Field Name              | Type    | Purpose                               |
|-------------------------|---------|---------------------------------------|
| custom_regulatory_board | Select  | AICTE/SPPU/NCTE/PCI/State Board       |
| custom_duration_years   | Int     | Program duration                      |
| custom_accreditation    | Select  | NAAC/NBA/None                         |
| custom_intake_capacity  | Int     | Sanctioned intake for seat matrix     |

### 9.3 Workflow Additions

Three custom Frappe Workflows:

| Workflow                           | States                                          | Approver             |
|------------------------------------|--------------------------------------------------|----------------------|
| Leave Application Workflow         | Draft→Pending HOD→Pending Principal→Approved     | HOD → Principal      |
| Teaching Assignment Workflow       | Draft→Pending HOD→Active                        | HOD                  |
| Fee Refund Approval Workflow       | Draft→Pending Accounts→Approved/Rejected         | Accounts Manager     |

### 9.4 Grading Scale

10-point CBCS-compliant grading scale installed on first install:

| Grade | Threshold | Points | Meaning      |
|-------|-----------|--------|--------------|
| O     | 90%       | 10.0   | Outstanding  |
| A+    | 80%       | 9.0    | Excellent    |
| A     | 70%       | 8.5    | Very Good    |
| B+    | 60%       | 8.0    | Good         |
| B     | 55%       | 7.5    | Above Average|
| C     | 50%       | 6.5    | Average      |
| P     | 45%       | 4.0    | Pass         |
| F     | 0%        | 0.0    | Fail         |

CGPA = Σ(Grade Points × Credits) / Σ(Credits) — weighted, recalculated on each Assessment Result submission.

---

## 10. Infrastructure and Deployment

### 10.1 Deployment Architecture

```
                          INTERNET
                              │
                    ┌─────────▼──────────┐
                    │   Cloudflare WAF    │
                    │  DDoS + Rate Limit  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Nginx (SSL/TLS)   │
                    │  Reverse proxy      │
                    │  /portal/ → SPA     │
                    │  /api/ → Gunicorn   │
                    │  Static assets      │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   ┌──────▼──────┐   ┌────────▼──────┐   ┌───────▼───────┐
   │  Gunicorn   │   │ Frappe Worker │   │  Redis Stack  │
   │  (web app)  │   │ (RQ jobs)     │   │  Cache/Queue  │
   │  8 workers  │   │ 4 workers     │   │  SocketIO pub │
   └──────┬──────┘   └────────┬──────┘   └───────────────┘
          │                   │
          └─────────┬─────────┘
                    │
          ┌─────────▼──────────┐
          │    MariaDB 10.6+    │
          │  (single database   │
          │   all 19 companies) │
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  S3 / MinIO         │
          │  (file attachments, │
          │   student photos,   │
          │   certificates)     │
          └────────────────────┘
```

### 10.2 Static Asset Serving

The portal-vue SPA builds to `university_erp/public/portal/`. Frappe's asset pipeline publishes this to `/assets/university_erp/portal/`. Nginx serves these files with long-lived cache headers (content-hashed filenames from Vite).

```
Build: cd /workspace/development/portal-vue && npm run build
Output: frappe-bench/apps/university_erp/university_erp/public/portal/
Served at: /assets/university_erp/portal/assets/<hashed-filename>.js
```

The Vite manifest at `public/portal/.vite/manifest.json` is read by `www/portal/index.py` at request time to inject the correct hashed filenames into the HTML template.

### 10.3 Frappe Bench Process Layout

```
frappe-bench/
├── Procfile (Supervisor-managed processes):
│   ├── web:        gunicorn -w 8 -b 0.0.0.0:8000 frappe.app:application
│   ├── worker:     frappe worker --queue default,long,short
│   ├── scheduler:  frappe schedule
│   └── socketio:   node apps/frappe/socketio.js
│
├── apps/
│   ├── frappe/        (framework)
│   ├── erpnext/       (ERP base)
│   ├── hrms/          (HR & payroll)
│   ├── education/     (academic base)
│   └── university_erp/ (custom app — primary development)
│
├── sites/
│   └── moze.edu.in/
│       ├── site_config.json  (DB, Redis, S3 config)
│       └── private/files/   (secure file storage)
│
└── nginx.conf.d/  (Nginx site config)
```

### 10.4 Required App Stack

```python
# university_erp/hooks.py
required_apps = ["frappe", "erpnext", "hrms", "education"]
```

Installation order: frappe → erpnext → hrms → education → university_erp

### 10.5 Environment Separation

| Environment | Purpose                     | Data                  |
|-------------|-----------------------------|-----------------------|
| Production  | Live operations             | Real student data     |
| Staging     | UAT with real data subsets  | Anonymized prod copy  |
| Development | Feature development         | Seed demo data        |
| Training    | Staff onboarding            | Demo data (permanent) |

Demo data is seeded via `university_erp/setup/seed_demo_data.py` which creates sample programs, students, faculty, and academic years for training environments.

---

## 11. Regulatory Compliance Architecture

### 11.1 Compliance Matrix

| Regulatory Body | Institutes Affected          | university_erp Support                         |
|-----------------|------------------------------|------------------------------------------------|
| AICTE           | Engineering, Pharmacy        | Intake capacity in Program, faculty:student ratio reports |
| SPPU            | All affiliated institutes    | Examination schedule, result formats, attendance reports |
| NCTE            | B.Ed, M.Ed, D.Ed             | OBE framework, Teaching Practice records       |
| PCI             | Pharmacy                     | Lab equipment tracking, practical exam records |
| State Board     | Junior Colleges, Schools     | UDISE+ data export, HSC result formats         |
| NAAC            | All (accreditation cycles)   | 7-criterion data collection, SSR generation    |
| NBA             | Engineering programs         | CO/PO mapping, attainment calculation, OBE     |
| DPDP 2023       | All (student data privacy)   | user_data_fields in hooks.py, masked Aadhaar   |
| UDISE+          | Schools                      | Student enrollment data export                 |

### 11.2 NAAC Compliance Architecture

```
Accreditation Cycle DocType
├── data_period_start: 2019-04-01
├── data_period_end:   2024-03-31
└── NAACDataCollector.collect_all_metrics()
    │
    ├── Criterion 1: Curricular Aspects
    │   └── Programs, courses, NEP compliance, syllabus revision frequency
    │
    ├── Criterion 2: Teaching-Learning & Evaluation
    │   └── Student:faculty ratio, pass %, attendance, results
    │
    ├── Criterion 3: Research, Innovations & Extension
    │   └── Research Publications, Grants, Research Projects (university_research)
    │       (faculty enters via portal /faculty/work?tab=research)
    │
    ├── Criterion 4: Infrastructure & Learning Resources
    │   └── Lab Equipment, Library Articles, University Laboratory DocType
    │
    ├── Criterion 5: Student Support & Progression
    │   └── Placement statistics, scholarships, Grievance resolution rate
    │
    ├── Criterion 6: Governance, Leadership & Management
    │   └── Employee data, HR policies, department structure
    │
    └── Criterion 7: Institutional Values & Best Practices
        └── Custom NAAC Metric DocType entries

SSR Generator → automated PDF/Word document assembly
NAAC Metric, NAAC Metric Document, NAAC Metric Year Data
```

### 11.3 DPDP (Digital Personal Data Protection) Compliance

```python
# hooks.py - user_data_fields defines what is PII
user_data_fields = [
    {
        "doctype": "Student",
        "filter_by": "student",
        "redact_fields": ["first_name", "last_name", "email", "mobile"],
    },
]
```

Additional measures:
- Aadhaar numbers stored as `custom_aadhaar_number` with application-level masking (display as XXXX-XXXX-1234)
- Parent mobile numbers used only for notification triggers, not displayed in list views
- Right to be forgotten: student data redaction via `user_data_fields` on account deletion
- Data retention policy: configurable in University Settings
- SSL/TLS in transit, MariaDB encryption at rest
- portal-vue never exposes raw PII fields — portal_api endpoints return only what each role should see

---

## 12. Security Architecture

### 12.1 Authentication Layers

```
Layer 1: Frappe session authentication
├── Username + password → session cookie (used by portal-vue)
├── www/portal/index.py rejects Guest → redirect to /login
├── router.beforeEach checks sessionStore.isAuthenticated (CSRF-safe)
└── 2FA: configurable via Frappe's built-in TOTP

Layer 2: API key authentication (external integrations only)
├── X-API-Key header (NOT used by portal-vue)
├── Validated against API Key DocType (enabled flag)
└── Maps to a Frappe user → inherits that user's roles

Layer 3: CSRF protection (portal-vue ↔ backend)
├── X-Frappe-CSRF-Token injected by useFrappe.js on every POST
├── Token read from window.frappe.csrf_token (injected by www/portal/index.py)
└── Fallback: read from csrf_token cookie

Layer 4: Webhook signature verification
├── HMAC-SHA256 on payload
├── Secret stored in gateway settings (not in code)
└── verify_webhook_signature() in api/v1/__init__.py
```

### 12.2 SQL Injection Prevention

As documented in the codebase (post Phase 03.1-06 security audit):

- All parameterized queries use `%s` placeholders with tuple arguments (never f-strings in SQL)
- `frappe.get_all()` and `frappe.get_doc()` use ORM (safe by default)
- Raw SQL via `frappe.db.sql()` uses parameter binding throughout
- Student query override (`student_query` in `overrides/student.py`) uses parameterized `%(txt)s`
- `faculty_api.py` uses Frappe ORM (`frappe.get_all`, `frappe.db.get_value`) throughout — no raw SQL

### 12.3 Portal Security Boundary

```
useFrappe.call() error handling:
├── HTTP 401 → window.location.href = /login?redirect-to=/portal/
│   (session expired — force re-authentication)
│
├── HTTP 403 → throw 'Permission denied'
│   (component shows error state — no redirect, user stays on page)
│   (this is the backend's authoritative rejection, not a Vue guard)
│
└── data.exc → extract and throw server exception message
    (Frappe exception serialized as string in response body)

Backend always authoritative:
• Vue router guards are UX convenience only
• A user with a tampered JWT or manually edited role cookie will
  still get 403 from every @frappe.whitelist endpoint
• company-scope is derived from Employee/Student record on server,
  not from any client-provided parameter
```

### 12.4 File Upload Security

- Student photos: stored in `private/files/` (not publicly accessible)
- Category certificates: private attachment, accessible only to authorized roles
- Exam answer sheets: private, accessible only to Exams Staff + System Manager
- Proctoring snapshots: private, auto-purged after result declaration

### 12.5 Emergency Broadcast System

```
Emergency Alert DocType (university_erp/doctype/emergency_alert/)
├── Created by: Principal / Admin (in portal management view or Desk)
├── Broadcast via:
│   ├── SocketIO push to all active portal sessions (real-time overlay)
│   ├── SMS to all enrolled students in affected campus
│   ├── WhatsApp to parent mobile numbers
│   └── Email via notification_service
├── Acknowledgment tracking: Emergency Acknowledgment DocType
└── Expiry: auto-expire at specified datetime
```

---

## Appendix A: DocType Inventory by Module

| Module                  | DocTypes (custom)         | Notable DocTypes                                      |
|-------------------------|---------------------------|-------------------------------------------------------|
| university_erp (core)   | 23                        | University Settings, Notice Board, Emergency Alert, NAAC Metric |
| university_portals      | 0 (API only)              | portal_api.py, faculty_api.py — no DocTypes, pure Python API |
| university_academics    | 7                         | Course Registration, Timetable Slot, Elective Course Group |
| university_admissions   | 6                         | Admission Cycle, Merit List, Seat Matrix              |
| university_student_info | 4                         | Student Status Log, University Alumni                 |
| university_examinations | 16                        | Hall Ticket, Online Examination, Question Bank, Practical Examination |
| faculty_management      | 10                        | Faculty Profile, Teaching Assignment, Workload Distributor |
| university_hostel       | 12                        | Hostel Building, Room, Allocation, Attendance, Maintenance |
| university_transport    | 5                         | Transport Route, Vehicle, Allocation, Trip Log        |
| university_library      | 7                         | Library Article, Transaction, Fine, Reservation       |
| university_placement    | 10                        | Placement Company, Drive, Job Opening, Application, Resume |
| university_lms          | 15                        | LMS Course, Module, Assignment, Quiz, Discussion      |
| university_research     | 6                         | Research Project, Grant, Publication                  |
| university_obe          | 25                        | Course Outcome, Program Outcome, CO-PO Mapping, Attainment |
| university_integrations | 20                        | SMS Template, WhatsApp Template, Biometric Device, DigiLocker |
| university_payments     | 3                         | Payment Transaction (+ webhook logs, settings)        |
| university_analytics    | 10                        | Custom Dashboard, KPI Definition, Scheduled Report    |
| university_grievance    | ~5                        | Grievance + SLA tracking                              |
| university_feedback     | ~5                        | Feedback Form, Response, Analytics                    |
| university_inventory    | 15                        | Lab Equipment, Booking, Asset, Maintenance            |
| **Total (custom)**      | **~204**                  | Plus 83 custom fields on base DocTypes                |

---

## Appendix B: Key Configuration Files

| File                                                              | Purpose                                          |
|-------------------------------------------------------------------|--------------------------------------------------|
| `university_erp/hooks.py`                                         | All Frappe hooks, route rules, scheduled tasks   |
| `university_erp/modules.txt`                                      | 21 module names registered with Frappe           |
| `university_erp/fixtures/custom_field.json`                       | 83 custom fields on base DocTypes                |
| `university_erp/setup/install.py`                                 | Post-install: grading scale, settings, hide ERPNext workspaces |
| `university_erp/university_erp/api/v1/__init__.py`                | API decorator, auth, error classes (external API)|
| `university_erp/university_portals/api/portal_api.py`             | 28 portal API endpoints (session, student, parent)|
| `university_erp/university_portals/api/faculty_api.py`            | 27 faculty portal endpoints                      |
| `university_erp/www/portal/index.py`                              | SPA shell: Guest redirect, Vite manifest reader  |
| `university_erp/www/portal/index.html`                            | HTML template (injects vue_js, vue_css from context) |
| `university_erp/overrides/student.py`                             | UniversityStudent class, permission hooks        |
| `university_erp/boot.py`                                          | Session boot data (roles, settings, academic year)|
| `university_erp/university_payments/payment_gateway.py`           | Unified Razorpay + PayU interface                |
| `university_erp/university_integrations/*.py`                     | SMS, WhatsApp, Biometric, DigiLocker adapters    |
| `portal-vue/src/main.js`                                          | Vue app entry point — session fetch before mount |
| `portal-vue/src/stores/session.js`                                | Pinia session store (roles, auth state)          |
| `portal-vue/src/router/index.js`                                  | Route table + beforeEach auth guard              |
| `portal-vue/src/config/navigation.js`                             | Single source of truth for sidebar + role-to-route mapping |
| `portal-vue/src/composables/useFrappe.js`                         | Base API client (CSRF, error handling)           |
| `portal-vue/src/composables/useFacultyApi.js`                     | 27 faculty domain endpoints                      |
| `portal-vue/src/layouts/PortalLayout.vue`                         | Shell: skip link + Sidebar + main landmark       |
| `portal-vue/vite.config.js`                                       | Build config: output to university_erp/public/portal/ |
| `portal-vue/vitest.config.js`                                     | Test config: jsdom + vitest-axe for a11y testing |

---

## Appendix C: Marathi Language Support

The platform serves 25,000 students and ~2,000 staff in Maharashtra. Bilingual support:

- Frappe's built-in `gettext` translation framework
- Translation files in `university_erp/translations/mr.csv` (Marathi)
- UI language switchable per user in Frappe preferences
- portal-vue components use translation-ready string patterns (Phase 7 will add i18n)
- SMS and WhatsApp templates available in both languages (WhatsApp Template DocType with language field)
- NAAC reports generated in English (regulatory requirement)
- Student portal defaults to English with Marathi option via language selector

---

*Document prepared based on analysis of the university_erp codebase at `/workspace/development/frappe-bench/apps/university_erp/` and the portal-vue frontend at `/workspace/development/portal-vue/`. All module names, DocType names, API paths, hook configurations, and component names reflect the actual implementation as of March 2026. Document version 2.0 reflects the architectural shift from Frappe Desk workspaces for all users to the two-tier model: Frappe Desk (System Admin only) + portal-vue unified SPA (all other roles).*
