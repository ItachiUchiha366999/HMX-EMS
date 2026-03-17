# University ERP — Duplicate DocType Audit & App Integration Strategy

> Generated: 2026-03-16
> Apps: frappe, erpnext, hrms, education, university_erp

---

## 1. Duplicate DocType Analysis

### Category A: EXACT DUPLICATES — University ERP re-implements doctypes from other apps

| University ERP DocType | Module | Duplicate Of | Source App | Recommendation |
|---|---|---|---|---|
| Supplier | University Inventory | Supplier | ERPNext (Buying) | Remove — use ERPNext with custom fields |
| Supplier Group | University Inventory | Supplier Group | ERPNext (Buying) | Remove — use ERPNext |
| Purchase Order | University Inventory | Purchase Order | ERPNext (Buying) | Remove — use ERPNext |
| Purchase Receipt | University Inventory | Purchase Receipt | ERPNext (Stock) | Remove — use ERPNext |
| Material Request | University Inventory | Material Request | ERPNext (Stock) | Remove — use ERPNext |
| Stock Entry | University Inventory | Stock Entry | ERPNext (Stock) | Remove — use ERPNext |
| Stock Ledger Entry | University Inventory | Stock Ledger Entry | ERPNext (Stock) | Remove — use ERPNext |
| Stock Reconciliation | University Inventory | Stock Reconciliation | ERPNext (Stock) | Remove — use ERPNext |
| Warehouse | University Inventory | Warehouse | ERPNext (Stock) | Remove — use ERPNext |
| Asset | University Inventory | Asset | ERPNext (Assets) | Remove — use ERPNext |
| Asset Category | University Inventory | Asset Category | ERPNext (Assets) | Remove — use ERPNext |
| Asset Maintenance | University Inventory | Asset Maintenance | ERPNext (Assets) | Remove — use ERPNext |
| Asset Movement | University Inventory | Asset Movement | ERPNext (Assets) | Remove — use ERPNext |
| Fee Category | University Finance | Fee Category | Education | Remove — use Education |
| Grievance Type | University Grievance | Grievance Type | HRMS (HR) | Remove — use HRMS |
| Bank Transaction | University Payments | Bank Transaction | ERPNext (Accounts) | Remove — use ERPNext |

**Total: 16 doctypes to remove**

### Doctypes with similar names but DIFFERENT purpose (Keep)

| University ERP DocType | Looks like | Why it's different |
|---|---|---|
| Batch | Batch (ERPNext Stock) | Used for inventory batch tracking, not student batches |
| University Department | Department (Frappe Setup) | Has department_code, hod, is_active — university-specific fields |
| Hostel Room | Room (Education) | Hostel-specific: occupancy, rent, amenities, floor |

### Category B: OVERLAPPING CONCEPTS — Different names, similar purpose

| University ERP DocType | Similar To (App) | Decision | Reason |
|---|---|---|---|
| Fee Payment | Fees (Education) + Payment Entry (ERPNext) | **Keep** | Extends Education's Fees with payment tracking |
| Fee Refund | Payment Entry (ERPNext) | **Keep** | University-specific refund approval workflow |
| Bulk Fee Generator | Fee Schedule (Education) | **Keep** | Batch generation approach vs fee structure |
| Course Registration | Course Enrollment (Education) | **Keep** | Term-based registration, more comprehensive |
| LMS Quiz / Quiz Attempt | Quiz / Quiz Activity (Education) | **Keep** | Separate LMS with richer features |
| Question Bank / Question Paper | Question (Education) | **Keep** | Full exam management vs simple quiz questions |
| Student Transcript | Assessment Result (Education) | **Keep** | Aggregate transcript vs individual results |
| Grievance / Grievance Committee | Employee Grievance (HRMS) | **Keep** | Student/general grievances vs employee-only |
| SMS Log / SMS Queue | SMS Settings (Frappe Core) | **Keep** | Extended messaging with queue management |
| Assessment Rubric | Assessment Criteria (Education) | **Keep** | OBE rubric system vs simple criteria |
| Internal Assessment | Assessment Plan (Education) | **Keep** | Detailed scoring with multiple components |
| Notification Preference/Template | Notification Settings (Desk) | **Keep** | Multi-channel: SMS, WhatsApp, push, in-app |
| Payment Gateway Settings | Payment Gateway Account (ERPNext) | **Keep** | University-specific gateway configuration |

### Category C: UNIVERSITY-UNIQUE — No equivalent in other apps

All hostel management, transport, placement, research/publications, OBE/accreditation, LMS content management, certificate issuance, biometric integration, DigiLocker, faculty profile, teaching assignment, workload distributor, emergency alerts, and other university-specific doctypes — **no duplicates, keep all**.

---

## 2. App Integration Architecture

### 2.1 Education App (Primary Foundation)

University ERP extends the Education app as its core:

**Override DocType Classes** (in `hooks.py`):
```python
override_doctype_class = {
    "Student": "university_erp.overrides.student.UniversityStudent",
    "Program": "university_erp.overrides.program.UniversityProgram",
    "Course": "university_erp.overrides.course.UniversityCourse",
    "Assessment Result": "university_erp.overrides.assessment_result.UniversityAssessmentResult",
    "Fees": "university_erp.overrides.fees.UniversityFees",
    "Student Applicant": "university_erp.overrides.student_applicant.UniversityApplicant",
}
```

**Document Events on Education DocTypes**:
- `Student.validate` → custom validations
- `Student.on_update` → sync with university systems
- `Fees.on_submit` → GL entry creation + payment posting

**Education DocTypes used directly** (via Link fields across university_erp):
- Student, Program, Course, Academic Year, Academic Term
- Student Group, Student Applicant, Instructor, Guardian
- Fees, Fee Schedule, Fee Structure, Assessment Result, Assessment Plan
- Room, Grading Scale, Program Enrollment

