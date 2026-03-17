# Stack Research

**Domain:** Frappe v15 Dashboard & Analytics tooling + Docker devcontainer sharing via GHCR
**Researched:** 2026-03-17
**Confidence:** HIGH (all findings verified directly from Frappe v15 source code in the running bench)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Frappe Dashboard DocType | v15 (frappe source verified) | Container for charts + number cards per module | Native, zero-setup, ships as JSON fixture, auto-loaded by `bench migrate` |
| Frappe Dashboard Chart DocType | v15 (frappe source verified) | All time-series, group-by, and report-backed charts | 6 chart types, 6 data modes, built-in caching, role-based access — no external lib needed |
| Frappe Number Card DocType | v15 (frappe source verified) | KPI big-number tiles with trend comparison | 3 card types, 5 aggregate functions, built-in period-over-period stats |
| Frappe Script Report | v15 (frappe source verified) | Complex cross-DocType tabular reports with filters | Full Python + SQL access, exports to Excel/PDF, feeds Dashboard Charts |
| Frappe Workspace DocType | v15 (frappe source verified) | Module landing page that embeds charts + shortcuts | Charts embedded directly in Workspace via `Workspace Chart` child table |
| Docker `docker commit` + `docker push` | Docker CLI (standard) | Capture exact running container state with DB | Preserves MariaDB data, site config, Redis state — the receiver just `docker run` |
| GitHub Container Registry (ghcr.io) | GitHub standard | Host and share the committed image | Free for public repos, auth via PAT, `docker pull ghcr.io/org/repo:tag` |

### Supporting Libraries / Patterns

| Library / Pattern | Version | Purpose | When to Use |
|-------------------|---------|---------|-------------|
| Frappe Dashboard Chart Source | v15 | Custom Python-backed chart with its own JS filter config | Use when Chart type "Custom" is needed — complex multi-join queries that can't be expressed as simple DocType aggregates |
| Frappe Query Report (Script Report) | v15 | Filterable tabular report with column definitions | Every module that needs an exportable data table (all 21 modules need one) |
| Frappe Report Builder | v15 | No-code point-and-click report | Use only for simple single-DocType reports that need no Python — Config saved as JSON, user-editable in UI |
| `bench export-fixtures` | bench CLI | Export Dashboard/Number Card/Report JSON to app files | Run after creating fixtures in the UI in developer mode to persist them to codebase |
| `frappe.utils.dashboard.cache_source` decorator | v15 | Cache custom chart source results | Apply to every custom chart source `get()` function — avoids repeated heavy queries |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Frappe developer mode (`developer_mode = 1`) | Enables `is_standard = 1` on DocTypes, auto-exports JSON on save | Must be on when creating dashboard fixtures so they export to the app directory |
| `bench migrate` | Syncs standard JSON fixtures from app files into the site database | Run after adding new dashboard/chart/number_card JSON files to the app |
| `bench export-fixtures` | Exports fixtures defined in `hooks.py` to the app directory | Use for fixtures that need hooks.py filter-based export (Roles, Custom Fields, etc.) |
| `docker commit <container> <image>:<tag>` | Snapshot a running container including filesystem | Captures MariaDB data directory, site config, installed apps, compiled assets |
| `docker push ghcr.io/<org>/<repo>:<tag>` | Push committed image to GitHub Container Registry | Requires `docker login ghcr.io` with a GitHub PAT (write:packages scope) |

---

## Dashboard DocType — Capabilities (verified from source)

The `Dashboard` DocType is a named container. Key fields:

| Field | Type | Notes |
|-------|------|-------|
| `dashboard_name` | Data (autoname) | Unique identifier — used in URL `/app/dashboard-view/<name>` |
| `charts` | Table of `Dashboard Chart Link` | Ordered list of chart names to display; each has a `width` (Full/Half) |
| `cards` | Table of `Number Card Link` | KPI tiles shown above charts |
| `chart_options` | JSON Code | Default color palette for all charts on this dashboard |
| `is_standard` | Check | Set to 1 + assign `module` to ship as app fixture |
| `module` | Link to Module Def | Must match a module in `modules.txt` — determines file path |

