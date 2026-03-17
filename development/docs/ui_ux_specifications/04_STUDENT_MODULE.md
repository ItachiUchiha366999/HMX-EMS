# Student Module - UI/UX Specification

## Module Overview

The Student Module is the **highest priority** module, serving ~2,000 students and ~2,000 parents. It must be **mobile-first** with excellent performance on 4G connections.

---

## 1. Module Structure

```
STUDENT MODULE
│
├── 📊 Dashboard
│   ├── Today's Schedule Widget
│   ├── Attendance Summary Widget
│   ├── Pending Fees Widget
│   ├── Upcoming Exams Widget
│   ├── Recent Notifications Widget
│   └── Quick Actions
│
├── 📚 Academics
│   ├── My Courses
│   ├── Timetable
│   ├── Attendance
│   └── Grades & Results
│
├── 💰 Fees & Payments
│   ├── Fee Summary
│   ├── Payment History
│   ├── Make Payment
│   └── Download Receipts
│
├── 📝 Examinations
│   ├── Exam Schedule
│   ├── Hall Tickets
│   ├── Results
│   └── Revaluation (if applicable)
│
├── 📖 Library (Optional)
│   ├── Search Books
│   ├── My Borrowings
│   └── Fines
│
├── 🏠 Hostel (Optional)
│   ├── Room Details
│   ├── Complaints
│   └── Mess Menu
│
├── 🚌 Transport (Optional)
│   ├── Route Info
│   └── Bus Tracking
│
├── 💼 Placement (Optional)
│   ├── Job Postings
│   ├── My Applications
│   └── Interview Schedule
│
├── 📢 Notifications
│   └── All Notifications
│
├── 🎫 Grievances
│   ├── Submit Grievance
│   └── My Grievances
│
└── 👤 Profile
    ├── Personal Info
    ├── Academic Info
    └── Documents
```

---

## 2. Screen Specifications

### 2.1 Dashboard

**Purpose**: Single view of everything important to the student

**Mobile Layout** (Primary):
```
┌─────────────────────────────────────────┐
│  ≡  University ERP          🔔  👤      │  <- Header
├─────────────────────────────────────────┤
│                                         │
│  Good Morning, Rahul! 👋                │
│  B.Tech CSE, Semester 5                 │
│                                         │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │  📅 TODAY'S CLASSES                 ││
│  │                                     ││
│  │  09:00  Data Structures     Room 301││
│  │  11:00  Database Systems    Lab 2   ││
│  │  14:00  Computer Networks   Room 205││
│  │  16:00  Software Engg       Room 301││
│  │                                     ││
│  │  [View Full Timetable →]            ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  📊 ATTENDANCE                      ││
│  │                                     ││
│  │  ████████████░░░  76%               ││
│  │                                     ││
│  │  Present: 45  │  Absent: 14         ││
│  │  Minimum Required: 75%              ││
│  │                                     ││
│  │  [View Details →]                   ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  💰 PENDING FEES                    ││
│  │                                     ││
│  │  ₹45,000                            ││
│  │  Due: 15 Feb 2026                   ││
│  │                                     ││
│  │  [Pay Now]                          ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  📝 UPCOMING EXAMS                  ││
│  │                                     ││
│  │  DBMS Mid-Sem    │  20 Feb  │ 15 days│
│  │  DSA End-Sem     │  10 Mar  │ 35 days│
│  │                                     ││
│  │  [View Schedule →]                  ││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      💰      📝      ≡      │  <- Bottom Nav
│  Home  Academic  Fees   Exams   More   │
└─────────────────────────────────────────┘
```

**Widgets Data**:

| Widget | Data Source | Refresh |
|--------|-------------|---------|
| Today's Classes | Course Schedule | On load |
| Attendance | Student Attendance | Daily |
| Pending Fees | Fees DocType | On load |
| Upcoming Exams | Exam Schedule | Weekly |
| Notifications | Notifications | Real-time |

**Interactions**:
- Pull-to-refresh on mobile
- Widget tap → Navigate to detail screen
- "View" links → Navigate to section
- Swipe between days for schedule

