# University Placement Module

## Overview

The University Placement module manages campus recruitment activities including company registrations, job postings, placement drives, student applications, and interview rounds. It facilitates the complete placement cycle from company onboarding to job offers.

## Module Location
```
university_erp/university_placement/
```

## DocTypes (11 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Industry Type | Main | Industry classification |
| Placement Company | Main | Recruiting companies |
| Job Eligible Program | Child | Eligible programs for job |
| Placement Job Opening | Main | Job postings |
| Placement Drive | Main | Recruitment events |
| Placement Round | Child | Interview rounds |
| Placement Application | Main | Student applications |
| Student Resume | Main | Student CVs |
| Resume Education | Child | Education details |
| Resume Project | Child | Project details |
| Resume Skill | Child | Skills list |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                   UNIVERSITY PLACEMENT MODULE                     |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  |  INDUSTRY TYPE    |       | PLACEMENT COMPANY |                |
|  +-------------------+       +-------------------+                |
|  | - IT/Software     |<------| - Company name    |                |
|  | - Banking/Finance |       | - Industry        |                |
|  | - Manufacturing   |       | - HR Contact      |                |
|  +-------------------+       +-------------------+                |
|                                      |                            |
|                                      v                            |
|                        +-------------------+                      |
|                        |PLACEMENT JOB      |                      |
|                        |    OPENING        |                      |
|                        +-------------------+                      |
|                        | - Job title       |                      |
|                        | - Package         |                      |
|                        | - Eligible programs|                     |
|                        +-------------------+                      |
|                                      |                            |
|           +--------------------------+-------------------------+  |
|           |                          |                         |  |
|           v                          v                         v  |
|  +----------------+       +-------------------+       +---------+ |
|  |PLACEMENT DRIVE |       | PLACEMENT         |       | STUDENT | |
|  +----------------+       |  APPLICATION      |       | RESUME  | |
|  | - Date         |       +-------------------+       +---------+ |
|  | - Venue        |       | - Student         |       | - Skills| |
|  | - Rounds       |       | - Status          |       | - Proj. | |
|  +----------------+       +-------------------+       +---------+ |
|           |                          |                            |
|           v                          v                            |
|  +----------------+       +-------------------+                   |
|  |PLACEMENT ROUND |       |    JOB OFFER      |                   |
|  +----------------+       |   (Final Status)  |                   |
|  | - Aptitude     |       +-------------------+                   |
|  | - Technical    |                                               |
|  | - HR Interview |                                               |
|  +----------------+                                               |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Education App Integration
```
+--------------------+       +--------------------+
|    PLACEMENT       |       |    EDUCATION       |
|     (Custom)       |------>|       (App)        |
+--------------------+       +--------------------+
|                    |       |                    |
| Application -------|------>| Student            |
| Job Opening -------|------>| Program            |
|                    |       | Student Group      |
+--------------------+       +--------------------+
```

### Cross-Module Relationships
```
                    +--------------------+
                    |    PLACEMENT       |
                    +--------------------+
                            /|\
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+----------------+  +----------------+  +----------------+
|   ACADEMICS    |  | STUDENT INFO   |  |   PORTALS      |
+----------------+  +----------------+  +----------------+
| Program ->     |  | Alumni ->      |  | Student Portal |
| Eligibility    |  | Job Posting    |  | -> Applications|
| CGPA check     |  | Mentoring      |  |                |
+----------------+  +----------------+  +----------------+
```

## DocType Details

### 1. Industry Type
**Purpose**: Classify recruiting industries

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| industry_name | Data | e.g., "Information Technology" |
| industry_code | Data | Short code |
| description | Text | Industry description |

**Standard Industries**:
- Information Technology / Software
- Banking / Finance / Insurance
- Manufacturing / Engineering
- Consulting / Advisory
- Retail / E-commerce
- Healthcare / Pharma
- FMCG / Consumer Goods
- Core Engineering / PSUs

### 2. Placement Company
**Purpose**: Company master for recruiters

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| company_name | Data | Official name |
| company_code | Data | Short identifier |
| industry_type | Link (Industry Type) | Industry |
| company_type | Select | MNC/Startup/SME/PSU |
| website | Data | Company website |
| headquarters | Data | HQ location |
| hr_name | Data | HR contact name |
| hr_email | Data | HR email |
| hr_phone | Data | HR phone |
| company_description | Text Editor | About company |
| logo | Attach Image | Company logo |
| partnership_status | Select | Active/Inactive |
| last_visited | Date | Last campus visit |

### 3. Placement Job Opening
**Purpose**: Job postings from companies

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| job_title | Data | Position title |
| company | Link (Placement Company) | Recruiting company |
| job_type | Select | Full-time/Internship/PPO |
| job_description | Text Editor | Role description |
| location | Data | Work location |
| package_ctc | Currency | Annual CTC |
| package_details | Text | Detailed compensation |
| bond_period | Int | Bond years (if any) |
| eligible_programs | Table | Eligible degrees |
| min_cgpa | Float | Minimum CGPA |
| max_backlogs | Int | Allowed backlogs |
| batch_year | Data | Graduating batch |
| application_deadline | Date | Last date to apply |
| positions_available | Int | Number of openings |
| positions_filled | Int | Offers made |
| status | Select | Open/Closed/On Hold |

