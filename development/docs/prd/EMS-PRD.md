# Product Requirements Document (PRD)

> **Project Name:** University ERP — Dashboards, Analytics & Role-Based Portals
> **Document Owner:** Vedant Zope, Engineering Lead
> **Stakeholders:** Product, Engineering, University Sponsor (Vice Chancellor / Registrar / Finance Officer / Dean), QA, System Administrator
> **Version:** 1.0
> **Date Created:** 30-Apr-2026
> **Last Updated:** 30-Apr-2026
> **Status:** ☐ Draft  ☑ In Review  ☐ Approved  ☑ In Development  ☐ Released

---

## 1. Executive Summary

We are building a unified Vue 3 portal and analytics layer on top of an existing Frappe v15 university ERP (275+ doctypes across 21 modules) to replace ad-hoc Excel-driven reporting and fragmented per-role UIs. The product gives students, faculty, HODs, parents, and management self-service access to the data and actions relevant to their role, while university leadership gets real-time KPI dashboards with drill-down from university → department → program → student. The strategy is **backend-first**: harden the Frappe backend (accounts fork, schema integrity, permission matrix) before any frontend rebuild, so portals are built once on stable foundations.

---

## 2. Problem Statement

- **Current pain point:** University leadership lacks a single source of truth for enrollment, fee collection, attendance, and academic performance — data lives across ERPNext, HRMS, Education, and a custom university_erp app, accessed through Frappe Desk (designed for sysadmins, not end-users) and patched together in Excel. Cross-app data has 1029 inter-doctype links of which integrity was previously unverified, 10+ reports broke silently, and ERPNext default labels (Customer, Sales Invoice, Supplier) confuse academic users.
- **Who feels it:**
  - **VC / Registrar / Finance Officer / Dean** — can't get real-time KPIs; rely on weekly Excel rollups.
  - **Faculty** — must use Frappe Desk for attendance/grades; takes >5 min per class for 60 students.
  - **Students / Parents** — no dedicated UI for fees, timetable, results, hostel, transport.
  - **HODs** — no department-level view; approvals scattered across Desk forms.
  - **System Administrators** — Desk usable, but report failures and broken cross-app links generate constant support tickets.
- **Cost of inaction:** Manual reporting consumes ~6 hrs/week per supervisor; finance reconciliation lags by days; broken reports erode trust in data; parent satisfaction (NAAC criterion) suffers without self-service; the university cannot scale enrollment without automating these flows.

---

## 3. Goals & Success Metrics

| # | Goal | Metric | Target | Measurement Method |
|---|------|--------|--------|--------------------|
| 1 | Reduce faculty time-to-mark attendance | Seconds per class of 60 students | < 120 s (from > 300 s in Desk) | In-app instrumentation; UAT timing trial |
| 2 | Eliminate broken reports | % of `university_erp` reports running error-free | 100% (from 83% baseline: 189/279) | Automated report-audit script (Phase 03.1-02) |
| 3 | Eliminate SQL injection risk | CRITICAL findings in static SQL scan | 0 (from 44 baseline) | Automated SQL audit (Phase 03.1-06) |
| 4 | Permission correctness | HIGH-severity unauthorized-access findings | 0 (from 2 baseline) | 9-role permission matrix audit |
| 5 | Cross-app data integrity | Broken doctype Link/Dynamic Link/Table targets | 0 | Schema audit script (Phase 03.4-04) |
| 6 | WCAG accessibility | Critical + serious WCAG 2.1 AA violations | 0 / 0 | vitest-axe automated runs |
| 7 | Management dashboard adoption | Distinct VC/Registrar/Finance/Dean weekly active users | ≥ 90% of role holders | Frappe `Activity Log` aggregation |
| 8 | Parent self-service adoption | % parents who pay fees online via portal | ≥ 60% within 1 semester post-launch | Razorpay/PayU webhook tags vs total fees |