**Fixture file path pattern:**
```
university_erp/<module_scrubbed>/dashboard/<dashboard_name_scrubbed>/<dashboard_name_scrubbed>.json
```
Example: `university_erp/university_finance/dashboard/fee_collections/fee_collections.json`

**Loading mechanism:** `bench migrate` calls Frappe's module import system which scans all app module directories for standard JSON fixtures. No hooks.py entry needed for `Dashboard`, `Dashboard Chart`, or `Number Card` — they are loaded automatically when `is_standard=1` and `module` is set, and the JSON file exists in the correct path.

---

## Dashboard Chart DocType — Capabilities (verified from source)

### Chart Types (visual rendering — `type` field)

| Type | Use Case |
|------|----------|
| `Line` | Time series trends (enrollment over months, fee collection over time) |
| `Bar` | Comparison between categories (department-wise student counts) |
| `Percentage` | Stacked percentage breakdown (program-wise pass/fail) |
| `Pie` | Distribution (payment method breakdown) |
| `Donut` | Same as Pie with hole; preferred for single-series distributions |
| `Heatmap` | Activity density over calendar year (attendance heatmap) |

### Data Modes (`chart_type` field)

| Mode | What It Does | Best For |
|------|-------------|----------|
| `Count` | COUNT(*) on a DocType, grouped by a date field | Student enrollment trends, admission counts over time |
| `Sum` | SUM(field) on a DocType, grouped by a date field | Monthly fee collection amounts, revenue trends |
| `Average` | AVG(field) on a DocType, grouped by a date field | Average CGPA trends, average marks over semesters |
| `Group By` | COUNT/SUM/AVG grouped by a categorical field | Department-wise student distribution, program-wise pass rates |
| `Report` | Pulls data from an existing Frappe Report | Use when the Report already computes complex data; can use report's own chart or map x/y axes |
| `Custom` | Calls a Python function via Dashboard Chart Source | Multi-join queries, cross-app data, anything requiring raw SQL |

### Timeseries Configuration

- `timeseries = 1` enables date-axis charts (Count, Sum, Average modes)
- `based_on`: the date field on the DocType to aggregate by (e.g., `enrollment_date`, `posting_date`)
- `timespan`: `Last Year | Last Quarter | Last Month | Last Week | Select Date Range`
- `time_interval`: `Yearly | Quarterly | Monthly | Weekly | Daily`
- `from_date` / `to_date`: used when `timespan = "Select Date Range"`

### Filters

- `filters_json`: Static filters as a JSON array of Frappe filter tuples: `[["DocType", "field", "operator", "value", false]]`
- `dynamic_filters_json`: Runtime filters as JS expressions — e.g. `{"company": "frappe.defaults.get_user_default(\"Company\")"}`
- `roles`: Optional table — if set, only users with these roles can view the chart

**Fixture file path pattern:**
```
university_erp/<module_scrubbed>/dashboard_chart/<chart_name_scrubbed>/<chart_name_scrubbed>.json
```

---

## Number Card DocType — Capabilities (verified from source)

### Card Types (`type` field)

| Type | What It Does | When to Use |
|------|-------------|-------------|
| `Document Type` | Runs COUNT/SUM/AVG/MIN/MAX against a DocType with filters | Standard KPIs — total students, total fee collected this year |
| `Report` | Pulls a single aggregated value from a Frappe Report column | When the KPI is already computed by a report (use Sum/Average/Min/Max of a column) |
| `Custom` | Calls a whitelisted Python method that returns `{"value": X, "fieldtype": "Currency", "route": [...]}` | Complex KPIs requiring joins, CGPA calculations, multi-source aggregations |

### Aggregate Functions (Document Type mode)

`Count | Sum | Average | Minimum | Maximum`

### Trend / Comparison Display

