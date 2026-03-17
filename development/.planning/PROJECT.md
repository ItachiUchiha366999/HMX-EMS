# University ERP — Dashboards, Analytics & Role-Based Portals

## What This Is

A production-ready extension of an existing Frappe-based University ERP system (275+ doctypes across 21 modules) that adds management-level dashboards, analytics, and role-based portal interfaces for faculty, HODs, and parents. The system runs on Frappe v15 with ERPNext, HRMS, Education, and a custom university_erp app inside a Docker dev container. A Vue 3 student portal already exists and will be extended into a unified multi-role portal application.

## Core Value

University leadership can make data-driven decisions through real-time dashboards with drill-down capability, while faculty, HODs, and parents have self-service portal access to the information and actions relevant to their role.

## Requirements

### Validated

<!-- Existing and working -->

- ✓ 275+ doctypes across 21 modules (academics, admissions, exams, finance, hostel, library, placement, LMS, OBE, research, grievance, feedback, inventory, transport, integrations, analytics) — existing
- ✓ Student portal (Vue 3 SPA) with 11 pages — existing at /student-portal-vue
- ✓ 54+ custom reports (finance, academics, placement, library, hostel, OBE, inventory) — existing
- ✓ Backend portal API (portal_api.py) with whitelisted methods — existing
- ✓ Payment gateway integration (Razorpay, PayU) — existing
- ✓ Scheduled tasks (30+ cron jobs for fees, library, exams, attendance) — existing
- ✓ External integrations (DigiLocker, WhatsApp, Firebase, SMS) — existing

### Active

<!-- Current scope — building toward these -->

- [ ] Cross-app integration verification (ERPNext ↔ HRMS ↔ Education ↔ university_erp)
- [ ] Unified Vue portal app with role-based routing (faculty, HOD, parent roles)
- [ ] Faculty portal — timetable, attendance marking, grade entry, student performance analytics, leave & workload, research & OBE views, LMS management
- [ ] HOD portal — everything faculty sees plus approvals, department analytics, faculty management, budget view
- [ ] Parent portal — child's academics (attendance, grades, exams, timetable), finance (fees, payments), hostel & transport status, communication (messages, announcements, grievances)
- [ ] Management dashboards — Vice Chancellor, Registrar, Finance Officer, Dean/Director views
- [ ] Real-time KPI counters (enrollment, fee collection, attendance today)
- [ ] Trend charts (year-over-year, semester trends, projections)
- [ ] Drill-down reports (summary → department → program → student level)
- [ ] Export & scheduled reports (PDF/Excel export, email reports to stakeholders)
- [ ] Backend APIs for all new portal and dashboard features

### Out of Scope

- HR & Accounts staff portals — deferred, not v1 priority
- Mobile native app — web-first, responsive design covers mobile
- Real-time chat/messaging — high complexity, not core to management decision-making
- New doctype creation — doctypes already exist, focus is on views and analytics
- Student portal redesign — already functional, only extend with unified app shell

## Context

**Technical environment:**
- Frappe v15+ / ERPNext v15+ / HRMS v15+ / Education v15+ running in Docker dev container
- MariaDB database, Redis cache/queue
- Student portal: Vue 3.5 + Vue Router 4.6 + Tailwind CSS 3.4 + Vite 7.2
- Backend APIs via Frappe @whitelist() decorated methods
- Site: university.local

**Existing portal pages (server-rendered, to be replaced/integrated):**
- /faculty-portal/, /parent-portal/, /alumni-portal/, /placement-portal/ — skeleton Jinja pages exist in /www/

**Cross-app integration status:**
- Not thoroughly tested — verification needed before building portal views on top
- Education app overrides exist (6 classes: Student, Program, Course, AssessmentResult, Fees, Applicant)
- Hook integrations exist for document events (Student, Fees, Leave, Employee, Department)

**Codebase locations:**
- Custom app: /frappe-bench/apps/university_erp/
- Student portal: /student-portal-vue/
- Portal API: university_portals/api/portal_api.py
- Analytics module: university_analytics/
- Existing dashboards: analytics/dashboards/executive_dashboard.py

## Constraints

- **Tech stack**: Must use Frappe framework backend, Vue 3 + Tailwind for portals — consistent with existing student portal
- **Architecture**: Unified Vue app with role-based routing — single codebase for all portals
- **Data**: All data comes from existing doctypes — no new doctype creation, only new APIs/views
- **Integration**: Must verify cross-app data flows before building dashboard views
- **Deployment**: Docker container environment, builds to Frappe's public directory
- **Target**: Production deployment for a live university

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Unified Vue app for all portals | Single codebase, shared components, easier maintenance vs separate SPAs | — Pending |
| Vue 3 + Tailwind (same as student portal) | Consistency, reuse existing composables (useFrappe, useAuth) | — Pending |
| Cross-app verification before dashboards | Dashboards built on bad data are worse than no dashboards | — Pending |
| Faculty + HOD + Parent portals for v1 | Highest impact roles; HR/Accounts deferred | — Pending |
| All 4 management dashboard personas | VC, Registrar, Finance Officer, Dean — each needs different KPIs | — Pending |

---
*Last updated: 2026-03-17 after initialization*
