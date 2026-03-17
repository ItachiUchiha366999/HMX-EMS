# Hanumatrix EMS - Developer Handover Document

**Project:** University ERP System (Educational Management System)
**Repository:** https://github.com/ItachiUchiha366999/HMX-EMS
**Based on:** Frappe Framework v15 + ERPNext
**Date:** March 17, 2026

---

## 1. Quick Start (Clone to Running in 5 Minutes)

### Prerequisites
- **Docker Desktop** installed and running
- **VS Code** with **Dev Containers** extension (`ms-vscode-remote.remote-containers`)

### Steps

```bash
git clone https://github.com/ItachiUchiha366999/HMX-EMS.git
cd HMX-EMS
code .
```

1. VS Code will detect `.devcontainer/` and prompt **"Reopen in Container"** — click it
2. Wait for the container to build and start (first time takes a few minutes)
3. Once inside the container terminal:

```bash
cd frappe-bench
bench setup env              # Recreates Python virtual environment
bench build                  # Rebuilds frontend assets and symlinks
bench start                  # Starts all services
```

4. Access the application:
   - **Frappe Desk:** http://localhost:8000
   - **Login:** Administrator / admin
   - **Student Portal:** http://localhost:8000/app/student_portal
   - **Database:** Use SQL Tools in VS Code sidebar (pre-configured)

---

## 2. Project Overview

Hanumatrix EMS is a comprehensive University ERP built on top of the Frappe ecosystem. It extends 4 standard Frappe apps with a custom `university_erp` app containing **275+ DocTypes across 21 modules**, plus a **Vue 3 Student Portal SPA**.

### Installed Apps

| App | Version | Purpose |
|-----|---------|---------|
| frappe | v15.94.0 | Core framework |
| erpnext | v15 (version-15) | Finance, accounting, inventory |
| hrms | v15.54.2 | Faculty HR, payroll, leave |
| education | v15.0.0 | Student, program, course management |
| university_erp | custom | 21 modules, 275+ DocTypes |

### Active Site
- **Site name:** `university.local`
- **Database:** MariaDB (`_df4394075d9a924d`)
- **Host:** http://localhost:8000

---

## 3. Directory Structure

```
HMX-EMS/
├── .devcontainer/                    # Dev container config
│   ├── devcontainer.json            # VS Code dev container settings
│   └── docker-compose.yml           # MariaDB, Redis, Frappe services
├── development/                      # Main development workspace
│   ├── frappe-bench/                # Frappe bench installation
│   │   ├── apps/                    # All installed Frappe apps
│   │   │   ├── frappe/
│   │   │   ├── erpnext/
│   │   │   ├── hrms/
│   │   │   ├── education/
│   │   │   └── university_erp/      # Custom app (your main work)
│   │   ├── sites/
│   │   │   ├── university.local/    # Dev site (config, backups, logs)
│   │   │   ├── common_site_config.json
│   │   │   └── assets/              # Compiled static files
│   │   ├── config/                  # Supervisor/Redis configs
│   │   ├── logs/                    # Application logs
│   │   └── Procfile                 # Process definitions
│   ├── ems-production/              # Production Docker build
│   │   ├── docker-compose.yml       # Production services
│   │   ├── Containerfile            # Docker image build
│   │   ├── .env                     # Production env vars
│   │   └── apps.json                # Apps for production build
│   ├── student-portal-vue/          # Vue 3 frontend SPA
│   ├── docs/                        # Architecture & module docs
│   ├── .planning/                   # Project roadmap & requirements
│   ├── installer.py                 # Automated bench setup script
│   ├── populate_student_portal_data.py  # Seed data generator
│   └── *.md                         # Requirements, pricing, hosting docs
├── compose.yaml                      # Root production compose
├── example.env                       # Environment template
├── .gitignore
└── DEVELOPER_HANDOVER.md             # This file
```

---

## 4. Dev Container Architecture

The devcontainer spins up 4 services:

| Service | Image | Purpose | Ports |
|---------|-------|---------|-------|
| **frappe** | frappe/bench:latest | Development container | 18000-18005 (web), 19000-19005 (socketio) |
| **mariadb** | mariadb:11.8 | Database | 3306 |
| **redis-cache** | redis:alpine | Session/cache store | - |
| **redis-queue** | redis:alpine | Background job queue | - |

### Pre-installed VS Code Extensions
- Python, Live Server, Excel Viewer
- SQL Tools + MariaDB driver (pre-configured connection)
- IntelliCode

### Database Access (SQL Tools)
- **Server:** mariadb
- **Port:** 3306
- **User:** root
- **Password:** 123

---

## 5. Custom App: university_erp

**Location:** `development/frappe-bench/apps/university_erp/`

### 21 Modules

| # | Module | Key Features |
|---|--------|-------------|
| 1 | Academics | CBCS curriculum, programs, courses, timetable |
| 2 | Admissions | Merit-based admission, entrance exams |
| 3 | Student Info | Complete student lifecycle management |
| 4 | Examinations | 10-point grading, SGPA/CGPA calculation |
| 5 | Finance | Fee structure, scholarships, GL integration |
| 6 | HR/Faculty | Workload allocation, performance, payroll |
| 7 | Hostel | Room allocation, mess, attendance |
| 8 | Transport | Route management, bus allocation |
| 9 | Library | Book issue/return, renewals |
| 10 | Placement | Job postings, company visits, applications |
| 11 | LMS | Learning management, content delivery |
| 12 | OBE | Outcome-Based Education, CO-PO mapping |
| 13 | Research | Publications, projects tracking |
| 14 | Grievances | Complaint submission and tracking |
| 15 | Inventory | Stock management |
| 16 | Integrations | DigiLocker, WhatsApp, Firebase, SMS |
| 17 | Payments | Razorpay, PayU integration |
| 18 | Analytics | Dashboards, 54+ custom reports |
| 19 | Student Portal | Student-facing API endpoints |
| 20 | Faculty Portal | Faculty-facing features |
| 21 | Parent Portal | Parent-facing features |

### Education App Overrides
The app extends standard Frappe Education doctypes via `overrides/`:
- `student.py` — Extended Student doctype
- `program.py` — Extended Program doctype
- `course.py` — Extended Course doctype
- `assessment_result.py` — Extended grading
- `fees.py` — Extended fee management
- `applicant.py` — Extended admission applicant

### Portal API
- **Location:** `university_erp/university_portals/api/portal_api.py`
- **30+ whitelisted endpoints** via `@frappe.whitelist()`
- Session-based auth inherited from Frappe login

---

## 6. Student Portal (Vue 3 SPA)

**Location:** `development/student-portal-vue/`

### Tech Stack
- Vue 3.5 (Composition API) + Vue Router 4
- Vite 7 (build tool)
- Tailwind CSS 3.4

### Pages

**Student Views:** Dashboard, Academics, Examinations, Finance, Hostel, Library, Notifications, Placement, Profile, Grievances, Transport

**Admin Views:** Dashboard, Academic Management, Exams, Institution Settings, Users & Roles, Reports, Audit Logs

### Key Files
```
src/
├── router/index.js          # Routes with role-based guards
├── layouts/
│   ├── StudentLayout.vue    # Student portal shell
│   └── AdminLayout.vue      # Admin portal shell
├── composables/
│   ├── useAuth.js           # Authentication & session
│   └── useFrappe.js         # Frappe API wrapper
└── views/                   # All page components
```

### Development
```bash
cd /workspace/development/student-portal-vue
npm run dev        # Dev server with hot reload
npm run build      # Production build → dist/
```

### Integration
- API calls to: `/api/method/university_erp.university_portals.api.portal_api.*`
- Sessions inherited from Frappe (no separate auth)
- Production assets served at `/assets/university_erp/`

---

## 7. Common Development Commands

