# University Portals Module

## Overview

The University Portals module manages self-service web interfaces for students, alumni, and external users. It handles alumni engagement, public announcements, job postings, and provides portal-specific functionality separate from the main ERP desk interface.

## Module Location
```
university_erp/university_portals/
```

## DocTypes (8 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Alumni | Main | Alumni profiles |
| Alumni Event | Main | Alumni events |
| Alumni Event Registration | Main | Event attendance |
| Announcement | Main | Public announcements |
| Placement Profile | Main | Student placement profile |
| Placement Drive | Main | Portal placement drives |
| Placement Application | Main | Portal job applications |
| Job Posting | Main | External job postings |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                    UNIVERSITY PORTALS MODULE                      |
+------------------------------------------------------------------+
|                                                                   |
|  ALUMNI PORTAL                                                    |
|  +-------------------+       +-------------------+                |
|  |      ALUMNI       |       |  ALUMNI EVENT     |                |
|  +-------------------+       +-------------------+                |
|  | - Profile         |       | - Event details   |                |
|  | - Employment      |       | - Registrations   |                |
|  | - Contact         |       +-------------------+                |
|  +-------------------+              |                             |
|           |                         v                             |
|           |                  +-------------------+                |
|           |                  | Alumni Event      |                |
|           |                  |  Registration     |                |
|           |                  +-------------------+                |
|           |                                                       |
|  PLACEMENT PORTAL                                                 |
|  +-------------------+       +-------------------+                |
|  | PLACEMENT PROFILE |       | PLACEMENT DRIVE   |                |
|  +-------------------+       +-------------------+                |
|  | - Skills          |       | - Company         |                |
|  | - Resume          |       | - Positions       |                |
|  +-------------------+       +-------------------+                |
|           |                         |                             |
|           v                         v                             |
|  +-------------------+       +-------------------+                |
|  |    PLACEMENT      |       |   JOB POSTING     |                |
|  |   APPLICATION     |       |   (Alumni/External|                |
|  +-------------------+       +-------------------+                |
|                                                                   |
|  PUBLIC PORTAL                                                    |
|  +-------------------+                                            |
|  |   ANNOUNCEMENT    |                                            |
|  +-------------------+                                            |
|  | - News            |                                            |
|  | - Events          |                                            |
|  | - Notices         |                                            |
|  +-------------------+                                            |
|                                                                   |
+------------------------------------------------------------------+
```

## Portal Types & Access

```
+------------------------------------------------------------------+
|                        PORTAL ECOSYSTEM                           |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  |  STUDENT PORTAL   |       |  FACULTY PORTAL   |                |
|  +-------------------+       +-------------------+                |
|  | Access:           |       | Access:           |                |
|  | - Academics       |       | - Classes         |                |
|  | - Fees            |       | - Attendance      |                |
|  | - Library         |       | - Grades          |                |
|  | - Placement       |       | - Leave           |                |
|  | - LMS             |       | - Feedback        |                |
|  +-------------------+       +-------------------+                |
|                                                                   |
|  +-------------------+       +-------------------+                |
|  |   ALUMNI PORTAL   |       |   PARENT PORTAL   |                |
|  +-------------------+       +-------------------+                |
|  | Access:           |       | Access:           |                |
|  | - Events          |       | - Child progress  |                |
|  | - Directory       |       | - Fees            |                |
|  | - Job Posting     |       | - Attendance      |                |
|  | - Mentoring       |       | - Announcements   |                |
|  +-------------------+       +-------------------+                |
|                                                                   |
|  +-------------------+                                            |
|  |   PUBLIC PORTAL   |                                            |
|  +-------------------+                                            |
|  | Access:           |                                            |
|  | - Announcements   |                                            |
|  | - Admissions      |                                            |
|  | - Contact         |                                            |
|  +-------------------+                                            |
|                                                                   |
+------------------------------------------------------------------+
```

## DocType Details

### 1. Alumni
**Purpose**: Alumni profiles and engagement

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| alumni_id | Data | Unique identifier |
| user | Link (User) | Portal login |
| first_name | Data | First name |
| last_name | Data | Last name |
| graduation_year | Data | Year graduated |
| program | Link (Program) | Degree completed |
| department | Link (Department) | Department |
| email | Data | Contact email |
| phone | Data | Phone number |
| current_employer | Data | Company name |
| designation | Data | Job title |
| industry | Data | Industry sector |
| linkedin_url | Data | LinkedIn profile |
| location | Data | Current city |
| is_mentor | Check | Available for mentoring |
| mentoring_topics | Small Text | Mentoring areas |
| membership_type | Select | Regular/Premium/Lifetime |
| membership_expiry | Date | Expiry date |
| photo | Attach Image | Profile photo |
| bio | Text | About section |

### 2. Alumni Event
**Purpose**: Alumni meetups and events

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| event_name | Data | Event title |
| event_type | Select | Reunion/Meetup/Webinar/Workshop |
| description | Text Editor | Event details |
| event_date | Date | Event date |
| start_time | Time | Start time |
| end_time | Time | End time |
| venue | Data | Location |
| is_virtual | Check | Online event |
| meeting_link | Data | Virtual meeting URL |
| organizer | Link (Alumni) | Event organizer |
| max_participants | Int | Capacity |
| registration_deadline | Date | Last date to register |
| registration_fee | Currency | Event fee |
| banner_image | Attach Image | Event banner |
| status | Select | Upcoming/Ongoing/Completed/Cancelled |

### 3. Alumni Event Registration
**Purpose**: Track event attendance

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| event | Link (Alumni Event) | Event |
| alumni | Link (Alumni) | Registrant |
| registration_date | Date | Registration date |
| payment_status | Select | Pending/Paid/Waived |
| attended | Check | Actually attended |
| feedback | Text | Post-event feedback |
| rating | Int | Event rating |

### 4. Announcement
**Purpose**: Public announcements and notices

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| title | Data | Announcement title |
| announcement_type | Select | News/Event/Notice/Alert |
| content | Text Editor | Full content |
| summary | Small Text | Short description |
| publish_date | Date | Publication date |
| expiry_date | Date | When to hide |
| target_audience | Multi Select | Student/Faculty/Alumni/Public |
| is_featured | Check | Show prominently |
| is_pinned | Check | Pin to top |
| banner_image | Attach Image | Featured image |
| attachments | Table | Related files |
| status | Select | Draft/Published/Archived |

### 5. Placement Profile
**Purpose**: Student profile for placements

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| headline | Data | Profile headline |
| about | Text | Summary |
| skills | Table MultiSelect | Technical skills |
| certifications | Small Text | Certifications |
| projects | Text | Project descriptions |
| internships | Text | Work experience |
| achievements | Text | Awards/achievements |
| resume | Attach | Uploaded resume |
| is_seeking_placement | Check | Actively looking |
| preferred_locations | Data | Preferred cities |
| expected_ctc | Currency | Salary expectation |
| profile_completeness | Percent | Completion percentage |

### 6. Placement Drive (Portal)
**Purpose**: Campus drives visible on portal

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| company_name | Data | Recruiting company |
| job_title | Data | Position |
| job_description | Text Editor | Role details |
| package | Data | CTC range |
| eligibility | Text | Requirements |
| drive_date | Date | Drive date |
| application_deadline | Date | Last date |
| eligible_programs | Table MultiSelect | Eligible degrees |
| min_cgpa | Float | CGPA requirement |
| is_active | Check | Open for applications |

### 7. Placement Application (Portal)
**Purpose**: Student job applications via portal

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Applicant |
| drive | Link (Placement Drive) | Applied drive |
| placement_profile | Link (Placement Profile) | Profile used |
| application_date | Datetime | Application time |
| cover_letter | Text | Cover letter |
| status | Select | Applied/Shortlisted/Interviewed/Selected/Rejected |
| feedback | Text | Company feedback |

### 8. Job Posting
**Purpose**: External job listings (alumni/HR posted)

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| job_title | Data | Position title |
| company_name | Data | Company |
| posted_by | Link (Alumni) | Alumni who posted |
| posted_by_hr | Data | If external HR |
| job_description | Text Editor | Full description |
| requirements | Text | Qualifications |
| location | Data | Job location |
| job_type | Select | Full-time/Part-time/Internship |
| experience_required | Data | Experience level |
| salary_range | Data | Compensation |
| application_link | Data | Apply URL |
| contact_email | Data | HR email |
| posting_date | Date | Posted on |
| expiry_date | Date | Valid until |
| is_approved | Check | Admin approved |
| status | Select | Open/Closed |

## Portal Routes & Configuration

### Website Routes (hooks.py)
```python
website_route_rules = [
    {"from_route": "/student-portal/<path:app_path>", "to_route": "student-portal"},
    {"from_route": "/faculty-portal/<path:app_path>", "to_route": "faculty-portal"},
    {"from_route": "/student-feedback/<path:app_path>", "to_route": "student-feedback"},
    {"from_route": "/library/<path:app_path>", "to_route": "library"},
    {"from_route": "/placement/<path:app_path>", "to_route": "placement"},
]
```

### Portal Page Structure
```
www/
+-- student-portal.html        # Student dashboard
+-- faculty-portal.html        # Faculty dashboard
+-- alumni-portal.html         # Alumni dashboard
+-- placement/
|   +-- index.html            # Placement home
|   +-- jobs.html             # Job listings
|   +-- apply.html            # Application form
+-- library/
|   +-- index.html            # Library home
|   +-- catalog.html          # Book search
+-- public/
    +-- announcements.html    # Public announcements
    +-- events.html           # Public events
```

## Data Flow Diagrams

### Student Portal Access
```
+----------------+     +------------------+     +------------------+
|   Student      |---->|   Authentication |---->|   Portal         |
|   Login        |     |   (User/Student  |     |   Dashboard      |
|                |     |    mapping)      |     |                  |
+----------------+     +------------------+     +------------------+
                                                        |
        +-----------------------------------------------+
        |              |              |              |
        v              v              v              v
+------------+  +------------+  +------------+  +------------+
|  Academic  |  |    Fees    |  |  Library   |  | Placement  |
|   Info     |  |  Summary   |  |   Status   |  |   Jobs     |
+------------+  +------------+  +------------+  +------------+
```

### Alumni Registration Flow
```
+----------------+     +------------------+     +------------------+
|   Graduate     |---->|   Request        |---->|   Admin          |
|   Student      |     |   Alumni Access  |     |   Approval       |
+----------------+     +------------------+     +------------------+
                                                        |
+----------------+     +------------------+            |
|   Access       |<----|   Alumni Account |<-----------+
|   Portal       |     |   Created        |
+----------------+     +------------------+
```

## Integration Points

### User-Student Mapping
```python
# Get student for current portal user
def get_student_for_user(user):
    """Get Student record linked to user"""
    student = frappe.db.get_value("Student", {"user": user})
    if not student:
        frappe.throw("No student profile linked to this user")
    return student

# Create user when student is created
def create_student_portal_user(student):
    """Create portal user for student"""
    student_doc = frappe.get_doc("Student", student)

    if not student_doc.user:
        user = frappe.new_doc("User")
        user.email = student_doc.student_email
        user.first_name = student_doc.first_name
        user.last_name = student_doc.last_name
        user.send_welcome_email = True
        user.add_roles("University Student")
        user.insert()

        student_doc.user = user.name
        student_doc.save()

    return student_doc.user
```

### Portal Redirection
```python
# hooks.py
get_website_user_home_page = "university_erp.utils.get_website_user_home_page"

# utils.py
def get_website_user_home_page(user):
    """Redirect user to appropriate portal"""
    roles = frappe.get_roles(user)

    if "University Student" in roles:
        return "/student-portal"
    elif "University Faculty" in roles:
        return "/faculty-portal"
    elif "University Alumni" in roles:
        return "/alumni-portal"

    return None  # Default desk
```

### Portal Data API
```python
@frappe.whitelist()
def get_student_dashboard_data():
    """Get all data for student dashboard"""
    user = frappe.session.user
    student = get_student_for_user(user)

    return {
        "student": frappe.get_doc("Student", student).as_dict(),
        "fees": get_pending_fees(student),
        "attendance": get_attendance_summary(student),
        "courses": get_current_courses(student),
        "announcements": get_recent_announcements(),
        "library": get_library_status(student),
        "placement": get_eligible_drives(student)
    }

@frappe.whitelist()
def get_alumni_dashboard_data():
    """Get alumni portal data"""
    user = frappe.session.user
    alumni = frappe.db.get_value("Alumni", {"user": user})

    return {
        "alumni": frappe.get_doc("Alumni", alumni).as_dict(),
        "upcoming_events": get_upcoming_alumni_events(),
        "my_registrations": get_event_registrations(alumni),
        "job_postings": get_my_job_postings(alumni) if alumni else [],
        "mentorship_requests": get_mentorship_requests(alumni) if alumni else []
    }
```

## API Endpoints

### Student Portal
```python
@frappe.whitelist()
def get_student_profile():
    """Get current student's profile"""
    student = get_student_for_user(frappe.session.user)
    return frappe.get_doc("Student", student)

@frappe.whitelist()
def get_fee_status():
    """Get fee payment status"""
    student = get_student_for_user(frappe.session.user)
    return frappe.get_all("Fees", {
        "student": student,
        "docstatus": 1
    }, ["name", "grand_total", "outstanding_amount", "due_date"])
```

### Alumni Portal
```python
@frappe.whitelist()
def get_alumni_events(status="Upcoming"):
    """Get alumni events"""
    filters = {"status": status}
    return frappe.get_all("Alumni Event", filters,
        ["name", "event_name", "event_date", "venue", "is_virtual"])

@frappe.whitelist()
def register_for_event(event):
    """Register alumni for event"""
    alumni = get_alumni_for_user(frappe.session.user)

    # Check if already registered
    existing = frappe.db.exists("Alumni Event Registration", {
        "event": event,
        "alumni": alumni
    })
    if existing:
        frappe.throw("Already registered for this event")

    registration = frappe.new_doc("Alumni Event Registration")
    registration.event = event
    registration.alumni = alumni
    registration.insert()

    return registration

@frappe.whitelist()
def post_job(job_data):
    """Alumni posts job opening"""
    alumni = get_alumni_for_user(frappe.session.user)

    job = frappe.new_doc("Job Posting")
    job.update(job_data)
    job.posted_by = alumni
    job.posting_date = frappe.utils.today()
    job.is_approved = 0  # Requires admin approval
    job.insert()

    return job
```

### Placement Portal
```python
@frappe.whitelist()
def get_eligible_drives():
    """Get placement drives student is eligible for"""
    student = get_student_for_user(frappe.session.user)
    student_doc = frappe.get_doc("Student", student)

    drives = frappe.get_all("Placement Drive", {
        "is_active": 1,
        "application_deadline": (">=", frappe.utils.today())
    })

    eligible = []
    for drive in drives:
        if check_eligibility(student_doc, drive):
            eligible.append(drive)

    return eligible

@frappe.whitelist()
def apply_for_drive(drive):
    """Apply for placement drive"""
    student = get_student_for_user(frappe.session.user)

    # Check if already applied
    if frappe.db.exists("Placement Application", {
        "student": student,
        "drive": drive
    }):
        frappe.throw("Already applied for this drive")

    application = frappe.new_doc("Placement Application")
    application.student = student
    application.drive = drive
    application.placement_profile = get_placement_profile(student)
    application.insert()

    return application
```

## Reports

1. **Portal Usage Report** - Login statistics
2. **Alumni Engagement Report** - Event participation
3. **Placement Application Report** - Applications via portal
4. **Announcement Reach Report** - Views by audience
5. **Job Posting Report** - Alumni job posts

## Related Files

```
university_erp/
+-- university_portals/
|   +-- doctype/
|   |   +-- alumni/
|   |   +-- alumni_event/
|   |   +-- alumni_event_registration/
|   |   +-- announcement/
|   |   +-- placement_profile/
|   |   +-- placement_drive/
|   |   +-- placement_application/
|   |   +-- job_posting/
|   +-- api.py
+-- www/
    +-- student-portal.html
    +-- faculty-portal.html
    +-- alumni-portal.html
```

## See Also

- [Student Info Module](03_STUDENT_INFO.md)
- [University Placement Module](10_UNIVERSITY_PLACEMENT.md)
- [University LMS Module](11_UNIVERSITY_LMS.md)
