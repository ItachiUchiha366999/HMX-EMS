# Phase 1: Docker Sharing - Research

**Researched:** 2026-03-17
**Domain:** Frappe v15 production Docker image build + GHCR push + MariaDB backup/restore + onboarding guide
**Confidence:** HIGH — all findings verified directly from the running bench, existing Containerfiles, compose files, and MariaDB backup artifacts in the repository.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Sharing Strategy:**
- The frappe container uses a bind mount (`..:/workspace:cached`) — `docker commit` of the frappe container will NOT include the code at `/workspace`
- MariaDB data lives in a named Docker volume (`mariadb-data`) — `docker commit` of the mariadb container will NOT include the database
- Redis containers are ephemeral (no persistent data) — can be pulled fresh from `docker.io/redis:alpine`
- Strategy must be: Build a custom production Docker image (using frappe_docker production Containerfile patterns) that bakes code + site config into the image, PLUS a database backup that gets restored on first run
- Git repo delivers: source code, production Dockerfiles, compose files, DB backup, onboarding guide

**What to Include:**
- Custom production image built from `frappe/bench` base with university_erp app installed, assets built, and site configured
- MariaDB database backup (`bench backup`) committed to repo or hosted as release artifact — restored by first-run entrypoint
- Redis: Pull fresh `redis:alpine` — no custom image needed (ephemeral cache/queue)
- Nginx/reverse proxy: Production compose should include nginx for proper routing (not just `bench serve` on port 8000)
- Site config: Template `site_config.json` with placeholders for production credentials

**Secrets Handling:**
- All real credentials scrubbed before sharing
- `site_config.json` templated with environment variable references
- MariaDB root password changed from hardcoded `123` to env var `${MYSQL_ROOT_PASSWORD}`
- Razorpay/PayU keys, encryption_key — replaced with placeholder values
- `.env.example` provided with all required variables documented

**GHCR Setup:**
- Push production image to `ghcr.io/{org}/university-erp:latest` and `ghcr.io/{org}/university-erp:{version-tag}`
- GHCR authentication: `docker login ghcr.io` with GitHub PAT
- Image visibility: private (production system)
- Tag convention: `v1.0.0` for initial release, `latest` for convenience

**Production Compose (`docker-compose.prod.yml`):**
- Custom university-erp image (from GHCR)
- MariaDB 11.8 with persistent volume
- Redis cache + queue (fresh alpine images)
- Nginx reverse proxy
- Environment variables from `.env` file
- Health checks on all services
- Restart policies (`unless-stopped`)
- Named volumes for data persistence

**Onboarding Guide:**
- Full production deployment guide covering prerequisites, pull + run, DB restore, bench migrate, admin login, SSL/TLS guidance, backup/restore procedures, project structure overview

### Claude's Discretion
- Exact Dockerfile layering and multi-stage build optimization
- Nginx configuration details
- Health check endpoints and intervals
- Log rotation setup

### Deferred Ideas (OUT OF SCOPE)
- Multi-architecture images (amd64 + arm64) — v2 requirement (DOCK-V2-01)
- CI/CD pipeline for automated builds — v2 requirement (DOCK-V2-02)
- SSL/TLS certificate automation — mention in guide but don't implement
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DOCK-01 | Docker container architecture audited (service names, container names, volume bindings documented from `docker ps` / `docker inspect`) | Devcontainer compose read; ems-production compose read; service names and volumes documented below |
| DOCK-02 | Pre-commit cleanup performed (bench clear-cache, delete logs, pip cache purge, compiled .pyc cleanup) | Pre-build cleanup sequence documented in Pitfalls section and Architecture Patterns |
| DOCK-03 | Secrets scrubbed from site_config.json (replace real credentials with placeholder/sandbox values) | site_config.json structure verified: contains db_name, db_password, host_name, domains — all must be templated |
| DOCK-04 | Bench container committed and tagged as Docker image | Superseded: production image built via Containerfile, not docker commit; ems-production/Containerfile is the template |
| DOCK-05 | MariaDB container committed and tagged or database backup embedded | bench backup files confirmed to exist at sites/university.local/private/backups/; 1.3MB gz dump verified |
| DOCK-06 | Both images pushed to GitHub Container Registry (ghcr.io) | GHCR authentication + push pattern documented; image naming convention confirmed |
| DOCK-07 | docker-compose.share.yml created pointing to GHCR images for the receiving developer | Compose pattern derived from ems-production/docker-compose.yml (already production-pattern compliant) |
| DOCK-08 | Developer onboarding guide written with pull + run instructions, credential setup, first-start checklist, project structure overview | All content areas researched and documented |
</phase_requirements>

---

## Summary

This phase produces a production-ready Docker packaging of the University ERP environment so another developer can pull from GHCR, run `docker compose up`, and have the complete ERP stack running with demo data. The critical architectural insight is that the devcontainer uses a bind mount for the frappe workspace (`..:/workspace:cached`) — this means `docker commit` is the wrong approach. Instead, a proper production image must be built using a Containerfile that clones/copies the source code into the image, compiles assets, and bakes the bench into a self-contained image.

