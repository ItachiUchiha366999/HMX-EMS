# G.S. MOZE EDUCATIONAL TRUST — ERP PROPOSAL
## B2C | HMX Builds → MOZE Uses → Per College Instance | 19 Institutes, 25,000 Students

---

# EXECUTIVE SUMMARY

| Item | Detail |
|------|--------|
| **Client** | G.S. MOZE Educational Trust (End Client — B2C) |
| **Relationship** | HMX builds, MOZE uses directly |
| **Trust Scale** | 13 Campuses, 19 Institutes, 25,000 Students |
| **Software** | Same ERP for all colleges, different configs per college |
| **Deployment** | Separate Frappe site per college (shared server) OR company-based isolation |
| **Infrastructure** | MOZE pays all hosting centrally |
| **AMC** | MOZE pays combined AMC (not per college) |
| **Platform** | Frappe v16 + Custom UI |
| **State** | Maharashtra (Phase 1) |
| **Timeline** | 2-3 months (Urgent) |

---

# PART 1: TRUST PROFILE (Verified Data)

## From GSMCOE Official Brochure:

> **"About Trust: 13 Campuses, 19 Institutes, 25,000 Students, Schools, Colleges for Engineering, Jr. Colleges, B.Ed, D.Ed"**

## All Identified Institutions

| # | Institution | Location | Type | Est. | Affiliation | Students (Est.) |
|---|------------|----------|------|------|-------------|----------------|
| 1 | **GSMCOE Balewadi** | Balewadi | Engineering + MBA/MCA/BCA | 1999 | SPPU | 2,000-2,500 |
| 2 | **PG MOZE COE Wagholi** | Wagholi | Engineering + MBA/MCA | 2006 | SPPU | 1,905 (confirmed) |
| 3 | **GS MOZE Pharmacy** | Wagholi | B.Pharm + D.Pharm | — | SPPU/MSBTE | 500-600 |
| 4 | **Parvatibai Genba Moze Pharmacy** | Wagholi | Pharmacy | — | SPPU/MSBTE | 400-500 |
| 5 | **GS MOZE ACS Yerwada** | Yerwada | BA/BCom/BSc/BBA/BCA | 2000 | SPPU | 1,219 (confirmed) |
| 6 | **GS MOZE ACS Wadmukhwadi** | Wadmukhwadi | BA/BCom/BSc | 2004 | SPPU | 800-1,000 |
| 7 | **GS MOZE Adhyapak Mahavidyalaya** | Alandi Road | B.Ed + M.Ed | 2004 | SPPU/NCTE | 500-800 |
| 8 | **GS MOZE Junior College of Education** | Yerwada | D.Ed | — | NCTE | 200-400 |
| 9-19 | **Other Institutes** | Various | Schools, Jr. Colleges, etc. | Various | State Board/NCTE | ~15,000-17,000 |
| | **TOTAL** | **13 campuses** | **19 institutes** | | | **~25,000** |

## Institution Types (Diversity)

| Type | Count (Est.) | Regulatory Body | Compliance |
|------|-------------|----------------|------------|
| Engineering Colleges | 2-3 | AICTE + SPPU | NAAC, NBA, CO-PO, AICTE |
| Pharmacy Colleges | 2 | PCI + SPPU/MSBTE | PCI, NAAC |
| Degree Colleges (Arts/Com/Sci) | 2-3 | SPPU | NAAC, CBCS |
| B.Ed/M.Ed Colleges | 1-2 | NCTE + SPPU | NCTE, NAAC |
| D.Ed Colleges | 1-2 | NCTE | NCTE |
| Junior Colleges | 2-3 | State Board | MSBSHSE |
| Schools | 3-5 | State Board/CBSE | RTE, UDISE+ |
| **Total** | **~19** | | |

---

# PART 2: DEPLOYMENT ARCHITECTURE

## Recommended: Company-Based Isolation (Single Site)

```
┌─────────────────────────────────────────────────────────────┐
│                    MOZE ERP PLATFORM                        │
│                    erp.gsmoze.in                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SINGLE FRAPPE SITE                      │   │
│  │              (Company-Based Isolation)               │   │
│  │                                                      │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │  │ GSMCOE   │ │ PG MOZE  │ │ Pharmacy │            │   │
│  │  │ Balewadi │ │ Wagholi  │ │ Wagholi  │  ...19     │   │
│  │  │(Company) │ │(Company) │ │(Company) │            │   │
│  │  │          │ │          │ │          │            │   │
│  │  │ Students │ │ Students │ │ Students │            │   │
│  │  │ Faculty  │ │ Faculty  │ │ Faculty  │            │   │
│  │  │ Fees     │ │ Fees     │ │ Fees     │            │   │
│  │  │ Exams    │ │ Exams    │ │ Exams    │            │   │
│  │  └──────────┘ └──────────┘ └──────────┘            │   │
│  │                                                      │   │
│  │  Shared: Roles, Permissions, Templates, Reports     │   │
│  │  Isolated: Data per Company (Row-Level)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SERVER: 32 vCPU | 64GB RAM | 1TB SSD                      │
│  (Handles 25K users, 19 companies)                          │
└─────────────────────────────────────────────────────────────┘
```