**States**:
- **Loading**: Skeleton cards
- **Empty**: Friendly message per widget
- **Error**: Retry option per widget
- **Offline**: Show cached data with indicator

---

### 2.2 Timetable Screen

**Purpose**: View weekly class schedule

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Timetable                    Today  │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┐│
│  │ Mon │ Tue │ Wed │ Thu │ Fri │ Sat  ││  <- Day selector
│  │ 15  │ 16  │ 17  │ 18  │ 19  │ 20   ││
│  │      ▲                              ││
│  └─────────────────────────────────────┘│
│                                         │
│  TUESDAY, 16 JANUARY                    │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  09:00 - 10:00                      ││
│  │  ┌─────────────────────────────────┐││
│  │  │ 📘 Data Structures              │││
│  │  │ Room 301 • Dr. Ananya K         │││
│  │  │ [Lecture]                       │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  10:00 - 11:00                      ││
│  │  ┌─────────────────────────────────┐││
│  │  │ ☕ Break                         │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  11:00 - 13:00                      ││
│  │  ┌─────────────────────────────────┐││
│  │  │ 💻 Database Lab                 │││
│  │  │ Lab 2 • Prof. Sharma            │││
│  │  │ [Practical]                     │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  14:00 - 15:00                      ││
│  │  ┌─────────────────────────────────┐││
│  │  │ 🌐 Computer Networks            │││
│  │  │ Room 205 • Dr. Kumar            │││
│  │  │ [Lecture]                       │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      💰      📝      ≡      │
└─────────────────────────────────────────┘
```

**Interactions**:
- Swipe left/right to change day
- Tap day to jump to date
- "Today" button to return to current day
- Tap class for details (room map, syllabus, etc.)

**Visual Design**:
- Color-code by class type (Lecture, Lab, Tutorial)
- Show current class highlighted if today
- Indicate cancelled classes with strikethrough
- Show free periods clearly

---

### 2.3 Attendance Screen

**Purpose**: View attendance for all courses

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Attendance                   Filter │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  OVERALL ATTENDANCE                 ││
│  │                                     ││
│  │         ┌───────────┐              ││
│  │        /             \             ││
│  │       │     76%      │             ││
│  │       │   Present    │             ││
│  │        \             /             ││
│  │         └───────────┘              ││
│  │                                     ││
│  │  45 Present  │  14 Absent  │  59 Total ││
│  │                                     ││
│  │  ⚠️ Minimum required: 75%           ││
│  └─────────────────────────────────────┘│
│                                         │
│  SUBJECT-WISE BREAKDOWN                 │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  Data Structures                    ││
│  │  ████████████████░░  82%   ✓       ││
│  │  12/15 classes attended             ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  Database Systems                   ││
│  │  ██████████████░░░░  70%   ⚠️       ││
│  │  10/14 classes attended             ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  Computer Networks                  ││
│  │  █████████████████░  85%   ✓       ││
│  │  11/13 classes attended             ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  Software Engineering               ││
│  │  ██████████████████░ 92%   ✓       ││
│  │  12/13 classes attended             ││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      💰      📝      ≡      │
└─────────────────────────────────────────┘
```

**Detail View (on tap)**:
```
┌─────────────────────────────────────────┐
│  ←  Data Structures              Export │
├─────────────────────────────────────────┤
│                                         │
│  ATTENDANCE: 82% (12/15)               │
│                                         │
│  JANUARY 2026                           │
│  ┌───┬───┬───┬───┬───┬───┬───┐         │
│  │ S │ M │ T │ W │ T │ F │ S │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │   │   │   │ 1 │ 2 │ 3 │ 4 │         │
│  │   │   │   │ ● │   │ ● │   │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │         │
│  │   │ ● │   │ ● │   │ ○ │   │         │
│  ├───┼───┼───┼───┼───┼───┼───┤         │
│  │12 │13 │14 │15 │16 │17 │18 │         │
│  │   │ ● │   │ ● │ ● │ ● │   │         │
│  └───┴───┴───┴───┴───┴───┴───┘         │
│                                         │
│  ● Present  ○ Absent  - No class        │
│                                         │
│  ATTENDANCE LOG                         │
│                                         │
│  17 Jan │ Present │ 09:00 - 10:00      │
│  16 Jan │ Present │ 09:00 - 10:00      │
│  15 Jan │ Present │ 09:00 - 10:00      │
│  10 Jan │ Absent  │ 09:00 - 10:00      │
│  09 Jan │ Present │ 09:00 - 10:00      │
│  ...                                    │
│                                         │
└─────────────────────────────────────────┘
```

