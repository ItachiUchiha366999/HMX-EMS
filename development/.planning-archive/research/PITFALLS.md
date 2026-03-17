# Pitfalls Research

**Domain:** Frappe v15 Dashboards / Analytics + Docker devcontainer sharing via GHCR
**Researched:** 2026-03-17
**Confidence:** MEDIUM — no external fetch available; findings from training data (Frappe v15 knowledge, Docker internals), verified against codebase analysis in `.planning/codebase/`. Flags indicate where live verification is recommended.

---

## Critical Pitfalls

### Pitfall 1: Dashboard Fixtures Not Exported — Dashboards Live Only in the Database

**What goes wrong:**
You build 21 module dashboards through the Frappe Desk UI (Number Cards, Charts, Dashboard DocTypes). They look complete. You `docker commit` the container. The other developer pulls and runs the image — all dashboards are present because the DB is included. But if anyone ever needs to reproduce this from source (reinstall, migrate, upgrade), the dashboards vanish. There is no code representation. The fixtures were never exported.

**Why it happens:**
Frappe dashboards (Dashboard, Number Card, Dashboard Chart) are DocType records stored in MariaDB. Creating them via the UI writes rows to the database — it does NOT auto-generate fixture JSON files in the app. Developers conflate "it's saved" (database) with "it's in source control" (fixtures). The `docker commit` approach papers over this by shipping the DB, but fixtures are the correct long-term mechanism for reproducibility.

**How to avoid:**
After building each dashboard batch, run `bench export-fixtures --app university_erp` or export via Frappe's fixture system. Fixture DocTypes to add to `hooks.py`:
```python
fixtures = [
    {"dt": "Dashboard", "filters": [["module", "like", "University%"]]},
    {"dt": "Number Card", "filters": [["module", "like", "University%"]]},
    {"dt": "Dashboard Chart", "filters": [["module", "like", "University%"]]},
    {"dt": "Workspace", "filters": [["module", "like", "University%"]]},
]
```
Export after every build session. Commit fixtures to `university_erp/fixtures/`. This ensures dashboards survive reinstalls and are reviewable in git.

**Warning signs:**
- Dashboards only visible on the running container, not reproducible via `bench install-app`
- No `*.json` files in `university_erp/fixtures/` for Dashboard or Number Card DocTypes
- Git history shows no fixture changes despite dashboard development

**Phase to address:** Dashboard build phase (before any docker commit work) — fixtures export must be part of the "definition of done" for each dashboard batch.

---

### Pitfall 2: `docker commit` Captures All Secrets in the Image Layer

**What goes wrong:**
The running devcontainer has `site_config.json` containing MariaDB credentials, Razorpay keys, Firebase service account JSON, and other secrets in plaintext. A `docker commit` captures the full filesystem of the container — every file, including `site_config.json`, `.env`, and any credential-bearing configs. The committed image is then pushed to GHCR. Even if the GHCR repo is private, the secrets are now in an image layer, and any developer who pulls the image can extract them with `docker run ... cat site_config.json`.

**Why it happens:**
`docker commit` is a snapshot of a running container's writable layer on top of the base image. It is not selective — it does not understand which files are secrets. Developers treating it like "copy my working directory" miss that it also copies all service credentials baked into Frappe's site config and the `.env` file if it was copied into the container.

**How to avoid:**
Before committing, scrub or replace credentials:
1. Replace real payment gateway keys in `site_config.json` with placeholder strings (`"razorpay_key_id": "PLACEHOLDER_FOR_SHARING"`)
2. Use `bench set-config` to update site_config with safe values before commit
3. Confirm no `.env` file with real secrets is inside the container at commit time
4. The receiving developer must supply their own `.env` and run `bench set-config` to restore working credentials
5. Document in the onboarding guide which config values need replacement

Alternatively: commit the container, then document that it contains dev credentials only valid for this specific demo environment (acceptable if the MariaDB password `123` and payment keys are already test/sandbox keys, which the hardcoded `--db-root-password=123` in `installer.py` suggests).

**Warning signs:**
- `site_config.json` inside container has `encryption_key`, `db_password`, payment gateway secrets before commit
- No pre-commit secrets scrub step in the sharing documentation
- GHCR image is public (or shared broadly) while containing real credentials

**Phase to address:** Docker packaging phase — secrets audit and scrub must happen before the first `docker commit` is attempted.

---

### Pitfall 3: Image Size Blowout — `docker commit` Includes the Full Bench Environment

