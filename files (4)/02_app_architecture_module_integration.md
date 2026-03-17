# University ERP - App Architecture & Module Integration Guide

## Document Overview

| Item | Details |
|------|---------|
| **Document Version** | 1.0 |
| **Last Updated** | December 2025 |
| **Purpose** | Architecture design for integrating all modules into single University EMS app |
| **Prerequisites** | Completed Document 01 (Docker/DevContainer Setup) |

---

## Part 1: Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         University ERP System                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    UNIVERSITY_EMS (Custom App)                       │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │   Hostel    │ │  Transport  │ │   Library   │ │  Advanced   │   │   │
│  │  │ Management  │ │ Management  │ │ Management  │ │   Exams     │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │  Training   │ │    NAAC     │ │     OBE     │ │   Alumni    │   │   │
│  │  │ & Placement │ │ Accreditation│ │   System   │ │ Management  │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │  Research   │ │    CBCS     │ │  Grievance  │ │   Sports    │   │   │
│  │  │ Management  │ │   System    │ │   System    │ │ & Cultural  │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓ Extends                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ERPNEXT CORE MODULES                            │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │   │
│  │  │ Education │ │   HRMS    │ │Accounting │ │   Stock   │           │   │
│  │  │  Module   │ │  Module   │ │  Module   │ │  Module   │           │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │   │
│  │  │  Assets   │ │  Projects │ │  Support  │ │  Website  │           │   │
│  │  │  Module   │ │  Module   │ │  Module   │ │  Module   │           │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓ Built on                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      FRAPPE FRAMEWORK v15                            │   │
│  │  • DocTypes • Workflows • Reports • Permissions • API • WebSocket  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Module Dependency Map

```
                          ┌──────────────────┐
                          │  Student Master  │
                          │   (Education)    │
                          └────────┬─────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│    Hostel     │         │   Transport   │         │    Library    │
│  Management   │         │  Management   │         │  Management   │
└───────────────┘         └───────────────┘         └───────────────┘
        │                          │                          │
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────────────────────────────────────────────────────────┐
│                      Fee Management (Accounting)                   │
└───────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   Advanced    │         │   Training    │         │    NAAC       │
│ Examinations  │         │ & Placement   │         │ Accreditation │
└───────────────┘         └───────────────┘         └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                          ┌────────▼─────────┐
                          │   OBE System     │
                          │  (CO-PO Mapping) │
                          └──────────────────┘
```

---

## Part 2: Creating the University EMS App

### Step 2.1: Initialize the App

```bash
# Enter the Frappe container
docker exec -it university_erp_frappe bash

# Navigate to bench directory
cd /home/frappe/frappe-bench

# Create new Frappe app
bench new-app university_ems

# Follow the prompts:
# App Title: University ERP Management System
# App Description: Comprehensive ERP solution for universities
# App Publisher: Your Organization Name
# App Email: admin@university.edu
# App License: MIT
```

### Step 2.2: App Directory Structure

After creation, organize the app with the following structure:

```
university_ems/
├── university_ems/
│   ├── __init__.py
│   ├── hooks.py                          # App hooks and configurations
│   ├── patches.txt                       # Database patches
│   ├── modules.txt                       # Module definitions
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── desktop.py                    # Desktop icons
│   │   └── docs.py                       # Documentation config
│   │
│   ├── university_ems/                   # Core module
│   │   ├── __init__.py
│   │   └── doctype/
│   │       └── university_settings/      # Global settings
│   │
│   ├── hostel_management/                # Hostel module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── hostel/
│   │   │   ├── hostel_room/
│   │   │   ├── hostel_room_allocation/
│   │   │   ├── hostel_fee_structure/
│   │   │   ├── mess_menu/
│   │   │   ├── hostel_visitor/
│   │   │   └── hostel_maintenance/
│   │   └── report/
│   │       ├── hostel_occupancy/
│   │       └── mess_bill_report/
│   │
│   ├── transport_management/             # Transport module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── transport_route/
│   │   │   ├── vehicle/
│   │   │   ├── vehicle_stop/
│   │   │   ├── student_route_assignment/
│   │   │   ├── driver/
│   │   │   └── transport_fee_structure/
│   │   └── report/
│   │       └── route_wise_students/
│   │
│   ├── library_management/               # Library module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── library_settings/
│   │   │   ├── library_book/
│   │   │   ├── library_member/
│   │   │   ├── library_transaction/
│   │   │   ├── library_fine/
│   │   │   ├── library_reservation/
│   │   │   └── library_card/
│   │   └── report/
│   │       ├── books_issued/
│   │       └── overdue_books/
│   │
│   ├── advanced_examination/             # Advanced Exam module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── exam_center/
│   │   │   ├── seating_arrangement/
│   │   │   ├── hall_ticket/
│   │   │   ├── invigilator_schedule/
│   │   │   ├── external_examiner/
│   │   │   ├── revaluation_request/
│   │   │   └── unfair_means_case/
│   │   └── report/
│   │       └── exam_result_analysis/
│   │
│   ├── training_placement/               # T&P module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── company_master/
│   │   │   ├── job_opening/
│   │   │   ├── placement_drive/
│   │   │   ├── student_application/
│   │   │   ├── interview_schedule/
│   │   │   ├── placement_offer/
│   │   │   └── student_skill/
│   │   └── report/
│   │       └── placement_statistics/
│   │
│   ├── accreditation/                    # NAAC/NBA module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── naac_criteria/
│   │   │   ├── quality_metric/
│   │   │   ├── best_practice/
│   │   │   ├── iqac_meeting/
│   │   │   ├── ssr_data/
│   │   │   └── accreditation_document/
│   │   └── report/
│   │       └── naac_compliance_report/
│   │
│   ├── obe_system/                       # OBE module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── course_outcome/
│   │   │   ├── program_outcome/
│   │   │   ├── co_po_mapping/
│   │   │   ├── attainment_level/
│   │   │   └── obe_settings/
│   │   └── report/
│   │       └── co_po_attainment/
│   │
│   ├── cbcs_system/                      # CBCS module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── credit_structure/
│   │   │   ├── elective_choice/
│   │   │   ├── credit_transfer/
│   │   │   └── cgpa_calculation/
│   │   └── report/
│   │       └── credit_summary/
│   │
│   ├── research_management/              # Research module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── research_project/
│   │   │   ├── publication/
│   │   │   ├── patent/
│   │   │   ├── research_guide/
│   │   │   └── phd_scholar/
│   │   └── report/
│   │       └── research_output/
│   │
│   ├── alumni_management/                # Alumni module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── alumni/
│   │   │   ├── alumni_event/
│   │   │   ├── alumni_donation/
│   │   │   └── alumni_chapter/
│   │   └── report/
│   │       └── alumni_engagement/
│   │
│   ├── grievance_management/             # Grievance module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── grievance/
│   │   │   ├── grievance_category/
│   │   │   └── grievance_resolution/
│   │   └── report/
│   │       └── grievance_summary/
│   │
│   ├── sports_cultural/                  # Sports & Cultural module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── sports_event/
│   │   │   ├── cultural_event/
│   │   │   ├── event_registration/
│   │   │   └── facility_booking/
│   │   └── report/
│   │       └── event_participation/
│   │
│   ├── cafeteria_management/             # Cafeteria module
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   ├── cafeteria_menu/
│   │   │   ├── meal_coupon/
│   │   │   └── cafeteria_vendor/
│   │   └── report/
│   │
│   ├── public/                           # Static assets
│   │   ├── css/
│   │   │   └── university_ems.css
│   │   ├── js/
│   │   │   └── university_ems.js
│   │   └── images/
│   │
│   ├── templates/                        # Jinja templates
│   │   ├── includes/
│   │   └── pages/
│   │
│   ├── www/                              # Web pages
│   │   ├── student_portal/
│   │   ├── faculty_portal/
│   │   ├── parent_portal/
│   │   └── alumni_portal/
│   │
│   └── api/                              # REST API endpoints
│       ├── __init__.py
│       ├── student_api.py
│       ├── hostel_api.py
│       └── library_api.py
│
├── setup.py
├── requirements.txt
├── README.md
├── license.txt
└── MANIFEST.in
```

### Step 2.3: Configure modules.txt

Edit `university_ems/modules.txt`:

```
University EMS
Hostel Management
Transport Management
Library Management
Advanced Examination
Training Placement
Accreditation
OBE System
CBCS System
Research Management
Alumni Management
Grievance Management
Sports Cultural
Cafeteria Management
```

### Step 2.4: Configure hooks.py

Edit `university_ems/hooks.py`:

```python
from . import __version__ as app_version

app_name = "university_ems"
app_title = "University ERP Management System"
app_publisher = "University ERP Team"
app_description = "Comprehensive ERP solution for universities"
app_email = "admin@university.edu"
app_license = "MIT"

# Required Apps
required_apps = ["frappe", "erpnext", "education", "hrms"]

# Includes in <head>
# ------------------
app_include_css = "/assets/university_ems/css/university_ems.css"
app_include_js = "/assets/university_ems/js/university_ems.js"

# Home Pages
# ----------
role_home_page = {
    "Student": "student-portal",
    "Guardian": "parent-portal",
    "Instructor": "faculty-portal",
    "Alumni": "alumni-portal",
}

# Website user home page
home_page = "login"

# Generators
# ----------
website_generators = ["Alumni", "Company Master"]

# DocType Class Fixtures
# ----------------------
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "in", [
        "University EMS",
        "Hostel Management",
        "Transport Management",
        "Library Management",
        "Advanced Examination",
        "Training Placement",
        "Accreditation",
        "OBE System"
    ]]]},
    {"dt": "Property Setter", "filters": [["module", "in", [
        "University EMS",
        "Hostel Management",
    ]]]},
    {"dt": "Print Format"},
    {"dt": "Workspace"},
    {"dt": "Dashboard"},
]

# Document Events
# ---------------
doc_events = {
    "Student": {
        "after_insert": "university_ems.university_ems.utils.student_utils.after_student_insert",
        "on_update": "university_ems.university_ems.utils.student_utils.on_student_update",
    },
    "Program Enrollment": {
        "on_submit": "university_ems.university_ems.utils.enrollment_utils.on_enrollment_submit",
    },
    "Fee Schedule": {
        "on_submit": "university_ems.university_ems.utils.fee_utils.add_hostel_transport_fees",
    },
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "university_ems.library_management.tasks.send_overdue_reminders",
        "university_ems.hostel_management.tasks.daily_attendance_report",
        "university_ems.transport_management.tasks.route_optimization_check",
    ],
    "weekly": [
        "university_ems.accreditation.tasks.quality_metrics_update",
        "university_ems.research_management.tasks.publication_reminder",
    ],
    "monthly": [
        "university_ems.alumni_management.tasks.alumni_engagement_report",
        "university_ems.training_placement.tasks.placement_statistics_update",
    ],
    "cron": {
        # Send library due reminders at 9 AM daily
        "0 9 * * *": [
            "university_ems.library_management.tasks.send_due_reminders"
        ],
        # Calculate hostel mess bills on 1st of every month
        "0 0 1 * *": [
            "university_ems.hostel_management.tasks.generate_mess_bills"
        ],
    }
}

# Jinja Environment
# -----------------
jinja = {
    "methods": [
        "university_ems.utils.jinja_utils.get_student_details",
        "university_ems.utils.jinja_utils.get_academic_year",
    ],
}

# Installation
# ------------
after_install = "university_ems.install.after_install"
before_uninstall = "university_ems.uninstall.before_uninstall"

# Desk Notifications
# ------------------
notification_config = "university_ems.notifications.get_notification_config"

# Permissions
# -----------
permission_query_conditions = {
    "Library Transaction": "university_ems.library_management.doctype.library_transaction.library_transaction.get_permission_query_conditions",
    "Hostel Room Allocation": "university_ems.hostel_management.doctype.hostel_room_allocation.hostel_room_allocation.get_permission_query_conditions",
}

has_permission = {
    "Library Transaction": "university_ems.library_management.doctype.library_transaction.library_transaction.has_permission",
}

# Reports
# -------
report_module_hooks = {
    "University EMS": [
        "hostel_occupancy_report",
        "library_circulation_report",
        "placement_statistics_report",
        "naac_compliance_report",
    ]
}

# API Endpoints
# -------------
override_whitelisted_methods = {
    "frappe.client.get_list": "university_ems.api.overrides.custom_get_list"
}

# Custom Fields
# -------------
# These will be added to existing ERPNext DocTypes
# Defined in install.py and fixtures

# Dashboard Charts
# ----------------
get_dashboard_charts = "university_ems.utils.dashboard.get_dashboard_charts"

# Workspaces
# ----------
# Workspaces are defined as JSON files in the workspace folder

# Document Links
# --------------
doctype_list_js = {
    "Student": "public/js/student_list.js",
    "Program Enrollment": "public/js/program_enrollment_list.js",
}

doctype_js = {
    "Student": "public/js/student.js",
    "Program Enrollment": "public/js/program_enrollment.js",
    "Fee Schedule": "public/js/fee_schedule.js",
}

# Override Standard DocTypes
# --------------------------
override_doctype_class = {
    "Student": "university_ems.overrides.student.CustomStudent",
}

# Communication
# -------------
communication_doctypes = ["Grievance", "Library Transaction"]
```

---

## Part 3: Custom Fields for ERPNext Integration

### Step 3.1: Student DocType Custom Fields

Create `university_ems/university_ems/custom_fields/student_custom_fields.py`:

```python
"""Custom fields to be added to Student DocType"""

STUDENT_CUSTOM_FIELDS = {
    "Student": [
        # Personal Information Section
        {
            "fieldname": "university_section_break",
            "fieldtype": "Section Break",
            "label": "University Information",
            "insert_after": "image"
        },
        {
            "fieldname": "admission_number",
            "fieldtype": "Data",
            "label": "Admission Number",
            "insert_after": "university_section_break",
            "unique": 1
        },
        {
            "fieldname": "prn_number",
            "fieldtype": "Data",
            "label": "PRN Number",
            "insert_after": "admission_number",
            "unique": 1
        },
        {
            "fieldname": "abc_id",
            "fieldtype": "Data",
            "label": "ABC ID (Academic Bank of Credits)",
            "insert_after": "prn_number"
        },
        {
            "fieldname": "category",
            "fieldtype": "Select",
            "label": "Category",
            "options": "\nGeneral\nOBC\nSC\nST\nEWS\nNT\nVJ/DT",
            "insert_after": "abc_id"
        },
        {
            "fieldname": "column_break_uni1",
            "fieldtype": "Column Break",
            "insert_after": "category"
        },
        {
            "fieldname": "physically_challenged",
            "fieldtype": "Check",
            "label": "Physically Challenged",
            "insert_after": "column_break_uni1"
        },
        {
            "fieldname": "disability_type",
            "fieldtype": "Data",
            "label": "Disability Type",
            "depends_on": "eval:doc.physically_challenged==1",
            "insert_after": "physically_challenged"
        },
        {
            "fieldname": "blood_group",
            "fieldtype": "Select",
            "label": "Blood Group",
            "options": "\nA+\nA-\nB+\nB-\nAB+\nAB-\nO+\nO-",
            "insert_after": "disability_type"
        },
        
        # Hostel Section
        {
            "fieldname": "hostel_section",
            "fieldtype": "Section Break",
            "label": "Hostel Information",
            "collapsible": 1,
            "insert_after": "blood_group"
        },
        {
            "fieldname": "hostel_required",
            "fieldtype": "Check",
            "label": "Hostel Required",
            "insert_after": "hostel_section"
        },
        {
            "fieldname": "current_hostel",
            "fieldtype": "Link",
            "label": "Current Hostel",
            "options": "Hostel",
            "depends_on": "eval:doc.hostel_required==1",
            "insert_after": "hostel_required"
        },
        {
            "fieldname": "hostel_room",
            "fieldtype": "Link",
            "label": "Hostel Room",
            "options": "Hostel Room",
            "depends_on": "eval:doc.hostel_required==1",
            "insert_after": "current_hostel"
        },
        
        # Transport Section
        {
            "fieldname": "transport_section",
            "fieldtype": "Section Break",
            "label": "Transport Information",
            "collapsible": 1,
            "insert_after": "hostel_room"
        },
        {
            "fieldname": "transport_required",
            "fieldtype": "Check",
            "label": "Transport Required",
            "insert_after": "transport_section"
        },
        {
            "fieldname": "transport_route",
            "fieldtype": "Link",
            "label": "Transport Route",
            "options": "Transport Route",
            "depends_on": "eval:doc.transport_required==1",
            "insert_after": "transport_required"
        },
        {
            "fieldname": "pickup_stop",
            "fieldtype": "Link",
            "label": "Pickup Stop",
            "options": "Vehicle Stop",
            "depends_on": "eval:doc.transport_required==1",
            "insert_after": "transport_route"
        },
        
        # Library Section
        {
            "fieldname": "library_section",
            "fieldtype": "Section Break",
            "label": "Library Information",
            "collapsible": 1,
            "insert_after": "pickup_stop"
        },
        {
            "fieldname": "library_card_number",
            "fieldtype": "Data",
            "label": "Library Card Number",
            "read_only": 1,
            "insert_after": "library_section"
        },
        {
            "fieldname": "library_member",
            "fieldtype": "Link",
            "label": "Library Member",
            "options": "Library Member",
            "read_only": 1,
            "insert_after": "library_card_number"
        },
        
        # Scholarship Section
        {
            "fieldname": "scholarship_section",
            "fieldtype": "Section Break",
            "label": "Scholarship Information",
            "collapsible": 1,
            "insert_after": "library_member"
        },
        {
            "fieldname": "scholarship_applicable",
            "fieldtype": "Check",
            "label": "Scholarship Applicable",
            "insert_after": "scholarship_section"
        },
        {
            "fieldname": "scholarship_type",
            "fieldtype": "Select",
            "label": "Scholarship Type",
            "options": "\nMerit Based\nMeans Based\nGovernment Scholarship\nInstitute Scholarship\nOther",
            "depends_on": "eval:doc.scholarship_applicable==1",
            "insert_after": "scholarship_applicable"
        },
        {
            "fieldname": "scholarship_percentage",
            "fieldtype": "Percent",
            "label": "Scholarship Percentage",
            "depends_on": "eval:doc.scholarship_applicable==1",
            "insert_after": "scholarship_type"
        },
        
        # Parent/Guardian Extended Info
        {
            "fieldname": "parent_extended_section",
            "fieldtype": "Section Break",
            "label": "Parent/Guardian Extended Information",
            "collapsible": 1,
            "insert_after": "scholarship_percentage"
        },
        {
            "fieldname": "father_occupation",
            "fieldtype": "Data",
            "label": "Father's Occupation",
            "insert_after": "parent_extended_section"
        },
        {
            "fieldname": "mother_occupation",
            "fieldtype": "Data",
            "label": "Mother's Occupation",
            "insert_after": "father_occupation"
        },
        {
            "fieldname": "annual_family_income",
            "fieldtype": "Currency",
            "label": "Annual Family Income",
            "insert_after": "mother_occupation"
        },
    ]
}
```