**A production Containerfile already exists at `/workspace/development/ems-production/Containerfile`.** This is a custom adaptation of the frappe_docker production Containerfile pattern, extended to copy the `university_erp` app directly from source (rather than git-cloning it). The production compose at `ems-production/docker-compose.yml` demonstrates the full 8-service production architecture (configurator, backend, frontend/nginx, websocket, queue-short, queue-long, scheduler, mariadb, redis). This existing work is the direct template for Phase 1.

The database is handled via `bench backup` — a verified 1.3MB gzipped SQL dump already exists at `sites/university.local/private/backups/20260312_185343-university_local-database.sql.gz`. The first-run entrypoint needs to restore this dump into a fresh MariaDB container. The apps stack is: frappe v15.94.0 + erpnext v15.93.1 + hrms v15.54.2 + education (latest version-15 commit) + university_erp v0.0.1.

**Primary recommendation:** Use `ems-production/Containerfile` as the starting point, parameterize it via build args and env vars, produce one image (`ghcr.io/{org}/university-erp:{tag}`), include a DB backup as a release artifact or baked into the image, and adapt `ems-production/docker-compose.yml` into `docker-compose.prod.yml` with the receiving developer's env in mind.

---

## Critical Architecture Discovery

### The Existing Production Containerfile

`/workspace/development/ems-production/Containerfile` already solves the core problem:

```
FROM python:3.11.6-slim-bookworm AS base
  → installs nginx, mariadb-client, Node 20.19.2, wkhtmltopdf, wait-for-it

FROM base AS builder
  → bench init with frappe branch version-15
  → git-clones erpnext, hrms, education via APPS_JSON_BASE64 build arg
  → COPY --chown=frappe:frappe university_erp /home/frappe/frappe-bench/apps/university_erp
  → pip install -e apps/university_erp
  → removes .git directories

FROM base AS backend
  → COPY --from=builder bench installation
  → VOLUME sites, sites/assets, logs
  → CMD: gunicorn on 0.0.0.0:8000
```

This Containerfile copies `university_erp` app from the build context (not from git), which is exactly what is needed — the source cannot be cloned from a public repo. The same image handles: gunicorn (backend), nginx (frontend), socketio node server (websocket), bench workers, and bench schedule.

### The Existing Production Compose

`/workspace/development/ems-production/docker-compose.yml` provides the complete 8-service production template:

| Service | Image | Role |
|---------|-------|------|
| ems-configurator | ems-university:v1 | One-shot: sets common_site_config then exits |
| ems-backend | ems-university:v1 | Gunicorn WSGI server |
| ems-frontend | ems-university:v1 | Nginx reverse proxy via nginx-entrypoint.sh |
| ems-websocket | ems-university:v1 | Node socketio.js server |
| ems-queue-short | ems-university:v1 | `bench worker --queue short,default` |
| ems-queue-long | ems-university:v1 | `bench worker --queue long,default,short` |
| ems-scheduler | ems-university:v1 | `bench schedule` |
| ems-mariadb | mariadb:10.6 | Database (NOTE: upgrade to 11.8 per decision) |
| ems-redis-cache | redis:6.2-alpine | Cache |
| ems-redis-queue | redis:6.2-alpine | Queue |

The existing compose uses named volumes (`ems-sites`, `ems-db-data`, `ems-logs`) and an isolated network (`ems-network`). It also connects to an external proxy network (`hanumatrix-erp_proxy`) for nginx-proxy-based SSL — this external network dependency must be removed or made optional in the shared version.

### What the Shared Compose Must Add vs Existing

