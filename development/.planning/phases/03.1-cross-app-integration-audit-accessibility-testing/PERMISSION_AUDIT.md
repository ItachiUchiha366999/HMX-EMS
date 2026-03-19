# Permission Matrix Audit Results

**Generated:** 2026-03-19 14:23:48
**Site:** university.local
**Scope:** 9 roles x 268 doctypes + 8 key API endpoints

## Summary

- **Roles Tested:** 8/9
- **Total Doctypes:** 268
- **API Endpoints Tested:** 8
- **Security Findings:** 2
- **Missing Users for Roles:** Faculty, HOD, VC, Dean, Finance

## Role-User Mapping

| Role | Label | Test User | Method |
|------|-------|-----------|--------|
| System Manager | Admin | zopevedant1@gmail.com | has_role |
| Instructor | Faculty | NO_USER | -- |
| Student | Student | aditya.joshi@nit.edu | has_role |
| Guardian | Parent | parent1@nit.edu | has_role |
| HOD | HOD | NO_USER | -- |
| University VC | VC | NO_USER | -- |
| University Dean | Dean | NO_USER | -- |
| University Registrar | Registrar | registrar@nit.edu | has_role |
| University Finance Officer | Finance | NO_USER | -- |

## Doctype Permission Matrix

Legend: R=Read, W=Write, C=Create, D=Delete

### Admin (System Manager)

Access to 155/268 doctypes.

