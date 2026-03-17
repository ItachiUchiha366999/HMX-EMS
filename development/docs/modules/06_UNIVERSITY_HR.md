# University HR Module

## Overview

The University HR module manages faculty profiles, teaching assignments, workload calculation, performance evaluation, and integrates with HRMS for payroll and leave management. It provides university-specific HR functionality while leveraging HRMS's employee management capabilities.

## Module Location
```
university_erp/university_hr/
```

## DocTypes (14 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Faculty Profile | Main | Comprehensive faculty record |
| Faculty Publication | Child | Research publications |
| Faculty Research Project | Child | Research projects |
| Faculty Award | Child | Awards and recognitions |
| Employee Qualification | Child | Academic qualifications |
| Teaching Assignment | Main | Course-faculty mapping |
| Teaching Assignment Schedule | Child | Class schedule |
| Temporary Teaching Assignment | Main | Substitute teaching |
| Leave Affected Course | Child | Courses affected by leave |
| Faculty Attendance | Main | Faculty attendance records |
| Faculty Performance Evaluation | Main | Annual appraisal |
| Student Feedback | Main | Teaching feedback |
| Workload Distributor | Main | Workload management tool |
| UGC Pay Scale | Main | Salary scale definitions |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                      UNIVERSITY HR MODULE                         |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  |  FACULTY PROFILE  |       |  TEACHING         |                |
|  +-------------------+       |  ASSIGNMENT       |                |
|  | - Personal Info   |       +-------------------+                |
|  | - Qualifications  |       | - Course          |                |
|  | - Publications    |       | - Student Group   |                |
|  | - Projects        |       | - Weekly Hours    |                |
|  | - Awards          |       +-------------------+                |
|  +-------------------+              |                             |
|           |                         |                             |
|           v                         v                             |
|  +-------------------+       +-------------------+                |
|  |     EMPLOYEE      |       |    WORKLOAD       |                |
|  |    (HRMS App)     |       |   DISTRIBUTOR     |                |
|  +-------------------+       +-------------------+                |
|           |                                                       |
|           +------------------+------------------+                 |
|           |                  |                  |                 |
|           v                  v                  v                 |
|  +----------------+  +----------------+  +------------------+     |
|  |    PAYROLL     |  |     LEAVE      |  |   PERFORMANCE    |     |
|  |   (HRMS)       |  |    (HRMS)      |  |   EVALUATION     |     |
|  +----------------+  +----------------+  +------------------+     |
|                              |                   |                |
|                              v                   v                |
|                      +----------------+  +----------------+       |
|                      | Leave Affected |  |   Student      |       |
|                      |    Course      |  |   Feedback     |       |
|                      +----------------+  +----------------+       |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### HRMS Integration
```
+--------------------+       +--------------------+
|   UNIVERSITY HR    |       |       HRMS         |
|     (Custom)       |------>|        (App)       |
+--------------------+       +--------------------+
|                    |       |                    |
| Faculty Profile ---|------>| Employee           |
|   (links to)       |       | (creates/syncs)    |
|                    |       |                    |
| Leave Events ------|------>| Leave Application  |
|   (hooks)          |       | (HRMS DocType)     |
|                    |       |                    |
| UGC Pay Scale -----|------>| Salary Structure   |
|   (feeds)          |       |                    |
+--------------------+       +--------------------+
```

### Cross-Module Relationships
```
                    +--------------------+
                    |   UNIVERSITY HR    |
                    +--------------------+
                            /|\
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+----------------+  +----------------+  +----------------+
|   ACADEMICS    |  |    RESEARCH    |  |   EXAMINATIONS |
+----------------+  +----------------+  +----------------+
| Teaching       |  | Faculty ->     |  | Invigilator -> |
| Assignment ->  |  | Publications,  |  | Faculty        |
| Instructor     |  | Projects       |  |                |
+----------------+  +----------------+  +----------------+
```

## DocType Details

