# Admin Module - UI/UX Specification

## Module Overview

The Admin Module serves ~5 system administrators for **system configuration**, **user management**, **academic setup**, and **reporting**. This is a **desktop-only** interface with advanced configuration options.

---

## 1. Module Structure

```
ADMIN MODULE
│
├── 📊 System Dashboard
│   ├── System Health
│   ├── Usage Statistics
│   ├── Active Users
│   └── Alerts
│
├── 👥 User Management
│   ├── Users List
│   ├── Add User
│   ├── Bulk Import
│   └── User Activity
│
├── 🔐 Roles & Permissions
│   ├── Roles List
│   ├── Permission Matrix
│   └── Role Assignment
│
├── 🎓 Academic Setup
│   ├── Programs
│   ├── Courses
│   ├── Batches
│   ├── Sections
│   ├── Academic Year
│   └── Academic Calendar
│
├── 📝 Examination Setup
│   ├── Exam Types
│   ├── Grade Scale
│   ├── Assessment Plans
│   └── Exam Schedule
│
├── 🏢 Institution Setup
│   ├── Departments
│   ├── Designations
│   ├── Rooms/Halls
│   └── Shifts
│
├── 📊 Reports
│   ├── Academic Reports
│   ├── Financial Reports
│   ├── HR Reports
│   └── Custom Reports
│
├── 📋 Audit Logs
│   ├── User Activity
│   ├── Data Changes
│   └── Login History
│
└── ⚙️ System Settings
    ├── General Settings
    ├── Email Configuration
    ├── SMS Configuration
    ├── Payment Gateway
    ├── Backup Settings
    └── Module Configuration
```

---

## 2. Screen Specifications

### 2.1 System Dashboard

**Purpose**: Overview of system health and key metrics

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ≡  University ERP - Admin                                   🔔 (1)  Vikram Singh  👤  ▼  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────┐  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │             │  │                                                                        │ │
│  │  [Logo]     │  │  Admin Dashboard                                 17 January 2026      │ │
│  │             │  │                                                                        │ │
│  │  ─────────  │  ├───────────────────────────────────────────────────────────────────────┤ │
│  │             │  │                                                                        │ │
│  │  📊 Dashboard│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────┐│ │
│  │             │  │  │  ✅ SYSTEM     │  │  👥 TOTAL     │  │  🟢 ACTIVE    │  │⚠️ ALERTS││ │
│  │  👥 Users   │  │  │    STATUS     │  │    USERS      │  │    NOW        │  │         ││ │
│  │             │  │  │               │  │               │  │               │  │         ││ │
│  │  🔐 Roles   │  │  │   Healthy     │  │    2,350      │  │     145       │  │    3    ││ │
│  │             │  │  │               │  │               │  │               │  │         ││ │
│  │  🎓 Academic│  │  │  Uptime: 99.9%│  │  +23 this week│  │  Peak: 312    │  │         ││ │
│  │             │  │  └───────────────┘  └───────────────┘  └───────────────┘  └─────────┘│ │
│  │  📝 Exams   │  │                                                                        │ │
│  │             │  │  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  🏢 Institut│  │  │  📊 USAGE STATISTICS (Last 7 Days)                                 ││
│  │             │  │  │                                                                     ││
│  │  📊 Reports │  │  │       ┌────────────────────────────────────────────────────────┐   ││
│  │             │  │  │  350  │                                              ▄▄▄        │   ││
│  │  📋 Audit   │  │  │       │                                    ▄▄▄      ███        │   ││
│  │             │  │  │  250  │              ▄▄▄      ▄▄▄  ▄▄▄    ███      ███        │   ││
│  │  ⚙️ Settings │  │  │       │      ▄▄▄    ███      ███  ███    ███      ███        │   ││
│  │             │  │  │  150  │      ███    ███      ███  ███    ███      ███        │   ││
│  │  ─────────  │  │  │       │      ███    ███      ███  ███    ███      ███        │   ││
│  │             │  │  │    0  └──────Mon────Tue──────Wed──Thu────Fri──────Sat──────────┘   ││
│  │  🚪 Logout  │  │  │                                                                     ││
│  │             │  │  │        ▪ Students  ▪ Faculty  ▪ Staff                              ││
│  │             │  │  └─────────────────────────────────────────────────────────────────────┘│
│  │             │  │                                                                        │ │
│  │             │  │  ┌────────────────────────────────┐  ┌────────────────────────────────┐│ │
│  │             │  │  │  ⚠️ ALERTS                     │  │  🕐 RECENT ACTIVITY            ││ │
│  │             │  │  │                                │  │                                ││ │
│  │             │  │  │  • Backup pending (2 days)    │  │  10:30  User created: ravi.k  ││ │
│  │             │  │  │  • SSL cert expires in 15 days│  │  10:15  Role updated: Faculty ││ │
│  │             │  │  │  • Storage at 75% capacity   │  │  09:45  Settings changed       ││ │
│  │             │  │  │                                │  │  09:30  Bulk import: 50 users ││ │
│  │             │  │  │  [View All Alerts]            │  │                                ││ │
│  │             │  │  └────────────────────────────────┘  └────────────────────────────────┘│ │
│  │             │  │                                                                        │ │
│  └─────────────┘  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 User Management