### Step 3.2: Course Custom Fields

Create `university_ems/university_ems/custom_fields/course_custom_fields.py`:

```python
"""Custom fields to be added to Course DocType"""

COURSE_CUSTOM_FIELDS = {
    "Course": [
        {
            "fieldname": "obe_section",
            "fieldtype": "Section Break",
            "label": "Outcome Based Education",
            "insert_after": "description"
        },
        {
            "fieldname": "course_outcomes",
            "fieldtype": "Table",
            "label": "Course Outcomes",
            "options": "Course Outcome Item",
            "insert_after": "obe_section"
        },
        {
            "fieldname": "credit_section",
            "fieldtype": "Section Break",
            "label": "Credit Information",
            "insert_after": "course_outcomes"
        },
        {
            "fieldname": "course_type",
            "fieldtype": "Select",
            "label": "Course Type",
            "options": "\nTheory\nPractical\nTheory + Practical\nProject\nSeminar\nInternship",
            "insert_after": "credit_section"
        },
        {
            "fieldname": "credit_hours",
            "fieldtype": "Float",
            "label": "Credit Hours",
            "insert_after": "course_type"
        },
        {
            "fieldname": "lecture_hours",
            "fieldtype": "Float",
            "label": "Lecture Hours per Week",
            "insert_after": "credit_hours"
        },
        {
            "fieldname": "tutorial_hours",
            "fieldtype": "Float",
            "label": "Tutorial Hours per Week",
            "insert_after": "lecture_hours"
        },
        {
            "fieldname": "practical_hours",
            "fieldtype": "Float",
            "label": "Practical Hours per Week",
            "insert_after": "tutorial_hours"
        },
        {
            "fieldname": "column_break_credit",
            "fieldtype": "Column Break",
            "insert_after": "practical_hours"
        },
        {
            "fieldname": "internal_marks",
            "fieldtype": "Int",
            "label": "Internal Marks",
            "default": "30",
            "insert_after": "column_break_credit"
        },
        {
            "fieldname": "external_marks",
            "fieldtype": "Int",
            "label": "External Marks",
            "default": "70",
            "insert_after": "internal_marks"
        },
        {
            "fieldname": "total_marks",
            "fieldtype": "Int",
            "label": "Total Marks",
            "default": "100",
            "read_only": 1,
            "insert_after": "external_marks"
        },
        {
            "fieldname": "passing_marks",
            "fieldtype": "Int",
            "label": "Passing Marks",
            "default": "40",
            "insert_after": "total_marks"
        },
        {
            "fieldname": "prerequisite_section",
            "fieldtype": "Section Break",
            "label": "Prerequisites",
            "insert_after": "passing_marks"
        },
        {
            "fieldname": "prerequisites",
            "fieldtype": "Table MultiSelect",
            "label": "Prerequisite Courses",
            "options": "Course Prerequisite",
            "insert_after": "prerequisite_section"
        },
    ]
}
```

### Step 3.3: Employee (Faculty) Custom Fields

Create `university_ems/university_ems/custom_fields/employee_custom_fields.py`:

```python
"""Custom fields to be added to Employee DocType for Faculty"""

EMPLOYEE_CUSTOM_FIELDS = {
    "Employee": [
        {
            "fieldname": "faculty_section",
            "fieldtype": "Section Break",
            "label": "Faculty Information",
            "depends_on": "eval:doc.employment_type=='Faculty'",
            "insert_after": "employment_type"
        },
        {
            "fieldname": "faculty_id",
            "fieldtype": "Data",
            "label": "Faculty ID",
            "insert_after": "faculty_section"
        },
        {
            "fieldname": "designation_category",
            "fieldtype": "Select",
            "label": "Designation Category",
            "options": "\nProfessor\nAssociate Professor\nAssistant Professor\nLecturer\nVisiting Faculty\nAdjunct Faculty",
            "insert_after": "faculty_id"
        },
        {
            "fieldname": "specialization",
            "fieldtype": "Data",
            "label": "Specialization",
            "insert_after": "designation_category"
        },
        {
            "fieldname": "column_break_faculty",
            "fieldtype": "Column Break",
            "insert_after": "specialization"
        },
        {
            "fieldname": "phd_guide",
            "fieldtype": "Check",
            "label": "PhD Guide",
            "insert_after": "column_break_faculty"
        },
        {
            "fieldname": "max_phd_students",
            "fieldtype": "Int",
            "label": "Max PhD Students Allowed",
            "depends_on": "eval:doc.phd_guide==1",
            "insert_after": "phd_guide"
        },
        {
            "fieldname": "current_phd_students",
            "fieldtype": "Int",
            "label": "Current PhD Students",
            "read_only": 1,
            "insert_after": "max_phd_students"
        },
        
        # Research Section
        {
            "fieldname": "research_section",
            "fieldtype": "Section Break",
            "label": "Research Information",
            "collapsible": 1,
            "insert_after": "current_phd_students"
        },
        {
            "fieldname": "research_areas",
            "fieldtype": "Small Text",
            "label": "Research Areas",
            "insert_after": "research_section"
        },
        {
            "fieldname": "google_scholar_id",
            "fieldtype": "Data",
            "label": "Google Scholar ID",
            "insert_after": "research_areas"
        },
        {
            "fieldname": "orcid_id",
            "fieldtype": "Data",
            "label": "ORCID ID",
            "insert_after": "google_scholar_id"
        },
        {
            "fieldname": "column_break_research",
            "fieldtype": "Column Break",
            "insert_after": "orcid_id"
        },
        {
            "fieldname": "publications_count",
            "fieldtype": "Int",
            "label": "Publications Count",
            "read_only": 1,
            "insert_after": "column_break_research"
        },
        {
            "fieldname": "patents_count",
            "fieldtype": "Int",
            "label": "Patents Count",
            "read_only": 1,
            "insert_after": "publications_count"
        },
        {
            "fieldname": "h_index",
            "fieldtype": "Float",
            "label": "H-Index",
            "insert_after": "patents_count"
        },
        
        # Workload Section
        {
            "fieldname": "workload_section",
            "fieldtype": "Section Break",
            "label": "Workload Information",
            "collapsible": 1,
            "insert_after": "h_index"
        },
        {
            "fieldname": "max_hours_per_week",
            "fieldtype": "Float",
            "label": "Max Teaching Hours/Week",
            "default": "18",
            "insert_after": "workload_section"
        },
        {
            "fieldname": "current_hours_per_week",
            "fieldtype": "Float",
            "label": "Current Teaching Hours/Week",
            "read_only": 1,
            "insert_after": "max_hours_per_week"
        },
    ]
}
```

---

## Part 4: Installation Script

### Step 4.1: Create Install Script

Create `university_ems/install.py`:

```python
"""Installation script for University EMS"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from university_ems.university_ems.custom_fields.student_custom_fields import STUDENT_CUSTOM_FIELDS
from university_ems.university_ems.custom_fields.course_custom_fields import COURSE_CUSTOM_FIELDS
from university_ems.university_ems.custom_fields.employee_custom_fields import EMPLOYEE_CUSTOM_FIELDS


def after_install():
    """Run after app installation"""
    print("Setting up University EMS...")
    
    # Create custom fields
    create_all_custom_fields()
    
    # Setup roles
    setup_roles()
    
    # Setup workspaces
    setup_workspaces()
    
    # Setup default settings
    setup_default_settings()
    
    # Setup print formats
    setup_print_formats()
    
    print("University EMS setup complete!")


def create_all_custom_fields():
    """Create all custom fields for ERPNext DocTypes"""
    print("Creating custom fields...")
    
    # Student custom fields
    create_custom_fields(STUDENT_CUSTOM_FIELDS)
    
    # Course custom fields
    create_custom_fields(COURSE_CUSTOM_FIELDS)
    
    # Employee custom fields
    create_custom_fields(EMPLOYEE_CUSTOM_FIELDS)
    
    frappe.db.commit()
    print("Custom fields created successfully!")


def setup_roles():
    """Setup custom roles for university"""
    roles = [
        {
            "role_name": "Hostel Warden",
            "desk_access": 1,
            "description": "Manages hostel operations"
        },
        {
            "role_name": "Transport Manager",
            "desk_access": 1,
            "description": "Manages transport operations"
        },
        {
            "role_name": "Librarian",
            "desk_access": 1,
            "description": "Manages library operations"
        },
        {
            "role_name": "Examination Controller",
            "desk_access": 1,
            "description": "Manages examination operations"
        },
        {
            "role_name": "Placement Officer",
            "desk_access": 1,
            "description": "Manages placement operations"
        },
        {
            "role_name": "IQAC Coordinator",
            "desk_access": 1,
            "description": "Manages accreditation and quality"
        },
        {
            "role_name": "Research Coordinator",
            "desk_access": 1,
            "description": "Manages research activities"
        },
        {
            "role_name": "Alumni Coordinator",
            "desk_access": 1,
            "description": "Manages alumni relations"
        },
        {
            "role_name": "Department Head",
            "desk_access": 1,
            "description": "Head of academic department"
        },
        {
            "role_name": "Dean",
            "desk_access": 1,
            "description": "Dean of faculty/school"
        },
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.new_doc("Role")
            role.role_name = role_data["role_name"]
            role.desk_access = role_data["desk_access"]
            role.insert(ignore_permissions=True)
            print(f"Created role: {role_data['role_name']}")
    
    frappe.db.commit()


def setup_workspaces():
    """Setup workspaces for different modules"""
    # Workspaces are typically created via JSON fixtures
    # This function can be used to verify and setup workspaces programmatically
    pass


def setup_default_settings():
    """Setup default settings for University EMS"""
    # Create University Settings if not exists
    if not frappe.db.exists("University Settings", "University Settings"):
        settings = frappe.new_doc("University Settings")
        settings.insert(ignore_permissions=True)
        print("Created University Settings")
    
    frappe.db.commit()


def setup_print_formats():
    """Setup print formats for various documents"""
    # Print formats are typically created via JSON fixtures
    pass
```

