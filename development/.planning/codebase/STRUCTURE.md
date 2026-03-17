# Codebase Structure

**Analysis Date:** 2026-03-17

## Directory Layout

```
/workspace/development/
├── frappe-bench/                           # Frappe development environment
│   ├── apps/
│   │   ├── frappe/                         # Core Frappe framework
│   │   ├── erpnext/                        # ERPNext business modules
│   │   ├── hrms/                           # HR management system
│   │   ├── education/                      # Education base app (extended by university_erp)
│   │   └── university_erp/                 # Main University ERP app
│   ├── sites/                              # Frappe site configuration & database
│   ├── config/                             # Frappe bench configuration
│   ├── logs/                               # Application logs
│   └── env/                                # Python virtual environment
├── student-portal-vue/                     # Vue 3 student portal SPA
│   ├── src/
│   │   ├── components/                     # Vue components (currently empty, views used instead)
│   │   ├── layouts/                        # Layout components (StudentLayout, AdminLayout)
│   │   ├── views/                          # Page views (Dashboard, Academics, Finance, etc.)
│   │   ├── router/                         # Vue Router configuration
│   │   ├── composables/                    # Vue composables (useAuth, useFrappe)
│   │   ├── assets/                         # Static assets (images, fonts)
│   │   ├── App.vue                         # Root Vue component
│   │   ├── main.js                         # App entry point
│   │   └── style.css                       # Global CSS
│   ├── public/                             # Public static files
│   ├── dist/                               # Built output (generated)
│   ├── package.json                        # Node dependencies
│   ├── vite.config.js                      # Vite build configuration
│   ├── tailwind.config.js                  # Tailwind CSS configuration
│   └── postcss.config.js                   # PostCSS configuration
├── ems-production/                         # Production EMS deployment config
├── university.local/                       # Local site configuration
├── docs/                                   # Documentation
│   ├── architecture/                       # Architecture documentation
│   ├── modules/                            # Module documentation
│   ├── UI changes/                         # UI specification docs
│   └── ui_ux_specifications/               # UX design specs
└── .planning/                              # GSD planning directory
    └── codebase/                           # Codebase analysis docs (ARCHITECTURE.md, STRUCTURE.md, etc.)
```

## Directory Purposes

**frappe-bench/apps/university_erp/university_erp/:**
- Purpose: Core application logic for University ERP system
- Contains: 21 functional modules, DocType definitions, APIs, webhooks, scheduled tasks
- Access pattern: Imported as Python package `university_erp`
- Dependency root: Extends Frappe, ERPNext, HRMS, Education apps

**frappe-bench/apps/university_erp/university_erp/university_academics/:**
- Purpose: Academic calendar, course management, class scheduling
- Contains: DocTypes (Course, Program, Class), timetable logic, course enrollment
- Structure: `/doctype/`, `/api/`, `/workspace/`, fixtures

**frappe-bench/apps/university_erp/university_erp/university_admissions/:**
- Purpose: Student application and admission workflow management
- Contains: DocTypes (Student Applicant, Admission Form), admission process controllers
- Key logic: `student_applicant.py` override handles custom admission rules

**frappe-bench/apps/university_erp/university_erp/university_finance/:**
- Purpose: Financial management, budget tracking, expense allocation
- Contains: Custom Finance DocTypes for university context
- Integration: GL posting via `integrations/gl_integration.py`

**frappe-bench/apps/university_erp/university_erp/university_payments/:**
- Purpose: Fee management, payment gateway integration, GL reconciliation
- Contains: DocTypes, Razorpay/PayU gateway handlers, webhook receivers
- Key files:
  - `gl_posting.py` - GL entry creation on fee submission
  - `scheduled_tasks.py` - Auto-reconciliation jobs
  - `webhooks/` - Payment gateway webhook handlers

**frappe-bench/apps/university_erp/university_erp/university_examinations/:**
- Purpose: Exam creation, online exam execution, result processing
- Contains: DocTypes (Exam, Exam Question, Student Exam Session), result calculation
- Key logic: `scheduled_tasks.py` handles exam auto-submission, result publishing

**frappe-bench/apps/university_erp/university_erp/university_hostel/:**
- Purpose: Hostel allocation, room management, fee charging
- Contains: DocTypes (Hostel, Room, Allocation), allocation algorithms
- Scheduling: Automated allocation during admission period

**frappe-bench/apps/university_erp/university_erp/university_library/:**
- Purpose: Book catalog, issue/return tracking, fine calculation
- Contains: DocTypes (Book, Issue, Reservation), library operations
- Scheduled tasks: Overdue notices, reservation expiration

