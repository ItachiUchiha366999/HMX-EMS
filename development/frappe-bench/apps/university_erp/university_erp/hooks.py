app_name = "university_erp"
app_title = "University ERP"
app_publisher = "University"
app_description = "Comprehensive University Management System"
app_email = "support@university.edu"
app_license = "MIT"
app_version = "0.0.1"

# Required Apps (Hybrid Architecture)
required_apps = ["frappe", "erpnext", "hrms", "education"]

# Frappe 15 compatibility
# NOTE: CSS overrides removed to preserve default ERPNext/Frappe UI and theme support
# The custom CSS (university_desk.css, university_erp.css) was overriding Frappe's
# CSS variables which broke dark mode and theme switching.
# Student portal uses scoped CSS in portal_base.html instead.
app_include_css = [
    # "/assets/university_erp/css/university_erp.css",    # Removed - overrides ERPNext styles
    # "/assets/university_erp/css/university_desk.css",   # Removed - breaks dark mode
    # "/assets/university_erp/css/mobile.css"             # Removed - has global overrides
]
app_include_js = [
    "/assets/university_erp/js/university_erp.js",
    "/assets/university_erp/js/pwa.js",
    "/assets/university_erp/js/student_redirect.js",
    "/assets/university_erp/js/emergency_alert.js",
    "/assets/university_erp/js/notification_center.js"
]

# Web includes (for portal pages)
# Note: Removed web_override.css and theme CSS to preserve default ERPNext UI
# Student portal pages use their own scoped CSS via portal_base.html
web_include_css = [
    # Only include mobile.css for responsive fixes (doesn't override base UI)
    # "/assets/university_erp/css/mobile.css"
]
web_include_js = [
    "/assets/university_erp/js/pwa.js",
    "/assets/university_erp/js/student_redirect.js"  # Auto-redirect students to portal
    # "/assets/university_erp/js/web_portal.js"
]

# App Modules (7 modules as per blueprint)
# Format: {"module_name": "Module Name", "category": "Category", "label": "Display Label"}
# Note: Using app_include_js instead of modules for Frappe v15
# Modules are defined in modules.txt

# Override Education DocType Classes (6 overrides)
# This allows us to extend Education DocTypes with university-specific logic
override_doctype_class = {
    "Student": "university_erp.overrides.student.UniversityStudent",
    "Program": "university_erp.overrides.program.UniversityProgram",
    "Course": "university_erp.overrides.course.UniversityCourse",
    "Assessment Result": "university_erp.overrides.assessment_result.UniversityAssessmentResult",
    "Fees": "university_erp.overrides.fees.UniversityFees",
    "Student Applicant": "university_erp.overrides.student_applicant.UniversityApplicant",
}

# Fixtures - Data that will be exported/imported during bench export-fixtures
fixtures = [
    {"dt": "Role", "filters": [["name", "like", "University%"]]},
    {"dt": "Custom Field", "filters": [["module", "=", "University ERP"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "University ERP"]]},
    {"dt": "Workspace", "filters": [["module", "in", ["University ERP", "University Academics", "University Admissions", "University Student Info", "University Examinations", "University Finance", "Faculty Management", "University Hostel", "University Transport", "University Library", "University Placement", "University LMS", "University Research", "University OBE", "University Integrations", "University Portals", "University Payments", "University Inventory", "University Grievance", "University Analytics", "University Feedback"]]]},
    {"dt": "Workflow", "filters": [["name", "in", ["Leave Application Workflow", "Teaching Assignment Approval Workflow", "Fee Refund Approval Workflow"]]]},
    "university_erp.faculty_management.fixtures.academic_leave_types",
    "university_erp.faculty_management.fixtures.salary_components",
    "university_erp.faculty_management.fixtures.department_custom_fields",
    "university_erp.university_payments.fixtures.fee_refund_workflow",
]

# Block ERPNext Modules from UI
# These modules are not relevant for a university context
block_modules = [
    "Manufacturing",
    "Stock",
    "Selling",
    "Buying",
    "CRM",
    "Projects",
    "Assets",
    "Quality",
    "Support",
    "ERPNext Integrations",
]

# Document Events
# Hook into Education DocTypes to add university-specific logic
doc_events = {
    "Student": {
        "validate": "university_erp.overrides.student.validate_student",
        "on_update": "university_erp.overrides.student.on_student_update",
    },
    "Fees": {
        "on_submit": [
            "university_erp.integrations.gl_integration.create_fee_gl_entry",
            "university_erp.university_payments.gl_posting.on_fees_submit",
        ],
        "on_cancel": "university_erp.university_payments.gl_posting.on_fees_cancel",
    },
    "Leave Application": {
        "on_submit": "university_erp.faculty_management.leave_events.on_submit",
        "on_cancel": "university_erp.faculty_management.leave_events.on_cancel",
    },
    "Employee": {
        "on_update": "university_erp.faculty_management.employee_events.on_update",
    },
    "Department": {
        "on_update": "university_erp.faculty_management.department_events.on_update",
    },
}

