# Faculty Module - UI/UX Specification

## Module Overview

The Faculty Module serves ~70 instructors and professors. Primary tasks are **attendance marking** and **grade entry**. Must work well on both **desktop (60%)** and **mobile (40%)** devices.

---

## 1. Module Structure

```
FACULTY MODULE
│
├── 📊 Dashboard
│   ├── Today's Classes Widget
│   ├── Pending Tasks Widget
│   ├── Quick Stats Widget
│   ├── Notifications Widget
│   └── Quick Actions
│
├── 📚 My Classes
│   ├── Class List
│   ├── Class Details
│   │   ├── Student List
│   │   ├── Attendance
│   │   └── Grades
│   └── Course Materials
│
├── 📋 Attendance
│   ├── Mark Attendance
│   ├── Attendance History
│   └── Reports
│
├── 📝 Grades
│   ├── Enter Grades
│   ├── Grade Summary
│   └── Submit for Approval
│
├── 👥 Mentees
│   ├── Mentee List
│   └── Mentee Details
│
├── 👤 HR Self-Service
│   ├── My Profile
│   ├── Leave Management
│   │   ├── Apply for Leave
│   │   ├── Leave Balance
│   │   └── Leave History
│   ├── Attendance (Self)
│   └── Payslips
│
├── 📖 Research (Optional)
│   ├── Publications
│   ├── Projects
│   └── Funding
│
└── 📢 Notifications
    └── All Notifications
```

---

## 2. Screen Specifications

### 2.1 Dashboard

