# Finance & Accounts Module - UI/UX Specification

## Module Overview

The Accounts Module serves ~5 accounts staff members for **fee collection**, **payment management**, and **financial reporting**. This is a **desktop-primary** interface optimized for high-volume transactions at the fee counter.

---

## 1. Module Structure

```
ACCOUNTS MODULE
│
├── 📊 Dashboard
│   ├── Collection Summary
│   ├── Today's Stats
│   ├── Outstanding Overview
│   └── Quick Actions
│
├── 💰 Fee Management
│   ├── Collect Fee
│   ├── Fee Structure
│   ├── Fee Schedule
│   └── Scholarships/Discounts
│
├── 💳 Payments
│   ├── Payment Entry
│   ├── Payment History
│   ├── Pending Verification
│   └── Receipts
│
├── 📋 Outstanding
│   ├── Dues List
│   ├── Send Reminders
│   └── Defaulters Report
│
├── 💵 Cash Management
│   ├── Cash Register
│   ├── Daily Collection
│   └── Bank Deposit
│
├── 📊 Reports
│   ├── Collection Report
│   ├── Outstanding Report
│   ├── Fee Structure Report
│   ├── Department-wise Collection
│   └── Payment Mode Analysis
│
└── ⚙️ Settings
    ├── Fee Categories
    ├── Payment Modes
    └── Receipt Formats
```

---

## 2. Screen Specifications

### 2.1 Accounts Dashboard

**Purpose**: Overview of financial status and quick access to collection

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ≡  University ERP                                          🔔 (2)  Sunita Agarwal  👤  ▼  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────┐  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │             │  │                                                                        │ │
│  │  [Logo]     │  │  Good Morning, Sunita! 👋                    Friday, 17 January 2026 │ │
│  │             │  │                                                                        │ │
│  │  ─────────  │  ├───────────────────────────────────────────────────────────────────────┤ │
│  │             │  │                                                                        │ │
│  │  📊 Dashboard│  │  ┌───────────────────────────────────────────────────────────────────┐│ │
│  │             │  │  │  💰 TODAY'S COLLECTION                                            ││ │
│  │  💰 Fee Mgmt│  │  │                                                                    ││ │
│  │             │  │  │     ₹5,25,000                    Target: ₹8,00,000                ││ │
│  │  💳 Payments│  │  │     ████████████████████░░░░░░░░  66%                              ││ │
│  │             │  │  │                                                                    ││ │
│  │  📋 Outstand│  │  │  Transactions: 42  │  Cash: ₹1,20,000  │  Online: ₹4,05,000      ││ │
│  │             │  │  │                                                                    ││ │
│  │  💵 Cash    │  │  └───────────────────────────────────────────────────────────────────┘│ │
│  │             │  │                                                                        │ │
│  │  📊 Reports │  │  ┌─────────────────────────┐  ┌─────────────────────────┐             │ │
│  │             │  │  │  📈 THIS MONTH          │  │  ⚠️ OUTSTANDING          │             │ │
│  │  ─────────  │  │  │                         │  │                         │             │ │
│  │             │  │  │  Collected: ₹1.2 Cr     │  │  Total: ₹45.5 Lakh      │             │ │
│  │  ⚙️ Settings │  │  │  Target: ₹1.5 Cr       │  │  Students: 312          │             │ │
│  │             │  │  │  Progress: 80%          │  │  Overdue: ₹28.2 Lakh    │             │ │
│  │  🚪 Logout  │  │  │                         │  │                         │             │ │
│  │             │  │  │  [View Details]         │  │  [View Defaulters]      │             │ │
│  │             │  │  └─────────────────────────┘  └─────────────────────────┘             │ │
│  │             │  │                                                                        │ │
│  │             │  │  ┌───────────────────────────────────────────────────────────────────┐│ │
│  │             │  │  │  ⚡ QUICK ACTIONS                                                 ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐         ││ │
│  │             │  │  │  │ 💰 COLLECT    │  │ 🔍 SEARCH     │  │ 📊 TODAY'S    │         ││ │
│  │             │  │  │  │    FEE        │  │    STUDENT    │  │    REPORT     │         ││ │
│  │             │  │  │  └───────────────┘  └───────────────┘  └───────────────┘         ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  └───────────────────────────────────────────────────────────────────┘│ │
│  │             │  │                                                                        │ │
│  │             │  │  ┌───────────────────────────────────────────────────────────────────┐│ │
│  │             │  │  │  🕐 RECENT TRANSACTIONS                                           ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  │  10:30  STU-2023-001234  Rahul Sharma     ₹45,000  Cash    [📄]  ││ │
│  │             │  │  │  10:15  STU-2023-002341  Priya Verma      ₹45,000  UPI     [📄]  ││ │
│  │             │  │  │  10:00  STU-2022-001122  Amit Singh       ₹25,000  Card    [📄]  ││ │
│  │             │  │  │  09:45  STU-2023-003421  Sneha Gupta      ₹45,000  Online  [📄]  ││ │
│  │             │  │  │  09:30  STU-2024-000112  Vikram Kumar     ₹90,000  DD      [📄]  ││ │
│  │             │  │  │                                                                    ││ │
│  │             │  │  │  [View All Transactions]                                          ││ │
│  │             │  │  └───────────────────────────────────────────────────────────────────┘│ │
│  │             │  │                                                                        │ │
│  └─────────────┘  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Fee Collection Screen (CRITICAL)

