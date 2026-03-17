# University ERP - Security & Permissions Model

## Overview

This document covers the comprehensive security model including role-based access, field-level permissions, audit logging, and data privacy requirements for the University ERP.

---

## Role Hierarchy

```
University Roles Hierarchy
│
├── University Admin (Super Admin)
│   └── Full access to all modules
│
├── University Registrar
│   ├── Admissions (Full)
│   ├── Student Records (Full)
│   ├── Certificates (Full)
│   └── Academics (Read)
│
├── University Finance
│   ├── Fees (Full)
│   ├── Scholarships (Full)
│   ├── Finance Reports (Full)
│   └── Student Records (Read - Limited)
│
├── University HR Admin
│   ├── Faculty/Staff (Full)
│   ├── Payroll (Full)
│   ├── Leave Management (Full)
│   └── Student Records (No Access)
│
├── University HOD
│   ├── Department Faculty (Full)
│   ├── Courses (Department - Full)
│   ├── Students (Department - Read)
│   └── Workload (Department - Full)
│
├── University Exam Cell
│   ├── Examinations (Full)
│   ├── Results (Full)
│   ├── Grading (Full)
│   └── Student Records (Read)
│
├── University Faculty
│   ├── Own Courses (Full)
│   ├── Own Students (Read)
│   ├── Attendance (Own Classes - Full)
│   ├── Grades (Own Courses - Full)
│   └── Own Profile (Read/Limited Edit)
│
└── University Student
    ├── Own Profile (Read/Limited Edit)
    ├── Own Courses (Read)
    ├── Own Results (Read)
    ├── Own Fees (Read)
    └── Own Attendance (Read)
```

---

## Role Definitions

### Fixture: Custom Roles
```json
[
    {
        "doctype": "Role",
        "role_name": "University Admin",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/university-home"
    },
    {
        "doctype": "Role",
        "role_name": "University Registrar",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/admissions"
    },
    {
        "doctype": "Role",
        "role_name": "University Finance",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/university-finance"
    },
    {
        "doctype": "Role",
        "role_name": "University HR Admin",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/university-hr"
    },
    {
        "doctype": "Role",
        "role_name": "University HOD",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/department-dashboard"
    },
    {
        "doctype": "Role",
        "role_name": "University Exam Cell",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/examinations"
    },
    {
        "doctype": "Role",
        "role_name": "University Faculty",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/faculty-dashboard"
    },
    {
        "doctype": "Role",
        "role_name": "University Student",
        "desk_access": 0,
        "is_custom": 1,
        "home_page": "/student-portal"
    },
    {
        "doctype": "Role",
        "role_name": "University Librarian",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/library"
    },
    {
        "doctype": "Role",
        "role_name": "University Warden",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/hostel"
    },
    {
        "doctype": "Role",
        "role_name": "University Placement Officer",
        "desk_access": 1,
        "is_custom": 1,
        "home_page": "/app/placement"
    }
]
```

---

## DocType Permission Matrix

### University Student
```json
{
    "doctype": "DocType",
    "name": "University Student",
    "permissions": [
        {
            "role": "University Admin",
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "submit": 0, "cancel": 0, "amend": 0,
            "export": 1, "import": 1, "report": 1, "print": 1
        },
        {
            "role": "University Registrar",
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "export": 1, "report": 1, "print": 1
        },
        {
            "role": "University HOD",
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "if_owner": 0,
            "match": "department"
        },
        {
            "role": "University Faculty",
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "if_owner": 0
        },
        {
            "role": "University Student",
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "if_owner": 1
        }
    ]
}
```

### Examination Result
```json
{
    "doctype": "DocType",
    "name": "Examination Result",
    "is_submittable": 1,
    "permissions": [
        {
            "role": "University Admin",
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "submit": 1, "cancel": 1, "amend": 1
        },
        {
            "role": "University Exam Cell",
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "submit": 1, "cancel": 0, "amend": 1
        },
        {
            "role": "University Faculty",
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "submit": 0, "cancel": 0,
            "match": "examiner"
        },
        {
            "role": "University Student",
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "if_owner": 0,
            "match": "student"
        }
    ]
}
```

### Fee Payment
```json
{
    "doctype": "DocType",
    "name": "Fee Payment",
    "is_submittable": 1,
    "permissions": [
        {
            "role": "University Admin",
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "submit": 1, "cancel": 1
        },
        {
            "role": "University Finance",
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "submit": 1, "cancel": 1
        },
        {
            "role": "University Student",
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "match": "student"
        }
    ]
}
```

---

## Permission Query Conditions