**Purpose**: Overview of today's work and pending tasks

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ≡  University ERP                                         🔔 (3)  Dr. Ananya K  👤  ▼     │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────┐  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │             │  │                                                                        │ │
│  │  [Logo]     │  │  Good Morning, Dr. Ananya! 👋                                         │ │
│  │             │  │  Assistant Professor, Computer Science                                 │ │
│  │  ─────────  │  │                                                                        │ │
│  │             │  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  📊 Dashboard│  │                                                                        │ │
│  │             │  │  ┌─────────────────────────────────┐  ┌─────────────────────────────┐ │ │
│  │  📚 My Classes│  │  │  📅 TODAY'S CLASSES             │  │  ⏳ PENDING TASKS          │ │ │
│  │             │  │  │                                  │  │                             │ │ │
│  │  📋 Attendance│  │  │  09:00  Data Structures (CSE-A) │  │  ⚠️ 3 attendance pending   │ │ │
│  │             │  │  │         Room 301 • 58 students   │  │  ⚠️ 2 grade entries due    │ │ │
│  │  📝 Grades   │  │  │         [Mark Attendance]       │  │  📝 1 mentee request       │ │ │
│  │             │  │  │                                  │  │                             │ │ │
│  │  👥 Mentees  │  │  │  11:00  DBMS Lab (CSE-B)        │  │  [View All Tasks →]        │ │ │
│  │             │  │  │         Lab 2 • 30 students      │  │                             │ │ │
│  │  ─────────  │  │  │         [Mark Attendance]       │  └─────────────────────────────┘ │ │
│  │             │  │  │                                  │                                  │ │
│  │  👤 HR Self  │  │  │  14:00  Data Structures (CSE-B) │  ┌─────────────────────────────┐ │ │
│  │  Service    │  │  │         Room 205 • 55 students   │  │  📊 QUICK STATS            │ │ │
│  │    ├ Leave  │  │  │         [Mark Attendance]       │  │                             │ │ │
│  │    ├ Attend │  │  │                                  │  │  Classes Today: 3          │ │ │
│  │    └ Payslip│  │  │  16:00  DSA Lab (CSE-A)         │  │  Students: 143             │ │ │
│  │             │  │  │         Lab 1 • 30 students      │  │  Mentees: 5                │ │ │
│  │  📖 Research │  │  │         [Mark Attendance]       │  │  Leave Balance: 8 days     │ │ │
│  │             │  │  │                                  │  │                             │ │ │
│  │  ─────────  │  │  └─────────────────────────────────┘  └─────────────────────────────┘ │ │
│  │             │  │                                                                        │ │
│  │  ⚙️ Settings │  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  🚪 Logout   │  │  │  📢 RECENT NOTIFICATIONS                                         │ │ │
│  │             │  │  │                                                                   │ │ │
│  │             │  │  │  • Grade submission deadline for Mid-Sem: 28 Jan 2026           │ │ │
│  │             │  │  │  • Faculty meeting scheduled for 20 Jan 2026, 4:00 PM           │ │ │
│  │             │  │  │  • New mentee assigned: Rahul Sharma (CSE-A)                    │ │ │
│  │             │  │  │                                                                   │ │ │
│  │             │  │  └─────────────────────────────────────────────────────────────────┘ │ │
│  │             │  │                                                                        │ │
│  └─────────────┘  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ≡  University ERP          🔔 (3)  👤  │
├─────────────────────────────────────────┤
│                                         │
│  Good Morning, Dr. Ananya! 👋           │
│  Assistant Professor, CSE               │
│                                         │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │  📅 TODAY'S CLASSES                 ││
│  │                                     ││
│  │  09:00  Data Structures (CSE-A)     ││
│  │         Room 301 • 58 students      ││
│  │         [Mark Attendance]           ││
│  │                                     ││
│  │  11:00  DBMS Lab (CSE-B)            ││
│  │         Lab 2 • 30 students         ││
│  │                                     ││
│  │  14:00  Data Structures (CSE-B)     ││
│  │         Room 205 • 55 students      ││
│  │                                     ││
│  │  [View All Classes →]               ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  ⏳ PENDING TASKS                   ││
│  │                                     ││
│  │  ⚠️ 3 attendance pending            ││
│  │  ⚠️ 2 grade entries due             ││
│  │  📝 1 mentee request                ││
│  │                                     ││
│  │  [View All Tasks →]                 ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  📊 QUICK STATS                     ││
│  │                                     ││
│  │  Classes: 3  │  Students: 143       ││
│  │  Mentees: 5  │  Leave: 8 days       ││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      📋      📝      ≡      │
│  Home  Classes  Attend  Grades  More   │
└─────────────────────────────────────────┘
```

---

### 2.2 Mark Attendance Screen

**Purpose**: Quick attendance marking for a class

**Critical UX Requirements**:
- Must handle 60 students efficiently
- Should take < 2 minutes to complete
- Support "Mark all present, then mark absent" workflow
- Work on mobile during class

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Mark Attendance                                                          Save  Cancel  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  DATA STRUCTURES (CS301) • CSE-A                                                      │ │
│  │  17 January 2026, Thursday • 09:00 - 10:00 • Room 301                                │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌────────────────────────────────────────────────┐  ┌────────────────────────────────────┐ │
│  │  QUICK ACTIONS                                 │  │  SUMMARY                           │ │
│  │                                                │  │                                    │ │
│  │  [✓ Mark All Present]  [✗ Mark All Absent]    │  │  Total: 58  Present: 55  Absent: 3 │ │
│  │                                                │  │                                    │ │
│  │  Search: [________________________] 🔍        │  │  ████████████████████░ 95%         │ │
│  │                                                │  │                                    │ │
│  └────────────────────────────────────────────────┘  └────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                        │ │
│  │  #   │ Roll No    │ Student Name           │ Overall %  │ Status                      │ │
│  │  ────┼────────────┼────────────────────────┼────────────┼─────────────────────────────│ │
│  │  1   │ CS23001    │ Aakash Kumar          │ 85%        │ [Present ▼]                 │ │
│  │  2   │ CS23002    │ Aditya Sharma         │ 78%        │ [Present ▼]                 │ │
│  │  3   │ CS23003    │ Amit Singh            │ 92%        │ [Present ▼]                 │ │
│  │  4   │ CS23004    │ Anjali Verma          │ 68% ⚠️     │ [Absent  ▼]                 │ │
│  │  5   │ CS23005    │ Arjun Reddy           │ 88%        │ [Present ▼]                 │ │
│  │  6   │ CS23006    │ Deepak Patel          │ 75%        │ [Present ▼]                 │ │
│  │  7   │ CS23007    │ Divya Nair            │ 82%        │ [Present ▼]                 │ │
│  │  8   │ CS23008    │ Gaurav Mishra         │ 71% ⚠️     │ [Absent  ▼]                 │ │
│  │  9   │ CS23009    │ Harish Kumar          │ 89%        │ [Present ▼]                 │ │
│  │  10  │ CS23010    │ Ishita Gupta          │ 95%        │ [Present ▼]                 │ │
│  │  ... │ ...        │ ...                   │ ...        │ ...                         │ │
│  │  58  │ CS23058    │ Zoya Khan             │ 87%        │ [Present ▼]                 │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                            [SAVE ATTENDANCE]                                           │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile Layout (Optimized for quick marking)**:
```
┌─────────────────────────────────────────┐
│  ←  Mark Attendance               Save  │
├─────────────────────────────────────────┤
│                                         │
│  Data Structures • CSE-A                │
│  17 Jan 2026 • 09:00 - 10:00           │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  [✓ All Present]     [✗ All Absent]    │
│                                         │
│  Present: 55  │  Absent: 3  │  Total: 58│
│                                         │
├─────────────────────────────────────────┤
│  🔍 Search student...                   │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  CS23001 • Aakash Kumar      [✓ P] ││
│  │  Overall: 85%                       ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  CS23002 • Aditya Sharma     [✓ P] ││
│  │  Overall: 78%                       ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  CS23003 • Amit Singh        [✓ P] ││
│  │  Overall: 92%                       ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  CS23004 • Anjali Verma  ⚠️  [✗ A] ││
│  │  Overall: 68% (Below 75%)           ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  CS23005 • Arjun Reddy       [✓ P] ││
│  │  Overall: 88%                       ││
│  └─────────────────────────────────────┘│
│                                         │
│  ... (scrollable list)                  │
│                                         │
├─────────────────────────────────────────┤
│          [SAVE ATTENDANCE]              │
├─────────────────────────────────────────┤
│  🏠      📚      📋      📝      ≡      │
└─────────────────────────────────────────┘
```

**Interaction Design**:

1. **Mark All Present First**:
   - Faculty clicks "Mark All Present"
   - All students set to Present
   - Now only need to tap absent students

2. **Tap to Toggle**:
   - Single tap toggles Present ↔ Absent
   - Clear visual feedback (color change)
   - Haptic feedback on mobile

3. **Quick Search**:
   - Type name or roll number
   - Instant filter
   - For latecomers

4. **Visual Indicators**:
   - ⚠️ for students below 75% attendance
   - Color: Green (Present), Red (Absent)
   - Show overall attendance %

**States**:
```
PRESENT STATE:
┌─────────────────────────────────────┐
│  CS23001 • Aakash Kumar      [✓ P] │  <- Green background
│  Overall: 85%                       │
└─────────────────────────────────────┘