**Purpose**: Primary screen for collecting fees from students

**Critical UX Requirements**:
- Student search must be instant (< 500ms)
- Complete transaction in < 2 minutes
- Clear fee breakup display
- Reliable receipt printing
- Handle queues efficiently

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Collect Fee                                                                    [F1] Help│
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  🔍 Search Student (ID, Name, or Phone)                                               │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │  STU-2023-001234                                                              X │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                                        │ │
│  │  Recent: Rahul Sharma (STU-2023-001234) • Priya Verma (STU-2023-002341)              │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────┐  ┌─────────────────────────────────────────────┐│
│  │  STUDENT DETAILS                      │  │  FEE DETAILS                                ││
│  │                                        │  │                                             ││
│  │  ┌──────────┐                         │  │  Semester 5 Fees (Odd 2025-26)              ││
│  │  │  [Photo] │  Rahul Sharma           │  │                                             ││
│  │  │          │  STU-2023-001234        │  │  ┌─────────────────────────────────────────┐││
│  │  └──────────┘  B.Tech CSE, Sem 5      │  │  │  COMPONENT              │    AMOUNT     │││
│  │               Section A, Batch 2023-27│  │  │  ───────────────────────┼───────────────│││
│  │                                        │  │  │  Tuition Fee           │    ₹35,000    │││
│  │  📱 +91 98765 43210                   │  │  │  Lab Fee                │    ₹5,000     │││
│  │  📧 rahul.s@email.com                 │  │  │  Library Fee            │    ₹2,000     │││
│  │                                        │  │  │  Sports Fee             │    ₹1,500     │││
│  │  ─────────────────────────────────    │  │  │  Development Fee        │    ₹1,500     │││
│  │                                        │  │  │  ───────────────────────┼───────────────│││
│  │  PAYMENT HISTORY                      │  │  │  TOTAL                  │    ₹45,000    │││
│  │                                        │  │  │                                         │││
│  │  Sem 4: ₹45,000 ✓ (15 Aug 2025)       │  │  │  Less: Scholarship      │   -₹10,000    │││
│  │  Sem 3: ₹45,000 ✓ (15 Feb 2025)       │  │  │  ───────────────────────┼───────────────│││
│  │  Sem 2: ₹45,000 ✓ (15 Aug 2024)       │  │  │  NET PAYABLE            │    ₹35,000    │││
│  │  Sem 1: ₹45,000 ✓ (15 Jul 2023)       │  │  └─────────────────────────────────────────┘││
│  │                                        │  │                                             ││
│  │  Status: ✓ No outstanding dues        │  │  Already Paid: ₹0                           ││
│  │         from previous semesters       │  │  Outstanding:  ₹35,000                      ││
│  │                                        │  │                                             ││
│  └───────────────────────────────────────┘  └─────────────────────────────────────────────┘│
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  PAYMENT ENTRY                                                                         │ │
│  │                                                                                        │ │
│  │  Amount to Pay *                                                                       │ │
│  │  ┌─────────────────────┐   ○ Full Amount (₹35,000)                                    │ │
│  │  │     ₹35,000         │   ○ Partial Amount                                           │ │
│  │  └─────────────────────┘                                                               │ │
│  │                                                                                        │ │
│  │  Payment Mode *                                                                        │ │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐                        │ │
│  │  │ CASH  │ │  UPI  │ │ CARD  │ │ NEFT  │ │ CHEQUE│ │  DD   │                        │ │
│  │  │   ▲   │ │       │ │       │ │       │ │       │ │       │                        │ │
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘                        │ │
│  │                                                                                        │ │
│  │  Reference Number (for online payments)                                               │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                                                                                 │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                                        │ │
│  │  Remarks (Optional)                                                                   │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                                                                                 │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                        │ │
│  │                        [COLLECT ₹35,000 & PRINT RECEIPT]                              │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Student Search Autocomplete**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  🔍 rah                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐│
│  │  Rahul Sharma        STU-2023-001234    B.Tech CSE, Sem 5    ₹35,000 due           ││
│  │  Rahul Kumar         STU-2022-002341    B.Com, Sem 3         No dues               ││
│  │  Rahul Verma         STU-2024-003421    B.Tech ECE, Sem 1    ₹45,000 due           ││
│  │  Rahman Khan         STU-2023-001122    MBA, Sem 2           ₹55,000 due           ││
│  └─────────────────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Payment Mode Selection States**:
```
CASH (Selected):
┌───────┐
│ CASH  │  <- Blue background, white text
│   ✓   │
└───────┘

UPI (Not Selected):
┌───────┐
│  UPI  │  <- Gray border, gray text
│       │
└───────┘
```

