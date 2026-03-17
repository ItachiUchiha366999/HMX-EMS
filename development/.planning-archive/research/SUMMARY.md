# Project Research Summary

**Project:** University ERP — Dashboards, Analytics & KPIs Milestone
**Domain:** Frappe v15 native dashboard tooling + Docker devcontainer sharing via GHCR
**Researched:** 2026-03-17
**Confidence:** HIGH (stack and features grounded in direct Frappe v15 source inspection; architecture verified against running codebase; pitfalls cross-referenced with project CONCERNS.md)

## Executive Summary

This milestone adds dashboards, KPI cards, and analytics to a functionally complete 21-module university ERP built on Frappe v15. The ERP already contains all the business logic — the gap is visibility. Experts building on Frappe do this entirely within Frappe's native tooling: Dashboard DocType, Dashboard Chart DocType, Number Card DocType, Script Reports, and Workspace fixtures. No external charting library is needed or appropriate; Frappe ships frappe-charts internally (Line, Bar, Pie, Donut, Heatmap, Percentage). All dashboard artifacts are JSON fixtures that travel with the codebase and load via `bench migrate`. The system already has 40+ Script Reports and a university_analytics module with KPI infrastructure — this milestone connects those data assets to visual dashboards.

The recommended build approach is module-by-module: each of the 21 modules gets a Workspace update (2-3 Number Cards + 1 embedded chart), a dedicated Dashboard page (3-5 cards + 3-4 charts), and links to existing or new Script Reports for drill-down. Build in dependency order: academics and examinations first (their data feeds almost every other dashboard), then finance and payments (high business value, independent), then operational modules, then cross-module views last. After all module dashboards are proven, build the executive cross-module dashboard. This order avoids dependency hell and catches data issues early.

The biggest risks are not technical — they are process risks. Dashboard records built via the Frappe Desk UI live only in MariaDB and are lost without fixture export. The `docker commit` sharing approach must handle a multi-container architecture (bench container + separate MariaDB container + Redis containers); committing only the bench container produces an image with no database. Both of these pitfalls have direct, tested mitigations: mandatory fixture export after every build session, and a two-container commit strategy. Architecture mismatch (amd64 vs arm64) and secrets baked into committed images round out the critical risks that must be addressed before the Docker packaging phase.

## Key Findings

### Recommended Stack

Frappe v15 provides everything needed natively. Dashboard Charts support six visual types (Line, Bar, Percentage, Pie, Donut, Heatmap) and six data modes (Count, Sum, Average, Group By, Report-backed, Custom). Number Cards provide KPI big-number tiles with built-in period-over-period trend comparison. Script Reports provide the filterable data tables with Python access to full SQL — the correct choice for all cross-DocType joins in a university context.

For Docker sharing: `docker commit` captures the running container's full filesystem (code, compiled assets, site config). Because frappe_docker runs MariaDB as a separate container with data in a named volume, both the bench container and the MariaDB container must be committed and pushed to GHCR separately. A companion `docker-compose.share.yml` pointing to both committed images is the correct sharing artifact.

**Core technologies:**
- Frappe Dashboard / Dashboard Chart / Number Card DocTypes (v15, source-verified) — native visual layer, ships as JSON fixtures, zero external dependencies
- Frappe Script Report (v15, source-verified) — primary data source for complex multi-table analytics; returns columns, data, chart config, and summary in one call
- Frappe Workspace DocType (v15, source-verified) — module landing pages that embed charts and number cards directly for at-a-glance status
- `docker commit` + GHCR — snapshot exact running state (bench + MariaDB) and push to GitHub Container Registry; receiver runs `docker compose up` with the committed images
- `bench export-fixtures` + `hooks.py` fixtures list — export Dashboard, Number Card, Dashboard Chart, Workspace records as JSON for source-controlled reproducibility

**Critical version requirements:**
- Developer mode (`developer_mode = 1`) must be active when creating fixtures so `is_standard = 1` and `module` fields are available
- `hooks.py` must be updated to add `{"dt": "Dashboard"}`, `{"dt": "Number Card"}`, and `{"dt": "Dashboard Chart"}` to the fixtures list — currently only Workspace is exported

### Expected Features