**Purpose**: Manage all system users

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  User Management                                    [+ Add User]  [Import CSV]  [Export]│
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  🔍 Search users...      │ Role: [All ▼]  │ Status: [All ▼]  │ Type: [All ▼]         │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  SUMMARY                                                                               │ │
│  │                                                                                        │ │
│  │  Total: 2,350  │  Students: 2,000  │  Faculty: 70  │  Staff: 150  │  Admins: 5       │ │
│  │                │  Active: 1,950    │  Active: 68   │  Active: 145  │  Active: 5       │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Showing 2,350 users                                                                   │ │
│  ├───────────────────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                                        │ │
│  │  □  │ Email                    │ Full Name         │ Type     │ Roles    │ Status │ ⋮ │ │
│  │  ───┼──────────────────────────┼───────────────────┼──────────┼──────────┼────────┼───│ │
│  │  □  │ rahul.s@university.edu   │ Rahul Sharma      │ Student  │ Student  │ Active │ ⋮ │ │
│  │  □  │ ananya.k@university.edu  │ Dr. Ananya K      │ Employee │ Faculty  │ Active │ ⋮ │ │
│  │  □  │ vikram.s@university.edu  │ Vikram Singh      │ Employee │ Admin    │ Active │ ⋮ │ │
│  │  □  │ priya.v@university.edu   │ Priya Verma       │ Student  │ Student  │ Active │ ⋮ │ │
│  │  □  │ amit.s@university.edu    │ Amit Singh        │ Employee │ Staff    │ Active │ ⋮ │ │
│  │  □  │ meera.g@university.edu   │ Meera Gupta       │ Employee │ HR Staff │ Active │ ⋮ │ │
│  │  □  │ sunita.a@university.edu  │ Sunita Agarwal    │ Employee │ Accounts │ Active │ ⋮ │ │
│  │  □  │ ravi.k@university.edu    │ Ravi Kumar        │ Student  │ Student  │ New    │ ⋮ │ │
│  │  ... │                         │                   │          │          │        │ ⋮ │ │
│  │                                                                                        │ │
│  ├───────────────────────────────────────────────────────────────────────────────────────┤ │
│  │  ◀ Previous    Page 1 of 235    Next ▶                       Showing 1-10 of 2,350   │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Row Actions**:
- View Profile
- Edit User
- Reset Password
- Assign Roles
- View Activity
- Disable/Enable
- Delete