---

## Part 5: API Layer for Module Integration

### Step 5.1: Student API

Create `university_ems/api/student_api.py`:

```python
"""API endpoints for Student operations"""

import frappe
from frappe import _


@frappe.whitelist()
def get_student_complete_profile(student_id):
    """Get complete student profile including all module data"""
    
    if not frappe.has_permission("Student", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    student = frappe.get_doc("Student", student_id)
    
    profile = {
        "basic_info": {
            "name": student.name,
            "student_name": student.student_name,
            "student_email_id": student.student_email_id,
            "admission_number": student.get("admission_number"),
            "prn_number": student.get("prn_number"),
        },
        "academic_info": get_academic_info(student_id),
        "hostel_info": get_hostel_info(student_id) if student.get("hostel_required") else None,
        "transport_info": get_transport_info(student_id) if student.get("transport_required") else None,
        "library_info": get_library_info(student_id),
        "fee_info": get_fee_info(student_id),
        "attendance_info": get_attendance_summary(student_id),
        "placement_info": get_placement_info(student_id),
    }
    
    return profile


def get_academic_info(student_id):
    """Get student's academic information"""
    enrollments = frappe.get_all(
        "Program Enrollment",
        filters={"student": student_id},
        fields=["name", "program", "academic_year", "academic_term", "enrollment_date"]
    )
    
    return {
        "enrollments": enrollments,
        "current_program": enrollments[0] if enrollments else None
    }


def get_hostel_info(student_id):
    """Get student's hostel information"""
    allocation = frappe.get_all(
        "Hostel Room Allocation",
        filters={"student": student_id, "status": "Active"},
        fields=["hostel", "room", "bed_number", "from_date", "to_date"]
    )
    
    return allocation[0] if allocation else None


def get_transport_info(student_id):
    """Get student's transport information"""
    assignment = frappe.get_all(
        "Student Route Assignment",
        filters={"student": student_id, "status": "Active"},
        fields=["route", "vehicle", "pickup_stop", "pickup_time", "drop_time"]
    )
    
    return assignment[0] if assignment else None


def get_library_info(student_id):
    """Get student's library information"""
    member = frappe.get_all(
        "Library Member",
        filters={"student": student_id, "status": "Active"},
        fields=["name", "library_card_number", "membership_type"]
    )
    
    if not member:
        return None
    
    # Get current issues
    current_issues = frappe.get_all(
        "Library Transaction",
        filters={
            "library_member": member[0]["name"],
            "type": "Issue",
            "docstatus": 1
        },
        fields=["article", "from_date", "to_date"]
    )
    
    return {
        "membership": member[0],
        "current_issues": current_issues,
        "books_issued_count": len(current_issues)
    }


def get_fee_info(student_id):
    """Get student's fee information"""
    fees = frappe.get_all(
        "Fees",
        filters={"student": student_id},
        fields=["name", "due_date", "grand_total", "outstanding_amount", "docstatus"],
        order_by="due_date desc",
        limit=10
    )
    
    total_outstanding = sum([f["outstanding_amount"] for f in fees if f["outstanding_amount"]])
    
    return {
        "recent_fees": fees,
        "total_outstanding": total_outstanding
    }


def get_attendance_summary(student_id):
    """Get student's attendance summary"""
    from frappe.utils import getdate, add_months
    
    today = getdate()
    start_date = add_months(today, -3)
    
    attendance = frappe.get_all(
        "Student Attendance",
        filters={
            "student": student_id,
            "date": ["between", [start_date, today]]
        },
        fields=["status", "date"]
    )
    
    present = len([a for a in attendance if a["status"] == "Present"])
    absent = len([a for a in attendance if a["status"] == "Absent"])
    total = len(attendance)
    
    return {
        "total_days": total,
        "present": present,
        "absent": absent,
        "percentage": round((present / total * 100), 2) if total > 0 else 0
    }


def get_placement_info(student_id):
    """Get student's placement information"""
    applications = frappe.get_all(
        "Student Application",
        filters={"student": student_id},
        fields=["job_opening", "company", "status", "applied_on"]
    )
    
    offers = frappe.get_all(
        "Placement Offer",
        filters={"student": student_id},
        fields=["company", "designation", "package", "status"]
    )
    
    return {
        "applications": applications,
        "offers": offers,
        "is_placed": any(o["status"] == "Accepted" for o in offers)
    }


@frappe.whitelist()
def bulk_allocate_hostel(students, hostel, academic_year):
    """Bulk allocate hostel rooms to students"""
    if not frappe.has_permission("Hostel Room Allocation", "create"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    import json
    students = json.loads(students) if isinstance(students, str) else students
    
    results = []
    for student_id in students:
        try:
            # Find available room
            available_room = get_available_hostel_room(hostel)
            if not available_room:
                results.append({
                    "student": student_id,
                    "status": "Failed",
                    "message": "No rooms available"
                })
                continue
            
            # Create allocation
            allocation = frappe.new_doc("Hostel Room Allocation")
            allocation.student = student_id
            allocation.hostel = hostel
            allocation.room = available_room
            allocation.academic_year = academic_year
            allocation.insert()
            allocation.submit()
            
            results.append({
                "student": student_id,
                "status": "Success",
                "room": available_room
            })
        except Exception as e:
            results.append({
                "student": student_id,
                "status": "Failed",
                "message": str(e)
            })
    
    return results


def get_available_hostel_room(hostel):
    """Find an available room in the hostel"""
    rooms = frappe.get_all(
        "Hostel Room",
        filters={
            "hostel": hostel,
            "status": "Available"
        },
        fields=["name"],
        order_by="room_number"
    )
    
    return rooms[0]["name"] if rooms else None
```

