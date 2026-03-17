# University ERP - Project Overview for UI/UX Team

## Document Purpose

This document provides the UI/UX design team with a comprehensive understanding of the University ERP project, its goals, users, and requirements. Use this as your starting point before diving into detailed module specifications.

---

## 1. Project Summary

### What We're Building

A **modern, user-friendly custom frontend** for a University Enterprise Resource Planning (ERP) system that replaces the default Frappe Desk interface with a purpose-built, role-specific interface.

### Why We Need a Custom Frontend

| Current State (Frappe Desk) | Desired State (Custom Frontend) |
|----------------------------|--------------------------------|
| Generic ERP interface | University-specific interface |
| Same UI for all users | Role-specific dashboards |
| Desktop-first design | Mobile-first, responsive |
| Many visible modules/workspaces | Clean, focused navigation |
| Technical appearance | Modern, intuitive design |
| No offline support | PWA with offline capabilities |

### Key Design Goals

1. **Simplicity** - Remove complexity, show only what users need
2. **Mobile-First** - Design for phone first, then scale up
3. **Role-Specific** - Different interfaces for students, faculty, HR, accounts
4. **Modern Aesthetics** - Clean, contemporary design language
5. **Accessibility** - WCAG 2.1 AA compliant
6. **Fast** - Quick load times, instant feedback
7. **Offline-Ready** - Core features work without internet

---