**What goes wrong:**
The frappe-bench inside the devcontainer includes Python virtualenv (`frappe-bench/env/`), node_modules, compiled assets, log files, and pip/npm caches. A naive `docker commit` captures all of this. The resulting image can easily be 8-15 GB, making GHCR push/pull impractical — GHCR has no per-layer deduplication benefit here because these layers are new. The other developer faces a 10+ GB pull over a normal internet connection.

**Why it happens:**
`docker commit` snapshots the current writable layer. The dev container writable layer accumulated everything written since the container started: bench installation, pip installs, npm builds, Frappe asset compilation, log files, MariaDB data directory (if MariaDB runs inside the same container). Developers underestimate cumulative layer size.

**How to avoid:**
Before committing:
1. Run `bench clear-cache` and delete log files (`frappe-bench/logs/*.log`)
2. Remove pip cache: `pip cache purge` inside the container
3. Remove npm cache if applicable
4. Run `bench build` to ensure assets are compiled but remove intermediate artifacts
5. Check MariaDB data directory — if MariaDB runs in a separate container (which is standard for frappe_docker), its data lives in a Docker volume, not the bench container. Verify this architecture before assuming DB state is automatically included

Run `docker history <image>` after commit to inspect layer sizes before pushing. Target under 5 GB for practical sharing.

**Warning signs:**
- `docker images` shows committed image over 8 GB before push
- MariaDB data directory is inside the bench container (unexpected — frappe_docker normally separates services)
- `frappe-bench/logs/` has GB of log files accumulated during development

**Phase to address:** Docker packaging phase — establish a pre-commit cleanup checklist.

---

### Pitfall 4: MariaDB State Is in a Docker Volume, Not the Committed Container

**What goes wrong:**
The project uses frappe_docker's standard multi-container architecture (bench container + MariaDB container + Redis containers). The MariaDB data lives in a named Docker volume, not inside the bench container's filesystem. A `docker commit` on the bench container captures Python code and Frappe site configs — but NOT the database. The other developer pulls and starts the image, finds the site exists in `site_config.json` but MariaDB has no databases — `bench doctor` shows site DB is missing, and the site cannot start.

**Why it happens:**
Developers assume "commit the container = commit everything." In Docker Compose setups, each service is its own container. The bench container knows about the database via connection parameters, but the data itself lives in the MariaDB container's volume. `docker commit` only commits one container.

**How to avoid:**
The correct approach is a two-step share:
1. **Database dump:** `bench backup --with-files` to create a `.sql.gz` of the database, committed into the image or provided as a separate artifact alongside it
2. **MariaDB container commit or volume export:** Either `docker commit` the MariaDB container separately and push that image, OR export the volume (`docker run --rm -v db-volume:/data alpine tar czf - /data > db.tar.gz`) and include restore instructions
3. **Or consolidate:** Before committing, restore the database dump INTO the bench container by running MariaDB locally inside it (non-standard, adds complexity)

Recommended approach for this project: Commit both the bench container and the MariaDB container, push both to GHCR, and provide a `docker-compose.override.yml` that replaces the default MariaDB image with the committed one. Document this explicitly.

**Warning signs:**
- MariaDB runs in a separate container named `university-mariadb` or similar (check `docker ps`)
- The site directory `frappe-bench/sites/university.local/` exists in bench container but DB is external
- Testing the committed image in isolation shows DB connection errors

**Phase to address:** Docker packaging phase — architecture must be verified (single vs multi-container) before any sharing strategy is planned.

---

### Pitfall 5: Frappe Number Cards Require Correct DocType Permissions to Display Data

**What goes wrong:**
You build Number Cards that query student counts, fee totals, exam pass rates. They display correctly when you're logged in as Administrator. You share the environment; the other developer logs in as a user with the "University Admin" role — all Number Cards show `0` or an error. The dashboard appears broken, but the data is there. The issue is that Number Card queries run with the logged-in user's permissions and Frappe's permission query conditions filter out all data for that role.

**Why it happens:**
Frappe Number Cards execute the underlying Report or raw query using the current session user's permissions. If the DocType has `get_permission_query_conditions()` (which `student.py` does in this codebase), all queries are filtered by department, program, or role. An administrator sees all students; a department head sees only their department. If the target user role doesn't have `read` permission on the source DocType, the count returns 0 silently.

