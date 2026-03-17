# User Personas & Role Definitions

## Document Purpose

This document defines detailed user personas for the University ERP system. These personas represent the actual users who will interact with the application. Use these to guide design decisions and prioritize features.

---

## 1. Student Personas

### 1.1 Primary Persona: Rahul (Undergraduate Student)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                RAHUL SHARMA                                          │
│                           B.Tech Computer Science, 3rd Year                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 20                │
│  Location: Hostel       │
│  Device: Android Phone  │
│  Internet: 4G Mobile    │
│  Tech Level: High       │
└─────────────────────────┘

BACKGROUND:
Rahul is a 3rd year B.Tech student from a middle-class family in Lucknow. He stays
in the college hostel and primarily uses his smartphone for everything. He's tech-savvy
and comfortable with apps. His laptop is 5 years old and he uses it mainly for coding
assignments.

GOALS:
├── Check daily class schedule quickly
├── Track attendance percentage (need 75% minimum)
├── Pay fees before deadline to avoid late fees
├── Check exam schedule and download hall tickets
├── View results as soon as they're published
└── Apply for placements when eligible

PAIN POINTS:
├── "The current system is confusing, too many menus"
├── "I can't easily see my attendance percentage"
├── "Fee payment process has too many steps"
├── "I never know when results are published"
└── "Site doesn't work well on phone"

TYPICAL DAY:
08:00 │ Wake up, check today's classes on phone
09:00 │ Attend classes
12:00 │ Check if any new notices during lunch
15:00 │ Check attendance after last class marked
19:00 │ Check for any assignment deadlines
22:00 │ Sometimes check placement updates

DEVICE USAGE:
├── Phone: 95% of interactions
├── Laptop: 5% (only for downloading documents)
└── Desktop: Never

KEY METRICS RAHUL TRACKS:
├── Attendance: 76% (just above minimum)
├── Pending Fees: ₹45,000
├── CGPA: 7.8
├── Classes Today: 4
└── Days to Next Exam: 23

DESIGN IMPLICATIONS:
├── Mobile-first is essential
├── Dashboard should show attendance prominently
├── One-tap fee payment
├── Push notifications for results/notices
├── Quick access to today's timetable
└── Offline access to schedule
```

### 1.2 Secondary Persona: Priya (Postgraduate Student)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                PRIYA MENON                                           │
│                              M.Tech Data Science, 1st Year                           │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 24                │
│  Location: Day Scholar  │
│  Device: iPhone + Mac   │
│  Internet: Home WiFi    │
│  Tech Level: Very High  │
└─────────────────────────┘

BACKGROUND:
Priya completed her B.Tech from another college and joined for M.Tech. She's a day
scholar living at home. She has industry experience from a 1-year internship. She
uses both phone and laptop interchangeably.

GOALS:
├── Manage research project timelines
├── Track thesis progress
├── Access research papers through library
├── Coordinate with faculty mentor
├── Check stipend/fellowship payments
└── Find placement opportunities

DIFFERENCES FROM RAHUL:
├── More focused on research than classes
├── Needs document management features
├── Tracks stipend instead of fees
├── Interacts more with specific faculty
└── Uses laptop more often

DESIGN IMPLICATIONS:
├── Research/thesis tracking section
├── Faculty messaging feature
├── Document upload/download
├── Stipend tracking
└── Desktop experience matters
```

### 1.3 Tertiary Persona: Suresh (Parent/Guardian)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                SURESH KUMAR                                          │
│                           Parent of B.Com 2nd Year Student                           │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 48                │
│  Location: Small Town   │
│  Device: Basic Android  │
│  Internet: Slow 4G      │
│  Tech Level: Low        │
└─────────────────────────┘

BACKGROUND:
Suresh is a government employee in a small town. His daughter Sneha studies B.Com
at the university. He's not very tech-savvy and struggles with complex apps. He
prefers Hindi but can read basic English.