**frappe-bench/apps/university_erp/university_erp/university_portals/:**
- Purpose: User-facing portal interfaces (student, faculty, parent, alumni)
- Key structure:
  - `api/portal_api.py` - Central API for Vue SPA (whitelisted methods)
  - `doctype/` - Portal-specific DocTypes (Alumni, Job Posting, Placement Application)
  - Portal pages: Rendered in `www/` directory
- Integration: Receives calls from `/student-portal-vue/` SPA

**frappe-bench/apps/university_erp/university_erp/faculty_management/:**
- Purpose: Faculty-specific operations (leave, salary, teaching assignment)
- Contains: Custom Leave types, Salary components, Faculty Profiles
- Key files:
  - `leave_events.py` - Leave application approval workflow
  - `employee_events.py` - Employee/faculty status management
  - `fixtures/` - Default leave types, salary components
  - `student_feedback.py` - Faculty performance feedback

**frappe-bench/apps/university_erp/university_erp/overrides/:**
- Purpose: Extend Education app DocTypes with university-specific logic
- Key files:
  - `student.py` - UniversityStudent class (validation, CGPA, status)
  - `course.py` - UniversityCourse class (course customization)
  - `program.py` - UniversityProgram class (program customization)
  - `assessment_result.py` - UniversityAssessmentResult class (grading, GL posting)
  - `fees.py` - UniversityFees class (fee validation, GL integration)
  - `student_applicant.py` - UniversityApplicant class (admission workflow)
- Pattern: Each override is a Python class inheriting from parent DocType class

**frappe-bench/apps/university_erp/university_erp/integrations/:**
- Purpose: External system integrations
- Contents: `gl_integration.py` for accounting GL posting

**frappe-bench/apps/university_erp/university_erp/setup/:**
- Purpose: Installation and initialization
- Key files:
  - `install.py` - Post-installation setup (workspace hiding, grading scale, settings creation)
  - `seed_demo_data.py` - Demo data for testing (students, courses, admissions)
  - `seed_chunk1.py` - Partial demo data

**frappe-bench/apps/university_erp/university_erp/www/:**
- Purpose: Frappe portal pages (server-rendered HTML)
- Directories:
  - `student_portal/` - Main student portal entry point (portal_base.html hosts Vue app)
  - `student-portal/` - Legacy student portal structure (alternative)
  - `faculty-portal/` - Faculty dashboard
  - `alumni-portal/` - Alumni network
  - `parent-portal/` - Parent access portal
  - `placement-portal/` - Placement tracking
  - `notice-board/` - Announcements and notices
  - `library/` - Library interface
  - `pay-fees/` - Fee payment form
  - `fee-payment-success/`, `fee-payment-failed/` - Payment status pages
- Routing: Defined in `hooks.py` via `website_route_rules`

**frappe-bench/apps/university_erp/university_erp/public/:**
- Purpose: Frontend assets served to browser
- Subdirectories:
  - `js/` - JavaScript files (PWA, student redirect, notifications, emergency alerts)
  - `css/` - CSS files (removed from app_include_css to preserve Frappe themes)
  - `images/` - Static images (favicon, splash image)
  - `student-portal-spa/` - Compiled Vue SPA (output of build process)

**frappe-bench/apps/university_erp/university_erp/tests/:**
- Purpose: Backend test files
- Contains: Unit tests for backend modules
- Pattern: Test files mirror module structure

**student-portal-vue/src/:**
- Purpose: Source code for Vue 3 student portal SPA
- Structure:
  - `main.js` - Entry point (creates app, uses router)
  - `App.vue` - Root component (StudentLayout wrapper with router-view)
  - `style.css` - Global CSS
  - `router/index.js` - Vue Router configuration (11 routes)
  - `composables/` - Vue 3 composition functions
    - `useFrappe.js` - API client for calling backend methods
    - `useAuth.js` - Authentication logic
  - `layouts/` - Layout wrapper components
    - `StudentLayout.vue` - Sidebar nav for student portal
    - `AdminLayout.vue` - Admin panel layout
  - `views/` - Page components (lazy-loaded via router)
    - `Dashboard.vue` - Student dashboard (overview)
    - `Academics.vue` - Courses and grades
    - `Finance.vue` - Fee status and payments
    - `Examinations.vue` - Exam schedules and results
    - `Library.vue` - Book catalog and issues
    - `Hostel.vue` - Room allocation and info
    - `Transport.vue` - Bus services
    - `Placement.vue` - Job postings and applications
    - `Notifications.vue` - Alerts and announcements
    - `Grievances.vue` - Complaint tracking
    - `Profile.vue` - Student profile editing
    - `admin/*` - Admin panel pages (Dashboard, Academic, Users, Roles, Settings, Audit Logs, etc.)
  - `assets/` - Images, icons, static files