**How to avoid:**
1. Test every Number Card with a non-Administrator user who has the expected role ("University Admin", "University Faculty", etc.) before declaring it complete
2. For aggregate analytics that need full data visibility, ensure the analytics role has unrestricted `read` on source DocTypes, or use `frappe.db.sql()` with explicit `ignore_permissions=True` in a custom method (but document this consciously)
3. Add explicit role-to-doctype permission grants in fixtures, not just UI configuration

**Warning signs:**
- All dashboard testing done as Administrator only
- Number Cards showing `0` for users with non-admin roles
- No permission fixtures (Role Permission Manager entries) exported alongside dashboard fixtures

**Phase to address:** Dashboard build phase — include role-based testing as part of each dashboard's acceptance criteria.

---

### Pitfall 6: Dashboard Charts with `frappe.Chart` Fail When Report Has No Rows

**What goes wrong:**
Dashboard Charts linked to Script Reports or Query Reports work during development (demo data populated). After a fresh pull with the shared image, or after clearing test data, charts render as blank or throw a JavaScript error because `frappe.Chart` receives an empty dataset. The chart container shows a broken state rather than a graceful "No data" message.

**Why it happens:**
Frappe's Dashboard Chart renders by fetching report data and passing it to `frappe.Chart` (a wrapper around Chart.js). If the report returns zero rows, the chart data structure is `{labels: [], datasets: [{values: []}]}`. Some chart types (line, bar) handle this gracefully; others (pie, donut) throw errors because Chart.js requires at least one non-zero data point. Developers don't test the zero-data state during development because demo data is always present.

**How to avoid:**
1. For each custom Script Report feeding a chart, add a zero-data guard:
   ```python
   if not data:
       return {"result": [], "columns": columns}
   ```
2. Test each chart by temporarily filtering to a date range with no data
3. Prefer "Number Card + Chart" pairs where the Number Card shows 0 gracefully and the chart is hidden via Frappe's chart `hide_name_field` or conditional visibility

**Warning signs:**
- Charts tested only with demo data loaded
- Script Reports return raw lists without empty-data handling
- JavaScript console shows `Cannot read property of undefined` on dashboard load

**Phase to address:** Dashboard build phase — zero-data testing required before marking any chart complete.

---

### Pitfall 7: GHCR Image Architecture Mismatch (amd64 vs arm64)

**What goes wrong:**
You build and commit the image on WSL2/Linux x86_64 (amd64). The other developer is on Apple Silicon (arm64). They pull the image — Docker either refuses to run it or runs it via Rosetta/QEMU emulation. Frappe's gunicorn workers and Python processes run 5-10x slower under emulation, making the shared dev environment nearly unusable.

**Why it happens:**
`docker commit` produces an image for the current host architecture. GHCR tags the image with the architecture of the host that pushed it. Unless the image is built with `--platform linux/amd64,linux/arm64` (multi-arch), it only runs natively on the matching architecture.

**How to avoid:**
1. Confirm the other developer's platform (x86_64 or arm64) before pushing
2. If arm64 is needed, the commit approach won't work for multi-arch — you'd need to rebuild natively on arm64 or use QEMU cross-compilation
3. For this project (dev share between two known developers), document the architecture requirement prominently in the onboarding guide: "Requires x86_64 / amd64 host (WSL2, Linux, or Intel Mac)"
4. If the other developer is on Apple Silicon, the alternative is providing a database dump + fresh install script rather than a committed image

**Warning signs:**
- Other developer's machine type is unknown at the time of packaging
- No `--platform` flag consideration in the sharing plan

**Phase to address:** Docker packaging phase — confirm target platform before committing.

---

### Pitfall 8: Redis State Is Ephemeral — Cached Dashboard Data May Be Stale or Missing

**What goes wrong:**
Frappe caches permission trees, user settings, and sometimes report results in Redis. After `docker commit` and restart, the Redis cache container is either empty (new container) or contains stale keys from the original session. Dashboard widgets that rely on cached metadata may display stale data or require a `bench clear-cache` before they behave correctly.

**Why it happens:**
Redis data in the original session (user session tokens, DocType metadata cache, report caches) is either in a separate Redis container (not committed) or in a Redis container that was committed but whose keys reference session IDs that no longer exist. Frappe is designed to rebuild its cache on demand, but stale keys can cause confusing behavior — e.g., a cached permission set that references a deleted role.