ABSENT STATE:
┌─────────────────────────────────────┐
│  CS23004 • Anjali Verma  ⚠️  [✗ A] │  <- Red/Pink background
│  Overall: 68% (Below 75%)           │
└─────────────────────────────────────┘
```

---

### 2.3 Grade Entry Screen

**Purpose**: Enter grades for assignments, tests, and exams

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Grade Entry                                                         Save Draft  Submit │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  DATA STRUCTURES (CS301) • CSE-A                                                      │ │
│  │  Mid-Semester Examination • Max Marks: 30                                             │ │
│  │  Due: 28 January 2026 • Status: In Progress                                          │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌────────────────────────────────────────────────┐  ┌────────────────────────────────────┐ │
│  │  QUICK ACTIONS                                 │  │  STATISTICS                        │ │
│  │                                                │  │                                    │ │
│  │  Import from CSV  │  Export Template          │  │  Entered: 45/58  │  Remaining: 13  │ │
│  │                                                │  │  Average: 24.5   │  Highest: 29    │ │
│  │  Filter: [All ▼]  Sort: [Roll No ▼]          │  │  Lowest: 12      │  Pass %: 87%    │ │
│  │                                                │  │                                    │ │
│  └────────────────────────────────────────────────┘  └────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                        │ │
│  │  #   │ Roll No    │ Student Name           │ Marks (0-30)  │ Grade  │ Remarks        │ │
│  │  ────┼────────────┼────────────────────────┼───────────────┼────────┼────────────────│ │
│  │  1   │ CS23001    │ Aakash Kumar          │ [  27  ]      │   A    │ [___________]  │ │
│  │  2   │ CS23002    │ Aditya Sharma         │ [  24  ]      │   B+   │ [___________]  │ │
│  │  3   │ CS23003    │ Amit Singh            │ [  29  ]      │   A+   │ [___________]  │ │
│  │  4   │ CS23004    │ Anjali Verma          │ [  18  ]      │   B    │ [___________]  │ │
│  │  5   │ CS23005    │ Arjun Reddy           │ [  25  ]      │   A    │ [___________]  │ │
│  │  6   │ CS23006    │ Deepak Patel          │ [     ]       │   -    │ [___________]  │ │
│  │  7   │ CS23007    │ Divya Nair            │ [  22  ]      │   B+   │ [___________]  │ │
│  │  8   │ CS23008    │ Gaurav Mishra         │ [  AB  ]      │   AB   │ [Absent     ]  │ │
│  │  9   │ CS23009    │ Harish Kumar          │ [     ]       │   -    │ [___________]  │ │
│  │  10  │ CS23010    │ Ishita Gupta          │ [  28  ]      │   A    │ [___________]  │ │
│  │  ... │ ...        │ ...                   │ ...           │ ...    │ ...            │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │           [SAVE DRAFT]                      [SUBMIT FOR APPROVAL]                      │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Grade Entry Interactions**:

1. **Keyboard Navigation**:
   - Tab to move between fields
   - Enter marks, auto-calculate grade
   - Arrow keys to navigate

2. **Quick Entry**:
   - "AB" for absent
   - Auto-save drafts
   - Validation on entry

3. **Bulk Actions**:
   - Import from CSV
   - Copy grades from previous assessment
   - Filter by entered/pending

**Grade Scale Reference** (shown as tooltip/modal):
```
┌─────────────────────────────────────┐
│  GRADE SCALE                        │
│                                     │
│  A+  : 90-100% (27-30)             │
│  A   : 80-89%  (24-26)             │
│  B+  : 70-79%  (21-23)             │
│  B   : 60-69%  (18-20)             │
│  C+  : 50-59%  (15-17)             │
│  C   : 40-49%  (12-14)             │
│  F   : <40%    (0-11)              │
│  AB  : Absent                       │
└─────────────────────────────────────┘
```

---

### 2.4 My Classes Screen

**Purpose**: View all assigned classes and courses

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  My Classes                                                     Current Semester: Odd 2025-26 │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  SEMESTER 5 (CURRENT)                                                                  │ │
│  │                                                                                        │ │
│  │  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐            │ │
│  │  │  📘 DATA STRUCTURES             │  │  📗 DATABASE SYSTEMS            │            │ │
│  │  │  CS301 • 4 Credits             │  │  CS302 • 4 Credits              │            │ │
│  │  │                                 │  │                                  │            │ │
│  │  │  Sections: CSE-A, CSE-B        │  │  Sections: CSE-B                │            │ │
│  │  │  Students: 113                  │  │  Students: 55                   │            │ │
│  │  │  Classes/Week: 6                │  │  Classes/Week: 3                │            │ │
│  │  │                                 │  │                                  │            │ │
│  │  │  [View Details]                │  │  [View Details]                 │            │ │
│  │  └─────────────────────────────────┘  └─────────────────────────────────┘            │ │
│  │                                                                                        │ │
│  │  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐            │ │
│  │  │  💻 DSA LAB                     │  │  💻 DBMS LAB                    │            │ │
│  │  │  CS301P • 2 Credits            │  │  CS302P • 2 Credits             │            │ │
│  │  │                                 │  │                                  │            │ │
│  │  │  Sections: CSE-A               │  │  Sections: CSE-B                │            │ │
│  │  │  Students: 30 (per batch)      │  │  Students: 30 (per batch)       │            │ │
│  │  │  Sessions/Week: 1               │  │  Sessions/Week: 1               │            │ │
│  │  │                                 │  │                                  │            │ │
│  │  │  [View Details]                │  │  [View Details]                 │            │ │
│  │  └─────────────────────────────────┘  └─────────────────────────────────┘            │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  QUICK SUMMARY                                                                        │ │
│  │                                                                                        │ │
│  │  Total Courses: 4  │  Total Students: 168  │  Classes/Week: 11  │  Labs/Week: 2      │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Class Detail View**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Data Structures (CS301)                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  [Overview]    [Students]    [Attendance]    [Grades]    [Materials]                    ││
│  │       ▼                                                                                  ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐          │
│  │  COURSE INFORMATION                 │  │  SCHEDULE                           │          │
│  │                                     │  │                                     │          │
│  │  Course Code: CS301                 │  │  Monday    09:00-10:00  Room 301   │          │
│  │  Credits: 4                         │  │  Wednesday 09:00-10:00  Room 301   │          │
│  │  Type: Theory                       │  │  Friday    09:00-10:00  Room 301   │          │
│  │  Sections: CSE-A, CSE-B             │  │                                     │          │
│  │  Total Students: 113                │  │  Lab: Tuesday 11:00-13:00 Lab 1    │          │
│  │                                     │  │                                     │          │
│  └─────────────────────────────────────┘  └─────────────────────────────────────┘          │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  ATTENDANCE SUMMARY                                                                     ││
│  │                                                                                          ││
│  │  Classes Conducted: 24  │  Average Attendance: 87%  │  Students Below 75%: 8           ││
│  │                                                                                          ││
│  │  [Mark Today's Attendance]          [View Attendance Report]                            ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐│
│  │  PENDING GRADES                                                                         ││
│  │                                                                                          ││
│  │  • Mid-Semester Exam (30 marks) - Due: 28 Jan 2026 - [Enter Grades]                    ││
│  │  • Assignment 2 (10 marks) - Due: 5 Feb 2026 - [Enter Grades]                          ││
│  │                                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.5 Leave Application Screen (HR Self-Service)

**Purpose**: Apply for leave and view balance

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Leave Management                    │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  LEAVE BALANCE                      ││
│  │                                     ││
│  │  Casual    │██████████░░│  8/12    ││
│  │  Sick      │████████████│  10/10   ││
│  │  Earned    │████░░░░░░░░│  5/15    ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │         [+ APPLY FOR LEAVE]         ││
│  └─────────────────────────────────────┘│
│                                         │
│  RECENT APPLICATIONS                    │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  15-16 Jan 2026                     ││
│  │  Casual Leave • 2 days              ││
│  │  ✅ Approved                        ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  10 Jan 2026                        ││
│  │  Sick Leave • 1 day                 ││
│  │  ✅ Approved                        ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  5-6 Dec 2025                       ││
│  │  Casual Leave • 2 days              ││
│  │  ✅ Approved                        ││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      📋      📝      ≡      │
└─────────────────────────────────────────┘
```