GOALS:
├── Pay daughter's fees on time
├── Check if daughter is attending classes
├── View exam results
├── Contact college if needed
└── Download fee receipts for tax purposes

PAIN POINTS:
├── "I don't understand all these English terms"
├── "Too many options, I just want to pay fees"
├── "I never know if payment went through"
├── "Can't find the receipt to download"
└── "Site is too slow on my phone"

KEY TASKS (Limited):
├── Pay fees (quarterly)
├── Check attendance (monthly)
├── View results (semester end)
└── Download receipts (tax season)

DESIGN IMPLICATIONS:
├── Simple, focused interface
├── Large text and buttons
├── Hindi language support (future)
├── Clear payment confirmation
├── Easy receipt download
├── Works on slow connections
└── Minimal navigation depth
```

---

## 2. Faculty Personas

### 2.1 Primary Persona: Dr. Ananya (Assistant Professor)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            DR. ANANYA KRISHNAMURTHY                                  │
│                        Assistant Professor, Computer Science                         │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 32                │
│  Experience: 5 years    │
│  Device: Laptop + Phone │
│  Location: On Campus    │
│  Tech Level: High       │
└─────────────────────────┘

BACKGROUND:
Dr. Ananya teaches 3 courses per semester to undergraduate students. She handles
approximately 180 students across her courses. She's also pursuing research and
mentors 5 final year project students.

DAILY RESPONSIBILITIES:
├── Teaching: 3-4 hours
├── Attendance marking: After each class
├── Student queries: Throughout day
├── Research: 2-3 hours
└── Administrative: 1 hour

GOALS:
├── Mark attendance quickly (60 students per class)
├── Enter grades for assignments/tests
├── Track mentee progress
├── Submit leave applications
├── View payslips and tax info
└── Upload course materials

PAIN POINTS:
├── "Marking attendance for 60 students takes forever"
├── "I can't mark attendance from my phone during class"
├── "Grade entry system is clunky"
├── "I forget which students I'm mentoring"
├── "Can't access payslips easily"
└── "Have to switch between too many systems"

TYPICAL CLASS WORKFLOW:
09:00 │ Open class roster
09:05 │ Start class
09:50 │ End class
09:52 │ Mark attendance (should take <2 min)
09:55 │ Move to next class

ATTENDANCE MARKING PATTERNS:
├── Prefers: "Mark all present, then mark absents"
├── Needs: Search by name/roll number
├── Wants: Remember last class attendance
└── Required: Bulk operations

DESIGN IMPLICATIONS:
├── Fast attendance marking (bulk actions)
├── Mobile-friendly attendance UI
├── Quick grade entry forms
├── Mentee dashboard section
├── Integrated HR self-service
└── Course material management
```

### 2.2 Secondary Persona: Prof. Sharma (Senior Professor)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              PROF. R.K. SHARMA                                       │
│                         Professor & Department Head, Mechanical                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 55                │
│  Experience: 28 years   │
│  Device: Desktop only   │
│  Location: Office       │
│  Tech Level: Medium     │
└─────────────────────────┘

BACKGROUND:
Prof. Sharma is a senior professor and department head. He teaches 1-2 courses but
has significant administrative responsibilities. He prefers desktop and finds mobile
apps difficult. He has an assistant who helps with some tasks.

ADDITIONAL RESPONSIBILITIES:
├── Approve leave for department faculty
├── Review academic reports
├── Approve grade sheets
├── Department budget oversight
└── Faculty recruitment interviews

PAIN POINTS:
├── "Too many clicks to do simple things"
├── "I prefer larger screens and bigger text"
├── "Can't understand mobile apps"
├── "Need printable reports"
└── "System should work like it did before"

