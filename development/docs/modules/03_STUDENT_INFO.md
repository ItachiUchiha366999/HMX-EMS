# Student Info Module

## Overview

The Student Info module manages student lifecycle status, alumni records, and university announcements. It provides supplementary functionality to the Education app's Student DocType for tracking student status changes and post-graduation engagement.

## Module Location
```
university_erp/student_info/
```

## DocTypes (3 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Student Status Log | Main | Track student status changes |
| University Alumni | Main | Alumni records and engagement |
| University Announcement | Main | News and notifications |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                     STUDENT INFO MODULE                           |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+                                            |
|  |     STUDENT       |                                            |
|  | (Education App)   |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           +------------------+------------------+                  |
|           |                  |                  |                  |
|           v                  v                  v                  |
|  +----------------+  +----------------+  +------------------+     |
|  | Student Status |  | University     |  | University       |     |
|  |     Log        |  |    Alumni      |  |  Announcement    |     |
|  +----------------+  +----------------+  +------------------+     |
|  | - Status       |  | - Graduation   |  | - Title          |     |
|  | - Reason       |  | - Employment   |  | - Content        |     |
|  | - Date         |  | - Contact      |  | - Target Roles   |     |
|  +----------------+  +----------------+  +------------------+     |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Student Entity Relationships
```
+--------------------+       +--------------------+
|   EDUCATION APP    |       |   STUDENT INFO     |
+--------------------+       +--------------------+
|                    |       |                    |
|     Student -------|------>| Student Status Log |
|                    |       | (history tracking) |
|                    |       |                    |
|     Student -------|------>| University Alumni  |
|   (graduated)      |       | (post-graduation)  |
|                    |       |                    |
+--------------------+       +--------------------+
```

### Cross-Module Connections
```
                        +--------------------+
                        |   STUDENT INFO     |
                        +--------------------+
                               /|\
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
    +-------------+    +---------------+   +-------------+
    |  ADMISSIONS |    |   PLACEMENT   |   |   PORTALS   |
    +-------------+    +---------------+   +-------------+
    | Status->     |   | Alumni ->      |   | Announce-   |
    | Enrolled     |   | Job Posting    |   | ments ->    |
    +-------------+    +---------------+   | Portal      |
                                          +-------------+
```

## DocType Details

### 1. Student Status Log
**Purpose**: Audit trail of student status changes

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student reference |
| student_name | Data | Name (fetched) |
| from_status | Select | Previous status |
| to_status | Select | New status |
| change_date | Date | Date of change |
| reason | Small Text | Reason for change |
| changed_by | Link (User) | User who made change |
| document_reference | Data | Related document |

**Status Options**:
- Active
- Inactive
- On Leave
- Suspended
- Graduated
- Withdrawn
- Transferred
- Deceased

**Auto-Creation**:
```python
# Triggered on Student status change
def on_student_update(doc, method):
    if doc.has_value_changed("status"):
        create_status_log(
            student=doc.name,
            from_status=doc.get_doc_before_save().status,
            to_status=doc.status
        )
```

### 2. University Alumni
**Purpose**: Track graduated students for engagement

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Original student record |
| alumni_id | Data | Alumni identification |
| full_name | Data | Name |
| graduation_year | Data | Year of graduation |
| program | Link (Program) | Degree completed |
| department | Link (Department) | Academic department |
| personal_email | Data | Personal contact |
| phone | Data | Phone number |
| current_employer | Data | Employment |
| designation | Data | Job title |
| linkedin_profile | Data | LinkedIn URL |
| is_active_member | Check | Active in alumni association |
| membership_type | Select | Regular/Premium/Lifetime |

**Auto-Creation from Student**:
```python
def create_alumni_from_student(student):
    """Create alumni record when student graduates"""
    if student.status == "Graduated":
        alumni = frappe.new_doc("University Alumni")
        alumni.student = student.name
        alumni.full_name = student.student_name
        alumni.graduation_year = frappe.utils.nowdate()[:4]
        alumni.program = student.custom_program
        alumni.save()
```

### 3. University Announcement
**Purpose**: Publish news and notifications

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| title | Data | Announcement title |
| content | Text Editor | Full content |
| announcement_type | Select | General/Academic/Event/Alert |
| publish_date | Date | Publication date |
| expiry_date | Date | When to hide |
| target_roles | Table MultiSelect | Who can see |
| is_pinned | Check | Pin to top |
| attachment | Attach | Related files |
| status | Select | Draft/Published/Archived |

**Target Audience**:
- All Users
- University Student
- University Faculty
- University Admin
- University Alumni

## Data Flow Diagrams

