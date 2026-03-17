# Phase 18: Grievance & Feedback Management System - Task List

## Overview
This phase implements a comprehensive grievance redressal and feedback management system including student grievances, faculty complaints, parent concerns, suggestion boxes, satisfaction surveys, and complaint escalation workflows.

**Module**: University ERP
**Total Estimated Tasks**: 150
**Priority**: Medium-High (Grievance & Feedback)
**Status**: Completed (100%)

---

## Section A: Grievance Core Child Tables

### A1. Grievance Attachment DocType (Child Table)
- [x] Create grievance_attachment folder in university_erp/doctype
- [x] Create grievance_attachment.json with fields:
  - file_name (Data, reqd, in_list_view)
  - file_url (Attach, reqd, in_list_view)
  - description (Small Text)
- [x] Create grievance_attachment.py controller
- [x] Create __init__.py file

### A2. Grievance Escalation Log DocType (Child Table)
- [x] Create grievance_escalation_log folder in university_erp/doctype
- [x] Create grievance_escalation_log.json with fields:
  - from_level (Int, in_list_view)
  - to_level (Int, in_list_view)
  - escalated_at (Datetime, in_list_view)
  - escalated_by (Link: User)
  - reason (Small Text)
  - previous_assignee (Link: User)
  - new_assignee (Link: User, in_list_view)
- [x] Create grievance_escalation_log.py controller
- [x] Create __init__.py file

### A3. Grievance Action DocType (Child Table)
- [x] Create grievance_action folder in university_erp/doctype
- [x] Create grievance_action.json with fields:
  - action_description (Text, reqd, in_list_view)
  - action_date (Date, in_list_view)
  - taken_by (Link: User, in_list_view)
- [x] Create grievance_action.py controller
- [x] Create __init__.py file

### A4. Grievance Communication DocType (Child Table)
- [x] Create grievance_communication folder in university_erp/doctype
- [x] Create grievance_communication.json with fields:
  - communication_type (Select: System/Response/Query/Note, in_list_view)
  - message (Text Editor, reqd, in_list_view)
  - timestamp (Datetime, in_list_view)
  - sent_by (Link: User, in_list_view)
- [x] Create grievance_communication.py controller
- [x] Create __init__.py file

### A5. Committee Member DocType (Child Table)
- [x] Create committee_member folder in university_erp/doctype
- [x] Create committee_member.json with fields:
  - user (Link: User, reqd, in_list_view)
  - member_name (Data, in_list_view)
  - role_in_committee (Select: Member/External Expert/Student Representative)
  - designation (Data)
- [x] Create committee_member.py controller
- [x] Create __init__.py file

### A6. Committee Category Link DocType (Child Table)
- [x] Create committee_category_link folder in university_erp/doctype
- [x] Create committee_category_link.json with fields:
  - category (Select: Academic/Administrative/Financial/etc, reqd, in_list_view)
- [x] Create committee_category_link.py controller
- [x] Create __init__.py file

### A7. Grievance Escalation Rule DocType (Child Table)
- [x] Create grievance_escalation_rule folder in university_erp/doctype
- [x] Create grievance_escalation_rule.json with fields:
  - level (Int, reqd, in_list_view)
  - assignee (Link: User, reqd, in_list_view)
  - days_before_escalation (Int, in_list_view)
  - auto_escalate_on_sla_breach (Check)
- [x] Create grievance_escalation_rule.py controller
- [x] Create __init__.py file

---

## Section B: Grievance Main DocTypes

### B1. Grievance Type DocType
- [x] Create grievance_type folder in university_erp/doctype
- [x] Create grievance_type.json with all fields from spec
- [x] Create grievance_type.py controller with:
  - validate() method
  - get_default_sla_date() method
- [x] Create __init__.py file

### B2. Grievance Committee DocType
- [x] Create grievance_committee folder in university_erp/doctype
- [x] Create grievance_committee.json with all fields from spec
- [x] Create grievance_committee.py controller with:
  - validate() method
  - get_active_members() method
- [x] Create __init__.py file

