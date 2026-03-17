# Hanumatrix EMS - Developer Handover Document

**Project:** University ERP System (Educational Management System)
**Repository:** https://github.com/ItachiUchiha366999/HMX-EMS
**Based on:** Frappe Framework v15 + ERPNext + HRMS + Education
**Date:** March 17, 2026

---

## 1. Quick Start — Clone to Running

### Prerequisites

- **Docker Desktop** installed and running
- **VS Code** with **Dev Containers** extension (`ms-vscode-remote.remote-containers`)
- **Git** installed

### Steps

```bash
git clone https://github.com/ItachiUchiha366999/HMX-EMS.git
cd HMX-EMS
code .
```

1. VS Code will detect `.devcontainer/` and show a popup — click **"Reopen in Container"**
2. Wait for the container to build and start (first time takes 3-5 minutes)
3. Once the terminal opens inside the container (you'll be at `/workspace/development`):

```bash
cd frappe-bench

# Step 1: Recreate Python virtual environment (excluded from git — Linux symlinks)
bench setup env

# Step 2: Rebuild frontend assets and symlinks
bench build

# Step 3: Restore the database from the included backup (dated 2026-03-17)
bench --site university.local restore \
  sites/university.local/private/backups/20260317_232814-university_local-database.sql.gz \
  --with-private-files sites/university.local/private/backups/20260317_232814-university_local-private-files.tar \
  --with-public-files sites/university.local/private/backups/20260317_232814-university_local-files.tar

# Step 4: Run migrations and clear cache
bench --site university.local migrate
bench --site university.local clear-cache

# Step 5: Start all services
bench start
```

4. Open in browser:

| URL | What |
|-----|------|
| http://localhost:8000 | Frappe Desk (Admin UI) |
| http://localhost:8000/app/student_portal | Student Portal |

**Login credentials:** `Administrator` / `admin`

> **Note:** Ports are mapped as 18000→8000 and 19000→9000 from host to container. If `localhost:8000` doesn't work, try `localhost:18000`.

---

## 2. Project Overview

Hanumatrix EMS is a comprehensive University ERP built on the Frappe ecosystem. It extends 4 standard Frappe apps with a custom `university_erp` app containing **275+ DocTypes across 21 modules**, plus a **Vue 3 Student Portal SPA**.

### Installed Apps (in load order)

| App | Version | Source | Purpose |
|-----|---------|--------|---------|
| frappe | v15.94.0 | github.com/frappe/frappe | Core framework, ORM, web server |
| erpnext | version-15 | github.com/frappe/erpnext | Finance, accounting, GL entries |
| hrms | v15.54.2 | github.com/frappe/hrms | Faculty HR, payroll, leave management |
| education | v15.0.0 | github.com/frappe/education | Student, program, course, assessment |
| university_erp | 0.0.1 (custom) | In-repo | 21 modules, 275+ custom DocTypes |

**Required dependency chain:** `university_erp` requires all 4 apps above (`required_apps = ["frappe", "erpnext", "hrms", "education"]`).

### Active Development Site

| Setting | Value |
|---------|-------|
| Site name | `university.local` |
| Database name | `_df4394075d9a924d` |
| Database type | MariaDB |
| Database password | `MEQEH6nrrzCmiP5Y` |
| Host | http://localhost:8000 |
| Domains | localhost, 127.0.0.1, university.local |

---

## 3. Directory Structure

```
HMX-EMS/
│
├── .devcontainer/                         # Dev Container configuration
│   ├── devcontainer.json                  # VS Code settings, extensions, ports
│   └── docker-compose.yml                 # MariaDB, 2x Redis, Frappe services
│
├── development/                           # Main development workspace (mounted at /workspace/development)
│   │
│   ├── frappe-bench/                      # Frappe bench installation
│   │   ├── apps/                          # All 5 installed Frappe apps
│   │   │   ├── frappe/                    #   Core framework (v15.94.0)
│   │   │   ├── erpnext/                   #   ERPNext (version-15)
│   │   │   ├── hrms/                      #   HR Management (v15.54.2)
│   │   │   ├── education/                 #   Education module (v15.0.0)
│   │   │   └── university_erp/            #   Custom app — YOUR MAIN WORK
│   │   ├── sites/
│   │   │   ├── university.local/          #   Dev site (site_config, backups, logs)
│   │   │   ├── common_site_config.json    #   Global config (DB host, Redis, ports)
│   │   │   ├── apps.txt                   #   Installed app list
│   │   │   └── assets/                    #   Compiled static files (css, js, images)
│   │   ├── config/                        # Supervisor/Redis configs
│   │   ├── logs/                          # Application logs (worker, scheduler, etc.)
│   │   ├── Procfile                       # Process definitions (web, socketio, watch, schedule, worker)
│   │   └── patches.txt                    # Applied migration patches
│   │
│   ├── ems-production/                    # Production Docker build files
│   │   ├── Containerfile                  #   Multi-stage Docker image build
│   │   ├── docker-compose.yml             #   10-service production stack
│   │   ├── apps.json                      #   Apps to clone during build (erpnext, hrms, education)
│   │   └── .env                           #   Production env vars (domain, DB password, SSL email)
│   │
│   ├── student-portal-vue/                # Vue 3 Student Portal SPA
│   │   ├── src/
│   │   │   ├── views/                     #   11 student pages + 10 admin pages
│   │   │   ├── layouts/                   #   StudentLayout.vue, AdminLayout.vue
│   │   │   ├── composables/               #   useAuth.js, useFrappe.js
│   │   │   └── router/index.js            #   Role-based routing
│   │   ├── package.json                   #   Vue 3.5, Vite 7, Tailwind 3.4
│   │   └── dist/                          #   Production build output
│   │
│   ├── docs/                              # Architecture & module documentation
│   │   ├── ARCHITECTURE_GUIDE.md
│   │   ├── IMPLEMENTATION_GAP_ANALYSIS.md
│   │   ├── UNIVERSITY_ERP_PROJECT.md
│   │   ├── DEMO_SEED_PLAN.md
│   │   └── modules/, architecture/, ui_ux_specifications/
│   │
│   ├── .planning/                         # Project roadmap & requirements (7 phases, 57 reqs)
│   │   ├── PROJECT.md                     #   Core project definition
│   │   ├── ROADMAP.md                     #   7-phase delivery roadmap
│   │   ├── REQUIREMENTS.md                #   57 mapped requirements
│   │   └── STATE.md                       #   Current progress tracker
│   │
│   ├── installer.py                       # Automated bench init + site creation script
│   ├── populate_student_portal_data.py    # Seed data generator for testing
│   ├── create_student_portal_data.py      # Student data creation utilities
│   ├── create_attendance_final.py         # Attendance record seed data
│   │
│   ├── HOSTEL_MANAGEMENT_SYSTEM_REQUIREMENTS_v2.md   # HMS specification
│   ├── HOSTEL_MODULE_GAP_ANALYSIS.md                 # Current vs required features
│   ├── UNIVERSITY_ERP_PRODUCT_PRICING_DOCUMENT.md    # Product pricing doc
│   ├── INTERNAL_COST_SHEET.md                        # Internal cost breakdown
│   └── cloud-hosting-plan.md                         # Infrastructure recommendations
│
├── compose.yaml                           # Root-level production compose (Frappe standard)
├── example.env                            # Environment variable template
├── .gitignore                             # Excludes env/, node_modules/, asset symlinks
├── docs/                                  # Frappe Docker docs
├── images/                                # Docker image build files
├── overrides/                             # Docker compose overrides
├── resources/                             # Nginx templates
├── tests/                                 # Docker test suite
└── DEVELOPER_HANDOVER.md                  # This file
```

---

## 4. Dev Container Architecture

### Services

The `.devcontainer/docker-compose.yml` spins up 4 services:

| Service | Image | Purpose | Ports (host→container) |
|---------|-------|---------|------------------------|
| **frappe** | frappe/bench:latest | Dev container (you work here) | 18000-18005→8000-8005, 19000-19005→9000-9005 |
| **mariadb** | mariadb:11.8 | Database server | 3306 (internal) |
| **redis-cache** | redis:alpine | Session & cache store | 6379 (internal) |
| **redis-queue** | redis:alpine | Background job queue | 6379 (internal) |

### Configuration

**devcontainer.json:**
- Forwarded ports: 8000 (web), 9000 (socketio), 6787 (file watcher)
- Remote user: `frappe`
- Workspace: `/workspace/development`
- Shutdown action: stops all compose services

**common_site_config.json** (global bench config):
```json
{
  "db_host": "mariadb",
  "db_port": 3306,
  "default_site": "university.local",
  "redis_cache": "redis://redis-cache:6379",
  "redis_queue": "redis://redis-queue:6379",
  "redis_socketio": "redis://redis-cache:6379",
  "webserver_port": 8000,
  "socketio_port": 9000,
  "live_reload": true,
  "gunicorn_workers": 25
}
```

### Pre-installed VS Code Extensions

- **ms-python.python** — Python language support
- **ms-vscode.live-server** — Live reload
- **grapecity.gc-excelviewer** — Excel/CSV viewer
- **mtxr.sqltools** + **mtxr.sqltools-driver-mysql** — Database browser
- **visualstudioexptteam.vscodeintellicode** — AI autocomplete

### Database Access via SQL Tools

Pre-configured in devcontainer.json — just open SQL Tools in the VS Code sidebar:

| Setting | Value |
|---------|-------|
| Driver | MariaDB |
| Server | mariadb |
| Port | 3306 |
| User | root |
| Password | 123 |

---

## 5. Processes (Procfile)

When you run `bench start`, these 5 processes launch:

| Process | Command | Purpose |
|---------|---------|---------|
| web | `bench serve --port 8000` | Gunicorn HTTP server |
| socketio | `node apps/frappe/socketio.js` | Real-time WebSocket (Node v20.19.2) |
| watch | `bench watch` | Auto-rebuild assets on file change |
| schedule | `bench schedule` | Background cron scheduler |
| worker | `bench worker` | Async job queue processor |

---

## 6. Custom App: university_erp

**Location:** `development/frappe-bench/apps/university_erp/`

### 21 Modules

| # | Module Directory | Purpose |
|---|-----------------|---------|
| 1 | `university_academics` | CBCS curriculum, programs, courses, timetable |
| 2 | `university_admissions` | Merit-based admission, entrance exams, applicants |
| 3 | `university_student_info` | Student lifecycle, enrollment, personal data |
| 4 | `university_examinations` | 10-point grading, SGPA/CGPA, hall tickets |
| 5 | `university_finance` | Fee structures, scholarships, GL integration |
| 6 | `faculty_management` | Workload, performance, teaching assignments |
| 7 | `university_hostel` | Room allocation, mess management, attendance |
| 8 | `university_transport` | Route management, bus allocation |
| 9 | `university_library` | Book issue/return, renewals, catalog |
| 10 | `university_placement` | Job postings, company visits, student applications |
| 11 | `university_lms` | Learning management, content delivery |
| 12 | `university_obe` | Outcome-Based Education, CO-PO attainment mapping |
| 13 | `university_research` | Publications, projects, grants tracking |
| 14 | `university_grievance` | Complaint submission and tracking |
| 15 | `university_feedback` | Student/faculty feedback collection |
| 16 | `university_inventory` | Stock and asset management |
| 17 | `university_integrations` | DigiLocker, WhatsApp, Firebase, SMS gateways |
| 18 | `university_payments` | Razorpay, PayU payment gateway integration |
| 19 | `university_analytics` | Dashboards, 54+ custom reports |
| 20 | `university_portals` | Student/Faculty/Parent portal API endpoints |
| 21 | `university_erp` | Core module (settings, shared utilities) |

### Education App Overrides (hooks.py)

The app extends 6 standard Frappe Education doctypes via `override_doctype_class`:

```python
override_doctype_class = {
    "Student":            "university_erp.overrides.student.UniversityStudent",
    "Program":            "university_erp.overrides.program.UniversityProgram",
    "Course":             "university_erp.overrides.course.UniversityCourse",
    "Assessment Result":  "university_erp.overrides.assessment_result.UniversityAssessmentResult",
    "Fees":               "university_erp.overrides.fees.UniversityFees",
    "Student Applicant":  "university_erp.overrides.student_applicant.UniversityApplicant",
}
```

### Frontend Includes (hooks.py)

```python
app_include_js = [
    "/assets/university_erp/js/university_erp.js",
    "/assets/university_erp/js/pwa.js",
    "/assets/university_erp/js/student_redirect.js",
    "/assets/university_erp/js/emergency_alert.js",
    "/assets/university_erp/js/notification_center.js"
]
```

### Fixtures (auto-exported data)

- Custom Roles (`University%` pattern)
- Custom Fields and Property Setters for University ERP module
- Workspaces for all 21 modules
- Workflows (Leave Application, Teaching Assignment Approval, Fee Refund Approval)
- Academic leave types, salary components, department custom fields
- Fee refund workflow

### Blocked ERPNext Modules

These are hidden from the UI (not relevant for university context): Manufacturing, Stock, Selling, Buying, CRM, Projects.

### Portal API

- **Location:** `university_erp/university_portals/api/portal_api.py`
- **30+ whitelisted endpoints** via `@frappe.whitelist()`
- Session-based auth inherited from Frappe login
- Called by the Vue student portal at `/api/method/university_erp.university_portals.api.portal_api.*`

### Key Utility Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `installer.py` | `development/` | Automated bench init + site creation with args |
| `populate_student_portal_data.py` | `development/` | Generate seed/test data |
| `create_student_portal_data.py` | `development/` | Student data creation utilities |
| `create_attendance_final.py` | `development/` | Attendance record seed data |
| `update_student_cgpa.py` | `university_erp/` | Recalculate CGPA for students |
| `update_attendance_trend.py` | `university_erp/` | Update attendance trend data |

---

## 7. Student Portal (Vue 3 SPA)

**Location:** `development/student-portal-vue/`

### Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Vue | 3.5.24 | UI framework (Composition API) |
| Vue Router | 4.6.4 | Client-side routing with role guards |
| Vite | 7.2.4 | Build tool |
| Tailwind CSS | 3.4.17 | Utility-first styling |

### Pages

**Student Views (11 pages):**

| Page | File | Features |
|------|------|----------|
| Dashboard | `Dashboard.vue` | KPIs, announcements, quick links |
| Academics | `Academics.vue` | Grades, timetable, courses |
| Examinations | `Examinations.vue` | Exam schedules, results, hall tickets |
| Finance | `Finance.vue` | Fees, payment history, dues |
| Hostel | `Hostel.vue` | Room allocation, mess, attendance |
| Library | `Library.vue` | Borrowed books, renewals |
| Notifications | `Notifications.vue` | Announcements, messages |
| Placement | `Placement.vue` | Job opportunities, applications |
| Profile | `Profile.vue` | Personal and academic details |
| Grievances | `Grievances.vue` | Submit and track complaints |
| Transport | `Transport.vue` | Route info, bus allocation |

**Admin Views (10 pages):** Dashboard, Academic, Exams, Institution, Users, Roles, Reports, AuditLogs, Settings, ComingSoon

### Key Architecture Files

| File | Purpose |
|------|---------|
| `src/router/index.js` | Route definitions with role-based auth guards |
| `src/layouts/StudentLayout.vue` | Student portal shell (sidebar, header) |
| `src/layouts/AdminLayout.vue` | Admin portal shell |
| `src/composables/useAuth.js` | Authentication, session management, role detection |
| `src/composables/useFrappe.js` | Frappe API wrapper for all backend calls |

### Development Commands

```bash
cd /workspace/development/student-portal-vue
npm run dev        # Vite dev server with hot reload
npm run build      # Production build → dist/
npm run preview    # Preview production build locally
```

### Integration with Frappe

- API calls go to: `/api/method/university_erp.university_portals.api.portal_api.*`
- Sessions inherited from Frappe login (no separate auth system)
- Production build served at `/assets/university_erp/` via Nginx

---

## 8. Common Development Commands

All commands run inside the devcontainer at `/workspace/development/frappe-bench`:

### Daily Development

```bash
bench start                                    # Start all 5 processes (web, socketio, watch, worker, schedule)
bench --site university.local clear-cache      # Clear Redis cache after config changes
bench --site university.local migrate          # Run pending database migrations
bench build                                    # Rebuild all frontend assets
bench build --app university_erp               # Rebuild only university_erp assets
```

### App Management

```bash
bench --site university.local install-app university_erp
bench --site university.local uninstall-app university_erp
bench get-app <git-url>                        # Clone a new app into apps/
```

### Database & Console

```bash
bench --site university.local console          # Python REPL with Frappe context
bench --site university.local mariadb          # Direct MySQL/MariaDB shell
bench --site university.local backup           # Create site backup
bench --site university.local restore <file>   # Restore from backup
```

**Console examples:**
```python
frappe.db.sql("SELECT count(*) FROM `tabStudent`")
frappe.get_doc("Student", "STUD-001")
frappe.get_all("Program", filters={"department": "Computer Science"})
```

### Testing

```bash
bench --site university.local run-tests --app university_erp
bench --site university.local run-tests --doctype "Student"
```

### Seed Data

```bash
cd /workspace/development
python populate_student_portal_data.py         # Generate test students, courses, etc.
python create_attendance_final.py              # Generate attendance records
python create_student_portal_data.py           # Additional test data
```

### Fresh Setup (if needed)

The `installer.py` script automates bench init + site creation:

```bash
cd /workspace/development
python installer.py \
  --apps-json apps-example.json \
  --bench-name frappe-bench \
  --site-name university.local \
  --frappe-branch version-15 \
  --admin-password admin \
  --db-type mariadb
```

---

## 9. Production Deployment

### Production Docker Image

**Containerfile** at `development/ems-production/Containerfile`:
- Base: Python 3.11.6 slim (Debian Bookworm)
- Node.js v20.19.2 via NVM
- wkhtmltopdf 0.12.6 (PDF generation)
- Clones frappe, erpnext, hrms, education from GitHub (version-15)
- Copies `university_erp` from local source
- Runs Gunicorn (2 workers, 4 threads, 120s timeout)

### Build & Deploy

```bash
cd development/ems-production

# Build the production Docker image
docker build \
  --build-arg APPS_JSON_BASE64=$(base64 -w0 apps.json) \
  -t ems-university:v1 .

# Start the full production stack
docker-compose up -d
```

### Production Services (10 containers)

| Service | Image | Purpose |
|---------|-------|---------|
| ems-mariadb | mariadb:10.6 | Database with health check |
| ems-redis-cache | redis:6.2-alpine | Cache store |
| ems-redis-queue | redis:6.2-alpine | Job queue |
| ems-configurator | ems-university:v1 | One-time config setup (sets DB host, Redis URLs) |
| ems-backend | ems-university:v1 | Gunicorn WSGI server |
| ems-frontend | ems-university:v1 | Nginx reverse proxy + Let's Encrypt SSL |
| ems-websocket | ems-university:v1 | Node.js socket.io |
| ems-queue-short | ems-university:v1 | Short async task worker |
| ems-queue-long | ems-university:v1 | Long async task worker |
| ems-scheduler | ems-university:v1 | Background cron scheduler |

### Production Environment Variables

File: `development/ems-production/.env`

```
SITE_DOMAIN=ems.hanumatrix.com
DB_ROOT_PASSWORD=MEQEH6nrrzCmiP5Y
LETSENCRYPT_EMAIL=connect@hanumatrix.com
```

### Production Networking

- **ems-network** — Internal bridge network for inter-container communication
- **hanumatrix-erp_proxy** — External network shared with reverse proxy (Traefik/Nginx Proxy)

### Production apps.json

The production build clones these 3 apps from GitHub (frappe is cloned separately by `bench init`):

```json
[
  { "url": "https://github.com/frappe/erpnext",   "branch": "version-15" },
  { "url": "https://github.com/frappe/hrms",      "branch": "version-15" },
  { "url": "https://github.com/frappe/education", "branch": "version-15" }
]
```

`university_erp` is copied directly from the repo via `COPY` in the Containerfile.

---

## 10. Project Roadmap (7 Phases)

**Current status:** Phase 1 not started. Roadmap created 2026-03-17.

| Phase | Name | Goal | Status |
|-------|------|------|--------|
| 1 | Foundation & Security Hardening | Fix SQL injection, add permission checks, verify cross-app data, scaffold Vue app shell with role routing | Not started |
| 2 | Shared Component Library | KPI cards, charts (ApexCharts), data tables (TanStack), filter bar, PDF/Excel export, report viewer | Pending |
| 3 | Faculty Portal | Timetable, attendance marking (<2 min for 60 students), grade entry, leave management, LMS, research views | Pending |
| 4 | Management Dashboards | VC/Registrar/Finance Officer/Dean role-specific dashboards with drill-down analytics | Pending |
| 5 | Parent Portal | Child selector, attendance heatmap, grades, fee payment (Razorpay/PayU), hostel/transport status | Pending |
| 6 | HOD Portal | Department oversight, faculty workload, leave/academic approvals, CO-PO attainment, budget view | Pending |
| 7 | Scheduled Reports & Polish | Email delivery, export verification, cross-portal enhancements | Pending |

**Parallelization:** Phases 3, 4, 5 can run in parallel after Phase 2 is complete.

**57 requirements** mapped across phases — see `development/.planning/REQUIREMENTS.md` for full list.

### Planning Files

| File | Purpose |
|------|---------|
| `development/.planning/PROJECT.md` | Core project definition and key decisions |
| `development/.planning/ROADMAP.md` | Full 7-phase roadmap with success criteria |
| `development/.planning/REQUIREMENTS.md` | 57 requirements (FOUND-*, COMP-*, FCTY-*, HOD-*, PRNT-*, MGMT-*, ANLT-*) |
| `development/.planning/STATE.md` | Current phase, progress, blockers, session continuity |

---

## 11. Known Issues & Blockers

| Issue | Severity | Location | Phase Fix |
|-------|----------|----------|-----------|
| SQL injection in dashboard queries | Critical | `university_analytics/dashboard_engine.py` | Phase 1 |
| Missing permission checks on analytics APIs | High | Analytics API endpoints | Phase 1 |
| N+1 query patterns | Medium | Executive dashboard related doc loading | Phase 1 |
| Cross-app data not verified | Medium | ERPNext ↔ HRMS ↔ Education data flows | Phase 1 |
| Management role names unverified | Low | VC, Registrar, Dean — need Frappe Role check | Phase 4 |
| Workflow engine for HOD approvals | Low | Needs API-level verification | Phase 6 |

---

## 12. What Gets Recreated Inside the Container

These directories are excluded from git because they contain Linux-specific symlinks that cannot be committed from Windows. They are regenerated inside the devcontainer:

| Excluded Directory | Why | Regeneration Command |
|-------------------|-----|---------------------|
| `development/frappe-bench/env/` | Python venv with Linux binaries/symlinks | `bench setup env` |
| `**/node_modules/` | npm packages with Linux symlinks in `.bin/` | `yarn install` or `npm install` |
| `sites/assets/` symlinks (frappe, erpnext, hrms, education, university_erp) | Symlinks to app public directories | `bench build` |

**After cloning, run these commands before `bench start`:**
```bash
bench setup env                              # Recreate Python venv
bench build                                  # Rebuild asset symlinks + compiled JS/CSS
bench --site university.local restore \      # Restore database from included backup
  sites/university.local/private/backups/20260317_232814-university_local-database.sql.gz \
  --with-private-files sites/university.local/private/backups/20260317_232814-university_local-private-files.tar \
  --with-public-files sites/university.local/private/backups/20260317_232814-university_local-files.tar
bench --site university.local migrate        # Run pending migrations
bench --site university.local clear-cache    # Clear Redis cache
```

---

## 13. Key Documentation

| Document | Location | Description |
|----------|----------|-------------|
| Architecture Guide | `development/docs/ARCHITECTURE_GUIDE.md` | System architecture overview |
| Implementation Gap Analysis | `development/docs/IMPLEMENTATION_GAP_ANALYSIS.md` | Features built vs planned |
| University ERP Project | `development/docs/UNIVERSITY_ERP_PROJECT.md` | Original project specification |
| Demo Seed Plan | `development/docs/DEMO_SEED_PLAN.md` | Test data generation plan |
| Hostel Requirements | `development/HOSTEL_MANAGEMENT_SYSTEM_REQUIREMENTS_v2.md` | HMS feature specification |
| Hostel Gap Analysis | `development/HOSTEL_MODULE_GAP_ANALYSIS.md` | Current vs required hostel features |
| Product Pricing | `development/UNIVERSITY_ERP_PRODUCT_PRICING_DOCUMENT.md` | Pricing for all 21 modules |
| Internal Cost Sheet | `development/INTERNAL_COST_SHEET.md` | Delivery cost breakdown |
| Cloud Hosting Plan | `development/cloud-hosting-plan.md` | Infrastructure recommendations & server sizing |

Additional documentation in `development/docs/`:
- `modules/` — Per-module documentation
- `architecture/` — Architecture diagrams and decisions
- `ui_ux_specifications/` — UI/UX design specs
- `university_erp_blueprint/` — Original system blueprint

---

## 14. Credentials Summary

### Development (inside devcontainer)

| Service | User | Password |
|---------|------|----------|
| Frappe Desk (Administrator) | Administrator | admin |
| MariaDB (root) | root | 123 |
| Site database | auto-generated | MEQEH6nrrzCmiP5Y |

### Production

| Setting | Value |
|---------|-------|
| Domain | ems.hanumatrix.com |
| DB root password | MEQEH6nrrzCmiP5Y |
| Let's Encrypt email | connect@hanumatrix.com |

---

## 15. Migrating Database to Another Machine

### Method 1: Using Bench Backup & Restore (Recommended)

**On the source machine** (inside devcontainer):
```bash
cd /workspace/development/frappe-bench

# Create a full backup (database + files)
bench --site university.local backup --with-files

# Backups are saved to:
ls sites/university.local/private/backups/
# You'll see files like:
#   20260317_232814-university_local-database.sql.gz      (database dump)
#   20260317_232814-university_local-files.tar             (uploaded files)
#   20260317_232814-university_local-private-files.tar     (private files)
#   20260317_232814-university_local-site_config_backup.json
```

**Transfer the backup files** to the other machine:
```bash
# From the source machine (outside container), copy the backups
scp development/frappe-bench/sites/university.local/private/backups/* user@other-machine:/path/to/HMX-EMS/development/frappe-bench/sites/university.local/private/backups/

# Or use any file transfer method (USB, cloud storage, etc.)
```

**On the target machine** (inside devcontainer):
```bash
cd /workspace/development/frappe-bench

# Restore the database backup
bench --site university.local restore \
  sites/university.local/private/backups/20260317_232814-university_local-database.sql.gz \
  --with-private-files sites/university.local/private/backups/20260317_232814-university_local-private-files.tar \
  --with-public-files sites/university.local/private/backups/20260317_232814-university_local-files.tar

# Run migrations to ensure schema is up to date
bench --site university.local migrate

# Clear cache
bench --site university.local clear-cache
```

### Method 2: Direct MariaDB Dump & Import

**On the source machine** (inside devcontainer):
```bash
# Dump the database directly
mysqldump -h mariadb -u root -p123 _df4394075d9a924d > /workspace/development/db_backup.sql

# Or compressed:
mysqldump -h mariadb -u root -p123 _df4394075d9a924d | gzip > /workspace/development/db_backup.sql.gz
```

**Transfer** `db_backup.sql.gz` to the other machine.

**On the target machine** (inside devcontainer):
```bash
# Import the dump
gunzip -c /workspace/development/db_backup.sql.gz | mysql -h mariadb -u root -p123 _df4394075d9a924d

# Run migrations
bench --site university.local migrate
bench --site university.local clear-cache
```

### Method 3: Docker Volume Export (Full Database State)

If you want to transfer the entire MariaDB data directory:

```bash
# On source machine (outside container) — stop containers first
docker-compose -f .devcontainer/docker-compose.yml down

# Find and export the MariaDB volume
docker volume ls | grep mariadb
docker run --rm -v <volume-name>:/data -v $(pwd):/backup alpine tar czf /backup/mariadb-data.tar.gz -C /data .

# Transfer mariadb-data.tar.gz to other machine

# On target machine — import into the volume
docker-compose -f .devcontainer/docker-compose.yml down
docker volume create <volume-name>
docker run --rm -v <volume-name>:/data -v $(pwd):/backup alpine tar xzf /backup/mariadb-data.tar.gz -C /data

# Start containers
docker-compose -f .devcontainer/docker-compose.yml up -d
```

### Important Notes

- **Method 1 is recommended** — it's the standard Frappe way and handles file attachments too
- The database name (`_df4394075d9a924d`) and password (`MEQEH6nrrzCmiP5Y`) are in `sites/university.local/site_config.json`
- If the target machine has a fresh setup with a different database name, update `site_config.json` accordingly
- Always run `bench migrate` after restoring to ensure schema compatibility
- Uploaded files (images, PDFs, attachments) are stored in `sites/university.local/public/files/` and `sites/university.local/private/files/` — Method 1 with `--with-files` handles these automatically

---

## 16. Contact

**Hanumatrix** — Hybrid Agency for Innovation, Impact & Intelligence
**Email:** connect@hanumatrix.com
**Production URL:** https://ems.hanumatrix.com

---

*Document Version: 2.0 | Last Updated: March 17, 2026*