---

## Part 6: Integration Checklist

### ERPNext Module Integration Matrix

| University Module | Integrates With | Integration Type | Priority |
|-------------------|-----------------|------------------|----------|
| Hostel Management | Student, Fees, Assets | DocType Link, Fee Component | High |
| Transport Management | Student, Fees, HR, Assets | DocType Link, Fee Component | High |
| Library Management | Student, Fees, Stock | DocType Link, Fine Integration | High |
| Advanced Examination | Education, Student | Extends Assessment | High |
| Training & Placement | Student, Program | DocType Link | High |
| NAAC Accreditation | All Modules | Data Aggregation | High |
| OBE System | Course, Assessment | Extends Course | High |
| CBCS System | Program, Course | Extends Education | Medium |
| Research Management | Employee, Projects | DocType Link | Medium |
| Alumni Management | Student | Alumni Creation | Medium |
| Grievance Management | Student, Employee | DocType Link | Low |
| Sports & Cultural | Student, Projects | Event Management | Low |

### Integration Implementation Checklist

#### Phase 1: Core Integration
- [ ] Create custom fields on Student DocType
- [ ] Create custom fields on Course DocType
- [ ] Create custom fields on Employee DocType
- [ ] Setup fee component integration for Hostel
- [ ] Setup fee component integration for Transport
- [ ] Setup fee component integration for Library fines
- [ ] Create student lifecycle hooks
- [ ] Create enrollment hooks

#### Phase 2: Module Linking
- [ ] Link Hostel allocation to Student
- [ ] Link Transport assignment to Student
- [ ] Link Library membership to Student
- [ ] Link Placement data to Student
- [ ] Link Research data to Employee (Faculty)

#### Phase 3: Data Flow
- [ ] Automatic library member creation on enrollment
- [ ] Fee schedule update for hostel/transport
- [ ] Attendance consolidation from all sources
- [ ] Academic record integration with examination

#### Phase 4: Reporting Integration
- [ ] Unified student report
- [ ] Department-wise analytics
- [ ] NAAC data aggregation
- [ ] Placement statistics dashboard

---

## Next Steps

After completing this setup:

1. **Install the App**:
   ```bash
   bench --site university.localhost install-app university_ems
   ```

2. **Proceed to Document 03**: Module-wise Implementation Checklist

3. **Begin Module Development**: Start with Hostel Management (Priority 1)

---

**Document End**