### 4. Job Eligible Program (Child Table)
**Purpose**: Programs eligible for job

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| program | Link (Program) | Degree program |
| min_cgpa | Float | Program-specific CGPA |
| branches | Data | Specific branches |

### 5. Placement Drive
**Purpose**: Campus recruitment events

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| drive_name | Data | e.g., "TCS Campus 2024" |
| company | Link (Placement Company) | Company |
| job_opening | Link (Placement Job Opening) | Related job |
| drive_date | Date | Event date |
| venue | Data | Location |
| registration_deadline | Date | Registration last date |
| rounds | Table | Interview rounds |
| registered_students | Int | Total registered |
| selected_students | Int | Final selections |
| status | Select | Scheduled/Ongoing/Completed |
| coordinator | Link (User) | Placement officer |

### 6. Placement Round (Child Table)
**Purpose**: Interview round details

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| round_number | Int | Sequence |
| round_type | Select | Aptitude/Technical/HR/GD |
| round_date | Date | Date |
| round_time | Time | Start time |
| venue | Data | Location |
| panel_members | Small Text | Interviewers |
| qualified_count | Int | Students passed |

**Round Types**:
1. Online Aptitude Test
2. Technical Test
3. Group Discussion
4. Technical Interview
5. HR Interview
6. Final Interview

### 7. Placement Application
**Purpose**: Student job applications

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Applicant |
| student_name | Data | Name |
| job_opening | Link (Placement Job Opening) | Job applied |
| drive | Link (Placement Drive) | Drive (if applicable) |
| resume | Link (Student Resume) | Attached resume |
| application_date | Date | Applied date |
| current_round | Int | Current stage |
| round_status | Table | Round-wise status |
| final_status | Select | Applied/Shortlisted/Selected/Rejected |
| package_offered | Currency | Offer CTC |
| offer_date | Date | Offer date |
| joining_date | Date | Expected joining |
| offer_letter | Attach | Offer document |

**Application Workflow**:
```
Applied --> Shortlisted --> Round 1 --> Round 2 --> ... --> Selected
                |              |           |
                v              v           v
           Rejected        Rejected    Rejected
```

### 8. Student Resume
**Purpose**: Student CV/profile

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| headline | Data | Profile headline |
| summary | Text | Career objective |
| education | Table | Academic details |
| skills | Table | Technical skills |
| projects | Table | Project experience |
| certifications | Small Text | Certifications |
| achievements | Small Text | Awards/achievements |
| resume_pdf | Attach | Generated PDF |
| last_updated | Datetime | Update timestamp |

### 9-11. Resume Child Tables
**Resume Education**: Degree, institution, year, CGPA
**Resume Project**: Title, description, technologies, duration
**Resume Skill**: Skill name, proficiency level

## Data Flow Diagrams

### Placement Cycle Flow
```
+----------------+     +------------------+     +------------------+
| Company        |---->| Job Opening      |---->| Placement        |
| Registration   |     | Created          |     | Drive Scheduled  |
+----------------+     +------------------+     +------------------+
                                                        |
+----------------+     +------------------+             |
|   Selection    |<----|   Interview      |<------------+
|   Finalized    |     |   Rounds         |
+----------------+     +------------------+
        |
        v
+----------------+
|  Offer Letter  |
|  Generated     |
+----------------+
```

### Student Application Flow
```
+----------------+     +------------------+     +------------------+
|  Student       |---->|  Check           |---->|  Submit          |
|  Browses Jobs  |     |  Eligibility     |     |  Application     |
+----------------+     +------------------+     +------------------+
                                                        |
                              +-------------------------+
                              |
                              v
+----------------+     +------------------+
|   Offer        |<----|   Progress       |
|   Letter       |     |   Through Rounds |
+----------------+     +------------------+
```

### Eligibility Check
```
+------------------------------------------------------------------+
|                    ELIGIBILITY CRITERIA                           |
+------------------------------------------------------------------+
|                                                                   |
|  Student: John Doe                                                |
|  Program: B.Tech CSE                                              |
|  CGPA: 7.5                                                        |
|  Backlogs: 0                                                      |
|                                                                   |
|  Job: Software Engineer at TechCorp                               |
|  Required: B.Tech CSE/IT/ECE, Min CGPA 7.0, Max Backlogs 0        |
|                                                                   |
|  Result: ELIGIBLE                                                 |
|                                                                   |
+------------------------------------------------------------------+
```

## Integration Points