### Why Company-Based (Not Multi-Site)?

| Factor | Company-Based | Multi-Site |
|--------|--------------|------------|
| **Simplicity** | ✅ One codebase, one deploy | ❌ 19 separate sites to manage |
| **Updates** | ✅ One migrate runs for all | ❌ Run migrate 19 times |
| **Consistency** | ✅ Same config everywhere | ❌ Config drift per site |
| **Performance** | ✅ Shared connection pool | ❌ 19 connection pools |
| **Reporting** | ✅ Cross-college reports easy | ❌ Need separate aggregation |
| **Isolation** | ⚠️ Row-level (Company field) | ✅ Full DB isolation |
| **Customization** | ⚠️ Limited per-college | ✅ Full per-college |

**For MOZE's use case (same software, different configs, 19 institutes): Company-Based is better.**

### When to Use Multi-Site Instead

- If a college needs completely different DocTypes
- If a college needs different Frappe apps
- If regulatory requirement demands full DB isolation
- **Can always split to multi-site later if needed**

---

# PART 3: SERVER SIZING (For 25K Users)

## Load Analysis

| Metric | Value |
|--------|-------|
| **Total Students** | 25,000 |
| **Total Staff** | ~1,500-2,000 |
| **Total Users** | ~27,000 |
| **Concurrent Users (Normal)** | 500-800 |
| **Concurrent Users (Peak)** | 1,500-2,500 |
| **Peak Scenarios** | Exam results, fee deadline, admission |
| **DB Size (Year 1)** | ~5-10GB |
| **DB Size (Year 3)** | ~15-25GB |
| **DB Size (Year 5)** | ~30-50GB |

## Server Recommendation

| Component | Spec | Provider | Monthly |
|-----------|------|----------|---------|
| **App Server** | 32 vCPU, 64GB RAM, 500GB NVMe | E2E Networks | ₹12,000 |
| **DB Server** | 16 vCPU, 32GB RAM, 200GB NVMe | E2E Networks | ₹8,000 |
| **Backup** | 500GB (Backblaze B2) | Backblaze | ₹1,500 |
| **CDN + DDoS** | Cloudflare Pro | Cloudflare | ₹1,500 |
| **Monitoring** | UptimeRobot Pro | UptimeRobot | ₹500 |
| **Domain + SSL** | erp.gsmoze.in + Let's Encrypt | | ₹150 |
| **Total Monthly** | | | **₹23,650** |
| **Total Annual** | | | **₹2,83,800** |

---

# PART 4: PRICING MODEL

## Model: Build + Per-College Setup + Combined AMC + Per-Student

### 4.1 One-Time Build (Core Platform)

| # | Component | Detail | Cost |
|---|-----------|--------|------|
| 1 | **Core ERP (12 modules)** | Student, Admission, Fees, Exams, LMS, Attendance, Timetable, HR/Payroll, Library, Placement, Alumni, Inventory | ₹7,00,000 |
| 2 | **Company-Based Multi-Tenant** | 19 company isolation, centralized admin, cross-college reporting | ₹1,50,000 |
| 3 | **Maharashtra Compliance** | SPPU, AICTE, NCTE, PCI, State Board, NAAC, FRA, DPDP, UDISE+ | ₹1,50,000 |
| 4 | **Data Masking + Privacy** | v16 masking, DPDP consent, field/print-level masking | ₹50,000 |
| 5 | **Multi-Language** | Marathi + English — UI, prints, SMS, consent | ₹50,000 |
| 6 | **SMS Integration (MSG91)** | 10 templates, DLT, auto-triggers | ₹40,000 |
| 7 | **All Portals** | Student, Parent, Faculty, Admin, Management | ₹1,00,000 |
| 8 | **Report Engine** | Custom reports, board formats, compliance exports | ₹60,000 |
| 9 | **Cross-College Dashboard** | Trust-level view: all 19 institutes in one dashboard | ₹50,000 |
| 10 | **Data Migration Tools** | Import utilities, validation, cleanup | ₹30,000 |
| 11 | **Training** | 5 days on-site (admin, faculty, accountants, management) | ₹30,000 |
| 12 | **Documentation** | User manual (Marathi+English), admin guide, video tutorials | ₹20,000 |
| 13 | **Testing + QA** | Load testing (25K users), security audit | ₹30,000 |
| | **TOTAL BUILD** | | **₹12,10,000** |