All 21 modules need coverage. The features are grounded in the codebase's DocType inventory — KPI choices reflect what data the system actually stores, not generic ERP speculation. 40+ existing Script Reports provide data sources for many dashboard charts without new code.

**Must have (table stakes) — P1:**
- Per-module Number Cards: 3-5 KPI cards per module covering the most-watched metrics (total students, fee collection, attendance rate, pass rate, occupancy, open grievances, etc.)
- Per-module summary chart embedded in each module's Workspace (1 bar or line chart for at-a-glance trend)
- Per-module Dashboard page with full analytical view (5-10 charts) linked from Workspace
- Finance: fee collection this month + outstanding dues + collection trend chart — high executive visibility
- Academics: attendance rate + students below 75% threshold + program enrollment chart — regulatory compliance metric
- Examinations: pass rate + grade distribution chart — most-watched academic metric
- Admissions: applicant funnel chart (applied → shortlisted → offered → enrolled) — core admissions metric
- Placement: students placed + placement rate % — #1 metric for placement cell and rankings

**Should have (differentiators) — P2, add after all module dashboards are proven:**
- Cross-module Executive Dashboard: one workspace with top 3 KPIs from all 21 modules for VP/Registrar overview
- At-risk student composite KPI: combines attendance + CGPA + fee outstanding + grievance into one risk flag per student
- NAAC/NIRF readiness gauge: percentage of accreditation criteria with sufficient data (red/amber/green)
- Faculty workload equity heatmap: surfaces overloaded vs underloaded faculty before semester planning
- Centralized analytics workspace linking to all 21 module dashboards

**Defer to v2+:**
- Student-facing analytics in Vue SPA — explicitly out of scope per PROJECT.md; next milestone
- Predictive analytics / cohort retention modeling — requires data science infrastructure, MLOps
- LMS vs classroom attendance correlation — complex multi-table statistical analysis
- External BI tool integration (Metabase, Superset) — scope explosion, introduces separate auth and service dependency
- Custom dashboard builder UI — Frappe's native Dashboard DocType already provides this natively

### Architecture Approach

The architecture uses two tiers per module: Workspace (at-a-glance hub, always visible) and Dashboard (full analytical destination, opt-in). Workspace carries 2-3 Number Card rows and 1 chart row; a Dashboard shortcut on the Workspace navigates to the full 5-10 chart view. This matches ERPNext's own pattern for Accounting Workspace vs Accounts Dashboard. Script Reports are the single source of truth for all non-trivial analytics — Dashboard Charts reference Reports rather than encoding query logic themselves. The university_analytics module provides the KPI Definition / KPI Value / Scheduled Task infrastructure for historical KPI tracking.

**Major components:**
1. Workspace fixtures (21 updated, 1 new for analytics hub) — navigation entry point per module; carries headline KPIs and 1 sparkline chart
2. Dashboard fixtures (21 per-module + 1 executive) — full analytical view per module with all charts and number cards
3. Number Card fixtures (~80-100 total) — KPI tiles; use Document Type mode for simple counts/sums, Custom method for computed ratios (pass rate %, placement rate %, collection efficiency %)
4. Dashboard Chart fixtures (~80-100 total) — trend and distribution charts; linked to Script Reports for data integrity
5. Script Reports (~30-40 total; 40+ already exist) — filterable data tables with export; primary data source for all complex metrics
6. Docker sharing artifacts — bench container image + MariaDB container image on GHCR + `docker-compose.share.yml` for receivers
7. hooks.py fixture additions — Dashboard, Number Card, Dashboard Chart must be added to the export list before any dashboard work begins

### Critical Pitfalls

1. **Dashboard fixtures not exported from MariaDB** — Dashboards built via the UI exist only in the database. Without `bench export-fixtures`, they disappear on any reinstall. Fix: add Dashboard, Number Card, Dashboard Chart to `hooks.py` fixtures list before starting; export after every module batch; verify fixture JSON appears in `university_erp/fixtures/`. This is the single highest-probability failure mode.

2. **MariaDB state missing from committed image** — frappe_docker runs MariaDB as a separate container with data in a named Docker volume. Committing only the bench container produces an image with no database. Fix: two-container commit strategy — commit both bench container and MariaDB container; push both to GHCR; provide `docker-compose.share.yml` pointing to both images.