**Add User Form**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Add New User                                                                      [X] Close│
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  USER INFORMATION                                                                           │
│                                                                                              │
│  Email *                               Full Name *                                          │
│  ┌─────────────────────────────┐      ┌─────────────────────────────┐                      │
│  │                             │      │                             │                      │
│  └─────────────────────────────┘      └─────────────────────────────┘                      │
│                                                                                              │
│  User Type *                           Send Welcome Email                                   │
│  ┌─────────────────────────────┐      ☑ Send welcome email with login details              │
│  │  Employee                ▼  │                                                            │
│  └─────────────────────────────┘                                                            │
│                                                                                              │
│  ROLE ASSIGNMENT                                                                            │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  Available Roles                     Assigned Roles                                     ││
│  │                                                                                          ││
│  │  ┌─────────────────────┐  [→]      ┌─────────────────────┐                             ││
│  │  │ □ System Manager    │  [←]      │ ☑ Faculty          │                             ││
│  │  │ □ HR Manager        │           │ ☑ Instructor        │                             ││
│  │  │ □ HR User           │           │                     │                             ││
│  │  │ □ Accounts Manager  │           │                     │                             ││
│  │  │ □ Accounts User     │           │                     │                             ││
│  │  │ □ Academic Admin    │           │                     │                             ││
│  │  │ □ Faculty           │           │                     │                             ││
│  │  │ □ Instructor        │           │                     │                             ││
│  │  │ □ Student           │           │                     │                             ││
│  │  └─────────────────────┘           └─────────────────────┘                             ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  LINK TO RECORD (Optional)                                                                  │
│                                                                                              │
│  Employee *                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  Search employee...                                                                     ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                           [Cancel]              [Create User]                          │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.3 Roles & Permissions

**Purpose**: Configure role-based access control

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Roles & Permissions                                                    [+ Create Role] │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌────────────────────────────────┐  ┌──────────────────────────────────────────────────────┐│
│  │  ROLES                         │  │  PERMISSIONS - Faculty                              ││
│  │                                │  │                                                      ││
│  │  ┌────────────────────────────┐│  │  ┌──────────────────────────────────────────────────┐││
│  │  │  System Manager        12  ││  │  │  DocType / Module        │ Read │Write│Delete│Exp│││
│  │  └────────────────────────────┘│  │  │  ────────────────────────┼──────┼─────┼──────┼───│││
│  │  ┌────────────────────────────┐│  │  │                                                  │││
│  │  │  HR Manager             3  ││  │  │  STUDENT MODULE                                  │││
│  │  └────────────────────────────┘│  │  │  ────────────────────────┼──────┼─────┼──────┼───│││
│  │  ┌────────────────────────────┐│  │  │  Student                 │  ✓   │  -  │  -   │ ✓ │││
│  │  │  HR User                8  ││  │  │  Student Attendance      │  ✓   │  ✓  │  -   │ ✓ │││
│  │  └────────────────────────────┘│  │  │  Student Group           │  ✓   │  -  │  -   │ - │││
│  │  ┌────────────────────────────┐│  │  │                                                  │││
│  │  │  Accounts Manager       2  ││  │  │  COURSE MODULE                                   │││
│  │  └────────────────────────────┘│  │  │  ────────────────────────┼──────┼─────┼──────┼───│││
│  │  ┌────────────────────────────┐│  │  │  Course                  │  ✓   │  -  │  -   │ - │││
│  │  │  Accounts User          5  ││  │  │  Course Schedule         │  ✓   │  ✓  │  -   │ ✓ │││
│  │  └────────────────────────────┘│  │  │  Course Material         │  ✓   │  ✓  │  ✓   │ ✓ │││
│  │  ┌────────────────────────────┐│  │  │                                                  │││
│  │  │▸ Faculty              68  ││  │  │  ASSESSMENT MODULE                               │││
│  │  └────────────────────────────┘│  │  │  ────────────────────────┼──────┼─────┼──────┼───│││
│  │  ┌────────────────────────────┐│  │  │  Assessment Plan         │  ✓   │  -  │  -   │ - │││
│  │  │  Instructor            68  ││  │  │  Assessment Result       │  ✓   │  ✓  │  -   │ ✓ │││
│  │  └────────────────────────────┘│  │  │                                                  │││
│  │  ┌────────────────────────────┐│  │  │  HR MODULE (Self-Service)                       │││
│  │  │  Student            2,000  ││  │  │  ────────────────────────┼──────┼─────┼──────┼───│││
│  │  └────────────────────────────┘│  │  │  Leave Application       │  ✓   │  ✓  │  -   │ - │││
│  │  ┌────────────────────────────┐│  │  │  Attendance (Self)       │  ✓   │  -  │  -   │ - │││
│  │  │  Guardian           1,800  ││  │  │  Salary Slip             │  ✓   │  -  │  -   │ - │││
│  │  └────────────────────────────┘│  │  │                                                  │││
│  │                                │  │  └──────────────────────────────────────────────────┘││
│  │  [+ Create New Role]          │  │                                                      ││
│  │                                │  │  [Edit Role]  [Duplicate]  [Delete]                 ││
│  └────────────────────────────────┘  └──────────────────────────────────────────────────────┘│
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.4 Academic Setup - Programs

