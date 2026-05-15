# University ERP - Architecture Guide

## 📐 Architecture Documentation

Complete architecture documentation with diagrams is available in the [architecture](./architecture/) directory.

## Quick Access

- **[System Architecture](./architecture/01_SYSTEM_ARCHITECTURE.md)** - System overview, technology stack, modules, DocTypes, database schema, security, and deployment
- **[Workflows](./architecture/02_WORKFLOWS.md)** - 15 detailed workflow diagrams for all major processes
- **[Sequence Diagrams](./architecture/03_SEQUENCE_DIAGRAMS.md)** - 15 sequence diagrams showing component interactions
- **[Activity Diagrams](./architecture/04_ACTIVITY_DIAGRAMS.md)** - 10 activity diagrams for key processes
- **[Use Case Diagrams](./architecture/05_USE_CASE_DIAGRAMS.md)** - Complete use cases for all actors
- **[README](./architecture/README.md)** - How to view diagrams and complete documentation guide

## 🎯 Quick Start

### View Diagrams in VS Code

1. **Install Mermaid Chart Extension**:
   ```bash
   code --install-extension MermaidChart.vscode-mermaid-chart
   ```

2. **Open any architecture file** and press `Ctrl+Shift+V` for preview

### Documentation Highlights

#### 300+ DocTypes Documented
All DocTypes across all modules with complete schemas and relationships.

#### 60+ Diagrams
Comprehensive visual documentation covering:
- System architecture
- Data flows
- Process workflows
- User interactions
- Integration patterns

#### Real-World Scenarios
Detailed flows including:
- Error handling
- Security considerations
- Performance optimizations
- Integration patterns

## 📚 Architecture Overview

### System Layers

```
┌─────────────────────────────────────────┐
│     Presentation Layer                  │
│  (Web, Mobile, Portal, REST API)        │
├─────────────────────────────────────────┤
│     Application Layer                   │
│  (Frappe Framework + Custom Apps)       │
├─────────────────────────────────────────┤
│     Business Logic Layer                │
│  (8+ Modules: Academic, Admission,      │
│   Examination, Finance, HR, etc.)       │
├─────────────────────────────────────────┤
│     Data Layer                          │
│  (MariaDB, Redis, S3 Storage)           │
├─────────────────────────────────────────┤
│     Integration Layer                   │
│  (Payment, SMS, Email, Biometric)       │
└─────────────────────────────────────────┘
```

### Key Modules

| Module | DocTypes | Key Features |
|--------|----------|--------------|
| **Academic** | 45 | Programs, Courses, Batches, Schedules, Attendance |
| **Admission** | 25 | Applications, Merit Lists, Seat Allocation, Enrollment |
| **Examination** | 35 | Question Banks, Online Exams, Evaluation, Results |
| **Finance** | 22 | Fee Structures, Invoices, Payments, Accounting |
| **HR** | 25 | Employees, Payroll, Leave, Recruitment |
| **Library** | 15 | Books, Transactions, Reservations, Fines |
| **Hostel** | 18 | Rooms, Allocations, Check-in/out, Visitors |
| **Transport** | 12 | Routes, Vehicles, Allocations |

### Technology Stack

**Backend**
- Frappe Framework v15+
- Python 3.11+
- MariaDB 10.6+
- Redis 7.0+

**Frontend**
- Frappe UI (Vue.js)
- React.js (Student Portal)
- React Native (Mobile App)

**DevOps**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Prometheus + Grafana (Monitoring)

**Integrations**
- Payment: Razorpay, PayU, Paytm
- SMS: Twilio, AWS SNS
- Email: AWS SES, SendGrid
- Storage: AWS S3, MinIO

## 🔄 Key Workflows

### Student Journey
1. **Admission** → Application → Merit List → Seat Allocation → Enrollment
2. **Registration** → Profile Setup → Course Selection → Fee Payment → Enrollment Confirmation
3. **Academic** → Attendance → Assignments → Examinations → Results
4. **Services** → Library, Hostel, Transport, Grievances