### B3. Grievance DocType
- [x] Create grievance folder in university_erp/doctype
- [x] Create grievance.json with all fields from spec (50+ fields)
- [x] Create grievance.py controller with:
  - validate() method
  - before_save() method
  - on_submit() method
  - update_sla_status() method
  - calculate_days_open() method
- [x] Create __init__.py file

---

## Section C: Feedback System Child Tables

### C1. Feedback Form Section DocType (Child Table)
- [x] Create feedback_form_section folder in university_erp/doctype
- [x] Create feedback_form_section.json with fields:
  - section_title (Data, reqd, in_list_view)
  - section_description (Small Text)
- [x] Create feedback_form_section.py controller
- [x] Create __init__.py file

### C2. Feedback Question DocType (Child Table)
- [x] Create feedback_question folder in university_erp/doctype
- [x] Create feedback_question.json with fields:
  - question_text (Text, reqd, in_list_view)
  - question_type (Select, reqd, in_list_view)
  - is_required (Check, in_list_view)
  - options (Small Text)
  - help_text (Small Text)
  - weightage (Float)
  - category (Data)
- [x] Create feedback_question.py controller
- [x] Create __init__.py file

### C3. Feedback Program Filter DocType (Child Table)
- [x] Create feedback_program_filter folder in university_erp/doctype
- [x] Create feedback_program_filter.json with fields:
  - program (Link: Program, reqd, in_list_view)
- [x] Create feedback_program_filter.py controller
- [x] Create __init__.py file

### C4. Feedback Department Filter DocType (Child Table)
- [x] Create feedback_department_filter folder in university_erp/doctype
- [x] Create feedback_department_filter.json with fields:
  - department (Link: Department, reqd, in_list_view)
- [x] Create feedback_department_filter.py controller
- [x] Create __init__.py file

### C5. Feedback Course Filter DocType (Child Table)
- [x] Create feedback_course_filter folder in university_erp/doctype
- [x] Create feedback_course_filter.json with fields:
  - course (Link: Course, reqd, in_list_view)
- [x] Create feedback_course_filter.py controller
- [x] Create __init__.py file

### C6. Feedback Answer DocType (Child Table)
- [x] Create feedback_answer folder in university_erp/doctype
- [x] Create feedback_answer.json with fields:
  - question_id (Data, reqd)
  - question_text (Data, in_list_view)
  - answer_value (Text, in_list_view)
- [x] Create feedback_answer.py controller
- [x] Create __init__.py file

### C7. Feedback Section Score DocType (Child Table)
- [x] Create feedback_section_score folder in university_erp/doctype
- [x] Create feedback_section_score.json with fields:
  - section_name (Data, reqd, in_list_view)
  - score (Float, in_list_view)
  - responses_count (Int)
- [x] Create feedback_section_score.py controller
- [x] Create __init__.py file

---

## Section D: Feedback Main DocTypes

### D1. Feedback Form DocType
- [x] Create feedback_form folder in university_erp/doctype
- [x] Create feedback_form.json with all fields from spec
- [x] Create feedback_form.py controller with:
  - validate() method
  - before_save() method
  - activate_form() method
  - close_form() method
  - update_statistics() method
- [x] Create __init__.py file

### D2. Feedback Response DocType
- [x] Create feedback_response folder in university_erp/doctype
- [x] Create feedback_response.json with all fields from spec
- [x] Create feedback_response.py controller with:
  - validate() method
  - before_save() method
  - calculate_scores() method
  - calculate_nps() method
- [x] Create __init__.py file

---

## Section E: Suggestion Box

### E1. Suggestion Attachment DocType (Child Table)
- [x] Create suggestion_attachment folder in university_erp/doctype
- [x] Create suggestion_attachment.json with fields:
  - file_name (Data, reqd, in_list_view)
  - file_url (Attach, reqd, in_list_view)
- [x] Create suggestion_attachment.py controller
- [x] Create __init__.py file

