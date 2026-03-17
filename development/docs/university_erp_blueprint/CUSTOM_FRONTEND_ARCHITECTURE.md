# Custom Frontend Architecture for University ERP

## Document Purpose

This document explains the complete architecture of implementing a custom Vue.js/React frontend for the University ERP system. It covers how the frontend connects to the Frappe backend, authentication flows, data access patterns, and integration with base ERPNext modules (Education, HRMS, Accounts).

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Diagrams](#2-architecture-diagrams)
3. [Authentication & Session Management](#3-authentication--session-management)
4. [API Communication Patterns](#4-api-communication-patterns)
5. [Accessing Base ERPNext Modules](#5-accessing-base-erpnext-modules)
6. [Data Flow Examples](#6-data-flow-examples)
7. [Frontend Project Structure](#7-frontend-project-structure)
8. [Deployment Options](#8-deployment-options)
9. [Security Considerations](#9-security-considerations)
10. [PWA Integration](#10-pwa-integration)

---

## 1. System Overview

### Current State
```
┌─────────────────────────────────────────────────────────────┐
│                    FRAPPE DESK UI                            │
│                                                              │
│   • Cluttered interface with many modules                   │
│   • Same UI for all users (admin, student, faculty)         │
│   • Not optimized for end-user experience                   │
│   • Desktop-focused design                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRAPPE BACKEND                            │
│                                                              │
│   Education │ HRMS │ ERPNext │ University_ERP (Custom)      │
└─────────────────────────────────────────────────────────────┘
```

### Proposed State
```
┌─────────────────────────────────────────────────────────────┐
│              CUSTOM FRONTEND (Vue/React)                     │
│                                                              │
│   • Clean, modern UI                                        │
│   • Role-based interfaces                                   │
│   • Mobile-first, responsive                                │
│   • PWA enabled (offline, installable)                      │
└─────────────────────────────────────────────────────────────┘
          │                                    │
          │ (Regular Users)                    │ (Admins Only)
          ▼                                    ▼
┌──────────────────────┐          ┌──────────────────────┐
│   REST API Layer     │          │   FRAPPE DESK UI     │
│                      │          │                      │
│ /api/method/*        │          │ /app                 │
│ /api/resource/*      │          │ System Config        │
└──────────────────────┘          └──────────────────────┘
          │                                    │
          └────────────────┬───────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRAPPE BACKEND                            │
│                                                              │
│   Education │ HRMS │ ERPNext │ University_ERP (Custom)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Diagrams

### 2.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER DEVICES                                    │
│                                                                              │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│    │ Desktop  │    │  Tablet  │    │  Mobile  │    │   PWA    │           │
│    │ Browser  │    │ Browser  │    │ Browser  │    │  (Installed)         │
│    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘           │
│         │               │               │               │                  │
│         └───────────────┴───────────────┴───────────────┘                  │
│                                   │                                         │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    │ HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND SERVER                                    │
│                     (Nginx / CDN / Frappe Static)                           │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    CUSTOM FRONTEND APP                               │   │
│   │                    (Vue.js or React + Vite)                          │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                      PAGES                                   │   │   │
│   │   │                                                              │   │   │
│   │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │   │   │
│   │   │  │  Login  │ │Dashboard│ │Academic │ │ Finance │           │   │   │
│   │   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │   │   │
│   │   │                                                              │   │   │
│   │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │   │   │
│   │   │  │   HR    │ │  Exams  │ │Placement│ │Analytics│           │   │   │
│   │   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                   SHARED COMPONENTS                          │   │   │
│   │   │                                                              │   │   │
│   │   │  Sidebar │ Header │ DataTable │ Forms │ Charts │ Modals    │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                    API CLIENT                                │   │   │
│   │   │                                                              │   │   │
│   │   │  • Session management (cookies)                             │   │   │
│   │   │  • CSRF token handling                                      │   │   │
│   │   │  • Request/Response interceptors                            │   │   │
│   │   │  • Error handling                                           │   │   │
│   │   │  • Offline queue                                            │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                    PWA LAYER                                 │   │   │
│   │   │                                                              │   │   │
│   │   │  Service Worker │ Manifest │ Offline Cache │ Push Notify   │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API Calls
                                    │ (HTTPS + Session Cookie + CSRF)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRAPPE BACKEND                                     │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         API LAYER                                    │   │
│   │                                                                      │   │
│   │   ┌───────────────────────────────────────────────────────────┐     │   │
│   │   │              UNIFIED APIs (university_erp)                 │     │   │
│   │   │                                                            │     │   │
│   │   │  /api/method/university_erp.api.unified.auth.*            │     │   │
│   │   │  /api/method/university_erp.api.unified.dashboard.*       │     │   │
│   │   │  /api/method/university_erp.api.unified.academic.*        │     │   │
│   │   │  /api/method/university_erp.api.unified.finance.*         │     │   │
│   │   │  /api/method/university_erp.api.unified.hr.*              │     │   │
│   │   └───────────────────────────────────────────────────────────┘     │   │
│   │                                                                      │   │
│   │   ┌───────────────────────────────────────────────────────────┐     │   │
│   │   │              GENERIC FRAPPE CLIENT APIs                    │     │   │
│   │   │                                                            │     │   │
│   │   │  /api/method/frappe.client.get                            │     │   │
│   │   │  /api/method/frappe.client.get_list                       │     │   │
│   │   │  /api/method/frappe.client.insert                         │     │   │
│   │   │  /api/method/frappe.client.save                           │     │   │
│   │   │  /api/method/frappe.client.delete                         │     │   │
│   │   └───────────────────────────────────────────────────────────┘     │   │
│   │                                                                      │   │
│   │   ┌───────────────────────────────────────────────────────────┐     │   │
│   │   │              BASE MODULE APIs                              │     │   │
│   │   │                                                            │     │   │
│   │   │  /api/method/education.education.api.*                    │     │   │
│   │   │  /api/method/hrms.api.*                                   │     │   │
│   │   │  /api/method/erpnext.accounts.*                           │     │   │
│   │   └───────────────────────────────────────────────────────────┘     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      BUSINESS LOGIC LAYER                            │   │
│   │                                                                      │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │   │
│   │   │  EDUCATION  │  │    HRMS     │  │   ERPNEXT   │                │   │
│   │   │   Module    │  │   Module    │  │  Accounts   │                │   │
│   │   │             │  │             │  │             │                │   │
│   │   │ • Student   │  │ • Employee  │  │ • Account   │                │   │
│   │   │ • Course    │  │ • Leave     │  │ • Payment   │                │   │
│   │   │ • Program   │  │ • Payroll   │  │ • Invoice   │                │   │
│   │   │ • Fees      │  │ • Attendance│  │ • Journal   │                │   │
│   │   │ • Schedule  │  │ • Expense   │  │ • Budget    │                │   │
│   │   └─────────────┘  └─────────────┘  └─────────────┘                │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                 UNIVERSITY_ERP (Custom)                      │   │   │
│   │   │                                                              │   │   │
│   │   │  Admission │ Examination │ Hostel │ Transport │ Placement   │   │   │
│   │   │  Library │ OBE/Accreditation │ Grievance │ Analytics        │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        DATA LAYER                                    │   │
│   │                                                                      │   │
│   │                      MariaDB / MySQL                                │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │  tabStudent │ tabEmployee │ tabAccount │ tabFees │ ...      │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Request/Response Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         REQUEST/RESPONSE FLOW                                 │
└──────────────────────────────────────────────────────────────────────────────┘

  FRONTEND                    FRAPPE API                    DATABASE
     │                            │                            │
     │  1. User clicks "View Fees"                            │
     │                            │                            │
     │  2. API Request            │                            │
     │  ─────────────────────────>│                            │
     │  POST /api/method/frappe.client.get_list               │
     │  Headers:                  │                            │
     │    Cookie: sid=abc123      │                            │
     │    X-Frappe-CSRF-Token: xyz│                            │
     │  Body:                     │                            │
     │    {                       │                            │
     │      "doctype": "Fees",    │                            │
     │      "filters": {          │                            │
     │        "student": "STU001" │                            │
     │      },                    │                            │
     │      "fields": ["name",    │                            │
     │        "amount", "due_date"│                            │
     │        "outstanding_amount"│                            │
     │      ]                     │                            │
     │    }                       │                            │
     │                            │                            │
     │                            │  3. Validate Session       │
     │                            │  ───────────────────────>  │
     │                            │  SELECT * FROM tabSessions │
     │                            │  WHERE sid = 'abc123'      │
     │                            │  <───────────────────────  │
     │                            │                            │
     │                            │  4. Check Permissions      │
     │                            │  ───────────────────────>  │
     │                            │  SELECT * FROM tabDocPerm  │
     │                            │  WHERE role IN (user_roles)│
     │                            │  <───────────────────────  │
     │                            │                            │
     │                            │  5. Execute Query          │
     │                            │  ───────────────────────>  │
     │                            │  SELECT name, amount,      │
     │                            │    due_date, outstanding   │
     │                            │  FROM tabFees              │
     │                            │  WHERE student = 'STU001'  │
     │                            │  <───────────────────────  │
     │                            │                            │
     │  6. JSON Response          │                            │
     │  <─────────────────────────│                            │
     │  {                         │                            │
     │    "message": [            │                            │
     │      {                     │                            │
     │        "name": "FEE-001",  │                            │
     │        "amount": 50000,    │                            │
     │        "due_date": "...",  │                            │
     │        "outstanding": 25000│                            │
     │      }                     │                            │
     │    ]                       │                            │
     │  }                         │                            │
     │                            │                            │
     │  7. Render UI              │                            │
     │  (Fee list displayed)      │                            │
     │                            │                            │
```

---

## 3. Authentication & Session Management

### 3.1 Login Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOGIN FLOW                                         │
└─────────────────────────────────────────────────────────────────────────────┘

   USER                    FRONTEND                   FRAPPE API
    │                         │                           │
    │  1. Enter credentials   │                           │
    │  ─────────────────────> │                           │
    │                         │                           │
    │                         │  2. POST /api/method/login│
    │                         │  ────────────────────────>│
    │                         │  {                        │
    │                         │    "usr": "student@uni.edu",
    │                         │    "pwd": "password123"   │
    │                         │  }                        │
    │                         │                           │
    │                         │                           │  3. Validate
    │                         │                           │     credentials
    │                         │                           │
    │                         │  4. Response              │
    │                         │  <────────────────────────│
    │                         │  Set-Cookie: sid=abc123;  │
    │                         │    HttpOnly; Secure       │
    │                         │  {                        │
    │                         │    "message": "Logged In",│
    │                         │    "home_page": "/app",   │
    │                         │    "full_name": "John",   │
    │                         │    "csrf_token": "xyz789" │
    │                         │  }                        │
    │                         │                           │
    │                         │  5. Store CSRF token      │
    │                         │     in memory/localStorage│
    │                         │                           │
    │                         │  6. Redirect to Dashboard │
    │  <───────────────────── │                           │
    │  Dashboard displayed    │                           │
    │                         │                           │
```

### 3.2 Session Cookie Behavior

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SESSION COOKIE DETAILS                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  COOKIE ATTRIBUTES:
  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Name:     sid                                                         │
  │  Value:    <session_id_hash>                                           │
  │  Domain:   .university.edu  (or your domain)                           │
  │  Path:     /                                                           │
  │  Expires:  Session (or configured expiry)                              │
  │  HttpOnly: true  (JavaScript cannot access)                            │
  │  Secure:   true  (HTTPS only)                                          │
  │  SameSite: Lax   (CSRF protection)                                     │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘

  IMPORTANT FOR CROSS-ORIGIN (if frontend on different domain):
  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Frontend Request must include:                                        │
  │    credentials: 'include'   // Send cookies with request               │
  │                                                                         │
  │  Backend must set CORS headers:                                        │
  │    Access-Control-Allow-Origin: https://portal.university.edu          │
  │    Access-Control-Allow-Credentials: true                              │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘
```

### 3.3 CSRF Token Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CSRF PROTECTION FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  1. LOGIN RESPONSE includes csrf_token:
     ┌─────────────────────────────────────┐
     │ {                                   │
     │   "message": "Logged In",           │
     │   "csrf_token": "abc123xyz789..."   │
     │ }                                   │
     └─────────────────────────────────────┘

  2. FRONTEND stores token:
     ┌─────────────────────────────────────┐
     │ // In memory (preferred)            │
     │ window.csrfToken = response.csrf_token;
     │                                     │
     │ // Or localStorage (less secure)    │
     │ localStorage.setItem('csrf_token',  │
     │   response.csrf_token);             │
     └─────────────────────────────────────┘

  3. EVERY POST/PUT/DELETE REQUEST includes token:
     ┌─────────────────────────────────────┐
     │ fetch('/api/method/...', {          │
     │   method: 'POST',                   │
     │   headers: {                        │
     │     'Content-Type': 'application/json',
     │     'X-Frappe-CSRF-Token': csrfToken│
     │   },                                │
     │   credentials: 'include',           │
     │   body: JSON.stringify(data)        │
     │ });                                 │
     └─────────────────────────────────────┘

  4. FRAPPE validates token against session:
     ┌─────────────────────────────────────┐
     │ if (request.headers['X-Frappe-CSRF-Token']
     │     !== session.csrf_token) {       │
     │   throw CSRFError();                │
     │ }                                   │
     └─────────────────────────────────────┘
```

---

## 4. API Communication Patterns

### 4.1 Three Ways to Access Data

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THREE API ACCESS PATTERNS                                │
└─────────────────────────────────────────────────────────────────────────────┘


  PATTERN 1: Generic Frappe Client API
  ═════════════════════════════════════

  Works with ANY DocType from ANY module:

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  // Get list of documents                                              │
  │  POST /api/method/frappe.client.get_list                               │
  │  {                                                                      │
  │    "doctype": "Student",           // From Education module            │
  │    "filters": {"enabled": 1},                                          │
  │    "fields": ["name", "student_name", "program"]                       │
  │  }                                                                      │
  │                                                                         │
  │  // Get single document                                                │
  │  POST /api/method/frappe.client.get                                    │
  │  {                                                                      │
  │    "doctype": "Employee",          // From HRMS module                 │
  │    "name": "EMP-001"                                                   │
  │  }                                                                      │
  │                                                                         │
  │  // Create new document                                                │
  │  POST /api/method/frappe.client.insert                                 │
  │  {                                                                      │
  │    "doc": {                                                            │
  │      "doctype": "Leave Application",                                   │
  │      "employee": "EMP-001",                                            │
  │      "leave_type": "Casual Leave",                                     │
  │      "from_date": "2024-01-15",                                        │
  │      "to_date": "2024-01-16"                                           │
  │    }                                                                    │
  │  }                                                                      │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘


  PATTERN 2: Module-Specific APIs
  ════════════════════════════════

  Pre-built functions in each module with business logic:

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  // Education Module APIs                                              │
  │  POST /api/method/education.education.api.get_fee_structure            │
  │  { "program": "B.Tech", "academic_term": "2024" }                      │
  │                                                                         │
  │  POST /api/method/education.education.api.get_course_schedule_events   │
  │  { "start": "2024-01-01", "end": "2024-01-31" }                        │
  │                                                                         │
  │  // HRMS Module APIs                                                   │
  │  POST /api/method/hrms.api.get_leave_balance_map                       │
  │  { "employee": "EMP-001" }                                             │
  │                                                                         │
  │  POST /api/method/hrms.api.get_attendance_calendar_events              │
  │  { "employee": "EMP-001", "from_date": "...", "to_date": "..." }       │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘


  PATTERN 3: Custom Unified APIs (RECOMMENDED)
  ═════════════════════════════════════════════

  Wrapper APIs that combine data from multiple modules:

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  // Single API call returns data from multiple modules                 │
  │  POST /api/method/university_erp.api.unified.dashboard.get_student_data
  │                                                                         │
  │  Response:                                                             │
  │  {                                                                      │
  │    "profile": { ... },           // From Education.Student             │
  │    "enrollments": [ ... ],       // From Education.Program Enrollment  │
  │    "attendance": { ... },        // From Education.Student Attendance  │
  │    "pending_fees": [ ... ],      // From Education.Fees                │
  │    "timetable": [ ... ],         // From Education.Course Schedule     │
  │    "notifications": [ ... ],     // From University_ERP.Notification   │
  │    "upcoming_exams": [ ... ]     // From University_ERP.Exam Schedule  │
  │  }                                                                      │
  │                                                                         │
  │  Benefits:                                                             │
  │  • Single network request instead of multiple                          │
  │  • Business logic handled server-side                                  │
  │  • Cleaner frontend code                                               │
  │  • Better performance                                                  │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘
```

### 4.2 API Response Formats

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     STANDARD API RESPONSE FORMATS                            │
└─────────────────────────────────────────────────────────────────────────────┘


  SUCCESS RESPONSE:
  ┌────────────────────────────────────────────────────────────────────────┐
  │  {                                                                      │
  │    "message": {                    // Actual data here                 │
  │      "name": "STU-001",                                                │
  │      "student_name": "John Doe",                                       │
  │      "program": "B.Tech CSE"                                           │
  │    }                                                                    │
  │  }                                                                      │
  │                                                                         │
  │  // For lists:                                                         │
  │  {                                                                      │
  │    "message": [                                                        │
  │      { "name": "STU-001", ... },                                       │
  │      { "name": "STU-002", ... }                                        │
  │    ]                                                                    │
  │  }                                                                      │
  └────────────────────────────────────────────────────────────────────────┘


  ERROR RESPONSE:
  ┌────────────────────────────────────────────────────────────────────────┐
  │  HTTP 403 Forbidden                                                    │
  │  {                                                                      │
  │    "exc_type": "PermissionError",                                      │
  │    "exception": "frappe.exceptions.PermissionError",                   │
  │    "_error_message": "You don't have permission to access this"        │
  │  }                                                                      │
  │                                                                         │
  │  HTTP 404 Not Found                                                    │
  │  {                                                                      │
  │    "exc_type": "DoesNotExistError",                                    │
  │    "_error_message": "Student STU-999 not found"                       │
  │  }                                                                      │
  │                                                                         │
  │  HTTP 417 Validation Error                                             │
  │  {                                                                      │
  │    "exc_type": "ValidationError",                                      │
  │    "_error_message": "From Date cannot be after To Date"               │
  │  }                                                                      │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Accessing Base ERPNext Modules

### 5.1 Module DocType Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BASE MODULE DOCTYPES OVERVIEW                             │
└─────────────────────────────────────────────────────────────────────────────┘


  EDUCATION MODULE (education app)
  ════════════════════════════════

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  MASTER DATA                    TRANSACTIONS                           │
  │  ───────────                    ────────────                           │
  │  • Student                      • Program Enrollment                   │
  │  • Program                      • Student Attendance                   │
  │  • Course                       • Assessment Plan                      │
  │  • Student Group                • Assessment Result                    │
  │  • Instructor                   • Fees                                 │
  │  • Room                         • Fee Schedule                         │
  │  • Academic Year                • Course Schedule                      │
  │  • Academic Term                                                       │
  │                                                                         │
  │  API Examples:                                                         │
  │  • frappe.client.get_list({doctype: "Student", ...})                   │
  │  • education.education.api.get_fee_structure(program, term)            │
  │  • education.education.api.mark_attendance(students, date, ...)        │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘


  HRMS MODULE (hrms app)
  ═══════════════════════

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  MASTER DATA                    TRANSACTIONS                           │
  │  ───────────                    ────────────                           │
  │  • Employee                     • Attendance                           │
  │  • Department                   • Leave Application                    │
  │  • Designation                  • Leave Allocation                     │
  │  • Leave Type                   • Expense Claim                        │
  │  • Shift Type                   • Employee Advance                     │
  │  • Holiday List                 • Salary Slip                          │
  │                                 • Shift Assignment                     │
  │                                                                         │
  │  API Examples:                                                         │
  │  • hrms.api.get_leave_balance_map(employee)                            │
  │  • hrms.api.get_attendance_calendar_events(employee, from, to)         │
  │  • hrms.api.get_expense_claims(employee)                               │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘


  ERPNEXT ACCOUNTS (erpnext app)
  ═══════════════════════════════

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  MASTER DATA                    TRANSACTIONS                           │
  │  ───────────                    ────────────                           │
  │  • Account                      • Payment Entry                        │
  │  • Cost Center                  • Journal Entry                        │
  │  • Company                      • Sales Invoice                        │
  │  • Currency                     • Purchase Invoice                     │
  │  • Mode of Payment              • Bank Transaction                     │
  │                                                                         │
  │  API Examples:                                                         │
  │  • frappe.client.get_list({doctype: "Payment Entry", ...})             │
  │  • frappe.client.get({doctype: "Account", name: "ACC-001"})            │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘


  UNIVERSITY_ERP (custom app)
  ════════════════════════════

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  MODULES                                                               │
  │  ───────                                                               │
  │  • Admission Management         • Hostel Management                    │
  │  • Examination System           • Transport Management                 │
  │  • Placement Module             • Library Integration                  │
  │  • Grievance System             • OBE & Accreditation                  │
  │  • Analytics & KPIs             • Notification System                  │
  │                                                                         │
  │  API Examples:                                                         │
  │  • university_erp.api.unified.dashboard.get_student_dashboard()        │
  │  • university_erp.api.v1.student.get_timetable(student_id)             │
  │  • university_erp.api.unified.exams.get_exam_schedule(program)         │
  │                                                                         │
  └────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Cross-Module Data Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CROSS-MODULE DATA RELATIONSHIPS                           │
└─────────────────────────────────────────────────────────────────────────────┘


                    ┌─────────────────────────────────┐
                    │           USER                   │
                    │         (Frappe)                │
                    │                                 │
                    │  email: student@uni.edu         │
                    │  roles: ["Student"]             │
                    └─────────────────────────────────┘
                                    │
                                    │ Links to
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
     ┌──────────────────────────┐    ┌──────────────────────────┐
     │        STUDENT           │    │        EMPLOYEE          │
     │      (Education)         │    │         (HRMS)           │
     │                          │    │                          │
     │  name: STU-001           │    │  name: EMP-001           │
     │  student_name: John      │    │  employee_name: Jane     │
     │  user: student@uni.edu   │    │  user_id: faculty@uni.edu│
     │  program: B.Tech CSE     │    │  department: CSE         │
     └──────────────────────────┘    └──────────────────────────┘
              │                               │
              │                               │
     ┌────────┴─────────┐            ┌────────┴─────────┐
     │                  │            │                  │
     ▼                  ▼            ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   FEES      │  │ ATTENDANCE  │  │   LEAVE     │  │  SALARY     │
│ (Education) │  │ (Education) │  │  (HRMS)     │  │   SLIP      │
│             │  │             │  │             │  │  (HRMS)     │
│ student:    │  │ student:    │  │ employee:   │  │ employee:   │
│  STU-001    │  │  STU-001    │  │  EMP-001    │  │  EMP-001    │
│ amount:     │  │ status:     │  │ leave_type: │  │ gross_pay:  │
│  50000      │  │  Present    │  │  Casual     │  │  75000      │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
       │
       │ Payment links to
       ▼
┌─────────────────────────┐
│     PAYMENT ENTRY       │
│      (ERPNext)          │
│                         │
│  party_type: Student    │
│  party: STU-001         │
│  paid_amount: 25000     │
│  mode_of_payment: UPI   │
└─────────────────────────┘
```

---

## 6. Data Flow Examples

### 6.1 Student Dashboard Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STUDENT DASHBOARD DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘


  FRONTEND                                           BACKEND
     │                                                  │
     │  User logs in as Student                         │
     │  ───────────────────────────────────────────────>│
     │                                                  │
     │  GET Dashboard Data                              │
     │  POST /api/method/university_erp.api.unified.    │
     │        dashboard.get_student_dashboard           │
     │  ───────────────────────────────────────────────>│
     │                                                  │
     │                                   ┌──────────────┴──────────────┐
     │                                   │                             │
     │                                   │  1. Get User → Student      │
     │                                   │     mapping                 │
     │                                   │                             │
     │                                   │  2. Fetch from EDUCATION:   │
     │                                   │     • Student profile       │
     │                                   │     • Program Enrollment    │
     │                                   │     • Attendance summary    │
     │                                   │     • Course Schedule       │
     │                                   │     • Fees pending          │
     │                                   │                             │
     │                                   │  3. Fetch from UNIVERSITY_ERP:
     │                                   │     • Exam schedule         │
     │                                   │     • Notifications         │
     │                                   │     • Announcements         │
     │                                   │                             │
     │                                   │  4. Combine into single     │
     │                                   │     response                │
     │                                   │                             │
     │                                   └──────────────┬──────────────┘
     │                                                  │
     │  Response:                                       │
     │  {                                               │
     │    "profile": {                                  │
     │      "name": "STU-001",                          │
     │      "student_name": "John Doe",                 │
     │      "program": "B.Tech CSE",                    │
     │      "semester": 5                               │
     │    },                                            │
     │    "attendance": {                               │
     │      "present": 85,                              │
     │      "absent": 10,                               │
     │      "percentage": 89.5                          │
     │    },                                            │
     │    "pending_fees": [                             │
     │      { "name": "FEE-001", "amount": 25000 }      │
     │    ],                                            │
     │    "today_classes": [                            │
     │      { "course": "Data Structures", "time": "9 AM" }
     │    ],                                            │
     │    "upcoming_exams": [                           │
     │      { "course": "DBMS", "date": "2024-02-15" }  │
     │    ],                                            │
     │    "notifications": [                            │
     │      { "title": "Fee Due Reminder", ... }        │
     │    ]                                             │
     │  }                                               │
     │  <───────────────────────────────────────────────│
     │                                                  │
     │  Render Dashboard UI                             │
     │                                                  │
```

### 6.2 Leave Application Flow (HRMS)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LEAVE APPLICATION FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘


  FRONTEND                                           BACKEND
     │                                                  │
     │  Step 1: Get Leave Balance                       │
     │  POST /api/method/hrms.api.get_leave_balance_map │
     │  { "employee": "EMP-001" }                       │
     │  ───────────────────────────────────────────────>│
     │                                                  │
     │  Response:                                       │
     │  {                                               │
     │    "Casual Leave": {                             │
     │      "allocated": 12,                            │
     │      "taken": 3,                                 │
     │      "balance": 9                                │
     │    },                                            │
     │    "Sick Leave": {                               │
     │      "allocated": 10,                            │
     │      "taken": 2,                                 │
     │      "balance": 8                                │
     │    }                                             │
     │  }                                               │
     │  <───────────────────────────────────────────────│
     │                                                  │
     │  Display leave balance in UI                     │
     │                                                  │
     │  Step 2: Submit Leave Application                │
     │  POST /api/method/frappe.client.insert           │
     │  {                                               │
     │    "doc": {                                      │
     │      "doctype": "Leave Application",             │
     │      "employee": "EMP-001",                      │
     │      "leave_type": "Casual Leave",               │
     │      "from_date": "2024-02-01",                  │
     │      "to_date": "2024-02-02",                    │
     │      "reason": "Personal work"                   │
     │    }                                             │
     │  }                                               │
     │  ───────────────────────────────────────────────>│
     │                                                  │
     │                                   ┌──────────────┴──────────────┐
     │                                   │                             │
     │                                   │  • Validate dates           │
     │                                   │  • Check leave balance      │
     │                                   │  • Check holiday conflicts  │
     │                                   │  • Create Leave Application │
     │                                   │  • Send notification to     │
     │                                   │    approver                 │
     │                                   │                             │
     │                                   └──────────────┬──────────────┘
     │                                                  │
     │  Response (Success):                             │
     │  {                                               │
     │    "message": {                                  │
     │      "name": "LA-00123",                         │
     │      "status": "Open",                           │
     │      "docstatus": 0                              │
     │    }                                             │
     │  }                                               │
     │  <───────────────────────────────────────────────│
     │                                                  │
     │  Show success message                            │
     │                                                  │
```

---

## 7. Frontend Project Structure

### 7.1 Multi-Page Application Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND PROJECT STRUCTURE                                │
│                    (Multi-Page Application)                                  │
└─────────────────────────────────────────────────────────────────────────────┘


  university-frontend/
  │
  ├── public/                          # Static files (copied as-is)
  │   ├── icons/                       # PWA icons
  │   │   ├── icon-72x72.png
  │   │   ├── icon-96x96.png
  │   │   ├── icon-128x128.png
  │   │   ├── icon-144x144.png
  │   │   ├── icon-152x152.png
  │   │   ├── icon-192x192.png
  │   │   ├── icon-384x384.png
  │   │   └── icon-512x512.png
  │   ├── manifest.json                # PWA manifest
  │   ├── sw.js                        # Service Worker
  │   ├── offline.html                 # Offline fallback page
  │   └── favicon.ico
  │
  ├── src/
  │   ├── api/                         # API communication layer
  │   │   ├── client.js                # Main API client class
  │   │   ├── endpoints.js             # API endpoint definitions
  │   │   ├── auth.js                  # Authentication helpers
  │   │   └── interceptors.js          # Request/response interceptors
  │   │
  │   ├── components/                  # Reusable components
  │   │   ├── layout/
  │   │   │   ├── Sidebar.vue          # Navigation sidebar
  │   │   │   ├── Header.vue           # Top header bar
  │   │   │   ├── Footer.vue           # Footer
  │   │   │   └── Layout.vue           # Main layout wrapper
  │   │   │
  │   │   ├── common/
  │   │   │   ├── DataTable.vue        # Reusable data table
  │   │   │   ├── FormBuilder.vue      # Dynamic form generator
  │   │   │   ├── Modal.vue            # Modal/dialog component
  │   │   │   ├── Card.vue             # Card component
  │   │   │   ├── Button.vue           # Button component
  │   │   │   ├── Input.vue            # Input component
  │   │   │   └── Select.vue           # Select/dropdown component
  │   │   │
  │   │   ├── charts/
  │   │   │   ├── LineChart.vue        # Line chart
  │   │   │   ├── BarChart.vue         # Bar chart
  │   │   │   ├── PieChart.vue         # Pie chart
  │   │   │   └── StatCard.vue         # Statistics card
  │   │   │
  │   │   └── pwa/
  │   │       ├── InstallPrompt.vue    # PWA install prompt
  │   │       ├── OfflineIndicator.vue # Offline status indicator
  │   │       └── UpdateNotifier.vue   # SW update notification
  │   │
  │   ├── pages/                       # Page-specific code
  │   │   ├── login/
  │   │   │   ├── main.js              # Entry point
  │   │   │   └── LoginPage.vue        # Login page component
  │   │   │
  │   │   ├── dashboard/
  │   │   │   ├── main.js
  │   │   │   ├── Dashboard.vue
  │   │   │   └── widgets/
  │   │   │       ├── AttendanceWidget.vue
  │   │   │       ├── FeesWidget.vue
  │   │   │       └── TimetableWidget.vue
  │   │   │
  │   │   ├── academic/
  │   │   │   ├── main.js
  │   │   │   ├── Academic.vue
  │   │   │   ├── Courses.vue
  │   │   │   ├── Timetable.vue
  │   │   │   └── Attendance.vue
  │   │   │
  │   │   ├── finance/
  │   │   │   ├── main.js
  │   │   │   ├── Finance.vue
  │   │   │   ├── Fees.vue
  │   │   │   ├── Payments.vue
  │   │   │   └── Receipts.vue
  │   │   │
  │   │   ├── hr/
  │   │   │   ├── main.js
  │   │   │   ├── HR.vue
  │   │   │   ├── Leave.vue
  │   │   │   ├── Attendance.vue
  │   │   │   └── Payslips.vue
  │   │   │
  │   │   ├── exams/
  │   │   │   ├── main.js
  │   │   │   ├── Exams.vue
  │   │   │   ├── Schedule.vue
  │   │   │   ├── Results.vue
  │   │   │   └── HallTicket.vue
  │   │   │
  │   │   ├── placement/
  │   │   │   ├── main.js
  │   │   │   ├── Placement.vue
  │   │   │   ├── Companies.vue
  │   │   │   └── Applications.vue
  │   │   │
  │   │   └── analytics/
  │   │       ├── main.js
  │   │       ├── Analytics.vue
  │   │       └── Reports.vue
  │   │
  │   ├── styles/
  │   │   ├── global.css               # Global styles
  │   │   ├── variables.css            # CSS variables/themes
  │   │   └── utilities.css            # Utility classes
  │   │
  │   └── utils/
  │       ├── storage.js               # localStorage/IndexedDB helpers
  │       ├── offline.js               # Offline detection
  │       ├── notifications.js         # Push notification helpers
  │       └── validators.js            # Form validators
  │
  ├── index.html                       # Login/Landing page
  ├── dashboard.html                   # Dashboard page
  ├── academic.html                    # Academic page
  ├── finance.html                     # Finance page
  ├── hr.html                          # HR page
  ├── exams.html                       # Exams page
  ├── placement.html                   # Placement page
  ├── analytics.html                   # Analytics page
  │
  ├── vite.config.js                   # Vite configuration
  ├── package.json                     # Dependencies
  └── README.md                        # Documentation
```

### 7.2 Vite Multi-Page Configuration

```javascript
// vite.config.js

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'  // or react() for React
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],

  build: {
    rollupOptions: {
      input: {
        // Each page is a separate entry point
        main: resolve(__dirname, 'index.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
        academic: resolve(__dirname, 'academic.html'),
        finance: resolve(__dirname, 'finance.html'),
        hr: resolve(__dirname, 'hr.html'),
        exams: resolve(__dirname, 'exams.html'),
        placement: resolve(__dirname, 'placement.html'),
        analytics: resolve(__dirname, 'analytics.html')
      }
    }
  },

  server: {
    proxy: {
      // Proxy API calls to Frappe backend during development
      '/api': {
        target: 'http://localhost:8000',  // Frappe dev server
        changeOrigin: true
      }
    }
  }
})
```

---

## 8. Deployment Options

### 8.1 Option A: Separate Domain (Recommended)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  OPTION A: SEPARATE DOMAIN/SUBDOMAIN                         │
└─────────────────────────────────────────────────────────────────────────────┘


  USER BROWSER
       │
       │ https://portal.university.edu
       ▼
  ┌─────────────────────────────────────┐
  │         FRONTEND SERVER             │
  │         (Nginx / CDN)               │
  │                                     │
  │  Serves: HTML, CSS, JS, Images      │
  │  Domain: portal.university.edu      │
  └─────────────────────────────────────┘
       │
       │ API calls to https://api.university.edu
       ▼
  ┌─────────────────────────────────────┐
  │         FRAPPE SERVER               │
  │                                     │
  │  API:  api.university.edu/api/*     │
  │  Desk: api.university.edu/app       │
  │                                     │
  │  CORS Headers:                      │
  │  Access-Control-Allow-Origin:       │
  │    https://portal.university.edu    │
  │  Access-Control-Allow-Credentials:  │
  │    true                             │
  └─────────────────────────────────────┘


  PROS:
  • Frontend can be served via CDN (fast, global)
  • Independent scaling of frontend and backend
  • Clear separation of concerns
  • Can use different technologies for each

  CONS:
  • CORS configuration required
  • Cookie handling more complex (SameSite)
  • Two servers to maintain
```

### 8.2 Option B: Same Domain with Path Prefix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  OPTION B: SAME DOMAIN, PATH PREFIX                          │
└─────────────────────────────────────────────────────────────────────────────┘


  USER BROWSER
       │
       │ https://university.edu/*
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                    NGINX REVERSE PROXY                       │
  │                                                              │
  │  Route /portal/*  ──────────>  Frontend Static Files         │
  │  Route /api/*     ──────────>  Frappe Backend                │
  │  Route /app/*     ──────────>  Frappe Backend (Desk)         │
  │                                                              │
  └─────────────────────────────────────────────────────────────┘
       │                              │
       ▼                              ▼
  ┌────────────────────┐    ┌────────────────────┐
  │  STATIC FILES      │    │  FRAPPE SERVER     │
  │  (Frontend Build)  │    │                    │
  │                    │    │  /api/* routes     │
  │  /portal/          │    │  /app (Desk)       │
  └────────────────────┘    └────────────────────┘


  NGINX CONFIGURATION:
  ┌────────────────────────────────────────────────────────────────────────┐
  │  server {                                                              │
  │      server_name university.edu;                                       │
  │                                                                        │
  │      # Frontend static files                                           │
  │      location /portal/ {                                               │
  │          alias /var/www/university-frontend/dist/;                     │
  │          try_files $uri $uri/ /portal/index.html;                      │
  │      }                                                                 │
  │                                                                        │
  │      # API and Desk - proxy to Frappe                                  │
  │      location / {                                                      │
  │          proxy_pass http://localhost:8000;                             │
  │          proxy_set_header Host $host;                                  │
  │          proxy_set_header X-Real-IP $remote_addr;                      │
  │      }                                                                 │
  │  }                                                                     │
  └────────────────────────────────────────────────────────────────────────┘


  PROS:
  • No CORS issues (same origin)
  • Simpler cookie handling
  • Single domain to manage

  CONS:
  • More complex Nginx configuration
  • Frontend updates require server access
```

### 8.3 Option C: Frappe Serves Frontend

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  OPTION C: FRAPPE SERVES FRONTEND                            │
└─────────────────────────────────────────────────────────────────────────────┘


  USER BROWSER
       │
       │ https://university.edu/*
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                      FRAPPE SERVER                           │
  │                                                              │
  │  ┌────────────────────────────────────────────────────────┐ │
  │  │                     www/ folder                         │ │
  │  │                                                         │ │
  │  │  Built frontend files copied here:                      │ │
  │  │  • www/portal/index.html                                │ │
  │  │  • www/portal/dashboard.html                            │ │
  │  │  • www/portal/assets/...                                │ │
  │  └────────────────────────────────────────────────────────┘ │
  │                                                              │
  │  /portal/*   → Serves from www/portal/                      │
  │  /api/*      → API endpoints                                │
  │  /app        → Frappe Desk                                  │
  │                                                              │
  └─────────────────────────────────────────────────────────────┘


  DEPLOYMENT SCRIPT:
  ┌────────────────────────────────────────────────────────────────────────┐
  │  #!/bin/bash                                                           │
  │                                                                        │
  │  # Build frontend                                                      │
  │  cd /path/to/university-frontend                                       │
  │  npm run build                                                         │
  │                                                                        │
  │  # Copy to Frappe www folder                                           │
  │  cp -r dist/* /path/to/frappe-bench/apps/university_erp/               │
  │                university_erp/www/portal/                              │
  │                                                                        │
  │  # Clear Frappe cache                                                  │
  │  cd /path/to/frappe-bench                                              │
  │  bench clear-cache                                                     │
  └────────────────────────────────────────────────────────────────────────┘


  PROS:
  • Simplest setup
  • No additional server needed
  • Same authentication mechanism
  • No CORS issues

  CONS:
  • Frontend tied to Frappe deployment
  • No CDN benefits
  • Frappe restart may be needed for updates
```

---

## 9. Security Considerations

### 9.1 Security Checklist

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SECURITY CHECKLIST                                    │
└─────────────────────────────────────────────────────────────────────────────┘


  AUTHENTICATION & SESSION
  ═════════════════════════

  ✓ Use HTTPS only (no HTTP)
  ✓ Session cookies with HttpOnly flag (prevents XSS access)
  ✓ Session cookies with Secure flag (HTTPS only)
  ✓ Session cookies with SameSite=Lax (CSRF protection)
  ✓ CSRF token validation on all POST/PUT/DELETE
  ✓ Session timeout after inactivity
  ✓ Logout clears session properly


  API SECURITY
  ════════════

  ✓ All APIs require authentication (except login)
  ✓ Role-based access control (RBAC) enforced
  ✓ Permission checks on every request
  ✓ Input validation on all parameters
  ✓ SQL injection prevention (use ORM, no raw queries)
  ✓ Rate limiting on login attempts
  ✓ API versioning for future changes


  FRONTEND SECURITY
  ══════════════════

  ✓ Content Security Policy (CSP) headers
  ✓ XSS prevention (sanitize user input)
  ✓ No sensitive data in localStorage
  ✓ CSRF token stored in memory, not localStorage
  ✓ Validate all data from API before display
  ✓ Use subresource integrity for CDN resources


  DATA PROTECTION
  ════════════════

  ✓ Passwords hashed (Frappe uses pbkdf2)
  ✓ Sensitive data encrypted at rest
  ✓ PII data access logged
  ✓ Data export requires authorization
  ✓ File uploads validated and scanned
```

### 9.2 Permission Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PERMISSION CHECK FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘


   REQUEST                     FRAPPE                      DATABASE
      │                          │                            │
      │  GET Student STU-001     │                            │
      │  ─────────────────────>  │                            │
      │                          │                            │
      │                          │  1. Validate Session       │
      │                          │  ───────────────────────>  │
      │                          │  Is session valid?         │
      │                          │  <───────────────────────  │
      │                          │  Yes, user = student@uni   │
      │                          │                            │
      │                          │  2. Get User Roles         │
      │                          │  ───────────────────────>  │
      │                          │  SELECT role FROM          │
      │                          │    tabHas Role             │
      │                          │  WHERE parent = 'student@' │
      │                          │  <───────────────────────  │
      │                          │  Roles: ["Student"]        │
      │                          │                            │
      │                          │  3. Check DocType Perm     │
      │                          │  ───────────────────────>  │
      │                          │  SELECT * FROM tabDocPerm  │
      │                          │  WHERE parent = 'Student'  │
      │                          │    AND role = 'Student'    │
      │                          │    AND read = 1            │
      │                          │  <───────────────────────  │
      │                          │  Has read permission: Yes  │
      │                          │                            │
      │                          │  4. Check User Permission  │
      │                          │  ───────────────────────>  │
      │                          │  SELECT * FROM             │
      │                          │    tabUser Permission      │
      │                          │  WHERE user = 'student@'   │
      │                          │    AND allow = 'Student'   │
      │                          │    AND for_value = 'STU-001'
      │                          │  <───────────────────────  │
      │                          │  Allowed: Yes              │
      │                          │                            │
      │  Response: Student data  │                            │
      │  <─────────────────────  │                            │
      │                          │                            │


  PERMISSION DENIED EXAMPLE:

      │  GET Student STU-002     │                            │
      │  (belongs to other user) │                            │
      │  ─────────────────────>  │                            │
      │                          │                            │
      │                          │  Check User Permission     │
      │                          │  ───────────────────────>  │
      │                          │  No permission for STU-002 │
      │                          │  <───────────────────────  │
      │                          │                            │
      │  403 Forbidden           │                            │
      │  <─────────────────────  │                            │
```

---

## 10. PWA Integration

### 10.1 PWA Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PWA ARCHITECTURE                                     │
└─────────────────────────────────────────────────────────────────────────────┘


  ┌─────────────────────────────────────────────────────────────────────────┐
  │                           BROWSER                                        │
  │                                                                          │
  │   ┌───────────────────────────────────────────────────────────────────┐ │
  │   │                      FRONTEND APP                                  │ │
  │   │                                                                    │ │
  │   │   Pages │ Components │ API Client │ State Management              │ │
  │   └───────────────────────────────────────────────────────────────────┘ │
  │                              │                                           │
  │                              │ Registers                                 │
  │                              ▼                                           │
  │   ┌───────────────────────────────────────────────────────────────────┐ │
  │   │                    SERVICE WORKER                                  │ │
  │   │                                                                    │ │
  │   │   ┌─────────────────────────────────────────────────────────────┐ │ │
  │   │   │                    CACHE STORAGE                             │ │ │
  │   │   │                                                              │ │ │
  │   │   │   ┌─────────────────┐  ┌─────────────────┐                  │ │ │
  │   │   │   │  STATIC CACHE   │  │  DYNAMIC CACHE  │                  │ │ │
  │   │   │   │                 │  │                 │                  │ │ │
  │   │   │   │  • HTML pages   │  │  • API responses│                  │ │ │
  │   │   │   │  • CSS files    │  │  • User data    │                  │ │ │
  │   │   │   │  • JS bundles   │  │  • Images       │                  │ │ │
  │   │   │   │  • Icons        │  │                 │                  │ │ │
  │   │   │   └─────────────────┘  └─────────────────┘                  │ │ │
  │   │   │                                                              │ │ │
  │   │   └─────────────────────────────────────────────────────────────┘ │ │
  │   │                                                                    │ │
  │   │   ┌─────────────────────────────────────────────────────────────┐ │ │
  │   │   │                   INDEXED DB                                 │ │ │
  │   │   │                                                              │ │ │
  │   │   │   • Offline form submissions (queue)                        │ │ │
  │   │   │   • User preferences                                        │ │ │
  │   │   │   • Cached complex data                                     │ │ │
  │   │   └─────────────────────────────────────────────────────────────┘ │ │
  │   │                                                                    │ │
  │   └───────────────────────────────────────────────────────────────────┘ │
  │                              │                                           │
  │                              │ Intercepts                                │
  │                              ▼                                           │
  │   ┌───────────────────────────────────────────────────────────────────┐ │
  │   │                    NETWORK REQUESTS                                │ │
  │   │                                                                    │ │
  │   │   Strategy: NetworkFirst for API, CacheFirst for static           │ │
  │   └───────────────────────────────────────────────────────────────────┘ │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS
                                    ▼
                           ┌─────────────────┐
                           │  FRAPPE SERVER  │
                           └─────────────────┘
```

### 10.2 Offline Functionality

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OFFLINE FUNCTIONALITY                                   │
└─────────────────────────────────────────────────────────────────────────────┘


  ONLINE MODE:
  ────────────

  User Action                    Service Worker                Network
       │                              │                           │
       │  Request Dashboard           │                           │
       │  ──────────────────────────> │                           │
       │                              │  Fetch from network       │
       │                              │  ───────────────────────> │
       │                              │  <─────────────────────── │
       │                              │  Response received        │
       │                              │                           │
       │                              │  Cache response           │
       │                              │  (for offline use)        │
       │                              │                           │
       │  Display dashboard           │                           │
       │  <────────────────────────── │                           │


  OFFLINE MODE:
  ─────────────

  User Action                    Service Worker                Network
       │                              │                           │
       │  Request Dashboard           │                           │
       │  ──────────────────────────> │                           │
       │                              │  Fetch from network       │
       │                              │  ───────────────────────> │
       │                              │        ✗ FAILED           │
       │                              │  <─────────────────────── │
       │                              │                           │
       │                              │  Fallback to cache        │
       │                              │  ┌──────────────────┐     │
       │                              │  │  CACHE STORAGE   │     │
       │                              │  │  Return cached   │     │
       │                              │  │  dashboard data  │     │
       │                              │  └──────────────────┘     │
       │                              │                           │
       │  Display cached dashboard    │                           │
       │  + "Offline" indicator       │                           │
       │  <────────────────────────── │                           │


  OFFLINE FORM SUBMISSION:
  ────────────────────────

  User Action                    Service Worker              IndexedDB
       │                              │                           │
       │  Submit Leave Application    │                           │
       │  ──────────────────────────> │                           │
       │                              │  Network check: OFFLINE   │
       │                              │                           │
       │                              │  Store in offline queue   │
       │                              │  ───────────────────────> │
       │                              │                           │
       │  "Saved offline.             │                           │
       │   Will sync when online"     │                           │
       │  <────────────────────────── │                           │
       │                              │                           │
       │  ... later, network restored │                           │
       │                              │                           │
       │                              │  Background Sync triggered│
       │                              │  <─────────────────────── │
       │                              │                           │
       │                              │  Retrieve queued items    │
       │                              │  ───────────────────────> │
       │                              │  <─────────────────────── │
       │                              │                           │
       │                              │  Submit to server         │
       │                              │  ────────────────> Network│
       │                              │  <──────────────── Success│
       │                              │                           │
       │  Notification: "Leave        │                           │
       │   application synced"        │                           │
       │  <────────────────────────── │                           │
```

### 10.3 Push Notifications Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PUSH NOTIFICATION FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘


  SETUP (One-time):
  ─────────────────

  Frontend                Service Worker              Backend                FCM
     │                         │                         │                    │
     │  Request permission     │                         │                    │
     │  ─────────────────────> │                         │                    │
     │                         │  Get FCM token          │                    │
     │                         │  ─────────────────────────────────────────> │
     │                         │  <───────────────────────────────────────── │
     │                         │  Token: abc123xyz789    │                    │
     │                         │                         │                    │
     │  Send token to backend  │                         │                    │
     │  ───────────────────────────────────────────────> │                    │
     │                         │                         │                    │
     │                         │                         │  Store token in    │
     │                         │                         │  User Device Token │
     │                         │                         │  DocType           │
     │                         │                         │                    │
     │  "Notifications enabled"│                         │                    │
     │  <─────────────────────────────────────────────── │                    │


  SENDING NOTIFICATION:
  ─────────────────────

  Trigger Event              Backend                    FCM              Device
     │                          │                        │                  │
     │  Fee payment due         │                        │                  │
     │  ─────────────────────>  │                        │                  │
     │                          │                        │                  │
     │                          │  Get user's FCM token  │                  │
     │                          │  from User Device Token│                  │
     │                          │                        │                  │
     │                          │  Send push message     │                  │
     │                          │  ─────────────────────>│                  │
     │                          │                        │                  │
     │                          │                        │  Deliver to      │
     │                          │                        │  Service Worker  │
     │                          │                        │  ───────────────>│
     │                          │                        │                  │
     │                          │                        │     ┌──────────┐ │
     │                          │                        │     │ PUSH     │ │
     │                          │                        │     │ NOTIF    │ │
     │                          │                        │     │          │ │
     │                          │                        │     │ Fee Due  │ │
     │                          │                        │     │ Rs 25000 │ │
     │                          │                        │     └──────────┘ │
     │                          │                        │                  │
```

---

## Summary

This document outlines a comprehensive architecture for building a custom Vue.js/React frontend for the University ERP system. Key takeaways:

1. **Separation of Concerns**: Frontend and backend are separate, connected via REST APIs
2. **Three API Access Methods**: Generic Frappe client, module-specific APIs, and custom unified APIs
3. **Base Module Integration**: Full access to Education, HRMS, and ERPNext modules
4. **Security**: Session-based auth with CSRF protection, role-based access control
5. **PWA Features**: Offline support, installable, push notifications
6. **Flexible Deployment**: Multiple hosting options based on requirements

The architecture maintains all existing Frappe/ERPNext functionality while providing a modern, user-friendly interface for end users.

---

**Document Version**: 1.0
**Created**: 2026-01-16
**Author**: University ERP Development Team
