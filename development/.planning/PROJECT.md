# University ERP — Dashboards, Analytics & Role-Based Portals

## What This Is

A production-ready university ERP system built on Frappe v15 with a **two-tier architecture**: Frappe Desk as admin-only backend, and a unified Vue 3 portal as the frontend for ALL other users (students, faculty, HODs, parents, management). The system has 275+ doctypes across 21 modules with ERPNext (accounting only), HRMS, Education, and a custom university_erp app inside a Docker dev container. ERPNext's Accounts module is being forked into university_erp with student-centric terminology. The existing student-portal-spa is being recreated within the unified portal-vue app.

## Core Value

University leadership can make data-driven decisions through real-time dashboards with drill-down capability, while students, faculty, HODs, and parents have self-service portal access to the information and actions relevant to their role — all through a single unified portal UI.

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
- Removing unused ERPNext modules — keep hidden via hooks.py block_modules, don't uninstall

## Context

**Technical environment:**
- Frappe v15+ / ERPNext v15+ / HRMS v15+ / Education v15+ running in Docker dev container
- MariaDB database, Redis cache/queue
- Unified portal: Vue 3.5 + Vue Router 4.6 + Pinia + Vite — at portal-vue/
- Backend APIs via Frappe @whitelist() decorated methods
- Site: university.local

**Two-tier architecture:**
- **Frappe Desk (backend UI)**: Admin-only. Used by system administrators for configuration, doctype management, and backend operations.
- **Portal-vue (frontend UI)**: ALL other users — students, faculty, HODs, parents, management. Single unified Vue 3 SPA with role-based routing.

**ERPNext module usage:**
- **Active**: Accounts (GL, Payment Entry, Bank Reconciliation, Cost Centers), Buying (procurement), Stock (inventory), Assets (depreciation)
- **Blocked/Hidden**: Manufacturing, Selling, CRM, Projects, Quality, Support — hidden via hooks.py block_modules
- **Being forked**: Accounts module → university_erp with student-centric labels (Customer→Student, Sales Invoice→Fee Invoice)

**Existing portal pages (server-rendered, to be replaced):**
- /faculty-portal/, /parent-portal/ — skeleton Jinja pages exist in /www/ (being replaced by portal-vue)
- /student-portal-vue/ — existing Vue 3 SPA with 11 pages (being recreated in portal-vue)

**Cross-app integration status (verified in Phase 03.1):**
- 1029 cross-app links tested, 1 broken (PO Attainment.department)
- 32 exact-name duplicate doctypes catalogued
- 189/279 reports passing (10 university_erp reports need schema fixes)
- Employee custom fields (custom_is_faculty etc.) defined in fixtures but not yet migrated to DB

**Codebase locations:**
- Custom app: /frappe-bench/apps/university_erp/
- Unified portal: /portal-vue/
- Student portal (legacy, to be recreated): /student-portal-vue/
- Portal API: university_portals/api/portal_api.py
- Faculty API: university_portals/api/faculty_api.py
- Analytics module: university_analytics/
- Existing dashboards: analytics/dashboards/executive_dashboard.py

## Constraints

- **Tech stack**: Must use Frappe framework backend, Vue 3 for portal — consistent with existing work
- **Architecture**: Unified Vue app with role-based routing — single codebase for all portal users. Frappe Desk is admin-only backend.
- **Data**: All data comes from existing doctypes — focus is on views, analytics, and the accounts fork
- **Integration**: Cross-app data flows verified in Phase 03.1 — gaps being closed
- **Deployment**: Docker container environment, portal builds to Frappe's public directory
- **Target**: Production deployment for a live university
- **ERPNext**: Only Accounts module actively used (being forked). Manufacturing/Selling/CRM blocked. Unused modules stay hidden, not removed.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Unified Vue app for all portals | Single codebase, shared components, easier maintenance vs separate SPAs | Decided — portal-vue/ |
| Frappe Desk = admin-only backend | Regular users should never touch Desk UI; portal covers all their needs | Decided — Phase 03.1 update |
| Fork ERPNext Accounts into university_erp | Confusing manufacturing labels, unused report noise, need university-specific features | Decided — full module fork with student-centric labels |
| Student-centric terminology | Customer→Student, Sales Invoice→Fee Invoice, Supplier→Vendor etc. | Decided — applies to forked module |
| Recreate student portal in portal-vue | Consistent UI across all user types, single codebase, shared components | Decided — all 11 existing student views recreated |
| Keep unused ERPNext modules hidden | Don't uninstall (dependency risk), just hide via hooks.py block_modules | Decided |
| Cross-app verification before dashboards | Dashboards built on bad data are worse than no dashboards | Complete — Phase 03.1 |
| Faculty + HOD + Parent + Student portals for v1 | All user-facing roles get portal access; HR/Accounts deferred | Decided |
| All 4 management dashboard personas | VC, Registrar, Finance Officer, Dean — each needs different KPIs | Decided |

---
*Last updated: 2026-03-19 after strategic pivot (accounts fork + student portal recreation + admin-only desk)*
