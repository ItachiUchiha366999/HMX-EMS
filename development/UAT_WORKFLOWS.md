# Workflow UAT — University ERP (ems.hanumatrix.com)

**Total workflows:** 24  
**Test site:** https://ems.hanumatrix.com  
**All roles are University-specific** — no generic Frappe roles remain.

---

## Role Reference

| Role | Who plays this in UAT |
|---|---|
| University Faculty | Any faculty user (e.g. faculty1@nit.edu) |
| University HOD | Department head user |
| University HR Admin | HR admin user |
| University Admin | General admin / registrar office staff |
| University Registrar | Senior registrar |
| University Finance | Finance department user |
| University Exam Cell | Exam controller user |
| University Warden | Hostel warden user |
| University Placement Officer | Placement cell user |
| University Student | Student user (e.g. student1@nit.edu) |

---

## HR / Faculty Workflows

---

### WF-01 · Leave Application Workflow

**DocType:** Leave Application  
**States:** Draft → Pending HOD Approval → Pending HR Approval → Approved / Rejected / Cancelled  
**Email alerts:** Yes

#### Happy path
| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create leave application | University Faculty | Fill leave type, from/to dates, reason. Save. | Status = **Draft** |
| 2 | Submit for approval | University Faculty | Click **Submit for Approval** | Status = **Pending HOD Approval**. HOD gets email alert. |
| 3 | HOD approves | University HOD | Open doc, click **Approve** | Status = **Pending HR Approval**. HR Admin gets email. |
| 4 | HR approves | University HR Admin | Click **Approve** | Status = **Approved**, docstatus = Submitted (1). |

#### Rejection path
| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1–2 | Same as above | — | — | Status = **Pending HOD Approval** |
| 3 | HOD rejects | University HOD | Click **Reject** | Status = **Rejected**. Faculty notified. |

#### Send-back path
| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1–3 | Reach HR Approval | — | — | Status = **Pending HR Approval** |
| 4 | HR sends back | University HR Admin | Click **Send Back to HOD** | Status = **Pending HOD Approval** again |
| 5 | HOD re-approves | University HOD | Click **Approve** | Proceeds to HR Approval |

#### Cancel path
| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Reach Approved state | — | — | docstatus = 1 |
| 2 | Cancel | University HR Admin | Click **Cancel** | Status = **Cancelled**, docstatus = 2 |

#### Negative tests
- Faculty cannot approve/reject (action buttons not visible)
- HOD cannot skip straight to HR Approval state

---

### WF-02 · Teaching Assignment Approval Workflow

**DocType:** Teaching Assignment  
**States:** Draft → Pending Faculty Acceptance → Pending HOD Approval → Pending Academic Registrar Approval → Approved / Rejected / Cancelled  
**Email alerts:** Yes

#### Happy path
| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create assignment | University Admin | Assign course + faculty. Save. | Status = **Draft** |
| 2 | Send to faculty | University Admin | Click **Send to Faculty** | Status = **Pending Faculty Acceptance** |
| 3 | Faculty accepts | University Faculty | Click **Accept** | Status = **Pending HOD Approval** |
| 4 | HOD approves | University HOD | Click **Approve** | Status = **Pending Academic Registrar Approval** |
| 5 | Registrar approves | University Registrar | Click **Approve** | Status = **Approved**, docstatus = 1 |

#### Decline and Send-back paths
| Step | Actor | Action | Expected result |
|---|---|---|---|
| Faculty declines | University Faculty | **Decline** from Pending Faculty Acceptance | Status = **Rejected** |
| HOD sends back | University HOD | **Send Back to Faculty** | Returns to Pending Faculty Acceptance |
| Registrar sends back | University Registrar | **Send Back to HOD** | Returns to Pending HOD Approval |

#### Negative tests
- Faculty cannot approve on HOD's behalf
- Admin cannot skip the faculty acceptance step

---

## Finance Workflows

---

### WF-03 · Fee Refund Approval Workflow

**DocType:** Fee Refund  
**States:** Pending → Pending Approval → Approved → Processed / Rejected / Cancelled  
**Email alerts:** Yes

