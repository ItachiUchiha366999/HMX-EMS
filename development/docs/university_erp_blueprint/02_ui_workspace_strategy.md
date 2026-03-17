# University ERP - UI & Workspace Strategy

## Overview

This document details how to create a dedicated University product experience by implementing custom workspaces, role-based sidebars, and hiding all ERPNext generic UI elements.

---

## Workspace Architecture

### Workspace Directory Structure
```
university_erp/
├── academics/
│   └── workspace/
│       └── academics/
│           └── academics.json
├── admissions/
│   └── workspace/
│       └── admissions/
│           └── admissions.json
├── student_info/
│   └── workspace/
│       └── student_information/
│           └── student_information.json
├── examinations/
│   └── workspace/
│       └── examinations/
│           └── examinations.json
├── fees/
│   └── workspace/
│       └── university_finance/
│           └── university_finance.json
├── university_hr/
│   └── workspace/
│       └── university_hr/
│           └── university_hr.json
```

---

## Role-Based Workspace Access

### University Roles Matrix

| Role | Workspaces Visible |
|------|-------------------|
| University Student | Student Portal, My Courses, My Results, Fee Status |
| University Faculty | Faculty Dashboard, My Classes, Attendance, Grade Entry |
| University HOD | Department Dashboard, Faculty Management, Course Approval |
| University Exam Cell | Examinations, Results Processing, Hall Tickets |
| University Finance | Finance Dashboard, Fee Collection, Reports |
| University HR Admin | HR Dashboard, Payroll, Leave Management |
| University Registrar | Admissions, Student Records, Certificates |
| University Admin | All Workspaces + Settings |
| University Librarian | Library Management |
| University Warden | Hostel Management |
| University Placement Officer | Placement & Career |

---

## Complete Workspace Definitions

### 1. University Home (Admin Dashboard)
```json
{
    "doctype": "Workspace",
    "name": "University Home",
    "module": "University ERP",
    "label": "University Home",
    "icon": "university",
    "indicator_color": "blue",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"}
    ],
    "charts": [
        {
            "label": "Student Enrollment Trend",
            "chart_name": "Student Enrollment Trend",
            "chart_type": "Group By"
        },
        {
            "label": "Fee Collection Status",
            "chart_name": "Fee Collection Status",
            "chart_type": "Sum"
        }
    ],
    "shortcuts": [
        {
            "label": "Students",
            "link_to": "University Student",
            "type": "DocType",
            "color": "blue",
            "stats_filter": "[[\"status\", \"=\", \"Active\"]]"
        },
        {
            "label": "Faculty",
            "link_to": "University Faculty",
            "type": "DocType",
            "color": "green"
        },
        {
            "label": "Today's Attendance",
            "link_to": "Daily Attendance Report",
            "type": "Report"
        },
        {
            "label": "Pending Fees",
            "link_to": "Fee Defaulters",
            "type": "Report",
            "color": "red"
        }
    ],
    "number_cards": [
        {
            "label": "Total Students",
            "number_card_name": "Total Active Students"
        },
        {
            "label": "Total Faculty",
            "number_card_name": "Total Faculty"
        },
        {
            "label": "Fee Collected (Month)",
            "number_card_name": "Monthly Fee Collection"
        },
        {
            "label": "Attendance Today",
            "number_card_name": "Today Attendance Percentage"
        }
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Quick Actions"
        },
        {
            "type": "Link",
            "label": "New Admission",
            "link_to": "Admission Application",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Register Student",
            "link_to": "University Student",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Collect Fee",
            "link_to": "Fee Payment",
            "link_type": "DocType"
        }
    ]
}
```