### 1. Faculty Profile
**Purpose**: Comprehensive faculty information

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| faculty_id | Data | Unique identifier |
| employee | Link (Employee) | HRMS Employee link |
| salutation | Select | Dr./Prof./Mr./Ms. |
| first_name | Data | First name |
| last_name | Data | Last name |
| department | Link (Department) | Academic department |
| designation | Select | Professor/Assoc./Asst./Lecturer |
| employment_type | Select | Permanent/Contract/Visiting |
| date_of_joining | Date | Join date |
| date_of_birth | Date | DOB |
| qualifications | Table | Academic degrees |
| specialization | Small Text | Research areas |
| publications | Table | Research papers |
| research_projects | Table | Ongoing/completed projects |
| awards | Table | Recognitions |
| max_weekly_hours | Int | Maximum teaching load |
| current_workload | Float | Calculated workload |
| email | Data | Official email |
| personal_email | Data | Personal email |
| phone | Data | Contact number |
| photo | Attach Image | Profile photo |
| status | Select | Active/On Leave/Resigned/Retired |

**Auto-Create Employee**:
```python
def on_insert(self):
    """Create HRMS Employee when Faculty Profile is created"""
    if not self.employee:
        employee = frappe.new_doc("Employee")
        employee.employee_name = f"{self.first_name} {self.last_name}"
        employee.department = self.department
        employee.designation = self.designation
        employee.date_of_joining = self.date_of_joining
        employee.company = frappe.get_single("University Settings").company
        employee.insert()
        self.employee = employee.name
```

### 2. Employee Qualification (Child Table)
**Purpose**: Academic degrees and certifications

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| qualification | Data | Degree name |
| level | Select | PhD/Masters/Bachelors |
| university | Data | Granting institution |
| year | Data | Year of completion |
| specialization | Data | Field of study |

### 3. Faculty Publication (Child Table)
**Purpose**: Research publication records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| title | Data | Paper title |
| publication_type | Select | Journal/Conference/Book |
| journal_name | Data | Journal/Conference name |
| year | Data | Publication year |
| doi | Data | DOI identifier |
| impact_factor | Float | Journal impact factor |
| co_authors | Small Text | Other authors |

### 4. Teaching Assignment
**Purpose**: Faculty-course-section mapping for semester

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| faculty | Link (Faculty Profile) | Faculty member |
| instructor | Link (Instructor) | Education Instructor |
| course | Link (Course) | Course taught |
| academic_term | Link | Semester |
| student_group | Link | Section |
| teaching_type | Select | Lecture/Tutorial/Practical |
| weekly_hours | Float | Hours per week |
| schedule | Table | Class timings |
| is_active | Check | Active status |

**Workload Calculation**:
```python
def update_faculty_workload(faculty):
    """Calculate total teaching workload"""
    assignments = frappe.get_all("Teaching Assignment", {
        "faculty": faculty,
        "is_active": 1
    }, ["weekly_hours"])

    total_hours = sum(a.weekly_hours for a in assignments)
    frappe.db.set_value("Faculty Profile", faculty, "current_workload", total_hours)
```

### 5. Temporary Teaching Assignment
**Purpose**: Substitute faculty for leaves/absences

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| original_faculty | Link (Faculty Profile) | Regular faculty |
| substitute_faculty | Link (Faculty Profile) | Replacement |
| course | Link (Course) | Course covered |
| from_date | Date | Start date |
| to_date | Date | End date |
| reason | Select | Leave/Medical/Duty |
| leave_application | Link | Related leave |
| status | Select | Pending/Approved/Completed |

### 6. Faculty Performance Evaluation
**Purpose**: Annual appraisal records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| faculty | Link (Faculty Profile) | Faculty evaluated |
| academic_year | Link | Evaluation year |
| evaluation_period | Select | H1/H2/Annual |
| teaching_score | Float | Teaching performance |
| research_score | Float | Research output |
| administrative_score | Float | Admin duties |
| overall_score | Float | Weighted average |
| student_feedback_avg | Float | From feedback forms |
| publications_count | Int | Papers published |
| evaluator | Link (User) | HOD/Dean |
| evaluation_date | Date | Date of evaluation |
| status | Select | Draft/Submitted/Approved |
| remarks | Text | Comments |