| Doctype | Module | R | W | C | D |
|---------|--------|---|---|---|---|
| Batch | University ERP | Y | Y | Y | Y |
| Emergency Acknowledgment | University ERP | Y | Y | Y | Y |
| Emergency Alert | University ERP | Y | Y | Y | Y |
| NAAC Metric | University ERP | Y | Y | Y | Y |
| NIRF Data | University ERP | Y | Y | Y | Y |
| Notice Board | University ERP | Y | Y | Y | Y |
| Notice View Log | University ERP | Y | Y | Y | Y |
| Notification Preference | University ERP | Y | Y | Y | Y |
| Notification Template | University ERP | Y | Y | Y | Y |
| Payment Webhook Log | University ERP | Y | Y | Y | Y |
| Suggestion | University ERP | Y | Y | Y | Y |
| University Department | University ERP | Y | Y | Y | Y |
| University Laboratory | University ERP | Y | Y | Y | Y |
| University Settings | University ERP | Y | Y | Y | Y |
| User Notification | University ERP | Y | Y | Y | Y |
| Course Registration | University Academics | Y | Y | Y | Y |
| Elective Course Group | University Academics | Y | Y | Y | Y |
| Timetable Slot | University Academics | Y | Y | Y | Y |
| Admission Criteria | University Admissions | Y | Y | Y | Y |
| Admission Cycle | University Admissions | Y | Y | Y | Y |
| Merit List | University Admissions | Y | Y | Y | Y |
| Seat Matrix | University Admissions | Y | Y | Y | Y |
| Student Status Log | University Student Info | Y | Y | Y | Y |
| University Alumni | University Student Info | Y | Y | Y | Y |
| University Announcement | University Student Info | Y | Y | Y | Y |
| Answer Sheet | University Examinations | Y | Y | Y | Y |
| Exam Schedule | University Examinations | Y | Y | Y | Y |
| External Examiner | University Examinations | Y | Y | Y | Y |
| Generated Question Paper | University Examinations | Y | Y | Y | Y |
| Hall Ticket | University Examinations | Y | Y | Y | Y |
| Internal Assessment | University Examinations | Y | Y | Y | Y |
| Online Examination | University Examinations | Y | Y | Y | Y |
| Practical Examination | University Examinations | Y | Y | Y | Y |
| Question Bank | University Examinations | Y | Y | Y | Y |
| Question Paper Template | University Examinations | Y | Y | Y | Y |
| Question Tag | University Examinations | Y | Y | Y | Y |
| Revaluation Request | University Examinations | Y | Y | Y | Y |
| Student Exam Attempt | University Examinations | Y | Y | Y | Y |
| Student Transcript | University Examinations | Y | Y | Y | Y |
| Bulk Fee Generator | University Finance | Y | Y | Y | Y |
| Scholarship Type | University Finance | Y | Y | Y | Y |
| Student Scholarship | University Finance | Y | Y | Y | Y |
| Faculty Profile | Faculty Management | Y | Y | Y | Y |
| Student Feedback | Faculty Management | Y | Y | Y | Y |
| Teaching Assignment | Faculty Management | Y | Y | Y | Y |
| Temporary Teaching Assignment | Faculty Management | Y | Y | Y | Y |
| Workload Distributor | Faculty Management | Y | Y | Y | Y |
| Hostel Allocation | University Hostel | Y | Y | Y | Y |
| Hostel Attendance | University Hostel | Y | Y | Y | Y |
| Hostel Building | University Hostel | Y | Y | Y | Y |
| Hostel Bulk Attendance | University Hostel | Y | Y | Y | Y |
| Hostel Maintenance Request | University Hostel | Y | Y | Y | Y |
| Hostel Mess | University Hostel | Y | Y | Y | Y |
| Hostel Room | University Hostel | Y | Y | Y | Y |
| Hostel Visitor | University Hostel | Y | Y | Y | Y |
| Mess Menu | University Hostel | Y | Y | Y | Y |
| Transport Allocation | University Transport | Y | Y | Y | Y |
| Transport Route | University Transport | Y | Y | Y | Y |
| Transport Trip Log | University Transport | Y | Y | Y | Y |
| Transport Vehicle | University Transport | Y | Y | Y | Y |
| Book Reservation | University Library | Y | Y | Y | Y |
| Library Article | University Library | Y | Y | Y | Y |
| Library Category | University Library | Y | Y | Y | Y |
| Library Fine | University Library | Y | Y | Y | Y |
| Library Member | University Library | Y | Y | Y | Y |
| Library Subject | University Library | Y | Y | Y | Y |
| Library Transaction | University Library | Y | Y | Y | Y |
| Industry Type | University Placement | Y | Y | Y | Y |
| Placement Company | University Placement | Y | Y | Y | Y |
| Placement Job Opening | University Placement | Y | Y | Y | Y |
| Student Resume | University Placement | Y | Y | Y | Y |
| Assignment Submission | University LMS | Y | Y | Y | Y |
| LMS Assignment | University LMS | Y | Y | Y | Y |
| LMS Content | University LMS | Y | Y | Y | Y |
| LMS Content Progress | University LMS | Y | Y | Y | Y |
| LMS Course | University LMS | Y | Y | Y | Y |
| LMS Discussion | University LMS | Y | Y | Y | Y |
| LMS Quiz | University LMS | Y | Y | Y | Y |
| Quiz Attempt | University LMS | Y | Y | Y | Y |
| Research Grant | University Research | Y | Y | Y | Y |
| Research Project | University Research | Y | Y | Y | Y |
| Research Publication | University Research | Y | Y | Y | Y |
| Accreditation Cycle | University OBE | Y | Y | Y | Y |
| Assessment Rubric | University OBE | Y | Y | Y | Y |
| CO Attainment | University OBE | Y | Y | Y | Y |
| CO PO Mapping | University OBE | Y | Y | Y | Y |
| Course Outcome | University OBE | Y | Y | Y | Y |
| OBE Survey | University OBE | Y | Y | Y | Y |
| PO Attainment | University OBE | Y | Y | Y | Y |
| Program Educational Objective | University OBE | Y | Y | Y | Y |
| Program Outcome | University OBE | Y | Y | Y | Y |
| Survey Template | University OBE | Y | Y | Y | Y |
| Biometric Attendance Log | University Integrations | Y | Y | Y | Y |
| Biometric Device | University Integrations | Y | Y | Y | Y |
| Certificate Request | University Integrations | Y | Y | Y | Y |
| Certificate Template | University Integrations | Y | Y | Y | Y |
| DigiLocker Issued Document | University Integrations | Y | Y | Y | Y |
| DigiLocker Settings | University Integrations | Y | Y | Y | Y |
| Email Queue Extended | University Integrations | Y | Y | Y | Y |
| Payment Gateway Settings | University Integrations | Y | Y | Y | Y |
| Payment Transaction | University Integrations | Y | Y | Y | Y |
| Push Notification Log | University Integrations | Y | Y | Y | Y |
| Push Notification Settings | University Integrations | Y | Y | Y | Y |
| SMS Log | University Integrations | Y | Y | Y | Y |
| SMS Queue | University Integrations | Y | Y | Y | Y |
| University SMS Settings | University Integrations | Y | Y | Y | Y |
| User Device Token | University Integrations | Y | Y | Y | Y |
| WhatsApp Log | University Integrations | Y | Y | Y | Y |
| WhatsApp Settings | University Integrations | Y | Y | Y | Y |
| WhatsApp Template | University Integrations | Y | Y | Y | Y |
| Alumni | University Portals | Y | Y | Y | Y |
| Alumni Event | University Portals | Y | Y | Y | Y |
| Alumni Event Registration | University Portals | Y | Y | Y | Y |
| Announcement | University Portals | Y | Y | Y | Y |
| Job Posting | University Portals | Y | Y | Y | Y |
| Placement Application | University Portals | Y | Y | Y | Y |
| Placement Drive | University Portals | Y | Y | Y | Y |
| Placement Profile | University Portals | Y | Y | Y | Y |
| Bank Transaction | University Payments | Y | Y | Y | Y |
| Fee Refund | University Payments | Y | Y | Y | Y |
| Payment Order | University Payments | Y | Y | Y | Y |
| PayU Settings | University Payments | Y | Y | Y | Y |
| Razorpay Settings | University Payments | Y | Y | Y | Y |
| University Accounts Settings | University Payments | Y | Y | Y | Y |
| Webhook Log | University Payments | Y | Y | Y | Y |
| Asset | University Inventory | Y | Y | Y | Y |
| Asset Category | University Inventory | Y | Y | Y | Y |
| Asset Maintenance | University Inventory | Y | Y | Y | Y |
| Asset Movement | University Inventory | Y | Y | Y | Y |
| Inventory Item | University Inventory | Y | Y | Y | Y |
| Inventory Item Group | University Inventory | Y | Y | Y | Y |
| Lab Consumable Issue | University Inventory | Y | Y | Y | Y |
| Lab Equipment | University Inventory | Y | Y | Y | Y |
| Lab Equipment Booking | University Inventory | Y | Y | Y | Y |
| Maintenance Team | University Inventory | Y | Y | Y | Y |
| Material Request | University Inventory | Y | Y | Y | Y |
| Purchase Order | University Inventory | Y | Y | Y | Y |
| Purchase Receipt | University Inventory | Y | Y | Y | Y |
| Stock Entry | University Inventory | Y | Y | Y | Y |
| Stock Ledger Entry | University Inventory | Y | Y | Y | Y |
| Stock Reconciliation | University Inventory | Y | Y | Y | Y |
| Supplier | University Inventory | Y | Y | Y | Y |
| Supplier Group | University Inventory | Y | Y | Y | Y |
| UOM | University Inventory | Y | Y | Y | Y |
| Warehouse | University Inventory | Y | Y | Y | Y |
| Grievance | University Grievance | Y | Y | Y | Y |
| Grievance Committee | University Grievance | Y | Y | Y | Y |
| Grievance Type | University Grievance | Y | Y | Y | Y |
| Custom Dashboard | University Analytics | Y | Y | Y | Y |
| Custom Report Definition | University Analytics | Y | Y | Y | Y |
| KPI Definition | University Analytics | Y | Y | Y | Y |
| KPI Value | University Analytics | Y | Y | Y | Y |
| Scheduled Report | University Analytics | Y | Y | Y | Y |
| Feedback Form | University Feedback | Y | Y | Y | Y |
| Feedback Response | University Feedback | Y | Y | Y | Y |