# Boot Session
# Called when user logs in - sends university data to client
boot_session = "university_erp.boot.boot_session"

# After Install
# Called after app is installed on a site
after_install = "university_erp.setup.install.after_install"

# Scheduled Tasks
# Format: {"cron_expression": "path.to.function"}
scheduler_events = {
    "daily": [
        # Fee Management
        "university_erp.university_erp.notification_service.send_fee_reminders",
        "university_erp.university_erp.notification_service.send_overdue_notices",
        # Library Management
        "university_erp.university_erp.notification_service.send_library_overdue_notices",
        "university_erp.university_erp.scheduled_tasks.expire_library_reservations",
        # Academic
        "university_erp.university_erp.scheduled_tasks.update_student_cgpa",
        "university_erp.university_erp.scheduled_tasks.check_attendance_thresholds",
        # Bank Reconciliation
        "university_erp.university_payments.scheduled_tasks.auto_reconcile_daily",
        # Notification Cleanup
        "university_erp.university_erp.notification_center.cleanup_expired_notifications",
        # Reset daily WhatsApp counters
        "university_erp.university_integrations.whatsapp_gateway.reset_daily_counters",
        # Inventory & Asset Management
        "university_erp.university_erp.inventory_scheduled_tasks.check_low_stock_items",
        "university_erp.university_erp.inventory_scheduled_tasks.check_maintenance_due",
        "university_erp.university_erp.inventory_scheduled_tasks.check_calibration_due",
        # Examination Module (Phase 17)
        "university_erp.university_erp.examination.scheduled_tasks.update_exam_status",
        "university_erp.university_erp.examination.scheduled_tasks.send_exam_reminders",
        "university_erp.university_erp.examination.scheduled_tasks.process_pending_evaluations",
        "university_erp.university_erp.examination.scheduled_tasks.update_question_statistics",
        "university_erp.university_erp.examination.scheduled_tasks.publish_scheduled_results",
        # Grievance & Feedback Module (Phase 18)
        "university_erp.university_erp.grievance.scheduled_tasks.daily_sla_check",
        "university_erp.university_erp.grievance.scheduled_tasks.send_pending_reminders",
        "university_erp.university_erp.grievance.scheduled_tasks.update_days_open",
        "university_erp.university_erp.grievance.scheduled_tasks.send_feedback_reminders",
        "university_erp.university_erp.grievance.scheduled_tasks.close_expired_feedback_forms",
        "university_erp.university_erp.grievance.scheduled_tasks.activate_scheduled_feedback_forms",
        "university_erp.university_erp.grievance.scheduled_tasks.update_feedback_form_statistics",
        # Analytics, Reporting & MIS Module (Phase 19)
        "university_erp.university_erp.analytics.scheduled_tasks.run_scheduled_reports",
        "university_erp.university_erp.analytics.scheduled_tasks.calculate_daily_kpis",
        "university_erp.university_erp.analytics.scheduled_tasks.check_kpi_alerts",
        "university_erp.university_erp.analytics.scheduled_tasks.update_dashboard_statistics",
        # Accreditation & Compliance Module (Phase 20)
        "university_erp.university_erp.accreditation.scheduled_tasks.daily_attainment_update",
        "university_erp.university_erp.accreditation.scheduled_tasks.check_deadline_reminders",
    ],
    "weekly": [
        # Attendance warnings
        "university_erp.university_erp.notification_service.send_attendance_warnings",
        # Placement updates
        "university_erp.university_erp.scheduled_tasks.send_placement_updates",
        # System maintenance
        "university_erp.university_erp.scheduled_tasks.cleanup_old_notifications",
        # Notification cleanup (older notifications)
        "university_erp.university_erp.notification_center.cleanup_old_notifications",
        # Weekly communication report
        "university_erp.university_erp.report.communication_analytics.communication_analytics.generate_weekly_communication_report",
        # Examination Module (Phase 17)
        "university_erp.university_erp.examination.scheduled_tasks.cleanup_expired_exam_attempts",
        # Analytics, Reporting & MIS Module (Phase 19)
        "university_erp.university_erp.analytics.scheduled_tasks.calculate_weekly_kpis",
        # Accreditation & Compliance Module (Phase 20)
        "university_erp.university_erp.accreditation.scheduled_tasks.weekly_naac_data_collection",
    ],
    "monthly": [
        # Reports and summaries
        "university_erp.university_erp.scheduled_tasks.generate_monthly_reports",
        "university_erp.university_erp.scheduled_tasks.update_placement_statistics",
        # Monthly communication report
        "university_erp.university_erp.report.communication_analytics.communication_analytics.generate_monthly_communication_report",
        # Asset depreciation posting
        "university_erp.university_erp.inventory_scheduled_tasks.post_depreciation_entries",
        # Analytics, Reporting & MIS Module (Phase 19)
        "university_erp.university_erp.analytics.scheduled_tasks.calculate_monthly_kpis",
        "university_erp.university_erp.analytics.scheduled_tasks.calculate_quarterly_kpis",
        "university_erp.university_erp.analytics.scheduled_tasks.cleanup_old_kpi_values",
        # Accreditation & Compliance Module (Phase 20)
        "university_erp.university_erp.accreditation.scheduled_tasks.monthly_progress_notification",
    ],
    "cron": {
        # Exam reminders handled in daily scheduler via examination.scheduled_tasks
        # Assignment deadline reminders (daily at 8 AM)
        "0 8 * * *": [
            "university_erp.university_erp.scheduled_tasks.send_assignment_reminders",
        ],
        # Auto-submit expired online exams (every 5 minutes)
        "*/5 * * * *": [
            "university_erp.university_erp.examination.scheduled_tasks.auto_submit_expired_exams",
        ],
    }
}