DESIGN IMPLICATIONS:
├── Desktop-optimized interface
├── Larger fonts option
├── Print-friendly reports
├── Approval workflows
├── Department overview dashboard
└── Simple, familiar patterns
```

---

## 3. HR Staff Personas

### 3.1 Primary Persona: Meera (HR Executive)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                MEERA GUPTA                                           │
│                           HR Executive, Human Resources                              │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 28                │
│  Experience: 4 years    │
│  Device: Desktop        │
│  Workstation: Shared PC │
│  Tech Level: Medium     │
└─────────────────────────┘

BACKGROUND:
Meera handles day-to-day HR operations including leave management, employee records,
and payroll processing. She works 9-5 and processes high volumes of requests,
especially at month-end.

DAILY TASKS:
├── Process leave applications: 10-15/day
├── Update employee records: 5-10/day
├── Handle employee queries: 20+/day
├── Document verification: As needed
└── Report generation: Weekly

MONTHLY TASKS:
├── Payroll processing: 3 days
├── Attendance consolidation: 2 days
├── Compliance reports: 1 day
└── New joining formalities: As needed

GOALS:
├── Process leave requests quickly
├── Keep employee records accurate
├── Run payroll without errors
├── Generate reports on demand
├── Track pending tasks
└── Maintain compliance documents

PAIN POINTS:
├── "Leave requests pile up, hard to track"
├── "Switching between employee records is slow"
├── "Payroll calculation takes too long"
├── "Can't see my pending tasks at a glance"
├── "Report generation is manual and tedious"
└── "No reminder for document expiries"

WORKFLOW: LEAVE APPROVAL
1. See pending leave request
2. Click to view details
3. Check employee's leave balance
4. Check team calendar for conflicts
5. Approve or reject with comment
6. Move to next request
(Should take < 1 minute per request)

DESIGN IMPLICATIONS:
├── Task queue/inbox approach
├── Quick actions on list views
├── Inline editing where possible
├── Bulk processing capabilities
├── Dashboard with pending counts
├── Calendar views for leave
└── One-click report generation
```

### 3.2 Secondary Persona: Rajesh (HR Manager)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                RAJESH VERMA                                          │
│                           HR Manager, Human Resources                                │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 42                │
│  Experience: 15 years   │
│  Device: Desktop + Phone│
│  Tech Level: Medium     │
└─────────────────────────┘

BACKGROUND:
Rajesh oversees the HR team and handles strategic HR functions. He approves
final-level requests, manages budgets, and reports to management.

KEY RESPONSIBILITIES:
├── Final approval for leaves/claims
├── Salary revision approvals
├── Recruitment decisions
├── HR budget management
├── Management reports
└── Policy compliance

GOALS:
├── Overview of HR metrics
├── Quick approvals (delegated items)
├── Exception handling
├── Trend analysis
└── Compliance monitoring

DESIGN IMPLICATIONS:
├── Executive dashboard with KPIs
├── Approval queue with filters
├── Trend charts and analytics
├── Exception highlighting
├── Mobile access for approvals
└── Drill-down capabilities
```

---

## 4. Accounts Staff Personas

### 4.1 Primary Persona: Sunita (Accounts Executive)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                SUNITA AGARWAL                                        │
│                         Accounts Executive, Finance Department                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 35                │
│  Experience: 10 years   │
│  Device: Desktop        │
│  Workstation: Counter   │
│  Tech Level: Medium     │
└─────────────────────────┘

BACKGROUND:
Sunita works at the fee collection counter. She handles student fee payments,
issues receipts, and manages the cash register. During admission season, she
processes 100+ payments daily.

DAILY TASKS:
├── Fee collection: 30-50 transactions
├── Receipt printing: For each payment
├── Query handling: Fee breakup, due dates
├── Cash reconciliation: End of day
└── Report to accountant: Daily summary

PEAK PERIODS:
├── Admission season: 100+ transactions/day
├── Fee due dates: 80+ transactions/day
├── Result release: 50+ (for revaluation fees)
└── Normal days: 20-30 transactions/day

GOALS:
├── Process payments quickly (student waiting)
├── Find student records fast (by ID/name)
├── Generate correct receipts
├── Avoid cash/transaction errors
├── Track daily collection
└── Close register accurately

PAIN POINTS:
├── "Student search is slow"
├── "Can't see complete fee breakup easily"
├── "Receipt printing sometimes fails"
├── "Hard to handle partial payments"
├── "Cash reconciliation is manual"
└── "No way to verify online payments quickly"

WORKFLOW: FEE COLLECTION
1. Student arrives at counter
2. Ask for student ID
3. Search and find student (< 5 seconds)
4. Show pending fees with breakup
5. Confirm amount to pay
6. Enter payment details (cash/cheque/DD)
7. Confirm and print receipt
8. Hand receipt to student
(Total time should be < 2 minutes)

DESIGN IMPLICATIONS:
├── Fast student search (autocomplete)
├── Clear fee breakup display
├── Quick payment mode selection
├── Reliable receipt printing
├── Cash drawer integration (future)
├── Payment verification for online
├── Daily collection dashboard
└── One-click reconciliation
```