### Department-Based Access
```python
# university_erp/permissions.py

import frappe

def student_query(user):
    """Restrict student access based on user role"""
    if "University Admin" in frappe.get_roles(user):
        return ""

    if "University HOD" in frappe.get_roles(user):
        # HOD sees only department students
        faculty = frappe.db.get_value("University Faculty", {"user": user}, "name")
        if faculty:
            department = frappe.db.get_value("University Faculty", faculty, "department")
            return f"`tabUniversity Student`.program IN (SELECT name FROM `tabUniversity Program` WHERE department = '{department}')"

    if "University Faculty" in frappe.get_roles(user):
        # Faculty sees only their course students
        faculty = frappe.db.get_value("University Faculty", {"user": user}, "name")
        if faculty:
            return f"""
                `tabUniversity Student`.name IN (
                    SELECT DISTINCT student FROM `tabCourse Enrollment`
                    WHERE course IN (
                        SELECT course FROM `tabTeaching Assignment`
                        WHERE faculty = '{faculty}'
                    )
                )
            """

    if "University Student" in frappe.get_roles(user):
        # Student sees only themselves
        student = frappe.db.get_value("University Student", {"user": user}, "name")
        return f"`tabUniversity Student`.name = '{student}'"

    return "1=0"  # No access by default

def course_query(user):
    """Restrict course access based on department"""
    if "University Admin" in frappe.get_roles(user):
        return ""

    if "University HOD" in frappe.get_roles(user):
        faculty = frappe.db.get_value("University Faculty", {"user": user}, "name")
        if faculty:
            department = frappe.db.get_value("University Faculty", faculty, "department")
            return f"`tabUniversity Course`.department = '{department}'"

    return ""

def result_query(user):
    """Restrict result access"""
    if "University Admin" in frappe.get_roles(user):
        return ""

    if "University Exam Cell" in frappe.get_roles(user):
        return ""

    if "University Faculty" in frappe.get_roles(user):
        faculty = frappe.db.get_value("University Faculty", {"user": user}, "name")
        if faculty:
            return f"""
                `tabExamination Result`.course IN (
                    SELECT course FROM `tabTeaching Assignment`
                    WHERE faculty = '{faculty}'
                )
            """

    if "University Student" in frappe.get_roles(user):
        student = frappe.db.get_value("University Student", {"user": user}, "name")
        return f"`tabExamination Result`.student = '{student}'"

    return "1=0"
```

### has_permission Implementation
```python
# university_erp/permissions.py

def has_student_permission(doc, ptype, user):
    """Check if user has permission on specific student document"""
    if "University Admin" in frappe.get_roles(user):
        return True

    if "University Registrar" in frappe.get_roles(user):
        return True

    if "University Student" in frappe.get_roles(user):
        # Students can only access their own record
        student = frappe.db.get_value("University Student", {"user": user}, "name")
        return doc.name == student

    if "University Faculty" in frappe.get_roles(user):
        # Faculty can read students in their courses
        faculty = frappe.db.get_value("University Faculty", {"user": user}, "name")
        is_teaching = frappe.db.exists(
            "Course Enrollment",
            {
                "student": doc.name,
                "course": ["in", frappe.get_all(
                    "Teaching Assignment",
                    {"faculty": faculty},
                    pluck="course"
                )]
            }
        )
        return bool(is_teaching) and ptype == "read"

    return False

def has_result_permission(doc, ptype, user):
    """Check permission on examination result"""
    if "University Admin" in frappe.get_roles(user):
        return True

    if "University Exam Cell" in frappe.get_roles(user):
        return True

    if "University Faculty" in frappe.get_roles(user):
        faculty = frappe.db.get_value("University Faculty", {"user": user}, "name")
        # Check if faculty is assigned to this course
        is_assigned = frappe.db.exists(
            "Teaching Assignment",
            {"faculty": faculty, "course": doc.course}
        )
        if is_assigned:
            # Can write only if result is not submitted
            if ptype in ["write", "create"] and doc.docstatus == 0:
                return True
            if ptype == "read":
                return True
        return False

    if "University Student" in frappe.get_roles(user):
        student = frappe.db.get_value("University Student", {"user": user}, "name")
        # Students can only read their own submitted results
        return doc.student == student and doc.docstatus == 1 and ptype == "read"

    return False
```

---

## Field-Level Permissions