**How to avoid:**
1. Run `bench clear-cache` inside the bench container immediately before `docker commit`
2. If Redis runs in a separate container (standard frappe_docker), acknowledge that Redis state is intentionally NOT preserved — this is correct behavior, Frappe will rebuild
3. Document in onboarding: "After first pull and start, run `bench clear-cache` inside the bench container before accessing the site"

**Warning signs:**
- Login page shows errors about invalid sessions after starting the shared image
- Dashboard loads show permission errors that disappear after `bench clear-cache`
- Redis container is part of the committed snapshot with active session keys

**Phase to address:** Docker packaging phase — add `bench clear-cache` to the pre-commit checklist.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Build dashboards only via UI, skip fixture export | Faster to build | Dashboards lost on reinstall; not in source control; cannot be reviewed in PRs | Never — always export fixtures |
| Use `docker commit` without secrets scrub | Fastest sharing path | Credentials baked into image layers; rotation requires new image | Only if all credentials are provably dev-only test values (e.g., Razorpay sandbox keys, DB password `123`) |
| Build all 21 module dashboards in one pass | Covers all modules quickly | No incremental testing; one broken chart blocks the batch; difficult to bisect | Never — build and test in module batches |
| Query raw SQL in Script Reports for dashboard charts | Full control, avoids Frappe ORM limits | Bypasses Frappe permission system; SQL injection risk if filters not sanitized (already flagged in CONCERNS.md) | Only for aggregate read-only queries with no user-supplied filters |
| Skip zero-data testing during dashboard build | Faster iteration | Charts break when data is filtered or demo data is cleared | Never — zero-data is a first-class state |
| Commit MariaDB container without running `mysqlcheck` | Preserves exact DB state | Corrupt tables silently included; other developer gets broken DB | Never — run integrity check before commit |

---

## Integration Gotchas

Common mistakes when connecting Frappe dashboards to existing data and when connecting the shared image to the developer's environment.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Frappe Dashboard → Script Report | Chart's `report_name` references a report in a different app (education, erpnext) that the other developer's image doesn't have at the right version | Always verify report exists in `university_erp` fixtures or is from a bundled app; test after fresh install |
| Number Card → Custom DocType | Number Card counts a DocType that exists in `university_erp` but is empty in the shared image (no demo data) | Either include demo data in the committed image (already planned) or add "N/A - no demo data" note in Number Card label |
| Dashboard → Workspace | Workspaces link to Dashboard by name; if the Dashboard name changes (renamed via UI), the Workspace shortcut silently shows a blank page | Use stable, slug-safe names for Dashboard DocType names; don't rename after linking |
| GHCR image → developer's Docker network | The committed image's internal hostnames (`mariadb`, `redis-cache`) are baked into `site_config.json`; if the other developer uses different Docker Compose service names, connections fail | Document exact service names required in `docker-compose.yml`; provide a ready-to-use compose file |
| Shared image → Payment gateway | Razorpay/PayU credentials in `site_config.json` are dev environment sandbox keys; the other developer may try to use them, find transactions don't work, and conclude the integration is broken | Explicitly mark credentials as "SANDBOX — for demo data browsing only" in onboarding docs |
| Scheduled tasks → Fee reminders | After starting the shared image, scheduled tasks immediately run (fee reminders, CGPA updates) against the demo data, sending emails/WhatsApp messages if SMTP/WhatsApp is configured | Disable notification integrations in `site_config.json` before committing; document how to re-enable |

---

## Performance Traps

Patterns that work with demo data but degrade with real university data.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Number Card uses `frappe.db.count()` on large table without filters | Card refresh takes 3-5 seconds; dashboard feels sluggish | Add date range or academic year filter to every count; use indexed fields in WHERE clause | >50,000 Student records or >500,000 Fee records |
| Dashboard Chart fetches full dataset, groups in Python | Chart data correct but API response is slow; browser hangs on render | Push aggregation to SQL (GROUP BY in Script Report query); never fetch all rows and sum in Python | >10,000 rows in source table |
| Dashboard auto-refresh set to every 60 seconds on 10+ charts | 10+ simultaneous API calls every minute; bench worker queue backs up | Disable auto-refresh for analytics dashboards; use manual refresh or longer intervals (1 hour) | Any number of concurrent users using the dashboard |
| Script Report uses `frappe.get_list()` with no `limit` | Report returns all records; page freezes | Always set `limit=500` or pagination in `frappe.get_list()` calls in Script Reports | >1,000 rows in result |
| Frappe Report Builder (Query Report) fetches linked document names via child table joins | Query is slow due to unindexed joins on custom fields | Use raw SQL with explicit JOINs on primary keys; add custom field indexes via DocType's `search_fields` | >20,000 linked child table rows |