### 4.2 Secondary Persona: CA Amit (Chief Accountant)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                CA AMIT JOSHI                                         │
│                              Chief Accountant, Finance                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 45                │
│  Qualification: CA      │
│  Device: Desktop        │
│  Tech Level: Medium     │
└─────────────────────────┘

BACKGROUND:
CA Amit manages the overall financial operations. He oversees fee collection,
budget management, audits, and financial reporting. He reports to the Director.

KEY RESPONSIBILITIES:
├── Financial oversight
├── Budget preparation and tracking
├── Audit coordination
├── Statutory compliance
├── Management reports
└── Fee structure decisions

GOALS:
├── Real-time collection visibility
├── Outstanding dues tracking
├── Budget vs actual analysis
├── Audit-ready reports
├── Trend analysis
└── Exception monitoring

DESIGN IMPLICATIONS:
├── Financial dashboard with KPIs
├── Drill-down reports
├── Comparison charts
├── Export to Excel/PDF
├── Audit trail access
├── Role-based data access
└── Scheduled report generation
```

---

## 5. Admin Personas

### 5.1 System Administrator

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                VIKRAM SINGH                                          │
│                            System Administrator, IT                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│        PROFILE          │
├─────────────────────────┤
│  Age: 30                │
│  Experience: 6 years    │
│  Device: Desktop/Laptop │
│  Tech Level: Very High  │
└─────────────────────────┘

BACKGROUND:
Vikram manages the technical infrastructure and user administration. He handles
user creation, permissions, system configuration, and troubleshooting.

KEY RESPONSIBILITIES:
├── User account management
├── Role and permission setup
├── System configuration
├── Data imports/exports
├── Troubleshooting issues
└── Backup monitoring

GOALS:
├── Efficient user management
├── Granular permission control
├── System health monitoring
├── Quick issue resolution
├── Audit log access
└── Bulk operations

DESIGN IMPLICATIONS:
├── User management interface
├── Role/permission matrix
├── System settings panel
├── Activity/audit logs
├── Bulk import/export
├── Search across all data
└── Technical diagnostics
```

---

## 6. Role Permission Matrix

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ROLE PERMISSION MATRIX                                          │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘

                           Student  Guardian  Faculty  HR Staff  HR Mgr  Accounts  Acct Mgr  Admin
                           ───────  ────────  ───────  ────────  ──────  ────────  ────────  ─────
STUDENT MODULE
├── View own profile          ✓        ✓         -        -        -        -         -        ✓
├── View own attendance       ✓        ✓         -        -        -        -         -        ✓
├── View own grades           ✓        ✓         -        -        -        -         -        ✓
├── View own fees             ✓        ✓         -        -        -        -         -        ✓
├── Pay fees                  ✓        ✓         -        -        -        -         -        -
├── View timetable            ✓        ✓         -        -        -        -         -        ✓
├── Download documents        ✓        ✓         -        -        -        -         -        ✓
└── Submit grievance          ✓        -         -        -        -        -         -        -