### Sensitive Field Protection
```python
# university_erp/field_permissions.py

FIELD_PERMISSIONS = {
    "University Student": {
        "bank_account_no": {"read": ["University Admin", "University Finance"]},
        "pan_number": {"read": ["University Admin", "University Finance"]},
        "aadhaar_number": {"read": ["University Admin", "University Registrar"]},
        "medical_records": {"read": ["University Admin", "University Registrar"]},
        "guardian_income": {"read": ["University Admin", "University Finance"]},
        "internal_notes": {"read": ["University Admin", "University Registrar"]},
    },
    "University Faculty": {
        "bank_account_no": {"read": ["University Admin", "University HR Admin"]},
        "pan": {"read": ["University Admin", "University HR Admin"]},
        "salary_details": {"read": ["University Admin", "University HR Admin"]},
        "appraisal_notes": {"read": ["University Admin", "University HR Admin", "University HOD"]},
    },
    "Examination Result": {
        "internal_marks": {"read": ["University Admin", "University Exam Cell", "University Faculty"]},
        "moderation_applied": {"read": ["University Admin", "University Exam Cell"]},
        "original_marks": {"read": ["University Admin", "University Exam Cell"]},
    }
}

def apply_field_permissions():
    """Apply field-level permissions via Property Setter"""
    for doctype, fields in FIELD_PERMISSIONS.items():
        for fieldname, perms in fields.items():
            # Create hidden permission for non-authorized roles
            frappe.make_property_setter({
                "doctype": doctype,
                "fieldname": fieldname,
                "property": "permlevel",
                "value": "1",  # Higher perm level
            })
```

### Property Setters for Field Permissions
```json
[
    {
        "doctype": "Property Setter",
        "doc_type": "University Student",
        "field_name": "bank_account_no",
        "property": "permlevel",
        "value": "1"
    },
    {
        "doctype": "Property Setter",
        "doc_type": "University Student",
        "field_name": "pan_number",
        "property": "permlevel",
        "value": "1"
    },
    {
        "doctype": "Property Setter",
        "doc_type": "Examination Result",
        "field_name": "moderation_applied",
        "property": "permlevel",
        "value": "2"
    }
]
```

### Role Permission for Permlevel
```json
[
    {
        "doctype": "Custom DocPerm",
        "parent": "University Student",
        "role": "University Finance",
        "permlevel": 1,
        "read": 1,
        "write": 0
    },
    {
        "doctype": "Custom DocPerm",
        "parent": "University Student",
        "role": "University Admin",
        "permlevel": 1,
        "read": 1,
        "write": 1
    },
    {
        "doctype": "Custom DocPerm",
        "parent": "Examination Result",
        "role": "University Exam Cell",
        "permlevel": 2,
        "read": 1,
        "write": 1
    }
]
```

---

## Audit Logging

### Audit Log Configuration
```python
# university_erp/audit.py

import frappe
from frappe.utils import now_datetime

AUDITED_DOCTYPES = [
    "University Student",
    "Examination Result",
    "Fee Payment",
    "University Faculty",
    "Admission Application",
    "Student Certificate",
    "Grade Card",
    "Student Transcript",
]

AUDITED_ACTIONS = ["Create", "Update", "Delete", "Submit", "Cancel", "Print", "Export"]

def log_audit_event(doctype, docname, action, old_values=None, new_values=None):
    """Log audit event for critical actions"""
    if doctype not in AUDITED_DOCTYPES:
        return

    audit_log = frappe.new_doc("University Audit Log")
    audit_log.doctype_name = doctype
    audit_log.document_name = docname
    audit_log.action = action
    audit_log.user = frappe.session.user
    audit_log.timestamp = now_datetime()
    audit_log.ip_address = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else ""
    audit_log.user_agent = frappe.request.headers.get('User-Agent', '') if frappe.request else ""

    if old_values:
        audit_log.old_values = frappe.as_json(old_values)
    if new_values:
        audit_log.new_values = frappe.as_json(new_values)

    # Calculate changes
    if old_values and new_values:
        changes = []
        for key in new_values:
            if old_values.get(key) != new_values.get(key):
                changes.append({
                    "field": key,
                    "old": old_values.get(key),
                    "new": new_values.get(key)
                })
        audit_log.changes = frappe.as_json(changes)

    audit_log.flags.ignore_permissions = True
    audit_log.insert()

# Document event hooks
def on_update_log(doc, method):
    """Log update events"""
    if doc.doctype in AUDITED_DOCTYPES:
        old_doc = doc.get_doc_before_save()
        if old_doc:
            log_audit_event(
                doc.doctype,
                doc.name,
                "Update",
                old_doc.as_dict(),
                doc.as_dict()
            )

def on_trash_log(doc, method):
    """Log delete events"""
    if doc.doctype in AUDITED_DOCTYPES:
        log_audit_event(doc.doctype, doc.name, "Delete", doc.as_dict())

def on_submit_log(doc, method):
    """Log submit events"""
    if doc.doctype in AUDITED_DOCTYPES:
        log_audit_event(doc.doctype, doc.name, "Submit", None, doc.as_dict())
```