| Gap | Resolution |
|-----|-----------|
| No DB restore mechanism on first run | Add init container or entrypoint script that checks if site DB exists and runs `bench restore` |
| External network dependency (`hanumatrix-erp_proxy`) | Remove from shared compose; add port `8080:8080` directly on frontend for standalone access |
| Hardcoded `MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}` (no default) | Document in `.env.example` |
| MariaDB version is 10.6 | CONTEXT.md specifies 11.8; update in shared compose |
| No SITE_DOMAIN default | Must be configurable; default to `university.local` |
| No `.env.example` | Create with all required vars |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| frappe | v15.94.0 | Core framework | Running in dev bench, locked |
| erpnext | v15.93.1 | Business modules | Running in dev bench, locked |
| hrms | v15.54.2 | HR management | Running in dev bench, locked |
| education | latest version-15 | Education DocTypes | Running in dev bench, locked |
| university_erp | 0.0.1 | Custom university app | The product being shared |
| python | 3.11.6 | Runtime | Matches existing Containerfile |
| Node.js | 20.19.2 | Asset compilation + socketio | Matches existing Containerfile |
| MariaDB | 11.8 | Database | Per CONTEXT.md locked decision (Containerfile currently uses 10.6 — must be updated) |
| Redis | alpine | Cache + queue | Standard frappe_docker pattern, ephemeral |
| Nginx | bundled in image | Reverse proxy | Bundled via frappe_docker pattern; `nginx-entrypoint.sh` handles config |
| gunicorn | bundled in frappe env | WSGI server | Standard Frappe production pattern |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| wkhtmltopdf | 0.12.6.1-3 | PDF generation | Installed in base image layer; required for fee receipts, reports |
| wait-for-it | bundled | Health check dependency ordering | Used in compose `depends_on` service_healthy conditions |
| restic | bundled | Backup utility | Available in image; can be used with backup-cron override if needed |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Single custom image for all roles | Separate images per role | Single image is simpler for small teams; multi-image allows separate scaling in v2 |
| MariaDB fresh + bench restore on first run | Committed MariaDB container | Fresh MariaDB + restore is production-correct and avoids large second image; committed MariaDB is simpler but harder to upgrade |
| DB backup in image layer | DB backup as GitHub Release asset | In-image backup has no separate download step; Release asset is smaller image but adds auth step; either works for private repo |

**Installation (build command):**
```bash
# From /workspace/development/
docker build \
  --build-arg FRAPPE_BRANCH=version-15 \
  --build-arg APPS_JSON_BASE64=$(base64 -w 0 ems-production/apps.json) \
  -t ghcr.io/{org}/university-erp:v1.0.0 \
  -f ems-production/Containerfile \
  .
```

---

## Architecture Patterns

### Recommended Production Structure

```
university-erp-docker/               # or inside university_erp app repo
├── Containerfile                    # Production image (adapted from ems-production/Containerfile)
├── apps.json                        # Apps to git-clone: erpnext, hrms, education
├── docker-compose.prod.yml          # Receiving developer's compose file
├── .env.example                     # All required env vars with documentation
├── db-backup/
│   └── university_local.sql.gz      # DB dump (bench backup output, committed or as Release asset)
├── scripts/
│   └── restore-on-first-run.sh      # Checks if site DB exists; runs bench restore if not
└── SETUP.md                         # Developer onboarding guide
```

### Pattern 1: Multi-Stage Containerfile Build

**What:** Two-stage build: `builder` stage installs build deps + compiles apps; `backend` stage copies compiled bench without build tools.

**When to use:** Always — standard frappe_docker pattern; reduces final image size by excluding gcc, libmariadb-dev, etc.

**Key adaptation for university_erp (from verified ems-production/Containerfile):**
```dockerfile
# Source: /workspace/development/ems-production/Containerfile

# Stage: builder
ARG APPS_JSON_BASE64
RUN if [ -n "${APPS_JSON_BASE64}" ]; then \
    mkdir /opt/frappe && echo "${APPS_JSON_BASE64}" | base64 -d > /opt/frappe/apps.json; \
  fi

RUN bench init ${APP_INSTALL_ARGS} \
    --frappe-branch=${FRAPPE_BRANCH} \
    --frappe-path=${FRAPPE_PATH} \
    --no-procfile --no-backups \
    --skip-redis-config-generation \
    /home/frappe/frappe-bench

# Copy university_erp directly (not from git — private app)
COPY --chown=frappe:frappe university_erp /home/frappe/frappe-bench/apps/university_erp
RUN cd /home/frappe/frappe-bench && \
  /home/frappe/frappe-bench/env/bin/pip install -e apps/university_erp && \
  echo "{}" > sites/common_site_config.json && \
  find apps -mindepth 1 -path "*/.git" | xargs rm -fr

# Stage: backend (final image)
COPY --from=builder --chown=frappe:frappe /home/frappe/frappe-bench /home/frappe/frappe-bench
VOLUME ["/home/frappe/frappe-bench/sites", "/home/frappe/frappe-bench/sites/assets", ...]
CMD ["/home/frappe/frappe-bench/env/bin/gunicorn", ...]
```

**Critical notes:**
- The `COPY university_erp` instruction uses the `development/` directory as build context. The Containerfile must be built from `/workspace/development/` with `--file ems-production/Containerfile` or the path adjusted.
- `find apps -mindepth 1 -path "*/.git" | xargs rm -fr` strips git history — keeps image smaller.
- `bench build --production` must be added to the builder stage after app installation to compile frontend assets into the sites/assets volume path.

### Pattern 2: Configurator Service for Dynamic Site Config

**What:** A one-shot service runs `bench set-config` commands to inject runtime values (DB host, Redis hosts, socket port) before the backend starts.

**When to use:** Always in production — allows the same image to run in different environments without baking connection strings.