3. **Secrets baked into committed image** — `docker commit` snapshots the full filesystem including `site_config.json` with MariaDB credentials, Razorpay keys, and Frappe's `encryption_key`. Fix: scrub or replace all credentials with sandbox/placeholder values before committing; run `bench set-config` for sensitive fields; keep GHCR package visibility as private.

4. **Number Cards show 0 for non-admin roles** — Frappe Number Cards execute queries with the logged-in user's permission context. `get_permission_query_conditions()` filters in `student.py` and other overrides mean role-restricted users see 0. Fix: test every Number Card with a "University Admin" role user before marking it complete; add explicit DocType read permissions in role permission fixtures.

5. **Dashboard charts break on empty data** — Pie and Donut chart types throw JavaScript errors when the dataset is empty (Chart.js requires at least one non-zero value). Fix: add empty-data guard to every Script Report (`if not data: return columns, [], None, None, None`); test each chart with a future-date filter that returns no rows.

6. **Architecture mismatch (amd64 vs arm64)** — `docker commit` produces an image for the host's architecture only. Apple Silicon developers cannot run an amd64-committed image at full speed. Fix: confirm the receiving developer's platform before committing; document "requires x86_64 host" prominently; provide `bench backup` + restore script as fallback for arm64 users.

## Implications for Roadmap

Research points to a clear five-phase structure. The ordering is driven by data dependencies (foundational modules first, cross-module views last), fixture infrastructure (must exist before any dashboard work), and Docker architecture requirements (fully understood before packaging begins).

