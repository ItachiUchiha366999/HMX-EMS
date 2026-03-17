# HR Module - UI/UX Specification

## Module Overview

The HR Module serves ~10 HR staff members and is used for **employee management**, **leave processing**, **payroll**, and **attendance tracking**. This is a **desktop-primary** interface with high information density.

---

## 1. Module Structure

```
HR MODULE
│
├── 📊 Dashboard
│   ├── Key Metrics
│   ├── Pending Tasks
│   ├── Quick Actions
│   └── Recent Activity
│
├── 👥 Employees
│   ├── Employee List
│   ├── Employee Profile
│   ├── Add New Employee
│   └── Bulk Import
│
├── 📋 Leave Management
│   ├── Leave Requests (Inbox)
│   ├── Leave Calendar
│   ├── Leave Balance Report
│   └── Leave Policies
│
├── 🕐 Attendance
│   ├── Daily Attendance
│   ├── Attendance Reports
│   ├── Regularization Requests
│   └── Shift Management
│
├── 💰 Payroll
│   ├── Process Payroll
│   ├── Salary Slips
│   ├── Salary Structure
│   ├── Payroll Reports
│   └── Bank File Generation
│
├── 💼 Recruitment (Optional)
│   ├── Job Openings
│   ├── Applications
│   └── Interview Schedule
│
├── 📑 Documents
│   ├── Employee Documents
│   └── HR Policies
│
└── 📊 Reports
    ├── Employee Reports
    ├── Leave Reports
    ├── Attendance Reports
    └── Payroll Reports
```

---

## 2. Screen Specifications

### 2.1 HR Dashboard

**Purpose**: Overview of HR operations and pending tasks

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ≡  University ERP                                            🔔 (5)  Meera Gupta  👤  ▼  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────┐  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │             │  │                                                                        │ │
│  │  [Logo]     │  │  Good Morning, Meera! 👋                     Friday, 17 January 2026 │ │
│  │             │  │                                                                        │ │
│  │  ─────────  │  ├───────────────────────────────────────────────────────────────────────┤ │
│  │             │  │                                                                        │ │
│  │  📊 Dashboard│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────┐│ │
│  │             │  │  │  👥 EMPLOYEES  │  │  📋 PENDING   │  │  🕐 PRESENT   │  │ 💰 PAYROL││ │
│  │  👥 Employees│  │  │               │  │    LEAVES     │  │    TODAY      │  │   STATUS ││ │
│  │             │  │  │     145       │  │               │  │               │  │         ││ │
│  │  📋 Leave   │  │  │               │  │      8        │  │   138/145     │  │  Pending ││ │
│  │             │  │  │  Active Staff │  │               │  │               │  │  (Jan)  ││ │
│  │  🕐 Attendan │  │  │  +2 this month│  │  ⚠️ Action    │  │     95%       │  │         ││ │
│  │             │  │  │               │  │    Required   │  │               │  │         ││ │
│  │  💰 Payroll │  │  └───────────────┘  └───────────────┘  └───────────────┘  └─────────┘│ │
│  │             │  │                                                                        │ │
│  │  💼 Recruit │  │  ┌─────────────────────────────────┐  ┌─────────────────────────────┐ │ │
│  │             │  │  │  ⏳ PENDING TASKS               │  │  ⚡ QUICK ACTIONS            │ │ │
│  │  📑 Document│  │  │                                 │  │                             │ │ │
│  │             │  │  │  ┌─────────────────────────────┐│  │  [+ Add Employee]           │ │ │
│  │  📊 Reports │  │  │  │ 📋 Leave Requests       8   ││  │                             │ │ │
│  │             │  │  │  │ 💰 Expense Claims       3   ││  │  [📋 Process Leave]         │ │ │
│  │  ─────────  │  │  │  │ 📄 Document Requests    2   ││  │                             │ │ │
│  │             │  │  │  │ 🕐 Regularization       5   ││  │  [💰 Run Payroll]           │ │ │
│  │  ⚙️ Settings │  │  │  │ ✅ Onboarding Tasks    1   ││  │                             │ │ │
│  │             │  │  │  └─────────────────────────────┘│  │  [📊 Generate Report]       │ │ │
│  │  🚪 Logout  │  │  │                                 │  │                             │ │ │
│  │             │  │  │  Total: 19 pending              │  │                             │ │ │
│  │             │  │  └─────────────────────────────────┘  └─────────────────────────────┘ │ │
│  │             │  │                                                                        │ │
│  │             │  │  ┌───────────────────────────────────────────────────────────────────┐│ │
│  │             │  │  │  📅 LEAVE CALENDAR (This Week)                                    ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  │  Mon 13 │ Tue 14 │ Wed 15 │ Thu 16 │ Fri 17 │ Sat 18 │ Sun 19   ││ │
│  │             │  │  │  ───────┼────────┼────────┼────────┼────────┼────────┼─────────  ││ │
│  │             │  │  │  2      │ 1      │ 3      │ 2      │ 4      │ -      │ -        ││ │
│  │             │  │  │  on     │ on     │ on     │ on     │ on     │        │          ││ │
│  │             │  │  │  leave  │ leave  │ leave  │ leave  │ leave  │        │          ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  │  [View Full Calendar]                                             ││ │
│  │             │  │  └───────────────────────────────────────────────────────────────────┘│ │
│  │             │  │                                                                        │ │
│  │             │  │  ┌───────────────────────────────────────────────────────────────────┐│ │
│  │             │  │  │  🕐 RECENT ACTIVITY                                               ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  │  10:30  Leave approved for Dr. Kumar (17-18 Jan)                  ││ │
│  │             │  │  │  10:15  New employee onboarded: Ravi Sharma                       ││ │
│  │             │  │  │  09:45  Salary slip generated for December 2025                   ││ │
│  │             │  │  │  09:30  Regularization request from Priya Nair                    ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  └───────────────────────────────────────────────────────────────────┘│ │
│  └─────────────┘  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Employee List Screen

