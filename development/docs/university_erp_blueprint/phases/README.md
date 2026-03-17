# University ERP - Phase-wise Development Guide

This folder contains detailed phase-wise development documents for building the University ERP system using the **Hybrid Architecture** approach (Frappe Education + Custom Extensions).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    University ERP Frontend                       │
│              (Custom Portals, Dashboards, Reports)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  university_erp Custom App                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Override Classes (hooks.py override_doctype_class)     │   │
│  │  • UniversityStudent    • UniversityProgram             │   │
│  │  • UniversityCourse     • UniversityFees                │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Custom DocTypes                                        │   │
│  │  • Hall Ticket          • Teaching Assignment           │   │
│  │  • Student Transcript   • Faculty Profile               │   │
│  │  • Hostel Allocation    • Placement Application         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Frappe Education Module                       │
│  Student │ Program │ Course │ Assessment │ Fees │ Attendance   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ERPNext + HRMS (Hidden Backend)                │
│         Accounts │ Payroll │ HR │ Asset Management              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Documents

### Core Phases (1-13)

| Phase | Module Focus | Duration | Status |
|-------|--------------|----------|--------|
| [Phase 1](phase_01_foundation.md) | Foundation & Core Setup | 4-6 weeks | 📋 |
| [Phase 2](phase_02_admissions_sis.md) | Admissions & Student Information System | 4-6 weeks | 📋 |
| [Phase 3](phase_03_academics.md) | Academics Module (CBCS, Timetable, Attendance) | 5-6 weeks | 📋 |
| [Phase 4](phase_04_examinations.md) | Examinations & Results | 5-6 weeks | 📋 |
| [Phase 5](phase_05_fees_finance.md) | Fees & Finance | 4-5 weeks | 📋 |
| [Phase 6](phase_06_hr_faculty.md) | HR & Faculty Management | 4-5 weeks | 📋 |
| [Phase 7](phase_07_extended_modules.md) | Extended Modules (Hostel, Transport, Library, Placement) | 6-8 weeks | 📋 |
| [Phase 8](phase_08_integrations_deployment.md) | Integrations, Analytics & Deployment | 4-6 weeks | 📋 |

### Extended Phases (14-22) - Gap Coverage

| Phase | Module Focus | Duration | Priority | Status |
|-------|--------------|----------|----------|--------|
| [Phase 14](phase_14_payment_financial_integrations.md) | Payment Gateway & Financial Integrations | 5 weeks | High | 📋 |
| [Phase 15](phase_15_communication_notifications.md) | Communication & Notification System | 5 weeks | High | 📋 |
| [Phase 16](phase_16_inventory_asset_management.md) | Inventory & Asset Management | 4 weeks | Medium | 📋 |
| [Phase 17](phase_17_examination_question_bank.md) | Advanced Examination & Question Bank | 6 weeks | High | 📋 |
| [Phase 18](phase_18_grievance_feedback.md) | Grievance & Feedback Management | 4 weeks | Medium-High | 📋 |
| [Phase 19](phase_19_analytics_reporting_mis.md) | Analytics, Reporting & MIS | 5 weeks | High | 📋 |
| [Phase 20](phase_20_accreditation_compliance.md) | Accreditation & Compliance (NAAC/NBA) | 6 weeks | High | 📋 |
| [Phase 21](phase_21_mobile_pwa.md) | Mobile Application & PWA | 6 weeks | Medium | 📋 |
| [Phase 22](phase_22_deployment_infrastructure.md) | Deployment & Infrastructure | 4 weeks | Critical | 📋 |

**Total Estimated Duration: 18-24 months (including extended phases)**

---

## Phase Summaries

### Phase 1: Foundation & Core Setup
**Duration:** 4-6 weeks

Sets up the project foundation including:
- Custom app scaffold (`university_erp`)
- Override classes for Education DocTypes
- Custom fields via fixtures
- Role and permission setup
- Basic workflow configuration

**Key Deliverables:**
- hooks.py with override_doctype_class
- Base override classes for Student, Program, Course, Fees
- Custom field JSON fixtures
- University-specific roles

---

### Phase 2: Admissions & Student Information System
**Duration:** 4-6 weeks

Implements the complete admissions lifecycle:
- Student Applicant extensions
- Admission Cycle management
- Seat Matrix and Merit List
- Applicant-to-Student conversion
- Student Portal

**Key Deliverables:**
- Extended Student Applicant with workflow
- Admission Cycle DocType
- Merit List Generator
- Student Profile Portal

---

### Phase 3: Academics Module
**Duration:** 5-6 weeks

Covers academic management with CBCS support:
- Program and Course extensions (L-T-P-S credits)
- Course Registration system
- Timetable generation
- Attendance tracking
- Teaching Assignment management

**Key Deliverables:**
- CBCS credit structure implementation
- Course Registration DocType
- Timetable Generator
- Extended Attendance tracking

---

### Phase 4: Examinations & Results
**Duration:** 5-6 weeks

Complete examination management:
- Assessment Plan extensions
- Hall Ticket generation
- Result Entry Tool (bulk entry)
- 10-point CGPA grading scale
- Transcript generation

**Key Deliverables:**
- Extended Assessment Result with grading
- Hall Ticket DocType
- Result Entry Tool
- Student Transcript Generator

---

### Phase 5: Fees & Finance
**Duration:** 4-5 weeks

