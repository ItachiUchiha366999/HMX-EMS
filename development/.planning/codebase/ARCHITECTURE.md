# Architecture

**Analysis Date:** 2026-03-17

## Pattern Overview

**Overall:** Hybrid Frappe-based Micromodular Architecture

**Key Characteristics:**
- Multi-layered service architecture built on Frappe Framework (Python backend)
- Domain-driven modular design with 21 functional modules (university_academics, university_admissions, university_finance, etc.)
- DocType-centric data model (Education app extensions + custom university DocTypes)
- Dual frontend: Frappe desk UI + Vue 3 SPA for student portal
- Event-driven hooks for cross-module communication
- Background job processing via Frappe queue system

## Layers

**Backend Application Layer:**
- Purpose: Core business logic and data management via Frappe framework
- Location: `/workspace/development/frappe-bench/apps/university_erp/university_erp/`
- Contains: 21 domain modules, DocType overrides, utility functions, API endpoints
- Depends on: Frappe framework, ERPNext, Education app, HRMS app
- Used by: Frontend applications (Vue SPA, portal pages), scheduled tasks, webhooks

**Module Layer (Domain-Specific):**
- Purpose: Organize functionality by business domain
- Locations:
  - `university_erp/university_academics/` - Course management, class scheduling
  - `university_erp/university_admissions/` - Student applications, admission workflows
  - `university_erp/university_finance/` - Fee management, financial tracking
  - `university_erp/university_payments/` - Payment gateway integration (Razorpay, PayU)
  - `university_erp/university_examinations/` - Exam management, result processing
  - `university_erp/university_hostel/` - Hostel allocation and management
  - `university_erp/university_library/` - Library operations and book tracking
  - `university_erp/university_portals/` - Portal interfaces for students/faculty
  - `university_erp/faculty_management/` - Employee/faculty-specific operations
  - Plus 12 additional modules for student info, transport, placement, LMS, OBE, research, integrations, inventory, grievance, analytics, feedback, etc.
- Each module contains: DocTypes, APIs, controllers, views, fixtures, tests

**DocType & Override Layer:**
- Purpose: Extend Education app base DocTypes with university-specific logic
- Location: `university_erp/overrides/`
- Contains:
  - `student.py` - UniversityStudent class (enrollment validation, CGPA calculation)
  - `program.py` - UniversityProgram class
  - `course.py` - UniversityCourse class
  - `assessment_result.py` - UniversityAssessmentResult class (grading logic)
  - `fees.py` - UniversityFees class (GL posting integration)
  - `student_applicant.py` - UniversityApplicant class (admission workflow)
- Pattern: Inheritance-based extension of Education app DocTypes

**API & Portal Layer:**
- Purpose: Expose business logic to frontend applications
- Location: `university_erp/university_portals/api/portal_api.py`
- Contains: Whitelisted methods for student dashboard, timetable, results, attendance
- Methods: `get_student_dashboard()`, `get_student_timetable()`, `get_student_results()`, `get_student_attendance_details()`, etc.
- Authentication: Frappe session-based (student must be logged in)

**Frontend SPA Layer:**
- Purpose: Modern Vue 3-based student portal user interface
- Location: `/workspace/development/student-portal-vue/`
- Technology: Vue 3 + Vite + Tailwind CSS + Vue Router
- Deployment target: `/assets/university_erp/student-portal-spa/` (compiled into Frappe assets)
- Route base: `/student_portal/`
- Contains: Dashboard, academics, finance, examinations, library, hostel, transport, placement, notifications, grievances, profile views

**Frappe Portal Pages Layer:**
- Purpose: Server-rendered portal pages for other user types
- Location: `university_erp/www/`
- Contains: Student portal (primary), faculty portal, alumni portal, parent portal, placement portal, notice board, fee payment pages
- Pattern: Frappe web form + Jinja templates for dynamic rendering

**Integration Layer:**
- Purpose: External service integration and data synchronization
- Location: `university_erp/integrations/`
- Contains: GL (General Ledger) integration for financial posting
- Modules: `university_erp/university_integrations/` for third-party services (WhatsApp, payment gateways)