**Purpose**: View and manage all employees

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Employees                                              [+ Add Employee]  [Import CSV]  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  🔍 Search employees...                    │  Department: [All ▼]  │  Status: [Active▼]│ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Showing 145 employees                                              Export ▼  │ ≡ List │ │
│  ├───────────────────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                                        │ │
│  │  □  │ Employee ID │ Name              │ Department    │ Designation      │ Status │ ⋮ │ │
│  │  ───┼─────────────┼───────────────────┼───────────────┼──────────────────┼────────┼───│ │
│  │  □  │ EMP-001     │ Dr. Ananya K      │ Computer Sci  │ Asst Professor   │ Active │ ⋮ │ │
│  │  □  │ EMP-002     │ Prof. R.K. Sharma │ Mechanical    │ Professor & HOD  │ Active │ ⋮ │ │
│  │  □  │ EMP-003     │ Dr. Suresh Kumar  │ Electronics   │ Assoc Professor  │ Active │ ⋮ │ │
│  │  □  │ EMP-004     │ Ms. Priya Nair    │ Computer Sci  │ Asst Professor   │ Active │ ⋮ │ │
│  │  □  │ EMP-005     │ Mr. Amit Singh    │ Admin         │ Office Asst      │ Active │ ⋮ │ │
│  │  □  │ EMP-006     │ Ms. Sunita Verma  │ Accounts      │ Accountant       │ Active │ ⋮ │ │
│  │  □  │ EMP-007     │ Dr. Rahul Mehta   │ Civil         │ Asst Professor   │ Leave  │ ⋮ │ │
│  │  □  │ EMP-008     │ Mr. Vijay Kumar   │ IT            │ System Admin     │ Active │ ⋮ │ │
│  │  □  │ EMP-009     │ Ms. Anjali Gupta  │ HR            │ HR Executive     │ Active │ ⋮ │ │
│  │  □  │ EMP-010     │ Dr. Meena Sharma  │ Mathematics   │ Asst Professor   │ Active │ ⋮ │ │
│  │  ...│ ...         │ ...               │ ...           │ ...              │ ...    │ ⋮ │ │
│  │                                                                                        │ │
│  ├───────────────────────────────────────────────────────────────────────────────────────┤ │
│  │  ◀ Previous    Page 1 of 15    Next ▶                  Showing 1-10 of 145            │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Row Actions (⋮ menu)**:
- View Profile
- Edit Employee
- View Documents
- Leave Balance
- Payslips
- Deactivate

---

### 2.3 Employee Profile Screen