- `show_percentage_stats = 1`: Shows percentage change vs. previous period
- `stats_time_interval`: `Daily | Weekly | Monthly | Yearly` — the comparison period
- `show_full_number`: Display `1,234,567` instead of `1.2M` (useful for student counts)
- `color` / `background_color`: Brand the card

### Custom Card Method Contract

```python
@frappe.whitelist()
def get_total_cgpa_above_threshold():
    value = frappe.db.sql("SELECT COUNT(*) FROM ...", as_list=True)[0][0]
    return {
        "value": value,
        "fieldtype": "Int",
        "route_options": {"program": "B.Tech"},
        "route": ["query-report", "Student CGPA Report"]
    }
```

The `route` key makes the card clickable — it navigates to a list or report for drill-down.

**Fixture file path pattern:**
```
university_erp/<module_scrubbed>/number_card/<card_name_scrubbed>/<card_name_scrubbed>.json
```

---

## Report Types — Comparison (verified from source)

| Type | Code Required | SQL Access | Filters UI | Column Config | Export | Dashboard Chart Feed | When to Use |
|------|--------------|-----------|-----------|---------------|--------|---------------------|-------------|
| `Report Builder` | None | No (ORM only) | Auto-generated | GUI | Yes | Yes | Simple single-DocType tabular lists; user-configurable; save as Custom Report |
| `Query Report` | SQL only | Full SQL | Defined in JSON | JSON | Yes | Yes | Complex JOINs across tables; no Python logic needed |
| `Script Report` | Python + optional JS | Full (via `frappe.db`) | Defined in Python | Python `columns` list | Yes | Yes | Cross-DocType analytics, computed columns, conditional formatting |
| `Custom Report` | None | No | From parent | Inherited | Yes | No | User-saved variant of Report Builder |

**Decision for this project:**
- Use **Script Report** for all 21 module analytics reports — they handle the complex joins needed for university data (e.g., Student + Enrollment + Program + Fees in one report)
- Use **Report Builder** only for simple list exports where users need to self-configure columns
- Use `Query Report` when Python logic is not needed but SQL joins are required and the query is stable

**Script Report file structure:**
```
university_erp/<module>/report/<report_name_scrubbed>/
    <report_name_scrubbed>.json   # DocType record: report_type, ref_doctype, is_standard, filters
    <report_name_scrubbed>.py     # get_columns(), get_data(filters)
    <report_name_scrubbed>.js     # Optional: frappe.query_reports["Name"] = {onload, formatter}
```

---

## Workspace Integration Pattern (verified from source)

Workspaces are the Frappe Desk home pages. Each module should have one Workspace. The `Workspace` DocType has:
- `charts` (Table of `Workspace Chart`): each row links to a `Dashboard Chart` — embeds the chart directly on the Workspace page without opening a separate Dashboard view
- `number_cards` (Table of `Workspace Number Card`): KPI tiles on the Workspace
- `shortcuts`: Quick links to lists, reports, forms
- `quick_lists`: Embedded list views

**Recommended approach for university_erp:**
- Each of the 21 modules gets one `Workspace` with 2-4 Number Cards and 1-2 key charts embedded
- A separate `Dashboard` (via the Dashboard DocType) per module provides the full analytics view with all charts
- Link from Workspace shortcut to the full Dashboard for deep-dive analytics

---

## Docker Commit + GHCR Push — Workflow

The goal is to capture the exact running state: MariaDB data, site config, Redis, Frappe app code, compiled assets — so the second developer can `docker run` and immediately have a working system.

### Why `docker commit` over alternatives

| Approach | Preserves DB Data | Preserves Code | Easy for Receiver | Notes |
|---------|-----------------|---------------|------------------|-------|
| `docker commit` | Yes (in container FS) | Yes | Single `docker pull` + `run` | MariaDB data at `/var/lib/mysql` is in the container layer |
| `bench backup` + fresh setup | No (manual restore) | Code only (git) | Requires re-setup | Better for production; complex for dev onboarding |
| Volume snapshot | Yes (external) | No | Volume must be shared separately | Requires shared storage infrastructure |
| Docker Compose with named volumes | Yes (external) | No | Volumes not in image | Named volumes not included in `docker commit` |

