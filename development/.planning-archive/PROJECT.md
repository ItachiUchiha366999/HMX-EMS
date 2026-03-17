# University ERP — Dashboards, Analytics & Developer Sharing

## What This Is

A comprehensive University ERP system built on Frappe/ERPNext with 21 functional modules covering academics, admissions, finance, payments, examinations, hostel, library, HR/faculty management, and more. The system includes a Vue 3 student portal SPA and runs inside a Frappe Docker devcontainer with MariaDB and Redis. The project has demo data populated and is functionally complete — this milestone focuses on adding dashboards/analytics across all modules and packaging the full environment for sharing with another developer.

## Core Value

Every module has actionable dashboards with KPI cards, trend charts, comparisons, and filterable reports — and the complete working environment (code, database, Docker state) can be shared to another developer who pulls from GHCR and starts working immediately.

## Requirements

### Validated

<!-- Inferred from existing codebase — these capabilities already exist and work. -->

- ✓ Student management with enrollment, CGPA tracking, status workflows — existing
- ✓ Admissions workflow with student applicant processing — existing
- ✓ Academic calendar, course management, class scheduling, timetables — existing
- ✓ Fee management with GL posting and payment gateway integration (Razorpay/PayU) — existing
- ✓ Examination management with online exams, auto-submission, result processing — existing
- ✓ Hostel allocation and room management — existing
- ✓ Library operations (issue/return, reservations, fines) — existing
- ✓ Faculty management (leave, salary, teaching assignments, feedback) — existing
- ✓ Student portal Vue SPA (dashboard, academics, finance, exams, library, hostel, transport, placement, grievances, profile) — existing
- ✓ Multiple portal pages (faculty, alumni, parent, placement, notice board) — existing
- ✓ Communication integrations (WhatsApp, SMS, email, Firebase push) — existing
- ✓ Scheduled tasks (fee reminders, CGPA updates, exam auto-submit, SLA checks) — existing
- ✓ Demo data seeded and functional — existing

### Active

<!-- Current scope — building toward these. -->

- [ ] Module-level overview dashboards with KPI cards and summary charts for all 21 modules
- [ ] Dedicated analytics pages with deep drill-down, filters, date ranges per module
- [ ] Centralized analytics module/workspace in Frappe Desk
- [ ] KPI cards (big numbers with trends — total students, revenue, pass rates, etc.)
- [ ] Time series charts (enrollment trends, monthly fee collections, attendance over time)
- [ ] Comparison charts (department-wise, program-wise breakdowns — bar/pie)
- [ ] Filterable data tables with export to Excel/PDF
- [ ] Docker commit of current running environment (code + DB + config)
- [ ] Push full snapshot image to GitHub Container Registry (ghcr.io)
- [ ] Developer onboarding documentation for pulling and running the shared image

### Out of Scope

- Vue SPA analytics — analytics live in Frappe Desk workspaces only, not in the Vue student portal
- Mobile app — web-first
- New feature development beyond dashboards — existing module functionality is frozen for this milestone
- CI/CD pipeline — manual Docker push for now
- Production deployment — this is a dev environment share

## Context

- Running inside Frappe Docker devcontainer (frappe_docker repo structure)
- Platform: Linux x86_64 on WSL2
- Database: MariaDB with existing demo data
- 21 modules in university_erp app, extending Education/ERPNext/HRMS/Frappe
- Frappe v15+ with native Dashboard, Report Builder, and Number Card DocTypes available
- All dashboards should use Frappe's built-in charting (frappe.Chart) and reporting infrastructure
- The other developer needs the exact running state — not just code, but database, site config, Redis state
- Codebase map available at `.planning/codebase/` for reference

## Constraints

- **Tech stack**: Must use Frappe's native Dashboard/Report/Number Card DocTypes — no external charting libraries for admin dashboards
- **Environment**: Running in Docker devcontainer — sharing must preserve the container state including database
- **Registry**: Docker image pushed to GitHub Container Registry (ghcr.io)
- **Scope**: Plan first, build later — create complete roadmap before execution

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Frappe Desk for analytics (not Vue SPA) | Native Dashboard/Report DocTypes reduce dev effort, consistent with ERP admin UX | — Pending |
| Docker commit + GHCR push for sharing | Preserves exact running state (DB + code + config), simplest for the other developer | — Pending |
| All 21 modules get dashboards | Complete coverage, no partial handoff | — Pending |
| All chart types (KPI, time series, comparison, tables) | Comprehensive analytics coverage per module | — Pending |

---
*Last updated: 2026-03-17 after initialization*