**Workflow**:
```
Self-Assessment --> HOD Review --> Dean Approval --> Completed
```

### 7. Student Feedback
**Purpose**: Course-end teaching evaluation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| faculty | Link (Faculty Profile) | Faculty rated |
| course | Link (Course) | Course evaluated |
| academic_term | Link | Semester |
| student | Link (Student) | Feedback giver |
| teaching_quality | Int | Rating 1-5 |
| course_content | Int | Rating 1-5 |
| punctuality | Int | Rating 1-5 |
| communication | Int | Rating 1-5 |
| overall_rating | Float | Average score |
| comments | Text | Open feedback |
| is_anonymous | Check | Hide student identity |

**Portal Access**:
- Students submit via portal
- Anonymous option for candid feedback
- Aggregated for performance evaluation

### 8. UGC Pay Scale
**Purpose**: Government salary structure

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| designation | Select | Professor/Assoc./Asst. |
| pay_band | Data | Pay band (7th CPC) |
| grade_pay | Currency | Grade pay |
| entry_level | Currency | Starting salary |
| maximum | Currency | Maximum in band |
| academic_grade_pay | Currency | AGP component |

## Data Flow Diagrams

### Faculty Onboarding Flow
```
+----------------+     +------------------+     +------------------+
|   HR Admin     |---->|  Faculty Profile |---->|    Employee      |
|   Creates      |     |    Created       |     |  Auto-Created    |
+----------------+     +------------------+     +------------------+
                                |                       |
                                v                       v
                       +----------------+      +----------------+
                       |   Teaching     |      |   Salary       |
                       |   Assignment   |      |   Structure    |
                       +----------------+      +----------------+
```

### Leave Impact Flow
```
+----------------+     +------------------+     +------------------+
|    Faculty     |---->| Leave            |---->|  Leave Affected  |
|  Applies Leave |     | Application      |     |     Courses      |
+----------------+     +------------------+     +------------------+
                                                        |
                                                        v
+----------------+     +------------------+     +------------------+
|   Temporary    |<----|   HOD Assigns    |<----|   Identify       |
|   Assignment   |     |   Substitute     |     |   Substitute     |
+----------------+     +------------------+     +------------------+
```

### Performance Evaluation Flow
```
+------------------+     +------------------+     +------------------+
|   Teaching       |     |   Research       |     |   Student        |
|   Assignments    |     |   Publications   |     |   Feedback       |
+------------------+     +------------------+     +------------------+
        |                       |                       |
        +-----------------------------------------------+
                               |
                               v
                    +------------------+
                    |   Performance    |
                    |   Evaluation     |
                    +------------------+
                               |
                               v
                    +------------------+
                    |   Appraisal      |
                    |   (HRMS)         |
                    +------------------+
```

## Integration Points

### HRMS Employee Sync
```python
# university_erp/university_hr/employee_events.py

def on_employee_update(doc, method):
    """Sync changes to Faculty Profile"""
    if hasattr(doc, 'university_faculty') and doc.university_faculty:
        faculty = frappe.get_doc("Faculty Profile", doc.university_faculty)
        faculty.designation = doc.designation
        faculty.department = doc.department
        faculty.status = "Active" if doc.status == "Active" else "Resigned"
        faculty.save()
```

### Leave Application Hook
```python
# university_erp/university_hr/leave_events.py

def on_submit(doc, method):
    """Handle leave approval - identify affected courses"""
    employee = frappe.get_doc("Employee", doc.employee)
    if not hasattr(employee, 'university_faculty'):
        return

    # Get teaching assignments during leave period
    assignments = get_assignments_in_period(
        employee.university_faculty,
        doc.from_date,
        doc.to_date
    )

    # Create affected course records
    for assignment in assignments:
        frappe.get_doc({
            "doctype": "Leave Affected Course",
            "leave_application": doc.name,
            "course": assignment.course,
            "student_group": assignment.student_group,
        }).insert()

def on_cancel(doc, method):
    """Handle leave cancellation"""
    # Remove affected course records
    frappe.db.delete("Leave Affected Course", {"leave_application": doc.name})
```