---

### 2.3 Receipt Preview & Print

**Purpose**: Preview and print fee receipt

**Print Receipt Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                              │
│                           UNIVERSITY NAME                                                   │
│                           Address Line 1                                                    │
│                           Address Line 2                                                    │
│                                                                                              │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│                              FEE RECEIPT                                                    │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│                                                                                              │
│  Receipt No: RCP-2026-00145                          Date: 17 January 2026                 │
│                                                                                              │
│  ───────────────────────────────────────────────────────────────────────────────────────   │
│  STUDENT DETAILS                                                                            │
│  ───────────────────────────────────────────────────────────────────────────────────────   │
│                                                                                              │
│  Student ID    : STU-2023-001234                                                            │
│  Name          : Rahul Sharma                                                               │
│  Program       : B.Tech Computer Science                                                    │
│  Semester      : 5 (Odd 2025-26)                                                            │
│  Section       : A                                                                          │
│                                                                                              │
│  ───────────────────────────────────────────────────────────────────────────────────────   │
│  FEE DETAILS                                                                                │
│  ───────────────────────────────────────────────────────────────────────────────────────   │
│                                                                                              │
│  S.No  │  Particulars                              │  Amount (₹)                           │
│  ──────┼───────────────────────────────────────────┼───────────────────────────────────    │
│    1   │  Tuition Fee                              │        35,000                          │
│    2   │  Lab Fee                                  │         5,000                          │
│    3   │  Library Fee                              │         2,000                          │
│    4   │  Sports Fee                               │         1,500                          │
│    5   │  Development Fee                          │         1,500                          │
│  ──────┼───────────────────────────────────────────┼───────────────────────────────────    │
│        │  Total                                    │        45,000                          │
│        │  Less: Merit Scholarship                  │       -10,000                          │
│  ══════╪═══════════════════════════════════════════╪═══════════════════════════════════    │
│        │  Net Amount                               │        35,000                          │
│  ══════╧═══════════════════════════════════════════╧═══════════════════════════════════    │
│                                                                                              │
│  Amount in Words: Rupees Thirty Five Thousand Only                                          │
│                                                                                              │
│  ───────────────────────────────────────────────────────────────────────────────────────   │
│  PAYMENT DETAILS                                                                            │
│  ───────────────────────────────────────────────────────────────────────────────────────   │
│                                                                                              │
│  Payment Mode   : Cash                                                                      │
│  Reference No   : -                                                                         │
│  Received By    : Sunita Agarwal                                                            │
│                                                                                              │
│                                                                                              │
│                                                                                              │
│  ─────────────────────                                        ─────────────────────        │
│       Student Sign                                               Accountant Sign            │
│                                                                                              │
│                                                                                              │
│  * This is a computer generated receipt.                                                    │
│  * For any queries, contact accounts@university.edu                                         │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.4 Outstanding Dues Screen

