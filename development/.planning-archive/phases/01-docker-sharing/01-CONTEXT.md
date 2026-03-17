# Phase 1: Docker Sharing - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Package the complete working University ERP environment for **production deployment** by another developer. This includes the running database with demo data, all source code, site configuration, and a compose setup that starts the full ERP stack. The receiving developer should be able to pull and run the complete system without rebuilding from scratch.

**Scope change from initial plan:** User clarified this is for **production**, not just a dev demo. The sharing approach must produce a production-ready deployment, not just a Docker snapshot for development.

</domain>

<decisions>
## Implementation Decisions

### Sharing Strategy
- The frappe container uses a **bind mount** (`..:/workspace:cached`) — `docker commit` of the frappe container will NOT include the code at `/workspace`
- MariaDB data lives in a named Docker volume (`mariadb-data`) — `docker commit` of the mariadb container will NOT include the database
- Redis containers are ephemeral (no persistent data) — can be pulled fresh from `docker.io/redis:alpine`
- **Strategy must be:** Build a custom production Docker image (using frappe_docker production Containerfile patterns) that bakes code + site config into the image, PLUS a database backup that gets restored on first run
- Git repo delivers: source code, production Dockerfiles, compose files, DB backup, onboarding guide

### What to Include
- **Custom production image** built from `frappe/bench` base with university_erp app installed, assets built, and site configured
- **MariaDB database backup** (`bench backup`) committed to repo or hosted as release artifact — restored by first-run entrypoint
- **Redis:** Pull fresh `redis:alpine` — no custom image needed (ephemeral cache/queue)
- **Nginx/reverse proxy:** Production compose should include nginx for proper routing (not just `bench serve` on port 8000)
- **Site config:** Template `site_config.json` with placeholders for production credentials

### Secrets Handling
- All real credentials scrubbed before sharing
- `site_config.json` templated with environment variable references
- MariaDB root password changed from hardcoded `123` to env var `${MYSQL_ROOT_PASSWORD}`
- Razorpay/PayU keys, encryption_key — replaced with placeholder values
- `.env.example` provided with all required variables documented

### GHCR Setup
- Push production image to `ghcr.io/{org}/university-erp:latest` and `ghcr.io/{org}/university-erp:{version-tag}`
- GHCR authentication: `docker login ghcr.io` with GitHub PAT
- Image visibility: private (production system)
- Tag convention: `v1.0.0` for initial release, `latest` for convenience

### Production Compose
- `docker-compose.prod.yml` with:
  - Custom university-erp image (from GHCR)
  - MariaDB 11.8 with persistent volume
  - Redis cache + queue (fresh alpine images)
  - Nginx reverse proxy
  - Environment variables from `.env` file
  - Health checks on all services
  - Restart policies (`unless-stopped`)
  - Named volumes for data persistence

### Onboarding Guide
- Full production deployment guide covering:
  - Prerequisites (Docker, Docker Compose, GHCR access)
  - Pull images + create `.env` from `.env.example`
  - `docker compose up -d` to start
  - Database restore from backup (first run)
  - `bench migrate` to apply latest schema
  - Admin login and initial setup
  - SSL/TLS setup guidance
  - Backup and restore procedures
  - Project structure overview and where to find things
  - How to build dashboards (link to planning docs)

### Claude's Discretion
- Exact Dockerfile layering and multi-stage build optimization
- Nginx configuration details
- Health check endpoints and intervals
- Log rotation setup

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Docker Architecture
- `/workspace/.devcontainer/docker-compose.yml` — Current devcontainer compose with 4 services (frappe, mariadb, redis-cache, redis-queue), volume bindings, port mappings
- `/workspace/.devcontainer/devcontainer.json` — VS Code devcontainer config, workspace folder, service name
- `/workspace/images/production/Containerfile` — Frappe Docker production image template
- `/workspace/compose.yaml` — Main frappe_docker compose template for production reference

### Application Config
- `/workspace/development/frappe-bench/apps/university_erp/university_erp/hooks.py` — App hooks, installed apps list, fixture exports
- `/workspace/example.env` — Environment variable template from frappe_docker

### Research
- `.planning/research/STACK.md` — Docker commit + GHCR workflow documented
- `.planning/research/PITFALLS.md` — Docker sharing pitfalls and mitigations
- `.planning/research/ARCHITECTURE.md` — Container architecture and fixture patterns

### Codebase
- `.planning/codebase/STACK.md` — Full tech stack reference
- `.planning/codebase/STRUCTURE.md` — Directory layout and key file locations

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `/workspace/images/production/Containerfile` — Frappe Docker's official production Containerfile, can be adapted for university_erp
- `/workspace/compose.yaml` — Production compose template from frappe_docker with nginx, workers, scheduler patterns
- `/workspace/example.env` — Environment variable template with all frappe_docker production vars
- `/workspace/overrides/` — Multiple compose override files for different production scenarios (SSL, traefik, backup-cron, etc.)
- `/workspace/resources/nginx-template.conf` — Nginx configuration template for Frappe sites

### Established Patterns
- frappe_docker uses multi-stage builds: base → build → production
- Production images use `frappe/base` with apps installed via `bench get-app`
- Sites configured via environment variables, not hardcoded site_config.json
- Bench backup produces SQL + files tarballs in `sites/{site}/private/backups/`

### Integration Points
- `bench backup` produces the database dump that needs to be included
- `bench restore` on the receiving end to load the database
- `bench migrate` after restore to apply any pending schema changes
- `bench build` to compile frontend assets into the image

</code_context>

<specifics>
## Specific Ideas

- Production-ready: must include nginx, proper restart policies, health checks, environment variable configuration
- Not a dev snapshot — this is a deployable production system
- The other developer needs to be able to run this in production and then start building dashboards on top

</specifics>

<deferred>
## Deferred Ideas

- Multi-architecture images (amd64 + arm64) — v2 requirement (DOCK-V2-01)
- CI/CD pipeline for automated builds — v2 requirement (DOCK-V2-02)
- SSL/TLS certificate automation — mention in guide but don't implement

</deferred>

---

*Phase: 01-docker-sharing*
*Context gathered: 2026-03-17*