#### Happy path
| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create refund request | University Finance | Fill student, amount, reason. Save. | Status = **Pending** |
| 2 | Submit for approval | University Finance | **Submit for Approval** | Status = **Pending Approval** |
| 3 | Approve | University Finance (senior) | **Approve** | Status = **Approved** |
| 4 | Process refund | University Finance | **Process Refund** | Status = **Processed**, docstatus = 1 |

#### Rejection & reconsideration
| Step | Actor | Action | Expected result |
|---|---|---|---|
| Reject | University Finance | **Reject** from Pending Approval | Status = **Rejected** |
| Reconsider | University Finance | **Reconsider** from Rejected | Returns to **Pending Approval** |
| Return to draft | University Finance | **Return to Draft** | Back to **Pending** |

---

### WF-04 · Journal Entry Approval

**DocType:** Journal Entry  
**States:** Draft → Pending Finance Approval → Approved / Rejected / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create JE | University Finance | Fill accounts, amounts. Save. | Status = **Draft** |
| 2 | Submit for approval | University Finance | **Submit for Approval** | Status = **Pending Finance Approval** |
| 3 | Approve | University Finance | **Approve** | Status = **Approved**, docstatus = 1 |
| 4 | Cancel | University Finance | **Cancel** | Status = **Cancelled**, docstatus = 2 |

**Negative:** Finance staff cannot self-approve (allow_self_approval = 0 on Approve transition).

---

### WF-05 · Payment Entry Approval

**DocType:** Payment Entry  
**States:** Draft → Pending Finance Approval → Approved / Rejected / Cancelled

Identical flow to WF-04. Verify same role restrictions apply.

---

## Hostel & Transport Workflows

---

### WF-06 · Hostel Allocation Approval

**DocType:** Hostel Allocation  
**States:** Draft → Pending Warden Approval → Approved / Rejected / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create allocation | University Admin | Assign student + room. Save. | Status = **Draft** |
| 2 | Submit for warden | University Admin | **Submit for Warden Approval** | Status = **Pending Warden Approval** |
| 3 | Warden approves | University Warden | **Approve** | Status = **Approved**, docstatus = 1 |
| 4 | Warden rejects | University Warden | **Reject** | Status = **Rejected** |

---

### WF-07 · Hostel Maintenance Request Workflow

**DocType:** Hostel Maintenance Request  
**States:** Open → Assigned → In Progress → Completed / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Raise request | University Warden | Fill issue details. Save. | Status = **Open** |
| 2 | Assign | University Warden | **Assign** (pick maintenance staff) | Status = **Assigned** |
| 3 | Start work | University Warden | **Start Work** | Status = **In Progress** |
| 4 | Complete | University Warden | **Complete** | Status = **Completed**, docstatus = 1 |

**Cancel path:** Cancel from Open or Assigned → Status = **Cancelled**

---

### WF-08 · Transport Allocation Approval

**DocType:** Transport Allocation  
**States:** Draft → Pending Approval → Active / Rejected / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create allocation | University Admin | Assign student + route. Save. | Status = **Draft** |
| 2 | Submit | University Admin | **Submit for Approval** | Status = **Pending Approval** |
| 3 | Approve | University Registrar | **Approve** | Status = **Active**, docstatus = 1 |
| 4 | Reject | University Registrar | **Reject** | Status = **Rejected** |
| 5 | Cancel active | University Registrar | **Cancel** from Active | Status = **Cancelled**, docstatus = 2 |

---

## Student Services Workflows

---

### WF-09 · Certificate Request Workflow

**DocType:** Certificate Request  
**States:** Pending → Approved → Generated → Issued / Rejected / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Student requests | University Student (portal) | Submit certificate request | Status = **Pending** |
| 2 | Registrar approves | University Registrar | **Approve** | Status = **Approved** |
| 3 | Admin generates | University Admin | **Generate** | Status = **Generated** |
| 4 | Registrar issues | University Registrar | **Issue** | Status = **Issued**, docstatus = 1 |

**Rejection:** Registrar → **Reject** from Pending → Status = **Rejected**  
**Cancel:** Registrar → **Cancel** from Approved → Status = **Cancelled**

---

### WF-10 · Course Registration Workflow