### 4.2 Per-College Setup Fee

Each college/institute needs initial configuration, data loading, and onboarding.

| Service | Per College | For 19 Colleges |
|---------|-------------|-----------------|
| **College Configuration** | ₹15,000 | ₹2,85,000 |
| **Fee Structure Setup** | ₹5,000 | ₹95,000 |
| **Subject/Course Mapping** | ₹5,000 | ₹95,000 |
| **User/Role Setup** | ₹3,000 | ₹57,000 |
| **Data Import (Student, Staff)** | ₹7,000 | ₹1,33,000 |
| **Go-Live Support (per college)** | ₹5,000 | ₹95,000 |
| **Total Per College** | **₹40,000** | **₹7,60,000** |

> **Note:** ₹40,000 per college setup is very reasonable. For comparison, competitors charge ₹50K-2L just for setup.

### 4.3 Combined AMC (Annual)

This covers everything MOZE needs to keep the platform running.

| # | Item | Detail | Cost |
|---|------|--------|------|
| 1 | **Core Platform Maintenance** | Bug fixes, security patches, Frappe updates, dependency upgrades | ₹1,50,000 |
| 2 | **24/7 Monitoring & Incident Response** | Uptime monitoring, performance alerts, incident escalation | ₹50,000 |
| 3 | **Backup & Disaster Recovery** | Automated backup verification, DR testing | ₹30,000 |
| 4 | **Compliance Updates** | Board format changes, new regulations, portal API changes | ₹75,000 |
| 5 | **Dedicated Support** | WhatsApp group, phone support, priority response (< 4h critical) | ₹50,000 |
| 6 | **Quarterly Health Check** | Performance review, DB optimization, security audit | ₹50,000 |
| 7 | **Per-Student Scaling** | Covers cost of supporting 25K users (₹10/student) | ₹2,50,000 |
| 8 | **New College Onboarding (2/year)** | For MOZE adding new institutes | ₹80,000 |
| | **TOTAL AMC** | | **₹7,35,000/year** |

### AMC Breakdown by Student Count

| Students | Base AMC | Per-Student (₹10) | Total AMC |
|----------|----------|-------------------|-----------|
| 10,000 | ₹4,85,000 | ₹1,00,000 | ₹5,85,000 |
| 15,000 | ₹4,85,000 | ₹1,50,000 | ₹6,35,000 |
| **25,000** | **₹4,85,000** | **₹2,50,000** | **₹7,35,000** |
| 35,000 | ₹4,85,000 | ₹3,50,000 | ₹8,35,000 |
| 50,000 | ₹4,85,000 | ₹5,00,000 | ₹9,85,000 |

### 4.4 Pay-Per-Incident (Beyond AMC)

| Service | Pricing |
|---------|---------|
| On-site visit | ₹5,000/visit |
| Small feature (< 2 days) | ₹12,000-20,000 |
| Medium feature (3-7 days) | ₹25,000-50,000 |
| New module (10+ days) | ₹60,000-1,50,000 |
| New state board compliance | ₹75,000-1,50,000 |
| Additional college setup | ₹40,000 |
| Data recovery | ₹8,000 |
| Emergency support (after hours) | ₹3,000/hour |
| Performance optimization | ₹15,000-30,000 |
| Migration to new server | ₹20,000-40,000 |
| Custom report | ₹3,000-8,000 |
| Mobile App (PWA) | ₹80,000-1,20,000 |
| WhatsApp Business Integration | ₹25,000-40,000 |

---

# PART 5: TOTAL COST & REVENUE

## Year 1 (Full Deployment — 19 Colleges, 25K Students)

| Item | Amount |
|------|--------|
| **Build** | ₹12,10,000 |
| **Per-College Setup (19 × ₹40K)** | ₹7,60,000 |
| **AMC (Year 1)** | ₹7,35,000 |
| **Total Year 1 to HMX** | **₹27,05,000** |

## Year 2+ (Maintenance + Growth)

| Item | Amount |
|------|--------|
| **AMC (25K students)** | ₹7,35,000 |
| **New College Setup (2/year × ₹40K)** | ₹80,000 |
| **Pay-Per-Incident (est.)** | ₹1,00,000 |
| **Total Year 2+** | **₹9,15,000/year** |

## Your Revenue Projection (5-10 Years)