**Visual Elements**:
- Overall percentage with circular progress
- Color coding: Green (≥75%), Yellow (70-74%), Red (<70%)
- Calendar view for monthly overview
- Trend indicator (improving/declining)

---

### 2.4 Fees & Payments Screen

**Purpose**: View fee details and make payments

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Fees & Payments              History│
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  💰 AMOUNT DUE                      ││
│  │                                     ││
│  │  ₹45,000                            ││
│  │                                     ││
│  │  Due Date: 15 February 2026         ││
│  │  ⏰ 28 days remaining               ││
│  │                                     ││
│  │  ┌─────────────────────────────────┐││
│  │  │        [PAY NOW]                │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
│                                         │
│  FEE BREAKUP                            │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │  Tuition Fee          ₹35,000      ││
│  │  Lab Fee              ₹5,000       ││
│  │  Library Fee          ₹2,000       ││
│  │  Sports Fee           ₹1,500       ││
│  │  Development Fee      ₹1,500       ││
│  │  ────────────────────────────────  ││
│  │  Total                ₹45,000      ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  PAYMENT SUMMARY (2025-26)              │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │  Total Annual Fee      ₹1,80,000   ││
│  │  Paid                  ₹1,35,000   ││
│  │  Pending               ₹45,000     ││
│  │                                     ││
│  │  ████████████████░░░░  75%         ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  RECENT PAYMENTS                        │
│  ┌─────────────────────────────────────┐│
│  │  15 Nov 2025  │  ₹45,000  │ [📄]   ││
│  │  15 Aug 2025  │  ₹45,000  │ [📄]   ││
│  │  15 May 2025  │  ₹45,000  │ [📄]   ││
│  │                                     ││
│  │  [View All Payments →]              ││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      💰      📝      ≡      │
└─────────────────────────────────────────┘
```

**Payment Flow**:
```
┌─────────────────────────────────────────┐
│  ←  Make Payment                        │
├─────────────────────────────────────────┤
│                                         │
│  PAYING FOR                             │
│  ┌─────────────────────────────────────┐│
│  │  Semester 5 Fees                    ││
│  │  Due: 15 February 2026              ││
│  └─────────────────────────────────────┘│
│                                         │
│  AMOUNT                                 │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │  ● Pay Full Amount     ₹45,000     ││
│  │                                     ││
│  │  ○ Pay Partial Amount              ││
│  │    [Enter amount: ₹_______]        ││
│  │    (Min: ₹10,000)                  ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  PAYMENT METHOD                         │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │  ○ UPI (GPay, PhonePe, Paytm)      ││
│  │  ○ Credit/Debit Card               ││
│  │  ○ Net Banking                     ││
│  │  ○ Wallet                          ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  SUMMARY                                │
│  ┌─────────────────────────────────────┐│
│  │  Amount:          ₹45,000          ││
│  │  Convenience Fee:     ₹0           ││
│  │  ─────────────────────────         ││
│  │  Total:           ₹45,000          ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │          [PROCEED TO PAY]          ││
│  └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
```

**Payment Success**:
```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│              ┌───────────┐              │
│             │     ✓     │              │
│             │  SUCCESS  │              │
│              └───────────┘              │
│                                         │
│         Payment Successful!             │
│                                         │
│         Amount: ₹45,000                 │
│         Receipt: RCP-2026-00145         │
│         Date: 17 Jan 2026               │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │       [DOWNLOAD RECEIPT]           ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │       [SHARE RECEIPT]              ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │       [BACK TO DASHBOARD]          ││
│  └─────────────────────────────────────┘│
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**States**:
- **No Dues**: Celebration message, green checkmark
- **Overdue**: Red highlight, late fee warning
- **Partial Payment**: Show paid vs remaining
- **Processing**: Show pending transaction