**Purpose**: View and edit complete employee information

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Dr. Ananya Krishnamurthy                                              [Edit]  [More ▼] │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  [Overview]    [Personal]    [Employment]    [Salary]    [Leave]    [Documents]        ││
│  │       ▼                                                                                 ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────────────────────┐  │
│  │                                 │  │  BASIC INFORMATION                              │  │
│  │         ┌───────────┐           │  │                                                 │  │
│  │        │   [Photo] │           │  │  Employee ID:    EMP-001                        │  │
│  │         └───────────┘           │  │  Full Name:      Dr. Ananya Krishnamurthy      │  │
│  │                                 │  │  Email:          ananya.k@university.edu       │  │
│  │  Dr. Ananya Krishnamurthy       │  │  Phone:          +91 98765 43210               │  │
│  │  Assistant Professor            │  │  Date of Birth:  15 March 1992                 │  │
│  │  Computer Science               │  │  Gender:         Female                        │  │
│  │                                 │  │  Blood Group:    O+                            │  │
│  │  📧 ananya.k@university.edu     │  │                                                 │  │
│  │  📱 +91 98765 43210             │  └─────────────────────────────────────────────────┘  │
│  │                                 │                                                       │
│  │  Status: Active ✓               │  ┌─────────────────────────────────────────────────┐  │
│  │  Joined: 15 July 2020           │  │  EMPLOYMENT DETAILS                             │  │
│  │                                 │  │                                                 │  │
│  └─────────────────────────────────┘  │  Department:     Computer Science               │  │
│                                       │  Designation:    Assistant Professor            │  │
│  ┌─────────────────────────────────┐  │  Employment Type: Permanent                     │  │
│  │  QUICK STATS                    │  │  Reporting To:   Prof. R.K. Sharma (HOD)       │  │
│  │                                 │  │  Date of Joining: 15 July 2020                 │  │
│  │  Leave Balance                  │  │  Experience:     5 years 6 months              │  │
│  │  ├ Casual: 8/12                 │  │                                                 │  │
│  │  ├ Sick: 10/10                  │  └─────────────────────────────────────────────────┘  │
│  │  └ Earned: 5/15                 │                                                       │
│  │                                 │  ┌─────────────────────────────────────────────────┐  │
│  │  Attendance (This Month)        │  │  SALARY INFORMATION                             │  │
│  │  Present: 15  │  Absent: 1      │  │                                                 │  │
│  │  Leave: 1     │  Holiday: 3     │  │  Gross Salary:   ₹85,000 / month               │  │
│  │                                 │  │  Net Salary:     ₹70,900 / month               │  │
│  │  Last Payslip: Dec 2025         │  │  Bank Account:   XXXX XXXX 1234                │  │
│  │  [View Payslip]                 │  │  PAN:            AAAAA1234A                    │  │
│  │                                 │  │                                                 │  │
│  └─────────────────────────────────┘  │  [View Salary Structure]  [View Payslips]      │  │
│                                       └─────────────────────────────────────────────────┘  │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.4 Leave Requests Inbox