**Verified pattern (from ems-production/docker-compose.yml):**
```yaml
# Source: /workspace/development/ems-production/docker-compose.yml
ems-configurator:
  image: university-erp:v1.0.0
  restart: "no"
  entrypoint: ["bash", "-c"]
  command:
    - >
      ls -1 apps > sites/apps.txt;
      bench set-config -g db_host $$DB_HOST;
      bench set-config -gp db_port $$DB_PORT;
      bench set-config -g redis_cache "redis://$$REDIS_CACHE";
      bench set-config -g redis_queue "redis://$$REDIS_QUEUE";
      bench set-config -g redis_socketio "redis://$$REDIS_QUEUE";
      bench set-config -gp socketio_port 9000;
  volumes:
    - sites:/home/frappe/frappe-bench/sites
  depends_on:
    db:
      condition: service_healthy
```

### Pattern 3: DB Restore on First Run

**What:** A one-shot init container (or extended configurator command) detects whether the site database exists in MariaDB. If not, it runs `bench restore` from the backup file baked into the image.

**When to use:** Required — without this, the receiving developer has an empty MariaDB and no site.

**Implementation:**
```bash
# scripts/restore-on-first-run.sh
#!/bin/bash
set -e
SITE_NAME="${FRAPPE_SITE_NAME:-university.local}"
BACKUP_FILE="/home/frappe/frappe-bench/db-backup/university_local.sql.gz"

# Check if site DB already exists
DB_EXISTS=$(mysql -h "${DB_HOST}" -u root -p"${MYSQL_ROOT_PASSWORD}" \
  -e "SHOW DATABASES LIKE '${DB_NAME}';" 2>/dev/null | grep -c "${DB_NAME}" || true)

if [ "$DB_EXISTS" -eq 0 ] && [ -f "$BACKUP_FILE" ]; then
  echo "First run detected: restoring database from backup..."
  cd /home/frappe/frappe-bench
  bench restore "$BACKUP_FILE" \
    --mariadb-root-password "${MYSQL_ROOT_PASSWORD}" \
    --force
  bench migrate
  echo "Database restored and migrated."
fi
```

**Key constraint:** The backup file must be copied into the image (either `COPY db-backup/ /home/frappe/frappe-bench/db-backup/` in Containerfile, or mounted as a volume, or downloaded from GitHub Release). Baking it in simplifies the receiver's experience; the DB dump is 1.3MB compressed (confirmed from backups directory) which adds negligible image size.

### Pattern 4: Frontend Nginx via nginx-entrypoint.sh

**What:** The image uses `nginx-entrypoint.sh` to dynamically generate nginx config from environment variables using `envsubst`, then starts nginx in foreground.

**Verified template at:** `/workspace/resources/nginx-template.conf` — handles WebSocket upgrade for socket.io, X-Accel-Redirect for file downloads, gzip compression, security headers.

**Environment variables nginx uses:**
```
BACKEND=backend:8000
SOCKETIO=websocket:9000
FRAPPE_SITE_NAME_HEADER=$host  (or specific site name)
UPSTREAM_REAL_IP_ADDRESS=127.0.0.1
UPSTREAM_REAL_IP_HEADER=X-Forwarded-For
PROXY_READ_TIMEOUT=120
CLIENT_MAX_BODY_SIZE=50m
```

### Anti-Patterns to Avoid

- **Using `docker commit` on the devcontainer:** The bind mount `..:/workspace:cached` means the frappe source code lives on the host, not in the container FS. A committed container image will have an empty `/workspace`. Always build from Containerfile.
- **Leaving MariaDB root password as `123`:** The existing devcontainer uses `MYSQL_ROOT_PASSWORD: 123`. This must not appear in the production compose. Use `${MYSQL_ROOT_PASSWORD}` from `.env`.
- **Baking `site_config.json` credentials into the image:** The `VOLUME ["/home/frappe/frappe-bench/sites", ...]` declaration means the sites directory is a Docker volume — it is NOT included in the image layers. The configurator pattern writes `common_site_config.json` at startup from env vars. Site-level `site_config.json` is created by `bench new-site` or `bench restore`. This is correct.
- **Forgetting `bench build --production` in the Containerfile builder stage:** Without this, the frontend assets (Frappe desk JS/CSS) are not compiled into the image. The sites/assets volume will be empty and the UI will not load.
- **Not running `bench migrate` after restore:** The DB backup is from March 12, 2026. The app code may have schema changes since then. `bench migrate` must be called after restore to apply any pending schema migrations.
- **External network dependency in compose:** The existing `ems-production/docker-compose.yml` references `hanumatrix-erp_proxy` as an external network. This will fail for the receiving developer. The shared compose must be self-contained with direct port mapping.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Nginx config generation | Custom shell script with sed | `nginx-entrypoint.sh` + `envsubst` | Already implemented in repo at `resources/nginx-entrypoint.sh`; handles all edge cases |
| DB health check | Custom wait loop | `wait-for-it` + compose `condition: service_healthy` | `wait-for-it` already installed in base image; MariaDB healthcheck pattern verified in `overrides/compose.mariadb.yaml` |
| MariaDB charset/collation | Custom my.cnf | Command flags: `--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci` | Verified in both devcontainer and ems-production compose |
| Multi-service orchestration | Custom start script | Docker Compose `depends_on` with `service_completed_successfully` condition | Configurator pattern already in ems-production compose |
| Site configuration at startup | Manual `site_config.json` edit | `bench set-config -g ...` in configurator service | Standard frappe_docker pattern; avoids hardcoding values in image |
| Asset compilation | Manual webpack/rollup | `bench build --production` | Official bench command; handles all Frappe + ERPNext + university_erp assets |