**Purpose**: Track and manage student fee dues

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Outstanding Dues                                                    [Send Reminders]   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  OUTSTANDING SUMMARY                                                                   │ │
│  │                                                                                        │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │ │
│  │  │  TOTAL DUE    │  │  STUDENTS     │  │  OVERDUE      │  │  THIS MONTH   │          │ │
│  │  │  ₹45.5 Lakh   │  │     312       │  │  ₹28.2 Lakh   │  │  ₹17.3 Lakh   │          │ │
│  │  │               │  │               │  │  (>30 days)   │  │               │          │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘          │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  🔍 Search...  │ Program: [All▼]  │ Semester: [All▼]  │ Age: [All▼]  │ [Export]      │ │
│  ├───────────────────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                                        │ │
│  │  □ │ Student ID      │ Name              │ Program      │ Amount    │ Due Date │ Age │ │
│  │  ──┼─────────────────┼───────────────────┼──────────────┼───────────┼──────────┼─────│ │
│  │  □ │ STU-2023-001234 │ Rahul Sharma      │ B.Tech CSE   │ ₹35,000   │ 15 Feb   │ -   │ │
│  │  □ │ STU-2022-002341 │ Priya Verma       │ B.Com        │ ₹28,000   │ 15 Jan   │ 2d  │ │
│  │  □ │ STU-2023-003421 │ Amit Singh        │ B.Tech ECE   │ ₹45,000   │ 01 Jan   │ 16d │ │
│  │  □ │ STU-2022-001122 │ Sneha Gupta       │ MBA          │ ₹55,000   │ 15 Dec   │ 33d │ │
│  │  □ │ STU-2021-004521 │ Vikram Kumar      │ B.Tech Mech  │ ₹35,000   │ 01 Dec   │ 47d │ │
│  │  □ │ STU-2023-005621 │ Anjali Sharma     │ BCA          │ ₹22,000   │ 15 Nov   │ 63d │ │
│  │  ... (more rows)                                                                       │ │
│  │                                                                                        │ │
│  ├───────────────────────────────────────────────────────────────────────────────────────┤ │
│  │  Selected: 0  │  [Send SMS Reminder]  [Send Email]  [Generate Demand Letter]          │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Age Color Coding**:
- Green: Due in future
- Yellow: 1-30 days overdue
- Orange: 31-60 days overdue
- Red: 60+ days overdue

---

### 2.5 Daily Collection Report

**Purpose**: End-of-day collection summary

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Daily Collection Report                               Date: 17 January 2026    [Print] │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  COLLECTION SUMMARY                                                                    │ │
│  │                                                                                        │ │
│  │  ┌───────────────────────────────────────────────────────────────────────────────────┐│ │
│  │  │                                                                                    ││ │
│  │  │  TOTAL COLLECTION            TRANSACTIONS           COLLECTED BY                  ││ │
│  │  │                                                                                    ││ │
│  │  │  ₹5,25,000                        42                 Sunita Agarwal               ││ │
│  │  │                                                                                    ││ │
│  │  └───────────────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  PAYMENT MODE BREAKDOWN                                                                │ │
│  │                                                                                        │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │ │
│  │  │     CASH        │  │      UPI        │  │     CARD        │  │    NEFT/DD      │   │ │
│  │  │   ₹1,20,000     │  │   ₹2,35,000     │  │   ₹85,000       │  │   ₹85,000       │   │ │
│  │  │   12 txns       │  │   18 txns       │  │   8 txns        │  │   4 txns        │   │ │
│  │  │     23%         │  │     45%         │  │     16%         │  │     16%         │   │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  PROGRAM-WISE COLLECTION                                                               │ │
│  │                                                                                        │ │
│  │  Program             │  Students  │  Amount                                           │ │
│  │  ────────────────────┼────────────┼─────────────                                      │ │
│  │  B.Tech              │     18     │  ₹2,70,000                                        │ │
│  │  MBA                 │      8     │  ₹1,20,000                                        │ │
│  │  B.Com               │     10     │  ₹80,000                                          │ │
│  │  BCA                 │      6     │  ₹55,000                                          │ │
│  │  ────────────────────┼────────────┼─────────────                                      │ │
│  │  Total               │     42     │  ₹5,25,000                                        │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  TRANSACTION LOG                                                                       │ │
│  │                                                                                        │ │
│  │  Time  │ Receipt No      │ Student           │ Amount    │ Mode    │ Collected By    │ │
│  │  ──────┼─────────────────┼───────────────────┼───────────┼─────────┼─────────────────│ │
│  │  10:30 │ RCP-2026-00145  │ Rahul Sharma      │ ₹35,000   │ Cash    │ Sunita          │ │
│  │  10:15 │ RCP-2026-00144  │ Priya Verma       │ ₹28,000   │ UPI     │ Sunita          │ │
│  │  10:00 │ RCP-2026-00143  │ Amit Singh        │ ₹45,000   │ Card    │ Sunita          │ │
│  │  ... (more rows)                                                                       │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  CASH REGISTER                                                                         │ │
│  │                                                                                        │ │
│  │  Opening Balance:  ₹5,000          Closing Balance: ₹1,25,000                         │ │
│  │  Cash Received:    ₹1,20,000       To Deposit:      ₹1,20,000                         │ │
│  │                                                                                        │ │
│  │  [Close Register & Generate Deposit Slip]                                             │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.6 Fee Structure Management