### Workload Distributor
```python
# Tool for HODs to balance teaching load

class WorkloadDistributor:
    def get_department_workload(self, department, academic_term):
        """Get workload distribution for department"""
        faculty = frappe.get_all("Faculty Profile", {
            "department": department,
            "status": "Active"
        }, ["name", "max_weekly_hours", "current_workload"])

        courses = frappe.get_all("Course", {
            "department": department
        }, ["name", "credits", "total_hours"])

        return {
            "faculty": faculty,
            "courses": courses,
            "unassigned_hours": self.calculate_unassigned(courses)
        }

    def suggest_assignment(self, course, department):
        """Suggest faculty for course based on workload"""
        faculty = frappe.get_all("Faculty Profile", {
            "department": department,
            "status": "Active"
        }, ["name", "max_weekly_hours", "current_workload", "specialization"])

        # Sort by available capacity
        faculty.sort(key=lambda f: f.max_weekly_hours - f.current_workload, reverse=True)

        return faculty[:3]  # Top 3 suggestions
```

## API Endpoints

### Faculty Management
```python
@frappe.whitelist()
def get_faculty_profile(faculty_id):
    """Get complete faculty profile"""
    return frappe.get_doc("Faculty Profile", faculty_id)

@frappe.whitelist()
def get_faculty_workload(faculty, academic_term):
    """Get faculty's teaching load"""
    assignments = frappe.get_all("Teaching Assignment", {
        "faculty": faculty,
        "academic_term": academic_term,
        "is_active": 1
    }, ["course", "student_group", "weekly_hours", "teaching_type"])

    total = sum(a.weekly_hours for a in assignments)
    max_hours = frappe.db.get_value("Faculty Profile", faculty, "max_weekly_hours")

    return {
        "assignments": assignments,
        "total_hours": total,
        "max_hours": max_hours,
        "available": max_hours - total
    }
```

### Performance
```python
@frappe.whitelist()
def get_faculty_performance(faculty, academic_year):
    """Get performance metrics"""
    # Teaching assignments
    teaching = get_teaching_stats(faculty, academic_year)

    # Publications
    publications = get_publication_count(faculty, academic_year)

    # Student feedback
    feedback = get_average_feedback(faculty, academic_year)

    return {
        "teaching": teaching,
        "publications": publications,
        "feedback_score": feedback
    }
```

## Reports

1. **Faculty Directory** - Department-wise listing
2. **Workload Report** - Hours per faculty
3. **Performance Dashboard** - Evaluation scores
4. **Publication Report** - Research output
5. **Leave Report** - Leave patterns
6. **Feedback Analysis** - Student ratings

## Related Files

```
university_erp/
+-- university_hr/
    +-- doctype/
    |   +-- faculty_profile/
    |   +-- employee_qualification/
    |   +-- faculty_publication/
    |   +-- faculty_research_project/
    |   +-- faculty_award/
    |   +-- teaching_assignment/
    |   +-- teaching_assignment_schedule/
    |   +-- temporary_teaching_assignment/
    |   +-- leave_affected_course/
    |   +-- faculty_attendance/
    |   +-- faculty_performance_evaluation/
    |   +-- student_feedback/
    |   +-- workload_distributor/
    |   +-- ugc_pay_scale/
    +-- employee_events.py
    +-- leave_events.py
    +-- department_events.py
    +-- api.py
    +-- fixtures/
        +-- academic_leave_types.py
        +-- salary_components.py
```

## See Also

- [Academics Module](01_ACADEMICS.md)
- [University Research Module](12_UNIVERSITY_RESEARCH.md)
- [HRMS Deep Dive](../05_hrms_deep_dive.md)
