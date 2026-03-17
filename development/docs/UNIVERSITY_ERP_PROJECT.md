# University ERP - Project Documentation

**Version:** 1.0.0
**Platform:** Frappe Framework v15
**Last Updated:** January 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Implementation Status](#2-implementation-status)
3. [Technology Stack & Architecture](#3-technology-stack--architecture)
4. [Features for Clients](#4-features-for-clients)
5. [Module Details](#5-module-details)
6. [Portal Access](#6-portal-access)

---

## 1. Project Overview

University ERP is a comprehensive, modern university management system designed to handle all aspects of higher education institution management. Built on the robust Frappe Framework, it integrates seamlessly with ERPNext for financial operations, HRMS for human resource management, and extends Frappe Education for academic workflows.

### Key Highlights

| Metric | Value |
|--------|-------|
| Total Modules | 16 |
| Custom DocTypes | 147+ |
| Lines of Code | 8,265+ |
| Development Phases | 13 |
| Completed Phases | 13/13 |

### Project Goals

- Digitize all university administrative processes
- Provide role-based portals for students, faculty, parents, and alumni
- Implement CBCS (Choice Based Credit System) compliant academics
- Enable online fee collection with payment gateway integration
- Support outcome-based education (OBE) and accreditation requirements
- Mobile-responsive design with PWA capabilities

---

## 2. Implementation Status

### Phase-wise Completion Status

| Phase | Module | Status | Completion |
|-------|--------|--------|------------|
| Phase 1 | Foundation & Core Setup | Completed | 100% |
| Phase 2 | Admissions & Student Information | Completed | 100% |
| Phase 3 | Academics Module | Completed | 100% |
| Phase 4 | Examinations & Results | Completed | 100% |
| Phase 5 | Fees & Finance | Completed | 100% |
| Phase 6 | HR & Faculty Management | Completed | 100% |
| Phase 7 | Extended Modules (Hostel, Transport, Library, Placement) | Completed | 100% |
| Phase 8 | University Dashboard & Analytics | Completed | 100% |
| Phase 9 | Notification System | Completed | 100% |
| Phase 10 | API & PWA | Completed | 100% |
| Phase 11 | LMS Integration | Completed | 100% |
| Phase 12 | Integrations & Certificates | Completed | 100% |
| Phase 13 | Web Portals & Mobile Enhancement | Completed | 100% |

### Overall Progress

```
[==================================================] 100%
```

**Current Status:** Production Ready

---

## 3. Technology Stack & Architecture

### Core Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Frappe | v15+ |
| ERP Backend | ERPNext | v15+ |
| HR Module | Frappe HRMS | v15+ |
| Education Core | Frappe Education | v15+ |
| Database | MariaDB | 10.6+ |
| Cache & Queue | Redis | 6.0+ |
| Web Server | Nginx | Latest |
| Backend Language | Python | 3.11+ |
| Frontend | JavaScript, Jinja2 | ES6+ |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        University ERP                            │
│                     (Custom Frappe App)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Web        │  │   Mobile     │  │    API Gateway       │   │
│  │   Portals    │  │   PWA        │  │    (REST/GraphQL)    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                 │                      │               │
│         └─────────────────┼──────────────────────┘               │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐    │
│  │              University ERP Application Layer            │    │
│  │                                                          │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐    │    │
│  │  │Academics│ │Exams    │ │Finance  │ │Student Info │    │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────────┘    │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐    │    │
│  │  │Hostel   │ │Library  │ │Transport│ │Placement    │    │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────────┘    │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐    │    │
│  │  │LMS      │ │Research │ │OBE      │ │Integrations │    │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────────┘    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                           │                                      │
├───────────────────────────┼──────────────────────────────────────┤
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Base Applications                        │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │  Frappe     │  │  ERPNext    │  │  Frappe         │   │   │
│  │  │  Education  │  │  (Finance)  │  │  HRMS           │   │   │
│  │  │             │  │             │  │                 │   │   │
│  │  │ • Student   │  │ • GL Entry  │  │ • Employee      │   │   │
│  │  │ • Program   │  │ • Accounts  │  │ • Payroll       │   │   │
│  │  │ • Course    │  │ • Company   │  │ • Leave         │   │   │
│  │  │ • Fees      │  │ • Journal   │  │ • Attendance    │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
├───────────────────────────┼──────────────────────────────────────┤
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Frappe Framework                         │   │
│  │         (ORM, REST API, WebSocket, Background Jobs)       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
├───────────────────────────┼──────────────────────────────────────┤
│                           ▼                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  MariaDB    │  │   Redis     │  │   File Storage          │  │
│  │  Database   │  │   Cache     │  │   (Local/S3)            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### App Dependencies & Connections

```
┌─────────────────────────────────────────────────────────────┐
│                     University ERP                           │
│                    (university_erp)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬───────────────┐
          │               │               │               │
          ▼               ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ education │   │  erpnext  │   │   hrms    │   │  frappe   │
    │           │   │           │   │           │   │           │
    │ Extended: │   │ Used for: │   │ Used for: │   │ Core:     │
    │ • Student │   │ • GL      │   │ • Employee│   │ • ORM     │
    │ • Program │   │ • Accounts│   │ • Payroll │   │ • API     │
    │ • Course  │   │ • Company │   │ • Leave   │   │ • Auth    │
    │ • Fees    │   │ • Payment │   │ • Salary  │   │ • Roles   │
    │ • Results │   │ • Reports │   │ • Claims  │   │ • Perms   │
    └───────────┘   └───────────┘   └───────────┘   └───────────┘
```

### Integration Points

| Integration | Purpose | Status |
|-------------|---------|--------|
| **Razorpay** | Online fee payment | Ready |
| **SMS Gateway** | Notifications & OTP | Ready |
| **Email (SMTP)** | Communications | Ready |
| **DigiLocker** | Digital certificates | Ready |
| **Biometric** | Attendance sync | Ready |
| **LMS** | Learning management | Integrated |

---

## 4. Features for Clients

### 4.1 Admissions Management

- **Online Application Portal** - Students can apply online with document upload
- **Merit List Generation** - Automatic ranking based on marks and entrance scores
- **Seat Matrix Management** - Category-wise seat allocation (General, SC, ST, OBC, EWS)
- **Admission Cycle Management** - Multi-batch, multi-program support
- **Eligibility Validation** - Automatic eligibility checking against criteria
- **Document Verification** - Digital document submission and verification workflow

### 4.2 Academic Management

- **CBCS Implementation** - Full Choice Based Credit System support
  - 8 Course Types: Core, DSE, GE, SEC, AEC, VAC, Project, Internship
  - L-T-P Credit calculation (Lecture-Tutorial-Practical)
  - Elective course groups and selection
- **Course Registration** - Online course selection with prerequisite validation
- **Timetable Management** - Automated scheduling with conflict detection
- **Attendance Tracking** - Digital attendance with shortage alerts
- **Teaching Assignments** - Faculty workload management

### 4.3 Examination System

- **10-Point CBCS Grading**
  | Grade | Points | Marks Range |
  |-------|--------|-------------|
  | O | 10 | 90-100 |
  | A+ | 9 | 80-89 |
  | A | 8 | 70-79 |
  | B+ | 7 | 60-69 |
  | B | 6 | 50-59 |
  | C | 5 | 45-49 |
  | P | 4 | 40-44 |
  | F | 0 | Below 40 |

- **Hall Ticket Generation** - Bulk and individual with eligibility check
- **Exam Scheduling** - Conflict-free scheduling with invigilator assignment
- **Result Entry Tool** - Bulk marks entry with moderation support
- **Transcript Generation** - Official transcripts with SGPA/CGPA
- **Degree Classification** - Automatic distinction/first class calculation

### 4.4 Fee & Finance Management

- **Flexible Fee Structure** - Multiple fee categories and components
- **Online Payment** - Razorpay integration for card/UPI/NetBanking
- **Scholarship Management** - Merit and need-based scholarship tracking
- **Late Fee Calculation** - Automatic penalty computation
- **Fee Defaulter Reports** - Identify and notify defaulters
- **Refund Processing** - Structured refund workflow
- **GL Integration** - Automatic accounting entries in ERPNext

### 4.5 Student Information System

- **Complete Student Profile** - Personal, academic, and contact details
- **Student Lifecycle** - Track from admission to alumni
- **Document Management** - Store certificates and documents
- **Announcement System** - Targeted announcements by batch/program
- **Status Tracking** - Active, suspended, graduated, withdrawn

### 4.6 HR & Faculty Management

- **Faculty Profiles** - Qualifications, publications, experience
- **Teaching Workload** - Track hours and course assignments
- **Leave Management** - Online leave application and approval
- **Payroll Integration** - Salary processing via HRMS
- **Performance Evaluation** - Periodic assessment tracking

### 4.7 Hostel Management

- **Building & Room Master** - Complete hostel inventory
- **Room Allocation** - Automated and manual allocation
- **Hostel Attendance** - Daily check-in tracking
- **Mess Management** - Menu planning and subscription
- **Visitor Management** - Log and track visitors
- **Maintenance Requests** - Issue reporting and resolution

### 4.8 Library Management

- **Catalog Management** - Books, journals, e-resources
- **Member Registration** - Student and faculty members
- **Issue/Return** - Circulation management
- **Reservation System** - Book reservations
- **Fine Calculation** - Automatic overdue fines
- **Reports** - Usage and inventory reports

### 4.9 Transport Management

- **Vehicle Fleet** - Vehicle master with capacity
- **Route Management** - Define routes with stops
- **Student Allocation** - Assign students to routes
- **Trip Logging** - Track daily trips
- **Fee Integration** - Transport fee collection

### 4.10 Training & Placement

- **Company Database** - Recruiting company profiles
- **Placement Drives** - Campus recruitment events
- **Job Postings** - Internal and alumni job board
- **Student Applications** - Track application status
- **Interview Scheduling** - Round-wise scheduling
- **Placement Statistics** - Dashboards and reports

### 4.11 Learning Management System (LMS)

- **Course Content** - Upload lectures, videos, documents
- **Assignments** - Create and grade assignments
- **Quizzes** - Online assessments
- **Discussion Forums** - Student-faculty interaction
- **Progress Tracking** - Monitor student engagement

### 4.12 Research Management

- **Research Projects** - Track ongoing research
- **Publications** - Faculty publication records
- **Grant Management** - Research funding tracking
- **Team Collaboration** - Multi-member projects
- **Patent Tracking** - Intellectual property records

### 4.13 Outcome-Based Education (OBE)

- **Program Outcomes (PO)** - Define learning outcomes
- **Program Educational Objectives (PEO)** - Long-term goals
- **CO-PO Mapping** - Course outcome to PO mapping
- **Attainment Calculation** - Direct and indirect assessment
- **Accreditation Reports** - NBA/NAAC ready reports

### 4.14 Web Portals

| Portal | Users | Key Features |
|--------|-------|--------------|
| **Student Portal** | Students | Dashboard, timetable, results, fees, attendance, library, certificates |
| **Faculty Portal** | Faculty | Classes, attendance marking, grade entry, research, leave management |
| **Parent Portal** | Parents | Child's attendance, results, fees, communication with faculty |
| **Alumni Portal** | Alumni | Directory, events, job postings, donations, networking |
| **Placement Portal** | Students | Job listings, applications, interview schedules, resume builder |

### 4.15 Mobile & PWA Features

- **Responsive Design** - Works on all screen sizes
- **Progressive Web App** - Install on mobile devices
- **Offline Support** - View cached data offline
- **Push Notifications** - Real-time alerts
- **Touch Gestures** - Pull-to-refresh, swipe navigation
- **Dark Mode** - Eye-friendly dark theme

### 4.16 Reports & Analytics

- **University Dashboard** - Key performance indicators
- **Admission Analytics** - Application trends, conversion rates
- **Academic Reports** - Pass percentage, grade distribution
- **Financial Reports** - Collection status, pending fees
- **Placement Statistics** - Offer trends, salary packages
- **Custom Reports** - Build reports with Report Builder

### 4.17 Integrations & Certificates

- **Payment Gateway** - Razorpay for online payments
- **SMS Gateway** - Bulk SMS notifications
- **Email Integration** - SMTP for communications
- **DigiLocker** - Digital certificate issuance
- **Biometric** - Attendance device integration
- **Certificate Generator** - Bonafide, character, degree certificates

---

## 5. Module Details

### 5.1 All 16 Modules

| # | Module | Description | DocTypes |
|---|--------|-------------|----------|
| 1 | University ERP | Core settings and configuration | 3 |
| 2 | Academics | Courses, registration, timetable | 8 |
| 3 | Admissions | Application, merit, seat matrix | 6 |
| 4 | Student Info | Student lifecycle management | 3 |
| 5 | Examinations | Exams, results, transcripts | 6 |
| 6 | University Finance | Fees, scholarships, payments | 8 |
| 7 | University HR | Faculty, workload, evaluation | 4 |
| 8 | University Hostel | Rooms, allocation, mess | 12 |
| 9 | University Transport | Vehicles, routes, allocation | 5 |
| 10 | University Library | Catalog, circulation, fines | 7 |
| 11 | University Placement | Companies, drives, applications | 11 |
| 12 | University LMS | Content, assignments, quizzes | 8 |
| 13 | University Research | Projects, publications, grants | 7 |
| 14 | University OBE | Outcomes, attainment, mapping | 9 |
| 15 | University Integrations | Payment, SMS, certificates | 6 |
| 16 | University Portals | Student, faculty, alumni portals | 8 |

### 5.2 Education DocType Extensions

The following core Education DocTypes are extended with university-specific features:

| DocType | Extension Class | Key Enhancements |
|---------|----------------|------------------|
| Student | UniversityStudent | Enrollment validation, CGPA calculation, category certificates |
| Program | UniversityProgram | CBCS structure, total credits, degree validation |
| Course | UniversityCourse | L-T-P credits, course types, prerequisites |
| Student Applicant | UniversityApplicant | Merit calculation, eligibility checking |
| Assessment Result | UniversityAssessmentResult | 10-point grading, SGPA/CGPA |
| Fees | UniversityFees | Scholarships, penalties, GL integration |

---

## 6. Portal Access

### Access URLs

| Portal | URL Path | Required Role |
|--------|----------|---------------|
| Student Portal | `/student-portal` | Student (linked to Student record) |
| Faculty Portal | `/faculty-portal` | Faculty (linked to Instructor record) |
| Parent Portal | `/parent-portal` | Parent (linked as Guardian) |
| Alumni Portal | `/alumni-portal` | Alumni (linked to Alumni record) |
| Placement Portal | `/placement-portal` | Student with placement access |

### Student Portal Pages

| Page | URL | Features |
|------|-----|----------|
| Dashboard | `/student-portal` | Overview, quick stats, announcements |
| Timetable | `/student-portal/timetable` | Weekly class schedule |
| Results | `/student-portal/results` | Semester-wise results, CGPA |
| Fees | `/student-portal/fees` | Fee status, payment history, pay online |
| Attendance | `/student-portal/attendance` | Subject-wise attendance percentage |
| Library | `/student-portal/library` | Issued books, due dates, reservations |
| Certificates | `/student-portal/certificates` | Request bonafide, character certificates |
| Grievances | `/student-portal/grievances` | Submit and track complaints |
| Profile | `/student-portal/profile` | View/update personal details |

### Faculty Portal Pages

| Page | URL | Features |
|------|-----|----------|
| Dashboard | `/faculty-portal` | Today's classes, pending tasks |
| Attendance | `/faculty-portal/attendance` | Mark class attendance |
| Grades | `/faculty-portal/grades` | Enter assessment marks |
| Classes | `/faculty-portal/classes` | View assigned courses |
| Research | `/faculty-portal/research` | Publications, projects |
| Leave | `/faculty-portal/leave` | Apply for leave |

---

## Support & Contact

For technical support or feature requests, please contact the development team.

---

**Document Version:** 1.0.0
**Generated:** January 2026
**Platform:** Frappe Framework v15 | ERPNext v15 | Education v15 | HRMS v15
