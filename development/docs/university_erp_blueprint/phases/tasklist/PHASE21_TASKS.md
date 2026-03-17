# Phase 21: Custom Vue/React Frontend + PWA - Task List

## Overview
This phase implements a custom frontend using Vue.js or React (framework choice deferred) with Progressive Web App (PWA) features. The frontend is a separate multi-page application that communicates with the Frappe backend via REST API. Frappe Desk remains available for system administrators.

**Module**: University ERP
**Total Estimated Tasks**: 130
**Priority**: Medium
**Status**: In Progress (0%)

**Architecture**: Separate Frontend (Vue/React + Vite) + Frappe Backend + Desk for Admins

---

## Section A: Backend API Layer

### A1. Unified API Module Structure
- [ ] Create api/unified folder in university_erp
- [ ] Create api/unified/__init__.py file
- [ ] Create api/__init__.py if not exists

### A2. Authentication API (auth.py)
- [ ] Create api/unified/auth.py
- [ ] Implement login() API - authenticate user, return session
- [ ] Implement logout() API - clear session
- [ ] Implement get_csrf_token() API - return CSRF token for forms
- [ ] Implement get_logged_user() API - return current user details
- [ ] Implement check_session() API - validate session is active
- [ ] Implement change_password() API - password change functionality
- [ ] Implement forgot_password() API - password reset initiation

### A3. Dashboard API (dashboard.py)
- [ ] Create api/unified/dashboard.py
- [ ] Implement get_dashboard_data() API - role-based dashboard stats
- [ ] Implement get_quick_stats() API - summary statistics
- [ ] Implement get_today_schedule() API - today's classes/events
- [ ] Implement get_pending_actions() API - pending approvals/tasks
- [ ] Implement get_recent_notifications() API - latest notifications
- [ ] Implement get_announcements() API - active announcements

### A4. Common Utilities API (common.py)
- [ ] Create api/unified/common.py
- [ ] Implement get_user_profile() API - full user profile data
- [ ] Implement update_user_profile() API - update profile fields
- [ ] Implement get_user_permissions() API - user's accessible modules
- [ ] Implement get_notifications() API - paginated notifications
- [ ] Implement mark_notification_read() API - mark as read
- [ ] Implement get_file() API - secure file download

### A5. Academic API (academic.py)
- [ ] Create api/unified/academic.py
- [ ] Implement get_courses() API - user's enrolled/teaching courses
- [ ] Implement get_course_details() API - single course details
- [ ] Implement get_timetable() API - weekly/daily timetable
- [ ] Implement get_attendance_summary() API - attendance statistics
- [ ] Implement get_attendance_details() API - detailed attendance records
- [ ] Implement mark_attendance() API - faculty marks attendance
- [ ] Implement get_syllabus() API - course syllabus
- [ ] Implement get_study_materials() API - course materials

### A6. Students API (students.py)
- [ ] Create api/unified/students.py
- [ ] Implement get_student_profile() API - student details
- [ ] Implement get_enrollment_history() API - enrollment records
- [ ] Implement get_documents() API - student documents
- [ ] Implement upload_document() API - upload new document
- [ ] Implement get_academic_history() API - grades, CGPA
- [ ] Implement get_certificates() API - available certificates

### A7. Finance API (finance.py)
- [ ] Create api/unified/finance.py
- [ ] Implement get_fee_structure() API - fee breakdown
- [ ] Implement get_pending_fees() API - outstanding dues
- [ ] Implement get_payment_history() API - past payments
- [ ] Implement initiate_payment() API - start payment flow
- [ ] Implement verify_payment() API - payment confirmation
- [ ] Implement get_receipt() API - download receipt
- [ ] Implement get_scholarships() API - scholarship status

### A8. HR API (hr.py)
- [ ] Create api/unified/hr.py
- [ ] Implement get_employee_profile() API - employee details
- [ ] Implement get_leave_balance() API - leave quotas
- [ ] Implement apply_leave() API - submit leave request
- [ ] Implement get_leave_history() API - past leaves
- [ ] Implement get_payslips() API - salary slips
- [ ] Implement get_attendance_log() API - punch records
- [ ] Implement get_holidays() API - holiday calendar

### A9. Exams API (exams.py)
- [ ] Create api/unified/exams.py
- [ ] Implement get_exam_schedule() API - upcoming exams
- [ ] Implement get_hall_ticket() API - generate hall ticket
- [ ] Implement get_results() API - exam results
- [ ] Implement get_grade_card() API - semester grade card
- [ ] Implement get_revaluation_status() API - revaluation requests

### A10. Placement API (placement.py)
- [ ] Create api/unified/placement.py
- [ ] Implement get_companies() API - visiting companies
- [ ] Implement get_job_postings() API - open positions
- [ ] Implement apply_for_job() API - submit application
- [ ] Implement get_application_status() API - application tracking
- [ ] Implement get_placement_stats() API - placement statistics
- [ ] Implement get_offers() API - received offers