---

### 2.5 Examinations Screen

**Purpose**: View exam schedule, download hall tickets, see results

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Examinations                        │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────┬────────────┬──────────┐│
│  │  Schedule  │ Hall Ticket │ Results  ││
│  │     ▼      │            │          ││
│  └────────────┴────────────┴──────────┘│
│                                         │
│  UPCOMING EXAMS                         │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  MID-SEMESTER EXAMINATIONS          ││
│  │  February 2026                      ││
│  │                                     ││
│  │  ┌─────────────────────────────────┐││
│  │  │  20 Feb │ DBMS                  │││
│  │  │  Mon    │ 09:00 - 12:00         │││
│  │  │         │ Hall A                │││
│  │  │         │ ⏰ 15 days            │││
│  │  └─────────────────────────────────┘││
│  │                                     ││
│  │  ┌─────────────────────────────────┐││
│  │  │  22 Feb │ Data Structures       │││
│  │  │  Wed    │ 09:00 - 12:00         │││
│  │  │         │ Hall B                │││
│  │  │         │ ⏰ 17 days            │││
│  │  └─────────────────────────────────┘││
│  │                                     ││
│  │  ┌─────────────────────────────────┐││
│  │  │  24 Feb │ Computer Networks     │││
│  │  │  Fri    │ 14:00 - 17:00         │││
│  │  │         │ Hall A                │││
│  │  │         │ ⏰ 19 days            │││
│  │  └─────────────────────────────────┘││
│  │                                     ││
│  │  ┌─────────────────────────────────┐││
│  │  │  26 Feb │ Software Engineering  │││
│  │  │  Sun    │ 09:00 - 12:00         │││
│  │  │         │ Hall C                │││
│  │  │         │ ⏰ 21 days            │││
│  │  └─────────────────────────────────┘││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  END-SEMESTER EXAMINATIONS              │
│  March 2026                             │
│  [Schedule not yet published]           │
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      💰      📝      ≡      │
└─────────────────────────────────────────┘
```

**Hall Ticket Tab**:
```
┌─────────────────────────────────────────┐
│  ←  Examinations                        │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────┬────────────┬──────────┐│
│  │  Schedule  │ Hall Ticket │ Results  ││
│  │            │     ▼      │          ││
│  └────────────┴────────────┴──────────┘│
│                                         │
│  HALL TICKETS                           │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  ✅ MID-SEMESTER EXAM               ││
│  │     February 2026                   ││
│  │                                     ││
│  │     Status: Available               ││
│  │                                     ││
│  │     [DOWNLOAD]  [VIEW]              ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  🔒 END-SEMESTER EXAM               ││
│  │     March 2026                      ││
│  │                                     ││
│  │     Status: Not Available           ││
│  │     (Will be available from 1 Mar)  ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  📋 PREVIOUS                        ││
│  │                                     ││
│  │  End-Sem Nov 2025    [DOWNLOAD]    ││
│  │  Mid-Sem Sep 2025    [DOWNLOAD]    ││
│  │  End-Sem Apr 2025    [DOWNLOAD]    ││
│  └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
```

**Results Tab**:
```
┌─────────────────────────────────────────┐
│  ←  Examinations                        │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────┬────────────┬──────────┐│
│  │  Schedule  │ Hall Ticket │ Results  ││
│  │            │            │    ▼     ││
│  └────────────┴────────────┴──────────┘│
│                                         │
│  CURRENT CGPA                           │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │          7.8 / 10                   ││
│  │                                     ││
│  │  Semester 1: 7.5  │  Semester 2: 7.6││
│  │  Semester 3: 7.9  │  Semester 4: 8.2││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  SEMESTER 4 RESULTS (Latest)            │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │  SGPA: 8.2                          ││
│  │                                     ││
│  │  Subject         │ Grade │ Credits  ││
│  │  ────────────────┼───────┼─────────││
│  │  Operating Sys   │   A   │    4     ││
│  │  Algorithms      │   A+  │    4     ││
│  │  Math IV         │   B+  │    3     ││
│  │  Web Tech        │   A   │    3     ││
│  │  Web Tech Lab    │   A+  │    2     ││
│  │                                     ││
│  │  Total Credits: 16                  ││
│  │                                     ││
│  │  [DOWNLOAD GRADE CARD]              ││
│  └─────────────────────────────────────┘│
│                                         │
│  PREVIOUS SEMESTERS                     │
│  ┌─────────────────────────────────────┐│
│  │  Semester 3  │  SGPA: 7.9  │ [View] ││
│  │  Semester 2  │  SGPA: 7.6  │ [View] ││
│  │  Semester 1  │  SGPA: 7.5  │ [View] ││
│  └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
```

---

### 2.6 Profile Screen

**Purpose**: View and manage personal information

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Profile                       Edit  │
├─────────────────────────────────────────┤
│                                         │
│           ┌───────────────┐             │
│          │               │             │
│          │     [Photo]   │             │
│          │               │             │
│           └───────────────┘             │
│                                         │
│           Rahul Sharma                  │
│           STU-2023-001234               │
│           B.Tech Computer Science       │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  PERSONAL INFORMATION                   │
│  ┌─────────────────────────────────────┐│
│  │  Date of Birth    15 May 2003       ││
│  │  Gender           Male              ││
│  │  Blood Group      B+                ││
│  │  Phone            +91 98765 43210   ││
│  │  Email            rahul@email.com   ││
│  │  Address          123, Street Name, ││
│  │                   City, State 12345 ││
│  └─────────────────────────────────────┘│
│                                         │
│  ACADEMIC INFORMATION                   │
│  ┌─────────────────────────────────────┐│
│  │  Admission Year   2023              ││
│  │  Program          B.Tech            ││
│  │  Branch           Computer Science  ││
│  │  Current Semester 5                 ││
│  │  Section          A                 ││
│  │  Batch            2023-27           ││
│  │  Roll Number      CS23001           ││
│  └─────────────────────────────────────┘│
│                                         │
│  GUARDIAN INFORMATION                   │
│  ┌─────────────────────────────────────┐│
│  │  Father's Name    Suresh Sharma     ││
│  │  Father's Phone   +91 98765 43211   ││
│  │  Mother's Name    Sunita Sharma     ││
│  │  Mother's Phone   +91 98765 43212   ││
│  └─────────────────────────────────────┘│
│                                         │
│  DOCUMENTS                              │
│  ┌─────────────────────────────────────┐│
│  │  ID Card            [DOWNLOAD]      ││
│  │  Bonafide Cert      [REQUEST]       ││
│  │  Character Cert     [REQUEST]       ││
│  └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
```