**Purpose**: Configure academic programs

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Programs                                                              [+ Add Program]  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  🔍 Search programs...                        │  Department: [All ▼]  │  Status: [All▼]│ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                        │ │
│  │  Program Code │ Program Name                  │ Duration │ Department  │ Students│ ⋮  │ │
│  │  ─────────────┼───────────────────────────────┼──────────┼─────────────┼─────────┼────│ │
│  │  BTECH-CSE    │ B.Tech Computer Science       │ 4 Years  │ CSE         │   480   │ ⋮  │ │
│  │  BTECH-ECE    │ B.Tech Electronics            │ 4 Years  │ ECE         │   360   │ ⋮  │ │
│  │  BTECH-MECH   │ B.Tech Mechanical             │ 4 Years  │ Mechanical  │   240   │ ⋮  │ │
│  │  BTECH-CIVIL  │ B.Tech Civil Engineering      │ 4 Years  │ Civil       │   180   │ ⋮  │ │
│  │  MBA          │ Master of Business Admin      │ 2 Years  │ Management  │   120   │ ⋮  │ │
│  │  MTECH-CSE    │ M.Tech Computer Science       │ 2 Years  │ CSE         │    60   │ ⋮  │ │
│  │  BCOM         │ Bachelor of Commerce          │ 3 Years  │ Commerce    │   300   │ ⋮  │ │
│  │  BCA          │ Bachelor of Computer Apps     │ 3 Years  │ CSE         │   180   │ ⋮  │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Program Detail/Edit**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  B.Tech Computer Science                                                         [Save] │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  [Details]    [Courses]    [Fee Structure]    [Batches]    [Students]                  ││
│  │      ▼                                                                                  ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  PROGRAM DETAILS                                                                            │
│                                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐                  │
│  │  Program Code *                 │  │  Program Name *                 │                  │
│  │  ┌─────────────────────────────┐│  │  ┌─────────────────────────────┐│                  │
│  │  │  BTECH-CSE                  ││  │  │  B.Tech Computer Science    ││                  │
│  │  └─────────────────────────────┘│  │  └─────────────────────────────┘│                  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘                  │
│                                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐                  │
│  │  Department *                   │  │  Duration *                     │                  │
│  │  ┌─────────────────────────────┐│  │  ┌─────────────────────────────┐│                  │
│  │  │  Computer Science        ▼  ││  │  │  4 Years                 ▼  ││                  │
│  │  └─────────────────────────────┘│  │  └─────────────────────────────┘│                  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘                  │
│                                                                                              │
│  SEMESTER CONFIGURATION                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │                                                                                          ││
│  │  Number of Semesters: 8                                                                 ││
│  │                                                                                          ││
│  │  Semester 1  │  Semester 2  │  Semester 3  │  Semester 4                               ││
│  │  Year 1 Odd  │  Year 1 Even │  Year 2 Odd  │  Year 2 Even                              ││
│  │  20 credits  │  22 credits  │  22 credits  │  22 credits                               ││
│  │                                                                                          ││
│  │  Semester 5  │  Semester 6  │  Semester 7  │  Semester 8                               ││
│  │  Year 3 Odd  │  Year 3 Even │  Year 4 Odd  │  Year 4 Even                              ││
│  │  22 credits  │  22 credits  │  18 credits  │  10 credits + Project                     ││
│  │                                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  PROGRAM SETTINGS                                                                           │
│                                                                                              │
│  ☑ Allow lateral entry (3rd semester)                                                      │
│  ☑ Internship required (Sem 6-7)                                                           │
│  ☑ Project work in final year                                                              │
│  ☐ Industry semester allowed                                                                │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.5 Audit Logs

