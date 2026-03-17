# Requirements: University ERP — Planning & Developer Sharing

**Defined:** 2026-03-17
**Core Value:** Complete project environment shared to another developer via GHCR with a clear roadmap for dashboard/analytics work they will build

## v1 Requirements

Requirements for this milestone. Dashboard development is deferred to the receiving developer — our scope is planning + sharing.

### Docker Sharing

- [ ] **DOCK-01**: Docker container architecture audited (service names, container names, volume bindings documented from `docker ps` / `docker inspect`)
- [ ] **DOCK-02**: Pre-commit cleanup performed (bench clear-cache, delete logs, pip cache purge, compiled .pyc cleanup)
- [ ] **DOCK-03**: Secrets scrubbed from site_config.json (replace real credentials with placeholder/sandbox values)
- [ ] **DOCK-04**: Bench container committed and tagged as Docker image
- [ ] **DOCK-05**: MariaDB container committed and tagged as Docker image (if separate container) or database backup embedded
- [ ] **DOCK-06**: Both images pushed to GitHub Container Registry (ghcr.io)
- [ ] **DOCK-07**: docker-compose.share.yml created pointing to GHCR images for the receiving developer
- [ ] **DOCK-08**: Developer onboarding guide written with pull + run instructions, credential setup, first-start checklist, and project structure overview

### Planning Artifacts for Handoff

- [ ] **PLAN-01**: PROJECT.md captures full project context, validated capabilities, and active requirements for the other developer
- [ ] **PLAN-02**: REQUIREMENTS.md defines all dashboard/analytics requirements with REQ-IDs organized by module tier
- [ ] **PLAN-03**: ROADMAP.md with phased plan for dashboard development (infrastructure → tier-1 → tier-2 → tier-3 → cross-module)
- [ ] **PLAN-04**: Research artifacts (.planning/research/) included with stack patterns, feature landscape, architecture guidance, and pitfalls
- [ ] **PLAN-05**: Codebase map (.planning/codebase/) included with architecture, structure, conventions, and concerns documentation
- [ ] **PLAN-06**: hooks.py pre-updated to export Dashboard, Dashboard Chart, and Number Card DocTypes as fixtures (so the other developer doesn't hit this pitfall)

### Dashboard Requirements (for other developer — documented in ROADMAP.md)

- [ ] **DASH-01**: Per-module dashboard specifications documented for all 21 modules with specific KPIs, chart types, and data sources
- [ ] **DASH-02**: Tier-1 module dashboards specified (Academics, Examinations, Finance, Payments) — highest priority
- [ ] **DASH-03**: Tier-2 module dashboards specified (Admissions, Student Info, Faculty, Hostel, Library, Transport)
- [ ] **DASH-04**: Tier-3 module dashboards specified (Placement, LMS, Research, OBE, Grievance, Feedback, Inventory, Integrations, Portals, Analytics, Core)
- [ ] **DASH-05**: Cross-module Executive Dashboard and at-risk student composite KPI specified
- [ ] **DASH-06**: Script Report patterns and fixture export workflow documented as developer guide

## v2 Requirements

### Enhanced Analytics (for other developer, future milestone)

- **ANLY-V2-01**: NAAC/NIRF readiness gauge with percentage of accreditation criteria met
- **ANLY-V2-02**: Faculty workload equity heatmap for semester planning
- **ANLY-V2-03**: Student-facing analytics in Vue SPA portal (personal KPIs, grade trends)

### Advanced Sharing

- **DOCK-V2-01**: Multi-architecture Docker images (amd64 + arm64) via buildx
- **DOCK-V2-02**: CI/CD pipeline for automated image builds and GHCR push

## Out of Scope

| Feature | Reason |
|---------|--------|
| Building dashboards ourselves | Dashboard development is handoff scope for the receiving developer |
| External BI tools (Metabase, Superset) | Scope explosion — introduces separate auth and maintenance burden |
| Predictive analytics / ML models | Requires data science infrastructure not in current stack |
| Vue SPA analytics | Scoped to Frappe Desk only per decision |
| Production deployment | This is a dev environment share, not production setup |
| CI/CD pipeline | Manual Docker push for this milestone |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DOCK-01 | Phase 1 | Pending |
| DOCK-02 | Phase 1 | Pending |
| DOCK-03 | Phase 1 | Pending |
| DOCK-04 | Phase 1 | Pending |
| DOCK-05 | Phase 1 | Pending |
| DOCK-06 | Phase 1 | Pending |
| DOCK-07 | Phase 1 | Pending |
| DOCK-08 | Phase 1 | Pending |
| PLAN-01 | Phase 2 | Pending |
| PLAN-02 | Phase 2 | Pending |
| PLAN-03 | Phase 2 | Pending |
| PLAN-04 | Phase 2 | Pending |
| PLAN-05 | Phase 2 | Pending |
| PLAN-06 | Phase 2 | Pending |
| DASH-01 | Phase 2 | Pending |
| DASH-02 | Phase 2 | Pending |
| DASH-03 | Phase 2 | Pending |
| DASH-04 | Phase 2 | Pending |
| DASH-05 | Phase 2 | Pending |
| DASH-06 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-17*
*Last updated: 2026-03-17 after scope clarification — dashboards are handoff work for receiving developer*