**Apply Leave Form**:
```
┌─────────────────────────────────────────┐
│  ←  Apply for Leave              Submit │
├─────────────────────────────────────────┤
│                                         │
│  Leave Type *                           │
│  ┌─────────────────────────────────────┐│
│  │  Casual Leave                    ▼  ││
│  └─────────────────────────────────────┘│
│  Available: 8 days                      │
│                                         │
│  From Date *                            │
│  ┌─────────────────────────────────────┐│
│  │  20 Jan 2026                     📅 ││
│  └─────────────────────────────────────┘│
│                                         │
│  To Date *                              │
│  ┌─────────────────────────────────────┐│
│  │  21 Jan 2026                     📅 ││
│  └─────────────────────────────────────┘│
│                                         │
│  Number of Days: 2                      │
│                                         │
│  Half Day?                              │
│  ○ No    ○ First Half    ○ Second Half │
│                                         │
│  Reason *                               │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │  Personal work                      ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  Attachment (Optional)                  │
│  ┌─────────────────────────────────────┐│
│  │  + Add Document                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │           [SUBMIT]                  ││
│  └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
```

---

### 2.6 Payslip View Screen

**Purpose**: View and download monthly payslips

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Payslips                            │
├─────────────────────────────────────────┤
│                                         │
│  Select Month                           │
│  ┌─────────────────────────────────────┐│
│  │  December 2025                   ▼  ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  SALARY SLIP - DECEMBER 2025        ││
│  │                                     ││
│  │  Employee: Dr. Ananya K             ││
│  │  Designation: Assistant Professor   ││
│  │  Department: Computer Science       ││
│  │                                     ││
│  │  ─────────────────────────────────  ││
│  │                                     ││
│  │  EARNINGS                           ││
│  │  Basic Salary        ₹45,000       ││
│  │  DA                  ₹18,000       ││
│  │  HRA                 ₹13,500       ││
│  │  Special Allowance   ₹8,500        ││
│  │  ─────────────────────────────────  ││
│  │  Gross Earnings      ₹85,000       ││
│  │                                     ││
│  │  DEDUCTIONS                         ││
│  │  PF                  ₹5,400        ││
│  │  Professional Tax    ₹200          ││
│  │  Income Tax          ₹8,500        ││
│  │  ─────────────────────────────────  ││
│  │  Total Deductions    ₹14,100       ││
│  │                                     ││
│  │  ═════════════════════════════════  ││
│  │  NET SALARY          ₹70,900       ││
│  │  ═════════════════════════════════  ││
│  │                                     ││
│  │  [DOWNLOAD PDF]                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  PREVIOUS MONTHS                        │
│  ┌─────────────────────────────────────┐│
│  │  Nov 2025  │  ₹70,900  │ [📄]      ││
│  │  Oct 2025  │  ₹70,900  │ [📄]      ││
│  │  Sep 2025  │  ₹70,900  │ [📄]      ││
│  └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
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
│  📚 My Classes  │
│                 │
│  📋 Attendance  │
│    ├ Mark       │
│    └ Reports    │
│                 │
│  📝 Grades      │
│    ├ Entry      │
│    └ Summary    │
│                 │
│  👥 Mentees     │
│                 │
│  ─────────────  │
│                 │
│  👤 HR Self-Serv│
│    ├ Profile    │
│    ├ Leave      │
│    ├ Attendance │
│    └ Payslips   │
│                 │
│  📖 Research    │
│                 │
│  ─────────────  │
│                 │
│  ⚙️ Settings    │
│  🚪 Logout      │
│                 │
└─────────────────┘
```

### Mobile Bottom Navigation

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│   🏠        📚         📋         📝         ≡               │
│  Home    Classes   Attendance  Grades     More               │
│                                                               │
└───────────────────────────────────────────────────────────────┘

MORE Menu:
├── 👥 Mentees
├── 👤 My Profile
├── 📋 Leave Management
├── 💰 Payslips
├── 📖 Research
├── ⚙️ Settings
└── 🚪 Logout
```