**Key insight:** The `ems-production/` directory already contains a working production Containerfile and compose. The planner should build on this existing work, not create from scratch.

---

## Common Pitfalls

### Pitfall 1: Bind Mount Means Source Code Is NOT in the Committed Container

**What goes wrong:** Developer runs `docker commit <devcontainer_frappe>` expecting to capture the Frappe source code. The resulting image has an empty `/workspace/` because `..:/workspace:cached` is a bind mount — that path refers to the host filesystem, not a writable container layer.

**Why it happens:** `docker commit` only captures the container's writable layer on top of its base image. Bind-mounted paths bypass this entirely — data accessed via bind mount stays on the host.

**How to avoid:** Build from Containerfile (as locked in CONTEXT.md). The Containerfile copies the source explicitly via `COPY --chown=frappe:frappe university_erp /home/frappe/frappe-bench/apps/university_erp`.

**Warning signs:** Resulting image starts but Frappe reports `No module named university_erp`; `bench version` shows only frappe installed.

### Pitfall 2: MariaDB Named Volume Not in Image Layers

**What goes wrong:** Developer commits the MariaDB container hoping to capture the database. The database lives in the named volume `mariadb-data`, not in the container's writable layer. The committed image starts with an empty `/var/lib/mysql`.

**Why it happens:** Named volumes are managed by the Docker daemon on the host. They are external storage — `docker commit` only captures the union filesystem layers, not mounted volumes.

**How to avoid:** Use `bench backup --with-files` to produce a SQL dump, then restore it in the receiving environment. The backup already exists: `sites/university.local/private/backups/20260312_185343-university_local-database.sql.gz` (1.3MB compressed).

**Warning signs:** MariaDB container starts but shows no databases when listing with `SHOW DATABASES;`; bench reports DB connection failure because the `_df4394075d9a924d` database is missing.

### Pitfall 3: site_config.json Contains Real Credentials That Must Be Scrubbed

**What goes wrong:** The current `site_config.json` contains:
- `"db_password": "MEQEH6nrrzCmiP5Y"` — the actual MariaDB password
- `"db_name": "_df4394075d9a924d"` — internal database name
- `"host_name": "http://localhost:8000"` — dev-only URL

These get baked into the image if not scrubbed. The encryption key (if set) would allow decryption of all encrypted fields.

**How to avoid:** Before building the production image, run:
```bash
bench set-config -s university.local host_name "http://${FRAPPE_SITE_NAME}"
# Remove payment gateway keys from site_config before commit
# db_password will be re-set by bench restore
```

The configurator pattern sets `common_site_config.json` (DB host, Redis) but `site_config.json` is per-site and lives in the `sites` volume — it is NOT in the image. The `bench restore` creates it fresh. This means per-site secrets are NOT baked into the image. Verify this is the case before build.

**Warning signs:** `docker run --rm university-erp:v1.0.0 cat /home/frappe/frappe-bench/sites/university.local/site_config.json` returns real credentials — means a site dir was baked in.

### Pitfall 4: `bench build --production` Not Run During Image Build

**What goes wrong:** The backend gunicorn starts fine, but the Frappe desk UI shows a blank page or throws JS errors. The browser console shows 404s for `/assets/frappe/...` files.

**Why it happens:** `bench build` compiles all Frappe, ERPNext, and app-level JavaScript/CSS into the `sites/assets/` directory. This directory is declared as a `VOLUME` — if it was not built before the `VOLUME` declaration in the Containerfile, the volume starts empty.

**Critical ordering in Containerfile:**
```dockerfile
# In builder stage, AFTER pip install of all apps:
RUN cd /home/frappe/frappe-bench && \
    bench build --production && \
    # Then copy assets into a location that's inside the bench (not volume)
    # OR: remove the VOLUME declaration for assets and bake assets into image
```

**How to avoid:** Add `bench build --production` in the builder stage. Check the current `ems-production/Containerfile` — it does NOT include `bench build`. This is a gap that must be filled.

**Warning signs:** Frappe desk loads HTML shell but JS files 404; "Network Error" in browser dev tools for asset requests.

### Pitfall 5: `hanumatrix-erp_proxy` External Network Breaks Receiving Developer's Compose

**What goes wrong:** The receiving developer runs `docker compose -f docker-compose.prod.yml up`. Docker fails with: `network hanumatrix-erp_proxy declared as external, but could not be found`.