**DocType:** Course Registration  
**States:** Draft → Pending Faculty Approval → Approved / Rejected

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Student registers | University Admin | Create course registration. Save. | Status = **Draft** |
| 2 | Submit | University Admin | **Submit for Approval** | Status = **Pending Faculty Approval** |
| 3 | Approve | University Registrar | **Approve** | Status = **Approved**, docstatus = 1 |
| 4 | Reject | University Registrar | **Reject** | Status = **Rejected** |

---

### WF-11 · Student Scholarship Workflow

**DocType:** Student Scholarship  
**States:** Draft → Under Verification → Approved → Disbursed / Rejected / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create scholarship | University Registrar | Fill student + amount. Save. | Status = **Draft** |
| 2 | Submit for verification | University Registrar | **Submit for Verification** | Status = **Under Verification** |
| 3 | Finance approves | University Finance | **Approve** | Status = **Approved**, docstatus = 1 |
| 4 | Finance disburses | University Finance | **Disburse** | Status = **Disbursed** |

**Rejection:** Finance → **Reject** → Status = **Rejected**  
**Cancel:** Registrar → **Cancel** from Approved → Status = **Cancelled**

---

## Admissions Workflows

---

### WF-12 · Student Admission Workflow

**DocType:** Student Applicant  
**States:** Applied → Document Verification → Shortlisted → Admitted / Rejected / Withdrawn  
**Email alerts:** Yes

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Application received | — | Applicant submits online. | Status = **Applied** |
| 2 | Verify documents | University Registrar | **Verify Documents** | Status = **Document Verification** |
| 3 | Shortlist | University Registrar | **Shortlist** | Status = **Shortlisted** |
| 4 | Admit | University Registrar | **Admit** | Status = **Admitted** |
| 5 | Withdraw | University Registrar | **Withdraw** from Admitted | Status = **Withdrawn** |

**Rejection path:** Reject from Document Verification or Shortlisted → **Rejected**  
**Reconsider:** Registrar → **Reconsider** from Rejected → Back to **Document Verification**

---

### WF-13 · Merit List Workflow

**DocType:** Merit List  
**States:** Draft → Pending Publication → Published → Expired

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create merit list | University Admin | Fill program + ranked applicants. Save. | Status = **Draft** |
| 2 | Submit for publication | University Admin | **Submit for Publication** | Status = **Pending Publication** |
| 3 | Publish | University Registrar | **Publish** | Status = **Published**, docstatus = 1 |
| 4 | Expire | University Registrar | **Mark Expired** | Status = **Expired** |

---

## Placement Workflow

---

### WF-14 · Placement Application Workflow

**DocType:** Placement Application  
**States:** Applied → Screening → Shortlisted → Interview Scheduled → Offer Received → Accepted / Rejected / Withdrawn  
**Email alerts:** Yes

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Student applies | University Student | Apply for job posting via portal. | Status = **Applied** |
| 2 | Screening | University Placement Officer | **Start Screening** | Status = **Screening** |
| 3 | Shortlist | University Placement Officer | **Shortlist** | Status = **Shortlisted** |
| 4 | Schedule interview | University Placement Officer | **Schedule Interview** | Status = **Interview Scheduled** |
| 5 | Mark offer | University Placement Officer | **Mark Offer Received** | Status = **Offer Received** |
| 6 | Accept | University Placement Officer | **Accept Offer** | Status = **Accepted** |

**Rejection:** Placement Officer → **Reject** at any stage → **Rejected**  
**Withdraw:** Student → **Withdraw** from Applied → **Withdrawn**  
**Decline offer:** Placement Officer → **Decline Offer** from Offer Received → **Withdrawn**

---

## Examinations Workflows

---

### WF-15 · Hall Ticket Workflow

**DocType:** Hall Ticket  
**States:** Draft → Eligibility Check → Issued / Withheld / Cancelled  
**Email alerts:** Yes

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Generate hall ticket | University Exam Cell | Create for student + term. Save. | Status = **Draft** |
| 2 | Submit for check | University Exam Cell | **Submit for Eligibility Check** | Status = **Eligibility Check** |
| 3 | Issue | University Exam Cell | **Issue** | Status = **Issued**, docstatus = 1 |
| 4 | Withhold (dues/shortage) | University Exam Cell | **Withhold** | Status = **Withheld** |
| 5 | Release withheld | University Exam Cell | **Release** from Withheld | Status = **Issued** |
| 6 | Cancel | University Exam Cell | **Cancel** from Issued | Status = **Cancelled**, docstatus = 2 |