---

## 4. Key Workflows

### Workflow 1: Morning Class Routine

```
1. Faculty opens app
2. Dashboard shows today's classes
3. Taps "Mark Attendance" on first class
4. Attendance screen opens with student list
5. Clicks "Mark All Present"
6. Marks absent students (tap to toggle)
7. Clicks "Save Attendance"
8. Returns to dashboard
9. Repeats for next class
```

### Workflow 2: Grade Entry

```
1. Faculty navigates to Grades
2. Selects course and assessment
3. Enters marks for each student
4. System auto-calculates grades
5. Reviews statistics
6. Saves as draft or submits for approval
```

### Workflow 3: Leave Application

```
1. Faculty goes to HR Self-Service > Leave
2. Views current balance
3. Clicks "Apply for Leave"
4. Fills form (type, dates, reason)
5. Submits application
6. Receives confirmation
7. Waits for approval notification
```

---

## 5. Component Specifications

### Attendance Toggle Button

```
PRESENT (Default after "Mark All"):
┌─────────────────────────────────────┐
│  CS23001 • Aakash Kumar      [✓ P] │
└─────────────────────────────────────┘
Background: Light Green (#E8F5E9)
Button: Green with checkmark
Tap → Changes to Absent

ABSENT:
┌─────────────────────────────────────┐
│  CS23004 • Anjali Verma  ⚠️  [✗ A] │
└─────────────────────────────────────┘
Background: Light Red (#FFEBEE)
Button: Red with X
Tap → Changes to Present
```