### Eligibility Verification
```python
def check_placement_eligibility(student, job_opening):
    """Check if student is eligible for job"""
    student_doc = frappe.get_doc("Student", student)
    job_doc = frappe.get_doc("Placement Job Opening", job_opening)

    # Check program eligibility
    student_program = student_doc.custom_program
    eligible_programs = [p.program for p in job_doc.eligible_programs]

    if student_program not in eligible_programs:
        return {"eligible": False, "reason": "Program not eligible"}

    # Check CGPA
    student_cgpa = student_doc.custom_cgpa or 0
    if student_cgpa < job_doc.min_cgpa:
        return {"eligible": False, "reason": f"CGPA below {job_doc.min_cgpa}"}

    # Check backlogs
    student_backlogs = get_backlog_count(student)
    if student_backlogs > job_doc.max_backlogs:
        return {"eligible": False, "reason": "Too many backlogs"}

    return {"eligible": True, "reason": "All criteria met"}
```

### With Student Portal
```python
# Portal API for students
@frappe.whitelist()
def get_eligible_jobs(student):
    """Get jobs student is eligible for"""
    jobs = frappe.get_all("Placement Job Opening", {"status": "Open"})

    eligible_jobs = []
    for job in jobs:
        eligibility = check_placement_eligibility(student, job.name)
        if eligibility["eligible"]:
            eligible_jobs.append(job)

    return eligible_jobs

@frappe.whitelist()
def apply_for_job(student, job_opening, resume=None):
    """Submit job application"""
    eligibility = check_placement_eligibility(student, job_opening)
    if not eligibility["eligible"]:
        frappe.throw(eligibility["reason"])

    application = frappe.new_doc("Placement Application")
    application.student = student
    application.job_opening = job_opening
    application.resume = resume
    application.insert()

    return application
```

### Statistics Update
```python
# Scheduled task for placement statistics
def update_placement_statistics():
    """Update placement statistics monthly"""
    batch_year = frappe.utils.nowdate()[:4]

    stats = {
        "total_students": frappe.db.count("Student", {"batch_year": batch_year}),
        "students_placed": frappe.db.count("Placement Application", {
            "final_status": "Selected",
            "batch_year": batch_year
        }),
        "companies_visited": frappe.db.sql("""
            SELECT COUNT(DISTINCT company) FROM `tabPlacement Drive`
            WHERE YEAR(drive_date) = %s
        """, batch_year)[0][0],
        "highest_package": frappe.db.sql("""
            SELECT MAX(package_offered) FROM `tabPlacement Application`
            WHERE final_status = 'Selected' AND batch_year = %s
        """, batch_year)[0][0],
        "average_package": frappe.db.sql("""
            SELECT AVG(package_offered) FROM `tabPlacement Application`
            WHERE final_status = 'Selected' AND batch_year = %s
        """, batch_year)[0][0],
    }

    return stats
```

## API Endpoints

### Company & Jobs
```python
@frappe.whitelist()
def get_active_companies():
    """Get active recruiting companies"""
    return frappe.get_all("Placement Company",
        filters={"partnership_status": "Active"},
        fields=["name", "company_name", "industry_type", "logo"]
    )

@frappe.whitelist()
def get_job_details(job_opening):
    """Get complete job details"""
    job = frappe.get_doc("Placement Job Opening", job_opening)
    company = frappe.get_doc("Placement Company", job.company)

    return {
        "job": job.as_dict(),
        "company": company.as_dict(),
        "applications_count": frappe.db.count("Placement Application", {
            "job_opening": job_opening
        })
    }
```

### Application Tracking
```python
@frappe.whitelist()
def get_application_status(student):
    """Get all applications for student"""
    applications = frappe.get_all("Placement Application",
        filters={"student": student},
        fields=["name", "job_opening", "final_status", "current_round"]
    )

    for app in applications:
        job = frappe.get_doc("Placement Job Opening", app.job_opening)
        app["company"] = job.company
        app["job_title"] = job.job_title

    return applications

@frappe.whitelist()
def update_round_status(application, round_number, status, remarks=None):
    """Update application round status"""
    app = frappe.get_doc("Placement Application", application)
    app.current_round = round_number

    if status == "Passed":
        app.current_round += 1
    elif status == "Failed":
        app.final_status = "Rejected"

    app.save()
    return app
```

## Reports

1. **Placement Dashboard** - Overall statistics
2. **Company Visits Report** - Recruiters by year
3. **Student Placement Report** - Placed students list
4. **Package Analysis Report** - CTC distribution
5. **Program-wise Placement** - By department
6. **Unplaced Students Report** - Students yet to be placed

## Related Files

```
university_erp/
+-- university_placement/
    +-- doctype/
    |   +-- industry_type/
    |   +-- placement_company/
    |   +-- job_eligible_program/
    |   +-- placement_job_opening/
    |   +-- placement_drive/
    |   +-- placement_round/
    |   +-- placement_application/
    |   +-- student_resume/
    |   +-- resume_education/
    |   +-- resume_project/
    |   +-- resume_skill/
    +-- api.py
```

## See Also

- [Student Info Module](03_STUDENT_INFO.md)
- [University Portals Module](15_UNIVERSITY_PORTALS.md)
- [Academics Module](01_ACADEMICS.md)
