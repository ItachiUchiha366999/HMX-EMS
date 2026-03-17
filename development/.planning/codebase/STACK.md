# Technology Stack

**Analysis Date:** 2026-03-17

## Languages

**Primary:**
- Python 3.10+ - Backend (Frappe/ERPNext framework and university_erp custom app)
- JavaScript (ES6+) - Frontend and Node.js runtime

**Secondary:**
- Vue.js 3 - Student portal single-page application (SPA)
- CSS3 / PostCSS - Styling with Tailwind CSS

## Runtime

**Environment:**
- Node.js v20.19.2 - Running Frappe socketio.js for real-time communication
- Python 3.10-3.13 (compatible per `requires-python = ">=3.10,<3.14"`)

**Package Manager:**
- npm - JavaScript package management (student portal and Frappe assets)
- pip - Python package management (frappe-bench environment)
- Lockfile: package-lock.json (student-portal-vue), pip freeze for Python

## Frameworks

**Core:**
- Frappe v15+ - Metadata-driven, full-stack low-code web framework
  - Location: `/workspace/development/frappe-bench/apps/frappe`
  - Serves the main ERP backend and admin interface
- ERPNext v15+ - Enterprise resource planning module built on Frappe
  - Location: `/workspace/development/frappe-bench/apps/erpnext`
- HRMS (Human Resource Management System) v15+ - HR and payroll module
  - Location: `/workspace/development/frappe-bench/apps/hrms`
- Education App v15+ - Education-specific modules for student management
  - Location: `/workspace/development/frappe-bench/apps/education`

**Custom Application:**
- university_erp v0.0.1 - Comprehensive University Management System
  - Location: `/workspace/development/frappe-bench/apps/university_erp`
  - Built on Frappe framework using flit build backend

**Frontend:**
- Vue.js 3.5.24 - Reactive component framework for student portal
  - Location: `/workspace/development/student-portal-vue`
  - Build tool: Vite 7.2.4
- Vue Router 4.6.4 - Client-side routing for student portal SPA

**Testing:**
- pytest - Python testing framework (configured as dev-dependency in bench)
- Faker - Test data generation for development
- unittest-xml-reporting - JUnit-format test reporting
- responses - HTTP mocking for API testing
- freezegun - Time mocking for scheduled task testing

**Build/Dev:**
- Vite 7.2.4 - Modern frontend build tool for student portal
  - Config: `/workspace/development/student-portal-vue/vite.config.js`
  - Outputs to: `/workspace/development/frappe-bench/apps/university_erp/university_erp/public/student-portal-spa`
- Tailwind CSS 3.4.17 - Utility-first CSS framework for student portal styling
  - Config: `/workspace/development/student-portal-vue/tailwind.config.js`
- PostCSS 8.5.6 - CSS transformation tool
- Autoprefixer 10.4.23 - Vendor prefix automation
- @vitejs/plugin-vue 6.0.1 - Vue 3 Vite integration
- Ruff - Python linting and formatting tool (configured in frappe pyproject.toml)
  - Line length: 110 characters
  - Uses double quotes for strings, tab indentation
- Gunicorn - WSGI HTTP Server (custom fork for Frappe)
- Bench - Frappe development and deployment toolkit
  - Includes CLI commands for app management, testing, and asset building

## Key Dependencies

**Critical (Backend):**
- PyMySQL 1.1.1 - MySQL/MariaDB database connection (strict version)
- Werkzeug 3.1.4 - WSGI utilities and request handling
- PyJWT 2.8.0 - JWT token generation/validation for auth
- RestrictedPython 8.0 - Safe execution of user-written scripts
- Jinja2 3.1.2 - Template engine for document generation
- redis 4.5.5 + hiredis 2.2.3 - Caching and job queue backend
- rq 1.15.1 - Job queue implementation (RQ - Redis Queue)
- requests 2.32.0 - HTTP client library for external APIs

**Document Processing:**
- WeasyPrint 59.0 - HTML/CSS to PDF generation
- pydyf 0.10.0 - PDF library foundation
- pypdf 6.4.0 - PDF reading/manipulation
- Pillow 11.3.0 - Image processing
- openpyxl 3.1.2 - Excel file handling
- python-dateutil 2.8.2 - Date/time utilities
- bleach 6.0.0 + bleach-allowlist 1.0.3 - HTML sanitization
- beautifulsoup4 4.12.2 - HTML parsing
- html5lib 1.1 - HTML5 parser
- lxml/cssutils 2.9.0 - CSS parsing

**Infrastructure:**
- boto3 1.34.143 - AWS SDK for S3 integration
- dropbox 11.36.2 - Dropbox API integration
- google-api-python-client 2.172.0 - Google APIs client
- google-auth 2.40.3 - Google OAuth authentication
- google-auth-oauthlib 1.2.2 - OAuth2 flow for Google
- posthog 3.21.0 - Product analytics and feature flags
- sentry-sdk 1.45.1 - Error tracking and monitoring
- pydantic 2.10.2 - Data validation using Python type hints
- cryptography 44.0.1 - Cryptographic operations
- PyYAML 6.0.2 - YAML config file parsing
- GitPython 3.1.34 - Git repository operations

**External Integrations (university_erp specific):**
- razorpay 1.4.0 - Indian payment gateway integration
- firebase-admin - Firebase Cloud Messaging for push notifications (imported conditionally)

**Database:**
- Database Type: MariaDB (default) or PostgreSQL (support via psycopg2-binary 2.9.1)
- Connection Pool: Integrated in Frappe

## Configuration

**Environment:**
- Environment variables sourced from `.env` file in `/workspace/development/frappe-bench/apps/university_erp`
- Example config template at: `/workspace/development/frappe-bench/apps/university_erp/.env.example`
- Key configs required:
  - `SITE_NAME` - Site identifier (default: university.local)
  - `HTTP_PORT` / `HTTPS_PORT` - Web server ports
  - `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` - Database access
  - `REDIS_CACHE`, `REDIS_QUEUE` - Redis connection URLs
  - `MAIL_SERVER`, `MAIL_PORT`, `MAIL_LOGIN`, `MAIL_PASSWORD` - SMTP email configuration
  - Payment gateway keys (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
  - Firebase credentials (service_account_json)
  - DigiLocker integration credentials
  - WhatsApp provider credentials
  - S3 backup bucket name

**Build:**
- Frappe config: Generated in `/workspace/development/frappe-bench/config/` directory
- Site config: `/workspace/development/frappe-bench/sites/university.local/site_config.json`
- Contains database credentials, domain list, app configuration
- Procfile: `/workspace/development/frappe-bench/Procfile` defines:
  - `web`: HTTP server on port 8000 via `bench serve`
  - `socketio`: Node.js real-time communication via socketio.js
  - `watch`: Asset file watcher for development
  - `schedule`: Scheduled task scheduler
  - `worker`: Background job processor

## Platform Requirements

**Development:**
- Node.js v20.x (for socketio.js and student portal build)
- Python 3.10-3.13
- MariaDB or PostgreSQL database
- Redis (for caching and job queue)
- wkhtmltopdf (optional, for PDF generation)

**Production:**
- Deployment via Docker using: `/workspace/development/frappe-bench/apps/university_erp/Dockerfile`
- Based on frappe/bench:version-15 image
- Requires: MariaDB v10.3+, Redis, Nginx (reverse proxy)
- Environment: Linux x86_64 (WSL2 in development)

---

*Stack analysis: 2026-03-17*