---

### 2.7 Notifications Screen

**Purpose**: View all notifications and announcements

**Mobile Layout**:
```
┌─────────────────────────────────────────┐
│  ←  Notifications           Mark All Read│
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  All  │  Unread (3)  │  Important   ││
│  │   ▼   │              │              ││
│  └─────────────────────────────────────┘│
│                                         │
│  TODAY                                  │
│  ┌─────────────────────────────────────┐│
│  │  ● 💰 Fee Reminder                  ││
│  │    Your semester fees of ₹45,000    ││
│  │    is due on 15 Feb 2026            ││
│  │    10:30 AM                         ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  ● 📅 Timetable Update              ││
│  │    Your DBMS class on Friday has    ││
│  │    been rescheduled to 2 PM         ││
│  │    09:15 AM                         ││
│  └─────────────────────────────────────┘│
│                                         │
│  YESTERDAY                              │
│  ┌─────────────────────────────────────┐│
│  │  ○ 📝 Exam Schedule Published       ││
│  │    Mid-semester exam schedule has   ││
│  │    been published. Check now.       ││
│  │    4:30 PM                          ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │  ○ 📊 Attendance Alert              ││
│  │    Your attendance in DBMS has      ││
│  │    dropped below 75%                ││
│  │    11:00 AM                         ││
│  └─────────────────────────────────────┘│
│                                         │
│  EARLIER                                │
│  ┌─────────────────────────────────────┐│
│  │  ○ 📢 Holiday Announcement          ││
│  │    College will be closed on 26th   ││
│  │    January for Republic Day         ││
│  │    15 Jan                           ││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  🏠      📚      💰      📝      ≡      │
└─────────────────────────────────────────┘
```