## 2. System Context

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USERS                                             │
│                                                                                      │
│    Students    │    Faculty    │    HR Staff    │    Accounts    │    Admins        │
│    (~2,000)    │    (~70)      │    (~10)       │    (~5)        │    (~5)          │
└───────┬────────────────┬────────────────┬────────────────┬────────────────┬─────────┘
        │                │                │                │                │
        ▼                ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│                        CUSTOM FRONTEND (What You're Designing)                       │
│                                                                                      │
│   ┌───────────────────────────────────────────────────────────────────────────────┐ │
│   │                                                                               │ │
│   │    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│   │    │   Student   │  │   Faculty   │  │     HR      │  │  Accounts   │        │ │
│   │    │   Module    │  │   Module    │  │   Module    │  │   Module    │        │ │
│   │    └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│   │                                                                               │ │
│   │    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│   │    │   Hostel    │  │  Transport  │  │   Library   │  │  Placement  │        │ │
│   │    │   Module    │  │   Module    │  │   Module    │  │   Module    │        │ │
│   │    └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│   │                                                                               │ │
│   └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ API Calls
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                FRAPPE BACKEND                                        │
│                          (Existing - Not Being Changed)                              │
│                                                                                      │
│   Education App  │  HRMS App  │  ERPNext Accounts  │  University ERP (Custom)       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### The Backend Exists - We're Designing the Frontend

The backend system is already built and functional. It contains:
- All data (students, employees, fees, grades, etc.)
- Business logic (fee calculations, attendance rules, etc.)
- User authentication and permissions

**Your job**: Design the visual interface that users interact with.

---

## 3. User Base & Demographics

### Primary Users

| User Type | Count | Age Range | Tech Savviness | Primary Device | Usage Frequency |
|-----------|-------|-----------|----------------|----------------|-----------------|
| Students | ~2,000 | 18-25 | High | Mobile (80%) | Daily |
| Parents/Guardians | ~2,000 | 40-55 | Medium | Mobile (60%) | Weekly |
| Faculty | ~70 | 30-55 | Medium | Desktop (60%) | Daily |
| HR Staff | ~10 | 25-45 | Medium-High | Desktop (80%) | Daily |
| Accounts Staff | ~5 | 30-50 | Medium | Desktop (90%) | Daily |
| System Admins | ~5 | 25-40 | High | Desktop (95%) | Daily |

### Device Distribution

```
STUDENT DEVICE USAGE:
├── Mobile Phone: ████████████████████████████████████████ 80%
├── Laptop: ████████████ 15%
└── Desktop: ███ 5%

FACULTY DEVICE USAGE:
├── Desktop: ████████████████████████ 40%
├── Laptop: ████████████████████ 35%
└── Mobile: ████████████ 25%

HR/ACCOUNTS DEVICE USAGE:
├── Desktop: ████████████████████████████████████████ 80%
├── Laptop: ████████ 15%
└── Mobile: ██ 5%
```

### Connectivity Context

- **On-Campus**: Good WiFi (50-100 Mbps)
- **Off-Campus**: Variable mobile data (3G-4G)
- **Rural Students**: May have limited connectivity
- **Implication**: Need offline support for critical features

---

## 4. Modules Overview

### Module Map

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              UNIVERSITY ERP MODULES                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│     STUDENT MODULE      │   │     FACULTY MODULE      │   │      HR MODULE          │
│                         │   │                         │   │                         │
│  • Dashboard            │   │  • Dashboard            │   │  • Dashboard            │
│  • My Profile           │   │  • My Classes           │   │  • Employees            │
│  • Academics            │   │  • Attendance Marking   │   │  • Leave Management     │
│    - Courses            │   │  • Grade Entry          │   │  • Attendance           │
│    - Timetable          │   │  • Student List         │   │  • Payroll              │
│    - Attendance         │   │  • Course Materials     │   │  • Recruitment          │
│    - Grades             │   │  • Mentees              │   │  • Employee Self-Service│
│  • Fees & Payments      │   │  • HR Self-Service      │   │  • Reports              │
│  • Examinations         │   │    - Leave              │   │                         │
│    - Schedule           │   │    - Attendance         │   │                         │
│    - Hall Tickets       │   │    - Payslips           │   │                         │
│    - Results            │   │  • Research             │   │                         │
│  • Library              │   │  • Reports              │   │                         │
│  • Hostel               │   │                         │   │                         │
│  • Transport            │   │                         │   │                         │
│  • Placement            │   │                         │   │                         │
│  • Grievances           │   │                         │   │                         │
│  • Notifications        │   │                         │   │                         │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘

┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│    ACCOUNTS MODULE      │   │      ADMIN MODULE       │   │   OPTIONAL MODULES      │
│                         │   │                         │   │                         │
│  • Dashboard            │   │  • System Dashboard     │   │  • Hostel               │
│  • Fee Management       │   │  • User Management      │   │    - Room Allocation    │
│    - Fee Structure      │   │  • Role/Permissions     │   │    - Complaints         │
│    - Fee Collection     │   │  • Academic Setup       │   │    - Mess Menu          │
│    - Due Tracking       │   │    - Programs           │   │                         │
│  • Payments             │   │    - Courses            │   │  • Transport            │
│    - Payment Entry      │   │    - Batches            │   │    - Routes             │
│    - Receipts           │   │  • Examination Setup    │   │    - Bus Tracking       │
│    - Reconciliation     │   │  • Reports              │   │                         │
│  • Reports              │   │    - Academic           │   │  • Library              │
│    - Collections        │   │    - Financial          │   │    - Book Search        │
│    - Outstanding        │   │    - HR                 │   │    - Issue/Return       │
│    - Daily Summary      │   │  • System Settings      │   │    - Fines              │
│  • Budgets              │   │  • Audit Logs           │   │                         │
│  • Journal Entries      │   │                         │   │  • Placement            │
│                         │   │                         │   │    - Job Postings       │
│                         │   │                         │   │    - Applications       │
│                         │   │                         │   │    - Interviews         │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘
```

### Module Priorities

| Priority | Module | Reason |
|----------|--------|--------|
| P0 (Critical) | Student | Largest user base, most frequent use |
| P0 (Critical) | Faculty | Daily operations, attendance/grades |
| P1 (High) | HR | Employee management, payroll |
| P1 (High) | Accounts | Fee collection, financial ops |
| P2 (Medium) | Admin | System configuration |
| P3 (Lower) | Hostel, Transport, Library, Placement | Optional features |

---

## 5. Key User Journeys

### Student Journey Map

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           TYPICAL STUDENT DAY                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

MORNING (8:00 AM)
├── Opens app on phone
├── Sees Dashboard with today's schedule
├── Checks which classes are happening
├── Sees notification: "Assignment due tomorrow"
│
DURING CLASS (9:00 AM)
├── Attendance marked by faculty
├── Student sees attendance updated in app
│
BETWEEN CLASSES (11:00 AM)
├── Checks fees - sees pending amount
├── Clicks "Pay Now"
├── Completes payment via UPI/Card
├── Downloads receipt
│
AFTER EXAMS (Periodic)
├── Checks exam schedule
├── Downloads hall ticket
├── After exam: Checks results when published
│
END OF SEMESTER
├── Reviews complete attendance record
├── Checks final grades
├── Downloads grade card
└── Applies for hostel/transport for next semester
```

### Faculty Journey Map

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           TYPICAL FACULTY DAY                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

MORNING (9:00 AM)
├── Opens app on desktop/laptop
├── Sees Dashboard with today's classes
├── Reviews student list for first class
│
DURING CLASS (9:30 AM)
├── Takes attendance
│   └── Quick mark: Present/Absent for each student
├── Uploads class material (optional)
│
AFTER CLASS (11:00 AM)
├── Enters quiz/assignment grades
├── Checks mentee requests
│
MONTHLY
├── Submits leave application
├── Checks leave balance
├── Reviews payslip when released
│
END OF SEMESTER
├── Enters final grades for all courses
├── Submits grade sheet for approval
├── Downloads attendance reports
```

### HR Staff Journey Map

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           TYPICAL HR DAY                                             │
└─────────────────────────────────────────────────────────────────────────────────────┘

MORNING (9:00 AM)
├── Opens Dashboard
├── Reviews pending tasks
│   ├── Leave applications to approve: 5
│   ├── Expense claims to review: 3
│   └── Document verifications: 2
│
THROUGHOUT DAY
├── Processes leave applications
│   ├── View request details
│   ├── Check leave balance
│   ├── Approve/Reject with comments
│
├── Manages employee records
│   ├── Updates employee information
│   ├── Uploads documents
│
├── Generates reports
│   ├── Monthly attendance summary
│   ├── Leave utilization report
│
MONTHLY
├── Processes payroll
│   ├── Reviews salary components
│   ├── Approves salary slips
│   ├── Generates bank files
│
├── Tracks recruitment
│   ├── Reviews applications
│   ├── Schedules interviews
```

### Accounts Staff Journey Map

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           TYPICAL ACCOUNTS DAY                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

MORNING (9:00 AM)
├── Opens Dashboard
├── Reviews collection summary
│   ├── Yesterday's collection: ₹5,25,000
│   ├── Today's expected: ₹8,00,000
│   └── Overdue amounts: ₹12,50,000
│
FEE COLLECTION WINDOW (10 AM - 4 PM)
├── Records fee payments
│   ├── Student walks in
│   ├── Searches by ID/Name
│   ├── Shows pending fees
│   ├── Records payment (Cash/Cheque/Online)
│   ├── Prints receipt
│
├── Handles queries
│   ├── Fee breakup explanations
│   ├── Payment history
│   ├── Scholarship adjustments
│
END OF DAY
├── Runs daily collection report
├── Bank reconciliation
├── Closes cash register
│
MONTHLY
├── Generates demand statements
├── Sends fee reminders
├── Reviews outstanding dues
├── Prepares financial reports
```

---

## 6. Design Requirements

### Platform Requirements

| Aspect | Requirement |
|--------|-------------|
| Mobile Web | Required - Primary for students |
| Desktop Web | Required - Primary for staff |
| PWA | Required - Installable, offline support |
| Native Apps | Not required - PWA covers needs |

### Browser Support

- Chrome 90+ (primary)
- Safari 14+ (iOS users)
- Firefox 90+
- Edge 90+

### Screen Sizes to Design For

```
MOBILE (Primary for Students)
├── Small: 320px - 375px (iPhone SE, older Androids)
├── Medium: 376px - 414px (iPhone 12/13/14, most Androids)
└── Large: 415px - 480px (iPhone Plus/Max)

TABLET
├── Portrait: 768px - 834px
└── Landscape: 1024px - 1194px

DESKTOP (Primary for Staff)
├── Standard: 1280px - 1440px
├── Wide: 1441px - 1920px
└── Ultra-wide: 1921px+ (optional)
```

### Accessibility Requirements

- **WCAG 2.1 AA Compliance**
- Color contrast ratio: minimum 4.5:1
- Touch targets: minimum 44px × 44px
- Keyboard navigation support
- Screen reader compatible
- Focus indicators visible
- No color-only information

### Performance Requirements

- First Contentful Paint: < 1.5s on 4G
- Time to Interactive: < 3s on 4G
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1

---

## 7. Design Language Guidance

### Visual Direction

| Aspect | Direction |
|--------|-----------|
| Style | Clean, minimal, modern |
| Feel | Professional but friendly |
| Imagery | Illustrations preferred over photos |
| Icons | Line icons, consistent style |
| Spacing | Generous whitespace |
| Typography | Clear hierarchy, readable |

### Color Psychology

| Usage | Color Direction |
|-------|-----------------|
| Primary | Blue family (trust, education) |
| Success | Green (positive actions) |
| Warning | Amber/Yellow (caution) |
| Error | Red (attention needed) |
| Neutral | Gray scale (backgrounds, text) |
| Accent | Institution's brand color |

### Information Density

```
STUDENTS (Low Density)
├── Large touch targets
├── One primary action per screen
├── Minimal text
├── Visual hierarchy through size
└── Bottom navigation

HR/ACCOUNTS (Higher Density)
├── Data tables with multiple columns
├── Multiple actions available
├── Sidebar navigation
├── Dense but organized information
└── Power user features
```

---

## 8. Feature Priority Matrix

### Must Have (MVP)

| Module | Features |
|--------|----------|
| **Student** | Dashboard, Timetable, Attendance view, Fee payment, Results |
| **Faculty** | Dashboard, Attendance marking, Grade entry, Leave application |
| **HR** | Employee list, Leave management, Basic payroll |
| **Accounts** | Fee collection, Payment entry, Basic reports |
| **All** | Login, Profile, Notifications, Password reset |

### Should Have (v1.1)

| Module | Features |
|--------|----------|
| **Student** | Library, Grievances, Detailed attendance |
| **Faculty** | Course materials, Mentoring, Research |
| **HR** | Recruitment, Training, Advanced reports |
| **Accounts** | Budgeting, Advanced reconciliation |

### Nice to Have (v2.0)

| Module | Features |
|--------|----------|
| **Student** | Hostel, Transport, Placement |
| **Faculty** | Research funding, Publications |
| **HR** | Performance management |
| **Accounts** | Asset management |

---

## 9. Deliverables Expected

### From UI/UX Team

1. **Design System**
   - Color palette
   - Typography scale
   - Spacing system
   - Component library (buttons, inputs, cards, etc.)
   - Icon set

2. **Wireframes**
   - Low-fidelity for all screens
   - Mobile and desktop versions

3. **High-Fidelity Mockups**
   - All major screens
   - All states (empty, loading, error, success)
   - Responsive versions

4. **Prototypes**
   - Interactive prototypes for key flows
   - User testing materials

5. **Documentation**
   - Component usage guidelines
   - Interaction patterns
   - Animation/transition specs

---

## 10. Reference Applications

### Similar Apps to Study

| App | What to Learn |
|-----|---------------|
| **Google Classroom** | Simple student interface, material organization |
| **Notion** | Clean design, flexible layouts |
| **Linear** | Modern SaaS design patterns |
| **Figma** | Workspace organization |
| **Zoho Books** | Indian accounting interface |
| **Razorpay Dashboard** | Payment interface patterns |
| **CRED** | Premium mobile experience |
| **Jupiter/Fi** | Modern Indian fintech |

### Patterns to Consider

- **Bottom Navigation** for mobile student app
- **Sidebar Navigation** for desktop staff apps
- **Card-based Dashboards** for overviews
- **Data Tables** for list views
- **Slide-over Panels** for quick edits
- **Modal Dialogs** for confirmations
- **Toast Notifications** for feedback
- **Pull-to-Refresh** for mobile

---

## 11. Next Steps

1. **Read** the remaining specification documents:
   - [03_USER_PERSONAS.md](./03_USER_PERSONAS.md)
   - [04_STUDENT_MODULE.md](./04_STUDENT_MODULE.md)
   - [05_FACULTY_MODULE.md](./05_FACULTY_MODULE.md)
   - [06_HR_MODULE.md](./06_HR_MODULE.md)
   - [07_ACCOUNTS_MODULE.md](./07_ACCOUNTS_MODULE.md)
   - [08_ADMIN_MODULE.md](./08_ADMIN_MODULE.md)
   - [09_DESIGN_SYSTEM.md](./09_DESIGN_SYSTEM.md)

2. **Understand** the user personas and their needs

3. **Begin** with the Design System foundation

4. **Start** wireframes for Student Module (highest priority)

5. **Review** with stakeholders before high-fidelity

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Audience**: UI/UX Design Team
