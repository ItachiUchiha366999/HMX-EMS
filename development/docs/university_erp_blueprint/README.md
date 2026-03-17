# University ERP - Complete Technical Blueprint

## Hybrid Architecture: Frappe Education + Custom Extensions

This blueprint provides comprehensive technical documentation for building a University ERP system using a **hybrid architecture** that leverages Frappe Education as the foundation while extending it with custom DocTypes and overrides for advanced university-specific functionality.

---

## Architecture Approach

### Hybrid Stack
```
┌─────────────────────────────────────────────────────────────┐
│                    University ERP App                        │
│  (Custom DocTypes, Overrides, Extensions, UI)               │
├─────────────────────────────────────────────────────────────┤
│                   Frappe Education                           │
│  (Student, Program, Course, Fees, Assessment)               │
├─────────────────────────────────────────────────────────────┤
│          ERPNext (Hidden)      │      HRMS (Hidden)         │
│  Accounts, GL, Workflow        │  Employee, Payroll, Leave  │
├─────────────────────────────────────────────────────────────┤
│                      Frappe Framework                        │
└─────────────────────────────────────────────────────────────┘
```

### Why Hybrid?

| Aspect | Pure Custom | Hybrid (Chosen) |
|--------|-------------|-----------------|
| Development Time | 18 months | 10-12 months |
| Maintenance | Full ownership | Shared with community |
| Upgrades | Manual | Automatic for Education |
| Student/Course/Fees | Build from scratch | Ready to use |
| Risk | Higher | Lower |

---

## Document Structure

| # | Document | Description |
|---|----------|-------------|
| 1 | [Architecture Overview](01_architecture_overview.md) | Hybrid stack, hooks.py, override classes, custom fields |
| 2 | [UI & Workspace Strategy](02_ui_workspace_strategy.md) | Custom workspaces, role-based sidebars, portal pages |
| 3 | [Module Mapping](03_module_mapping.md) | Education DocTypes reuse vs custom builds |
| 4 | [Education Deep Dive](04_education_deep_dive.md) | Student lifecycle, CBCS, exams, grading, attendance |
| 5 | [HRMS Deep Dive](05_hrms_deep_dive.md) | Faculty modeling, workload, payroll, appraisal |
| 6 | [Security & Permissions](06_security_permissions.md) | Roles, permissions, audit logging, data privacy |
| 7 | [Integrations & Deployment](07_integrations_deployment.md) | Payment gateways, biometric, government portals, deployment |

---

## Key Design Principles

### 1. Reuse Frappe Education DocTypes
These DocTypes are used directly with custom field extensions:
- **Student** - Extended with enrollment number, category, documents
- **Program** - Extended with CBCS credits (L-T-P-S), regulation year
- **Course** - Extended with credit structure, CO-PO mapping
- **Student Group** - Used as-is for sections/batches
- **Assessment Plan/Result** - Extended for university grading
- **Fees/Fee Schedule** - Extended with GL integration
- **Student Applicant** - Extended for admissions workflow

### 2. Build Custom DocTypes
These are university-specific and built from scratch:
```
university_erp/
├── academics/          # Credit Structure, Elective Group, Timetable Slot
├── admissions/         # Merit List, Seat Matrix, Counseling Round
├── examinations/       # Hall Ticket, Transcript, Grade Card
├── university_hr/      # University Faculty, Workload, Appraisal
├── hostel/             # Hostel, Room, Allotment, Mess
├── transport/          # Route, Vehicle, Pass
├── placement/          # Company, Drive, Offer
├── research/           # Publication, Grant, PhD Scholar
├── accreditation/      # CO, PO, Attainment
├── alumni/             # Alumni, Event, Donation
└── analytics/          # Dashboard configs, Custom reports
```

### 3. ERPNext as Hidden Backend
- **Accounts Engine**: GL entries for fees, payments (hidden from UI)
- **HRMS Engine**: Employee, Salary Slip, Leave for faculty (hidden from UI)
- **Workflow Engine**: Document approval workflows
- **Notification Engine**: Alerts and reminders

### 4. University-Only UI
- Custom workspaces per role (hide Education/ERPNext workspaces)
- Role-based sidebar navigation
- Branded portals for students/faculty
- Restricted global search

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Frappe v15+ |
| Education Base | Frappe Education v15+ |
| ERP Backend | ERPNext v15+ |
| HR Backend | Frappe HRMS v15+ |
| Database | MariaDB 10.6+ |
| Cache | Redis |
| Web Server | nginx |
| Container | Docker |

---

## Role Matrix

| Role | Primary Access |
|------|---------------|
| University Admin | All modules |
| University Registrar | Admissions, Student Records |
| University Finance | Fees, Scholarships, Reports |
| University HR Admin | Faculty, Staff, Payroll |
| University HOD | Department resources |
| University Exam Cell | Examinations, Results |
| University Faculty | Own classes, Attendance, Grades |
| University Student | Portal access only |

---

## Implementation Phases (Hybrid Approach)

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| Phase 1 | Foundation | App setup, Education extensions, HRMS integration |
| Phase 2 | Admissions & SIS | Student Applicant extensions, Merit Lists, Student Portal |
| Phase 3 | Academics | CBCS, Timetable, Attendance, Faculty Portal |
| Phase 4 | Exams & Fees | Assessment extensions, Transcripts, Payment Gateway |
| Phase 5 | Hostel & Support | Room allocation, Transport, Placement |
| Phase 6 | Advanced | OBE, Research, Analytics, Mobile |

**Estimated Duration**: 10-12 months (reduced from 18 months due to Education reuse)

---

## Quick Start

### 1. Create the App
```bash
bench new-app university_erp
```

### 2. Configure hooks.py
```python
required_apps = ["education"]

override_doctype_class = {
    "Student": "university_erp.overrides.student.UniversityStudent",
    "Program": "university_erp.overrides.program.UniversityProgram",
    "Course": "university_erp.overrides.course.UniversityCourse",
    "Fees": "university_erp.overrides.fees.UniversityFees",
}
```

### 3. Install Dependencies & App
```bash
bench get-app education
bench get-app erpnext
bench get-app hrms
bench --site university.local install-app education
bench --site university.local install-app erpnext
bench --site university.local install-app hrms
bench --site university.local install-app university_erp
```

### 4. Run Setup
```bash
bench --site university.local migrate
bench --site university.local execute university_erp.setup.install.after_install
```

---

## Key Integrations

| Integration | Purpose |
|-------------|---------|
| Razorpay/PayU | Online fee payment |
| ZKTeco/eSSL | Biometric attendance |
| MSG91/Twilio | SMS, WhatsApp notifications |
| AISHE/UGC | Government reporting |
| DigiLocker | Digital certificates |

---

## Deployment Options

| Option | Best For |
|--------|----------|
| Docker Compose | Single server, development |
| Kubernetes | Multi-campus, high availability |
| Frappe Cloud | Managed hosting |
| AWS/GCP/Azure | Enterprise deployment |

---

## License

MIT License - See individual documents for detailed implementation.

---

## Contributing

This blueprint is designed to be extended. Key areas for contribution:
- Additional Education DocType extensions
- Integration adapters
- Mobile app components
- Accreditation templates (NAAC/NBA)

---

**Document Version**: 2.0
**Architecture**: Hybrid (Frappe Education + Custom)
**Target Platform**: ERPNext v15+ / Education v15+
**Last Updated**: December 2025