<details><summary>No access (113 doctypes)</summary>

- NAAC Document Checklist Item
- NAAC Metric Document
- NAAC Metric Year Data
- Notice Target Department
- Notice Target Program
- Proctoring Snapshot
- Suggestion Attachment
- Course Prerequisite
- Course Registration Item
- Elective Course Group Item
- Admission Cycle Program
- Merit List Applicant
- Answer Sheet Score
- Answer Sheet Tracking Log
- Exam Invigilator
- Hall Ticket Exam
- Internal Assessment Score
- Online Exam Student
- Practical Evaluation Criteria
- Practical Exam Examiner
- Practical Exam Slot
- Practical Exam Student Score
- Question Option
- Question Paper Content Section
- Question Paper Question Item
- Question Paper Section
- Question Tag Link
- Student Answer
- Transcript Semester Result
- Bulk Fee Generator Student
- Employee Qualification
- Faculty Award
- Faculty Publication
- Faculty Research Project
- Leave Affected Course
- Teaching Assignment Schedule
- Hostel Attendance Record
- Hostel Room Occupant
- Mess Menu Item
- Transport Route Stop
- Job Eligible Program
- Placement Round
- Resume Education
- Resume Project
- Resume Skill
- Assignment Rubric Item
- Discussion Reply
- LMS Course Module
- Quiz Answer
- Quiz Question
- Submission File
- Submission Rubric Score
- Grant Utilization
- Project Publication Link
- Publication Author
- Research Team Member
- Accreditation Criterion
- Accreditation Department Link
- Accreditation Program Link
- Accreditation Team Member
- Assessment CO Link
- Assessment Criteria Item
- Bloom Distribution Rule
- CO Direct Attainment
- CO Final Attainment
- CO Indirect Attainment
- CO PO Mapping Entry
- Committee Category Link
- Committee Member
- PO Attainment Entry
- PO Final Entry
- PO Indirect Entry
- PO PEO Mapping
- Survey PO Rating
- Survey Question Item
- Unit Distribution Rule
- Certificate Field
- DigiLocker Document Type
- SMS Template
- WhatsApp Template Button
- Fee Category Account
- Asset Maintenance Part
- Asset Movement Item
- Depreciation Schedule
- Item Specification
- Lab Consumable Issue Item
- Maintenance Team Member
- Material Request Item
- Purchase Order Item
- Purchase Receipt Item
- Purchase Taxes and Charges
- Stock Entry Item
- Stock Reconciliation Item
- Grievance Action
- Grievance Attachment
- Grievance Communication
- Grievance Escalation Log
- Grievance Escalation Rule
- Dashboard Role
- Dashboard User
- Dashboard Widget
- Report Access Role
- Report Column Definition
- Report Filter Definition
- Report Join Definition
- Scheduled Report Recipient
- Feedback Answer
- Feedback Course Filter
- Feedback Department Filter
- Feedback Form Section
- Feedback Program Filter
- Feedback Question
- Feedback Section Score