**Why it happens:** The existing `ems-production/docker-compose.yml` was built for a specific host that already has an nginx-proxy network running. The receiving developer's machine has no such network.

**How to avoid:** Remove the external network from the shared compose. Add direct port mapping:
```yaml
ems-frontend:
  ports:
    - "${HTTP_PUBLISH_PORT:-8080}:8080"  # Direct access without reverse proxy
```

For production with SSL, the onboarding guide can recommend Traefik via `overrides/compose.traefik-ssl.yaml` pattern, but the base compose must work standalone.

### Pitfall 6: Scheduled Tasks Attempt Email/WhatsApp on First Start

**What goes wrong:** The scheduler starts and `university_erp` has extensive daily scheduled tasks including `send_fee_reminders`, `send_library_overdue_notices`, `send_attendance_warnings`. If SMTP or WhatsApp credentials are set to real values, the receiving developer's instance sends emails to real students/staff from demo data.

**How to avoid:** Before building the image, set email/WhatsApp integration to disabled:
```bash
bench set-config -s university.local mail_server ""
bench set-config -s university.local disable_scheduler 0  # Keep scheduler on but...
# Ensure notification credentials are placeholder values in site_config.json
```

Document in onboarding guide: "By default, email sending is disabled. To enable: update `.env` with your SMTP settings."

### Pitfall 7: Architecture Mismatch (amd64 vs arm64)

**What goes wrong:** Image built on WSL2/Linux (x86_64/amd64). Receiving developer on Apple Silicon (arm64). Docker runs via Rosetta emulation — 5-10x slower. Frappe bench processes feel unresponsive.

**How to avoid:** Confirm receiving developer's platform before pushing. Document prominently in onboarding: "Requires x86_64/amd64 host (WSL2, Linux, Intel Mac). Apple Silicon support deferred to v2."

Multi-arch is DOCK-V2-01 and is out of scope for this phase.

---

## Code Examples

Verified patterns from the existing codebase:

### MariaDB Health Check (from overrides/compose.mariadb.yaml)
```yaml
# Source: /workspace/overrides/compose.mariadb.yaml
db:
  image: mariadb:11.8
  healthcheck:
    test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
    start_period: 5s
    interval: 5s
    timeout: 5s
    retries: 5
  restart: unless-stopped
  command:
    - --character-set-server=utf8mb4
    - --collation-server=utf8mb4_unicode_ci
    - --skip-character-set-client-handshake
    - --skip-innodb-read-only-compressed
  environment:
    MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-123}
    MARIADB_AUTO_UPGRADE: 1
  volumes:
    - db-data:/var/lib/mysql
```

### Configurator Pattern (from ems-production/docker-compose.yml)
```yaml
# Source: /workspace/development/ems-production/docker-compose.yml
configurator:
  image: university-erp:v1.0.0
  restart: "no"
  entrypoint: ["bash", "-c"]
  command:
    - >
      ls -1 apps > sites/apps.txt;
      bench set-config -g db_host $$DB_HOST;
      bench set-config -gp db_port $$DB_PORT;
      bench set-config -g redis_cache "redis://$$REDIS_CACHE";
      bench set-config -g redis_queue "redis://$$REDIS_QUEUE";
      bench set-config -g redis_socketio "redis://$$REDIS_QUEUE";
      bench set-config -gp socketio_port 9000;
  volumes:
    - sites:/home/frappe/frappe-bench/sites
  depends_on:
    db:
      condition: service_healthy
```

### Frontend Service with Nginx (from ems-production/docker-compose.yml)
```yaml
# Source: /workspace/development/ems-production/docker-compose.yml (adapted)
frontend:
  image: university-erp:v1.0.0
  restart: unless-stopped
  command: nginx-entrypoint.sh
  environment:
    BACKEND: backend:8000
    FRAPPE_SITE_NAME_HEADER: ${SITE_DOMAIN:-university.local}
    SOCKETIO: websocket:9000
    UPSTREAM_REAL_IP_ADDRESS: 172.18.0.0/16
    UPSTREAM_REAL_IP_HEADER: X-Forwarded-For
    UPSTREAM_REAL_IP_RECURSIVE: "off"
    PROXY_READ_TIMEOUT: "120"
    CLIENT_MAX_BODY_SIZE: 50m
  ports:
    - "${HTTP_PUBLISH_PORT:-8080}:8080"
  volumes:
    - sites:/home/frappe/frappe-bench/sites
  depends_on:
    - backend
    - websocket
```