**Purpose**: Define and manage fee structures

**Desktop Layout**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  Fee Structure                                                        [+ Create New]    │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Academic Year: [2025-26 ▼]    Program: [All ▼]                                       │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                        │ │
│  │  Program                │ Category      │ Per Semester │ Annual    │ Status  │ Actions│ │
│  │  ──────────────────────┼───────────────┼──────────────┼───────────┼─────────┼────────│ │
│  │  B.Tech                 │ General       │ ₹45,000      │ ₹90,000   │ Active  │ [⋮]    │ │
│  │  B.Tech                 │ SC/ST         │ ₹35,000      │ ₹70,000   │ Active  │ [⋮]    │ │
│  │  B.Tech                 │ Management    │ ₹75,000      │ ₹1,50,000 │ Active  │ [⋮]    │ │
│  │  MBA                    │ General       │ ₹55,000      │ ₹1,10,000 │ Active  │ [⋮]    │ │
│  │  MBA                    │ Management    │ ₹85,000      │ ₹1,70,000 │ Active  │ [⋮]    │ │
│  │  B.Com                  │ General       │ ₹28,000      │ ₹56,000   │ Active  │ [⋮]    │ │
│  │  BCA                    │ General       │ ₹22,000      │ ₹44,000   │ Active  │ [⋮]    │ │
│  │  M.Tech                 │ General       │ ₹35,000      │ ₹70,000   │ Active  │ [⋮]    │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Fee Structure Detail (Edit)**:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ←  B.Tech (General) - Fee Structure                                              [Save]   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  Program: B.Tech Computer Science                                                           │
│  Category: General                                                                          │
│  Academic Year: 2025-26                                                                     │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  FEE COMPONENTS                                                        [+ Add Row]    │ │
│  │                                                                                        │ │
│  │  Component Name        │  Amount    │  Frequency     │  Optional  │  Action          │ │
│  │  ─────────────────────┼────────────┼────────────────┼────────────┼──────────────────│ │
│  │  Tuition Fee           │ ₹35,000    │ Per Semester   │    No      │  [Edit] [Del]   │ │
│  │  Lab Fee               │ ₹5,000     │ Per Semester   │    No      │  [Edit] [Del]   │ │
│  │  Library Fee           │ ₹2,000     │ Per Semester   │    No      │  [Edit] [Del]   │ │
│  │  Sports Fee            │ ₹1,500     │ Per Semester   │    No      │  [Edit] [Del]   │ │
│  │  Development Fee       │ ₹1,500     │ Per Semester   │    No      │  [Edit] [Del]   │ │
│  │  ─────────────────────┼────────────┼────────────────┼────────────┼──────────────────│ │
│  │  TOTAL PER SEMESTER    │ ₹45,000    │                │            │                  │ │
│  │                                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│  │  LATE FEE CONFIGURATION                                                                │ │
│  │                                                                                        │ │
│  │  Enable Late Fee:  ✓ Yes                                                              │ │
│  │  Grace Period:     15 days after due date                                             │ │
│  │  Late Fee Amount:  ₹500 per week (max ₹2,000)                                         │ │
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
│  💰 Fee Mgmt    │
│    ├ Collect    │
│    ├ Structure  │
│    ├ Schedule   │
│    └ Discounts  │
│                 │
│  💳 Payments    │
│    ├ Entry      │
│    ├ History    │
│    ├ Pending    │
│    └ Receipts   │
│                 │
│  📋 Outstanding │
│    ├ Dues List  │
│    ├ Reminders  │
│    └ Defaulters │
│                 │
│  💵 Cash        │
│    ├ Register   │
│    ├ Collection │
│    └ Deposit    │
│                 │
│  📊 Reports     │
│    ├ Collection │
│    ├ Outstanding│
│    ├ Dept-wise  │
│    └ Analysis   │
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