**Non-goals** _(explicitly out of scope, to avoid scope creep)_:
- Predictive analytics / ML-based dropout risk scoring — deferred to v2.
- Real-time chat/messaging — WhatsApp integration covers it.
- Custom in-portal report builder — SQL injection surface; expose curated 54+ reports instead.
- Mobile-native app — responsive Vue covers mobile; PWA deferred to v2.
- Removing unused ERPNext modules — keep hidden via `block_modules`, do not uninstall (dependency risk).
- HR / Accounts staff portals and Alumni portal — not v1 priority.
- New doctype creation — all 275+ already exist; focus is views, analytics, accounts fork.
- Multi-campus real-time sync — single-university deployment only.

---

## 4. Target Users / Personas

| Persona | Role | Key Need |
|---------|------|----------|
| Student | Learner | One-stop view of timetable, attendance, grades, fees, exams, hostel, transport, library, placement, grievances; online fee payment |
| Faculty | Teaching staff | Mark attendance for 60 students in < 2 min; spreadsheet grade entry; LMS management; approve student leave; view workload, research, OBE |
| HOD | Department head | All faculty features for own courses + department-wide attendance/performance, faculty workload distribution, approval queue, CO-PO heatmap, budget |
| Parent / Guardian | Family stakeholder | Multi-child selector; child's academics, fees (online payment), hostel, transport; messaging with faculty — all guardian-verified (no IDOR) |
| Vice Chancellor | University leadership | University-wide KPIs (enrollment, collection, attendance, pass rate, faculty count, grievances) with year-over-year trends |
| Registrar | Academic administration | Admissions pipeline, examination status, student lifecycle metrics |
| Finance Officer | Finance leadership | Daily/monthly/yearly collection, outstanding dues, budget utilization |
| Dean / Director | Program leadership | Program-level academics, placement statistics, research output |
| System Administrator | IT operations | Frappe Desk only — configuration, doctype management, workflow setup, user/role admin |

---

## 5. Scope

**In Scope (v1):**

- Foundation & security hardening — parameterized SQL, permission guards, role-based routing, cached session auth, academic-year/semester global filter, management role detection (VC, Registrar, Finance Officer, Dean).
- Shared component library — KPI card, ApexCharts wrapper, TanStack DataTable, filter bar, jsPDF/ExcelJS export, report viewer, notification panel.
- Faculty portal — today's classes, bulk attendance, spreadsheet grade entry, pending tasks, performance analytics, leave management, LMS, research, OBE, workload, announcements.
- Comprehensive system audit & fix — 488 `@whitelist` endpoints audited, 9-role permission matrix, custom field migration, report fixes, SQL injection remediation, accessibility audit, business-logic duplicate documentation.
- ERPNext Accounts module fork into `university_finance` — student-centric relabeling (Customer → Student, Sales Invoice → Fee Invoice, Supplier → Vendor), unused doctypes/reports archived, GL/JE/PE/Bank Reconciliation working through fork, Razorpay/PayU webhooks redirected.
- Post-fork backend audit — demo data seed (510 students, 54 faculty, 800 GL entries), missing workflows, doctype CRUD audit, field-level Link validation, report schema validation, post-fork permission re-verification.
- Portal redesign & build — design system + recreated student portal (11 views), redesigned faculty portal, scaffolding for HOD / Parent / Management with shared components and dark mode.
- Management dashboards — VC, Registrar, Finance Officer, Dean role-specific views; enrollment trend; collection vs target; drill-down (university → department → program → student); department comparison; alert panel; report viewer over 54+ reports.
- Parent portal — multi-child selector with guardian ownership verification, attendance heatmap, grades/exams, fees + online payment, hostel/transport, announcements, messaging with faculty.
- HOD portal — inherits faculty features; department attendance, faculty workload, approval queue, department KPIs, CO-PO heatmap, budget utilization.
- Scheduled reports & cross-portal polish — PDF/Excel export verified across all data tables/reports; daily/weekly/monthly email scheduling with role-correct data scoping.