### A11. Analytics API (analytics.py)
- [ ] Create api/unified/analytics.py
- [ ] Implement get_kpi_dashboard() API - KPI metrics
- [ ] Implement get_report_list() API - available reports
- [ ] Implement run_report() API - execute report
- [ ] Implement export_data() API - data export (CSV/Excel)
- [ ] Implement get_charts_data() API - chart data

---

## Section B: Push Notifications

### B1. User Device Token DocType
- [ ] Create user_device_token folder in university_erp/doctype
- [ ] Create user_device_token.json with fields:
  - user (Link: User, reqd)
  - token (Data, reqd, unique)
  - platform (Select: android/ios/web)
  - device_name (Data)
  - is_active (Check, default 1)
  - last_used (Datetime)
  - created_at (Datetime)
- [ ] Create user_device_token.py controller
- [ ] Create __init__.py file

### B2. Push Notification Settings DocType
- [ ] Create push_notification_settings folder (Single DocType)
- [ ] Create push_notification_settings.json with fields:
  - firebase_project_id (Data)
  - firebase_credentials_path (Data)
  - vapid_public_key (Data)
  - vapid_private_key (Password)
  - is_enabled (Check)
- [ ] Create push_notification_settings.py controller
- [ ] Create __init__.py file

### B3. Push Notification Service
- [ ] Create api/push_notifications.py
- [ ] Implement register_device() API - register FCM token
- [ ] Implement unregister_device() API - remove FCM token
- [ ] Implement MobilePushService class:
  - _initialize_firebase() method
  - send_to_device() method
  - send_to_topic() method
  - send_to_multiple_devices() method
  - subscribe_to_topic() method
  - unsubscribe_from_topic() method
- [ ] Implement send_notification_to_user() helper
- [ ] Implement send_bulk_notification() helper

---

## Section C: Hooks & Configuration

### C1. Update hooks.py
- [ ] Add Phase 21 doc_events if needed
- [ ] Add CORS configuration for frontend domain
- [ ] Add website_route_rules for API if needed

---

## Section D: Frontend Project Documentation

### D1. Frontend Setup Guide
- [ ] Create docs/frontend/README.md with:
  - Project overview
  - Architecture diagram
  - Prerequisites (Node.js, npm/yarn)
  - Setup instructions
  - Development workflow
  - Build & deployment

### D2. API Integration Guide
- [ ] Create docs/frontend/API_INTEGRATION.md with:
  - Authentication flow
  - API client setup
  - CSRF token handling
  - Error handling patterns
  - Offline queue implementation

### D3. PWA Configuration Guide
- [ ] Create docs/frontend/PWA_SETUP.md with:
  - Service Worker configuration
  - Manifest.json template
  - Caching strategies
  - Offline fallback
  - Push notification setup

### D4. Frontend Project Template
- [ ] Create docs/frontend/PROJECT_STRUCTURE.md with:
  - Folder structure for Vue.js
  - Folder structure for React
  - Vite configuration for MPA
  - Component organization
  - State management options

---

## Section E: Testing

### E1. API Tests
- [ ] Create tests folder in api/unified if not exists
- [ ] Create test_auth.py - authentication API tests
- [ ] Create test_dashboard.py - dashboard API tests
- [ ] Create test_academic.py - academic API tests
- [ ] Create test_finance.py - finance API tests
- [ ] Create test_push_notifications.py - push notification tests

---

## Summary

| Section | Total Tasks | Completed | Pending |
|---------|-------------|-----------|---------|
| A. Backend API Layer | 55 | 0 | 55 |
| B. Push Notifications | 15 | 0 | 15 |
| C. Hooks & Configuration | 3 | 0 | 3 |
| D. Frontend Documentation | 12 | 0 | 12 |
| E. Testing | 5 | 0 | 5 |
| **Total** | **90** | **0** | **90** |

**Completion: 0%**

---

## Implementation Notes

### Backend Focus
This phase focuses primarily on creating a robust API layer that the frontend can consume. The actual frontend (Vue/React) will be in a separate project.

### API Design Principles
1. All APIs are RESTful and return JSON
2. Authentication via Frappe session cookies
3. CSRF protection for POST requests
4. Role-based access control enforced server-side
5. Pagination for list endpoints
6. Consistent error response format

### Frontend Project (Separate)
The frontend is a separate project that will be:
- Built with Vite (React or Vue)
- Multi-page application (not SPA)
- PWA-enabled with service worker
- Hosted separately or served by Frappe

---

**Created**: 2026-01-15
**Status**: In Progress (0%)
**Last Updated**: 2026-01-15