**Purpose**: Track all system activities

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Audit Logs                                                                    [Export] │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  [All Activity]    [Data Changes]    [Login History]    [API Calls]                   │ │
│  │        ▼                                                                               │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Date: [Last 7 days ▼]  │  User: [All ▼]  │  Action: [All ▼]  │  🔍 Search...        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                        │ │
│  │  Timestamp           │ User              │ Action     │ Details                │ IP   │ │
│  │  ────────────────────┼───────────────────┼────────────┼────────────────────────┼──────│ │
│  │  17 Jan 10:30:45    │ vikram.s@...      │ Create     │ User: ravi.k created   │ 192..│ │
│  │  17 Jan 10:15:22    │ vikram.s@...      │ Update     │ Role: Faculty modified │ 192..│ │
│  │  17 Jan 09:45:11    │ meera.g@...       │ Update     │ Employee: EMP-045 upd  │ 192..│ │
│  │  17 Jan 09:30:05    │ vikram.s@...      │ Import     │ 50 students imported   │ 192..│ │
│  │  17 Jan 09:15:33    │ ananya.k@...      │ Create     │ Attendance: 58 entries │ 192..│ │
│  │  17 Jan 09:00:12    │ sunita.a@...      │ Create     │ Payment: ₹45,000       │ 192..│ │
│  │  16 Jan 17:45:22    │ rahul.s@...       │ Login      │ Login successful       │ 103..│ │
│  │  16 Jan 17:30:11    │ system            │ Scheduled  │ Backup completed       │ local│ │
│  │  ... (more rows)                                                                       │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Log Detail Modal**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Audit Log Details                                                                 [X] Close│
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  GENERAL                                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  Timestamp:    17 January 2026, 10:15:22 AM                                            ││
│  │  User:         vikram.s@university.edu                                                 ││
│  │  Action:       Update                                                                   ││
│  │  DocType:      Role                                                                     ││
│  │  Document:     Faculty                                                                  ││
│  │  IP Address:   192.168.1.100                                                            ││
│  │  User Agent:   Chrome 120 on Windows                                                    ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  CHANGES                                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │                                                                                          ││
│  │  Field              │  Old Value                │  New Value                            ││
│  │  ──────────────────┼───────────────────────────┼───────────────────────────────────────││
│  │  permissions[5]     │  {read: 0, write: 0}      │  {read: 1, write: 1}                  ││
│  │  description        │  "Faculty role"           │  "Faculty role with attendance"       ││
│  │                                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.6 System Settings