### Audit Log DocType
```json
{
    "doctype": "DocType",
    "name": "University Audit Log",
    "module": "University ERP",
    "is_virtual": 0,
    "fields": [
        {"fieldname": "doctype_name", "fieldtype": "Data", "label": "Document Type"},
        {"fieldname": "document_name", "fieldtype": "Dynamic Link", "options": "doctype_name"},
        {"fieldname": "action", "fieldtype": "Select", "options": "Create\nUpdate\nDelete\nSubmit\nCancel\nPrint\nExport"},
        {"fieldname": "user", "fieldtype": "Link", "options": "User"},
        {"fieldname": "timestamp", "fieldtype": "Datetime"},
        {"fieldname": "ip_address", "fieldtype": "Data"},
        {"fieldname": "user_agent", "fieldtype": "Small Text"},
        {"fieldname": "old_values", "fieldtype": "Code"},
        {"fieldname": "new_values", "fieldtype": "Code"},
        {"fieldname": "changes", "fieldtype": "Code"}
    ],
    "permissions": [
        {"role": "University Admin", "read": 1, "write": 0, "create": 0, "delete": 0}
    ],
    "track_changes": 0
}
```

---

## Data Privacy & Compliance

### Student Data Privacy
```python
# university_erp/privacy.py

import frappe

class StudentDataPrivacy:
    """Handle student data privacy requirements"""

    SENSITIVE_FIELDS = [
        "date_of_birth",
        "aadhaar_number",
        "pan_number",
        "bank_account_no",
        "medical_records",
        "guardian_income",
        "caste_category",
        "religion",
        "disability_status",
    ]

    def get_student_data_export(self, student):
        """Export all data for a student (GDPR-style right to access)"""
        data = {
            "personal_info": frappe.get_doc("University Student", student).as_dict(),
            "enrollments": frappe.get_all("Program Enrollment", {"student": student}),
            "course_enrollments": frappe.get_all("Course Enrollment", {"student": student}),
            "results": frappe.get_all("Examination Result", {"student": student}),
            "attendance": frappe.get_all("Student Attendance", {"student": student}),
            "fees": frappe.get_all("Fee Payment", {"student": student}),
            "certificates": frappe.get_all("Student Certificate", {"student": student}),
        }

        return data

    def anonymize_student_data(self, student):
        """Anonymize student data (right to be forgotten)"""
        # This should only be used after graduation + retention period

        doc = frappe.get_doc("University Student", student)

        # Anonymize personal data
        doc.student_name = f"Anonymized-{student}"
        doc.email = f"anonymized-{student}@deleted.local"
        doc.mobile = "0000000000"
        doc.address = "REDACTED"
        doc.date_of_birth = None
        doc.aadhaar_number = None
        doc.pan_number = None
        doc.bank_account_no = None
        doc.image = None

        # Clear guardian info
        doc.guardians = []

        doc.flags.ignore_permissions = True
        doc.save()

        # Log the anonymization
        frappe.get_doc({
            "doctype": "University Audit Log",
            "doctype_name": "University Student",
            "document_name": student,
            "action": "Anonymize",
            "user": frappe.session.user,
            "timestamp": frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)

    def mask_sensitive_data(self, data, user_roles):
        """Mask sensitive fields based on user role"""
        for field in self.SENSITIVE_FIELDS:
            if field in data:
                # Check if user has permission to view
                if not self.can_view_field(field, user_roles):
                    data[field] = "***MASKED***"

        return data

    def can_view_field(self, field, roles):
        """Check if roles can view the field"""
        field_permissions = {
            "aadhaar_number": ["University Admin", "University Registrar"],
            "pan_number": ["University Admin", "University Finance"],
            "bank_account_no": ["University Admin", "University Finance"],
            "medical_records": ["University Admin", "University Registrar"],
            "guardian_income": ["University Admin", "University Finance"],
        }

        allowed_roles = field_permissions.get(field, ["University Admin"])
        return any(role in roles for role in allowed_roles)
```

