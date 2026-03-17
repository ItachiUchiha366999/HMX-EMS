# Architecture Research

**Domain:** University ERP Dashboards, Analytics & Multi-Role Portals
**Researched:** 2026-03-17
**Confidence:** HIGH (based on direct codebase analysis of existing patterns)

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Vue 3 Unified Portal SPA                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Student  │ │ Faculty  │ │   HOD    │ │  Parent  │ │Management│ │
│  │  Module  │ │  Module  │ │  Module  │ │  Module  │ │Dashboard │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │            │            │        │
│  ┌────┴────────────┴────────────┴────────────┴────────────┴─────┐  │
│  │              Shared Layer (composables, components)           │  │
│  │  useAuth  useFrappe  useRole  Charts  DataTable  KPICard    │  │
│  └──────────────────────────┬───────────────────────────────────┘  │
├─────────────────────────────┼─────────────────────────────────────┤
│                     HTTP / WebSocket                               │
│         /api/method/*  (REST)    │    Socket.IO (realtime)         │
├─────────────────────────────┼─────────────────────────────────────┤
│                     Frappe Backend                                  │
│  ┌──────────────────┐  ┌────┴───────────┐  ┌───────────────────┐  │
│  │   Portal APIs    │  │ Analytics APIs │  │  Dashboard Engine │  │
│  │ (portal_api.py)  │  │   (api.py)     │  │(dashboard_engine) │  │
│  └────────┬─────────┘  └────────┬───────┘  └────────┬──────────┘  │
│           │                     │                    │             │
│  ┌────────┴─────────────────────┴────────────────────┴──────────┐  │
│  │              Frappe ORM / Permission Layer                    │  │
│  │  frappe.get_doc  frappe.get_all  frappe.has_permission       │  │
│  └──────────────────────────┬───────────────────────────────────┘  │
├─────────────────────────────┼─────────────────────────────────────┤
│           MariaDB           │           Redis                      │
│  275+ doctypes across       │  Session cache, queue,               │
│  21 modules                 │  realtime pub/sub                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **Unified Portal SPA** | Single Vue 3 app serving all roles via role-based routing | Frappe Backend via REST + Socket.IO |
| **Role Modules** (Student/Faculty/HOD/Parent/Management) | Role-specific views, navigation, and feature sets | Shared Layer for data fetching, shared UI components |
| **Shared Layer** | Auth, API client, role resolution, chart components, data tables | Portal APIs, Analytics APIs |
| **Portal APIs** (`portal_api.py`) | Role-scoped data retrieval, action endpoints (attendance marking, grade entry, approvals) | Frappe ORM, existing module code |
| **Analytics APIs** (`api.py`) | KPI calculation, dashboard data, trend queries, report execution | Dashboard Engine, Analytics Manager, KPI definitions |
| **Dashboard Engine** (`dashboard_engine.py`) | Widget data assembly, report execution, query execution, access control | Frappe Reports, custom SQL, Python methods |
| **Report Scheduler** | Automated PDF/Excel generation, email distribution | Frappe Reports, File storage, Email |
| **Frappe Permission Layer** | DocType-level CRUD permissions, role resolution via `frappe.get_roles()` | MariaDB, Redis session |

## Recommended Project Structure

```
student-portal-vue/           -->  portal-vue/  (rename)
├── src/
│   ├── app/                    # App shell
│   │   ├── App.vue             # Root: role resolver + layout selector
│   │   └── RoleResolver.vue    # Determines user role, redirects
│   │
│   ├── layouts/                # Role-specific layouts
│   │   ├── StudentLayout.vue   # (existing, minor refactor)
│   │   ├── FacultyLayout.vue   # New
│   │   ├── HODLayout.vue       # New (extends FacultyLayout)
│   │   ├── ParentLayout.vue    # New
│   │   ├── ManagementLayout.vue # New (dashboard-focused)
│   │   └── AdminLayout.vue     # (existing)
│   │
│   ├── modules/                # Role-scoped feature modules
│   │   ├── student/            # Existing views, moved here
│   │   │   ├── views/
│   │   │   ├── composables/
│   │   │   └── routes.js
│   │   ├── faculty/
│   │   │   ├── views/
│   │   │   │   ├── FacultyDashboard.vue
│   │   │   │   ├── AttendanceMarking.vue
│   │   │   │   ├── GradeEntry.vue
│   │   │   │   ├── MyTimetable.vue
│   │   │   │   ├── StudentPerformance.vue
│   │   │   │   └── LeaveWorkload.vue
│   │   │   ├── composables/
│   │   │   │   └── useFaculty.js
│   │   │   └── routes.js
│   │   ├── hod/
│   │   │   ├── views/
│   │   │   │   ├── HODDashboard.vue
│   │   │   │   ├── DepartmentAnalytics.vue
│   │   │   │   ├── FacultyManagement.vue
│   │   │   │   ├── Approvals.vue
│   │   │   │   └── BudgetView.vue
│   │   │   ├── composables/
│   │   │   │   └── useHOD.js
│   │   │   └── routes.js
│   │   ├── parent/
│   │   │   ├── views/
│   │   │   │   ├── ParentDashboard.vue
│   │   │   │   ├── ChildAcademics.vue
│   │   │   │   ├── ChildFinance.vue
│   │   │   │   ├── ChildHostelTransport.vue
│   │   │   │   └── Communication.vue
│   │   │   ├── composables/
│   │   │   │   └── useParent.js
│   │   │   └── routes.js
│   │   └── management/
│   │       ├── views/
│   │       │   ├── ExecutiveDashboard.vue
│   │       │   ├── FinanceDashboard.vue
│   │       │   ├── AcademicDashboard.vue
│   │       │   ├── DrillDown.vue
│   │       │   └── ReportViewer.vue
│   │       ├── composables/
│   │       │   └── useDashboard.js
│   │       └── routes.js
│   │
│   ├── shared/                 # Shared across all roles
│   │   ├── components/
│   │   │   ├── charts/         # Chart.js wrappers
│   │   │   │   ├── BarChart.vue
│   │   │   │   ├── LineChart.vue
│   │   │   │   ├── PieChart.vue
│   │   │   │   └── GaugeChart.vue
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICard.vue
│   │   │   │   ├── StatCard.vue
│   │   │   │   ├── TrendIndicator.vue
│   │   │   │   ├── AlertBanner.vue
│   │   │   │   └── WidgetGrid.vue
│   │   │   ├── data/
│   │   │   │   ├── DataTable.vue
│   │   │   │   ├── FilterBar.vue
│   │   │   │   └── ExportButton.vue
│   │   │   └── ui/
│   │   │       ├── LoadingState.vue
│   │   │       ├── ErrorBoundary.vue
│   │   │       └── EmptyState.vue
│   │   └── composables/
│   │       ├── useFrappe.js    # (existing, enhanced)
│   │       ├── useAuth.js      # (existing, enhanced for multi-role)
│   │       ├── useRole.js      # NEW: role detection + guard
│   │       ├── useRealtime.js  # NEW: Socket.IO wrapper
│   │       ├── useExport.js    # NEW: PDF/Excel export triggers
│   │       └── useChart.js     # NEW: chart data formatting
│   │
│   ├── router/
│   │   └── index.js            # Unified router, imports module routes
│   │
│   └── main.js
│
├── vite.config.js
└── package.json
```

### Structure Rationale

- **modules/**: Feature-based grouping by role. Each module owns its routes, views, and composables. Enables code-splitting per role so a parent never downloads faculty code.
- **shared/**: Components and composables used across 2+ roles. The `useFrappe` composable already exists and is the proven pattern for backend communication.
- **layouts/**: Each role gets a layout with its own sidebar navigation, header, and mobile bottom nav. HODLayout extends FacultyLayout because HOD sees everything faculty sees plus more.
- **router/index.js**: Central router that imports route definitions from each module. Route-level guards check role before loading module chunks.

## Architectural Patterns

### Pattern 1: Role-Based Route Guards with Lazy Module Loading

**What:** The router determines user role once at app boot, stores it in a reactive composable, and uses per-route `meta.roles` to gate access. Each module's routes are lazy-imported so only the active role's code is downloaded.

**When to use:** Every route in the unified app.

**Trade-offs:** Adds a loading spinner on first navigation (role resolution API call), but prevents unauthorized module code from even being downloaded.

**Example:**
```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/portal/'),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../app/RoleResolver.vue')
    },
    // Student routes (existing, relocated)
    ...studentRoutes,
    // Faculty module - lazy loaded
    {
      path: '/faculty',
      component: () => import('../layouts/FacultyLayout.vue'),
      meta: { roles: ['Instructor'] },
      children: (await import('../modules/faculty/routes.js')).default
    },
    // HOD module
    {
      path: '/hod',
      component: () => import('../layouts/HODLayout.vue'),
      meta: { roles: ['Department Head', 'HOD'] },
      children: (await import('../modules/hod/routes.js')).default
    },
    // Parent module
    {
      path: '/parent',
      component: () => import('../layouts/ParentLayout.vue'),
      meta: { roles: ['Guardian'] },
      children: (await import('../modules/parent/routes.js')).default
    },
    // Management dashboards
    {
      path: '/dashboard',
      component: () => import('../layouts/ManagementLayout.vue'),
      meta: { roles: ['Vice Chancellor', 'Registrar', 'Finance Officer', 'Dean'] },
      children: (await import('../modules/management/routes.js')).default
    }
  ]
})

// Guard
router.beforeEach(async (to) => {
  const { role, resolveRole } = useRole()
  if (!role.value) await resolveRole()

  if (to.meta.roles && !to.meta.roles.some(r => role.value.includes(r))) {
    return { name: 'home' }  // RoleResolver will redirect properly
  }
})
```

### Pattern 2: Backend API Facade per Role

**What:** Each portal role gets its own API facade file on the backend that aggregates data from multiple doctypes into role-appropriate payloads. The existing `portal_api.py` already follows this pattern for student and faculty. Extend it with separate files.

**When to use:** Every new portal role (HOD, Parent, Management).

**Trade-offs:** More backend files, but each endpoint returns exactly what a single view needs (one request per page load, not N+1 calls from the frontend).

**Example:**
```python
# university_portals/api/hod_api.py

@frappe.whitelist()
def get_hod_dashboard():
    """Single API call returns everything the HOD dashboard needs"""
    instructor = get_current_instructor()
    department = get_instructor_department(instructor.name)

    return {
        "department": department,
        "faculty_count": frappe.db.count("Instructor", {"department": department}),
        "student_count": frappe.db.count("Student", {"department": department}),
        "pending_approvals": get_pending_approvals(department),
        "attendance_today": get_department_attendance_today(department),
        "recent_grievances": get_department_grievances(department, limit=5),
        "kpis": get_department_kpis(department)
    }
```

### Pattern 3: Dashboard Widget Composition via Dashboard Engine

**What:** The existing `DashboardEngine` already supports widget-based dashboards with multiple data sources (Report, Query, Method, Static). Management dashboards should compose widgets through `Custom Dashboard` doctype configuration rather than hardcoded views. The engine handles access control, data formatting, and error isolation per widget.

**When to use:** Management dashboards (VC, Registrar, Finance Officer, Dean). NOT for portal views (which need tighter, role-specific API facades).

**Trade-offs:** Configuration-driven dashboards are flexible but harder to optimize for performance. Use pre-computed KPI values (stored in `KPI Value` doctype) for widgets that query expensive aggregations.

### Pattern 4: Polling with Stale-While-Revalidate for Dashboard KPIs

**What:** Dashboard KPI cards use polling (not WebSocket) with a stale-while-revalidate strategy. Show cached data immediately, fetch fresh data in the background, update UI when ready. The existing `refresh_interval` field on `Custom Dashboard` already supports this.

**When to use:** All KPI cards and dashboard widgets.

**Why not WebSocket:** Frappe's `publish_realtime` works well for event-driven notifications (grievance updates, emergency alerts -- already used in the codebase). But KPI values are computed aggregations, not event streams. Polling every 30-60 seconds is simpler, more reliable, and avoids the complexity of maintaining WebSocket connections for data that changes slowly.

**Reserve Socket.IO for:** Notification badges, emergency alerts, approval notifications -- events that are genuinely real-time and already use `frappe.publish_realtime` in the existing codebase.

**Example:**
```javascript
// shared/composables/useDashboard.js
export function useDashboard(dashboardName) {
  const data = ref(null)
  const stale = ref(false)
  let pollInterval = null

  async function fetch(filters = {}) {
    const { call } = useFrappe()
    try {
      const fresh = await call(
        'university_erp.university_erp.analytics.api.get_dashboard',
        { dashboard_name: dashboardName, filters: JSON.stringify(filters) },
        { method: 'GET' }
      )
      data.value = fresh
      stale.value = false
    } catch (e) {
      stale.value = true  // keep showing old data
    }
  }

  function startPolling(intervalMs = 60000) {
    fetch()
    pollInterval = setInterval(fetch, intervalMs)
  }

  onUnmounted(() => clearInterval(pollInterval))
  return { data, stale, fetch, startPolling }
}
```

### Pattern 5: Drill-Down Navigation via Route Params

**What:** Management dashboards support drill-down from summary to detail: University > Department > Program > Student. Implement as route navigation with query params rather than in-page state, so drill-down views are bookmarkable and shareable.

**When to use:** Every summary metric that links to more detail.

**Example:**
```
/dashboard/academic                           # University-level overview
/dashboard/academic?department=CSE            # Department drill-down
/dashboard/academic?department=CSE&program=BTech  # Program drill-down
/dashboard/academic?student=STU-2026-001      # Student detail
```

## Data Flow

### Portal Page Load Flow

```
User navigates to /portal/
    |
RoleResolver.vue
    |
    +--> GET /api/method/portal_api.get_portal_redirect
    |    (returns role type: student|faculty|parent|hod|management)
    |
    +--> router.push('/faculty') or '/parent' etc.
    |
FacultyLayout.vue loads
    |
    +--> Route guard checks meta.roles against useRole().role
    |
FacultyDashboard.vue mounts
    |
    +--> GET /api/method/portal_api.get_faculty_dashboard
    |    (single aggregated payload)
    |
    +--> Render KPI cards, timetable, pending tasks
```

### Dashboard Data Flow

```
ManagementDashboard.vue
    |
    +--> useDashboard('executive-dashboard').startPolling(60000)
    |
    +--> GET /api/method/analytics.api.get_dashboard
    |    { dashboard_name, filters }
    |
DashboardEngine.get_dashboard_data()
    |
    +--> Check has_access() via role/user tables
    |
    +--> For each widget:
    |    +--> data_source == "Report"  --> frappe.desk.query_report.run()
    |    +--> data_source == "Query"   --> frappe.db.sql()
    |    +--> data_source == "Method"  --> frappe.get_attr(method_path)()
    |    +--> data_source == "Static"  --> return config
    |
    +--> Format per widget_type (Number Card, Chart, Table, Gauge, etc.)
    |
    +--> Return { widgets: {0: {...}, 1: {...}}, refresh_interval: 60 }
```

### Report Export Flow

```
User clicks "Export PDF" in dashboard
    |
    +--> POST /api/method/analytics.api.execute_custom_report
    |    { report_name, filters, format: "pdf" }
    |
ReportScheduler._generate_pdf()
    |
    +--> frappe.desk.query_report.run()
    +--> Build HTML table
    +--> frappe.utils.pdf.get_pdf(html)
    +--> Save as File doctype (private)
    |
    +--> Return { file_url: "/private/files/report_20260317.pdf" }
    |
Frontend triggers download via file_url
```

### Real-Time Notification Flow (existing, extend to portal)

```
Backend event (e.g., grievance status change)
    |
    +--> frappe.publish_realtime('university_notification', data, user=user)
    |
Socket.IO server (Redis pub/sub)
    |
    +--> Socket.IO client in Vue SPA
    |
useRealtime() composable
    |
    +--> Update notification badge count
    +--> Show toast notification
```

## Key Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Vue SPA <-> Frappe Backend | REST via `@frappe.whitelist()` methods, CSRF token in cookie | Existing pattern in `useFrappe.js`. All API calls go through `/api/method/` prefix |
| Vue SPA <-> Socket.IO | WebSocket via Frappe's built-in socketio server on port 9000 | Already configured in nginx. Used for notifications, not for data polling |
| Portal APIs <-> Existing Module Code | Python imports from `www/` and module packages | Existing pattern: `portal_api.py` imports from `www.student_portal.index`, `www.faculty_portal.index` |
| Dashboard Engine <-> Frappe Reports | `frappe.desk.query_report.run()` | Executes existing 54+ reports programmatically. Returns columns + data |
| Dashboard Engine <-> KPI System | `AnalyticsManager.calculate_kpi()` reads `KPI Definition`, stores in `KPI Value` | Pre-computed values avoid expensive real-time aggregation |
| Report Scheduler <-> Email | `frappe.sendmail()` with File attachment | Existing pattern for automated report distribution |

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Razorpay/PayU | Existing payment gateway integration via `Payment Request` doctype | Parent portal payment flows reuse existing student payment code |
| WhatsApp/SMS | Existing notification integrations | Can extend for parent notifications about child's attendance |
| Firebase | Push notification integration exists | Potential for mobile web push from portal |

### Cross-App Data Dependencies

| Data Need | Source App | DocType | Risk |
|-----------|-----------|---------|------|
| Student records | Education | Student | LOW - core, well-tested |
| Instructor records | Education | Instructor | LOW - core |
| Attendance | Education/Custom | Student Attendance | MEDIUM - cross-app verification needed |
| Fee data | ERPNext/Custom | Fees, Fee Schedule | MEDIUM - custom overrides exist |
| Leave data | HRMS | Leave Application | MEDIUM - HRMS integration untested |
| Department data | ERPNext | Department | LOW - standard doctype |
| Guardian-Student link | Education | Student Guardian (child table) | HIGH - existing SQL in portal_api.py has a bug (joins on wrong column) |

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-5k users (current target) | Current architecture is fine. Single Frappe instance, polling dashboards, direct SQL queries in dashboard engine |
| 5k-20k concurrent | Cache expensive KPI calculations in Redis (already available). Pre-compute dashboard data on schedule instead of on-demand. Use `KPI Value` doctype as cache layer |
| 20k+ concurrent | Separate read replica for analytics queries. Move dashboard engine to background workers. Consider dedicated analytics database (materialized views) |

### Scaling Priorities

1. **First bottleneck: Dashboard SQL queries.** The `DashboardEngine._execute_query()` runs raw SQL on every widget load. At scale, cache widget results in Redis with 30-60 second TTL. The `refresh_interval` field already exists on `Custom Dashboard` -- use it as cache TTL.
2. **Second bottleneck: Report generation.** PDF generation is CPU-intensive. The `ReportScheduler` already runs via scheduled tasks, which is correct. Never generate PDFs synchronously on user request -- queue them via `frappe.enqueue()` and notify via Socket.IO when ready.

## Anti-Patterns

### Anti-Pattern 1: Separate SPA per Role

**What people do:** Build `/student-portal-spa/`, `/faculty-portal-spa/`, `/parent-portal-spa/` as independent Vue apps with duplicated components.
**Why it's wrong:** Duplicated UI code, inconsistent UX, 4x build configs, impossible to share auth state.
**Do this instead:** Single unified SPA at `/portal/` with role-based routing and code-splitting. The existing student portal gets absorbed as the `student` module.

### Anti-Pattern 2: N+1 API Calls from Frontend

**What people do:** Frontend makes 8 separate API calls to populate a dashboard page (one per card/widget).
**Why it's wrong:** Slow page loads, race conditions, complex loading states.
**Do this instead:** One aggregated API call per page (the existing `get_student_dashboard`, `get_faculty_dashboard` pattern). Each endpoint returns everything the view needs.

### Anti-Pattern 3: WebSocket for Everything

**What people do:** Use Socket.IO to push every KPI update in real-time.
**Why it's wrong:** KPIs are computed aggregations that change slowly. WebSocket connections consume server resources. Complex reconnection logic needed.
**Do this instead:** Polling at 30-60 second intervals for dashboards. Reserve Socket.IO for genuine events (notifications, approvals, alerts) -- which the codebase already does correctly.

### Anti-Pattern 4: Bypassing Frappe Permissions in Portal APIs

**What people do:** Use `ignore_permissions=True` on every query to "simplify" portal code.
**Why it's wrong:** Security hole. Any authenticated user could access any student's data.
**Do this instead:** Every portal API must verify the caller's identity against the resource (the existing `get_current_student()` / `get_current_guardian()` pattern is correct). Use `frappe.has_permission()` for DocType-level checks, and explicit ownership verification for record-level access.

### Anti-Pattern 5: Hardcoded Dashboard Layouts in Vue Components

**What people do:** Build each management dashboard as a fixed Vue component with hardcoded widget positions.
**Why it's wrong:** Every new KPI or layout change requires a frontend deployment.
**Do this instead:** Use the existing `Custom Dashboard` + `Dashboard Widget` doctype configuration. The `DashboardEngine` already returns layout metadata (columns, positions, widget types). The Vue frontend renders a generic `WidgetGrid` driven by this configuration.

## Build Order (Dependency Chain)

The following order reflects component dependencies -- each phase builds on what the previous phase established:

```
Phase 1: Unified App Shell + Role System
    |  - Refactor student portal into module structure
    |  - Build useRole composable + role-based routing
    |  - Build shared layout components
    |  - Backend: enhance get_portal_redirect with all roles
    |
    v
Phase 2: Shared Dashboard Components
    |  - Chart components (Chart.js wrappers)
    |  - KPI cards, stat cards, trend indicators
    |  - DataTable with sort/filter
    |  - Export button component
    |  - useRealtime composable for notifications
    |
    v
Phase 3: Faculty Portal
    |  - Faculty API facade (extends existing portal_api.py stubs)
    |  - FacultyLayout + views (dashboard, attendance, grades)
    |  - Depends on: app shell (P1), shared components (P2)
    |
    v
Phase 4: HOD Portal
    |  - HOD API facade (extends faculty with department scope)
    |  - HODLayout + views (approvals, dept analytics, faculty mgmt)
    |  - Depends on: faculty module (P3, HOD sees faculty features)
    |
    v
Phase 5: Parent Portal
    |  - Parent API facade (fix guardian-student link query)
    |  - ParentLayout + views (child selector, academics, fees)
    |  - Depends on: app shell (P1), shared components (P2)
    |  - Independent of faculty/HOD -- can be parallelized with P3/P4
    |
    v
Phase 6: Management Dashboards
    |  - Connect Vue to existing DashboardEngine + Analytics APIs
    |  - WidgetGrid renderer, drill-down navigation
    |  - Report viewer with export
    |  - Depends on: shared chart components (P2), backend APIs (already exist)
    |
    v
Phase 7: Report Export & Scheduling
       - Frontend triggers for PDF/Excel export
       - Scheduled report configuration UI
       - Depends on: management dashboards (P6)
```

**Critical note:** Phase 5 (Parent Portal) is independent of Phases 3-4 (Faculty/HOD). It can be built in parallel if team capacity allows. Phase 6 (Management Dashboards) has the most existing backend support (DashboardEngine, Analytics APIs, KPI system all exist) but needs the shared chart components from Phase 2.

## Sources

- Direct codebase analysis of `/workspace/development/student-portal-vue/` (Vue 3 SPA structure, composables, router)
- Direct codebase analysis of `/workspace/development/frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py` (700+ lines of existing portal APIs for student, faculty, parent)
- Direct codebase analysis of `/workspace/development/frappe-bench/apps/university_erp/university_erp/university_erp/analytics/` (DashboardEngine, Analytics API, executive dashboard, report scheduler, KPI system)
- Direct codebase analysis of `university_analytics` doctypes (Custom Dashboard, Dashboard Widget, KPI Definition, KPI Value, Dashboard Role/User access control)
- Frappe realtime usage grep across codebase: `frappe.publish_realtime` used in notifications, emergency alerts, grievances, examinations (confirms event-driven pattern for notifications)
- Frappe framework knowledge: `@frappe.whitelist()`, `frappe.get_roles()`, `frappe.has_permission()`, `frappe.desk.query_report.run()`, `frappe.utils.pdf.get_pdf()`, Socket.IO via Redis pub/sub (HIGH confidence -- standard Frappe patterns confirmed in codebase)

---
*Architecture research for: University ERP Dashboards, Analytics & Multi-Role Portals*
*Researched: 2026-03-17*