**Purpose**: Configure system-wide settings

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  System Settings                                                                 [Save] │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  [General]  [Email]  [SMS]  [Payment]  [Backup]  [Security]  [Modules]                 ││
│  │      ▼                                                                                  ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  GENERAL SETTINGS                                                                           │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  INSTITUTION DETAILS                                                                    ││
│  │                                                                                          ││
│  │  Institution Name *               Institution Code                                      ││
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐                      ││
│  │  │  University Name            │  │  UNIV-001                   │                      ││
│  │  └─────────────────────────────┘  └─────────────────────────────┘                      ││
│  │                                                                                          ││
│  │  Address                                                                                ││
│  │  ┌─────────────────────────────────────────────────────────────────────────────────────┐││
│  │  │  123 University Road, City, State - 123456                                          │││
│  │  └─────────────────────────────────────────────────────────────────────────────────────┘││
│  │                                                                                          ││
│  │  Phone                           Email                                                  ││
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐                      ││
│  │  │  +91 1234 567890            │  │  info@university.edu        │                      ││
│  │  └─────────────────────────────┘  └─────────────────────────────┘                      ││
│  │                                                                                          ││
│  │  Logo                                                                                   ││
│  │  ┌────────────────────────────────────────────────┐                                    ││
│  │  │  [Current Logo]    [Upload New]  [Remove]      │                                    ││
│  │  └────────────────────────────────────────────────┘                                    ││
│  │                                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  REGIONAL SETTINGS                                                                      ││
│  │                                                                                          ││
│  │  Timezone                         Date Format                                           ││
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐                      ││
│  │  │  Asia/Kolkata (IST)      ▼  │  │  DD-MM-YYYY               ▼│                      ││
│  │  └─────────────────────────────┘  └─────────────────────────────┘                      ││
│  │                                                                                          ││
│  │  Currency                         Language                                              ││
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐                      ││
│  │  │  INR (₹)                 ▼  │  │  English                  ▼│                      ││
│  │  └─────────────────────────────┘  └─────────────────────────────┘                      ││
│  │                                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  SESSION SETTINGS                                                                       ││
│  │                                                                                          ││
│  │  Session Timeout (minutes)        Max Login Attempts                                    ││
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐                      ││
│  │  │  30                         │  │  5                          │                      ││
│  │  └─────────────────────────────┘  └─────────────────────────────┘                      ││
│  │                                                                                          ││
│  │  ☑ Allow remember me                                                                    ││
│  │  ☑ Force password change on first login                                                ││
│  │  ☑ Enable two-factor authentication (optional)                                         ││
│  │                                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Navigation Structure

### Desktop Sidebar

```
┌─────────────────┐
│  [Logo]         │
│  ADMIN          │
│                 │
│  ─────────────  │
│                 │
│  📊 Dashboard   │
│                 │
│  👥 Users       │
│    ├ All Users  │
│    ├ Add User   │
│    ├ Import     │
│    └ Activity   │
│                 │
│  🔐 Roles       │
│    ├ All Roles  │
│    └ Permissions│
│                 │
│  🎓 Academic    │
│    ├ Programs   │
│    ├ Courses    │
│    ├ Batches    │
│    ├ Sections   │
│    └ Calendar   │
│                 │
│  📝 Exams       │
│    ├ Exam Types │
│    ├ Grade Scale│
│    └ Schedule   │
│                 │
│  🏢 Institution │
│    ├ Departments│
│    ├ Designations│
│    └ Rooms      │
│                 │
│  📊 Reports     │
│                 │
│  📋 Audit Logs  │
│                 │
│  ⚙️ Settings    │
│                 │
│  ─────────────  │
│                 │
│  🚪 Logout      │
│                 │
└─────────────────┘
```

---

## 4. Key Workflows

### Workflow 1: Create New User (Bulk)

```
1. Admin navigates to Users > Import
2. Downloads CSV template
3. Fills template with user data
4. Uploads filled CSV
5. System validates data
6. Shows preview with errors highlighted
7. Admin fixes errors or proceeds
8. Clicks "Import"
9. System creates users
10. Sends welcome emails
11. Shows summary report
```

### Workflow 2: Configure New Academic Year