</details>

### Faculty (Instructor)

No test user available -- skipped.

### Student (Student)

Access to 0/268 doctypes.

<details><summary>No access (268 doctypes)</summary>

- Batch
- Emergency Acknowledgment
- Emergency Alert
- NAAC Document Checklist Item
- NAAC Metric
- NAAC Metric Document
- NAAC Metric Year Data
- NIRF Data
- Notice Board
- Notice Target Department
- Notice Target Program
- Notice View Log
- Notification Preference
- Notification Template
- Payment Webhook Log
- Proctoring Snapshot
- Suggestion
- Suggestion Attachment
- University Department
- University Laboratory
- University Settings
- User Notification
- Course Prerequisite
- Course Registration
- Course Registration Item
- Elective Course Group
- Elective Course Group Item
- Timetable Slot
- Admission Criteria
- Admission Cycle
- Admission Cycle Program
- Merit List
- Merit List Applicant
- Seat Matrix
- Student Status Log
- University Alumni
- University Announcement
- Answer Sheet
- Answer Sheet Score
- Answer Sheet Tracking Log
- Exam Invigilator
- Exam Schedule
- External Examiner
- Generated Question Paper
- Hall Ticket
- Hall Ticket Exam
- Internal Assessment
- Internal Assessment Score
- Online Exam Student
- Online Examination
- Practical Evaluation Criteria
- Practical Exam Examiner
- Practical Exam Slot
- Practical Exam Student Score
- Practical Examination
- Question Bank
- Question Option
- Question Paper Content Section
- Question Paper Question Item
- Question Paper Section
- Question Paper Template
- Question Tag
- Question Tag Link
- Revaluation Request
- Student Answer
- Student Exam Attempt
- Student Transcript
- Transcript Semester Result
- Bulk Fee Generator
- Bulk Fee Generator Student
- Scholarship Type
- Student Scholarship
- Employee Qualification
- Faculty Award
- Faculty Profile
- Faculty Publication
- Faculty Research Project
- Leave Affected Course
- Student Feedback
- Teaching Assignment
- Teaching Assignment Schedule
- Temporary Teaching Assignment
- Workload Distributor
- Hostel Allocation
- Hostel Attendance
- Hostel Attendance Record
- Hostel Building
- Hostel Bulk Attendance
- Hostel Maintenance Request
- Hostel Mess
- Hostel Room
- Hostel Room Occupant
- Hostel Visitor
- Mess Menu
- Mess Menu Item
- Transport Allocation
- Transport Route
- Transport Route Stop
- Transport Trip Log
- Transport Vehicle
- Book Reservation
- Library Article
- Library Category
- Library Fine
- Library Member
- Library Subject
- Library Transaction
- Industry Type
- Job Eligible Program
- Placement Company
- Placement Job Opening
- Placement Round
- Resume Education
- Resume Project
- Resume Skill
- Student Resume
- Assignment Rubric Item
- Assignment Submission
- Discussion Reply
- LMS Assignment
- LMS Content
- LMS Content Progress
- LMS Course
- LMS Course Module
- LMS Discussion
- LMS Quiz
- Quiz Answer
- Quiz Attempt
- Quiz Question
- Submission File
- Submission Rubric Score
- Grant Utilization
- Project Publication Link
- Publication Author
- Research Grant
- Research Project
- Research Publication
- Research Team Member
- Accreditation Criterion
- Accreditation Cycle
- Accreditation Department Link
- Accreditation Program Link
- Accreditation Team Member
- Assessment CO Link
- Assessment Criteria Item
- Assessment Rubric
- Bloom Distribution Rule
- CO Attainment
- CO Direct Attainment
- CO Final Attainment
- CO Indirect Attainment
- CO PO Mapping
- CO PO Mapping Entry
- Committee Category Link
- Committee Member
- Course Outcome
- OBE Survey
- PO Attainment
- PO Attainment Entry
- PO Final Entry
- PO Indirect Entry
- PO PEO Mapping
- Program Educational Objective
- Program Outcome
- Survey PO Rating
- Survey Question Item
- Survey Template
- Unit Distribution Rule
- Biometric Attendance Log
- Biometric Device
- Certificate Field
- Certificate Request
- Certificate Template
- DigiLocker Document Type
- DigiLocker Issued Document
- DigiLocker Settings
- Email Queue Extended
- Payment Gateway Settings
- Payment Transaction
- Push Notification Log
- Push Notification Settings
- SMS Log
- SMS Queue
- SMS Template
- University SMS Settings
- User Device Token
- WhatsApp Log
- WhatsApp Settings
- WhatsApp Template
- WhatsApp Template Button
- Alumni
- Alumni Event
- Alumni Event Registration
- Announcement
- Job Posting
- Placement Application
- Placement Drive
- Placement Profile
- Bank Transaction
- Fee Category Account
- Fee Refund
- Payment Order
- PayU Settings
- Razorpay Settings
- University Accounts Settings
- Webhook Log
- Asset
- Asset Category
- Asset Maintenance
- Asset Maintenance Part
- Asset Movement
- Asset Movement Item
- Depreciation Schedule
- Inventory Item
- Inventory Item Group
- Item Specification
- Lab Consumable Issue
- Lab Consumable Issue Item
- Lab Equipment
- Lab Equipment Booking
- Maintenance Team
- Maintenance Team Member
- Material Request
- Material Request Item
- Purchase Order
- Purchase Order Item
- Purchase Receipt
- Purchase Receipt Item
- Purchase Taxes and Charges
- Stock Entry
- Stock Entry Item
- Stock Ledger Entry
- Stock Reconciliation
- Stock Reconciliation Item
- Supplier
- Supplier Group
- UOM
- Warehouse
- Grievance
- Grievance Action
- Grievance Attachment
- Grievance Committee
- Grievance Communication
- Grievance Escalation Log
- Grievance Escalation Rule
- Grievance Type
- Custom Dashboard
- Custom Report Definition
- Dashboard Role
- Dashboard User
- Dashboard Widget
- KPI Definition
- KPI Value
- Report Access Role
- Report Column Definition
- Report Filter Definition
- Report Join Definition
- Scheduled Report
- Scheduled Report Recipient
- Feedback Answer
- Feedback Course Filter
- Feedback Department Filter
- Feedback Form
- Feedback Form Section
- Feedback Program Filter
- Feedback Question
- Feedback Response
- Feedback Section Score