### Exam Data Confidentiality
```python
# university_erp/exam_security.py

import frappe
from frappe.utils import now_datetime

class ExamSecurity:
    """Handle exam data confidentiality"""

    def validate_result_access(self, result_doc):
        """Validate access to result before declaration"""
        if result_doc.docstatus == 0:  # Draft
            # Only exam cell and assigned faculty can access
            user_roles = frappe.get_roles()
            if "University Exam Cell" not in user_roles:
                # Check if user is the examiner
                faculty = frappe.db.get_value("University Faculty", {"user": frappe.session.user})
                if result_doc.examiner != faculty:
                    frappe.throw("You don't have permission to view undeclared results")

    def lock_result_entry(self, examination):
        """Lock result entry after deadline"""
        exam_doc = frappe.get_doc("Examination", examination)

        if frappe.utils.getdate() > frappe.utils.getdate(exam_doc.result_entry_deadline):
            frappe.throw("Result entry deadline has passed")

    def validate_grade_modification(self, result_doc):
        """Validate grade modification rules"""
        if result_doc.docstatus == 1:  # Submitted
            # Only Exam Controller can modify submitted results
            if "University Exam Controller" not in frappe.get_roles():
                frappe.throw("Only Exam Controller can modify submitted results")

            # Log the modification attempt
            frappe.get_doc({
                "doctype": "University Audit Log",
                "doctype_name": "Examination Result",
                "document_name": result_doc.name,
                "action": "Grade Modification Attempt",
                "user": frappe.session.user,
                "timestamp": now_datetime()
            }).insert(ignore_permissions=True)
```

---

## Session Security

### Login Restrictions
```python
# university_erp/session_security.py

import frappe

def validate_login(login_manager):
    """Custom login validation for university users"""
    user = login_manager.user

    # Check if user is a student
    student = frappe.db.get_value("University Student", {"user": user}, ["name", "status"])

    if student:
        if student[1] not in ["Active", "Alumni"]:
            frappe.throw("Your student account is not active. Please contact the registrar.")

    # Check if user is faculty
    faculty = frappe.db.get_value("University Faculty", {"user": user}, ["name", "status"])

    if faculty:
        if faculty[1] not in ["Active", "On Leave", "Sabbatical"]:
            frappe.throw("Your faculty account is not active. Please contact HR.")

def on_session_creation(login_manager):
    """Actions on successful login"""
    user = login_manager.user

    # Log login event
    frappe.get_doc({
        "doctype": "University Audit Log",
        "doctype_name": "User",
        "document_name": user,
        "action": "Login",
        "user": user,
        "timestamp": frappe.utils.now_datetime(),
        "ip_address": frappe.local.request_ip
    }).insert(ignore_permissions=True)

    # Set role-based landing page
    set_landing_page(user)

def set_landing_page(user):
    """Set landing page based on role"""
    roles = frappe.get_roles(user)

    if "University Student" in roles:
        frappe.local.response["home_page"] = "/student-portal"
    elif "University Faculty" in roles:
        frappe.local.response["home_page"] = "/app/faculty-dashboard"
    elif "University Admin" in roles:
        frappe.local.response["home_page"] = "/app/university-home"
```

### hooks.py Security Configuration
```python
# In hooks.py

on_login = "university_erp.session_security.validate_login"
on_session_creation = "university_erp.session_security.on_session_creation"

# Rate limiting for sensitive operations
rate_limit = {
    "Fee Payment": {"limit": 5, "seconds": 60},
    "Examination Result": {"limit": 100, "seconds": 60},
}
```

---

## API Security

### REST API Authentication
```python
# university_erp/api/security.py

import frappe
from frappe import _

def validate_api_access(doctype, method):
    """Validate API access for university doctypes"""

    # Ensure user is authenticated
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required"), frappe.AuthenticationError)

    # Check if doctype is a university doctype
    if doctype.startswith("University"):
        # Apply additional validation
        validate_university_api_permission(doctype, method)

def validate_university_api_permission(doctype, method):
    """Additional API permission checks"""
    user_roles = frappe.get_roles()

    # Define API access matrix
    api_permissions = {
        "University Student": {
            "read": ["University Admin", "University Registrar", "University Faculty", "University Student"],
            "write": ["University Admin", "University Registrar"],
            "create": ["University Admin", "University Registrar"],
        },
        "Examination Result": {
            "read": ["University Admin", "University Exam Cell", "University Faculty", "University Student"],
            "write": ["University Admin", "University Exam Cell", "University Faculty"],
            "create": ["University Admin", "University Exam Cell"],
        }
    }

    allowed_roles = api_permissions.get(doctype, {}).get(method, ["University Admin"])

    if not any(role in user_roles for role in allowed_roles):
        frappe.throw(_("Insufficient permissions for this API"), frappe.PermissionError)
```

---

## Next Document

Continue to [07_integrations_deployment.md](07_integrations_deployment.md) for integration patterns and deployment strategy.