```
1. Admin navigates to Academic > Academic Year
2. Creates new year (2026-27)
3. Sets start/end dates
4. Configures terms/semesters
5. Copies fee structure from previous year
6. Adjusts fees if needed
7. Creates batches
8. Opens admission/enrollment
9. Notifies relevant staff
```

### Workflow 3: Role Permission Update

```
1. Admin navigates to Roles
2. Selects role to modify
3. Reviews current permissions
4. Checks/unchecks permissions
5. Saves changes
6. System logs the change
7. All users with role see updated access
```

---

## 5. Component Specifications

### Permission Checkbox Matrix

```
┌──────────────────────────────────────────────────────────────────────┐
│  DocType              │ Read │ Write │ Create │ Delete │ Export    │
│  ─────────────────────┼──────┼───────┼────────┼────────┼───────────│
│  Student              │  ☑   │   ☐   │   ☐    │   ☐    │    ☑      │
│  Student Attendance   │  ☑   │   ☑   │   ☑    │   ☐    │    ☑      │
│  Assessment Result    │  ☑   │   ☑   │   ☑    │   ☐    │    ☑      │
└──────────────────────────────────────────────────────────────────────┘
```

### Status Badge

```
Active:   ┌──────────┐
          │ ● Active │  (Green)
          └──────────┘

Inactive: ┌────────────┐
          │ ○ Inactive │  (Gray)
          └────────────┘

New:      ┌───────┐
          │ ★ New │  (Blue)
          └───────┘
```

### Alert Card

```
┌─────────────────────────────────────────┐
│  ⚠️  SSL Certificate Expiring           │
│                                         │
│  Your SSL certificate will expire in   │
│  15 days. Renew now to avoid service   │
│  interruption.                          │
│                                         │
│  [Dismiss]              [Take Action]   │
└─────────────────────────────────────────┘
```

---

## 6. Data Import/Export

### Import Flow

1. **Download Template**
   - CSV with headers
   - Sample data rows
   - Validation rules in comments

2. **Upload File**
   - Drag-drop or file picker
   - Progress indicator
   - File validation

3. **Preview**
   - Table view of data
   - Error highlighting (red rows)
   - Error details on hover
   - Fix inline or re-upload

4. **Import**
   - Progress bar
   - Success/failure count
   - Download error report

### Export Options

- CSV
- Excel (.xlsx)
- PDF (for reports)
- JSON (for backup)

---

## 7. Security Considerations

| Feature | Implementation |
|---------|----------------|
| Password Policy | Min 8 chars, complexity rules |
| Session Timeout | Configurable (default 30 min) |
| Login Attempts | Lockout after 5 failures |
| Audit Trail | All changes logged |
| IP Restriction | Optional whitelist |
| 2FA | Optional TOTP |
| Role Hierarchy | Prevent privilege escalation |

---

## 8. Technical Admin Features

### System Health Indicators

```
┌─────────────────────────────────────────┐
│  SYSTEM HEALTH                          │
│                                         │
│  Database:      ● Connected (12ms)      │
│  Redis Cache:   ● Connected (2ms)       │
│  Background:    ● Running (5 workers)   │
│  Storage:       ⚠ 75% used (Warning)    │
│  Last Backup:   ✓ 2 hours ago           │
└─────────────────────────────────────────┘
```

### Maintenance Mode

```
┌─────────────────────────────────────────┐
│  MAINTENANCE MODE                       │
│                                         │
│  ○ System is operational                │
│  ● Enable maintenance mode              │
│                                         │
│  Message to users:                      │
│  ┌─────────────────────────────────────┐│
│  │  System under maintenance.          ││
│  │  Please try again in 30 minutes.    ││
│  └─────────────────────────────────────┘│
│                                         │
│  [Enable Maintenance]                   │
└─────────────────────────────────────────┘
```

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Module Priority**: P2 (Medium)
**Primary Device**: Desktop Only