| Year | Students | Build | Setup | AMC | PPI | **Total** |
|------|----------|-------|-------|-----|-----|-----------|
| 1 | 25,000 | ₹12,10,000 | ₹7,60,000 | ₹7,35,000 | ₹50,000 | **₹27,55,000** |
| 2 | 28,000 | — | ₹80,000 | ₹7,65,000 | ₹1,00,000 | **₹9,45,000** |
| 3 | 31,000 | — | ₹80,000 | ₹7,95,000 | ₹1,00,000 | **₹9,75,000** |
| 4 | 34,000 | — | ₹80,000 | ₹8,25,000 | ₹1,00,000 | **₹10,05,000** |
| 5 | 37,000 | — | ₹80,000 | ₹8,55,000 | ₹1,00,000 | **₹10,35,000** |
| 6 | 40,000 | — | ₹80,000 | ₹8,85,000 | ₹1,00,000 | **₹10,65,000** |
| 7 | 43,000 | — | ₹80,000 | ₹9,15,000 | ₹1,00,000 | **₹10,95,000** |
| 8 | 46,000 | — | ₹80,000 | ₹9,45,000 | ₹1,00,000 | **₹11,25,000** |
| 9 | 50,000 | — | ₹80,000 | ₹9,85,000 | ₹1,00,000 | **₹11,65,000** |
| 10 | 50,000+ | — | ₹80,000 | ₹9,85,000 | ₹1,00,000 | **₹11,65,000** |
| **5-Year Total** | | | | | | **₹67,15,000** |
| **10-Year Total** | | | | | | **₹1,23,30,000** |

**That's ₹1.23 Crore over 10 years from one client (MOZE).**

---

# PART 6: MOZE's INVESTMENT vs VALUE

## What MOZE Pays (Year 1)

| Item | Amount |
|------|--------|
| Build + Setup | ₹19,70,000 |
| AMC | ₹7,35,000 |
| Infrastructure (hosting) | ₹2,84,000 |
| SMS costs (est.) | ₹1,00,000 |
| Support staff (1 person) | ₹3,00,000 |
| **Total Year 1** | **₹33,89,000** |

## What MOZE Gets

| Value | Detail |
|-------|--------|
| **19 institutes digitized** | All on one platform |
| **25,000 students managed** | Admission to alumni |
| **NAAC ready** | Data warehouse for accreditation |
| **AICTE/PCI/NCTE compliant** | All regulatory bodies covered |
| **DPDP compliant** | Data protection, consent |
| **Centralized trust dashboard** | View all 19 institutes in one place |
| **No vendor lock-in** | Frappe is open source, MOZE owns data |
| **Scalable** | Add more colleges easily |

## Per-Student Cost for MOZE

| Metric | Value |
|--------|-------|
| Year 1 total cost | ₹33,89,000 |
| Students | 25,000 |
| **Cost per student (Year 1)** | **₹135.56** |
| Year 2+ annual cost | ₹10,19,000 |
| **Cost per student (Year 2+)** | **₹40.76** |

> **₹41/student/year for complete ERP + LMS + compliance across 19 institutes is EXTREMELY competitive.**

---

# PART 7: AMC JUSTIFICATION (Why ₹7.35L is Fair)

## What MOZE Gets for ₹7.35L/year

| Service | Equivalent Market Rate |
|---------|----------------------|
| 24/7 monitoring + incident response | ₹1,50,000-2,50,000 (external) |
| Bug fixes + security patches | ₹1,00,000-2,00,000 |
| Compliance updates (NAAC, AICTE, DPDP) | ₹1,50,000-2,50,000 |
| Dedicated support team | ₹1,00,000-2,00,000 |
| Quarterly health checks | ₹50,000-1,00,000 |
| Per-student scaling (25K users) | ₹2,00,000-3,00,000 |
| **Market Equivalent** | **₹7,50,000-13,00,000** |
| **Our Price** | **₹7,35,000** |
| **MOZE Saves** | **₹15,000-5,65,000/year** |

## Per-College AMC Cost

| Metric | Value |
|--------|-------|
| Total AMC | ₹7,35,000 |
| Number of colleges | 19 |
| **Per-college AMC** | **₹38,684/year** |
| **Per-college AMC** | **₹3,224/month** |

> **₹3,224/month per college for complete ERP support is cheaper than a single staff member's salary.**

---

# PART 8: TIMELINE (2-3 Months — Urgent)

## Phase 1: Foundation (Week 1-4)