**frappe-bench/sites/university.local/:**
- Purpose: Site-specific configuration and data
- Contains: Site configuration, database dump, SSL certificates
- Note: Local development site

**frappe-bench/apps/university_erp/:**
- Purpose: App package root
- Key files:
  - `setup.py` - Python package configuration
  - `hooks.py` - Frappe extension points (CRITICAL - defines all integrations)
  - `modules.txt` - List of 21 modules
  - `patches.txt` - Database migration patches
  - `README.md` - App documentation
  - `requirements.txt` - Python dependencies

## Key File Locations

**Entry Points:**

- Backend entry: `frappe-bench/apps/university_erp/` (Frappe app root)
  - Initialized by Frappe bench at startup
  - Configuration: `hooks.py`
- Frontend entry: `student-portal-vue/src/main.js`
  - Creates Vue app, mounts to `#app`
- Portal page entry: `frappe-bench/apps/university_erp/university_erp/www/student_portal/` (Frappe website page)
  - Serves HTML shell with Vue app container

**Configuration:**

- Frappe hooks: `frappe-bench/apps/university_erp/university_erp/hooks.py` (16KB, 330+ lines)
  - Defines: DocType overrides, doc events, scheduled tasks, website routes, permissions, boot session logic
- App metadata: `frappe-bench/apps/university_erp/setup.py`
- Build config: `student-portal-vue/vite.config.js` (output path points to Frappe assets)
- Module list: `frappe-bench/apps/university_erp/university_erp/modules.txt` (21 modules)

**Core Logic:**

- DocType extensions: `frappe-bench/apps/university_erp/university_erp/overrides/` (6 files)
  - `student.py` - Primary student logic
  - `assessment_result.py` - Grading and GL posting
  - `fees.py` - Fee processing
  - Others: program.py, course.py, student_applicant.py
- Utilities: `frappe-bench/apps/university_erp/university_erp/utils.py` (100+ lines)
  - Jinja filters, helper functions
- Boot logic: `frappe-bench/apps/university_erp/university_erp/boot.py` (130 lines)
  - Session initialization with university data

**API Layer:**

- Portal API: `frappe-bench/apps/university_erp/university_erp/university_portals/api/portal_api.py` (100+ lines)
  - Whitelisted methods for Vue SPA
- Specialized APIs:
  - Analytics: `university_analytics/api.py`
  - Accreditation: `university_erp/accreditation/api.py`

**Testing:**

- Backend tests: `frappe-bench/apps/university_erp/university_erp/tests/` (module mirroring)
- Backend test files: Multiple `test_*.py` files at root:
  - `test_dashboard_context.py`
  - `test_exams_page.py`
  - `test_hall_ticket_download.py`
  - `test_library_page.py`
  - `test_portal_pages.py`

**Setup & Installation:**

- Post-install: `frappe-bench/apps/university_erp/university_erp/setup/install.py` (160 lines)
  - Hides ERPNext workspaces, creates default grading scale, initializes university settings
- Demo data: `frappe-bench/apps/university_erp/university_erp/setup/seed_demo_data.py` (1000+ lines)

## Naming Conventions

**Files:**

- Backend modules: `snake_case.py` (e.g., `student.py`, `portal_api.py`)
- Vue components: `PascalCase.vue` (e.g., `Dashboard.vue`, `StudentLayout.vue`)
- Test files: `test_*.py` for unit tests (Frappe convention)
- Config files: lowercase with extension (e.g., `hooks.py`, `vite.config.js`)

**Directories:**

- Backend modules: `snake_case` (e.g., `university_academics`, `university_payments`)
- Django-style app structure: `module_name/doctype/doctype_name/` (Frappe convention)
- Vue structure: lowercase kebab-case (e.g., `src/views/`, `src/layouts/`)
- Config directories: lowercase (e.g., `.planning/`, `frappe-bench/`)

**Python Classes:**

- DocType overrides: `University{DocTypeName}` (e.g., `UniversityStudent`, `UniversityFees`)
- Inherited from Education base classes
- Convention: Class name matches DocType logical name

**JavaScript/Vue:**

- Components: PascalCase (e.g., `StudentLayout.vue`, `Dashboard.vue`)
- Functions: camelCase (e.g., `useFrappe()`, `handleResponse()`)
- Composables: `useXxx` pattern (e.g., `useAuth.js`, `useFrappe.js`)
- Constants: UPPER_SNAKE_CASE (e.g., `PORTAL_API` in useFrappe.js)