**Notification Types**:
- 💰 Fee Related
- 📅 Schedule Changes
- 📝 Exams
- 📊 Attendance Alerts
- 📢 Announcements
- 📚 Academic
- 🎓 Placement

---

## 3. Navigation Structure

### Bottom Navigation (Mobile)

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│   🏠        📚         💰         📝         ≡               │
│  Home    Academic     Fees      Exams      More              │
│                                                               │
└───────────────────────────────────────────────────────────────┘

HOME (Dashboard)
├── Today's Schedule
├── Attendance Summary
├── Pending Fees
└── Quick Actions

ACADEMIC
├── My Courses
├── Timetable
├── Attendance
└── Grades

FEES
├── Fee Summary
├── Make Payment
└── Payment History

EXAMS
├── Schedule
├── Hall Tickets
└── Results

MORE (Hamburger)
├── 📖 Library
├── 🏠 Hostel
├── 🚌 Transport
├── 💼 Placement
├── 🎫 Grievances
├── 📢 Notifications
├── 👤 Profile
├── ⚙️ Settings
└── 🚪 Logout
```

### Desktop Sidebar Navigation

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│  ┌─────────────┐  ┌─────────────────────────────────────────────────────────────┐  │
│  │             │  │                                                              │  │
│  │  [Logo]     │  │                      MAIN CONTENT                            │  │
│  │             │  │                                                              │  │
│  │  ─────────  │  │                                                              │  │
│  │             │  │                                                              │  │
│  │  🏠 Dashboard│  │                                                              │  │
│  │             │  │                                                              │  │
│  │  📚 Academic │  │                                                              │  │
│  │    ├ Courses│  │                                                              │  │
│  │    ├ Timetab│  │                                                              │  │
│  │    ├ Attenda│  │                                                              │  │
│  │    └ Grades │  │                                                              │  │
│  │             │  │                                                              │  │
│  │  💰 Fees    │  │                                                              │  │
│  │             │  │                                                              │  │
│  │  📝 Exams   │  │                                                              │  │
│  │             │  │                                                              │  │
│  │  📖 Library │  │                                                              │  │
│  │             │  │                                                              │  │
│  │  🏠 Hostel  │  │                                                              │  │
│  │             │  │                                                              │  │
│  │  🚌Transport│  │                                                              │  │
│  │             │  │                                                              │  │
│  │  💼Placement│  │                                                              │  │
│  │             │  │                                                              │  │
│  │  🎫Grievance│  │                                                              │  │
│  │             │  │                                                              │  │
│  │  ─────────  │  │                                                              │  │
│  │             │  │                                                              │  │
│  │  👤 Profile │  │                                                              │  │
│  │  ⚙️ Settings│  │                                                              │  │
│  │  🚪 Logout  │  │                                                              │  │
│  │             │  │                                                              │  │
│  └─────────────┘  └─────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Specifications

### 4.1 Dashboard Widgets

| Widget | Size (Mobile) | Content | Actions |
|--------|--------------|---------|---------|
| Today's Schedule | Full width | 4-5 classes | Tap to view timetable |
| Attendance | Full width | Percentage, bar | Tap to view details |
| Pending Fees | Full width | Amount, due date | Pay Now button |
| Upcoming Exams | Full width | 2-3 exams | Tap to view schedule |
| Notifications | Full width | 2-3 latest | Tap to view all |

### 4.2 Cards

**Schedule Card**:
```
┌─────────────────────────────────────┐
│  09:00  │  📘 Data Structures       │
│         │  Room 301 • Dr. Ananya K  │
│         │  [Lecture]                │
└─────────────────────────────────────┘
```

**Attendance Card**:
```
┌─────────────────────────────────────┐
│  Data Structures                    │
│  ████████████████░░  82%   ✓       │
│  12/15 classes attended             │
└─────────────────────────────────────┘
```

**Fee Card**:
```
┌─────────────────────────────────────┐
│  Semester 5 Fees                    │
│  ₹45,000  │  Due: 15 Feb 2026      │
│  [PAY NOW]                          │
└─────────────────────────────────────┘
```

### 4.3 Buttons

| Type | Usage | Style |
|------|-------|-------|
| Primary | Main actions (Pay Now, Submit) | Filled, primary color |
| Secondary | Alternative actions | Outlined |
| Ghost | Less emphasis | Text only |
| Icon | Quick actions | Icon with optional label |
| FAB | Primary floating action | Circular, bottom right |

### 4.4 Form Elements

- **Text Input**: Single line with label
- **Text Area**: Multi-line input
- **Select**: Dropdown selection
- **Date Picker**: Calendar selector
- **Checkbox**: Multiple selection
- **Radio**: Single selection
- **File Upload**: Document/image upload
- **Toggle**: On/Off switch

---

## 5. Empty States

### No Classes Today
```
┌─────────────────────────────────────┐
│                                     │
│         📅                          │
│         No classes today!           │
│                                     │
│         Enjoy your day off.         │
│         Check tomorrow's schedule   │
│         below.                      │
│                                     │
│         [View Tomorrow]             │
│                                     │
└─────────────────────────────────────┘
```

### No Pending Fees
```
┌─────────────────────────────────────┐
│                                     │
│         ✅                          │
│         All dues cleared!           │
│                                     │
│         You have no pending fees.   │
│         Keep up the good work!      │
│                                     │
│         [View Payment History]      │
│                                     │
└─────────────────────────────────────┘
```

### No Results Yet
```
┌─────────────────────────────────────┐
│                                     │
│         📊                          │
│         Results not published       │
│                                     │
│         Results for this semester   │
│         are not yet available.      │
│         We'll notify you when       │
│         they're out.                │
│                                     │
│         [Enable Notifications]      │
│                                     │
└─────────────────────────────────────┘
```

---

## 6. Error States

### Network Error
```
┌─────────────────────────────────────┐
│                                     │
│         📶                          │
│         Connection Error            │
│                                     │
│         Unable to connect to        │
│         the server. Please check    │
│         your internet connection.   │
│                                     │
│         [Try Again]                 │
│                                     │
└─────────────────────────────────────┘
```

### Payment Failed
```
┌─────────────────────────────────────┐
│                                     │
│         ❌                          │
│         Payment Failed              │
│                                     │
│         Your payment could not be   │
│         processed. Please try       │
│         again or use a different    │
│         payment method.             │
│                                     │
│         Error: Bank declined        │
│                                     │
│         [Try Again]  [Use Different │
│                       Method]       │
│                                     │
└─────────────────────────────────────┘
```

---

## 7. Loading States

### Skeleton Loading
```
┌─────────────────────────────────────┐
│                                     │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░         │
│  ░░░░░░░░░░░░░░░                    │
│                                     │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│  ░░░░░░░░░░░░░░░░░░░░               │
│  ░░░░░░░░░░░░░                      │
│                                     │
└─────────────────────────────────────┘
```

### Processing Payment
```
┌─────────────────────────────────────┐
│                                     │
│         ⏳                          │
│         Processing Payment          │
│                                     │
│         Please wait while we        │
│         process your payment.       │
│         Do not close this window.   │
│                                     │
│         ████████░░░░░░░░            │
│                                     │
└─────────────────────────────────────┘
```

---

## 8. Accessibility Considerations

| Requirement | Implementation |
|-------------|----------------|
| Color Contrast | Min 4.5:1 for text |
| Touch Targets | Min 44×44 px |
| Font Size | Min 16px body, scalable |
| Focus Indicators | Visible focus ring |
| Screen Reader | ARIA labels |
| Reduced Motion | Respect preference |
| Text Alternatives | Alt text for images |

---

## 9. Offline Behavior

| Screen | Offline Capability |
|--------|-------------------|
| Dashboard | Show cached data |
| Timetable | Full offline access |
| Attendance | Show cached percentage |
| Fees | Show summary, disable payment |
| Results | Show cached results |
| Notifications | Show cached notifications |
| Profile | Show cached profile |

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Module Priority**: P0 (Critical)
**Primary Device**: Mobile