**Decision: `docker commit` is the right tool.** It captures the union filesystem layer including all files written at runtime (MariaDB data directory, site_config.json, Redis dump, compiled assets). The receiver does not need to install anything except Docker.

### Step-by-step Workflow

**Phase 1 — Prepare the container for commit:**
```bash
# 1. Stop bench processes gracefully (don't stop the container)
#    Run inside the devcontainer:
bench stop

# 2. Flush MariaDB and Redis to disk before commit
#    Inside devcontainer:
mysql -u root -p123 -e "FLUSH TABLES WITH READ LOCK; FLUSH LOGS;"
redis-cli -h redis-cache BGSAVE
redis-cli -h redis-queue BGSAVE
# Wait a few seconds for BGSAVE to complete

# 3. Exit the container (don't stop it — commit the running or stopped container)
exit
```

**Phase 2 — Commit the devcontainer:**
```bash
# Find the container ID (on the host machine)
docker ps -a | grep frappe
# or if using docker-compose:
docker compose ps

# Commit the container to a local image
docker commit <container_id_or_name> university-erp-dev:v1.0-demo

# Verify the image
docker images | grep university-erp-dev
```

**Phase 3 — Tag and push to GHCR:**
```bash
# Authenticate with GitHub Container Registry
# Requires a GitHub PAT with write:packages scope
echo $GITHUB_PAT | docker login ghcr.io -u <github_username> --password-stdin

# Tag for GHCR
docker tag university-erp-dev:v1.0-demo ghcr.io/<github_org>/<repo_name>:v1.0-demo

# Push (may be large — 5-15GB depending on data)
docker push ghcr.io/<github_org>/<repo_name>:v1.0-demo
```

**Phase 4 — Receiver pulls and runs:**
```bash
# Authenticate (public package = no auth needed; private = needs read:packages PAT)
echo $GITHUB_PAT | docker login ghcr.io -u <username> --password-stdin

# Pull the image
docker pull ghcr.io/<github_org>/<repo_name>:v1.0-demo

# Run it (map ports to match original devcontainer)
docker run -d \
  --name university-erp \
  -p 8000:8000 \
  -p 9000:9000 \
  ghcr.io/<github_org>/<repo_name>:v1.0-demo \
  /bin/bash -c "cd /workspace/development/frappe-bench && bench start"
```

### Critical Caveats

1. **MariaDB must be in the same container as frappe** — if MariaDB runs as a *separate* compose service container, `docker commit` of the frappe container will NOT include the database. You must either:
   - Commit both containers and coordinate running them, OR
   - Use `bench backup` to create a SQL dump, include it in the committed image, and add a startup script that restores it on first run

2. **Redis state is ephemeral** — Redis data (cache + queue) will be included only if `redis.conf` has `save` directives and `appendonly yes`. For a dev snapshot, Redis data loss is acceptable — Frappe rebuilds cache on startup.

3. **Image size** — A full Frappe bench with MariaDB data can be 8-15GB. Use `--compress` flag with `docker commit` if size is a concern:
   ```bash
   docker commit --compress <container> university-erp-dev:v1.0-demo
   ```

4. **Network dependencies** — If the devcontainer uses Docker Compose networking (separate mariadb, redis-cache, redis-queue services), the committed frappe container will fail to start because those services won't exist. Before committing, reconfigure bench to point to localhost:
   ```bash
   bench set-config -g db_host 127.0.0.1
   bench set-config -g redis_cache redis://127.0.0.1:6379
   ```
   And ensure MariaDB + Redis are installed inside the frappe container, or use a single-container setup.

### Recommended Architecture for Sharing