### 2. Academics Workspace
```json
{
    "doctype": "Workspace",
    "name": "Academics",
    "module": "University ERP",
    "label": "Academics",
    "icon": "book",
    "indicator_color": "green",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University Registrar"},
        {"role": "University HOD"},
        {"role": "University Faculty"}
    ],
    "shortcuts": [
        {
            "label": "Programs",
            "link_to": "University Program",
            "type": "DocType"
        },
        {
            "label": "Courses",
            "link_to": "University Course",
            "type": "DocType"
        },
        {
            "label": "Timetable",
            "link_to": "Class Timetable",
            "type": "DocType"
        }
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Programs & Curriculum"
        },
        {
            "type": "Link",
            "label": "Program",
            "link_to": "University Program",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Department",
            "link_to": "University Department",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Course",
            "link_to": "University Course",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Semester",
            "link_to": "Academic Semester",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Academic Year",
            "link_to": "Academic Year",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Scheduling"
        },
        {
            "type": "Link",
            "label": "Class Timetable",
            "link_to": "Class Timetable",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Room Allocation",
            "link_to": "Room Allocation",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Academic Calendar",
            "link_to": "Academic Calendar",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Reports"
        },
        {
            "type": "Link",
            "label": "Program Wise Students",
            "link_to": "Program Wise Student Report",
            "link_type": "Report"
        },
        {
            "type": "Link",
            "label": "Course Load Analysis",
            "link_to": "Course Load Analysis",
            "link_type": "Report"
        }
    ]
}
```

### 3. Student Information Workspace
```json
{
    "doctype": "Workspace",
    "name": "Student Information",
    "module": "University ERP",
    "label": "Student Records",
    "icon": "users",
    "indicator_color": "blue",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University Registrar"}
    ],
    "shortcuts": [
        {
            "label": "All Students",
            "link_to": "University Student",
            "type": "DocType"
        },
        {
            "label": "Active Students",
            "link_to": "University Student",
            "type": "DocType",
            "stats_filter": "[[\"status\", \"=\", \"Active\"]]"
        }
    ],
    "number_cards": [
        {
            "label": "Total Students",
            "number_card_name": "Total Students"
        },
        {
            "label": "Active Students",
            "number_card_name": "Active Students"
        },
        {
            "label": "Alumni",
            "number_card_name": "Alumni Count"
        }
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Student Management"
        },
        {
            "type": "Link",
            "label": "Student",
            "link_to": "University Student",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Student Group",
            "link_to": "Student Group",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Student Batch",
            "link_to": "Student Batch",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Enrollment"
        },
        {
            "type": "Link",
            "label": "Program Enrollment",
            "link_to": "Program Enrollment",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Course Enrollment",
            "link_to": "Course Enrollment",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Documents"
        },
        {
            "type": "Link",
            "label": "Student Certificate",
            "link_to": "Student Certificate",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "ID Card",
            "link_to": "Student ID Card",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Reports"
        },
        {
            "type": "Link",
            "label": "Student Directory",
            "link_to": "Student Directory Report",
            "link_type": "Report"
        }
    ]
}
```

### 4. Admissions Workspace
```json
{
    "doctype": "Workspace",
    "name": "Admissions",
    "module": "University ERP",
    "label": "Admissions",
    "icon": "file-text",
    "indicator_color": "orange",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University Registrar"}
    ],
    "charts": [
        {
            "label": "Applications by Program",
            "chart_name": "Applications by Program"
        }
    ],
    "number_cards": [
        {
            "label": "Total Applications",
            "number_card_name": "Total Applications"
        },
        {
            "label": "Pending Review",
            "number_card_name": "Pending Applications"
        },
        {
            "label": "Approved",
            "number_card_name": "Approved Applications"
        }
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Application Processing"
        },
        {
            "type": "Link",
            "label": "Admission Application",
            "link_to": "Admission Application",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Inquiry",
            "link_to": "Admission Inquiry",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Merit List",
            "link_to": "Merit List",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Configuration"
        },
        {
            "type": "Link",
            "label": "Admission Cycle",
            "link_to": "Admission Cycle",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Seat Matrix",
            "link_to": "Seat Matrix",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Admission Criteria",
            "link_to": "Admission Criteria",
            "link_type": "DocType"
        }
    ]
}
```