```bash
# Inside the devcontainer, working dir: /workspace/development/frappe-bench

# Start/stop services
bench start                                    # Start all (web, socketio, watch, worker, schedule)

# Site management
bench --site university.local console          # Python REPL
bench --site university.local migrate          # Run pending migrations
bench --site university.local clear-cache      # Clear Redis cache

# App management
bench --site university.local install-app university_erp
bench --site university.local uninstall-app university_erp

# Frontend
bench build                                    # Build all app assets
bench build --app university_erp               # Build specific app

# Database
bench --site university.local backup           # Create backup
bench --site university.local restore [file]   # Restore from backup

# Testing
bench --site university.local run-tests --app university_erp

# Seed data
cd /workspace/development
python populate_student_portal_data.py         # Generate test data
python create_attendance_final.py              # Generate attendance records
```

---

## 8. Production Deployment

### Build & Deploy
```bash
cd development/ems-production

# Build production image
docker build --build-arg APPS_JSON_BASE64=$(base64 -w0 apps.json) -t ems-university:v1 .

# Start production stack
docker-compose up -d
```

### Production Services
| Service | Purpose |
|---------|---------|
| ems-backend | Gunicorn WSGI server (8 workers, 4 threads) |
| ems-frontend | Nginx reverse proxy + SSL (Let's Encrypt) |
| ems-websocket | Node.js socket.io |
| ems-mariadb | MariaDB 10.6 |
| ems-redis-cache | Redis cache |
| ems-redis-queue | Redis queue |
| ems-scheduler | Background cron jobs |
| ems-queue-short | Quick async tasks |
| ems-queue-long | Heavy async tasks |

### Production Environment
```
SITE_DOMAIN=ems.hanumatrix.com
DB_ROOT_PASSWORD=MEQEH6nrrzCmiP5Y
LETSENCRYPT_EMAIL=connect@hanumatrix.com
```

---

## 9. Project Roadmap (7 Phases)

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation & Security Hardening | Not started |
| 2 | Shared Component Library | Pending |
| 3 | Faculty Portal | Pending |
| 4 | Management Dashboards | Pending |
| 5 | Parent Portal | Pending |
| 6 | HOD Portal | Pending |
| 7 | Scheduled Reports & Polish | Pending |

**Full roadmap:** `development/.planning/ROADMAP.md`
**57 requirements:** `development/.planning/REQUIREMENTS.md`
**Current state:** `development/.planning/STATE.md`

---

## 10. Known Issues

1. **SQL Injection Risk** — `dashboard_engine.py` uses string interpolation in queries (Phase 1 fix)
2. **Missing Permission Checks** — Analytics APIs lack role-based access control
3. **N+1 Query Patterns** — Executive dashboard has inefficient related doc loading
4. **Symlink Note** — `sites/localhost` → `university.local` symlink is recreated inside the container; ignore if missing on Windows

---

## 11. What Gets Recreated Inside the Container

These directories are excluded from git (contain Linux symlinks) and must be regenerated:

| Directory | Regeneration Command |
|-----------|---------------------|
| `frappe-bench/env/` | `bench setup env` |
| `**/node_modules/` | `yarn install` or `npm install` (inside apps) |
| `sites/assets/` symlinks | `bench build` |

---

## 12. Key Documentation

| Document | Location |
|----------|----------|
| Architecture Guide | `development/docs/ARCHITECTURE_GUIDE.md` |
| Implementation Gap Analysis | `development/docs/IMPLEMENTATION_GAP_ANALYSIS.md` |
| Hostel System Requirements | `development/HOSTEL_MANAGEMENT_SYSTEM_REQUIREMENTS_v2.md` |
| Module Gap Analysis | `development/HOSTEL_MODULE_GAP_ANALYSIS.md` |
| Cloud Hosting Plan | `development/cloud-hosting-plan.md` |
| Product Pricing | `development/UNIVERSITY_ERP_PRODUCT_PRICING_DOCUMENT.md` |
| Internal Cost Sheet | `development/INTERNAL_COST_SHEET.md` |

---

## 13. Contact

**Hanumatrix** — Hybrid Agency for Innovation, Impact & Intelligence
**Email:** connect@hanumatrix.com
**Production Domain:** ems.hanumatrix.com

---

*Document Version: 1.0 | Prepared: March 17, 2026*