### E2. Suggestion DocType
- [x] Create suggestion folder in university_erp/doctype
- [x] Create suggestion.json with all fields from spec
- [x] Create suggestion.py controller with:
  - validate() method
  - before_save() method
  - upvote() method
  - downvote() method
  - approve() method
  - reject() method
- [x] Create __init__.py file

---

## Section F: Manager Classes

### F1. Grievance Manager Class
- [x] Create grievance folder in university_erp/university_erp
- [x] Create __init__.py file
- [x] Create grievance_manager.py with GrievanceManager class:
  - submit_grievance() method
  - auto_assign() method
  - send_acknowledgment() method
  - add_response() method
  - escalate() method
  - resolve() method
  - reopen() method
  - record_satisfaction() method
  - check_sla_status() method
  - get_grievance_stats() method
  - _notify_complainant() method
  - _notify_resolution() method

### F2. Feedback Manager Class
- [x] Create feedback folder in university_erp/university_erp
- [x] Create __init__.py file
- [x] Create feedback_manager.py with FeedbackManager class:
  - create_course_feedback_forms() method
  - create_standard_course_feedback() method
  - submit_response() method
  - calculate_response_scores() method
  - _get_numeric_score() method
  - _check_existing_response() method
  - update_form_statistics() method
  - _get_target_count() method
  - get_feedback_analysis() method
  - _get_question_analysis() method
  - _extract_comments() method

### F3. API Endpoints
- [x] Add get_pending_feedback_forms() API in feedback_manager.py
- [x] Add submit_feedback() API in feedback_manager.py
- [x] Add submit_grievance() API in grievance_manager.py
- [x] Add get_grievance_status() API in grievance_manager.py
- [x] Add update module __init__.py with exports

---

## Section G: Reports

### G1. Grievance Summary Report
- [x] Create grievance_summary folder in university_erp/report
- [x] Create grievance_summary.json with filters:
  - from_date (Date)
  - to_date (Date)
  - category (Select)
  - grievance_type (Link)
  - status (Select)
- [x] Create grievance_summary.py with:
  - get_columns() function
  - get_data() function
  - get_chart() function
  - get_summary() function
- [x] Create grievance_summary.js with filters

### G2. Faculty Feedback Report
- [x] Create faculty_feedback_report folder in university_erp/report
- [x] Create faculty_feedback_report.json with filters:
  - academic_term (Link)
  - department (Link)
  - faculty (Link)
- [x] Create faculty_feedback_report.py with:
  - get_columns() function
  - get_data() function
  - get_chart() function
- [x] Create faculty_feedback_report.js with filters

### G3. Feedback Analysis Report
- [x] Create feedback_analysis folder in university_erp/report
- [x] Create feedback_analysis.json with filters:
  - feedback_form (Link)
  - form_type (Select)
  - academic_term (Link)
  - from_date (Date)
  - to_date (Date)
- [x] Create feedback_analysis.py with:
  - get_columns() function
  - get_data() function
  - get_chart() function
  - get_summary() function
- [x] Create feedback_analysis.js with filters

### G4. SLA Compliance Report
- [x] Create sla_compliance_report folder in university_erp/report
- [x] Create sla_compliance_report.json with filters:
  - from_date (Date)
  - to_date (Date)
  - category (Select)
  - grievance_type (Link)
  - assigned_to (Link)
  - sla_status (Select)
- [x] Create sla_compliance_report.py with:
  - get_columns() function
  - get_data() function
  - get_chart() function
  - get_summary() function
- [x] Create sla_compliance_report.js with filters

---

## Section H: Workspace & Portal Integration

### H1. Grievance Management Workspace
- [x] Create grievance_and_feedback workspace folder
- [x] Create grievance_and_feedback.json with:
  - Shortcuts for Grievance, Grievance Type, Committee
  - Links by category
  - Report shortcuts

### H2. Student Grievance Portal Page
- [x] Create grievances/index.html in university_erp/www/student-portal
- [x] Create grievances/index.py controller
- [x] Add JavaScript for form submission and tracking

### H3. Feedback Portal Page
- [x] Create feedback/index.html in university_erp/www/student-portal
- [x] Create feedback/index.py controller
- [x] Add JavaScript for feedback form rendering