### Containerfile Key Section (from ems-production/Containerfile)
```dockerfile
# Source: /workspace/development/ems-production/Containerfile

# === ADAPTATION NEEDED: add bench build after app install ===
FROM base AS builder

ARG APPS_JSON_BASE64
RUN if [ -n "${APPS_JSON_BASE64}" ]; then \
    mkdir /opt/frappe && echo "${APPS_JSON_BASE64}" | base64 -d > /opt/frappe/apps.json; \
  fi

ARG FRAPPE_BRANCH=version-15
ARG FRAPPE_PATH=https://github.com/frappe/frappe
RUN export APP_INSTALL_ARGS="" && \
  if [ -n "${APPS_JSON_BASE64}" ]; then \
    export APP_INSTALL_ARGS="--apps_path=/opt/frappe/apps.json"; \
  fi && \
  bench init ${APP_INSTALL_ARGS} \
    --frappe-branch=${FRAPPE_BRANCH} \
    --frappe-path=${FRAPPE_PATH} \
    --no-procfile --no-backups \
    --skip-redis-config-generation \
    /home/frappe/frappe-bench

COPY --chown=frappe:frappe university_erp /home/frappe/frappe-bench/apps/university_erp
RUN cd /home/frappe/frappe-bench && \
  /home/frappe/frappe-bench/env/bin/pip install -e apps/university_erp && \
  echo "{}" > sites/common_site_config.json && \
  find apps -mindepth 1 -path "*/.git" | xargs rm -fr

# === THIS LINE IS MISSING IN ems-production/Containerfile — MUST ADD ===
RUN cd /home/frappe/frappe-bench && \
  bench build --production
```

### .env.example Template
```bash
# Required
MYSQL_ROOT_PASSWORD=changeme-strong-password
DB_HOST=db
DB_PORT=3306
REDIS_CACHE=redis-cache:6379
REDIS_QUEUE=redis-queue:6379
SITE_DOMAIN=university.local

# Optional (defaults shown)
HTTP_PUBLISH_PORT=8080
PROXY_READ_TIMEOUT=120
CLIENT_MAX_BODY_SIZE=50m

# Email (disabled by default — set to enable outbound email)
MAIL_SERVER=
MAIL_PORT=
MAIL_USE_TLS=
MAIL_LOGIN=
MAIL_PASSWORD=

# Production secrets — generate fresh values
# ENCRYPTION_KEY is auto-generated by Frappe on new-site; do not set manually
```

### apps.json for builder stage (from ems-production/apps.json — verified)
```json
[
  { "url": "https://github.com/frappe/erpnext", "branch": "version-15" },
  { "url": "https://github.com/frappe/hrms",    "branch": "version-15" },
  { "url": "https://github.com/frappe/education", "branch": "version-15" }
]
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `docker commit` for sharing dev environments | Build from Containerfile + `bench backup` for data | Decision in CONTEXT.md | More reproducible; production-ready; handles bind mount correctly |
| Single mariadb container committed | Fresh MariaDB + `bench restore` from SQL dump | CONTEXT.md decision | Smaller total image; idiomatic production approach |
| `bench serve` on port 8000 | Gunicorn + Nginx frontend | Production best practice | Proper request handling, WebSocket support, file serving via X-Accel-Redirect |
| All-in-one monolith | Multi-service compose (backend + frontend + websocket + workers + scheduler) | frappe_docker pattern | Independent scaling; proper service isolation |

**Deprecated/outdated:**
- `docker commit` approach: The STACK.md research file documents `docker commit` as the "decision," but CONTEXT.md overrides this — that was the old approach. The bind mount architecture makes `docker commit` incorrect. The new approach is Containerfile build.
- MariaDB 10.6 in `ems-production/docker-compose.yml`: CONTEXT.md specifies 11.8. Must be updated.

---

## Open Questions

1. **Where should the DB backup be stored in the production image?**
   - What we know: The backup is 1.3MB compressed. The `VOLUME` declaration covers `sites/` and `logs/`, but not a custom `db-backup/` path.
   - What's unclear: Whether to `COPY` the backup into `/home/frappe/frappe-bench/db-backup/` (inside image) or mount it as an external volume or download from GitHub Release.
   - Recommendation: `COPY` into image at `/home/frappe/frappe-bench/db-backup/university_local.sql.gz`. The 1.3MB is negligible. Avoids external download step for receiving developer. The backup is demo data — not sensitive.

2. **What site name should the production deployment use?**
   - What we know: Dev site is `university.local`. CONTEXT.md says `SITE_DOMAIN` env var drives `FRAPPE_SITE_NAME_HEADER`.
   - What's unclear: Whether `bench restore` preserves the site name or allows renaming via `--site` flag.
   - Recommendation: Use `${FRAPPE_SITE_NAME:-university.local}` as default. `bench restore` can be targeted to a named site with `--site university.local`. Document that changing the site name requires additional `bench setup nginx` steps.

3. **Is `bench build --production` missing from ems-production/Containerfile?**
   - What we know: The Containerfile does not include a `bench build` command. The `VOLUME` declaration includes `sites/assets`. If assets are compiled after the VOLUME declaration, they go into the volume at runtime, not the image.
   - What's unclear: Whether the ems-production deployment works because assets are compiled separately or via a runtime step.
   - Recommendation: Add `bench build --production` to the builder stage BEFORE the `FROM base AS backend` switch. Verify assets appear in `/home/frappe/frappe-bench/sites/assets/` after image build with: `docker run --rm university-erp:v1.0.0 ls /home/frappe/frappe-bench/sites/assets/`.

4. **What is the GHCR org/username to use?**
   - What we know: Git remote `hmx` points to `https://github.com/ItachiUchiha366999/HMX-EMS.git`. The frappe_docker origin is `frappe/frappe_docker`.
   - What's unclear: Whether the university_erp app will be pushed to `ItachiUchiha366999`'s personal GHCR or an org.
   - Recommendation: Use `ghcr.io/ItachiUchiha366999/university-erp:v1.0.0` as a working default. The planner should leave `{GHCR_USERNAME}` as a placeholder that the implementer fills in from `gh auth status`.

