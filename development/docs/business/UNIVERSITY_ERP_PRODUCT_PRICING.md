# University ERP — Complete Product Pricing Document

**Document Type:** Internal Strategic Pricing Reference
**Prepared By:** Senior ERP Solution Architect / Implementation Consultant
**Product:** University ERP (university_erp)
**Platform:** Frappe Framework v15 / ERPNext v15 / Frappe Education v15 / HRMS v15
**Version:** 1.0
**Date:** March 2026
**Classification:** Internal Use Only — Do Not Share with Clients

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [ERP Modules and Custom App Analysis](#3-erp-modules-and-custom-app-analysis)
4. [Product Features Summary](#4-product-features-summary)
5. [Development Scope and Phase Breakdown](#5-development-scope-and-phase-breakdown)
6. [Internal Resource Cost Assumptions](#6-internal-resource-cost-assumptions)
7. [Development Cost Breakdown](#7-development-cost-breakdown)
8. [Requirement Analysis Cost](#8-requirement-analysis-cost)
9. [Data Migration Cost](#9-data-migration-cost)
10. [Deployment and Infrastructure Cost](#10-deployment-and-infrastructure-cost)
11. [Implementation and Go-Live Support](#11-implementation-and-go-live-support)
12. [Travel and On-Site Service Charges](#12-travel-and-on-site-service-charges)
13. [AMC and Support Pricing Model](#13-amc-and-support-pricing-model)
14. [Final Product Pricing Estimate](#14-final-product-pricing-estimate)

---

## 1. Project Overview

### 1.1 Product Identity

**University ERP** is a comprehensive, production-ready university management system built as a custom Frappe application (`university_erp`). It is not a standalone product — it is a deeply integrated ERP layered on top of four major open-source frameworks:

- **Frappe Framework v15** — Core ORM, REST API, Permissions, WebSockets
- **ERPNext v15** — Financial accounting engine (GL, Payments, Accounts)
- **Frappe HRMS v15** — Human Resource and Payroll management
- **Frappe Education v15** — Base academic DocTypes (extended and overridden)

The custom `university_erp` app adds **17 specialized modules**, **147–155 custom DocTypes**, **280+ JSON schema files**, and over **13,000 lines of Python/JavaScript code** on top of this foundation.

### 1.2 System Scale (As Discovered in Codebase)

| Metric | Value |
|--------|-------|
| Custom App Name | `university_erp` |
| Total Modules | 17 |
| Custom DocTypes | 147–155 |
| JSON Schema Files (Doctypes) | 280+ |
| Python Source Files | 959 |
| JavaScript Files | 75 |
| Total Lines of Code | 13,000+ (custom app) |
| Reports | 60+ custom reports |
| Web Portals | 5 (Student, Faculty, Parent, Alumni, Placement) |
| Scheduled Tasks | 35+ automated jobs |
| External Integrations | 6 (Razorpay, PayU, SMS, WhatsApp, DigiLocker, Biometric) |
| Workflows | 4 (Leave, Faculty Evaluation, Teaching Assignment, Fee Refund) |

### 1.3 Target Client Profile

The system is designed and sized for:

- **Institution type:** College, University, or Higher Education Institution (HEI)
- **Student strength:** 500 to 5,000 students
- **Faculty strength:** 30 to 200
- **Staff:** 20 to 100
- **Regulatory context:** Indian Higher Education (UGC, NAAC, NBA, CBCS, DigiLocker)

---

## 2. System Architecture

### 2.1 Application Stack

```
┌──────────────────────────────────────────────────────────┐
│           university_erp (Custom Frappe App)             │
│  17 Modules | 155 DocTypes | 960 Python Files | 75 JS    │
│                                                          │
│  Academics | Admissions | Examinations | Finance         │
│  HR | Hostel | Transport | Library | Placement           │
│  LMS | Research | OBE | Integrations | Portals           │
│  Payments | Analytics | Notifications                   │
└──────────────────────────┬───────────────────────────────┘
                           │ requires / extends
     ┌─────────────────────┼───────────────────────┐
     ▼                     ▼                       ▼
┌─────────────┐   ┌─────────────────┐   ┌──────────────────┐
│  Education  │   │    ERPNext      │   │      HRMS        │
│  (73 DT)   │   │  (550+ DT)      │   │    (150 DT)      │
│ + Overrides │   │  GL, Accounts   │   │  Employee, Leave │
└─────────────┘   └─────────────────┘   └──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Frappe    │
                    │  Framework  │
                    └──────┬──────┘
          ┌────────────────┼──────────────┐
          ▼                ▼              ▼
     MariaDB            Redis         Nginx
     (Database)         (Cache)       (Web Server)
```

### 2.2 Override Architecture

Six core Education DocTypes are overridden with university-specific logic:

| DocType | Override Class | Key Additions |
|---------|----------------|---------------|
| Student | UniversityStudent | CGPA calc, enrollment validation, certificates |
| Program | UniversityProgram | CBCS structure, total credits, degree |
| Course | UniversityCourse | L-T-P credits, course types, prerequisites |
| Assessment Result | UniversityAssessmentResult | 10-point grading, SGPA/CGPA |
| Fees | UniversityFees | Scholarships, late fee penalties, GL integration |
| Student Applicant | UniversityApplicant | Merit calculation, eligibility checking |

### 2.3 Blocked Modules

ERPNext modules not relevant to a university context are intentionally hidden: Manufacturing, Stock, Selling, Buying, CRM, Projects, Assets, Quality, Support — ensuring a clean, context-appropriate UI for university staff.

### 2.4 Integration Architecture

| Integration | Gateway/Provider | Purpose |
|------------|-----------------|---------|
| Payment Gateway | Razorpay + PayU | Online fee collection with webhooks |
| SMS | University SMS Settings (MSG91 compatible) | OTP, fee reminders, notifications |
| WhatsApp | Meta Business API / Twilio WhatsApp | Bulk notifications, template messaging |
| Email | Frappe SMTP | System emails, fee receipts |
| DigiLocker | DigiLocker API | Digital certificate issuance |
| Biometric | BioSync compatible | Attendance device sync |

### 2.5 Portals and Web Access

| Portal | URL | Users | Pages |
|--------|-----|-------|-------|
| Student Portal | /student-portal | Students | 14 pages |
| Faculty Portal | /faculty-portal | Faculty | 5 pages |
| Parent Portal | /parent-portal | Parents/Guardians | 2 pages |
| Alumni Portal | /alumni-portal | Graduates | 1 page |
| Placement Portal | /placement-portal | Students | 1 page |

---

## 3. ERP Modules and Custom App Analysis

### 3.1 Module Inventory

#### Module 1: Academics
**Purpose:** CBCS-compliant course management, timetable, and academic workflow
**DocTypes:** Course Registration, Course Registration Item, Course Prerequisite, Elective Course Group, Elective Course Group Item, Teaching Assignment, Timetable Slot, University Classroom
**Key Features:** CBCS credit system, L-T-P credit calculation, elective selection, prerequisite validation, classroom conflict detection, faculty-course assignment
**Automation:** Attendance threshold alerts, CGPA calculation updates

#### Module 2: Admissions
**Purpose:** End-to-end student admission lifecycle management
**DocTypes:** Admission Cycle, Admission Cycle Program, Admission Criteria, Seat Matrix, Merit List, Merit List Applicant
**Key Features:** Online applications, merit list generation, category-wise seat allocation (General/SC/ST/OBC/EWS), 11-state workflow, eligibility validation, Student Applicant override
**Gap Identified:** Inquiry/lead management not yet implemented; document verification automation pending

#### Module 3: Examinations
**Purpose:** University examination scheduling, hall ticket generation, and result processing
**DocTypes:** Exam Schedule, Exam Invigilator, Hall Ticket, Hall Ticket Exam, Student Transcript, Transcript Semester Result
**Key Features:** Conflict-free exam scheduling, bulk hall ticket generation, 10-point CBCS grading (O/A+/A/B+/B/C/P/F), SGPA/CGPA calculation, official transcript generation, degree classification
**Gap Identified:** Question bank, online examination platform, answer sheet tracking are planned (Phase 17) but not yet fully implemented

#### Module 4: Fees and Finance
**Purpose:** Comprehensive fee management with accounting integration
**DocTypes:** Fee Category, Fee Payment, Fee Refund, Fee Refund Deduction, Student Scholarship, Scholarship Type, Bulk Fee Generator, Bulk Fee Generator Student
**Key Features:** 18 predefined fee categories, scholarship management, late fee penalty calculation, bulk fee generation, refund workflow, GL entries in ERPNext
**Payment Integration:** Razorpay + PayU with webhooks; University Payments module handles payment gateway settings, bank reconciliation, fee category accounts

#### Module 5: Student Information System
**Purpose:** Student lifecycle and communication management
**DocTypes:** Student Status Log, University Alumni, University Announcement
**Key Features:** Student lifecycle tracking (Admission → Alumni), targeted announcements, status history logging

#### Module 6: University HR / Faculty Management
**Purpose:** Faculty profiles, workload, leave, and performance management
**DocTypes:** Faculty Profile, Faculty Attendance, Faculty Award, Faculty Performance Evaluation, Faculty Publication, Faculty Research Project, Student Feedback, Teaching Assignment, Teaching Assignment Schedule, Temporary Teaching Assignment, UGC Pay Scale, Workload Distributor, Employee Qualification, Leave Affected Course
**Key Features:** UGC pay scales, workload tracking, teaching assignment approval workflow, student feedback on faculty, performance evaluation workflow, leave integration with HRMS
**HRMS Integration:** Leave Application workflow, Employee/Department event hooks, payroll via Frappe HRMS

#### Module 7: University Hostel
**Purpose:** Hostel operations including room allocation, attendance, and mess
**DocTypes:** Hostel Building, Hostel Room, Hostel Allocation, Hostel Attendance, Hostel Attendance Record, Hostel Bulk Attendance, Hostel Maintenance Request, Hostel Mess, Hostel Room Occupant, Hostel Visitor, Mess Menu, Mess Menu Item
**Key Features:** Building/room master, gender-validated allocation, daily attendance, bulk attendance, mess menu management, maintenance request tracking, visitor log, fee integration
**Reports:** Hostel Occupancy, Hostel Attendance, Room Availability, Visitor Log

#### Module 8: University Transport
**Purpose:** Fleet and student transport management
**DocTypes:** Transport Route, Transport Route Stop, Transport Vehicle, Transport Allocation, Transport Trip Log
**Key Features:** Route/stop management, vehicle fleet tracking, student allocation with capacity check, trip logging with odometer validation, transport fee integration
**Reports:** Route-wise Students, Vehicle Utilization, Transport Fee Collection

#### Module 9: University Library
**Purpose:** Library catalog and circulation management
**DocTypes:** Library Article, Library Category, Library Subject, Library Member, Library Transaction, Library Fine, Book Reservation
**Key Features:** Book catalog with availability, member registration, issue/return/renew, fine calculation, book reservations, expiry notifications
**Reports:** Library Circulation, Overdue Books, Library Collection, Member Borrowing History

#### Module 10: Training and Placement
**Purpose:** Campus recruitment and placement management
**DocTypes:** Placement Company, Placement Drive, Placement Job Opening, Placement Application, Placement Round, Industry Type, Job Eligible Program, Student Resume, Resume Education, Resume Project, Resume Skill
**Key Features:** Company database, drive management, round-wise interview tracking, eligibility checking, resume builder with auto-fill, bulk operations, placement statistics
**Reports:** Placement Statistics, Company Wise Placement, Program Wise Placement, Placement Trend

#### Module 11: Learning Management System (LMS)
**Purpose:** Online course content delivery and assessment
**DocTypes:** LMS Course, LMS Course Module, LMS Content, LMS Content Progress, LMS Assignment, Assignment Submission, Submission File, Assignment Rubric Item, Submission Rubric Score, LMS Quiz, Quiz Question, Quiz Answer, Quiz Attempt, LMS Discussion, Discussion Reply
**Key Features:** Course content upload, assignment creation with rubric grading, online quizzes, discussion forums, progress tracking, completion reports
**Reports:** Course Progress, Assignment Submission Report, Quiz Analytics

#### Module 12: University Research
**Purpose:** Research project, publication, and grant management
**DocTypes:** Research Project, Research Publication, Research Grant, Research Team Member, Grant Utilization, Publication Author, Project Publication Link
**Key Features:** Research project tracking, publication records, grant management with utilization tracking, team collaboration, patent tracking
**Reports:** Faculty Research Output, Grant Utilization Report, Publication Statistics

#### Module 13: Outcome-Based Education (OBE)
**Purpose:** NAAC/NBA accreditation support through CO-PO mapping
**DocTypes:** Course Outcome, Program Outcome, Program Educational Objective, CO-PO Mapping, CO-PO Mapping Entry, CO Attainment, CO Direct Attainment, CO Indirect Attainment, CO Final Attainment, PO Attainment, PO Attainment Entry, PO Final Entry, PO Indirect Entry, PO-PEO Mapping, OBE Survey, Survey Template, Survey Question Item, Survey PO Rating
**Key Features:** CO-PO mapping matrix, direct/indirect attainment calculation, NAAC criterion progress, survey-based indirect attainment
**Reports:** CO Attainment Report, CO-PO Mapping Matrix, PO Attainment Report, Program Attainment Summary, NAAC Criterion Progress, NIRF Parameter Report

#### Module 14: University Integrations
**Purpose:** External system connectivity hub
**DocTypes:** Biometric Device, Biometric Attendance Log, Certificate Template, Certificate Field, Certificate Request, DigiLocker Settings, DigiLocker Document Type, DigiLocker Issued Document, SMS Template, SMS Queue, SMS Log, University SMS Settings, WhatsApp Settings, WhatsApp Template, WhatsApp Template Button, WhatsApp Log, Push Notification Settings, Push Notification Log, User Device Token, Email Queue Extended, Payment Gateway Settings, Payment Transaction
**Key Features:** Biometric attendance sync, bulk certificate generation, DigiLocker API integration, SMS/WhatsApp bulk messaging, push notification support
**Reports:** SMS Delivery Report, Certificate Issuance Report, Communication Analytics

#### Module 15: University Portals
**Purpose:** Alumni and job posting management portal
**DocTypes:** Alumni (Portal), Alumni Donation, Alumni Event, Alumni Event Registration, Alumni News, Announcement, Job Posting, Placement Application (Portal), Placement Drive (Portal), Placement Profile

#### Module 16: University Payments
**Purpose:** Payment gateway management and bank reconciliation
**DocTypes:** Razorpay Settings, PayU Settings, Payment Order, Bank Transaction, University Accounts Settings, Fee Category Account, Fee Refund (Payments), Webhook Log
**Key Features:** Razorpay + PayU integration, webhook handling, bank reconciliation, payment transaction reporting
**Reports:** Payment Transaction Report, Daily Collection Report, Gateway Reconciliation Report, Refund Report

#### Module 17: Notifications and Analytics (Core Module)
**Purpose:** System-wide notification and analytics engine
**Scheduled Tasks:** 35+ daily/weekly/monthly automated jobs including:
- Fee reminders and overdue notices
- Library overdue alerts
- CGPA updates
- WhatsApp counter resets
- Exam status updates and reminders
- Grievance SLA checks
- KPI calculations and dashboard updates
- NAAC data collection

---

## 4. Product Features Summary

### 4.1 Complete Feature Matrix

| Feature Category | Feature | Status |
|-----------------|---------|--------|
| **Admissions** | Online applications, merit list, seat matrix | ✅ Implemented |
| **Admissions** | Lead/inquiry management | ❌ Gap |
| **Academics** | CBCS, L-T-P credits, course registration | ✅ Implemented |
| **Academics** | Timetable scheduling | ✅ Implemented |
| **Examinations** | Hall tickets, exam schedule, transcripts | ✅ Implemented |
| **Examinations** | Online exam platform, question bank | ⚠️ Partial (Planned) |
| **Fees** | Fee structure, scholarships, bulk generation | ✅ Implemented |
| **Fees** | Online payment (Razorpay/PayU) | ✅ Implemented |
| **Finance** | GL integration, bank reconciliation | ✅ Implemented |
| **HR** | Faculty profiles, workload, UGC scales | ✅ Implemented |
| **HR** | Payroll (via HRMS) | ✅ Implemented |
| **Hostel** | Room allocation, attendance, mess, maintenance | ✅ Implemented |
| **Transport** | Routes, fleet, student allocation | ✅ Implemented |
| **Library** | Catalog, circulation, fines, reservations | ✅ Implemented |
| **Placement** | Companies, drives, applications, resume | ✅ Implemented |
| **LMS** | Content, assignments, quizzes, discussions | ✅ Implemented |
| **Research** | Projects, publications, grants | ✅ Implemented |
| **OBE** | CO-PO mapping, attainment, NAAC reports | ✅ Implemented |
| **Portals** | Student portal (14 pages), Faculty (5), Parent, Alumni | ✅ Implemented |
| **Notifications** | Email, SMS, WhatsApp, Push | ✅ Implemented |
| **Integrations** | Razorpay, PayU, DigiLocker, Biometric | ✅ Implemented |
| **Mobile/PWA** | Responsive design, PWA manifest | ✅ Implemented |
| **Analytics** | 60+ reports, dashboards, KPIs | ✅ Implemented |
| **Accreditation** | NAAC/NBA/NIRF report generation | ✅ Implemented |

### 4.2 Functional Completeness

Based on gap analysis document (`IMPLEMENTATION_GAP_ANALYSIS.md`):

| Category | Documented Features | Implemented | Gap |
|----------|-------------------|-------------|-----|
| DocTypes | 150+ | 147 | ~2% |
| Portal Pages | 25+ | 23 | ~8% |
| Workflows | 15 | 6 | 60% |
| External Integrations (Live) | 15+ | 6 (with stubs) | ~60% |
| Mobile Features (PWA) | 8+ | Partial | ~40% |
| **Overall System** | **100%** | **~75%** | **~25%** |

> **Implementation Note:** The remaining 25% gaps are mostly advanced features (question bank, full online exam platform, complete mobile native app, automated document verification) — these represent opportunities for phased delivery to clients.

---

## 5. Development Scope and Phase Breakdown

The product was built across **22 documented phases**. Each phase is mapped below with its scope, complexity, and effort rationale.

### 5.1 Phase Summary Table

| Phase | Module/Feature | Complexity | Notes |
|-------|---------------|------------|-------|
| Phase 1 | Foundation & Core Setup | High | App scaffolding, config, base roles |
| Phase 2 | Admissions & Student Info | High | Admission lifecycle, merit lists |
| Phase 3 | Academics (CBCS) | Very High | Credit system, timetable, course reg |
| Phase 4 | Examinations & Results | High | Hall tickets, grading, transcripts |
| Phase 5 | Fees & Finance | Very High | Fee engine, GL integration, refunds |
| Phase 6 | HR & Faculty | High | Workload, evaluation, UGC pay |
| Phase 7 | Hostel, Transport, Library, Placement | Very High | 4 independent modules in one phase |
| Phase 8 | Integrations & Deployment | High | DevOps, API wiring |
| Phase 9 | Hostel Complete | Medium | Extended hostel features |
| Phase 10 | LMS & Research | High | 2 feature-rich modules |
| Phase 11 | OBE & Accreditation | Very High | CO-PO, NAAC, NBA |
| Phase 12 | Integrations & Certificates | High | DigiLocker, Biometric, SMS |
| Phase 13 | Portals & Mobile | Very High | 5 web portals + PWA |
| Phase 14 | Payment Integration | High | Razorpay + PayU + webhooks |
| Phase 15 | Communication & Notifications | Medium | WhatsApp, SMS, push, email |
| Phase 16 | Inventory & Asset | Medium | Low stock, maintenance tracking |
| Phase 17 | Examination Question Bank | Very High | Online exams (partial) |
| Phase 18 | Grievance & Feedback | Medium | SLA tracking, student feedback |
| Phase 19 | Analytics & MIS | High | Dashboards, KPIs, scheduled reports |
| Phase 20 | Accreditation & Compliance | High | NAAC, NIRF full compliance |
| Phase 21 | Mobile PWA | Medium | PWA enhancement |
| Phase 22 | Deployment & Infrastructure | High | Docker, Nginx, VPS/Cloud setup |

---

## 6. Internal Resource Cost Assumptions

### 6.1 Developer Profile

**Role:** Senior ERPNext / Frappe Developer + Implementation Consultant
**Tool:** Claude Code Max subscription (AI-assisted development)

### 6.2 Salary Assumption

**Actual developer cost: ₹5,000/month**

This reflects the actual cost in our specific setup — a single developer working on the project at a fixed monthly engagement rate (freelance / intern / junior associate model), with AI tooling (Claude Code Max) serving as the primary productivity multiplier that makes this rate viable for delivering enterprise-grade ERP work.

### 6.3 Cost Per Unit (Developer)

| Period | Calculation | Cost |
|--------|------------|------|
| Monthly | Fixed engagement rate | ₹5,000 |
| Weekly | ₹5,000 ÷ 4.33 weeks | ₹1,155 |
| Daily | ₹5,000 ÷ 22 working days | ₹227 |
| Hourly | ₹227 ÷ 8 hours | ₹28 |

### 6.4 AI Tooling Cost (Claude Code Max)

| Tool | Cost |
|------|------|
| Claude Code Max Subscription | ₹25,000/month |
| Per hour (160 hrs/month) | ₹156/hour |

### 6.5 All-In Hourly Rate

Development cost is exactly two components: developer engagement cost and the Claude Code Max subscription. No other overhead is included.

| Component | Monthly | Per Hour (160 hrs/month) |
|-----------|---------|--------------------------|
| Developer Cost | ₹5,000 | ₹31 |
| Claude Code Max Subscription | ₹25,000 | ₹156 |
| **Total** | **₹30,000** | **₹187** |

> **Billing Rate Used in All Calculations: ₹190/hour** (rounded up for simplicity)

> **Key Insight:** The all-in development cost is only ₹30,000/month — meaning the product delivers extremely high margin relative to the market price charged to clients. The Claude Code Max subscription (₹25,000) is the dominant cost component, not the developer salary.

---

## 7. Development Cost Breakdown

### 7.1 Assumption: Delivering This Product to a New Client

When deploying this ERP product for a new university client, the following development effort is required — even though the core product already exists. Each client requires:

- Configuration for their specific data (programs, courses, fee structures)
- Custom fields, roles, and permissions per institution
- Integration setup (payment gateway, SMS, DigiLocker accounts)
- Portal branding and customization
- Testing on client data
- Deployment and infrastructure setup

The table below separates **base product development** (already done, to be amortized) from **per-client implementation effort**.

---

### 7.2 Phase-wise Development Cost — Base Product (Already Built)

This is the total investment already made to build the system from scratch. This is **amortized** across clients.

| Phase | Module | Estimated Hours | Rate (₹/hr) | Total Cost (₹) |
|-------|--------|-----------------|------------|----------------|
| Phase 1 | Foundation, Setup, Core Config | 80 | 190 | 15,200 |
| Phase 2 | Admissions & Student Info Module | 120 | 190 | 22,800 |
| Phase 3 | Academics / CBCS Module | 160 | 190 | 30,400 |
| Phase 4 | Examinations & Results | 120 | 190 | 22,800 |
| Phase 5 | Fees & Finance Module | 150 | 190 | 28,500 |
| Phase 6 | HR & Faculty Management | 130 | 190 | 24,700 |
| Phase 7 | Hostel + Transport + Library + Placement | 200 | 190 | 38,000 |
| Phase 9 | Complete Hostel Module | 80 | 190 | 15,200 |
| Phase 10 | LMS & Research | 140 | 190 | 26,600 |
| Phase 11 | OBE & Accreditation | 160 | 190 | 30,400 |
| Phase 12 | Integrations & Certificates | 120 | 190 | 22,800 |
| Phase 13 | Portals & Mobile (5 portals) | 200 | 190 | 38,000 |
| Phase 14 | Payment Gateway Integration | 80 | 190 | 15,200 |
| Phase 15 | Communication & Notifications | 80 | 190 | 15,200 |
| Phase 16 | Inventory & Asset Management | 60 | 190 | 11,400 |
| Phase 17 | Examination Question Bank (partial) | 100 | 190 | 19,000 |
| Phase 18 | Grievance & Feedback | 60 | 190 | 11,400 |
| Phase 19 | Analytics & MIS | 80 | 190 | 15,200 |
| Phase 20 | Accreditation Compliance | 80 | 190 | 15,200 |
| Phase 21 | Mobile / PWA | 60 | 190 | 11,400 |
| Phase 22 | Deployment & Infrastructure | 80 | 190 | 15,200 |
| **Documentation & Testing** | QA, Docs | 100 | 190 | 19,000 |
| **Bug Fixes & Iterations** | Debugging | 100 | 190 | 19,000 |
| **TOTAL** | | **2,540 hours** | | **₹4,82,600** |

> **Total Base Product Investment: ₹4,82,600 (~₹4.83 Lakhs)**

---

### 7.3 Per-Client Implementation Development Effort

This is the development/configuration work done for each new client engagement.

| Task | Description | Hours | Rate | Cost (₹) |
|------|-------------|-------|------|---------|
| Client-specific configuration | Programs, courses, fee heads, academic year setup | 24 | 190 | 4,560 |
| Custom field adjustments | Client-requested field additions/changes | 16 | 190 | 3,040 |
| Role and permission setup | Department roles, custom workflows | 12 | 190 | 2,280 |
| Payment gateway configuration | Razorpay/PayU account linking, testing | 8 | 190 | 1,520 |
| SMS/WhatsApp integration setup | Gateway credentials, template approval | 8 | 190 | 1,520 |
| Email and SMTP setup | DKIM, SPF, template branding | 4 | 190 | 760 |
| Report customization | Client-specific report fields | 16 | 190 | 3,040 |
| Portal branding | Logo, color scheme, institution name | 12 | 190 | 2,280 |
| DigiLocker / Biometric setup | API keys, device config | 8 | 190 | 1,520 |
| Testing (client env) | End-to-end functional testing | 32 | 190 | 6,080 |
| Debugging (client-specific issues) | Environment and data edge cases | 16 | 190 | 3,040 |
| **TOTAL** | | **156 hours** | | **₹29,640** |

> **Per-Client Development and Configuration: ~₹30,000 (internal cost)**

---

## 8. Requirement Analysis Cost

### 8.1 What This Covers

Requirement analysis is the discovery phase — understanding the client's unique processes before any implementation begins. For a university, this includes understanding:

- Academic program structure (semester/annual, CBCS/legacy)
- Fee structure complexity (number of components, scholarships, installments)
- Existing processes to be replaced or integrated
- Departmental workflows and approvals
- Existing data in Excel/legacy systems
- Regulatory requirements (NAAC, NIRF, UGC compliance)
- Custom features requested by the client

### 8.2 Requirement Analysis Activities

| Activity | Description | Hours | Rate | Cost (₹) |
|----------|-------------|-------|------|---------|
| Initial discovery meeting | Understand institution, size, modules needed | 4 | 190 | 760 |
| Stakeholder interviews | Meet department heads, accounts, hostel wardens | 12 | 190 | 2,280 |
| Business process mapping | Document current workflows, approval chains | 20 | 190 | 3,800 |
| ERP gap analysis | Compare client needs vs standard product | 12 | 190 | 2,280 |
| Fee structure analysis | Map all fee heads, categories, installments | 8 | 190 | 1,520 |
| Data audit | Review existing Excel/legacy data quality | 8 | 190 | 1,520 |
| Requirement document writing | Formal FRS/BRS document | 16 | 190 | 3,040 |
| Implementation planning | Phased rollout plan, go-live timeline | 8 | 190 | 1,520 |
| Proposal and sign-off | Client review and approval | 4 | 190 | 760 |
| **TOTAL** | | **92 hours** | | **₹17,480** |

> **Requirement Analysis Cost: ₹17,480 (~₹18,000 internal cost)**

> **Note:** This cost is typically billed separately as a "pre-implementation consulting fee" even if the client does not proceed with development. It is non-refundable.

---

## 9. Data Migration Cost

### 9.1 Scope of Data Migration

University data migration involves multiple data categories:

- Student master records (with personal, academic, guardian info)
- Historical results and mark sheets
- Fee ledger and payment history
- Employee / faculty records
- Library catalog
- Asset register
- Chart of accounts setup

### 9.2 Data Migration Effort

| Task | Description | Hours | Rate | Cost (₹) |
|------|-------------|-------|------|---------|
| Data audit and assessment | Inspect existing Excel/legacy DB structures | 8 | 190 | 1,520 |
| Excel template preparation | Create import templates for all entities | 12 | 190 | 2,280 |
| Student master migration | Clean, map, validate, import student records | 20 | 190 | 3,800 |
| Academic history migration | Historical results, grade sheets | 16 | 190 | 3,040 |
| Fee history migration | Previous year payments, outstanding records | 16 | 190 | 3,040 |
| Employee/faculty migration | HR records, qualifications, pay details | 12 | 190 | 2,280 |
| Chart of accounts setup | GL accounts, cost centers, opening balances | 12 | 190 | 2,280 |
| Library catalog import | Books, journals, members | 8 | 190 | 1,520 |
| Data validation scripts | Write Python scripts to validate imported data | 16 | 190 | 3,040 |
| Migration dry run | Test migration on staging server | 12 | 190 | 2,280 |
| Issue resolution | Data correction cycles (typically 2-3 rounds) | 16 | 190 | 3,040 |
| Final migration and verification | Production migration with sign-off | 8 | 190 | 1,520 |
| **TOTAL** | | **156 hours** | | **₹29,640** |

> **Data Migration Cost: ~₹30,000 (internal cost)**

### 9.3 Complexity Scaling

| Institution Size | Students | Complexity | Internal Cost Est. |
|-----------------|---------|-----------|-------------------|
| Small College | < 500 | Low | ₹15,000 – ₹20,000 |
| Medium College | 500–2,000 | Medium | ₹25,000 – ₹35,000 |
| Large University | 2,000–5,000 | High | ₹35,000 – ₹55,000 |
| Multi-campus | 5,000+ | Very High | ₹55,000 – ₹90,000 |

---

## 10. Deployment and Infrastructure Cost

### 10.1 On-Premise Deployment

#### 10.1.1 Server Requirements (Client-Provided Hardware)

| Component | Minimum Spec | Recommended Spec |
|-----------|-------------|-----------------|
| Server CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 200 GB SSD | 500 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Network | 1 Gbps LAN | 1 Gbps + Static IP |

#### 10.1.2 On-Premise Implementation Effort

| Task | Hours | Rate | Cost (₹) |
|------|-------|------|---------|
| Server OS preparation and hardening | 4 | 190 | 760 |
| Frappe bench installation (Docker/native) | 6 | 190 | 1,140 |
| App installation and site creation | 4 | 190 | 760 |
| Nginx reverse proxy configuration | 2 | 190 | 380 |
| SSL certificate setup (Let's Encrypt) | 2 | 190 | 380 |
| Backup configuration (scheduled + remote) | 4 | 190 | 760 |
| Email relay configuration | 2 | 190 | 380 |
| Security hardening (firewall, fail2ban) | 4 | 190 | 760 |
| Redis and supervisor configuration | 2 | 190 | 380 |
| Final system testing | 4 | 190 | 760 |
| **TOTAL** | **34 hours** | | **₹6,460** |

> **On-Premise Deployment Effort: ₹6,460 (~₹6,500 internal cost)**
> *(Client provides and manages their own hardware; our cost is only for setup effort)*

---

### 10.2 Cloud Deployment

#### 10.2.1 Cloud Provider Options and Hosting Costs

Based on the infrastructure analysis in [/workspace/development/docs/architecture/06_CLOUD_INFRASTRUCTURE.md](docs/architecture/06_CLOUD_INFRASTRUCTURE.md):

**Option A: AWS (Production Grade) — Recommended**

| Component | Specification | Monthly (₹) |
|-----------|--------------|-------------|
| EC2 t3.medium (Reserved 1yr) | 2 vCPU, 4GB RAM | ₹2,000 |
| RDS MariaDB db.t3.small | 2 vCPU, 2GB, 20GB | ₹1,700 |
| ElastiCache Redis | cache.t3.micro | ₹1,000 |
| S3 Storage | 150 GB | ₹300 |
| Application Load Balancer | Standard | ₹1,500 |
| Data Transfer (100GB) | Outbound | ₹750 |
| SES + SMS | 18,000 emails/month | ₹500 |
| Domain + SSL | Route 53 | ₹100 |
| CloudFlare Pro (optional) | CDN + DDoS | ₹1,700 |
| **Total** | | **₹9,550/month** |
| **Annual Total** | | **₹1,14,600/year** |

**Option B: DigitalOcean (Cost Effective)**

| Component | Specification | Monthly (₹) |
|-----------|--------------|-------------|
| Droplet 4GB | 2 vCPU, 4GB RAM, 80GB SSD | ₹2,000 |
| Managed MySQL | 1GB RAM, 10GB | ₹1,250 |
| Managed Redis | 1GB | ₹1,250 |
| Spaces Object Storage | 250GB + 1TB transfer | ₹420 |
| Load Balancer | Basic | ₹1,000 |
| CloudFlare Free | CDN | ₹0 |
| **Total** | | **₹5,920/month** |
| **Annual Total** | | **₹71,040/year** |

**Option C: E2E Networks (Recommended for Indian Universities)**

| Component | Specification | Monthly (₹) |
|-----------|--------------|-------------|
| C2.Medium Node | 2 vCPU, 4GB RAM, 60GB SSD | ₹1,500 |
| C2.Small Worker | 1 vCPU, 2GB RAM, 40GB SSD | ₹750 |
| Managed MySQL | 2GB RAM, 50GB | ₹1,200 |
| Block Storage | 100GB SSD | ₹500 |
| Object Storage | 200GB | ₹200 |
| Load Balancer | Basic | ₹500 |
| **Total** | | **₹4,650/month** |
| **Annual Total** | | **₹55,800/year** |

> **E2E Networks is recommended** for Indian universities due to:
> - Data residency in India (IT Act, PDPB compliance)
> - 40–60% cheaper than AWS/DigitalOcean
> - Indian GST invoicing (Input tax credit available)

**Option D: Starter VPS (Small Colleges, < 500 students)**

| Provider | Specification | Monthly ($) | Monthly (₹) |
|----------|--------------|------------|------------|
| Hetzner CPX31 | 4 vCPU, 8GB, 160GB | $15 | ₹1,250 |
| DigitalOcean Spaces | Object storage | $5 | ₹420 |
| CloudFlare Free | CDN | $0 | ₹0 |
| **Total** | | **$20** | **₹1,670/month** |

#### 10.2.2 Cloud Deployment Setup Effort

| Task | Hours | Rate | Cost (₹) |
|------|-------|------|---------|
| Server provisioning and configuration | 4 | 190 | 760 |
| Docker compose / Frappe setup | 6 | 190 | 1,140 |
| Domain DNS and SSL configuration | 2 | 190 | 380 |
| Automated backup setup (S3/Spaces) | 3 | 190 | 570 |
| Monitoring setup (UptimeRobot/Grafana) | 3 | 190 | 570 |
| Security configuration | 3 | 190 | 570 |
| Staging environment setup | 4 | 190 | 760 |
| Final performance testing | 4 | 190 | 760 |
| **TOTAL** | **29 hours** | | **₹5,510** |

> **Cloud Deployment Setup: ₹5,510 (~₹5,500 internal cost)**

#### 10.2.3 Hosting Cost to Client (Monthly Billing Models)

We resell/manage hosting for clients. Our recommended billing:

| Hosting Tier | Client Size | Infrastructure Used | Our Billing to Client | Our Cost | Our Margin |
|-------------|------------|--------------------|-----------------------|----------|------------|
| Starter | < 500 students | Single VPS (Hetzner) | ₹3,500/month | ₹1,670 | ₹1,830 |
| Standard | 500–2,000 students | E2E Networks | ₹7,500/month | ₹4,650 | ₹2,850 |
| Professional | 2,000–5,000 students | DigitalOcean | ₹12,000/month | ₹5,920 | ₹6,080 |
| Enterprise | 5,000+ students | AWS | ₹20,000/month | ₹9,550 | ₹10,450 |

> This hosting margin contributes to ongoing support, monitoring, and server management costs.

---

## 11. Implementation and Go-Live Support

### 11.1 User Training

| Training Type | Audience | Duration | Format | Cost (₹) |
|--------------|---------|---------|--------|---------|
| Admin Training | System Administrator (1–2 persons) | 8 hours | Live online | 1,520 |
| Accounts/Finance Training | Finance department (3–5 persons) | 4 hours | Live online | 760 |
| HR/Faculty Training | HR dept + Faculty coordinators (5–10) | 4 hours | Live online | 760 |
| Student Affairs Training | Admissions, Exam cell (5–10 persons) | 4 hours | Live online | 760 |
| Portal Usage Training | Faculty representatives (5–10) | 2 hours | Recorded video | 380 |
| End User Materials | User manuals, PDF guides | — | Documentation | 1,900 |
| **TOTAL TRAINING COST** | | **22 hrs + docs** | | **₹6,080** |

> **Total Training Internal Cost: ₹6,080 (~₹6,000)**

### 11.2 Configuration and Go-Live Activities

| Activity | Hours | Rate | Cost (₹) |
|----------|-------|------|---------|
| Final system configuration review | 8 | 190 | 1,520 |
| UAT (User Acceptance Testing) support | 16 | 190 | 3,040 |
| Issue resolution during UAT | 12 | 190 | 2,280 |
| Go-live day monitoring and support | 8 | 190 | 1,520 |
| Post go-live support (first 2 weeks) | 16 | 190 | 3,040 |
| **TOTAL GO-LIVE SUPPORT** | **60 hours** | | **₹11,400** |

---

## 12. Travel and On-Site Service Charges

### 12.1 Assumptions

- Developer based in a Tier-2 city (e.g., Pune, Nagpur, Ahmedabad)
- Client may be within city, within state, or in another state
- Travel charged at actuals for outstation; local travel at flat rate
- On-site work charged at a premium over remote rates

### 12.2 On-Site Rate Card

| Service | Rate | Unit | Notes |
|---------|------|------|-------|
| Remote developer support | ₹190 | Per hour | Internal cost rate |
| On-site developer support (on-site premium) | ₹300 | Per hour | ~60% premium for physical presence |
| Full day on-site consulting | ₹2,400 | Per day | 8 hours × ₹300 |
| Half day on-site consulting | ₹1,350 | Half day | 4.5 hours × ₹300 |
| Local travel (within city) | ₹500 | Flat per visit | Petrol + parking |
| Petrol reimbursement (outstation self-drive) | ₹12 | Per km | ₹95/L fuel ÷ ~8 km/L (approx.) |
| Outstation travel allowance | ₹1,500 | Per day | DA (daily allowance) |
| Intercity train/bus (economic) | Actuals | Per trip | Billed at actuals |
| Flight travel | Actuals + 10% | Per trip | Admin overhead |
| Hotel accommodation | ₹2,500 – ₹4,000 | Per night | Budget to mid-range |

### 12.3 Sample On-Site Visit Estimates (Internal Cost)

| Scenario | Days On-Site | Travel | Accommodation | Total Internal Cost |
|----------|-------------|--------|---------------|---------------------|
| Same city: 1-day training | 1 day | ₹500 local | — | ₹2,900 |
| Within 200 km: 2-day implementation | 2 days | ₹2,400 (200km×₹12) | ₹2,500 | ₹9,700 |
| Outstation flight: 3-day go-live support | 3 days | ₹8,000 (flight) | ₹9,000 | ₹24,200 |

> **Standard Policy:** First 3 months of remote support are included. On-site visits are charged separately per above rates.

---

## 13. AMC and Support Pricing Model

### 13.1 Why AMC Is Critical

Post-go-live, the institution will need:
- Bug fixes from ERPNext/Frappe version updates
- Minor configuration changes as policies change
- System monitoring and uptime management
- Database backup management
- Security patches
- Staff turnover — retraining of new admin users

### 13.2 AMC Tiers

---

#### Tier 1: Basic Support Plan — "Maintenance"

**Best for:** Small colleges with stable requirements and basic needs.

| Component | Detail |
|-----------|--------|
| Response Time | 48 business hours |
| Support Channel | Email only |
| Coverage Hours | Mon–Fri, 10 AM – 5 PM |
| Bug Fixes | Critical bugs only |
| Minor Config Changes | 2 hours/month included |
| Version Updates | Twice a year |
| System Monitoring | Not included |
| On-site Visits | Not included |

| Duration | Price |
|----------|-------|
| Monthly | ₹5,000/month |
| Annual AMC | ₹50,000/year (save ₹10,000) |

---

#### Tier 2: Priority Support Plan — "Support+"

**Best for:** Mid-size colleges actively using multiple modules with regular workflow changes.

| Component | Detail |
|-----------|--------|
| Response Time | 24 business hours |
| Support Channel | Email + WhatsApp |
| Coverage Hours | Mon–Sat, 9 AM – 7 PM |
| Bug Fixes | Critical + major bugs |
| Minor Config Changes | 8 hours/month included |
| Feature Tweaks | Minor enhancements included |
| Version Updates | Quarterly |
| System Monitoring | Basic uptime monitoring |
| On-site Visits | 1 visit/year included |
| Hosting Management | Included if hosted by us |

| Duration | Price |
|----------|-------|
| Monthly | ₹12,000/month |
| Annual AMC | ₹1,20,000/year (save ₹24,000) |

---

#### Tier 3: Enterprise Support Plan — "Dedicated"

**Best for:** Universities with high user volume, multiple departments, and evolving requirements.

| Component | Detail |
|-----------|--------|
| Response Time | 8 business hours (critical: 4 hours) |
| Support Channel | Email + WhatsApp + Phone |
| Coverage Hours | Mon–Sat, 8 AM – 9 PM |
| Bug Fixes | All bugs (critical, major, minor) |
| Minor Config Changes | 20 hours/month included |
| Feature Enhancements | Up to 2 small features/quarter |
| Version Updates | Monthly |
| System Monitoring | 24×7 uptime + alert monitoring |
| On-site Visits | 3 visits/year included |
| Hosting Management | Included (managed cloud) |
| Database Backups | Daily + weekly offsite |
| Emergency Support | 24×7 emergency contact |
| Dedicated Account Manager | Yes |

| Duration | Price |
|----------|-------|
| Monthly | ₹25,000/month |
| Annual AMC | ₹2,50,000/year (save ₹50,000) |

---

### 13.3 AMC Tier Comparison

| Feature | Basic | Priority | Enterprise |
|---------|-------|---------|-----------|
| Monthly Price | ₹5,000 | ₹12,000 | ₹25,000 |
| Annual Price | ₹50,000 | ₹1,20,000 | ₹2,50,000 |
| Response Time | 48 hrs | 24 hrs | 4–8 hrs |
| Included Hours/Month | 2 hrs | 8 hrs | 20 hrs |
| System Monitoring | ❌ | Basic | 24×7 |
| On-site Visits | ❌ | 1/year | 3/year |
| Emergency Support | ❌ | ❌ | ✅ |

### 13.4 Additional / Out-of-Scope Support

Work beyond included hours is billed at (these are **client-facing billable rates**, not internal cost):

| Service | Billable Rate to Client |
|---------|------------------------|
| Remote developer support | ₹500/hour |
| On-site developer support | ₹800/hour |
| New feature development | ₹500/hour (min 8 hours) |
| Custom report development | ₹5,000–₹15,000 per report |
| New integration (payment gateway, etc.) | ₹20,000–₹50,000 per integration |
| Emergency out-of-hours support | ₹1,000/hour |

---

## 14. Final Product Pricing Estimate

### 14.1 Cost Components Summary

> **Important:** The columns below show **internal cost** (what it costs us at ₹190/hr). Client-facing prices in Section 14.2 include substantial margin.

#### 14.1.1 One-Time Internal Costs Per Client

| Component | Small College (<500 students) | Medium College (500–2000) | Large University (2000–5000) |
|-----------|------------------------------|--------------------------|------------------------------|
| Base Product (amortized) | ₹48,260 | ₹48,260 | ₹48,260 |
| Requirement Analysis | ₹12,000 | ₹18,000 | ₹25,000 |
| Client Configuration & Dev | ₹20,000 | ₹30,000 | ₹45,000 |
| Data Migration | ₹15,000 | ₹30,000 | ₹55,000 |
| Deployment Setup | ₹5,500 | ₹6,500 | ₹6,500 |
| User Training | ₹4,000 | ₹6,000 | ₹10,000 |
| Go-Live Support | ₹8,000 | ₹11,400 | ₹18,000 |
| **TOTAL INTERNAL COST** | **₹1,12,760** | **₹1,50,160** | **₹2,07,760** |

#### 14.1.2 Recurring Internal Costs Per Client (Annual)

| Component | Small College | Medium College | Large University |
|-----------|-------------|---------------|-----------------|
| Hosting (cloud infra) | ₹20,040/yr | ₹55,800/yr | ₹71,040/yr |
| AMC labour (2/8/20 hrs/mo × ₹190 × 12) | ₹4,560/yr | ₹18,240/yr | ₹45,600/yr |
| **TOTAL ANNUAL INTERNAL** | **₹24,600/yr** | **₹74,040/yr** | **₹1,16,640/yr** |

---

### 14.2 Recommended Client Pricing (With Margin)

The above cost estimates already include a reasonable profit margin on developer time. Below are the **recommended client-facing prices** for standard packages.

---

#### Package A — Foundation Package (Small College)

**Best for:** Degree colleges, polytechnics, small private colleges
**Student strength:** Up to 500 students

**Modules included:**
- Student Information System
- Admissions Management
- Academic Management (CBCS)
- Fee Management + Payment Gateway
- Examinations & Results + Transcripts
- Faculty Management + Leave
- Student Portal + Faculty Portal
- Notification System (Email + SMS)

| Item | Price |
|------|-------|
| One-time implementation fee | ₹4,00,000 |
| Annual AMC (Basic) | ₹50,000/year |
| Hosting (Starter VPS) | ₹42,000/year (₹3,500/month) |
| **Year 1 Total** | **₹4,92,000** |
| **Year 2 onwards (Annual)** | **₹92,000/year** |

---

#### Package B — Standard Package (Medium College)

**Best for:** Engineering colleges, arts/science colleges, management institutes
**Student strength:** 500–2,000 students

**Modules included:** All Foundation Package modules plus:
- Hostel Management
- Library Management
- Transport Management
- Training & Placement
- HR Full Suite (Payroll, Performance)
- Parent Portal + Alumni Portal
- Reports and Analytics Dashboard

| Item | Price |
|------|-------|
| One-time implementation fee | ₹7,50,000 |
| Annual AMC (Priority) | ₹1,20,000/year |
| Hosting (Standard Cloud) | ₹90,000/year (₹7,500/month) |
| **Year 1 Total** | **₹9,60,000** |
| **Year 2 onwards (Annual)** | **₹2,10,000/year** |

---

#### Package C — Professional Package (Large University)

**Best for:** Universities, deemed universities, multi-department institutions
**Student strength:** 2,000–5,000 students

**Modules included:** All Standard Package modules plus:
- Learning Management System (LMS)
- Research Management
- Outcome-Based Education (OBE) / NAAC/NBA
- WhatsApp Integration
- DigiLocker Integration
- Biometric Attendance Integration
- Online Examination (Partial Phase 17)
- Grievance Management
- Communication Analytics
- Full Accreditation Reports

| Item | Price |
|------|-------|
| One-time implementation fee | ₹12,00,000 |
| Annual AMC (Enterprise) | ₹2,50,000/year |
| Hosting (Professional Cloud) | ₹1,44,000/year (₹12,000/month) |
| **Year 1 Total** | **₹15,94,000** |
| **Year 2 onwards (Annual)** | **₹3,94,000/year** |

---

#### Package D — Enterprise / Multi-Campus

**Best for:** Universities with multiple campuses or 5,000+ students

Pricing: **Custom Quote** — typically ₹20,00,000 to ₹40,00,000 one-time + ₹5,00,000–₹8,00,000 annual.

---

### 14.3 Cost-to-Revenue Analysis

#### For Package B (Standard) as baseline example:

| Component | Our Internal Cost | Client Price | Gross Margin | Margin % |
|-----------|-----------------|-------------|-------------|---------|
| Requirement Analysis | ₹18,000 | ₹75,000 | ₹57,000 | 76% |
| Base Product (amortized, 10 clients) | ₹48,260 | ₹2,00,000 | ₹1,51,740 | 76% |
| Client Config & Dev | ₹30,000 | ₹1,25,000 | ₹95,000 | 76% |
| Data Migration | ₹30,000 | ₹1,00,000 | ₹70,000 | 70% |
| Deployment | ₹6,500 | ₹25,000 | ₹18,500 | 74% |
| Training | ₹6,000 | ₹25,000 | ₹19,000 | 76% |
| Go-live Support | ₹11,400 | ₹25,000 | ₹13,600 | 54% |
| **TOTAL ONE-TIME** | **₹1,50,160** | **₹7,50,000** | **₹5,99,840** | **~80%** |
| Hosting (annual) | ₹55,800 | ₹90,000 | ₹34,200 | 38% |
| AMC labour (annual) | ₹18,240 | ₹1,20,000 | ₹1,01,760 | 85% |
| **ANNUAL RECURRING** | **₹74,040** | **₹2,10,000** | **₹1,35,960** | **~65%** |

> **Year 1 gross margin: ~80%** — exceptionally high due to low developer cost (₹5k/month)
> **Year 2+ gross margin: ~65%** — driven by AMC at 85% margin and hosting at 38% margin
> **This is the core business advantage:** total internal cost is ₹30,000/month; product charges ₹7.5L+ per client.

---

### 14.4 Product Amortization Logic

The ₹4,82,600 base product investment is amortized based on number of clients:

| Clients | Amortization Per Client | Break-even Status |
|---------|------------------------|--------------------|
| 1 client | ₹4,82,600 | Product cost recovered in first deal |
| 2 clients | ₹2,41,300 | Profitable from client 2 |
| 5 clients | ₹96,520 | Near-zero product cost |
| 10 clients | ₹48,260 | Negligible — pure profit |

> **Target:** The product fully pays for itself with the **very first Package B or C client**. Every subsequent client is nearly pure margin on the product component.

---

### 14.5 Additional Revenue Opportunities

| Service | Price Range |
|---------|-----------|
| Custom report development | ₹5,000 – ₹20,000/report |
| New feature development | ₹500/hr (min ₹8,000) |
| Extra integrations (custom payment, ERP link) | ₹25,000 – ₹75,000 |
| Mobile app (React Native / Flutter wrapper) | ₹1,50,000 – ₹3,00,000 |
| Online examination platform (full Phase 17) | ₹1,00,000 – ₹2,00,000 |
| Multi-language support (regional language UI) | ₹50,000 – ₹1,00,000 |
| Data analytics dashboard (Power BI / Metabase) | ₹50,000 – ₹1,50,000 |
| Hostel-only standalone system (per gap analysis) | ₹3,00,000 – ₹5,00,000 |

---

### 14.6 Complete Pricing Summary Card

```
┌────────────────────────────────────────────────────────────────────┐
│              UNIVERSITY ERP — PRICING SUMMARY                      │
├────────────────────────────────────────────────────────────────────┤
│  PACKAGE A — Foundation (< 500 students)                           │
│  One-time: ₹4,00,000 | Annual: ₹92,000 | Year 1 Total: ₹4,92,000  │
├────────────────────────────────────────────────────────────────────┤
│  PACKAGE B — Standard (500–2,000 students)                         │
│  One-time: ₹7,50,000 | Annual: ₹2,10,000 | Year 1: ₹9,60,000      │
├────────────────────────────────────────────────────────────────────┤
│  PACKAGE C — Professional (2,000–5,000 students)                   │
│  One-time: ₹12,00,000 | Annual: ₹3,94,000 | Year 1: ₹15,94,000    │
├────────────────────────────────────────────────────────────────────┤
│  PACKAGE D — Enterprise (5,000+ or Multi-campus)                   │
│  Custom Quote: ₹20,00,000 – ₹40,00,000 + ₹5,00,000–8,00,000/yr   │
├────────────────────────────────────────────────────────────────────┤
│  INTERNAL COST RATE: ₹190/hour (₹5k dev + ₹25k Claude ÷ 160hrs)  │
│  ON-SITE COST RATE: ₹300/hour                                      │
│  TRAVEL: ₹12/km + ₹1,500 DA + actuals                             │
├────────────────────────────────────────────────────────────────────┤
│  AMC TIERS:                                                        │
│  Basic: ₹5,000/month | Priority: ₹12,000/month | Enterprise: ₹25,000│
└────────────────────────────────────────────────────────────────────┘
```

---

## Appendix A — Assumptions and Disclaimers

1. **Developer cost is ₹5,000/month** — a fixed engagement rate (freelance / junior associate). Claude Code Max serves as the primary productivity multiplier enabling enterprise-grade ERP delivery at this rate.

2. **Claude Code Max at ₹25,000/month** is the dominant cost component (₹25k vs ₹5k developer). If multiple clients are served simultaneously, this cost is shared and per-client cost reduces further.

3. **Hosting costs** are based on March 2026 pricing from E2E Networks, DigitalOcean, and AWS. These vary with exchange rates (for USD-priced providers).

4. **Development hours** for the base product (Phase 1–22) are estimates based on code volume, complexity, and documented implementation status. Actual developer effort may differ ±20%.

5. **Data migration effort** scales with data quality. Poor legacy data (inconsistent Excel formats, missing fields) can increase effort by 50–100%.

6. **SMSes and WhatsApp messages** are not included in hosting costs. Clients are billed at actuals for third-party SMS/WhatsApp gateway charges (approximately ₹0.15–₹0.25/SMS).

7. **Razorpay/PayU transaction fees** (typically 2% of transaction value) are borne by the client institution and are not included in any package price.

8. **GST (18%)** is applicable on all software services, implementation fees, and AMC. All prices above are exclusive of GST unless stated otherwise.

9. **This pricing model assumes the system is deployed for a single institution on a dedicated environment.** SaaS multi-tenant pricing would be structured differently.

---

## Appendix B — Competitive Context

Indian University ERP market has several established players. Our competitive positioning:

| Vendor | Price Range (One-time) | Notes |
|--------|----------------------|-------|
| Generic ERPNext Implementors | ₹2,00,000 – ₹8,00,000 | Standard ERPNext without university customization |
| SIMS / Fedena / iCloudEMS | ₹3,00,000 – ₹15,00,000 | Proprietary, limited customization |
| SAP ERP for Education | ₹50,00,000 – ₹2,00,00,000 | Enterprise, overkill for mid-size |
| Oracle PeopleSoft | ₹1,00,00,000+ | Large universities only |
| **Our University ERP** | **₹4,00,000 – ₹12,00,000** | Open-source base, fully customizable, India-specific |

**Our Advantage:**
- Indian-context features built-in (CBCS, NAAC, NBA, DigiLocker, UPI payments)
- Open-source foundation (no vendor lock-in)
- Frappe framework — extensible by any Python developer
- AI-assisted development = faster feature delivery
- Competitive pricing with enterprise-grade features

---

*Document prepared based on analysis of actual codebase at `/workspace/development/frappe-bench/apps/university_erp/`, documentation at `/workspace/development/docs/`, and infrastructure analysis at `/workspace/development/docs/architecture/`. All costs are in Indian Rupees (₹). Valid for internal planning purposes as of March 2026.*