# Website Settings
# These settings control the university portal (if enabled)
website_route_rules = [
    {"from_route": "/student_portal/<path:app_path>", "to_route": "student_portal"},
    {"from_route": "/faculty-portal/<path:app_path>", "to_route": "faculty-portal"},
    {"from_route": "/student-feedback/<path:app_path>", "to_route": "student-feedback"},
    {"from_route": "/library/<path:app_path>", "to_route": "library"},
    {"from_route": "/placement/<path:app_path>", "to_route": "placement"},
    {"from_route": "/notice-board/<path:app_path>", "to_route": "notice-board"},
    {"from_route": "/emergency-alert/<path:app_path>", "to_route": "emergency-alert"},
    # Online Examination Portal (Phase 17)
    {"from_route": "/online-exam/<path:app_path>", "to_route": "online-exam"},
    # Payment Gateway Webhooks
    {"from_route": "/api/method/university_erp.university_payments.webhooks.razorpay_webhook.handle_razorpay_webhook", "to_route": "razorpay-webhook"},
    {"from_route": "/api/method/university_erp.university_payments.webhooks.payu_callback.payu_success", "to_route": "payu-success"},
    {"from_route": "/api/method/university_erp.university_payments.webhooks.payu_callback.payu_failure", "to_route": "payu-failure"},
    {"from_route": "/api/method/university_erp.university_payments.webhooks.payu_callback.payu_cancel", "to_route": "payu-cancel"},
    # WhatsApp Webhook
    {"from_route": "/api/method/university_erp.university_integrations.whatsapp_gateway.whatsapp_webhook", "to_route": "whatsapp-webhook"},
]

# Portal Menu Items
website_context = {
    "favicon": "/assets/university_erp/images/favicon.png",
    "splash_image": "/assets/university_erp/images/splash.png"
}

# Portal Settings
has_website_permission = {
    "Faculty Profile": "university_erp.faculty_management.faculty_profile.has_website_permission",
    "Student Feedback": "university_erp.faculty_management.student_feedback.has_website_permission",
}

# Permissions
# Skip certain permissions for university-specific workflows
permission_query_conditions = {
    "Student": "university_erp.overrides.student.get_permission_query_conditions",
}

has_permission = {
    "Student": "university_erp.overrides.student.has_permission",
}

# Jinja Filters
# Custom Jinja filters for templates
jinja = {
    "methods": [
        "university_erp.utils.format_enrollment_number",
        "university_erp.utils.calculate_cgpa",
        "university_erp.utils.format_time",
    ],
}

# Standard Filters
# These filters appear in list views
standard_queries = {
    "Student": "university_erp.overrides.student.student_query",
}

# Notification Config
# notification_config = "university_erp.notifications.get_notification_config"

# On Document Update
# Global document events
# doc_events is preferred, but this is kept for reference

# Web Form Hooks
# webform_list_context = "university_erp.admissions.web_form.get_webform_list_context"

# Override Whitelisted Methods
# override_whitelisted_methods = {
#     "frappe.desk.form.save.savedocs": "university_erp.overrides.savedocs"
# }

# Each module gets its own controllers
# Uncomment when specific controllers are created
# override_doctype_dashboards = {
#     "Student": "university_erp.overrides.student.get_dashboard_data",
# }

# User Data Protection
user_data_fields = [
    {
        "doctype": "Student",
        "filter_by": "student",
        "redact_fields": ["first_name", "last_name", "email", "mobile"],
    },
]

# Regional Overrides (if needed for specific regions/countries)
# regional_overrides = {
#     "India": {
#         "university_erp.overrides.student": "university_erp.regional.india.student"
#     }
# }

# Translation
# Frappe 15 uses standard gettext
# Place translations in university_erp/translations/

# Leaderboard (Frappe 15 feature)
# leaderboards = "university_erp.leaderboards.get_leaderboards"

# Role-based Home Pages
# NOTE: role_home_page expects Workspace names, not URLs
# For portal redirects, use get_website_user_home_page instead
# role_home_page = {
# 	"Student": "student_portal",  # This would look for a Workspace, not a portal page
# }

# Website User Home Page
# This function is called to determine where to redirect a user after login
get_website_user_home_page = "university_erp.utils.get_website_user_home_page"

# Session Creation Hook (must be a list)
# Called when a user logs in (after successful authentication)
on_session_creation = [
	"university_erp.utils.on_session_creation"
]