**Purpose**: Process pending leave applications

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Leave Requests                                                        Filter ▼  Refresh │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  [Pending (8)]    [Approved]    [Rejected]    [All]                                   │ │
│  │       ▼                                                                                │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌────────────────────────────────────────────┐  ┌────────────────────────────────────────┐│
│  │  LEAVE REQUESTS                            │  │  REQUEST DETAILS                       ││
│  │                                            │  │                                        ││
│  │  ┌────────────────────────────────────────┐│  │  Dr. Rahul Mehta                      ││
│  │  │  ▸ Dr. Rahul Mehta                    ││  │  Assistant Professor, Civil            ││
│  │  │    Casual Leave • 20-21 Jan • 2 days  ││  │                                        ││
│  │  │    Applied: 15 Jan 2026               ││  │  ─────────────────────────────────────  ││
│  │  └────────────────────────────────────────┘│  │                                        ││
│  │                                            │  │  Leave Type:    Casual Leave          ││
│  │  ┌────────────────────────────────────────┐│  │  From:          20 January 2026       ││
│  │  │  Prof. Sharma                          ││  │  To:            21 January 2026       ││
│  │  │  Earned Leave • 25-31 Jan • 7 days    ││  │  Duration:      2 days                ││
│  │  │  Applied: 14 Jan 2026                 ││  │  Half Day:      No                    ││
│  │  └────────────────────────────────────────┘│  │                                        ││
│  │                                            │  │  ─────────────────────────────────────  ││
│  │  ┌────────────────────────────────────────┐│  │                                        ││
│  │  │  Ms. Priya Nair                        ││  │  REASON                               ││
│  │  │    Sick Leave • 18 Jan • 1 day        ││  │  Personal work - family function      ││
│  │  │    Applied: 17 Jan 2026               ││  │                                        ││
│  │  └────────────────────────────────────────┘│  │  ─────────────────────────────────────  ││
│  │                                            │  │                                        ││
│  │  ┌────────────────────────────────────────┐│  │  LEAVE BALANCE                        ││
│  │  │  Mr. Amit Singh                        ││  │  Casual: 6 available (after this: 4) ││
│  │  │    Casual Leave • 22 Jan • 1 day      ││  │  Sick: 10 available                   ││
│  │  │    Applied: 16 Jan 2026               ││  │  Earned: 12 available                 ││
│  │  └────────────────────────────────────────┘│  │                                        ││
│  │                                            │  │  ─────────────────────────────────────  ││
│  │  ┌────────────────────────────────────────┐│  │                                        ││
│  │  │  Dr. Meena Sharma                      ││  │  TEAM CALENDAR (20-21 Jan)            ││
│  │  │    Casual Leave • 23-24 Jan • 2 days  ││  │  ┌─────────────────────────────────┐  ││
│  │  │    Applied: 15 Jan 2026               ││  │  │  No other leaves in Civil Dept │  ││
│  │  └────────────────────────────────────────┘│  │  │  during this period             │  ││
│  │                                            │  │  └─────────────────────────────────┘  ││
│  │  ... (4 more)                              │  │                                        ││
│  │                                            │  │  ─────────────────────────────────────  ││
│  └────────────────────────────────────────────┘  │                                        ││
│                                                  │  COMMENTS (Optional)                   ││
│                                                  │  ┌─────────────────────────────────┐  ││
│                                                  │  │                                 │  ││
│                                                  │  │                                 │  ││
│                                                  │  └─────────────────────────────────┘  ││
│                                                  │                                        ││
│                                                  │  ┌───────────────┐  ┌───────────────┐ ││
│                                                  │  │   ✗ REJECT    │  │  ✓ APPROVE    │ ││
│                                                  │  └───────────────┘  └───────────────┘ ││
│                                                  │                                        ││
│                                                  └────────────────────────────────────────┘│
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key Features**:
- Master-detail layout
- One-click approve/reject
- Shows leave balance before approval
- Team calendar to check conflicts
- Batch processing for multiple requests

---

### 2.5 Leave Calendar

**Purpose**: Visual overview of leaves across organization

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Leave Calendar                                   ◀ January 2026 ▶    Department: [All▼]│
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │       │ Mon    │ Tue    │ Wed    │ Thu    │ Fri    │ Sat    │ Sun    │               │ │
│  │       │   13   │   14   │   15   │   16   │   17   │   18   │   19   │               │ │
│  │  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤               │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  CSE  │ AK     │        │        │ SN     │ SN     │        │        │  AK: Ananya K │ │
│  │       │        │        │        │        │        │        │        │  SN: Sunil N  │ │
│  │  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤               │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  MECH │        │ RS     │ RS     │        │        │        │        │  RS: R. Sharma│ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤               │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  ECE  │        │        │ PG     │ PG     │ PG     │        │        │  PG: P. Gupta │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤               │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  CIVIL│        │        │        │        │ RM     │ RM     │        │  RM: R. Mehta │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  ─────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤               │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  │  ADMIN│ AS     │ AS     │        │        │        │        │        │  AS: A. Singh │ │
│  │       │        │        │        │        │        │        │        │               │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  Legend:  ▪ Casual Leave   ▪ Sick Leave   ▪ Earned Leave   ▪ Pending                       │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.6 Payroll Processing Screen