### Faculty Journey
1. **Teaching** → Course Assignment → Content Upload → Attendance Marking
2. **Assessment** → Assignment Creation → Evaluation → Grade Entry
3. **Examination** → Answer Sheet Evaluation → Result Submission

### Administrative Journey
1. **Planning** → Program Creation → Course Definition → Fee Structure
2. **Operations** → Student Management → Timetable → Reports
3. **Monitoring** → Analytics → Compliance → Audits

## 🔐 Security Architecture

### Multi-Layer Security
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-Based Access Control (RBAC)
- **Encryption**: At-rest (AES-256) and in-transit (TLS 1.3)
- **Audit**: Comprehensive logging of all critical operations
- **Compliance**: GDPR, data privacy, secure data handling

### Role Hierarchy
```
System Admin
    ↓
Registrar / Dean
    ↓
HOD / Exam Controller / Accounts Manager
    ↓
Faculty / Librarian / Hostel Warden
    ↓
Student / Parent
```

## 📊 Integration Architecture

### External Integrations

**Payment Gateways**
- Razorpay API with webhook verification
- PayU with signature validation
- Paytm integration

**Communication Services**
- Email: AWS SES, SendGrid
- SMS: Twilio, AWS SNS
- Push: Firebase Cloud Messaging

**Storage Services**
- AWS S3 for documents
- MinIO for on-premise alternative
- CDN for static assets

**Identity Management**
- Biometric attendance integration
- SSO/LDAP for faculty
- OAuth for student portal

## 🚀 Deployment Architecture

### Production Setup
- **Load Balancer**: Nginx with SSL termination
- **App Servers**: 3+ Frappe instances
- **Workers**: Background job processors
- **Database**: MariaDB with replication
- **Cache**: Redis with sentinel
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

### High Availability
- Multi-server deployment
- Database replication
- Redis sentinel for failover
- Automated backups to S3
- Health checks and auto-recovery

## 📖 Documentation Structure

```
docs/
├── architecture/
│   ├── 01_SYSTEM_ARCHITECTURE.md      ← System design & DocTypes
│   ├── 02_WORKFLOWS.md                ← Process workflows
│   ├── 03_SEQUENCE_DIAGRAMS.md        ← Component interactions
│   ├── 04_ACTIVITY_DIAGRAMS.md        ← Process activities
│   ├── 05_USE_CASE_DIAGRAMS.md        ← Use cases by actor
│   └── README.md                      ← How to view diagrams
├── university_erp_blueprint/
│   └── phases/                        ← Implementation phases
│       ├── phase_01_*.md              ← Phase 1-13 (Core features)
│       ├── phase_14_*.md              ← Phase 14-22 (Gap coverage)
│       └── README.md                  ← Phase overview
└── IMPLEMENTATION_GAP_ANALYSIS.md     ← Gap analysis
```

## 🎓 Use Cases by Actor

### Student (20+ Use Cases)
- Portal access, profile management
- Course enrollment, timetable viewing
- Fee payment, receipt download
- Online exams, result viewing
- Library, hostel, transport services
- Grievance filing, document requests

### Faculty (15+ Use Cases)
- Course content management
- Attendance marking (multiple methods)
- Assignment creation and evaluation
- Answer sheet evaluation
- Internal marks entry

### Admin (Various Roles)
- **Registrar**: Student records, documents
- **Admission Officer**: Applications, merit lists
- **Exam Controller**: Exam scheduling, results
- **Accounts Manager**: Fee management, accounting
- **HOD**: Course approval, evaluation verification

## 📞 Support & Resources

### Getting Help
- Review the architecture documentation in this directory
- Check the phase-wise implementation guides
- Refer to workflow diagrams for process understanding

### Contributing
- Follow existing diagram patterns
- Validate Mermaid syntax before committing
- Update version history in README

### Tools & Extensions
- **Mermaid Chart** (VS Code): `MermaidChart.vscode-mermaid-chart`
- **Mermaid Live Editor**: https://mermaid.live/
- **Mermaid Documentation**: https://mermaid.js.org/

---

**Note**: All diagrams use Mermaid syntax and can be viewed directly in VS Code with the Mermaid Chart extension, or on GitHub/GitLab which have native Mermaid support.