---

## Section I: Scheduled Tasks & Hooks

### I1. Scheduled Tasks
- [x] Create scheduled_tasks.py in university_erp/grievance
- [x] Implement daily_sla_check (daily)
- [x] Implement send_pending_reminders (daily)
- [x] Implement update_days_open (daily)
- [x] Implement send_feedback_reminders (daily)
- [x] Implement close_expired_feedback_forms (daily)
- [x] Implement activate_scheduled_feedback_forms (daily)
- [x] Implement update_feedback_form_statistics (daily)

### I2. Hooks Configuration
- [x] Update hooks.py with scheduler_events
- [x] Add website_route_rules for portal pages (existing)
- [x] Add doc_events for Grievance status changes (in hooks.py)

---

## Section J: Email Templates

### J1. Grievance Email Templates
- [x] Create grievance_acknowledgment.html template
- [x] Create grievance_update.html template
- [x] Create grievance_escalation.html template
- [x] Create grievance_resolved.html template
- [x] Create grievance_reminder.html template

### J2. Feedback Email Templates
- [x] Create feedback_reminder.html template
- [x] Create feedback_thank_you.html template

---

## Section K: Testing

### K1. Unit Tests
- [x] Create test_grievance.py
- [x] Create test_feedback_form.py
- [x] Create test_feedback_response.py
- [x] Create test_suggestion.py
- [x] Create __init__.py for tests module

---

## Summary

| Section | Total Tasks | Completed | Pending |
|---------|-------------|-----------|---------|
| A. Grievance Child Tables | 28 | 28 | 0 |
| B. Grievance Main DocTypes | 12 | 12 | 0 |
| C. Feedback Child Tables | 28 | 28 | 0 |
| D. Feedback Main DocTypes | 8 | 8 | 0 |
| E. Suggestion Box | 8 | 8 | 0 |
| F. Manager Classes | 20 | 20 | 0 |
| G. Reports | 16 | 16 | 0 |
| H. Workspace & Portal | 8 | 8 | 0 |
| I. Scheduled Tasks & Hooks | 10 | 10 | 0 |
| J. Email Templates | 7 | 7 | 0 |
| K. Testing | 5 | 5 | 0 |
| **Total** | **150** | **150** | **0** |

**Completion: 100%**

---

## Implementation Notes

### Files Created:
1. **Child Tables (15)**:
   - Grievance: grievance_attachment, grievance_escalation_log, grievance_action, grievance_communication, committee_member, committee_category_link, grievance_escalation_rule
   - Feedback: feedback_form_section, feedback_question, feedback_program_filter, feedback_department_filter, feedback_course_filter, feedback_answer, feedback_section_score
   - Suggestion: suggestion_attachment

2. **Main DocTypes (6)**:
   - grievance_type, grievance_committee, grievance
   - feedback_form, feedback_response
   - suggestion

3. **Manager Classes (2)**:
   - grievance_manager.py (in university_erp/grievance/)
   - feedback_manager.py (in university_erp/feedback/)

4. **Reports (4)**:
   - Grievance Summary
   - Faculty Feedback Report
   - Feedback Analysis
   - SLA Compliance Report

5. **Portal Pages (2)**:
   - grievances/index.html & index.py
   - feedback/index.html & index.py

6. **Workspace (1)**:
   - grievance_and_feedback/grievance_and_feedback.json

7. **Scheduled Tasks (1)**:
   - scheduled_tasks.py with 7 daily tasks

8. **Email Templates (7)**:
   - grievance_acknowledgment.html
   - grievance_update.html
   - grievance_escalation.html
   - grievance_resolved.html
   - grievance_reminder.html
   - feedback_reminder.html
   - feedback_thank_you.html

9. **Tests (4)**:
   - test_grievance.py
   - test_feedback_form.py
   - test_feedback_response.py
   - test_suggestion.py

---

**Created**: 2026-01-14
**Status**: Completed (100%)
**Last Updated**: 2026-01-14