### 5. Examinations Workspace
```json
{
    "doctype": "Workspace",
    "name": "Examinations",
    "module": "University ERP",
    "label": "Examinations",
    "icon": "clipboard",
    "indicator_color": "red",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University Exam Cell"}
    ],
    "shortcuts": [
        {
            "label": "Upcoming Exams",
            "link_to": "Examination",
            "type": "DocType",
            "stats_filter": "[[\"exam_date\", \">=\", \"Today\"]]"
        },
        {
            "label": "Result Entry",
            "link_to": "Examination Result",
            "type": "DocType"
        }
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Examination Management"
        },
        {
            "type": "Link",
            "label": "Examination",
            "link_to": "Examination",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Exam Schedule",
            "link_to": "Exam Schedule",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Hall Ticket",
            "link_to": "Hall Ticket",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Seating Arrangement",
            "link_to": "Seating Arrangement",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Results"
        },
        {
            "type": "Link",
            "label": "Examination Result",
            "link_to": "Examination Result",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Grade Card",
            "link_to": "Grade Card",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Transcript",
            "link_to": "Student Transcript",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Assessment"
        },
        {
            "type": "Link",
            "label": "Internal Assessment",
            "link_to": "Internal Assessment",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Assignment",
            "link_to": "Course Assignment",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Configuration"
        },
        {
            "type": "Link",
            "label": "Grading Scale",
            "link_to": "Grading Scale",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Exam Type",
            "link_to": "Exam Type",
            "link_type": "DocType"
        }
    ]
}
```

### 6. University Finance Workspace
```json
{
    "doctype": "Workspace",
    "name": "University Finance",
    "module": "University ERP",
    "label": "Finance",
    "icon": "dollar-sign",
    "indicator_color": "green",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University Finance"}
    ],
    "charts": [
        {
            "label": "Fee Collection Trend",
            "chart_name": "Fee Collection Trend"
        }
    ],
    "number_cards": [
        {
            "label": "Total Collected",
            "number_card_name": "Total Fee Collected"
        },
        {
            "label": "Pending Amount",
            "number_card_name": "Pending Fee Amount"
        },
        {
            "label": "Scholarships Given",
            "number_card_name": "Scholarships Amount"
        }
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Fee Management"
        },
        {
            "type": "Link",
            "label": "Fee Payment",
            "link_to": "Fee Payment",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Student Fee",
            "link_to": "Student Fee",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Fee Structure",
            "link_to": "Fee Structure",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Fee Category",
            "link_to": "Fee Category",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Scholarships & Concessions"
        },
        {
            "type": "Link",
            "label": "Scholarship",
            "link_to": "Scholarship",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Fee Concession",
            "link_to": "Fee Concession",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Fee Waiver",
            "link_to": "Fee Waiver",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Reports"
        },
        {
            "type": "Link",
            "label": "Fee Collection Report",
            "link_to": "Fee Collection Report",
            "link_type": "Report"
        },
        {
            "type": "Link",
            "label": "Fee Defaulters",
            "link_to": "Fee Defaulters Report",
            "link_type": "Report"
        },
        {
            "type": "Link",
            "label": "Program Wise Fee",
            "link_to": "Program Wise Fee Report",
            "link_type": "Report"
        }
    ]
}
```

### 7. University HR Workspace
```json
{
    "doctype": "Workspace",
    "name": "University HR",
    "module": "University ERP",
    "label": "Human Resources",
    "icon": "users",
    "indicator_color": "purple",
    "is_standard": 1,
    "public": 1,
    "roles": [
        {"role": "University Admin"},
        {"role": "University HR Admin"}
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Faculty & Staff"
        },
        {
            "type": "Link",
            "label": "Faculty",
            "link_to": "University Faculty",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Staff",
            "link_to": "University Staff",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Department",
            "link_to": "University Department",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Workload"
        },
        {
            "type": "Link",
            "label": "Teaching Assignment",
            "link_to": "Teaching Assignment",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Faculty Workload",
            "link_to": "Faculty Workload",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Leave & Attendance"
        },
        {
            "type": "Link",
            "label": "Leave Application",
            "link_to": "University Leave Application",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Attendance",
            "link_to": "Faculty Attendance",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Payroll"
        },
        {
            "type": "Link",
            "label": "Process Payroll",
            "link_to": "University Payroll Entry",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Salary Structure",
            "link_to": "University Salary Structure",
            "link_type": "DocType"
        },
        {
            "type": "Card Break",
            "label": "Performance"
        },
        {
            "type": "Link",
            "label": "Faculty Appraisal",
            "link_to": "Faculty Appraisal",
            "link_type": "DocType"
        },
        {
            "type": "Link",
            "label": "Publications",
            "link_to": "Faculty Publication",
            "link_type": "DocType"
        }
    ]
}
```