</details>

### Parent (Guardian)

Access to 0/268 doctypes.

<details><summary>No access (268 doctypes)</summary>

- Batch
- Emergency Acknowledgment
- Emergency Alert
- NAAC Document Checklist Item
- NAAC Metric
- NAAC Metric Document
- NAAC Metric Year Data
- NIRF Data
- Notice Board
- Notice Target Department
- Notice Target Program
- Notice View Log
- Notification Preference
- Notification Template
- Payment Webhook Log
- Proctoring Snapshot
- Suggestion
- Suggestion Attachment
- University Department
- University Laboratory
- University Settings
- User Notification
- Course Prerequisite
- Course Registration
- Course Registration Item
- Elective Course Group
- Elective Course Group Item
- Timetable Slot
- Admission Criteria
- Admission Cycle
- Admission Cycle Program
- Merit List
- Merit List Applicant
- Seat Matrix
- Student Status Log
- University Alumni
- University Announcement
- Answer Sheet
- Answer Sheet Score
- Answer Sheet Tracking Log
- Exam Invigilator
- Exam Schedule
- External Examiner
- Generated Question Paper
- Hall Ticket
- Hall Ticket Exam
- Internal Assessment
- Internal Assessment Score
- Online Exam Student
- Online Examination
- Practical Evaluation Criteria
- Practical Exam Examiner
- Practical Exam Slot
- Practical Exam Student Score
- Practical Examination
- Question Bank
- Question Option
- Question Paper Content Section
- Question Paper Question Item
- Question Paper Section
- Question Paper Template
- Question Tag
- Question Tag Link
- Revaluation Request
- Student Answer
- Student Exam Attempt
- Student Transcript
- Transcript Semester Result
- Bulk Fee Generator
- Bulk Fee Generator Student
- Scholarship Type
- Student Scholarship
- Employee Qualification
- Faculty Award
- Faculty Profile
- Faculty Publication
- Faculty Research Project
- Leave Affected Course
- Student Feedback
- Teaching Assignment
- Teaching Assignment Schedule
- Temporary Teaching Assignment
- Workload Distributor
- Hostel Allocation
- Hostel Attendance
- Hostel Attendance Record
- Hostel Building
- Hostel Bulk Attendance
- Hostel Maintenance Request
- Hostel Mess
- Hostel Room
- Hostel Room Occupant
- Hostel Visitor
- Mess Menu
- Mess Menu Item
- Transport Allocation
- Transport Route
- Transport Route Stop
- Transport Trip Log
- Transport Vehicle
- Book Reservation
- Library Article
- Library Category
- Library Fine
- Library Member
- Library Subject
- Library Transaction
- Industry Type
- Job Eligible Program
- Placement Company
- Placement Job Opening
- Placement Round
- Resume Education
- Resume Project
- Resume Skill
- Student Resume
- Assignment Rubric Item
- Assignment Submission
- Discussion Reply
- LMS Assignment
- LMS Content
- LMS Content Progress
- LMS Course
- LMS Course Module
- LMS Discussion
- LMS Quiz
- Quiz Answer
- Quiz Attempt
- Quiz Question
- Submission File
- Submission Rubric Score
- Grant Utilization
- Project Publication Link
- Publication Author
- Research Grant
- Research Project
- Research Publication
- Research Team Member
- Accreditation Criterion
- Accreditation Cycle
- Accreditation Department Link
- Accreditation Program Link
- Accreditation Team Member
- Assessment CO Link
- Assessment Criteria Item
- Assessment Rubric
- Bloom Distribution Rule
- CO Attainment
- CO Direct Attainment
- CO Final Attainment
- CO Indirect Attainment
- CO PO Mapping
- CO PO Mapping Entry
- Committee Category Link
- Committee Member
- Course Outcome
- OBE Survey
- PO Attainment
- PO Attainment Entry
- PO Final Entry
- PO Indirect Entry
- PO PEO Mapping
- Program Educational Objective
- Program Outcome
- Survey PO Rating
- Survey Question Item
- Survey Template
- Unit Distribution Rule
- Biometric Attendance Log
- Biometric Device
- Certificate Field
- Certificate Request
- Certificate Template
- DigiLocker Document Type
- DigiLocker Issued Document
- DigiLocker Settings
- Email Queue Extended
- Payment Gateway Settings
- Payment Transaction
- Push Notification Log
- Push Notification Settings
- SMS Log
- SMS Queue
- SMS Template
- University SMS Settings
- User Device Token
- WhatsApp Log
- WhatsApp Settings
- WhatsApp Template
- WhatsApp Template Button
- Alumni
- Alumni Event
- Alumni Event Registration
- Announcement
- Job Posting
- Placement Application
- Placement Drive
- Placement Profile
- Bank Transaction
- Fee Category Account
- Fee Refund
- Payment Order
- PayU Settings
- Razorpay Settings
- University Accounts Settings
- Webhook Log
- Asset
- Asset Category
- Asset Maintenance
- Asset Maintenance Part
- Asset Movement
- Asset Movement Item
- Depreciation Schedule
- Inventory Item
- Inventory Item Group
- Item Specification
- Lab Consumable Issue
- Lab Consumable Issue Item
- Lab Equipment
- Lab Equipment Booking
- Maintenance Team
- Maintenance Team Member
- Material Request
- Material Request Item
- Purchase Order
- Purchase Order Item
- Purchase Receipt
- Purchase Receipt Item
- Purchase Taxes and Charges
- Stock Entry
- Stock Entry Item
- Stock Ledger Entry
- Stock Reconciliation
- Stock Reconciliation Item
- Supplier
- Supplier Group
- UOM
- Warehouse
- Grievance
- Grievance Action
- Grievance Attachment
- Grievance Committee
- Grievance Communication
- Grievance Escalation Log
- Grievance Escalation Rule
- Grievance Type
- Custom Dashboard
- Custom Report Definition
- Dashboard Role
- Dashboard User
- Dashboard Widget
- KPI Definition
- KPI Value
- Report Access Role
- Report Column Definition
- Report Filter Definition
- Report Join Definition
- Scheduled Report
- Scheduled Report Recipient
- Feedback Answer
- Feedback Course Filter
- Feedback Department Filter
- Feedback Form
- Feedback Form Section
- Feedback Program Filter
- Feedback Question
- Feedback Response
- Feedback Section Score