**Out of Scope (this release):**

- Student dropout prediction / ML risk scoring — planned for v2.
- Customizable dashboard widgets with drag-and-drop layout — planned for v2.
- NAAC/NIRF accreditation auto-report generation — planned for v2.
- Faculty performance scorecards (teaching effectiveness + research + feedback) — planned for v2.
- Real-time alert thresholds with WhatsApp/push delivery — planned for v2.
- HR staff portal, Accounts staff portal, Alumni portal — needs separate discovery.
- PWA manifest for mobile home-screen install — planned for v2.
- Real-time chat, custom report builder, mobile-native app, multi-campus sync, granular per-user permission builder, sub-5-second auto-refresh, full BI/OLAP engine — permanently excluded.

---

## 6. Functional Requirements

Authoritative requirement IDs live in `.planning/REQUIREMENTS.md`. Representative high-priority items are reproduced below; full list (85 v1 items) traceable in that file.

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FOUND-02 | SQL injection in `dashboard_engine.py` fixed with parameterized queries | P0 | Zero string-interpolated values in any `frappe.db.sql` call; static-scan returns 0 CRITICAL |
| FOUND-03 | Permission checks enforced on all analytics/dashboard API endpoints | P0 | A logged-in Student calling executive dashboard API receives 403, not data |
| FOUND-05 | Unified Vue app shell with role-based routing | P0 | Visiting `/portal/` routes user to correct module (student/faculty/HOD/parent/management) based on Frappe roles |
| COMP-01 | KPI counter card (value, label, trend, status color) | P0 | Component reused identically across faculty, management, HOD views; renders in < 100 ms |
| COMP-03 | Data table with sorting, pagination, search (TanStack) | P0 | Server-side pagination over 200+ rows; sort and search re-query backend in < 500 ms |
| FCTY-02 | Faculty bulk-mark attendance | P0 | 60 students marked in < 2 min; idempotent (re-submit doesn't duplicate Student Attendance) |
| FCTY-03 | Spreadsheet-style grade entry per course | P0 | Save without page reload; per-course grade distribution + at-risk analytics shown alongside |
| FCTY-08 | Faculty approve/reject student leave from portal | P0 | Decision propagates to Student Leave Application; student notified |
| ACCT-01 | Full ERPNext Accounts module forked into `university_finance` | P0 | Zero `from erpnext.accounts` imports remaining in `university_erp` |
| ACCT-04 | Fee → GL posting verified end-to-end through fork | P0 | Submitting Fees creates GL Entries with grand_total; smoke test green |
| ACCT-05 | Razorpay/PayU webhooks create Payment Entries through fork | P0 | Webhook handler uses `frappe.get_doc` ORM path; Payment Entry references university_finance accounts |
| AUDIT-BACKEND-04 | Cross-app data connections verified | P0 | Student↔Enrollment, Fees↔GL, Employee↔Faculty, Academic Year — all integrity scripts green |
| AUDIT-BACKEND-07 | Every Link/Dynamic Link/Table reference validated against parent doctype schema | P0 | Doctype schema audit returns zero broken targets |
| AUDIT-BACKEND-08 | Every report validated against source doctype schema, filter and join fields | P0 | Report schema audit returns zero field errors; all reports render data |
| PORTAL-01 | Design system chosen and implemented | P1 | Tokens, components, dark mode shared across all portal modules |
| PORTAL-02 | Student portal — all 11 views recreated | P0 | Each STUD-01..STUD-11 view rendered with real data; no Desk navigation needed |
| MGMT-01 | VC dashboard with university-wide KPIs | P0 | Real aggregated data (no mock); refresh on load + manual refresh |
| MGMT-09 | Drill-down navigation summary → department → program → student | P0 | Every KPI on every dashboard supports drill-through |
| MGMT-10 | Scheduled email delivery (daily/weekly/monthly) | P1 | Reports delivered on schedule with role-scoped data; failure alerts to admin |
| PRNT-01 | Multi-child selector with guardian ownership verification | P0 | Switching children rescopes all data; guardian-link check prevents IDOR (verified in tests) |
| PRNT-07 | Parent online fee payment via Razorpay/PayU in parent auth context | P0 | Payment Entry created with guardian as paying party; receipt emailed |
| HOD-01 | HOD inherits all faculty features for own courses | P0 | HOD route includes faculty module views without code duplication |
| HOD-04 | HOD approves/rejects faculty leave, course registrations, academic requests | P0 | Approval queue updates underlying doctypes; decisions audit-logged |
| HOD-07 | CO-PO attainment heatmap for department programs | P1 | Heatmap renders from `Faculty Publication`/COPOAttainmentCalculator with graceful fallback |
| ANLT-01 | PDF export on all data tables and reports | P1 | Export button on every table; correct column visibility + filter context |
| ANLT-02 | Excel export on all data tables and reports | P1 | ExcelJS dynamic import; export ≤ 5 s for 1,000 rows |
| ANLT-05 | Scheduled email delivery of any report on configurable frequency | P1 | Recipients configurable per report; cron job runs reliably |
| GAP-01..05 | Phase 03.1 gap closure (custom fields migrated, reports fixed, dashboard fix, faculty API verified) | P0 | All five GAP-* IDs marked Complete in REQUIREMENTS.md | 

> **Priority legend:** P0 = launch blocker · P1 = important · P2 = nice-to-have

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | Faculty attendance for 60 students < 2 min (FCTY-02); chart render < 500 ms; report load < 5 s for 1,000 rows; ExcelJS lazy-loaded via dynamic `import()` to keep initial bundle below 500 KB |
| Scalability | Single-university deployment; ~10,000 students × ~500 faculty × ~5 concurrent management users; pre-computed KPIs via cron rather than live OLAP |
| Security | All `@whitelist` endpoints role-checked (488 audited; 0 HIGH open); zero f-string interpolation in `frappe.db.sql`; parent endpoints enforce guardian ownership server-side; audit log retained per Frappe defaults |
| Availability | Production deployment on Docker container infrastructure; standard Frappe MariaDB + Redis stack; 99% business-hours availability target |
| Compatibility | Chrome, Edge, Safari, Firefox (latest 2 versions); Vue 3.5 + Vue Router 4.6 + Pinia + Vite; portal-vue builds to Frappe `public/portal/` |
| Accessibility | WCAG 2.1 AA: 0 critical and 0 serious violations enforced via vitest-axe; `--text-muted` ≥ 4.5:1 contrast on white |
| Localization | English for v1 (institutional language); doctype label fork already neutralizes manufacturing terminology to academic terms |
| Data correctness | 1029 cross-app links verified; idempotent demo seed with FY 2026-2027 backfill + GL re-post path; all reports validated against live schema (Phase 03.4-05) |
| Deployment | Docker dev container (Frappe v15+ / ERPNext v15+ / HRMS v15+ / Education v15+); MariaDB primary, Redis cache/queue; site `university.local`; portal-vue build output committed to Frappe `public/portal/` |

---

## 8. User Stories / Use Cases

**Story 1 — Faculty (Phase 3, complete):** As a *faculty member*, I want to *open today's class and bulk-mark attendance for all 60 students*, so that *I finish in under 2 minutes and don't lose teaching time to data entry*.

**Story 2 — Management (Phase 5):** As the *Vice Chancellor*, I want to *see live university-wide enrollment, fee collection, and pass-rate KPIs with year-over-year trends*, so that *I can make data-driven decisions in cabinet meetings without waiting for weekly Excel rollups*.

**Story 3 — Management drill-down (Phase 5):** As the *Finance Officer*, I want to *click a department's outstanding-dues number and drill from department → program → individual student*, so that *I can identify exactly which students need follow-up*.

**Story 4 — Parent (Phase 6):** As a *parent with two children enrolled*, I want to *switch between them in a child selector and pay outstanding fees for the selected child via Razorpay*, so that *I can manage both kids' finances from one login without confusion*.

**Story 5 — HOD (Phase 7):** As the *HOD of Computer Science*, I want to *see department-wide attendance and faculty workload distribution and approve pending faculty leave requests*, so that *I can rebalance teaching load before approving leave*.

**Story 6 — Student (Phase 4):** As a *student*, I want to *view my timetable, attendance heatmap, current grades, fees due, and hostel/transport status from one portal*, so that *I never have to call the office or open Frappe Desk*.

**Story 7 — System Administrator (ongoing):** As a *system administrator*, I want to *manage doctype configuration, workflows, and user roles only through Frappe Desk*, so that *end-user portals stay simple and admin operations stay auditable*.

**Story 8 — Stakeholder reporting (Phase 8):** As the *Registrar*, I want to *receive a weekly admissions-pipeline PDF in my inbox automatically*, so that *I have an accurate snapshot every Monday morning without logging in*.

---

## 9. Technical Considerations

- **Architecture:**
  - Two-tier: **Frappe Desk** (admin-only backend UI) + **portal-vue** (Vue 3.5 SPA for all end-users).
  - Backend: Frappe v15+ Python app `university_erp` (21 modules) layered on ERPNext v15+ (Accounts forked into `university_finance`, plus Buying/Stock/Assets), HRMS v15+, Education v15+. Manufacturing/Selling/CRM/Projects/Quality/Support hidden via `hooks.py block_modules`.
  - Frontend: Vue 3.5 + Vue Router 4.6 + Pinia + Vite at `portal-vue/`; build output committed to Frappe `public/portal/`. Pinia session store fetches once at boot; router guard reads synchronously (no per-route API calls).
  - Charts: ApexCharts via single wrapper component; tables: TanStack with manualPagination + manualSorting; tests: vitest + vitest-axe.
- **Integrations / APIs:**
  - Payment gateways: Razorpay, PayU (existing; webhooks redirected through `university_finance`).
  - External: DigiLocker, WhatsApp, Firebase, SMS (existing).
  - Backend APIs via Frappe `@whitelist()` decorated methods. Key surfaces: `university_portals/api/portal_api.py`, `university_portals/api/faculty_api.py` (27 endpoints), `university_analytics/`.
  - 30+ existing scheduled cron jobs (fees, library, exams, attendance) preserved.
- **Data model changes:**
  - Accounts module forked: ~200 files copied to `university_erp/university_finance/`; controllers stripped of stock/selling/buying dependencies; 57 unused doctype dirs and 18 unused reports archived (reversibly under `_archived/`).
  - 24 custom Employee + Leave Application fields migrated via explicit script (not fixtures) for idempotent rerun.
  - No new doctypes — all 275+ already exist.
  - `--success-text` / `--warning-text` / `--error-text` / `--info-text` CSS vars added for accessible text.
- **Open technical questions:**
  1. Verify management Frappe `Role` records (`Vice Chancellor`, `Registrar`, `Finance Officer`, `Dean`) exist before Phase 5 (currently flagged as concern in STATE.md).
  2. Confirm Frappe workflow engine REST API supports approval-queue UX needed for HOD portal (Phase 7 prereq).
  3. Phase 4 design system choice (Tailwind tokens vs custom; light/dark variants) to be locked in `/gsd:discuss-phase`.
  4. Duplicate business logic between Education's `Fees`/`Student Attendance`/`Assessment Result` and university_erp overrides — authoritative source documented in Phase 03.1-06; long-term consolidation deferred.

---

## 10. Dependencies & Assumptions

- **Dependencies:**
  - Frappe v15+, ERPNext v15+, HRMS v15+, Education v15+ — all pinned in apps.json; bench upgrade in lockstep.
  - MariaDB primary database; Redis for cache and queue (provisioned via Docker dev container).
  - Razorpay and PayU production keys + webhook URLs configured by operations team.
  - University DigiLocker/WhatsApp/Firebase/SMS credentials provisioned (existing).
  - Real Frappe `Role` records for Vice Chancellor, Registrar, Finance Officer, Dean (open — see §9).
  - `gsd-sdk` runtime for `.planning/` artifact tooling (developer tooling, not production runtime).
- **Assumptions:**
  - Single-university deployment; multi-campus is a deployment-time concern, not a feature.
  - University data is OLTP-scale (~10,000 students); no need for separate OLAP cube.
  - All 275+ doctypes are stable; v1 ships no new doctypes.
  - Frappe Desk is acceptable as admin-only UI; system administrators are trained on Desk.
  - Portal users (student/faculty/HOD/parent/management) never touch Desk.
  - Existing 54+ reports and 30+ cron jobs are correct sources of truth; analytics layer aggregates from them.
  - Dark mode and English are the only theming/localization scopes for v1.

---

## 11. Timeline & Milestones

| Phase | Deliverable | Owner | Start | **Deadline** | Status |
|-------|-------------|-------|-------|--------------|--------|
| Phase 1 — Foundation & Security Hardening | Cross-app data verification, parameterized SQL, permission guards, role-routed Vue shell, session auth | Backend Lead | 17-Mar-2026 | **18-Mar-2026** | ✅ |
| Phase 2 — Shared Component Library | KPI card, chart wrapper, DataTable, filter bar, exports, report viewer, notification panel | Frontend Lead | 18-Mar-2026 | **18-Mar-2026** | ✅ |
| Phase 3 — Faculty Portal | Today's classes, bulk attendance, grade grid, leave, LMS, research, OBE, workload | Frontend Lead | 18-Mar-2026 | **18-Mar-2026** | ✅ |
| Phase 03.1 — Comprehensive System Audit & Fix | 488 endpoints audited, 9-role permission matrix, 24 custom fields migrated, 14 reports fixed, SQL remediation, WCAG audit | Backend Lead | 19-Mar-2026 | **19-Mar-2026** | ✅ |
| Phase 03.3 — ERPNext Accounts Module Fork | Fork to `university_finance`, relabel, archive 57 unused doctypes + 18 reports, redirect imports, smoke tests | Backend Lead | 20-Mar-2026 | **24-Mar-2026** | ✅ |
| Phase 03.4 — Post-Fork Backend Audit & Fix | Demo data seed (Plan 1 ✅), missing workflows, doctype + report schema audit, permission re-verify | Backend Lead | 25-Mar-2026 | **15-May-2026** | 🟡 (Plan 1/5) |
| Phase 4 — Portal Redesign & Build | Design system, recreate 11 student views, redesign faculty, scaffold HOD/Parent/Management with dark mode | Frontend Lead | _TBD post-03.4_ | **TBD** | ☐ |
| Phase 5 — Management Dashboards | VC/Registrar/Finance/Dean dashboards, drill-down, department comparison, alert panel, report viewer | Frontend Lead | _After Phase 4_ | **TBD** | ☐ |
| Phase 6 — Parent Portal | Multi-child selector with guardian verification, academics, fees + online payment, hostel/transport, messaging | Frontend Lead | _After Phase 4_ | **TBD** | ☐ |
| Phase 7 — HOD Portal | Inherit faculty + department analytics, approval queue, CO-PO heatmap, budget | Frontend Lead | _After Phase 4_ | **TBD** | ☐ |
| Phase 8 — Scheduled Reports & Cross-Portal Polish | Export verification across all portals, scheduled email delivery (daily/weekly/monthly) with role scoping | Backend Lead | _After Phases 5/6/7_ | **TBD** | ☐ |
| QA — UAT cycle | End-to-end UAT with university stakeholders | QA Lead | _After Phase 8_ | **TBD** | ☐ |
| Pilot / Soft launch | Limited rollout to single department | PM | _Post-UAT_ | **TBD** | ☐ |
| GA Release | Full university rollout + comms | PM | _Post-Pilot_ | **TBD** | ☐ |

> Update the Status column with: ☐ Not started · 🟡 In progress · ✅ Done · 🔴 Blocked

**Progress to date:** 5/11 phases complete; 19/23 plans complete (~83%). See `.planning/STATE.md` for live state.

---

## 12. Risks & Mitigation

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|------|------------|--------|------------|-------|
| 1 | Accounts fork breaks downstream finance flows (200+ files modified) | Medium | High | Phase 03.4 backend audit; idempotent demo seed with FY backfill + GL re-post; webhook-level smoke tests | Backend Lead |
| 2 | Management role records (`Vice Chancellor`, `Registrar`, `Finance Officer`, `Dean`) don't exist in Frappe | Medium | Medium | Verify against live `Role` table before Phase 5 starts; create via fixtures if missing | Backend Lead |
| 3 | Frappe workflow engine integration for HOD approval queue API-incompatible with portal UX | Medium | Medium | API-level POC before Phase 7; fall back to direct doctype state machine if needed | Backend Lead |
| 4 | Portal redesign (Phase 4) regresses already-shipped faculty portal | Low | High | Phase 4 keeps API contract stable; faculty smoke tests gate the rebuild; feature flag for design rollout | Frontend Lead |
| 5 | Report schema drift after fork (orphan column references) | Medium | High | Phase 03.4-05 validates every report column/filter/join against live schema; CI guard | Backend Lead |
| 6 | Parent IDOR via child selector (parent X views child Y of parent Z) | Medium | Critical | Server-side guardian ownership check on every parent endpoint (PRNT-01); test fixture covers cross-parent attempts | Backend Lead |
| 7 | Bundle size bloat from charts + table + export libs | Low | Medium | ApexCharts + ExcelJS dynamic `import()`; Vite vendor splitting; bundle-size CI check | Frontend Lead |
| 8 | Frappe / ERPNext upstream upgrade breaks the fork | Medium | High | Pin upstream versions; document delta; scheduled re-base review per minor release | Backend Lead |
| 9 | Demo data drift between dev and production (PII/seeding errors) | Low | Medium | Idempotent seed script; production seed runs separately and tagged; STATE.md documents quick-task seed runs | Backend Lead |
| 10 | UAT feedback delays from university stakeholders | High | Medium | Weekly checkpoint with VC office; written sign-off gates per phase | PM |

---

## 13. Open Questions

- [ ] Confirm management `Role` records exist (VC, Registrar, Finance Officer, Dean) — owner: Backend Lead — due before Phase 5 kickoff.
- [ ] Validate Frappe workflow engine REST API supports HOD approval-queue UX — owner: Backend Lead — due before Phase 7 kickoff.
- [ ] Lock Phase 4 design system choice (Tailwind tokens vs custom; dark mode treatment) — owner: Frontend Lead — due in `/gsd:discuss-phase` for Phase 4.
- [ ] Decide long-term consolidation strategy for duplicate logic (Education vs university_erp `Fees`, `Student Attendance`, `Assessment Result`) — owner: Backend Lead — deferred, but track.
- [ ] Confirm parent authentication model for online payments (does Razorpay session need to be parent-bound, or can guardian-link be sufficient?) — owner: Backend Lead — due before Phase 6 PRNT-07.
- [ ] Define exact email-delivery failure escalation path for Phase 8 scheduled reports — owner: Backend Lead — due in Phase 8 plan.

---

## 14. Approval / Sign-off

| Role | Name | Decision | Date |
|------|------|----------|------|
| Product Owner | _TBD_ | ☐ Approved ☐ Changes Requested | |
| Engineering Lead | Vedant Zope | ☐ Approved ☐ Changes Requested | |
| Client / Sponsor (University) | _TBD_ | ☐ Approved ☐ Changes Requested | |

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 30-Apr-2026 | Vedant Zope | Initial draft synthesized from `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` |