**Verify portal:** After status = Issued, student portal download hall ticket should work.

---

### WF-16 · Internal Assessment Workflow

**DocType:** Internal Assessment  
**States:** Draft → Marks Entry → Pending HOD Review → Finalised / Rejected / Cancelled  
**Email alerts:** Yes

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create IA | University Faculty | Create for course + term. Save. | Status = **Draft** |
| 2 | Open marks entry | University Faculty | **Start Marks Entry** | Status = **Marks Entry** |
| 3 | Submit to HOD | University Faculty | **Submit for HOD Review** | Status = **Pending HOD Review** |
| 4 | HOD finalises | University HOD | **Finalise** | Status = **Finalised**, docstatus = 1 |

**Send back:** HOD → **Send Back for Correction** → Returns to **Marks Entry**  
**Reject:** HOD → **Reject** → Status = **Rejected**  
**Cancel:** Exam Cell → **Cancel** from Finalised → **Cancelled**

---

### WF-17 · Practical Examination Workflow

**DocType:** Practical Examination  
**States:** Draft → Scheduled → In Progress → Marks Submitted → Finalised / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create | University Exam Cell | Fill course + date + examiners. Save. | Status = **Draft** |
| 2 | Schedule | University Exam Cell | **Schedule** | Status = **Scheduled** |
| 3 | Start exam | University Faculty | **Start** | Status = **In Progress** |
| 4 | Submit marks | University Faculty | **Submit Marks** | Status = **Marks Submitted** |
| 5 | HOD finalises | University HOD | **Finalise** | Status = **Finalised**, docstatus = 1 |
| 6 | Cancel | University Exam Cell | **Cancel** from Finalised | Status = **Cancelled**, docstatus = 2 |

**Send back:** HOD → **Send Back for Correction** from Marks Submitted → **In Progress**

---

### WF-18 · Generated Question Paper Workflow

**DocType:** Generated Question Paper  
**States:** Draft → Ready for Review → Approved → Locked / Rejected

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Generate paper | University Exam Cell | Generate from question bank. Save. | Status = **Draft** |
| 2 | Submit for review | University Exam Cell | **Submit for Review** | Status = **Ready for Review** |
| 3 | Approve | University Registrar | **Approve** | Status = **Approved**, docstatus = 1 |
| 4 | Lock | University Exam Cell | **Lock** | Status = **Locked** |
| 5 | Reject | University Registrar | **Reject** from Ready for Review | Status = **Rejected** |

**Security check:** Verify that a non-Exam Cell user cannot see the question paper content after it is Locked.

---

### WF-19 · Revaluation Request Workflow

**DocType:** Revaluation Request  
**States:** Draft → Pending Review → In Progress → Completed / Rejected

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Student raises request | University Admin | Create for student + exam. Save. | Status = **Draft** |
| 2 | Submit | University Admin | **Submit for Review** | Status = **Pending Review** |
| 3 | Accept | University Exam Cell | **Accept** | Status = **In Progress** |
| 4 | Complete | University Exam Cell | **Complete** | Status = **Completed**, docstatus = 1 |
| 5 | Reject | University Exam Cell | **Reject** from Pending Review | Status = **Rejected** |

---

### WF-20 · Lab Equipment Booking Workflow

**DocType:** Lab Equipment Booking  
**States:** Pending → Approved → In Use → Completed / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Request booking | University Admin | Fill equipment + date + requester. Save. | Status = **Pending** |
| 2 | Approve | University Registrar | **Approve** | Status = **Approved** |
| 3 | Start use | University Admin | **Start Use** | Status = **In Use** |
| 4 | Complete | University Admin | **Complete** | Status = **Completed**, docstatus = 1 |
| 5 | Cancel pending | University Registrar | **Cancel** from Pending | Status = **Cancelled** |

---

## Research & Governance

---

### WF-21 · Research Grant Workflow