</details>

### HOD (HOD)

No test user available -- skipped.

### VC (University VC)

No test user available -- skipped.

### Dean (University Dean)

No test user available -- skipped.

### Registrar (University Registrar)

Access to 13/268 doctypes.

| Doctype | Module | R | W | C | D |
|---------|--------|---|---|---|---|
| Course Registration | University Academics | Y | Y | Y | Y |
| Elective Course Group | University Academics | Y | Y | Y | Y |
| Timetable Slot | University Academics | Y | Y | Y | Y |
| Admission Criteria | University Admissions | Y | Y | Y | Y |
| Admission Cycle | University Admissions | Y | Y | Y | Y |
| Merit List | University Admissions | Y | Y | Y | Y |
| Seat Matrix | University Admissions | Y | Y | Y | Y |
| Student Status Log | University Student Info | Y | Y | Y | Y |
| University Alumni | University Student Info | Y | Y | Y | Y |
| University Announcement | University Student Info | Y | Y | Y | Y |
| Bulk Fee Generator | University Finance | Y | - | - | - |
| Scholarship Type | University Finance | Y | - | - | - |
| Student Scholarship | University Finance | Y | - | - | - |

<details><summary>No access (255 doctypes)</summary>

- Batch
- Emergency Acknowledgment
- Emergency Alert
- NAAC Document Checklist Item
- NAAC Metric
- NAAC Metric Document
- NAAC Metric Year Data
- NIRF Data
- Notice Board
- Notice Target Department
- Notice Target Program
- Notice View Log
- Notification Preference
- Notification Template
- Payment Webhook Log
- Proctoring Snapshot
- Suggestion
- Suggestion Attachment
- University Department
- University Laboratory
- University Settings
- User Notification
- Course Prerequisite
- Course Registration Item
- Elective Course Group Item
- Admission Cycle Program
- Merit List Applicant
- Answer Sheet
- Answer Sheet Score
- Answer Sheet Tracking Log
- Exam Invigilator
- Exam Schedule
- External Examiner
- Generated Question Paper
- Hall Ticket
- Hall Ticket Exam
- Internal Assessment
- Internal Assessment Score
- Online Exam Student
- Online Examination
- Practical Evaluation Criteria
- Practical Exam Examiner
- Practical Exam Slot
- Practical Exam Student Score
- Practical Examination
- Question Bank
- Question Option
- Question Paper Content Section
- Question Paper Question Item
- Question Paper Section
- Question Paper Template
- Question Tag
- Question Tag Link
- Revaluation Request
- Student Answer
- Student Exam Attempt
- Student Transcript
- Transcript Semester Result
- Bulk Fee Generator Student
- Employee Qualification
- Faculty Award
- Faculty Profile
- Faculty Publication
- Faculty Research Project
- Leave Affected Course
- Student Feedback
- Teaching Assignment
- Teaching Assignment Schedule
- Temporary Teaching Assignment
- Workload Distributor
- Hostel Allocation
- Hostel Attendance
- Hostel Attendance Record
- Hostel Building
- Hostel Bulk Attendance
- Hostel Maintenance Request
- Hostel Mess
- Hostel Room
- Hostel Room Occupant
- Hostel Visitor
- Mess Menu
- Mess Menu Item
- Transport Allocation
- Transport Route
- Transport Route Stop
- Transport Trip Log
- Transport Vehicle
- Book Reservation
- Library Article
- Library Category
- Library Fine
- Library Member
- Library Subject
- Library Transaction
- Industry Type
- Job Eligible Program
- Placement Company
- Placement Job Opening
- Placement Round
- Resume Education
- Resume Project
- Resume Skill
- Student Resume
- Assignment Rubric Item
- Assignment Submission
- Discussion Reply
- LMS Assignment
- LMS Content
- LMS Content Progress
- LMS Course
- LMS Course Module
- LMS Discussion
- LMS Quiz
- Quiz Answer
- Quiz Attempt
- Quiz Question
- Submission File
- Submission Rubric Score
- Grant Utilization
- Project Publication Link
- Publication Author
- Research Grant
- Research Project
- Research Publication
- Research Team Member
- Accreditation Criterion
- Accreditation Cycle
- Accreditation Department Link
- Accreditation Program Link
- Accreditation Team Member
- Assessment CO Link
- Assessment Criteria Item
- Assessment Rubric
- Bloom Distribution Rule
- CO Attainment
- CO Direct Attainment
- CO Final Attainment
- CO Indirect Attainment
- CO PO Mapping
- CO PO Mapping Entry
- Committee Category Link
- Committee Member
- Course Outcome
- OBE Survey
- PO Attainment
- PO Attainment Entry
- PO Final Entry
- PO Indirect Entry
- PO PEO Mapping
- Program Educational Objective
- Program Outcome
- Survey PO Rating
- Survey Question Item
- Survey Template
- Unit Distribution Rule
- Biometric Attendance Log
- Biometric Device
- Certificate Field
- Certificate Request
- Certificate Template
- DigiLocker Document Type
- DigiLocker Issued Document
- DigiLocker Settings
- Email Queue Extended
- Payment Gateway Settings
- Payment Transaction
- Push Notification Log
- Push Notification Settings
- SMS Log
- SMS Queue
- SMS Template
- University SMS Settings
- User Device Token
- WhatsApp Log
- WhatsApp Settings
- WhatsApp Template
- WhatsApp Template Button
- Alumni
- Alumni Event
- Alumni Event Registration
- Announcement
- Job Posting
- Placement Application
- Placement Drive
- Placement Profile
- Bank Transaction
- Fee Category Account
- Fee Refund
- Payment Order
- PayU Settings
- Razorpay Settings
- University Accounts Settings
- Webhook Log
- Asset
- Asset Category
- Asset Maintenance
- Asset Maintenance Part
- Asset Movement
- Asset Movement Item
- Depreciation Schedule
- Inventory Item
- Inventory Item Group
- Item Specification
- Lab Consumable Issue
- Lab Consumable Issue Item
- Lab Equipment
- Lab Equipment Booking
- Maintenance Team
- Maintenance Team Member
- Material Request
- Material Request Item
- Purchase Order
- Purchase Order Item
- Purchase Receipt
- Purchase Receipt Item
- Purchase Taxes and Charges
- Stock Entry
- Stock Entry Item
- Stock Ledger Entry
- Stock Reconciliation
- Stock Reconciliation Item
- Supplier
- Supplier Group
- UOM
- Warehouse
- Grievance
- Grievance Action
- Grievance Attachment
- Grievance Committee
- Grievance Communication
- Grievance Escalation Log
- Grievance Escalation Rule
- Grievance Type
- Custom Dashboard
- Custom Report Definition
- Dashboard Role
- Dashboard User
- Dashboard Widget
- KPI Definition
- KPI Value
- Report Access Role
- Report Column Definition
- Report Filter Definition
- Report Join Definition
- Scheduled Report
- Scheduled Report Recipient
- Feedback Answer
- Feedback Course Filter
- Feedback Department Filter
- Feedback Form
- Feedback Form Section
- Feedback Program Filter
- Feedback Question
- Feedback Response
- Feedback Section Score