**Frappe DocTypes:**

- Custom DocTypes: Use `University` prefix or full name (e.g., `University Settings`, `University Department`)
- Education base: Standard (e.g., `Student`, `Course`, `Assessment Result`)

## Where to Add New Code

**New Feature in Existing Module:**
- Primary code: `frappe-bench/apps/university_erp/university_erp/{module_name}/`
  - Example: Adding new hostel feature → `university_hostel/doctype/{doctype_name}/`
  - Add Python controller: `university_hostel/doctype/{doctype_name}/{doctype_name}.py`
  - Add tests: `university_hostel/doctype/{doctype_name}/test_{doctype_name}.py`
- Hooks: Update `hooks.py` if adding doc_events, scheduled_tasks, or website routes

**New Feature in New Module:**
- Create module directory: `frappe-bench/apps/university_erp/university_erp/university_{module_name}/`
- Add to modules.txt: Add "University {Module Name}" as new line
- Structure:
  - `doctype/` - DocType definitions
  - `api/` - API methods (if needed)
  - `fixtures/` - Default data
  - Workspace configuration file (for Frappe workspace)
- Register in hooks.py: Add to fixture list, add any scheduled tasks or doc_events

**New Component/Module in Frontend (Vue SPA):**
- Implementation: `student-portal-vue/src/views/{FeatureName}.vue`
- Add route: Update `student-portal-vue/src/router/index.js`
- Add layout if needed: `student-portal-vue/src/layouts/{LayoutName}.vue`
- Add composable: `student-portal-vue/src/composables/use{FeatureName}.js`

**API Endpoints:**
- For Vue SPA: Add whitelisted method to `university_portals/api/portal_api.py`
  - Decorate with `@frappe.whitelist()`
  - Called via `useFrappe().call('method_name', params)`
- For custom logic: Create module-specific API file (e.g., `university_examinations/api.py`)

**Utilities:**
- Shared backend helpers: `frappe-bench/apps/university_erp/university_erp/utils.py`
  - Jinja filters
  - Permission helpers
  - Calculation functions
- Shared frontend helpers: Create in `student-portal-vue/src/composables/` or as utility functions

**Scheduled Tasks:**
- Define in `hooks.py` under `scheduler_events`
- Implement in module-specific file: `{module_name}/scheduled_tasks.py`
- Categories: `daily`, `weekly`, `monthly`, `cron`

**Document Events:**
- Define in `hooks.py` under `doc_events` pointing to handler functions
- Implement in module: `{module_name}/{handler_name}.py`
- Hooks: `validate`, `on_update`, `on_submit`, `on_cancel`, etc.

**Overrides of Education DocTypes:**
- Location: `frappe-bench/apps/university_erp/university_erp/overrides/{doctype_name}.py`
- Must extend parent class from Education app
- Register in `hooks.py`: `override_doctype_class` dictionary
- Include any permission logic: `get_permission_query_conditions()`, `has_permission()`

## Special Directories

**frappe-bench/sites/university.local/:**
- Purpose: Local development site data and configuration
- Generated: Auto-created by `bench new-site` command
- Committed: No (in .gitignore)
- Contains: Database backup, site config, SSL certs for local testing

**frappe-bench/logs/:**
- Purpose: Application logs from backend
- Generated: Runtime (created when code runs)
- Committed: No (in .gitignore)
- Cleanup: Periodically rotated (size-based or age-based)

**student-portal-vue/dist/:**
- Purpose: Built Vue SPA output
- Generated: By `npm run build`
- Committed: No (in .gitignore)
- Usage: Output is copied to `frappe-bench/apps/university_erp/university_erp/public/student-portal-spa/`

**frappe-bench/apps/university_erp/university_erp/public/student-portal-spa/:**
- Purpose: Compiled Vue SPA assets served by Frappe
- Generated: By Vite build process
- Committed: Yes (final output)
- Route: `/assets/university_erp/student-portal-spa/`

**frappe-bench/env/:**
- Purpose: Python virtual environment
- Generated: By `bench --help` setup
- Committed: No (in .gitignore)
- Contains: Python packages installed via pip

**frappe-bench/config/:**
- Purpose: Frappe bench configuration
- Generated: By bench init
- Committed: Partial (some files like database config ignored)
- Contains: Procfile, Socketio config, app list

**frappe-bench/apps/university_erp/university_erp/fixtures/:**
- Purpose: Exportable data to be installed with the app
- Generated: Created manually or exported via `bench export-fixtures`
- Committed: Yes
- Contains: Default roles, custom fields, property setters, workflows

---

*Structure analysis: 2026-03-17*