FACULTY MODULE
├── View own classes          -        -         ✓        -        -        -         -        ✓
├── Mark attendance           -        -         ✓        -        -        -         -        ✓
├── Enter grades              -        -         ✓        -        -        -         -        ✓
├── View student list         -        -         ✓        -        -        -         -        ✓
├── Upload materials          -        -         ✓        -        -        -         -        ✓
├── View mentees              -        -         ✓        -        -        -         -        ✓
├── Apply for leave           -        -         ✓        -        -        -         -        -
├── View payslips             -        -         ✓        -        -        -         -        -
└── View own attendance       -        -         ✓        -        -        -         -        -

HR MODULE
├── View employee list        -        -         -        ✓        ✓        -         -        ✓
├── Edit employee records     -        -         -        ✓        ✓        -         -        ✓
├── Process leave             -        -         -        ✓        ✓        -         -        -
├── Approve leave             -        -         -        -        ✓        -         -        -
├── Process payroll           -        -         -        ✓        ✓        -         -        -
├── Approve payroll           -        -         -        -        ✓        -         -        -
├── View HR reports           -        -         -        ✓        ✓        -         -        ✓
├── Manage recruitment        -        -         -        ✓        ✓        -         -        -
└── System settings           -        -         -        -        ✓        -         -        ✓

ACCOUNTS MODULE
├── View fee structure        -        -         -        -        -        ✓         ✓        ✓
├── Collect fees              -        -         -        -        -        ✓         ✓        -
├── Issue receipts            -        -         -        -        -        ✓         ✓        -
├── View payment history      -        -         -        -        -        ✓         ✓        ✓
├── Generate reports          -        -         -        -        -        ✓         ✓        ✓
├── Manage budgets            -        -         -        -        -        -         ✓        ✓
├── Approve adjustments       -        -         -        -        -        -         ✓        -
└── View all financial data   -        -         -        -        -        -         ✓        ✓

ADMIN MODULE
├── Manage users              -        -         -        -        -        -         -        ✓
├── Manage roles              -        -         -        -        -        -         -        ✓
├── System configuration      -        -         -        -        -        -         -        ✓
├── View audit logs           -        -         -        -        -        -         -        ✓
├── Manage academic setup     -        -         -        -        -        -         -        ✓
└── Generate system reports   -        -         -        -        -        -         -        ✓
```

---

## 7. Usage Frequency Matrix

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    USAGE FREQUENCY MATRIX                                          │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘

FEATURE                        STUDENT    FACULTY    HR STAFF   ACCOUNTS
─────────────────────────────  ─────────  ─────────  ─────────  ─────────
Dashboard                      Daily      Daily      Daily      Daily
Timetable/Schedule             Daily      Daily      -          -
Attendance (View)              Daily      -          Weekly     -
Attendance (Mark)              -          Daily      -          -
Grades (View)                  Weekly     -          -          -
Grades (Enter)                 -          Weekly     -          -
Fee Payment                    Monthly    -          -          -
Fee Collection                 -          -          -          Daily
Leave Apply                    Monthly    Monthly    -          -
Leave Approve                  -          -          Daily      -
Payroll                        -          -          Monthly    -
Reports                        Rare       Weekly     Weekly     Daily
Profile Update                 Rare       Rare       Daily      -
Notifications                  Daily      Daily      Daily      Daily
```

---

## 8. Design Priority by Persona

### High Priority (Design First)
1. **Rahul (Student)** - Largest user base, mobile-first
2. **Dr. Ananya (Faculty)** - Daily operations, attendance/grades
3. **Meera (HR Executive)** - Transaction volume
4. **Sunita (Accounts Executive)** - Fee collection efficiency

### Medium Priority (Design Second)
5. **Suresh (Parent)** - Simpler subset of student features
6. **Rajesh (HR Manager)** - Approval workflows
7. **CA Amit (Accountant)** - Reports and dashboards

### Lower Priority (Design Later)
8. **Priya (PG Student)** - Variant of student
9. **Prof. Sharma (Senior)** - Desktop accessibility
10. **Vikram (Admin)** - Technical interface

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Audience**: UI/UX Design Team