**DocType:** Research Grant  
**States:** Draft → Under Review → Approved → Completed / Rejected

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create grant proposal | University Admin | Fill PI, funding body, amount. Save. | Status = **Draft** |
| 2 | Submit for review | University Admin | **Submit for Review** | Status = **Under Review** |
| 3 | Approve | University Registrar | **Approve** | Status = **Approved**, docstatus = 1 |
| 4 | Complete | University Registrar | **Mark Completed** | Status = **Completed** |
| 5 | Reject | University Registrar | **Reject** from Under Review | Status = **Rejected** |

---

### WF-22 · Grievance Resolution Workflow

**DocType:** Grievance  
**States:** Draft → Submitted → Under Review → Resolution Proposed → Resolved → Closed / Rejected

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Lodge grievance | University Admin | Fill student + description. Save. | Status = **Draft** |
| 2 | Submit | University Admin | **Submit** | Status = **Submitted** |
| 3 | Take up | University Registrar | **Take Up for Review** | Status = **Under Review** |
| 4 | Propose resolution | University Registrar | **Propose Resolution** | Status = **Resolution Proposed** |
| 5 | Accept | University Admin | **Accept Resolution** | Status = **Resolved** |
| 6 | Close | University Registrar | **Close** | Status = **Closed** |

**Rejection:** Registrar → **Reject** from Under Review → **Rejected**  
**Reopen:** Registrar → **Reopen** from Resolved → **Under Review**

---

## Procurement Workflows

---

### WF-23 · Purchase Order Approval

**DocType:** Purchase Order  
**States:** Draft → Pending HOD Approval → Pending Finance Approval → Approved / Rejected / Cancelled  
**Email alerts:** Yes

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Create PO | University Admin | Fill supplier + items. Save. | Status = **Draft** |
| 2 | Submit to HOD | University Admin | **Submit for HOD Approval** | Status = **Pending HOD Approval** |
| 3 | HOD approves | University HOD | **Approve** | Status = **Pending Finance Approval** |
| 4 | Finance approves | University Finance | **Approve** | Status = **Approved**, docstatus = 1 |
| 5 | Cancel | University Finance | **Cancel** from Approved | Status = **Cancelled**, docstatus = 2 |

**Send back:** Finance → **Send Back to HOD** → Returns to **Pending HOD Approval**  
**Rejection:** HOD or Finance → **Reject** → **Rejected**

---

### WF-24 · Material Request Approval

**DocType:** Material Request  
**States:** Draft → Pending HOD Approval → Approved / Rejected / Cancelled

| # | Step | Actor | Action | Expected result |
|---|---|---|---|---|
| 1 | Raise request | University Admin | Fill department + items required. Save. | Status = **Draft** |
| 2 | Submit to HOD | University Admin | **Submit for HOD Approval** | Status = **Pending HOD Approval** |
| 3 | HOD approves | University HOD | **Approve** | Status = **Approved**, docstatus = 1 |
| 4 | HOD rejects | University HOD | **Reject** | Status = **Rejected** |
| 5 | Cancel | University HOD | **Cancel** from Approved | Status = **Cancelled**, docstatus = 2 |

---

## Cross-Cutting Checks

These apply to every workflow above:

| Check | How to verify |
|---|---|
| **Role isolation** | Log in as University Faculty. Verify you cannot see Approve/Reject buttons on docs pending HOD or Finance action. |
| **No action buttons in wrong state** | Open a doc in "Approved" state. Confirm only the allowed next actions (e.g. Cancel) appear, not transitions from earlier states. |
| **Email alerts** | On workflows with `send_email_alert = 1`, trigger a state change and confirm the next approver receives a Frappe notification / email. |
| **Workflow state field visible** | In any workflow-enabled doctype, confirm the `Workflow State` field badge is visible on the form. |
| **docstatus integrity** | Submitted docs (docstatus = 1) should not be editable except via allowed workflow actions. |
| **Cancel only from submitted** | Verify Cancel action (→ docstatus = 2) is only reachable from a docstatus = 1 state, never from docstatus = 0. |
| **Idempotency** | Re-run `bench execute university_erp.setup.create_workflows.run` — confirm it prints "Active workflow already exists" for all 24 and creates 0 new ones. |