### Student Lifecycle with Status Logging
```
+----------------+     +------------------+     +------------------+
|   ADMISSION    |---->|    ENROLLED      |---->|   ACTIVE         |
|   Approved     |     |   (New Student)  |     |   (Studying)     |
+----------------+     +------------------+     +------------------+
                              |                        |
                              v                        v
                       +-----------+            +-----------+
                       |Status Log |            |Status Log |
                       |Created    |            |Updates    |
                       +-----------+            +-----------+
                                                      |
        +---------------------------------------------+
        |                    |                        |
        v                    v                        v
+----------------+   +----------------+   +------------------+
|   GRADUATED    |   |   SUSPENDED    |   |   WITHDRAWN      |
|   (Complete)   |   |   (Temporary)  |   |   (Left)         |
+----------------+   +----------------+   +------------------+
        |
        v
+----------------+
|    ALUMNI      |
|   (Created)    |
+----------------+
```

### Announcement Distribution
```
+------------------+     +------------------+
| Admin Creates    |---->|   Announcement   |
| Announcement     |     |   (Published)    |
+------------------+     +------------------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
+---------------+      +---------------+      +---------------+
| Student       |      |   Faculty     |      |   Alumni      |
|   Portal      |      |   Portal      |      |   Portal      |
+---------------+      +---------------+      +---------------+
```

## Integration Points

### With Student Override
```python
# university_erp/overrides/student.py

class UniversityStudent(Student):
    def on_update(self):
        super().on_update()
        if self.has_value_changed("status"):
            self.create_status_log()

        if self.status == "Graduated":
            self.create_alumni_record()

    def create_status_log(self):
        from university_erp.student_info.api import log_status_change
        log_status_change(self)

    def create_alumni_record(self):
        from university_erp.student_info.api import create_alumni
        create_alumni(self)
```

### With Placement Module
```python
# Alumni can post jobs and mentor students
class UniversityAlumni:
    def get_posted_jobs(self):
        return frappe.get_all("Placement Job Opening",
            filters={"posted_by_alumni": self.name})

    def can_mentor_students(self):
        return self.is_active_member and self.years_of_experience >= 5
```

### With Portals Module
```python
# Announcements shown on portal dashboards
def get_announcements_for_user(user):
    user_roles = frappe.get_roles(user)
    return frappe.get_all("University Announcement",
        filters={
            "status": "Published",
            "publish_date": ("<=", today()),
            "expiry_date": (">=", today()),
        },
        or_filters={
            "target_roles": ("in", user_roles),
            "target_all": 1
        }
    )
```

## API Endpoints

### Student Status
```python
@frappe.whitelist()
def get_student_status_history(student):
    """Get complete status history for a student"""
    return frappe.get_all("Student Status Log",
        filters={"student": student},
        fields=["*"],
        order_by="change_date desc"
    )

@frappe.whitelist()
def change_student_status(student, new_status, reason):
    """Change student status with logging"""
    doc = frappe.get_doc("Student", student)
    doc.status = new_status
    doc.status_change_reason = reason
    doc.save()
```

### Alumni Management
```python
@frappe.whitelist()
def register_alumni(student_id):
    """Register graduated student as alumni"""
    student = frappe.get_doc("Student", student_id)
    if student.status != "Graduated":
        frappe.throw("Only graduated students can be registered as alumni")

    return create_alumni_from_student(student)

@frappe.whitelist()
def update_alumni_employment(alumni_id, employer, designation):
    """Update alumni employment details"""
    alumni = frappe.get_doc("University Alumni", alumni_id)
    alumni.current_employer = employer
    alumni.designation = designation
    alumni.save()
```

## Reports

1. **Student Status Report** - Current status distribution
2. **Status Change History** - Status transitions over time
3. **Alumni Directory** - Searchable alumni list
4. **Alumni Employment Report** - Where alumni work
5. **Announcement Reach Report** - Views/engagement

## Related Files

```
university_erp/
+-- student_info/
    +-- doctype/
    |   +-- student_status_log/
    |   |   +-- student_status_log.json
    |   |   +-- student_status_log.py
    |   +-- university_alumni/
    |   |   +-- university_alumni.json
    |   |   +-- university_alumni.py
    |   +-- university_announcement/
    |       +-- university_announcement.json
    |       +-- university_announcement.py
    +-- api.py
+-- overrides/
    +-- student.py  # Status logging hooks
```

## See Also

- [Admissions Module](02_ADMISSIONS.md)
- [University Portals Module](15_UNIVERSITY_PORTALS.md)
- [University Placement Module](10_UNIVERSITY_PLACEMENT.md)