---

## Sidebar Configuration by Role

### Student Sidebar
```python
# Visible Workspaces for Students
student_workspaces = [
    "Student Portal",      # Primary dashboard
    "My Courses",          # Enrolled courses
    "My Results",          # Grades & transcripts
    "Fee Status",          # Fee dues & payments
    "Library",             # Library services
    "LMS",                 # Online learning
]
```

### Faculty Sidebar
```python
faculty_workspaces = [
    "Faculty Dashboard",   # Primary dashboard
    "My Classes",          # Teaching assignments
    "Attendance Entry",    # Mark attendance
    "Grade Entry",         # Enter marks
    "Research",            # Publications & projects
]
```

### HOD Sidebar
```python
hod_workspaces = [
    "Department Dashboard",
    "Faculty Management",
    "Course Management",
    "Academics",
    "Student Records",
]
```

### Exam Cell Sidebar
```python
exam_cell_workspaces = [
    "Examinations",
    "Result Processing",
    "Student Records",
]
```

### Finance Sidebar
```python
finance_workspaces = [
    "University Finance",
    "Reports",
]
```

### HR Admin Sidebar
```python
hr_workspaces = [
    "University HR",
    "Payroll",
    "Reports",
]
```

### Admin Sidebar
```python
admin_workspaces = [
    "University Home",
    "Academics",
    "Admissions",
    "Student Information",
    "Examinations",
    "University Finance",
    "University HR",
    "Hostel",
    "Transport",
    "Library",
    "Placement",
    "Settings",
]
```

---

## Client Script for Role-Based Sidebar

```javascript
// university_erp/public/js/sidebar_controller.js

frappe.provide("university_erp.sidebar");

university_erp.sidebar.setup = function() {
    // Get user roles
    const roles = frappe.user_roles;

    // Define workspace visibility per role
    const role_workspaces = {
        "University Student": [
            "Student Portal", "My Courses", "My Results",
            "Fee Status", "Library", "LMS"
        ],
        "University Faculty": [
            "Faculty Dashboard", "My Classes", "Attendance Entry",
            "Grade Entry", "Research"
        ],
        "University HOD": [
            "Department Dashboard", "Faculty Management",
            "Course Management", "Academics", "Student Records"
        ],
        "University Exam Cell": [
            "Examinations", "Result Processing", "Student Records"
        ],
        "University Finance": [
            "University Finance", "Reports"
        ],
        "University HR Admin": [
            "University HR", "Payroll", "Reports"
        ],
        "University Admin": null  // null means all workspaces
    };

    // Collect allowed workspaces for current user
    let allowed_workspaces = new Set();

    roles.forEach(role => {
        if (role_workspaces[role] === null) {
            // Admin - allow all
            allowed_workspaces = null;
            return;
        }
        if (role_workspaces[role]) {
            role_workspaces[role].forEach(ws => allowed_workspaces.add(ws));
        }
    });

    // Filter sidebar if not admin
    if (allowed_workspaces !== null) {
        university_erp.sidebar.filter_workspaces(allowed_workspaces);
    }
};

university_erp.sidebar.filter_workspaces = function(allowed) {
    // Hide workspaces not in allowed list
    $(".workspace-sidebar-item").each(function() {
        const workspace_name = $(this).data("workspace");
        if (!allowed.has(workspace_name)) {
            $(this).hide();
        }
    });
};

// Initialize on page load
$(document).ready(function() {
    university_erp.sidebar.setup();
});
```

---

## Hiding ERPNext Default Workspaces

### Method 1: Property Setter (Fixtures)
```json
[
    {
        "doctype": "Property Setter",
        "doc_type": "Workspace",
        "property": "public",
        "value": "0",
        "property_type": "Check",
        "doctype_or_field": "DocType"
    }
]
```