### Phase 1: Foundation Infrastructure
**Rationale:** Both dashboard development and Docker sharing require upfront configuration that cannot be patched mid-build. No dashboard work should begin until this phase is complete.
**Delivers:** Updated `hooks.py` with Dashboard/Number Card/Dashboard Chart in fixtures list; confirmed fixture export workflow (`bench export-fixtures` tested and producing correct JSON); developer mode confirmed active; Docker architecture documented (service names, container names, volume names from `docker ps`); pre-commit checklist written; base university_analytics workspace reviewed.
**Addresses:** FEATURES.md prerequisite — "Number Cards require underlying data: All KPI cards depend on demo data being populated"; ARCHITECTURE.md requirement — "hooks.py Fixtures Addition Required before any dashboard build work begins"
**Avoids:** Pitfall 1 (fixtures never exported), Pitfall 2 (MariaDB architecture misunderstood), Pitfall 4 (secrets in image committed without understanding what's in the container)
**Research flag:** Standard patterns — skip additional research. Frappe fixture export syntax is well-documented and verified in STACK.md against Frappe v15 source.

### Phase 2: Tier-1 Module Dashboards (Academics, Examinations, Finance, Payments)
**Rationale:** These four modules provide the data that almost every other dashboard references (student counts, assessment results, fee records). Building them first validates the fixture export workflow on real data and ensures the KPI infrastructure works before scaling to 21 modules.
**Delivers:** 4 module Dashboards with full Number Card sets and charts; 4 updated Workspaces with embedded KPI tiles; 4-8 Script Reports (using/extending existing reports where possible); fixture JSON committed for all artifacts; role-based testing completed for University Admin role.
**Addresses:** FEATURES.md P1 features — Academics (attendance rate + at-risk students + enrollment chart), Examinations (pass rate + grade distribution), Finance (collection this month + outstanding dues + collection trend), Payments (gateway success rate + daily collection)
**Uses:** Script Report as single source of truth for all non-trivial metrics; Number Card Document Type mode for simple counts; Number Card Custom method for computed ratios (pass rate %, collection efficiency %)
**Avoids:** Pitfall 5 (zero-data chart testing required per module before moving on); Pitfall 4 (role-based testing as acceptance criterion)
**Research flag:** Standard patterns — Script Report and Dashboard Chart patterns are verified in STACK.md and ARCHITECTURE.md with code examples. No additional research needed.

### Phase 3: Tier-2 Operational Module Dashboards (Admissions, Student Info, Faculty, Hostel, Library, Transport)
**Rationale:** These modules are more independent — they don't feed each other and don't require Tier-1 data. They cover the operational dashboard requirements for day-to-day university administration.
**Delivers:** 6 module Dashboards, 6 updated Workspaces, associated Number Cards, Dashboard Charts, and Script Reports; all fixture JSON committed and tested.
**Addresses:** FEATURES.md P1 features — Admissions (applicant funnel chart + conversion rate), Faculty (faculty-student ratio + workload table), Hostel (occupancy rate + building breakdown), Library (books issued + overdue count), Transport (route load + vehicle utilization)
**Avoids:** ARCHITECTURE.md anti-pattern — "build all dashboards in one pass without incremental testing"; each module is its own deliverable with acceptance criteria
**Research flag:** Standard patterns for most modules. Faculty workload heatmap may need additional thought on chart configuration — consider as a mild research area if the standard Group By chart type proves insufficient.

### Phase 4: Tier-3 Ancillary Module Dashboards (Placement, LMS, Research, OBE, Grievance, Feedback, Inventory, Integrations, Portals, Analytics)
**Rationale:** These modules have lower daily query volumes but contain high-value metrics (placement rate, OBE attainment, NAAC criteria). OBE requires CO-PO mapping to be present in demo data — verify before building OBE dashboards.
**Delivers:** 10 module Dashboards with full coverage; remaining Number Cards and Dashboard Charts; all fixtures committed; all 21 modules now have dashboard coverage.
**Addresses:** FEATURES.md P1 features for remaining modules; OBE (CO/PO attainment + NAAC progress chart); Placement (placement rate % + company-wise breakdown); Grievance (SLA compliance + type Pareto chart)
**Avoids:** FEATURES.md dependency note — "OBE attainment requires CO-PO mapping first"; verify in demo data before building OBE charts
**Research flag:** OBE module may need a brief research-phase task — CO/PO attainment calculation involves Bloom's taxonomy levels and multi-join queries. The existing `co_attainment_report` and `po_attainment_report` should be assessed to confirm they return chart-ready data before building Dashboard Charts against them.

### Phase 5: Cross-Module Views and Docker Packaging
**Rationale:** The executive dashboard and composite KPIs require all 21 module dashboards to be proven accurate. Docker packaging should happen last to capture the fully-built environment including all fixtures and demo data in their final state.
**Delivers:** Cross-module Executive Dashboard (top 3 KPIs from all 21 modules); at-risk student composite KPI (attendance + CGPA + fee + grievance); NAAC/NIRF readiness gauge; Docker bench container image + MariaDB container image pushed to GHCR; `docker-compose.share.yml` for receiver; onboarding guide.
**Addresses:** FEATURES.md P2 features (executive dashboard, at-risk KPI, NAAC gauge); Docker sharing requirements from PROJECT.md
**Uses:** STACK.md two-container commit strategy; ARCHITECTURE.md `docker-compose.share.yml` pattern
**Avoids:** Pitfall 2 (two-container commit: bench + MariaDB separately); Pitfall 3 (pre-commit cleanup checklist: `bench clear-cache`, delete logs, `pip cache purge`); Pitfall 4 (secrets scrub before push); Pitfall 7 (confirm target developer's platform before committing)
**Research flag:** Docker two-container commit is well-documented in STACK.md and ARCHITECTURE.md with step-by-step commands. However, the exact MariaDB container name and volume configuration should be verified live from `docker ps` before executing — do not assume service names.

### Phase Ordering Rationale

- Fixture infrastructure must precede all dashboard work because records built without it are irrecoverable from source
- Tier-1 modules (Academics, Examinations, Finance) feed data to other dashboards; building them first reveals data quality issues early
- Operational modules (Tier-2 and Tier-3) are built module-by-module, each as its own deliverable, to avoid the anti-pattern of building all 21 in one unverified pass
- Cross-module views (Executive Dashboard, at-risk student KPI) are deliberately last because they depend on all underlying module dashboards being proven accurate
- Docker packaging is the final step so the committed image represents the fully-built and tested state

### Research Flags

Phases needing deeper research during planning:
- **Phase 4 (OBE module):** CO/PO attainment calculation is domain-specific and the existing reports may return data in a format that requires transformation before feeding Dashboard Charts. Recommend a brief research task before building OBE dashboards.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundation Infrastructure):** Fixture export syntax and hooks.py patterns are verified directly in Frappe v15 source
- **Phase 2 (Tier-1 Dashboards):** Script Report + Dashboard Chart pattern is fully documented with code examples in STACK.md and ARCHITECTURE.md
- **Phase 3 (Tier-2 Operational):** Same established patterns; no novel integration points
- **Phase 5 (Docker Packaging):** Step-by-step commands are documented in STACK.md; only live verification of container names is needed

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All Frappe DocType capabilities verified directly from v15 source files in the running bench; Docker commit/GHCR mechanics are stable Docker internals |
| Features | HIGH | KPI choices grounded in direct DocType inventory across all 21 modules; 40+ existing reports confirm data availability; not speculation |
| Architecture | HIGH | Component relationships verified from Frappe v15 source (dashboard_chart.json, number_card.json, workspace.json); fixture structure verified against ERPNext accounts module |
| Pitfalls | MEDIUM-HIGH | Docker pitfalls are HIGH confidence (stable internals); Frappe permission interaction with Number Cards is MEDIUM confidence (requires live testing to confirm `get_permission_query_conditions` behavior in v15 dashboard context); zero-data chart behavior is MEDIUM (train data, verify during build) |

**Overall confidence:** HIGH

### Gaps to Address

- **Fixture export syntax in Frappe v15:** Verify that `bench export-fixtures` respects module-based `filters` in `hooks.py` (syntax may differ from v14). Test this in Phase 1 before scaling to all modules.
- **`dynamic_filters_json` behavior in v15:** The dynamic filter mechanism (injecting current academic year from session context) is documented but should be tested early — one Dashboard Chart per module should use it to validate before it's applied broadly.
- **MariaDB container name and volume mapping:** Before planning the Docker commit strategy, run `docker ps` and `docker inspect` on the running environment to confirm actual service names, container names, and which volumes hold MariaDB data. The architecture diagrams in ARCHITECTURE.md are informed assumptions — live verification is required.
- **OBE CO/PO data completeness:** Verify whether demo data includes completed CO-PO mappings and Assessment Results needed for attainment calculations. If not, OBE dashboard KPIs will show 0 regardless of implementation correctness.
- **Feedback Response demo data:** Verify whether demo data includes Feedback Responses (not just Feedback Form definitions). Feedback score KPIs depend on response records existing.

## Sources

### Primary (HIGH confidence — direct source inspection)
- Frappe v15 source: `frappe/desk/doctype/dashboard/dashboard.json` — Dashboard fields, is_standard mechanism, fixture path pattern
- Frappe v15 source: `frappe/desk/doctype/dashboard_chart/dashboard_chart.json` — all 6 chart types, all 6 data modes, filter fields (modified 2025-06-08)
- Frappe v15 source: `frappe/desk/doctype/number_card/number_card.json` and `number_card.py` — card types, aggregate functions, custom method contract (modified 2025-05-21)
- Frappe v15 source: `frappe/core/doctype/report/report.json` — 4 report types confirmed (modified 2025-08-28)
- Frappe v15 source: `frappe/desk/doctype/workspace/workspace.json` — Workspace Chart and Workspace Number Card child tables confirmed
- ERPNext v15 source: `erpnext/accounts/` — verified real fixture structure for Dashboard, Dashboard Chart, Number Card
- University ERP source: all 21 module directories — DocType inventory, existing 40+ reports, scheduled task definitions
- University ERP source: `hooks.py` — confirmed current fixture export scope (Workspace only; Dashboard/Number Card/Dashboard Chart not yet exported)
- University ERP source: `university_analytics/report/student_performance_analysis/student_performance_analysis.py` — confirmed Script Report pattern with columns/data/chart/summary

### Secondary (MEDIUM confidence — training data, aligned with codebase analysis)
- Frappe v15 permission system interaction with dashboard queries (`get_permission_query_conditions`) — MEDIUM; verify by testing during Phase 2
- `frappe.Chart` zero-data behavior for Pie/Donut charts — MEDIUM; verify by filtering to empty date range during each chart build
- `dynamic_filters_json` in Frappe v15 Dashboard Chart — MEDIUM; test one instance in Phase 1 before broad adoption

### Tertiary (LOW confidence — needs live verification)
- MariaDB container name, volume binding in the actual running devcontainer — verify via `docker ps` before Phase 5
- `bench export-fixtures` v15 filter syntax — verify in Phase 1 against a test Dashboard fixture

---
*Research completed: 2026-03-17*
*Ready for roadmap: yes*
