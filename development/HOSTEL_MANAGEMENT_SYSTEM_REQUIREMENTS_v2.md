# Hostel Management System — Requirements Document (Revised)

**Client:** [Client Name] (via 797Events referral)
**Prepared by:** Hanumatrix
**Date:** February 2026
**Version:** 2.0 | **Status:** Final Scope

---

## 1. Project Overview

### 1.1 Objective
Build a self-hosted, lightweight Hostel Management System for a hostel with 150–200 rooms. The system covers admission, attendance, fee tracking, room management, inventory, and compliance record-keeping — with a public-facing landing page in 3 languages.

### 1.2 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14+ (App Router) |
| UI Components | Tailwind CSS + shadcn/ui |
| Backend | Next.js API Routes |
| ORM | Prisma |
| Database | PostgreSQL |
| Languages | Marathi, Hindi, English (next-intl) |
| File Storage | Local disk / S3-compatible (MinIO) |
| Auth | NextAuth.js (credentials provider, role-based) |
| Hosting | Client-arranged VPS (DigitalOcean 2GB RAM recommended) |
| PDF Generation | Template-based (receipts, admission letters, registers) |

### 1.3 Users & Roles (3 Only)

| Role | Access |
|------|--------|
| Admin | Full system access — students, rooms, fees, inventory, reports, settings, IP whitelist |
| Warden | Student management, attendance, room allocation, reports (view) |
| Guard | Attendance marking (daily check-in/check-out) |

### 1.4 Access Control

| Area | Access Level |
|------|-------------|
| Landing page + Admission form | Public (no restriction) |
| Admin panel (all management) | IP-restricted (Nginx whitelist, server-level) |

---

## 2. Module Requirements

---

### Module 1: Landing Page (Public)

**Purpose:** Public-facing page for hostel information and admission.

**Content Sections:**
- Hostel name, description, photos
- Facilities & amenities overview
- Room types and pricing summary
- Rules & regulations summary
- "Apply Now" CTA → links to admission form
- Contact information (address, phone, email, map)
- Terms & Conditions page (linked)

**Features:**
- 3-language support: Marathi, Hindi, English (toggle/selector)
- Mobile-responsive design
- SEO-friendly (meta tags, structured data)
- Fast loading (<3 sec)
- T&C acceptance required before form submission
- Designed by HMX designer — integrated by dev team

---

### Module 2: Admission Form (Public)

**Purpose:** Online admission application accessible via URL/QR code.

**Fields (configurable by admin):**
- Student full name
- Date of birth, Gender
- Contact number (student + parent/guardian)
- Email address
- Permanent address & local address
- College/Institution name & course (if educational hostel)
- Year / semester
- Blood group
- Emergency contact (name, relation, phone)
- Preferred room type (single / double / triple / dormitory)
- Meal plan preference (veg / non-veg / no mess)
- Medical conditions / allergies (optional)
- Photo upload (passport size)
- Document uploads (Aadhaar, college ID, address proof — see Module 4)
- Terms & conditions acceptance checkbox (mandatory)

**Features:**
- Auto-generated application reference number
- Email confirmation on submission (to student)
- Admin notification on new application
- Captcha/bot protection
- 3-language support (Marathi/Hindi/English)
- Mobile-responsive
- T&C link with full terms displayed