---

## Security Mistakes

Domain-specific security issues for this project.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Committing image with `encryption_key` from `site_config.json` | Frappe's encryption key decrypts all encrypted fields in the DB (payment gateway secrets, API keys); anyone with image and DB dump can decrypt all secrets | Rotate encryption key before committing, or replace with a fresh key and re-encrypt (complex — simpler to scrub all credential fields) |
| Dashboard Number Card uses `frappe.whitelist()` method that bypasses `get_permission_query_conditions()` | Admin can see all students; restricted role user triggers the same count and also sees all students (data leak) | Never use `ignore_permissions=True` in dashboard data methods; test each card with restricted user |
| Shared image contains hardcoded student ID `EDU-STU-2026-00002` in scripts (from CONCERNS.md) | Low risk for dev share, but real student IDs in demo data could be PII if real names/emails used | Confirm all demo data uses fictional names/emails; strip real PII before commit |
| GHCR package visibility set to public for ease of sharing | Image (with DB contents) is publicly downloadable worldwide | Keep GHCR package visibility as `private`; add the other developer as a package collaborator explicitly |
| Payment gateway webhooks remain active in dev environment share | If Razorpay sandbox sends a webhook to `university.local`, and the shared environment processes it, it could corrupt payment state | Disable webhook processing in `site_config.json` or configure Razorpay sandbox to point to a different URL before committing |

---

## UX Pitfalls

User experience issues specific to Frappe Desk dashboards.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| All 21 module dashboards added to a single Workspace | Workspace becomes a scroll-of-death; users can't find anything | Create one Workspace per module cluster (Academics, Finance, Examinations, etc.); link dashboards via Workspace shortcuts |
| Number Card labels use internal field names ("custom_cgpa", "enrollment_no") | Admin users read technical names, not meaningful labels | Use human-readable labels: "Average CGPA", "Enrolled Students"; always set the `label` field explicitly |
| Dashboard charts have no title or context | User sees chart data but doesn't know what timeframe or filters are active | Set chart `timespan` and `time_interval` explicitly; add `filters_json` with academic year pre-set |
| KPI cards show raw database IDs in count (e.g., counting FK references) | Number shows 847 but user doesn't know "847 what?" | Add unit labels to Number Cards ("847 Students", "₹2.4L Collected") using the `label` field |
| Dashboard not linked from module Workspace | Users must search for dashboards by name | Add Dashboard shortcut tile to each module's Workspace; test navigation from Workspace to Dashboard and back |

---

## "Looks Done But Isn't" Checklist

Things that appear complete in the devcontainer but are missing critical pieces for the shared environment.

- [ ] **Dashboard fixtures exported:** Verify `university_erp/fixtures/` contains `Dashboard.json`, `Number Card.json`, `Dashboard Chart.json` — not just UI entries in the DB
- [ ] **Role permissions fixtures exported:** Verify that role-based access to dashboard DocTypes is in `Role Permission Manager` fixtures — not just set via UI
- [ ] **MariaDB state committed separately:** Confirm the MariaDB container (or a DB dump) is included in the sharing artifact — not just the bench container
- [ ] **Redis cleared before commit:** Verify `bench clear-cache` was run immediately before `docker commit`; no stale session keys in image
- [ ] **Secrets scrubbed or documented:** Verify `site_config.json` credentials are dev/sandbox values with clear labels, or have been scrubbed to placeholders
- [ ] **Scheduled tasks safe to run:** Verify SMTP and WhatsApp notification credentials are disabled/placeholder so the other developer doesn't accidentally send real messages on startup
- [ ] **Zero-data chart testing done:** Verify each Dashboard Chart was tested with an empty date range — no JavaScript errors in browser console
- [ ] **Non-Administrator role testing done:** Verify each Number Card and Dashboard Chart was viewed as "University Admin" role user, not just Administrator
- [ ] **Workspace shortcuts linked:** Verify each module Workspace has a shortcut to its Dashboard — not just the Dashboard existing in isolation
- [ ] **Image size checked:** Verify committed image is under 6 GB total before pushing to GHCR (`docker images` after commit)
- [ ] **Onboarding document written:** Verify pull-and-start instructions exist, including: start order (MariaDB first, then bench), `bench clear-cache` step, credential substitution steps