| Week | Task | Deliverable |
|------|------|-------------|
| 1 | Server setup, Frappe v16 install, company-based config | Platform ready, 19 company slots |
| 2 | Student Information System, Admission module | Student CRUD, admission workflow |
| 3 | Fee Management, Payment gateway | Fee structure, collection, receipts |
| 4 | Attendance, Timetable | Daily attendance, timetable views |

## Phase 2: Core Modules (Week 5-8)

| Week | Task | Deliverable |
|------|------|-------------|
| 5 | Examination system, Grade calculation | Marks entry, result processing |
| 6 | HR/Payroll, Leave management | Employee records, salary |
| 7 | SMS integration (MSG91), Notifications | Attendance alerts, fee reminders |
| 8 | Student Portal, Parent Portal, Management Dashboard | Self-service + trust-level view |

## Phase 3: Compliance + Pilot (Week 9-12)

| Week | Task | Deliverable |
|------|------|-------------|
| 9 | NAAC/AICTE/NCTE compliance, Report generator | Compliance reports |
| 10 | Data masking (v16), DPDP consent, Multi-language | Privacy compliance |
| 11 | Data migration (3-5 pilot colleges), Training (3 days) | Pilot colleges live |
| 12 | Go-live (pilot colleges), Bug fixes, remaining setup | First colleges live |

## Phase 4: Full Rollout (Month 4-6)

| Month | Task | Deliverable |
|-------|------|-------------|
| 4-5 | Setup remaining 14-16 colleges | All 19 colleges live |
| 5-6 | LMS, Library, Placement, Alumni | Extended modules |
| 6 | Full training (all branches), stabilization | Platform mature |

---

# PART 9: QUESTIONS FOR MOZE MEETING

## Must-Ask (Before Pricing Finalization)

| # | Question | Why Critical |
|---|----------|-------------|
| 1 | **Can you share the complete list of all 19 institutes with current student counts?** | Need exact numbers for pricing |
| 2 | **Which institutes are priority for Phase 1?** (Which 3-5 go live first?) | Pilot planning |
| 3 | **What existing software/data does each institute use?** | Migration complexity |
| 4 | **Do all 19 institutes have reliable internet?** | Cloud feasibility |
| 5 | **Do any institutes have on-prem servers already?** | Hybrid option |

## Strategic Questions

| # | Question | Why It Matters |
|---|----------|---------------|
| 6 | **Will MOZE add more institutes in the next 3-5 years?** | Growth planning |
| 7 | **Do institutes need different DocTypes or features?** | Company vs multi-site decision |
| 8 | **What's the biggest pain point across all institutes today?** | Feature prioritization |
| 9 | **Who will be the single point of contact at MOZE?** | Project management |
| 10 | **What's MOZE's budget for Year 1?** | Pricing negotiation |

## Technical Questions

| # | Question | Why It Matters |
|---|----------|---------------|
| 11 | **Internet speed at each campus?** | Performance expectations |
| 12 | **Do staff use mobile phones for work?** (Attendance, etc.) | Mobile-first design |
| 13 | **Payment gateway preference?** (Razorpay, PayU, UPI?) | Fee module |
| 14 | **LMS — what does MOZE need?** (Video hosting, assignments, quizzes?) | LMS scope |
| 15 | **Any integration needed?** (Biometric, library software, accounting?) | Integration planning |

---

# PART 10: KEY TALKING POINTS FOR MEETING

## Opening

> "You have 19 institutes, 25,000 students, and no ERP. We build one platform. Every college uses the same software, different configs. You pay ₹12L to build, ₹7.6L to set up all colleges, ₹7.35L/year AMC. That's ₹41/student/year. Cheaper than a single staff member's salary per college."

## Why Company-Based

> "One platform. One update. One backup. 19 colleges. Every college sees only their data. You see all 19 in one dashboard. No managing 19 separate servers."

## Why Frappe v16

> "Data masking built-in — your teachers won't see bank details. 2x faster — your 25K students won't wait. Marathi + English — your staff can work in their language."

## The Investment

> "Year 1: ₹27L total. Year 2+: ₹9L/year. Over 10 years: ₹1.23Cr. But what you get: 19 institutes digitized, NAAC ready, DPDP compliant, centralized trust dashboard. Worth every rupee."

## Close

> "We build. You own. You host. We support. ₹27L to start. ₹9L/year after. Long-term partnership."

---

*Document Version: 3.0 (Final — B2C MOZE)*
*Date: March 20, 2026*
*Client: G.S. MOZE Educational Trust*
*Model: B2C (HMX builds → MOZE uses)*
*Scale: 19 Institutes, 25,000 Students*
*Architecture: Company-Based Isolation (Frappe v16)*
*Pricing: Build + Per-College Setup + Combined AMC + Per-Student*
