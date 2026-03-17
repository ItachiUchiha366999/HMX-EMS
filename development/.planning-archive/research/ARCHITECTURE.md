# Architecture Research

**Domain:** Frappe v15 University ERP — Dashboards/Analytics + Docker devcontainer sharing via GHCR
**Researched:** 2026-03-17
**Confidence:** HIGH — findings are from direct codebase inspection of the Frappe v15 source (dashboard_chart.json, number_card.json, workspace.json, hooks.py, existing university_analytics module) plus verified Docker architecture principles.

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Frappe Desk (Browser)                            │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐    │
│  │  Workspace   │  │  Dashboard   │  │  Query/Script Report     │    │
│  │  (nav hub)   │  │  (chart+card │  │  (data source, filterable│    │
│  │              │  │   container) │  │   table + chart + summary│    │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘   │
│         │ links/shortcuts  │ embeds                 │ linked from     │
├─────────┼──────────────────┼────────────────────────┼─────────────────┤
│         │                  │ Frappe Dashboard Layer  │                 │
│         │       ┌──────────┼───────┐                │                 │
│         │       │          │       │                │                 │
│         │  ┌────▼──────┐  ┌▼──────▼───┐            │                 │
│         │  │ Number    │  │ Dashboard │            │                 │
│         │  │ Card      │  │ Chart     │            │                 │
│         │  │ DocType   │  │ DocType   │            │                 │
│         │  └────┬──────┘  └────┬──────┘            │                 │
│         │       │              │                    │                 │
├─────────┼───────┼──────────────┼────────────────────┼─────────────────┤
│         │       │   Data Layer │                    │                 │
│         │       │              │                    │                 │
│  ┌──────▼──┐  ┌─▼───────┐  ┌──▼────────┐  ┌────────▼──────────────┐  │
│  │Workspace│  │DocType  │  │Dashboard  │  │  Script/Query Report   │  │
│  │ Links   │  │(Count/  │  │Chart      │  │  (Python execute()     │  │
│  │(DocType │  │Sum/Avg/ │  │Source     │  │   with columns, data,  │  │
│  │ Report) │  │Max/Min) │  │(Custom JS)│  │   chart, summary)      │  │
│  └─────────┘  └────┬────┘  └───────────┘  └────────────────────────┘  │
│                    │                                                    │
├────────────────────┼─────────────────────────────────────────────────  │
│                    │  MariaDB                                            │
│  ┌─────────────────▼───────────────────────────────────────────────┐   │
│  │  tabStudent · tabFees · tabCourse Enrollment · tabAssessment     │   │
│  │  Result · tabLeave Application · tabBook Issue · tabExam · …    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Where Configured |
|-----------|----------------|-----------------|
| Workspace | Navigation hub; contains shortcuts, links, embedded charts (Workspace Chart rows), and number cards (Workspace Number Card rows) | `{module}/workspace/{module}/{module}.json` — fixture file |
| Dashboard | Groups Dashboard Charts and Number Cards into a named, shareable page accessible via `/app/dashboard/{name}` | Frappe DB → exported as fixture JSON under `fixtures/` |
| Dashboard Chart | Single chart backed by a DocType aggregate (Count/Sum/Avg/Group By), a Report, or a Custom JS source; renders via `frappe.Chart` | Frappe DB → exported as fixture JSON |
| Number Card | Single big-number KPI: counts/sums/averages a DocType, or calls a Report, or calls a Custom whitelisted method | Frappe DB → exported as fixture JSON |
| Dashboard Chart Source | Custom chart whose data comes from a `.js` file in the module's `dashboard_chart_source/` directory | `{module}/dashboard_chart_source/{name}/{name}.js` |
| Script Report | Named Python report (`execute()` returns columns, data, optional chart, optional summary); the primary deep-analytics page | `{module}/report/{report_name}/{report_name}.py` + `.json` |
| Query Report | SQL-based report built in Report Builder UI; simpler than Script Report | Frappe DB → exported as fixture JSON |
| KPI Definition (custom) | University-specific DocType in `university_analytics`; stores KPI metadata, thresholds, calculation method | `university_analytics/doctype/kpi_definition/` |
| KPI Value (custom) | Stores historical computed KPI values; populated by scheduled tasks | `university_analytics/doctype/kpi_value/` |

---

## Frappe Dashboard Component Relationships

The relationship between DocTypes is critically important for structuring build work.

```
Workspace (1)
    ├── number_cards → [Workspace Number Card rows] → Number Card (many)
    ├── charts       → [Workspace Chart rows]        → Dashboard Chart (many)
    └── links        → [Workspace Link rows]         → Dashboard / Report / DocType

Dashboard (1)
    ├── cards  → [Number Card Link rows]      → Number Card (many)
    └── charts → [Dashboard Chart Link rows]  → Dashboard Chart (many)

Dashboard Chart (1)
    ├── chart_type = "Count/Sum/Average/Group By"
    │       └── document_type → DocType (1)   [direct DB aggregate — no report needed]
    ├── chart_type = "Report"
    │       └── report_name → Report (1)      [Script or Query Report drives chart data]
    └── chart_type = "Custom"
            └── source → Dashboard Chart Source (1)
                         └── reads {module}/dashboard_chart_source/{name}/{name}.js

Number Card (1)
    ├── type = "Document Type"
    │       └── document_type → DocType (1)   [direct aggregate: Count/Sum/Avg/Min/Max]
    ├── type = "Report"
    │       └── report_name → Report (1)      [report field + function applied to result]
    └── type = "Custom"
            └── method → whitelisted Python function path

Script Report (1)
    └── execute(filters) returns:
            columns  — list of column definitions
            data     — list of row dicts
            None     — (message field, unused)
            chart    — optional {data, type} for Dashboard Chart to embed
            summary  — optional [{label, value, datatype, indicator}]
```

### Key Insight: Two Access Patterns

**Pattern A — Workspace as entry point (module overview):**
A user opens a module Workspace (e.g., "University Finance"). The workspace has embedded Workspace Chart and Workspace Number Card rows that surface directly on the workspace page. This is a lightweight, always-visible summary — ideal for 2-3 KPI cards and 1-2 trend charts per module.

**Pattern B — Standalone Dashboard page (deep analytics):**
A Dashboard DocType groups multiple charts and number cards into a dedicated page, reached via the Dashboard list or a shortcut on the Workspace. This is the right place for 6-10 charts per module with date-range filters and drill-down.

For 21 modules with comprehensive analytics, the recommended structure uses both patterns: Workspace carries 2-3 headline KPIs and 1 sparkline chart; a linked Dashboard per module carries the full analytical view.

---

## Recommended Project Structure for Dashboard Artifacts

### Where Dashboard Configs Live

```
frappe-bench/apps/university_erp/university_erp/
│
├── {module_name}/                          # e.g., university_finance
│   ├── workspace/
│   │   └── {module_name}/
│   │       └── {module_name}.json          # Workspace fixture (already exists for 16 modules)
│   │           └── ← Add: number_cards[], charts[] rows here for workspace-level KPIs
│   │
│   ├── report/
│   │   └── {report_name}/
│   │       ├── {report_name}.json          # Report DocType config (is_standard, module, etc.)
│   │       ├── {report_name}.py            # execute() → columns, data, chart, summary
│   │       └── {report_name}.js            # Optional: client-side filters definition
│   │
│   └── dashboard_chart_source/             # Only for "Custom" chart type (advanced)
│       └── {source_name}/
│           └── {source_name}.js
│
├── university_analytics/                   # Existing centralized analytics module
│   ├── workspace/
│   │   └── university_analytics/
│   │       └── university_analytics.json   # Cross-module executive workspace
│   ├── report/
│   │   └── {cross_module_report}/          # Reports spanning multiple modules
│   └── doctype/
│       ├── kpi_definition/                 # KPI metadata (already exists)
│       └── kpi_value/                      # Historical KPI storage (already exists)
│
└── fixtures/                               # CRITICAL: all dashboard fixtures must land here
    ├── Dashboard.json                      # All Dashboard DocType records
    ├── Number Card.json                    # All Number Card DocType records
    └── Dashboard Chart.json                # All Dashboard Chart DocType records
```

### What Goes In Each Location

| Artifact | Location | Commitment Method |
|----------|----------|------------------|
| Module workspace KPI tiles (2-3 per module) | Workspace JSON `number_cards[]` field | Already in fixtures via `hooks.py` Workspace filter |
| Module workspace sparkline chart (1 per module) | Workspace JSON `charts[]` field | Already in fixtures via `hooks.py` Workspace filter |
| Module deep-analytics Dashboard | `fixtures/Dashboard.json` | Add `{"dt": "Dashboard"}` to `hooks.py` fixtures list |
| Module Number Cards (full set) | `fixtures/Number Card.json` | Add `{"dt": "Number Card"}` to `hooks.py` fixtures list |
| Module Dashboard Charts | `fixtures/Dashboard Chart.json` | Add `{"dt": "Dashboard Chart"}` to `hooks.py` fixtures list |
| Module Script Reports (filterable tables) | `{module}/report/{name}/` | Committed as source files — auto-discovered by Frappe |
| Cross-module executive dashboard | `university_analytics` workspace + Dashboard fixture | Same fixture mechanism |

### hooks.py Fixtures Addition Required

The current `hooks.py` exports Workspaces but does NOT export Dashboard, Number Card, or Dashboard Chart DocTypes. This must be added before any dashboard build work begins:

```python
fixtures = [
    # ... existing entries ...
    {"dt": "Dashboard", "filters": [["module", "in", [
        "University Academics", "University Admissions", "University Finance",
        "University Payments", "University Examinations", "University Hostel",
        "University Library", "Faculty Management", "University Analytics",
        # ... all 21 module names
    ]]]},
    {"dt": "Dashboard Chart", "filters": [["module", "in", [
        # same module list
    ]]]},
    {"dt": "Number Card", "filters": [["module", "in", [
        # same module list
    ]]]},
]
```

---

## Data Flow: DocType to Dashboard

### Flow 1 — Direct DocType Aggregate (simplest, for Number Cards and simple charts)

```
Administrator opens Frappe Desk
    → Creates Number Card: type="Document Type", document_type="Student", function="Count"
    → Frappe builds: SELECT COUNT(*) FROM tabStudent WHERE {permission_filters}
    → Number Card renders: "1,247 Students"
    → Filter applied automatically via get_permission_query_conditions() from overrides/student.py
```

**Use for:** Total students, total fee documents, open library issues, active hostel allocations — any simple aggregate with no complex joins.

### Flow 2 — Script Report → Dashboard Chart (recommended for trend charts)

```
Developer writes Script Report (Python):
    university_finance/report/fee_collection_trend/fee_collection_trend.py
        execute(filters) {
            columns = [month, amount]
            data = frappe.db.sql("SELECT MONTH(posting_date), SUM(grand_total)
                                  FROM tabFees
                                  WHERE docstatus=1
                                  GROUP BY MONTH(posting_date)")
            chart = {"data": {"labels": months, "datasets": [{"values": amounts}]},
                     "type": "bar"}
            summary = [{"value": total, "label": "Total Collected", "datatype": "Currency"}]
            return columns, data, None, chart, summary
        }

Administrator creates Dashboard Chart:
    chart_type = "Report"
    report_name = "Fee Collection Trend"
    type = "Bar"  (visual type)
    x_field = "month"
    y_axis = [{"y_field": "amount"}]

Dashboard Chart is added to:
    → "University Finance Dashboard" (Dashboard DocType)
    → And/or University Finance Workspace (Workspace Chart row)

User views dashboard:
    → Frappe calls /api/method/frappe.desk.doctype.dashboard_chart.dashboard_chart.get
    → Backend runs the Script Report execute() with current user's session
    → Chart data returned as JSON
    → frappe.Chart renders in browser
```

**Use for:** Monthly fee collection trends, enrollment trends over time, exam pass rate by semester, attendance trends.

### Flow 3 — Group By Chart (no report needed, built from UI)

```
Administrator creates Dashboard Chart:
    chart_type = "Group By"
    document_type = "Student"
    group_by_based_on = "program"
    group_by_type = "Count"
    number_of_groups = 10
    type = "Bar"

Frappe executes:
    SELECT program, COUNT(*) FROM tabStudent
    GROUP BY program ORDER BY COUNT(*) DESC LIMIT 10

Chart renders: "Students per Program" bar chart
```

**Use for:** Students per department/program, exam results by category, fee collection by category — any distribution without custom logic.

### Flow 4 — Custom Number Card Method (for computed KPIs)

```
Developer writes whitelisted method:
    university_analytics/api.py
        @frappe.whitelist()
        def get_pass_percentage():
            passed = frappe.db.count("Assessment Result", {"grade": [">=", "C"]})
            total  = frappe.db.count("Assessment Result")
            return {"value": round(passed/total*100, 1), "fieldtype": "Percent",
                    "route": ["query-report", "Student Performance Analysis"]}

Administrator creates Number Card:
    type = "Custom"
    method = "university_analytics.api.get_pass_percentage"
    show_percentage_stats = 1
    stats_time_interval = "Monthly"
```

**Use for:** Pass rate %, CGPA averages, fee collection efficiency %, placement rate — metrics requiring cross-table logic.

### Flow 5 — KPI Definition → Scheduled Task → KPI Value → Dashboard

```
KPI Definition record created (e.g., "Overall Pass Rate"):
    calculation_method = "Python Method"
    python_method = "university_erp.university_analytics.kpi_calculator.calculate_pass_rate"
    tracking_frequency = "Monthly"
    target_value = 85.0, red_threshold = 70.0

Scheduled task runs daily:
    university_erp.university_erp.analytics.scheduled_tasks.calculate_daily_kpis()
        → Reads KPI Definition records with tracking_frequency matching today
        → Calls each python_method
        → Inserts row into KPI Value (kpi_definition, value, date, academic_year)

Number Card "Custom" reads latest KPI Value:
    @frappe.whitelist()
    def get_kpi_value(kpi_name):
        return frappe.db.get_value("KPI Value", {"kpi_definition": kpi_name},
                                   "value", order_by="date DESC")
```

**Use for:** Long-term trend KPIs that need historical comparison (this month vs last month vs last year).

---

## Dashboard Organization: Per-Module vs Centralized

### Recommended: Hybrid (per-module dashboards + centralized executive view)

Given 21 modules and the constraint that all dashboards must use Frappe's native system:

**Per-module Dashboard (21 dashboards):**
- Each module gets one Dashboard DocType named `"{Module Name} Overview"` (e.g., "University Finance Overview")
- Contains 3-5 Number Cards + 3-4 charts specific to that module
- Linked from the module's Workspace via a shortcut
- Module field set to the module name — enables fixture filtering by module

**Centralized Analytics Workspace (1 cross-module hub):**
- `university_analytics` module Workspace (already exists at `university_analytics/workspace/university_analytics/university_analytics.json`)
- Contains shortcuts to all 21 module dashboards
- Contains 5-8 Number Cards for institution-wide KPIs (total students, total revenue, overall pass rate, faculty count, placement rate)
- Contains 2-3 cross-module trend charts
- Accessed by System Manager and University Admin roles only

**Workspace-level summary (per module, lightweight):**
- Each existing module Workspace gains 2-3 Number Card rows and 1 Chart row embedded directly on the workspace page
- These are the "at-a-glance" metrics visible without navigating to the Dashboard page
- Reduces clicks for common daily operations

This means the total artifact count is:
- 21 module Dashboards
- 21 updated module Workspaces (adding number_cards and charts rows)
- 1 updated University Analytics Workspace
- ~80-100 Number Cards (3-5 per module + executive cards)
- ~80-100 Dashboard Charts (3-4 per module + cross-module charts)
- ~30-40 Script Reports (1-2 per module for deep data tables + existing reports)

---

## Module Build Order

Based on data dependencies and existing infrastructure:

### Tier 1 — Foundation modules (build first, their data feeds other dashboards)

| Module | Reason |
|--------|--------|
| University Students (core DocType) | Student count/status is referenced by nearly every other dashboard; test permission system here |
| University Academics | Course registrations, enrollment counts — baseline for academic dashboards |
| University Examinations | Assessment Results feed CGPA, pass rate — needed before academic analytics charts |

### Tier 2 — Financial modules (high business value, mostly independent)

| Module | Reason |
|--------|--------|
| University Finance | Fee collection trends are high-visibility; Fees DocType is already well-indexed |
| University Payments | Extends Finance; Razorpay/PayU transaction summaries |

### Tier 3 — Operational modules (each relatively independent)

| Module | Reason |
|--------|--------|
| University Admissions | Admission funnel charts; flows into student creation |
| University Hostel | Room allocation rates; fairly independent dataset |
| University Library | Book issue/return trends; simple aggregates |
| Faculty Management | Leave utilization, faculty counts per department |
| University Examinations deep analytics | After Tier 1 establishes baseline pass-rate Number Cards |

### Tier 4 — Ancillary modules (lower data volume, build last)

| Module | Reason |
|--------|--------|
| University Transport | Route/bus utilization |
| University Placement | Placement rates, company-wise breakdown |
| University LMS | Online course completion rates |
| University OBE | Outcome attainment — depends on Assessment Results |
| University Research | Project tracking |
| University Grievance | SLA compliance (already has SLA Compliance Report) |
| University Feedback | Feedback form response rates |
| University Inventory | Stock levels, maintenance due alerts |
| University Integrations / Communication | Message delivery analytics |
| University Portals | Portal usage stats (if logged) |

### Tier 5 — Cross-module (build last)

| Module | Reason |
|--------|--------|
| University Analytics executive dashboard | Aggregates all Tier 1-4 metrics into one view; needs others complete first |

---

## Docker Sharing Architecture

### Architecture Diagram

The frappe_docker setup runs multiple containers. Understanding which container holds what state determines the sharing strategy.

```
Docker Compose (running devcontainer)
├── bench container ("university-bench" or similar)
│   ├── /workspace/frappe-bench/apps/university_erp/  ← Python source code
│   ├── /workspace/frappe-bench/sites/university.local/
│   │   ├── site_config.json                          ← DB credentials, payment keys
│   │   └── private/backups/                          ← bench backup outputs
│   └── /workspace/frappe-bench/env/                  ← Python venv (large, ~2 GB)
│
├── mariadb container ("university-mariadb" or similar)
│   └── /var/lib/mysql/                               ← ALL DATABASE DATA (Docker volume)
│
└── redis containers (cache + queue + socketio)
    └── Redis data (ephemeral — do not commit)
```

### What `docker commit` Captures vs Misses

| State | `docker commit bench-container` captures? | Alternative |
|-------|-------------------------------------------|-------------|
| Python source code (university_erp app) | YES | Git repository |
| Frappe site config (credentials, settings) | YES | Scrub before commit |
| Frappe assets (compiled JS/CSS) | YES | `bench build` output |
| MariaDB database + demo data | NO — separate container/volume | `bench backup` + commit MariaDB container |
| Redis cache | NO — separate container | `bench clear-cache` before commit; ephemeral is correct |
| Log files | YES (unwanted — adds size) | Delete before commit |
| Python venv | YES (large but needed) | Keep; bench cannot function without it |

### Two-Container Commit Strategy (Recommended)

This is the correct approach for preserving exact running state (code + database):

```
Step 1: Prepare bench container
    bench clear-cache
    bench build --production   (ensures assets are compiled)
    rm -rf frappe-bench/logs/*.log
    pip cache purge
    # Scrub or document all credentials in site_config.json
    bench set-config -g developer_mode 1   (ensure dev mode on for sharing)

Step 2: Take DB backup inside bench container (belt-and-suspenders)
    bench backup --with-files
    # Creates: frappe-bench/sites/university.local/private/backups/YYYYMMDD_*.sql.gz

Step 3: Commit bench container
    docker commit university-bench-1 ghcr.io/{org}/university-erp-bench:v1.0

Step 4: Commit MariaDB container
    docker commit university-mariadb-1 ghcr.io/{org}/university-erp-mariadb:v1.0

Step 5: Authenticate and push to GHCR
    echo $GITHUB_TOKEN | docker login ghcr.io -u {github_username} --password-stdin
    docker push ghcr.io/{org}/university-erp-bench:v1.0
    docker push ghcr.io/{org}/university-erp-mariadb:v1.0

Step 6: Create docker-compose.share.yml for recipient
    services:
      bench:
        image: ghcr.io/{org}/university-erp-bench:v1.0
        # same ports, volumes, environment as original devcontainer
      mariadb:
        image: ghcr.io/{org}/university-erp-mariadb:v1.0
        # no external volume mount — data is baked in

Step 7: Recipient pull and start
    echo $GITHUB_TOKEN | docker login ghcr.io -u {username} --password-stdin
    docker pull ghcr.io/{org}/university-erp-bench:v1.0
    docker pull ghcr.io/{org}/university-erp-mariadb:v1.0
    docker compose -f docker-compose.share.yml up -d
    # Wait ~60s for services to start
    docker exec -it bench bench clear-cache
    # Access: http://localhost:8000/app
```

### GHCR Authentication Requirements

- GHCR packages default to private visibility when pushed by a user account
- Sender: needs `write:packages` scope on their GitHub PAT
- Recipient: needs `read:packages` scope on their GitHub PAT
- Sender must add recipient as a package collaborator in GitHub package settings, OR make the package visibility "internal" (org members only) or "public"
- Organization vs personal account: under `ghcr.io/{github_username}/...` for personal; `ghcr.io/{org}/...` for organization accounts

### Image Size Management

Expected sizes for this project:

| Component | Expected Committed Size | Notes |
|-----------|------------------------|-------|
| Bench container (after cleanup) | 4-7 GB | Python venv (~1.5 GB), Frappe app source + compiled assets (~1.5 GB), node_modules in frappe app (~1 GB), DB backup copy (~500 MB) |
| MariaDB container | 1-3 GB | MariaDB binaries + university.local database with demo data |
| Redis containers | Do not commit | Ephemeral; rebuilt by Frappe on startup |

Total: approximately 5-10 GB across two pushes. Practical for developer-to-developer sharing over reasonable internet.

### Alternative: Bench Backup as Side Artifact

If the MariaDB two-container approach is too complex, an alternative:

```
Step 1: Commit only the bench container (with scrubbed credentials)
Step 2: Export DB dump: bench backup --with-files
Step 3: Upload SQL.gz as a GitHub Release asset on the private repo (not GHCR)
Step 4: Recipient pulls bench image, installs fresh MariaDB, restores dump:
    bench restore /path/to/backup.sql.gz --mariadb-root-password=123
```

This approach has a smaller GHCR footprint but requires more steps for the recipient.

---

## Architectural Patterns to Follow

### Pattern 1: Script Report as Single Source of Truth for Complex Metrics

**What:** Build all non-trivial analytics (more than a simple COUNT/SUM) as Script Reports first. The Script Report's `execute()` function returns columns, data, chart config, and summary. Dashboard Charts and Number Cards then reference the Report — they do not contain query logic themselves.

**Why:** Script Reports are versioned source files in the app directory. They appear in the Report Builder UI for end-user exploration. They can be exported and filtered. They are independently testable. Dashboard Charts and Number Cards that reference Reports stay thin; business logic stays in Python.

**When to use "Document Type" chart type instead:** Only for the simplest possible aggregates (total student count, total fee documents created this month) where no joins, conditions, or transformations are needed.

**Example:**
```python
# university_finance/report/fee_collection_trend/fee_collection_trend.py
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)     # SQL with GROUP BY month
    chart = get_chart(data)      # frappe.Chart config dict
    summary = get_summary(data)  # total collection, pending, collected %
    return columns, data, None, chart, summary
```

### Pattern 2: Module Field Set on All Dashboard Artifacts

**What:** When creating Dashboard, Dashboard Chart, and Number Card records (whether via UI or fixture), always set the `module` field to the owning module (e.g., "University Finance"). Set `is_standard = 1` in developer mode.

**Why:** The `fixtures` list in `hooks.py` filters by module to know which records to export. Without `module` set, records are invisible to `bench export-fixtures`. Dashboard Charts and Number Cards with no module are also invisible in the Desk UI filter dropdowns. This is the single most important metadata field for fixture management.

### Pattern 3: Workspace as Navigation Hub, Dashboard as Analytics Destination

**What:** Module Workspaces contain 2-3 Number Card rows and 1 chart row for at-a-glance status. They also contain a shortcut tile that navigates to the full Dashboard. The Dashboard contains the comprehensive analytical view (5-10 charts, full Number Card set, filter controls).

**Why:** The Workspace is visible every time a user navigates to the module. Overloading it with 10 charts creates scroll fatigue. The Dashboard is opt-in — users who want deep analytics click through. This matches standard Frappe ERP UX patterns (ERPNext uses the same two-tier pattern for Accounting Workspace vs Accounts Dashboard).

### Pattern 4: Fixture Export After Every Dashboard Build Session

**What:** At the end of every dashboard build session (or after every batch of 3-5 dashboards), run `bench export-fixtures --app university_erp` and commit the resulting JSON files. This is mandatory infrastructure, not optional cleanup.

**Why:** Dashboard records exist in MariaDB. If the DB is lost or the environment is rebuilt without `docker commit`, all dashboard work is gone unless it is also in fixture JSON files. The `docker commit` approach for sharing means the shared image IS the database — but fixtures ensure reproducibility from source for future work.

```
# After every dashboard build session:
bench export-fixtures --app university_erp
# Inspect changed files in university_erp/fixtures/
git add university_erp/fixtures/Dashboard.json university_erp/fixtures/"Number Card.json" ...
git commit -m "feat: add {module} dashboard fixtures"
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Building All Dashboards in One Pass Without Incremental Testing

**What people do:** Create all 21 module dashboards over several days, then run fixture export once at the end, then discover that 5 modules have permission errors, 3 have zero-data chart failures, and the fixture export silently missed 8 charts because `module` was not set.

**Why it's wrong:** Errors compound. Debugging 21 modules at once is a debugging nightmare. Fixture export errors are silent — `bench export-fixtures` does not warn about records with missing `module` fields.

**Do this instead:** Build one module dashboard, test it (with both Administrator and University Admin role), export fixtures, verify fixture JSON contains the expected records, commit. Then repeat for the next module. Treat each module as its own deliverable.

### Anti-Pattern 2: Using `dashboard_chart.chart_type = "Custom"` for Everything

**What people do:** Skip Script Reports entirely; write all chart logic in JavaScript dashboard_chart_source files because it gives more control over rendering.

**Why it's wrong:** Custom JS sources are not exportable as human-readable fixtures in the same way. They bypass the Report Builder UI that administrators use for ad-hoc exploration. They do not support the `summary` pattern (totals shown below the chart). They make testing harder.

**Do this instead:** Use Script Reports for all data logic. Use `chart_type = "Report"` on Dashboard Charts. Reserve `chart_type = "Custom"` only for exotic visualizations not achievable with the standard chart types (which are: Line, Bar, Percentage, Pie, Donut, Heatmap).

### Anti-Pattern 3: Hardcoding Academic Year or Date Ranges in Fixtures

**What people do:** Set `filters_json` on Dashboard Charts to a specific academic year (`"filters": [["academic_year", "=", "2025-2026"]]`) so charts show data during development. Export fixtures with this hardcoded filter.

**Why it's wrong:** The shared image will show the correct data, but when the academic year changes, all dashboards silently show 0 because the filter references a past year. New administrators won't know to update the filter.

**Do this instead:** Use `dynamic_filters_json` (the `dynamic_filters_section` field on Dashboard Chart) to inject the current academic year from the session context. Or leave the academic year filter empty (show all-time data by default) and rely on the chart's `timespan` field ("Last Year", "Last Quarter") for time-based charts. If a specific academic year default is needed, use `frappe.defaults.get_user_default("academic_year")` in the dynamic filter.

### Anti-Pattern 4: Committing MariaDB Container Without Integrity Check

**What people do:** Stop Docker Compose, commit the MariaDB container immediately, push to GHCR. Recipient starts the container and finds the database has corrupted InnoDB tables from an interrupted transaction or an unclean MariaDB shutdown.

**Why it's wrong:** MariaDB requires a clean shutdown before its data files are in a consistent state for copying. A container that was `docker stop`-ed abruptly may have in-flight transactions that were not flushed.

**Do this instead:** Before committing the MariaDB container:
1. Connect to MariaDB and run `FLUSH TABLES WITH READ LOCK;`
2. Or simply run `bench backup --with-files` from the bench container, which triggers a clean dump and verifies table integrity during the dump process
3. Then stop the MariaDB container cleanly (`docker stop --time 30 university-mariadb-1`)
4. Then `docker commit` the stopped (not running) container

---

## Integration Points

### Dashboard → Existing Report Infrastructure

| Existing Report | Module | Can be used for Dashboard Chart |
|-----------------|--------|--------------------------------|
| Fee Collection Summary | University Finance | YES — chart_type = "Report", x=month, y=amount |
| Fee Defaulters | University Finance | YES — Number Card counting defaulters |
| Student Performance Analysis | University Analytics | YES — chart_type = "Report", existing pie chart |
| Communication Analytics | University Analytics | YES — chart_type = "Report" |
| SLA Compliance Report | University Grievance | YES — Number Card for open grievances |

### Dashboard → Existing Scheduled Task Infrastructure

The analytics module already has scheduled tasks for KPI calculation:
- `university_erp.university_erp.analytics.scheduled_tasks.calculate_daily_kpis` (daily)
- `university_erp.university_erp.analytics.scheduled_tasks.calculate_weekly_kpis` (weekly)
- `university_erp.university_erp.analytics.scheduled_tasks.calculate_monthly_kpis` (monthly)

These tasks populate `KPI Value` records. Number Cards using `type = "Custom"` can read the latest `KPI Value` for a given `Kpi Definition` — this is the pattern for showing "this month vs last month" percentage change.

### Docker Sharing → Developer Environment

| Component | Sender Prepares | Recipient Configures |
|-----------|----------------|---------------------|
| Bench image | Commit after `bench clear-cache`, cleanup, credential scrub | Pull, verify `bench doctor`, run `bench clear-cache` again |
| MariaDB image | Commit after clean shutdown; verify with `bench backup` first | Pull, start before bench container (MariaDB must be ready first) |
| Site credentials | Scrub or document sandbox values in `site_config.json` | Update with their own payment gateway sandbox keys if needed |
| GHCR access | Add recipient as package collaborator | `echo $TOKEN | docker login ghcr.io` then pull |
| Startup order | Document in onboarding | Start MariaDB → wait 15s → start bench → wait 60s → `bench clear-cache` → access site |

---

## Scaling Considerations

| Scale | Dashboard Architecture Adjustment |
|-------|----------------------------------|
| Dev share (2 developers) | `docker commit` two-container approach; private GHCR package; no CDN needed |
| Demo environment (10 admin users) | Same architecture; add Redis commit or at minimum document `bench clear-cache` on start |
| Production university (~500 staff using dashboards) | Move from `docker commit` to proper Docker image build; use `bench backup` + restore for DB; add db indexes for aggregate queries; set Number Card auto-refresh to 1 hour minimum |
| Large university (>10,000 students, dashboard queries slow) | Add read replica for analytics queries; cache Number Card results via KPI Value scheduled computation; limit raw SQL reports to background jobs only |

---

## Sources

- **HIGH confidence:** Direct inspection of Frappe v15 source files: `dashboard/dashboard.json`, `dashboard_chart/dashboard_chart.json`, `number_card/number_card.json`, `workspace/workspace.json`, `dashboard_chart_link/dashboard_chart_link.json`, `workspace_chart/workspace_chart.json`, `dashboard_chart_source/dashboard_chart_source.py` — all in `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/`
- **HIGH confidence:** Direct inspection of existing university_erp workspace fixtures (16 module workspaces in `workspace/**/*.json`) confirming fixture structure and module field conventions
- **HIGH confidence:** `hooks.py` fixture list inspection confirming current export scope (Workspaces only — Dashboard, Number Card, Dashboard Chart not yet in fixtures)
- **HIGH confidence:** `university_analytics/report/student_performance_analysis/student_performance_analysis.py` — confirms existing Script Report pattern with columns/data/chart/summary return signature
- **HIGH confidence:** `university_analytics/doctype/kpi_definition/kpi_definition.json` — confirms KPI infrastructure exists with SQL/Python/Formula calculation methods
- **HIGH confidence:** `university_analytics/workspace/university_analytics/university_analytics.json` — confirms centralized analytics workspace already exists
- **HIGH confidence:** Docker container commit/push mechanics — stable Docker internals
- **HIGH confidence (from PITFALLS.md):** MariaDB in separate container from bench container — confirmed by frappe_docker standard architecture
- **MEDIUM confidence:** Frappe dashboard `dynamic_filters_json` behavior in v15 — from training data (Frappe v15 released February 2024); recommend testing during build

---

*Architecture research for: Frappe v15 University ERP Dashboards + Docker devcontainer sharing via GHCR*
*Researched: 2026-03-17*