Comprehensive fee management:
- Fee Structure extensions
- Payment gateway integration (Razorpay)
- Scholarship management
- GL integration with ERPNext
- Financial reports

**Key Deliverables:**
- Extended Fees with penalties/scholarships
- Razorpay payment integration
- Fee collection workflow
- Fee Defaulters Report

---

### Phase 6: HR & Faculty Management
**Duration:** 4-5 weeks

Faculty and staff management:
- Employee extensions for teaching staff
- Faculty Profile with research metrics
- Teaching workload management
- Leave management extensions
- Performance evaluation

**Key Deliverables:**
- Faculty Profile DocType
- Teaching Assignment system
- Workload Summary Report
- Faculty Portal

---

### Phase 7: Extended Modules
**Duration:** 6-8 weeks

Four additional modules:
1. **Hostel Management** - Room allocation, attendance, mess
2. **Transport Management** - Routes, vehicles, tracking
3. **Library Management** - Catalog, circulation, fines
4. **Training & Placement** - Companies, jobs, applications

**Key Deliverables:**
- Hostel Allocation system
- Transport Route management
- Library Transaction system
- Placement Portal

---

### Phase 8: Integrations, Analytics & Deployment
**Duration:** 4-6 weeks

Final integration and go-live:
- University Dashboard with KPIs
- Notification system (Email, SMS, Push)
- REST API for mobile apps
- PWA configuration
- Docker production deployment
- CI/CD pipeline

**Key Deliverables:**
- University Dashboard
- Multi-channel notifications
- Mobile API endpoints
- Production deployment scripts

---

## Document Structure

Each phase document follows a consistent structure:

```
1. Overview
   - Duration
   - Priority
   - Dependencies

2. Prerequisites
   - Completed phases
   - Technical requirements
   - Knowledge requirements

3. Week-by-Week Deliverables
   - Detailed tasks
   - Code examples
   - Configuration snippets

4. Output Checklist
   - DocTypes created
   - Custom fields installed
   - Reports developed
   - Integrations completed

5. Risks & Mitigations

6. Dependencies for Next Phase

7. Sign-off Criteria
   - Functional acceptance
   - Technical acceptance
   - Documentation requirements

8. Estimated Timeline
```

---

## Key Technical Concepts

### Override Classes
```python
# hooks.py
override_doctype_class = {
    "Student": "university_erp.overrides.student.UniversityStudent",
    "Program": "university_erp.overrides.program.UniversityProgram",
    "Course": "university_erp.overrides.course.UniversityCourse",
    "Fees": "university_erp.overrides.fees.UniversityFees",
    "Assessment Result": "university_erp.overrides.assessment_result.UniversityAssessmentResult"
}
```

### Custom Fields Convention
- All custom fields use `custom_` prefix
- Stored in JSON fixtures: `fixtures/custom_field/*.json`
- Loaded via hooks.py fixtures list

### CBCS Credit Structure
```
Credits = L + T + (P/2) + S
Where:
  L = Lecture hours per week
  T = Tutorial hours per week
  P = Practical hours per week
  S = Self-study credits
```

### 10-Point Grading Scale
| Grade | Points | Percentage Range |
|-------|--------|------------------|
| O | 10 | 90-100 |
| A+ | 9 | 80-89.99 |
| A | 8 | 70-79.99 |
| B+ | 7 | 60-69.99 |
| B | 6 | 55-59.99 |
| C | 5 | 50-54.99 |
| P | 4 | 45-49.99 |
| F | 0 | Below 45 |

---

## Getting Started

1. **Review Architecture Documents**
   - [01_architecture_overview.md](../01_architecture_overview.md)
   - [03_modules_doctypes.md](../03_modules_doctypes.md)

2. **Start with Phase 1**
   - Set up development environment
   - Create custom app scaffold
   - Implement override classes

3. **Follow Phase Sequence**
   - Each phase builds on previous ones
   - Check prerequisites before starting
   - Complete all checklist items before moving on

4. **Use Checklists**
   - Each phase has detailed output checklists
   - Mark items as completed
   - Get sign-off before next phase

---

## Timeline Overview

```
Month 1-2:   Phase 1 (Foundation) + Phase 2 (Admissions)
Month 3-4:   Phase 3 (Academics) + Phase 4 (Examinations)
Month 5-6:   Phase 5 (Fees) + Phase 6 (HR)
Month 7-9:   Phase 7 (Extended Modules)
Month 10-12: Phase 8 (Integration & Deployment)
```

---

## Support Documents

| Document | Description |
|----------|-------------|
| [Architecture Overview](../01_architecture_overview.md) | System architecture and design decisions |
| [Tech Stack](../02_tech_stack.md) | Technology choices and versions |
| [Modules & DocTypes](../03_modules_doctypes.md) | Complete DocType reference |
| [Education Deep Dive](../04_education_deep_dive.md) | Frappe Education integration details |
| [Workflows & Permissions](../05_workflows_permissions.md) | Workflow and security configuration |
| [UI/UX Guidelines](../06_ui_ux_guidelines.md) | Design standards and portal specs |
| [Integrations & Deployment](../07_integrations_deployment.md) | External integrations and deployment |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 📋 | Not started |
| 🚧 | In progress |
| ✅ | Completed |
| ⚠️ | Blocked |

---

*Last Updated: December 2024*