**Purpose**: Process monthly payroll

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Payroll Processing                                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  PAYROLL PERIOD                                                                        │ │
│  │                                                                                        │ │
│  │  Month: [January 2026 ▼]    Status: ⏳ Processing                    [Start Payroll]  │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  PAYROLL SUMMARY                                                                       │ │
│  │                                                                                        │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │ │
│  │  │  EMPLOYEES    │  │  GROSS        │  │  DEDUCTIONS   │  │  NET          │          │ │
│  │  │     145       │  │  ₹98,45,000   │  │  ₹18,52,000   │  │  ₹79,93,000   │          │ │
│  │  │               │  │               │  │               │  │               │          │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘          │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  PROCESSING STEPS                                                                      │ │
│  │                                                                                        │ │
│  │  ✓ Step 1: Attendance Pulled                      Completed                           │ │
│  │  ✓ Step 2: Leave Deductions Calculated            Completed                           │ │
│  │  ✓ Step 3: Salary Components Computed             Completed                           │ │
│  │  ⏳ Step 4: Tax Calculations                       In Progress...                      │ │
│  │  ○ Step 5: Salary Slips Generated                 Pending                             │ │
│  │  ○ Step 6: Bank File Ready                        Pending                             │ │
│  │                                                                                        │ │
│  │  ████████████████████░░░░░░░░░░  60%                                                  │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  SALARY SLIPS                                                           Filter ▼       │ │
│  │                                                                                        │ │
│  │  □  │ Employee      │ Department │ Gross      │ Deductions │ Net        │ Status     │ │
│  │  ───┼───────────────┼────────────┼────────────┼────────────┼────────────┼────────────│ │
│  │  □  │ Dr. Ananya K  │ CSE        │ ₹85,000    │ ₹14,100    │ ₹70,900    │ ✓ Ready    │ │
│  │  □  │ Prof. Sharma  │ MECH       │ ₹1,25,000  │ ₹25,000    │ ₹1,00,000  │ ✓ Ready    │ │
│  │  □  │ Dr. Kumar     │ ECE        │ ₹95,000    │ ₹18,000    │ ₹77,000    │ ⏳ Process │ │
│  │  ... │               │            │            │            │            │            │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  [Download All Slips]    [Generate Bank File]    [Email Slips]    [Submit for Approval]│ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.7 Daily Attendance Screen

**Purpose**: View and manage daily attendance

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Daily Attendance                                               Date: 17 January 2026   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  ATTENDANCE SUMMARY                                                                    │ │
│  │                                                                                        │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │ │
│  │  │  ✓ PRESENT    │  │  ✗ ABSENT     │  │  📋 ON LEAVE  │  │  🏠 WFH       │          │ │
│  │  │     128       │  │      5        │  │      7        │  │      5        │          │ │
│  │  │     88%       │  │     3%        │  │     5%        │  │     4%        │          │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘          │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Search: [_______________]  │  Department: [All▼]  │  Status: [All▼]  │  [Export]    │ │
│  ├───────────────────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                                        │ │
│  │  Employee         │ Department │ Check In  │ Check Out │ Hours   │ Status  │ Actions │ │
│  │  ─────────────────┼────────────┼───────────┼───────────┼─────────┼─────────┼─────────│ │
│  │  Dr. Ananya K     │ CSE        │ 08:45 AM  │ -         │ 5h 15m  │ Present │ [⋮]     │ │
│  │  Prof. Sharma     │ MECH       │ 09:00 AM  │ -         │ 5h 00m  │ Present │ [⋮]     │ │
│  │  Dr. Kumar        │ ECE        │ -         │ -         │ -       │ Absent  │ [⋮]     │ │
│  │  Ms. Priya Nair   │ CSE        │ -         │ -         │ -       │ Leave   │ [⋮]     │ │
│  │  Mr. Amit Singh   │ Admin      │ 08:30 AM  │ -         │ 5h 30m  │ Present │ [⋮]     │ │
│  │  Ms. Sunita Verma │ Accounts   │ 09:15 AM  │ -         │ 4h 45m  │ Present │ [⋮]     │ │
│  │  Dr. Rahul Mehta  │ Civil      │ -         │ -         │ -       │ Leave   │ [⋮]     │ │
│  │  ... (more rows)                                                                       │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Navigation Structure

### Desktop Sidebar

```
┌─────────────────┐
│  [Logo]         │
│                 │
│  ─────────────  │
│                 │
│  📊 Dashboard   │
│                 │
│  👥 Employees   │
│    ├ All Emp    │
│    ├ Add New    │
│    └ Org Chart  │
│                 │
│  📋 Leave       │
│    ├ Requests   │
│    ├ Calendar   │
│    ├ Balance    │
│    └ Policies   │
│                 │
│  🕐 Attendance  │
│    ├ Daily      │
│    ├ Reports    │
│    ├ Regularize │
│    └ Shifts     │
│                 │
│  💰 Payroll     │
│    ├ Process    │
│    ├ Slips      │
│    ├ Structure  │
│    └ Reports    │
│                 │
│  💼 Recruitment │
│    ├ Openings   │
│    ├ Applicants │
│    └ Interviews │
│                 │
│  📑 Documents   │
│                 │
│  📊 Reports     │
│                 │
│  ─────────────  │
│                 │
│  ⚙️ Settings    │
│  🚪 Logout      │
│                 │
└─────────────────┘
```