</details>

### Finance (University Finance Officer)

No test user available -- skipped.

## API Permission Matrix

| Endpoint | Description | Admin | Faculty | Student | Parent | HOD | VC | Dean | Registrar | Finance |
|----------|-------------|----|----|----|----|----|----|----|----|----|
| `get_faculty_dashboard` | Faculty dashboard (should need faculty user) | DENIED | NO_USER | DENIED | DENIED | NO_USER | NO_USER | NO_USER | DENIED | NO_USER |
| `get_session_info` | Session info (should work for all logged-in users) | PASS | NO_USER | PASS | PASS | NO_USER | NO_USER | NO_USER | PASS | NO_USER |
| `get_available_dashboards` | Analytics dashboards (management + admin) | PASS | NO_USER | PASS | PASS | NO_USER | NO_USER | NO_USER | PASS | NO_USER |
| `run_checks` | Health checks (System Manager only) | PASS | NO_USER | DENIED | DENIED | NO_USER | NO_USER | NO_USER | DENIED | NO_USER |
| `get_profile` | Student profile API v1 (Student + Admin) | PASS | NO_USER | PASS | PASS | NO_USER | NO_USER | NO_USER | PASS | NO_USER |
| `get_dashboard_stats` | Admin dashboard stats (System Manager only) | PASS | NO_USER | PASS | PASS | NO_USER | NO_USER | NO_USER | PASS | NO_USER |
| `get_quick_stats` | Quick stats (needs Custom Dashboard read) | PASS | NO_USER | DENIED | DENIED | NO_USER | NO_USER | NO_USER | DENIED | NO_USER |
| `get_portal_redirect` | Portal redirect (guest allowed) | PASS | NO_USER | PASS | PASS | NO_USER | NO_USER | NO_USER | PASS | NO_USER |

## Security Findings

**Total findings:** 2 (HIGH: 2, MEDIUM: 0, LOW: 0)

| # | Severity | Role | Resource | Finding | Permissions |
|---|----------|------|----------|---------|-------------|
| 1 | HIGH | Student | API: university_erp.university_erp.analytics.api.get_available_dashboards | Student can access get_available_dashboards (expected DENIED, got PASS) | Status: PASS |
| 2 | HIGH | Student | API: university_erp.university_erp.api.v1.admin.get_dashboard_stats | Student can access get_dashboard_stats (expected DENIED, got PASS) | Status: PASS |

## Missing Users

The following roles have no test user in the system:

- **Instructor** (Faculty): No user with this role found
- **HOD** (HOD): No user with this role found
- **University VC** (VC): No user with this role found
- **University Dean** (Dean): No user with this role found
- **University Finance Officer** (Finance): No user with this role found

Create test users with these roles for complete coverage.