---

## Recovery Strategies

When pitfalls occur despite prevention.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Dashboards not exported as fixtures | MEDIUM | `bench export-fixtures --app university_erp`; commit JSON files; add fixture DocTypes to `hooks.py`; re-test after `bench install-app` on clean instance |
| Secrets committed to GHCR image | HIGH | Delete GHCR package version immediately; rotate all committed credentials (MariaDB password, Razorpay keys, encryption_key); re-scrub and re-commit; notify the other developer to pull the new image |
| MariaDB not included in share | HIGH | Take `bench backup --with-files` from source; send dump file separately; provide restore instructions (`bench restore <backup.sql.gz>`) |
| Image too large to push (>10 GB) | MEDIUM | Clean up inside running container (logs, caches, pip cache), re-commit; OR provide DB dump separately and trim image to code+config only |
| Architecture mismatch (amd64 vs arm64) | HIGH | No quick fix for committed image; provide DB dump + fresh install script as fallback; document platform requirement prominently |
| Number Cards show 0 for non-admin users | LOW | Check DocType permissions for the queried DocType; add `read` permission for the target role via Role Permission Manager; export updated permission fixtures |
| Charts break on empty data | LOW | Add empty-data guard to Script Report (`if not data: return`); redeploy via `bench migrate` |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Dashboard fixtures not exported | Dashboard build phase (every batch) | `bench install-app university_erp` on a clean container — dashboards appear without DB |
| Secrets in committed image | Docker packaging phase (pre-commit checklist) | `docker run <image> cat /workspace/frappe-bench/sites/university.local/site_config.json` — no real credentials visible |
| Image size blowout | Docker packaging phase (pre-commit cleanup) | `docker images` shows committed image under 6 GB |
| MariaDB state not included | Docker packaging phase (architecture audit) | Pull image on fresh machine, start containers — site loads with demo data |
| Number Cards broken for non-admin | Dashboard build phase (acceptance criteria) | Log in as "University Admin" role user — all cards show expected non-zero values |
| Charts break on empty data | Dashboard build phase (zero-data testing) | Filter chart to a future academic year with no data — graceful empty state displayed |
| GHCR architecture mismatch | Docker packaging phase (pre-push) | Confirm target developer's platform; `docker inspect <image> | grep Architecture` matches |
| Redis stale state | Docker packaging phase (pre-commit checklist) | Start shared image cold — no session errors, site loads cleanly |
| Scheduled tasks send real notifications | Docker packaging phase (config audit) | Check `site_config.json` for SMTP/WhatsApp credentials — all set to placeholders |
| Workspace shortcuts missing | Dashboard build phase (final review) | Navigate from each module Workspace — shortcut to dashboard present and working |

---

## Sources

- Training data: Frappe v15 Dashboard, Number Card, Dashboard Chart DocType behavior — MEDIUM confidence (knowledge cutoff August 2025; Frappe v15 is well-established)
- Training data: Docker `docker commit` behavior, layer mechanics, multi-container volume architecture — HIGH confidence (stable Docker internals)
- Training data: GHCR image architecture (amd64/arm64) constraints — HIGH confidence
- Project context: `.planning/codebase/CONCERNS.md` — hardcoded credentials, silent exceptions, permission model — HIGH confidence (direct codebase analysis)
- Project context: `.planning/codebase/ARCHITECTURE.md` — multi-container architecture, Redis/MariaDB separation — HIGH confidence (direct codebase analysis)
- Project context: `.planning/codebase/INTEGRATIONS.md` — secrets in `site_config.json`, scheduled task configuration — HIGH confidence (direct codebase analysis)
- Training data: Frappe permission system (`get_permission_query_conditions`) interaction with Dashboard queries — MEDIUM confidence (verify with Frappe v15 docs)
- Training data: `frappe.Chart` zero-data behavior — MEDIUM confidence (verify by testing during dashboard build phase)

**Flags for live verification:**
- Confirm exact `fixtures` export syntax for Dashboard/Number Card in Frappe v15 (syntax may have changed from v14)
- Confirm whether `bench export-fixtures` respects `filters` in `hooks.py` in Frappe v15 or requires explicit `--doctype` flags
- Verify MariaDB container name in the actual running `docker ps` output before planning the two-container commit strategy

---

*Pitfalls research for: Frappe v15 University ERP Dashboards + Docker devcontainer sharing via GHCR*
*Researched: 2026-03-17*