---

## 4. Key Workflows

### Workflow 1: Process Leave Request

```
1. HR sees pending leave count on dashboard
2. Clicks "Leave Requests" or pending count
3. List shows all pending requests
4. Clicks on a request to see details
5. Reviews:
   - Employee leave balance
   - Team calendar for conflicts
   - Reason for leave
6. Adds optional comment
7. Clicks Approve or Reject
8. System notifies employee
9. Moves to next request
```

### Workflow 2: Monthly Payroll

```
1. HR navigates to Payroll > Process
2. Selects month (January 2026)
3. Clicks "Start Payroll"
4. System auto-processes:
   - Pulls attendance
   - Calculates deductions
   - Computes salary
   - Generates slips
5. HR reviews summary
6. Checks for any exceptions
7. Generates bank file
8. Submits for approval
9. After approval, emails slips
```

### Workflow 3: New Employee Onboarding

```
1. HR clicks "Add Employee"
2. Fills basic information form
3. Uploads documents
4. Sets up salary structure
5. Creates user account
6. Assigns roles
7. Sends welcome email
8. Employee appears in list
```

---

## 5. Component Specifications

### Task Counter Badge

```
┌───────────────────────┐
│  📋 Leave Requests    │
│                       │
│         8             │  <- Large number
│                       │
│    ⚠️ Action Required │
└───────────────────────┘
```

### Employee Row

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  [Photo] │ EMP-001 │ Dr. Ananya K │ Computer Sci │ Asst Professor │ Active │ [⋮]      │
└─────────────────────────────────────────────────────────────────────────────────────────┘

States:
- Active: Normal
- On Leave: Muted with badge
- Inactive: Grayed out
```

### Leave Request Card

```
┌─────────────────────────────────────┐
│  Dr. Rahul Mehta                    │
│  Casual Leave • 20-21 Jan • 2 days  │
│  Applied: 15 Jan 2026               │
└─────────────────────────────────────┘

Selected state: Blue border, light blue background
```

### Approval Buttons

```
┌─────────────────────────────────────────┐
│  ┌───────────────┐  ┌───────────────┐  │
│  │   ✗ REJECT    │  │  ✓ APPROVE    │  │
│  │   (Gray/Red)  │  │   (Green)     │  │
│  └───────────────┘  └───────────────┘  │
└─────────────────────────────────────────┘
```

---

## 6. Data Tables

### Standard Table Features

- Sortable columns (click header)
- Filterable (dropdown/search)
- Resizable columns
- Row selection (checkbox)
- Bulk actions
- Pagination
- Export (CSV, Excel, PDF)
- Column visibility toggle

### Table Toolbar

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│  🔍 Search...  │  Filter: [Department▼] [Status▼]  │  [Export▼]  │  [Columns]  │  ≡  │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Form Patterns

### Add Employee Form (Multi-step)

```
Step 1: Basic Information
┌─────────────────────────────────────────┐
│  ○ Basic  ○ Employment  ○ Salary  ○ Docs│
│  ────▲────────────────────────────────  │
│                                         │
│  First Name *     [________________]    │
│  Last Name *      [________________]    │
│  Email *          [________________]    │
│  Phone *          [________________]    │
│  Date of Birth    [_______________]📅   │
│  Gender           [Male ▼]              │
│                                         │
│           [Next →]                      │
└─────────────────────────────────────────┘
```

---

## 8. Accessibility Considerations

| Requirement | Implementation |
|-------------|----------------|
| Keyboard Navigation | Full table navigation |
| Screen Reader | ARIA labels for status |
| High Contrast | Status indicators |
| Focus Management | Trap in modals |
| Shortcuts | Approve (A), Reject (R) |

---

## 9. Print Layouts

### Salary Slip Print

- A4 portrait
- Company letterhead
- Employee details
- Earnings/Deductions table
- Bank details
- Digital signature area

### Leave Report Print

- A4 landscape
- Month/period header
- Employee-wise leave summary
- Department totals
- Signatures section

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Module Priority**: P1 (High)
**Primary Device**: Desktop (95%)