### Method 2: After Install Hook
```python
def hide_default_workspaces():
    """Hide all ERPNext default workspaces"""
    import frappe

    erpnext_workspaces = [
        "Home", "Accounting", "Stock", "Selling", "Buying",
        "Manufacturing", "CRM", "HR", "Payroll", "Projects",
        "Assets", "Support", "Quality", "Website", "Settings"
    ]

    for ws in erpnext_workspaces:
        if frappe.db.exists("Workspace", ws):
            frappe.db.set_value("Workspace", ws, "public", 0)
            frappe.db.set_value("Workspace", ws, "restrict_to_domain", "Hidden")

    frappe.db.commit()
```

### Method 3: Runtime Override
```python
# In boot_session hook
def boot_session(bootinfo):
    # Filter allowed workspaces
    allowed_prefixes = ["University", "Student", "Faculty", "Exam", "Admission"]

    if bootinfo.get("allowed_workspaces"):
        bootinfo["allowed_workspaces"] = [
            ws for ws in bootinfo["allowed_workspaces"]
            if any(ws.startswith(prefix) for prefix in allowed_prefixes)
        ]
```

---

## Global Search Restriction

### Override Search Results
```javascript
// university_erp/public/js/search_override.js

frappe.provide("university_erp.search");

// Override AwesomeBar search
const original_search = frappe.search.AwesomeBar.prototype.get_doctypes;

frappe.search.AwesomeBar.prototype.get_doctypes = function() {
    // Only return university doctypes
    return [
        "University Student",
        "University Faculty",
        "University Course",
        "University Program",
        "Admission Application",
        "Fee Payment",
        "Examination",
        "Examination Result",
        "University Department",
        "Student Group",
        "Teaching Assignment",
    ];
};

// Override global search API call
frappe.search.utils.get_crumb_html = function(txt, doctype) {
    // Filter out non-university doctypes
    const allowed_doctypes = university_erp.search.allowed_doctypes;
    if (!allowed_doctypes.includes(doctype)) {
        return "";
    }
    return this._original_get_crumb_html(txt, doctype);
};

university_erp.search.allowed_doctypes = [
    "University Student",
    "University Faculty",
    "University Course",
    "University Program",
    "University Department",
    "Admission Application",
    "Fee Payment",
    "Examination",
    "Examination Result",
    "Student Group",
    "Teaching Assignment",
    "Fee Structure",
    "Scholarship",
];
```

### Server-Side Search Filter
```python
# university_erp/overrides/search.py

import frappe
from frappe.utils import cint

def custom_search(doctype, txt, searchfield, start, page_len, filters):
    """Override search to only return university doctypes"""

    allowed_doctypes = [
        "University Student",
        "University Faculty",
        "University Course",
        "University Program",
        # ... add all university doctypes
    ]

    if doctype not in allowed_doctypes:
        return []

    # Call original search for allowed doctypes
    return frappe.get_list(
        doctype,
        filters=filters,
        fields=["name", searchfield],
        limit_start=start,
        limit_page_length=page_len
    )
```

---

## Portal Pages

### Student Portal Structure
```
www/
├── student-portal/
│   ├── index.html              # Dashboard
│   ├── index.py                # Controller
│   ├── courses/
│   │   ├── index.html          # My courses list
│   │   └── index.py
│   ├── results/
│   │   ├── index.html          # My results/grades
│   │   └── index.py
│   ├── fees/
│   │   ├── index.html          # Fee status
│   │   └── index.py
│   ├── attendance/
│   │   ├── index.html          # Attendance record
│   │   └── index.py
│   └── profile/
│       ├── index.html          # Student profile
│       └── index.py
```

### Faculty Portal Structure
```
www/
├── faculty-portal/
│   ├── index.html              # Dashboard
│   ├── classes/
│   │   ├── index.html          # My classes
│   │   └── index.py
│   ├── attendance/
│   │   ├── index.html          # Mark attendance
│   │   └── index.py
│   ├── grades/
│   │   ├── index.html          # Enter grades
│   │   └── index.py
│   └── profile/
│       ├── index.html          # Faculty profile
│       └── index.py
```

---

## Next Document

Continue to [03_module_mapping.md](03_module_mapping.md) for detailed mapping between University modules and ERPNext backend engines.