**Setup & Configuration Layer:**
- Purpose: Installation and initialization logic
- Location: `university_erp/setup/`
- Contains:
  - `install.py` - Post-installation setup (workspace configuration, default grading scale, university settings)
  - `seed_demo_data.py` - Demo data population for testing

**Background Job Layer:**
- Purpose: Asynchronous task processing and scheduled jobs
- Location: Defined in `hooks.py` scheduler_events
- Execution: Frappe queue system (short/long workers) + APScheduler
- Tasks: Fee reminders, library notifications, CGPA updates, exam status updates, SLA checks, report generation, KPI calculations

## Data Flow

**Student Portal Authentication & Data Retrieval:**

1. Student accesses `/student_portal/` (Vue SPA)
2. Vue Router beforeEach guard calls `/api/method/frappe.auth.get_logged_user`
3. Frappe session validated - if guest, redirect to `/login`
4. Authenticated student's session available to API calls
5. Frontend calls `useFrappe().call('get_student_dashboard')`
6. Request: `POST /api/method/university_erp.university_portals.api.portal_api.get_student_dashboard`
7. Backend executes whitelisted method with student context
8. Method calls `get_current_student()` (permission-checked via `student.py` overrides)
9. Returns aggregated dashboard data (student doc, metrics, classes, announcements)
10. Vue component receives data, renders in reactive template

**Document Lifecycle with Hooks:**

1. Student document submitted via Frappe desk UI
2. `validate` event fires → calls `university_erp.overrides.student.validate_student`
3. Validations: enrollment number uniqueness, category certificate presence
4. `on_update` event fires → calls `university_erp.overrides.student.on_student_update`
5. Status updated, student marked as active/inactive
6. Boot session hook sends updated university roles to client

**Fee Processing to GL:**

1. Fees document created/submitted
2. `on_submit` event triggers dual hooks:
   - `university_erp.integrations.gl_integration.create_fee_gl_entry`
   - `university_erp.university_payments.gl_posting.on_fees_submit`
3. GL entries created in accounting system
4. Payment gateway webhook (Razorpay/PayU) updates payment status
5. Fees document status synchronized

**Scheduled Task Execution:**

1. APScheduler triggers daily, weekly, monthly, or cron-based jobs
2. Examples:
   - Daily: `university_erp.university_erp.notification_service.send_fee_reminders` (8 AM)
   - Daily: `university_erp.university_erp.scheduled_tasks.update_student_cgpa`
   - Every 5 min: `university_erp.university_erp.examination.scheduled_tasks.auto_submit_expired_exams`
3. Jobs execute with system context (permissions bypass)
4. Results stored in database, logs written to `/frappe-bench/logs/`

**State Management:**

- **Client State:** Vue component state via `ref()` and reactive data
- **Server State:** Frappe database (MariaDB)
- **Session State:** Frappe session (Redis cache)
- **Cache State:** Redis cache for frequently accessed data (university settings, academic year)
- **Queue State:** Redis queue for pending jobs
- **Broadcast State:** Socket.IO connections for real-time updates (defined in hooks but not fully implemented)

## Key Abstractions

**UniversityStudent (DocType Override):**
- Purpose: Encapsulate student-specific business rules
- File: `university_erp/overrides/student.py`
- Pattern: Class-based extension of Education's Student DocType
- Methods: `validate()`, `on_update()`, `validate_enrollment_number()`, `calculate_cgpa()`, `update_student_status()`
- Triggers: Permission checks, custom field validations, status workflows

**Portal API Module:**
- Purpose: Centralized API surface for frontend consumption
- File: `university_erp/university_portals/api/portal_api.py`
- Pattern: Frappe whitelisted methods (decorator `@frappe.whitelist()`)
- Methods: `get_student_dashboard()`, `get_student_timetable()`, `get_student_results()`, etc.
- Each method: Retrieves current student, fetches business data, aggregates into JSON response

**Module Pattern:**
- Purpose: Isolate functionality and reduce coupling
- Example: `university_erp/university_payments/`
- Contains: DocTypes (GL posting, payment records), APIs, scheduled tasks, fixtures
- Entry points: Hooks for document events, scheduled tasks, API methods
- Example: `university_erp/faculty_management/` includes employee events, leave workflows, salary components