### 2.2 HRMS Integration

**Document Events**:
- `Leave Application.on_submit/on_cancel` → faculty leave events (track course impact, trigger temporary teaching assignments)
- `Employee.on_update` → auto-create Faculty Profile when employee is marked as faculty
- `Department.on_update` → sync department events

**Custom Fields on HRMS DocTypes** (via fixture JSONs):
- **Employee**: `custom_is_faculty`, `custom_faculty_profile`, `custom_employee_category`, `custom_faculty_type`, `custom_current_workload`, `custom_qualifications` (table), `custom_highest_qualification`, `custom_specialization`, `custom_total_experience`, `custom_teaching_experience`
- **Leave Application**: `custom_affected_courses` (table), `custom_total_classes_affected`, `custom_temporary_assignment`, `custom_hod_notified`, `custom_affects_teaching`
- **Department**: custom fields for university context

**HRMS DocTypes used directly**:
- Employee, Leave Application, Attendance, Department
- Salary Structure, Salary Component (via salary_components fixture)
- Leave Type (via academic_leave_types fixture)

**Workflows on HRMS DocTypes**:
- Leave Application Workflow (custom approval chain)

### 2.3 ERPNext (Accounts) Integration

**Document Events**:
- `Fees.on_submit` → `create_fee_gl_entry()` (Journal Entry creation for accounting)
- `Fees.on_submit` → `on_fees_submit()` (payment posting)
- `Fees.on_cancel` → `on_fees_cancel()` (reverse payment)

**ERPNext DocTypes used**:
- Company, Account, Journal Entry, Cost Center (for GL posting)
- Mode of Payment (for fee collection)
- Currently has DUPLICATE inventory/asset/purchasing doctypes (see Category A above)

### 2.4 Frappe Core Integration

- **Custom Roles**: 11 university roles (University Admin, Registrar, Finance, HOD, Exam Cell, Faculty, Student, Librarian, Warden, Placement Officer, HR Admin)
- **Custom Fields**: on core DocTypes via fixtures
- **Workflows**: Leave Application, Teaching Assignment Approval, Fee Refund Approval
- **Boot Session**: custom data sent to client on login
- **Website Route Rules**: SPA routing for `/student_portal/<path>`
- **Block Modules**: Manufacturing, Stock, Selling, Buying, CRM, Projects, Assets, Quality, Support hidden from UI

---

## 3. Integration Gaps & Roadmap

### Phase 1 — Remove 16 Exact Duplicate Doctypes
**Impact**: High — eliminates confusion, reduces maintenance
**Effort**: Medium — need to update Link field references across university_erp doctypes
**Steps**:
1. For each duplicate, find all university_erp doctypes that link to it
2. Update those Link fields to point to the ERPNext/Education equivalent
3. Add custom fields to ERPNext/Education doctypes if university-specific fields are needed
4. Delete duplicate doctype directories and DB records
5. Update workspace JSONs

### Phase 2 — Connect Inventory Module to ERPNext
**Impact**: High — university_inventory becomes a configuration/reports layer instead of duplicating core ERP
**Effort**: High — need to map fields, migrate data, update all references
**Approach**:
- Use ERPNext Stock module with custom fields for university context
- Use ERPNext Buying module for purchase orders
- Use ERPNext Assets module for asset management
- Add `override_doctype_class` entries for university-specific logic
- Keep university-unique doctypes: `Inventory Item`, `Inventory Item Group`, `Lab Equipment`, `Lab Equipment Booking`, `Lab Consumable Issue`, `Maintenance Team`

### Phase 3 — Strengthen Education Integration
**Impact**: Medium — reduces doctype proliferation
**Effort**: Medium
**Opportunities**:
- Override `Fee Schedule` instead of separate `Bulk Fee Generator`
- Use Education's `Assessment Plan` with custom fields where possible
- Extend `Student Attendance` for hostel attendance cross-referencing
- Use Education's `Quiz` with custom fields instead of separate `LMS Quiz` (evaluate)

### Phase 4 — Unified API & Portal Layer
**Impact**: Medium — better user experience
**Effort**: Low-Medium
**Areas**:
- Unified portal APIs aggregating Education + University ERP data
- Standardize grading system integration
- Connect placement module with HRMS for alumni tracking
- DigiLocker integration with Education certificates

---

## 4. Current Module Summary (Post-Cleanup)

| Module | Standalone DocTypes | Connects To |
|---|---|---|
| University ERP (core) | 17 | Frappe Core, Education |
| University Academics | 4 | Education (Course, Program) |
| University Admissions | 4 | Education (Student Applicant) |
| University Student Info | 3 | Education (Student) |
| University Examinations | 14 | Education (Assessment, Room) |
| University Finance | 5 | Education (Fees, Fee Schedule) |
| University Payments | 7 | ERPNext (Accounts) |
| University Inventory | 20 | ERPNext (Stock, Buying, Assets) — currently duplicated |
| University Hostel | 9 | Education (Room), standalone |
| University Transport | 4 | Standalone |
| University Library | 7 | Standalone |
| University LMS | 8 | Education (Course) |
| University Placement | 4 | Standalone |
| University Research | 3 | Standalone |
| University OBE | 10 | Education (Course, Program, Assessment) |
| University Integrations | 18 | Frappe Core (SMS, Email) |
| University Grievance | 3 | HRMS (Employee Grievance — related) |
| University Analytics | 5 | Standalone (cross-module reporting) |
| University Feedback | 2 | Standalone |
| University Portals | 8 | Education (Student, Alumni) |
| Faculty Management | 5 | HRMS (Employee, Leave Application, Attendance) |