**Terms & Conditions Must Include:**
- Consent for identity verification and data collection
- Consent for police verification (owner's responsibility)
- Agreement to hostel rules and regulations
- Data usage and privacy statement
- Disclaimer: "Identity verification and police verification are conducted by the hostel administration as per local regulations. The hostel management system is a record-keeping tool only."

---

### Module 3: Student Management (Admin/Warden)

**Student Master Record:**
- Unique Student ID (auto-generated)
- Full profile: personal, academic, guardian details
- Room allocation (current + history)
- Fee payment history
- Attendance summary
- Document checklist & status
- Status: Active / On Leave / Vacated / Suspended

**Features:**
- CRUD with search, filter, sort, pagination
- Quick filters: by status, room, floor, block
- Export student list to Excel/CSV
- Individual student profile page (all info in one view)
- Bulk status update (e.g., mark multiple as "Vacated" at year-end)

---

### Module 4: Document Management & KYC Record-Keeping (Admin)

**Purpose:** Store and track compliance documents. Software facilitates record-keeping — does NOT perform identity authentication.

**Required Documents (configurable checklist):**
- Aadhaar card (front + back)
- College ID / Institution letter
- Passport-size photos (2)
- Address proof (parent/guardian)
- Parent/Guardian ID
- Police verification receipt/status (uploaded by admin after offline verification)
- Custom document types (admin can add)

**Per-Student KYC Checklist:**
| Document | Status Options |
|----------|---------------|
| Each configured document | Not Uploaded / Uploaded / Verified by Admin / Rejected (with remarks) |

**Features:**
- Drag-and-drop upload (PDF, JPG, PNG — max 5MB per file)
- Admin manually marks each document as "Verified" or "Rejected" with remarks
- Police verification field: Admin uploads receipt/screenshot after completing offline verification
- Compliance dashboard: students with missing/unverified documents
- Filter by document type, status
- Bulk download of a student's documents (ZIP)
- Export compliance report (Excel)

**Compliance Disclaimers (displayed in system):**
- "This system stores documents for record-keeping. Identity verification and police verification are the sole responsibility of the hostel operator."
- "Hostel operator must comply with local police verification requirements, fire safety regulations, and tenant registration laws."

---

### Module 5: Room & Bed Management (Admin/Warden)

**Room Master (150–200 rooms):**
- Room number
- Floor / Block / Building
- Room type: Single / Double / Triple / Dormitory
- Total beds / capacity
- Current occupancy (auto-calculated)
- Rent per bed (monthly)
- Status: Available / Partially Occupied / Fully Occupied / Under Maintenance
- Amenities (AC, attached bathroom, etc.)

**Bed-Level Tracking:**
- Bed number within room
- Assigned student (linked)
- Status: Vacant / Occupied / Reserved / Blocked

**Features:**
- Search available rooms by type, floor, block
- Allocate student to specific bed
- Room transfer with history
- Vacancy dashboard (summary cards: total, occupied, vacant, maintenance)
- Auto-deallocation on student vacating
- Export occupancy report (Excel/PDF)

---

### Module 6: Attendance (Guard/Warden)

**Daily Attendance:**
- Manual entry by Guard (room-wise list, mark exceptions only — bulk "present" default)
- Attendance types: Present / Absent / On Leave / Late Entry
- Evening/Night check-in (configurable cutoff time)
- Lock attendance after cutoff

**Features:**
- Room-wise and floor-wise attendance view
- Quick mark: "Mark All Present" then mark exceptions
- Monthly attendance register (printable — PDF)
- Student-wise attendance percentage
- Defaulter list (below threshold %)
- Absentee report (daily summary)
- Export to Excel/PDF

**Leave Management (Simple):**
- Student leave entry (by Warden): dates, reason, type (Casual/Medical/Emergency)
- Warden marks leave in attendance
- Leave history per student

---

### Module 7: Fee Management — Manual Verification (Admin)

**Fee Structure (Admin configures):**
- Hostel rent (room-type based)
- Security deposit (refundable)
- Admission fee (one-time)
- Mess charges (if applicable)
- Other charges (electricity, laundry, internet — configurable)
- Late payment penalty (admin-set flat amount or %)

**Fee Collection Flow:**
1. Admin generates invoice for student (monthly/quarterly/custom)
2. Student pays via UPI/cash/bank transfer (outside the system)
3. Student uploads payment proof (screenshot/receipt photo) via a link or form
4. Admin reviews proof, verifies, marks as "Paid" with:
   - Payment date
   - Amount received
   - Payment mode (Cash/UPI/Bank Transfer)
   - Reference number (UPI ref, etc.)
   - Proof attachment (screenshot stored)
   - Remarks (if any)
5. System generates receipt (PDF — printable)

**No payment gateway integration.** All payments are offline; system only tracks and records.

**Features:**
- Invoice generation (individual + bulk)
- Payment proof upload by student (simple link/page — public, no login needed)
- Admin verification queue (pending proofs to review)
- Receipt generation (PDF)
- Partial payment tracking
- Due date management
- Defaulter list with outstanding amounts
- Student-wise payment ledger
- Monthly collection summary
- Export to Excel/PDF

---

### Module 8: Basic Inventory (Admin)

**Item Master:**
- Item name, category (Bedding / Furniture / Electrical / Cleaning / Kitchen / Other)
- Unit (piece, kg, litre, etc.)
- Current stock
- Reorder level

**Stock Operations:**
- Stock-in (purchase: vendor, quantity, rate, date)
- Stock-out (issue to room/area with reason)
- Damage/write-off (with reason)

**Features:**
- Low stock alerts on dashboard
- Stock movement history
- Current stock summary report
- Export to Excel

---

### Module 9: Resident Register (Compliance)

**Purpose:** Generate police-ready resident register in printable format.

**Register Fields:**
- Serial number
- Student name
- Father's/Guardian's name
- Permanent address
- Local address
- Aadhaar number
- Contact number
- Room number
- Date of admission
- Date of vacating
- Police verification status
- Remarks

**Features:**
- Auto-populated from student data
- Printable format (PDF — A4 landscape)
- Filter by date range, status
- Export to Excel

---

### Module 10: Dashboard & Reports (Admin/Warden)

**Dashboard Cards:**
- Total students (active / on leave / vacated)
- Occupancy rate (% occupied vs total capacity)
- Today's attendance snapshot
- Fee collection vs outstanding (current month)
- Pending admissions (new applications)
- Low stock alerts
- Documents pending verification

**Standard Reports:**
| Report | Export |
|--------|--------|
| Daily attendance register | Excel, PDF |
| Monthly attendance summary | Excel, PDF |
| Fee collection report (daily/monthly) | Excel, PDF |
| Defaulter list (outstanding fees) | Excel, PDF |
| Room occupancy report | Excel, PDF |
| Inventory stock status | Excel |
| Student enrollment statistics | Excel, PDF |
| Resident register (police format) | PDF |
| KYC compliance status | Excel |

---

## 3. Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Performance | Page load <3 seconds for all admin pages |
| Security | Role-based access, bcrypt passwords, HTTPS, IP restriction (Nginx) |
| Data Backup | Automated daily backups (cron to backup disk/S3) |
| Mobile Access | Responsive web — works on phone/tablet browser for Guard attendance |
| Browser Support | Chrome, Firefox, Edge (latest versions) |
| Language | Marathi, Hindi, English (landing page + admission form + admin labels) |
| Database Scale | Handle 600+ students, 200 rooms, 2L+ attendance records/year |
| Indexing | Proper DB indexes on attendance (date, student), fees (student, status), rooms |

---

## 4. What's NOT Included (Separately Quoted if Needed)

- Payment gateway integration (Razorpay, PayU, etc.)
- WhatsApp Business API notifications
- SMS gateway integration
- Native mobile app (iOS/Android)
- Biometric / QR code / RFID attendance hardware
- Mess / Food management module
- Visitor management module
- Complaint / Grievance system
- Student / Parent login portal
- Multi-hostel management
- CCTV integration
- Aadhaar eKYC API integration (UIDAI license required)
- Accounting / Tally integration

---

## 5. Delivery Plan

| Phase | Activities | Timeline |
|-------|------------|----------|
| **Setup** | Project setup, Prisma schema, auth, roles, IP restriction | Week 1 |
| **Core Build** | Landing page (designer), admission form, student CRUD, room/bed management | Week 1–2 |
| **Operations** | Attendance, fee management (manual verify), inventory, document management | Week 2–3 |
| **Reports & Polish** | Dashboard, reports, exports, PDFs, resident register, testing | Week 3–4 |
| **Go-Live** | Deployment, master data setup, training (2 sessions), handover | Week 4 |

**Total: 4 weeks from signing**

---

## 6. Deliverables

| # | Deliverable |
|---|-------------|
| 1 | Hostel Management System (self-hosted web application) |
| 2 | Public landing page (3 languages, T&C, admission form) |
| 3 | Admin panel with 3 role-based access levels |
| 4 | All master data pre-configured (rooms, beds, fee structure) |
| 5 | User training — 2 sessions (Admin + Warden/Guard) |
| 6 | System documentation (user guide) |
| 7 | Source code — full ownership (Git repository) |
| 8 | 3-month post-launch warranty (bug fixes) |
| 9 | Deployment on client's server |

---

## 7. Client Responsibilities

- Provide hostel master data (room inventory, fee structure, current student list if migrating)
- Arrange VPS hosting (DigitalOcean 2GB RAM recommended — ~₹800-1,200/mo)
- Provide domain name
- Provide content for landing page (logo, hostel photos, description, rules)
- Designate one point-of-contact (SPOC) for feedback and sign-offs
- Conduct police verification of students independently (software stores records only)
- Provide timely feedback (within 2 business days) during development

---

## 8. Compliance & Legal Disclaimer

**The Hostel Management System is a digital record-keeping and operational management tool.**

- Identity verification (KYC) and police verification of residents are the sole legal responsibility of the hostel owner/operator
- The system stores uploaded documents and verification status for record-keeping purposes only
- The system does not authenticate identity documents or interface with UIDAI/police databases
- Hostel operator must independently comply with:
  - Local police verification requirements for tenants
  - Fire safety regulations
  - Municipal licensing for hostel/PG operation
  - DPDP Act (Digital Personal Data Protection) for student PII
- Hanumatrix bears no liability for non-compliance with local regulations

---

## 9. Investment

| Item | Amount |
|------|--------|
| **Complete System (one-time)** | **₹75,000** |
| Payment — On signing | ₹37,500 (50%) |
| Payment — On go-live | ₹37,500 (50%) |

*All amounts exclusive of 18% GST*

**Includes:** Everything listed in Deliverables (Section 6)
**Hosting:** Client arranges separately (~₹800-1,200/mo)

**Post-Warranty Support:** Per-incident basis (₹2,000-5,000 per request)
**Feature Additions:** Quoted separately as mini-projects

---

## 10. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Client Representative | | | |
| HMX Project Lead | | | |

---

*This document defines the complete scope. Any changes after sign-off will be handled via change request process.*

**HANUMATRIX**
*Hybrid Agency for Innovation, Impact & Intelligence*