**Utility Functions:**
- Purpose: Shared logic across modules
- File: `university_erp/utils.py`
- Examples:
  - `format_enrollment_number()` - Jinja filter for template rendering
  - `calculate_cgpa()` - Grade calculation logic
  - `format_time()` - Time formatting Jinja filter
  - `get_website_user_home_page()` - Portal redirect logic
  - `on_session_creation()` - Session initialization

**Boot Session Customization:**
- Purpose: Send university-specific data to client on login
- File: `university_erp/boot.py`
- Pattern: Hook into Frappe's `boot_session` event
- Data sent:
  - University settings (name, code, grading scale, passing threshold)
  - User's university roles (filtered by "University" prefix)
  - Current academic year
  - Payment gateway configuration (Razorpay, PayU status)

## Entry Points

**Web Application Entry:**
- Location: `student-portal-vue/src/main.js`
- Creates Vue app, mounts router, initializes to `#app` DOM element
- Router base: `/student_portal/`
- Auth guard: Checks Frappe session before rendering any page

**Backend Entry:**
- Location: `frappe-bench/apps/university_erp/` (Frappe app)
- Initialization: `hooks.py` defines all extension points
- Install hook: `setup/install.py` - runs post-installation setup
- Boot hook: `boot.py` - executes on every user login
- Scheduler: Runs background jobs defined in `scheduler_events`

**Portal Pages Entry:**
- Location: `www/student_portal/index.py` (Frappe web page controller)
- Route: `/student_portal/` (Frappe website route)
- Renders: `portal_base.html` template with Vue app shell

**API Entry Points:**
- Dashboard: `/api/method/university_erp.university_portals.api.portal_api.get_student_dashboard`
- Timetable: `/api/method/university_erp.university_portals.api.portal_api.get_student_timetable`
- Results: `/api/method/university_erp.university_portals.api.portal_api.get_student_results`
- Attendance: `/api/method/university_erp.university_portals.api.portal_api.get_student_attendance_details`

## Error Handling

**Strategy:** Frappe exception framework with custom error types

**Patterns:**

- **Permission Errors:** `frappe.PermissionError` - raised when accessing unauthorized resources (e.g., another student's data)
  ```python
  if student != frappe.session.user:
      frappe.throw(_("Access denied"), frappe.PermissionError)
  ```

- **Validation Errors:** `frappe.ValidationError` - raised during document validation
  ```python
  if not self.custom_enrollment_number:
      frappe.throw(_("Enrollment number is required"))
  ```

- **API Errors:** Return error in `_server_messages` field for frontend handling
  ```python
  data = {"_server_messages": json.dumps([error_message])}
  ```

- **Frontend Error Handling:** useFrappe composable catches and stores errors, components display in UI
  ```javascript
  try { await call(method) }
  catch (e) { error.value = e.message }
  ```

## Cross-Cutting Concerns

**Logging:**
- Framework: Frappe's built-in logger
- Method: `frappe.logger().info()`, `.error()`, `.warning()`
- Files: Written to `/frappe-bench/logs/`
- Usage: Setup, scheduled tasks, error tracking (boot.py, install.py, all hooks)

**Validation:**
- Approach: DocType-level validation via `validate()` method and custom validators
- Examples:
  - Enrollment number uniqueness (student.py)
  - Category certificate requirement (student.py)
  - Fee amount validation
- Pattern: Raise `frappe.ValidationError` with translated message

**Authentication:**
- Approach: Frappe session-based (cookies, CSRF tokens)
- Enforcement:
  - Frontend: Router guard checks `/api/method/frappe.auth.get_logged_user`
  - Backend: Whitelisted methods execute with current user context
  - Permission override: `ignore_permissions=True` only for post-install setup
- Portal roles: Defined in fixtures, assigned via Frappe role system

**Authorization:**
- Approach: Custom permission logic in DocType overrides
- Example: `student.py` has `get_permission_query_conditions()` and `has_permission()`
- Pattern: Filter documents based on current user's roles/departments
- Enforcement: Frappe permission engine applies filters automatically on queries

---

*Architecture analysis: 2026-03-17*