### Workflow 1: Fee Collection (Counter)

```
1. Student arrives at counter
2. Staff searches by ID/Name (F2 shortcut)
3. System shows student details + pending fees
4. Staff confirms amount with student
5. Selects payment mode (Cash/UPI/Card)
6. For online: Enters reference number
7. Clicks "Collect & Print"
8. Receipt prints automatically
9. Staff hands receipt to student
10. Ready for next student (< 2 min total)
```

### Workflow 2: Verify Online Payment

```
1. Staff navigates to Payments > Pending
2. Sees list of unverified online payments
3. Clicks on payment to verify
4. Checks reference number in bank portal
5. If verified: Click "Confirm"
6. If not found: Click "Reject" with reason
7. System updates status and notifies student
```

### Workflow 3: End of Day

```
1. Staff navigates to Cash > Collection
2. System shows today's summary
3. Reviews all transactions
4. For cash: Counts physical cash
5. Enters closing balance
6. System calculates difference (if any)
7. Notes any discrepancy
8. Clicks "Close Register"
9. Generates deposit slip
10. Prints daily summary report
```

### Workflow 4: Send Fee Reminders

```
1. Staff navigates to Outstanding > Dues List
2. Filters by criteria (age, program, etc.)
3. Selects multiple students (checkbox)
4. Clicks "Send Reminder"
5. Chooses channel (SMS/Email/Both)
6. Reviews message template
7. Confirms send
8. System logs all reminders sent
```

---

## 5. Component Specifications

### Student Search Box

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  🔍  Search by ID, Name, or Phone...                                          [F2]     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

- Keyboard shortcut: F2
- Autocomplete after 2 characters
- Shows: Name, ID, Program, Pending Amount
- Handles 10,000+ records
- Response time: < 500ms
```

### Payment Mode Selector

```
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│ CASH  │ │  UPI  │ │ CARD  │ │ NEFT  │ │CHEQUE │ │  DD   │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘

- Keyboard shortcuts: 1-6
- Selected state: Blue background
- Each mode may show additional fields
```

### Amount Input

```
┌─────────────────────────────────────┐
│  ₹                       35,000    │
└─────────────────────────────────────┘

- Right-aligned
- Thousand separator
- No decimals for fees
- Maximum validation
```

### Collection Stat Card

```
┌───────────────────────────┐
│  💰 TODAY'S COLLECTION    │
│                           │
│     ₹5,25,000             │
│     ████████████░░░  66%  │
│                           │
│  Target: ₹8,00,000        │
│  Transactions: 42         │
└───────────────────────────┘
```

---

## 6. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| F1 | Help |
| F2 | Focus on search |
| F3 | New collection |
| F4 | Print last receipt |
| F5 | Refresh |
| 1-6 | Select payment mode |
| Enter | Confirm/Submit |
| Esc | Cancel/Close |
| Ctrl+P | Print |

---

## 7. Accessibility Considerations

| Requirement | Implementation |
|-------------|----------------|
| Keyboard Navigation | Full keyboard support |
| High Contrast | Amount fields prominent |
| Large Text | Important numbers larger |
| Screen Reader | ARIA labels |
| Focus Visible | Clear focus states |
| Error Feedback | Visual + audio for errors |

---

## 8. Offline Behavior

| Feature | Offline Capability |
|---------|-------------------|
| Student Search | Cached student list |
| Fee Collection | Queue transactions |
| Receipt | Generate offline receipt |
| Reports | Cached previous reports |
| Sync | Auto-sync when online |

---

## 9. Print Requirements

### Receipt Print Specifications

- Paper Size: A5 or Half-letter
- Auto-cut support
- Duplicate copy option
- Logo at top
- QR code for verification (optional)
- Student and cashier signature lines

### Report Print Specifications

- Paper Size: A4
- Landscape for wide reports
- Header with date and filters
- Footer with page numbers
- Summary at end

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Module Priority**: P1 (High)
**Primary Device**: Desktop (95%)