### Grade Input Field

```
┌──────────────┐
│   [ 27 ]     │  <- Numeric input
└──────────────┘
- Max length based on max marks
- Validates on blur
- Shows error if > max or negative
- Accepts "AB" for absent
```

### Class Card

```
┌─────────────────────────────────────┐
│  📘 DATA STRUCTURES                 │
│  CS301 • 4 Credits                  │
│                                     │
│  Sections: CSE-A, CSE-B             │
│  Students: 113                       │
│  Classes/Week: 6                     │
│                                     │
│  [View Details]                     │
└─────────────────────────────────────┘
```

---

## 6. Accessibility Considerations

| Requirement | Implementation |
|-------------|----------------|
| Keyboard Navigation | Full support for grade entry |
| Tab Order | Logical flow in forms |
| Focus Visible | Clear focus rings |
| High Contrast | For attendance toggle |
| Screen Reader | ARIA labels for actions |
| Large Targets | Min 44×44px for toggle |

---

## 7. Offline Behavior

| Feature | Offline Capability |
|---------|-------------------|
| Dashboard | Show cached schedule |
| Class List | Full offline access |
| Mark Attendance | Queue for sync |
| Grade Entry | Draft mode, sync later |
| Leave Balance | Cached value |
| Payslips | Downloaded PDFs only |

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Module Priority**: P0 (Critical)
**Primary Device**: Desktop (60%), Mobile (40%)