**Use a single-container commit approach:**
- Run MariaDB and Redis inside the devcontainer (not as separate compose services)
- OR: create a `docker-compose.yml` for the receiver that uses the committed image for frappe + separate mariadb/redis images, and include a `demo-data.sql.gz` in the frappe image that the entrypoint restores on first run

**Simplest working approach for this project:**
1. `bench backup --with-files` to create `*.sql.gz` backup inside the container
2. `docker commit` the container (includes the backup file)
3. Write an entrypoint script that detects first-run and runs `bench restore <backup>` automatically
4. Receiver runs `docker run` — entrypoint restores DB, starts bench

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Script Report | Query Report | When you need SQL JOINs but zero Python logic and the query is truly static |
| Script Report | External BI tool (Metabase, Grafana) | When analytics must be standalone, multi-tenant, or need real-time streaming — not applicable here |
| Dashboard Chart (native) | Chart.js / D3.js custom page | Only if you need interaction Frappe Charts cannot provide (e.g., map visualizations, custom drill-down trees) — overkill here |
| `docker commit` | Ansible/IaC provisioning | For repeatable production-like setup — NOT appropriate for a one-time dev snapshot with specific DB state |
| `docker commit` | `bench backup` + setup docs | When the receiver has a reliable network and 2+ hours; too slow for dev onboarding |
| GHCR | Docker Hub | When you want public anonymous pull; Docker Hub rate-limits unauthenticated pulls. GHCR is free and GitHub-native |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| External charting libraries (Chart.js, Recharts, Plotly) in Frappe Desk | Project constraint; also redundant — Frappe already ships `frappe-charts` (Heatmap, Line, Bar, Pie, Donut) internally used by Dashboard Chart | Frappe Dashboard Chart DocType with appropriate `type` |
| Custom Page with `frappe.ui.Chart` calls in raw JS | Manual, not shippable as fixtures, bypasses Frappe's caching and permission system | Dashboard Chart DocType — ships as JSON, auto-loads, respects roles |
| Report Builder for complex analytics | GUI-only, no Python access, cannot do JOINs across DocTypes, columns limited to single DocType fields | Script Report |
| `is_standard = 0` fixtures in hooks.py for dashboards | Works but is the wrong tool — hooks.py fixtures are for data fixtures (Roles, Custom Fields). Dashboard/Chart/NumberCard have their own module-based loading | Set `is_standard = 1`, assign `module`, place JSON in correct path, run `bench migrate` |
| `docker save` / `docker export` instead of `docker commit` | `docker save` exports the image (already built); `docker export` flattens a container FS but loses layer history and metadata. Neither captures a running container's current state into a new pushable image | `docker commit` to create a new image from the current container state |
| Named Docker volumes for DB sharing | Named volumes are host-local; they can't be pushed to GHCR | Embed MariaDB data inside the container via single-container approach or use a backup+restore entrypoint |

---

## Pattern: Standard Fixture File Structure for Dashboard Artifacts

This is the exact pattern used by ERPNext, verified against `erpnext/accounts/`:

```
university_erp/
└── university_finance/                    # module directory (scrubbed name)
    ├── number_card/
    │   └── total_fee_collected/
    │       └── total_fee_collected.json   # Number Card fixture
    ├── dashboard_chart/
    │   └── monthly_fee_collection/
    │       └── monthly_fee_collection.json  # Dashboard Chart fixture
    └── dashboard/
        └── fee_collections/
            └── fee_collections.json        # Dashboard fixture
```

**Number Card fixture example (Document Type mode):**
```json
{
    "doctype": "Number Card",
    "name": "Total Fee Collected",
    "label": "Total Fee Collected",
    "type": "Document Type",
    "document_type": "Fees",
    "function": "Sum",
    "aggregate_function_based_on": "grand_total",
    "filters_json": "[[\"Fees\",\"docstatus\",\"=\",\"1\",false],[\"Fees\",\"posting_date\",\"Timespan\",\"this year\",false]]",
    "show_percentage_stats": 1,
    "stats_time_interval": "Monthly",
    "is_public": 1,
    "is_standard": 1,
    "module": "University Finance"
}
```