---

## Validation Architecture

No test framework is detected for this phase. DOCK-01 through DOCK-08 are infrastructure/artifact requirements, not unit-testable code. Validation is manual verification against a checklist.

### Phase Requirements Validation Map

| Req ID | Behavior | Test Type | Verification Method |
|--------|----------|-----------|---------------------|
| DOCK-01 | Architecture documented | Manual | Compare `docker ps` output against documentation |
| DOCK-02 | Pre-build cleanup done | Manual | Verify no log files >1MB; `bench clear-cache` completes without error |
| DOCK-03 | Secrets scrubbed | Manual | `grep -r "MEQEH6nrrzCmiP5Y" ./` returns no results in committed files |
| DOCK-04 | Production image built | Smoke | `docker run --rm university-erp:v1.0.0 bench version` succeeds, shows all 5 apps |
| DOCK-05 | DB backup exists and is valid | Manual | `zcat db-backup/university_local.sql.gz | head -20` shows valid SQL |
| DOCK-06 | Images pushed to GHCR | Manual | `docker pull ghcr.io/{org}/university-erp:v1.0.0` succeeds from a clean machine |
| DOCK-07 | docker-compose.prod.yml works | Smoke | `docker compose -f docker-compose.prod.yml up -d && sleep 120 && curl localhost:8080` returns 200 |
| DOCK-08 | Onboarding guide complete | Manual | Walk through guide on a clean machine; reach Frappe login page |

### Wave 0 Gaps

- [ ] No automated test exists. All verification is manual/smoke.
- [ ] Consider adding a `validate.sh` script that performs the smoke test checks above as part of the delivery.

---

## Sources

### Primary (HIGH confidence)
- Direct read: `/workspace/.devcontainer/docker-compose.yml` — current devcontainer architecture, 4 services, bind mount confirmed, MariaDB named volume confirmed
- Direct read: `/workspace/development/ems-production/Containerfile` — existing production Containerfile; direct template for Phase 1 work
- Direct read: `/workspace/development/ems-production/docker-compose.yml` — existing 8-service production compose; direct template for docker-compose.prod.yml
- Direct read: `/workspace/development/ems-production/apps.json` — apps to git-clone: erpnext, hrms, education
- Direct read: `/workspace/images/production/Containerfile` — upstream frappe_docker reference Containerfile
- Direct read: `/workspace/compose.yaml` — frappe_docker reference production compose
- Direct read: `/workspace/overrides/compose.mariadb.yaml` — MariaDB health check pattern verified
- Direct read: `/workspace/resources/nginx-template.conf` — nginx config template for frontend service
- Direct read: `/workspace/resources/nginx-entrypoint.sh` — nginx startup script using envsubst
- Direct read: `/workspace/example.env` — frappe_docker env var reference
- Direct read: `/workspace/development/frappe-bench/sites/common_site_config.json` — confirmed dev Redis/DB host config
- Direct read: `/workspace/development/frappe-bench/sites/university.local/site_config.json` — secrets structure confirmed (db_name, db_password, host_name, domains)
- Direct check: `/workspace/development/frappe-bench/sites/university.local/private/backups/` — confirmed backup exists: `20260312_185343-university_local-database.sql.gz`, 1.3MB

### Secondary (MEDIUM confidence)
- Git tag: frappe v15.94.0, erpnext v15.93.1, hrms v15.54.2 — from `git describe --tags --abbrev=0` in each app directory
- Git remote: `https://github.com/ItachiUchiha366999/HMX-EMS.git` — candidate GHCR org for `university-erp` image
- Python 3.11.6, Node 20.19.2 — confirmed from `python3 --version` and `node --version` in running environment

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions verified from running bench
- Architecture patterns: HIGH — existing ems-production Containerfile and compose verified directly
- Pitfalls: HIGH — majority of pitfalls verified directly (bind mount behavior, named volume behavior, external network dependency)
- Build gap (bench build missing): MEDIUM — inferred from Containerfile analysis; must be confirmed during implementation by testing image build

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (30 days) — Frappe v15 patch versions may increment but architecture is stable