**Dashboard Chart fixture example (timeseries Count):**
```json
{
    "doctype": "Dashboard Chart",
    "name": "Monthly Enrollment",
    "chart_name": "Monthly Enrollment",
    "chart_type": "Count",
    "document_type": "Student",
    "based_on": "enrollment_date",
    "timeseries": 1,
    "timespan": "Last Year",
    "time_interval": "Monthly",
    "type": "Line",
    "filters_json": "[]",
    "is_public": 1,
    "is_standard": 1,
    "module": "University Academics"
}
```

**Dashboard fixture example:**
```json
{
    "doctype": "Dashboard",
    "name": "Academics",
    "dashboard_name": "Academics",
    "is_standard": 1,
    "module": "University Academics",
    "cards": [
        {"card": "Total Active Students"},
        {"card": "Total Enrolled This Semester"}
    ],
    "charts": [
        {"chart": "Monthly Enrollment", "width": "Full"},
        {"chart": "Department-Wise Students", "width": "Half"},
        {"chart": "Program-Wise Distribution", "width": "Half"}
    ]
}
```

---

## Version Compatibility

| Component | Version | Compatibility Notes |
|-----------|---------|-------------------|
| Frappe Dashboard Chart | v15 (source modified 2025-06-08) | `show_values_over_chart` field added; `currency` field present; `roles` table for access control |
| Frappe Number Card | v15 (source modified 2025-05-21) | `show_full_number`, `background_color` fields confirmed present |
| Frappe Report | v15 (source modified 2025-08-28) | 4 report types confirmed: Report Builder, Query Report, Script Report, Custom Report |
| Frappe Workspace | v15 | `number_cards` tab and `workspace_number_card` child table confirmed; `charts` tab uses `Workspace Chart` child |
| MariaDB | 10.3+ (required by Frappe v15) | `docker commit` captures `/var/lib/mysql` — ensure InnoDB is used (not MEMORY engine) |
| Docker | 20.10+ | `--compress` flag available; `docker login ghcr.io` syntax unchanged |

---

## Sources

- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/dashboard/dashboard.json` — Dashboard DocType fields, permissions, is_standard mechanism
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/dashboard_chart/dashboard_chart.json` — All chart types, data modes, filter options (modified 2025-06-08)
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/dashboard_chart/dashboard_chart.py` — `get()` function signature, `get_chart_config()`, `get_group_by_chart_config()`, cache mechanism
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/number_card/number_card.json` — Number Card fields confirmed (modified 2025-05-21)
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/number_card/number_card.py` — `get_result()`, `get_percentage_difference()`, Custom card method contract
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/core/doctype/report/report.json` — Report types confirmed (modified 2025-08-28)
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/workspace/workspace.json` — Workspace tabs, charts/number_cards child tables
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/desk/doctype/dashboard_chart_source/dashboard_chart_source.py` — Custom chart source JS file path convention
- ERPNext v15 source: `/workspace/development/frappe-bench/apps/erpnext/erpnext/accounts/` — Verified real fixture structure for Dashboard, Dashboard Chart, Number Card
- ERPNext v15 source: `/workspace/development/frappe-bench/apps/erpnext/erpnext/accounts/dashboard_chart_source/account_balance_timeline/account_balance_timeline.js` — Custom Dashboard Chart Source JS pattern
- Frappe v15 source: `/workspace/development/frappe-bench/apps/frappe/frappe/modules/utils.py` — `export_module_json()` confirms `is_standard + developer_mode` triggers auto-export and subsequent `bench migrate` auto-import
- University ERP: `/workspace/development/frappe-bench/apps/university_erp/university_erp/hooks.py` — Existing fixtures pattern, 21 modules confirmed in `modules.txt`

---

*Stack research for: Frappe v15 Dashboard & Analytics + Docker GHCR sharing*
*Researched: 2026-03-17*
