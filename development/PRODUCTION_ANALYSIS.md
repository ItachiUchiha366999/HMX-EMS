# Production Site Analysis — `ems.hanumatrix.com`

**Analyzed:** 2026-04-29
**Source of truth:** Production container `ems-backend` on `139.59.5.1` (root SSH)
**Scope:** Read-only inspection. No data modified, no commands run on the site DB.

---

## 1. Deployment topology

| Item | Value |
|---|---|
| Host | `ems.hanumatrix.com` (139.59.5.1) — `ERP-ubuntu-hanumatrix` |
| Deployment | Docker Compose (`/home/ems-erp/docker-compose.yml`) |
| Image | `ems-university:v1` (image ID `36b77944ec81`) |
| Containers | `ems-backend`, `ems-frontend`, `ems-websocket`, `ems-queue-short`, `ems-queue-long`, `ems-scheduler`, `ems-mariadb`, `ems-redis-cache`, `ems-redis-queue` |
| Frappe site | `ems.hanumatrix.com` |
| Bench path (in container) | `/home/frappe/frappe-bench` |
| Site config | `developer_mode: 0`, `allow_tests: 0` |
| DB | MariaDB 10.6 in `ems-mariadb` |

### Installed apps (`bench list-apps`)

| App | Version | Branch |
|---|---|---|
| frappe | 15.94.0 | version-15 |
| erpnext | 15.93.1 | version-15 |
| hrms | 15.54.2 | version-15 |
| education | 15.0.0 | version-15 |
| university_erp | 0.0.1 | main |

Existing backups in `/home/frappe/frappe-bench/sites/`:
- `20260312_185343-university_local-*` (db + files + private files)
- `20260318_123133-university_local-*` (db + files + private files)

> Note: the original site name was `university_local` based on backup filenames; the current site is `ems.hanumatrix.com`. No fresh backup taken in the last ~6 weeks. **Take a backup before deleting any data.**

---

## 2. Production vs local code differences

I compared `apps/university_erp` between this prod container and your local working copy.

### Same on both sides
- `modules.txt` — identical (21 modules)
- All workspaces except `University Finance`
- DocType set in: faculty_management, university_academics, university_admissions, university_analytics, university_erp (root), university_examinations, university_feedback, university_grievance, university_hostel, university_integrations, university_inventory, university_library, university_lms, university_obe, university_payments, university_placement, university_portals, university_research, university_student_info, university_transport
- Reports in every module **except** university_finance

### Different on prod
**`university_finance` module is the un-forked, lean version.** Production does NOT have the ERPNext-fork that exists locally (the one with Account, GL Entry, Journal Entry, Sales Invoice, Purchase Invoice, Bank Account, etc. baked into university_finance). On prod, those DocTypes come from the standalone `erpnext` app.

Production `university_finance/doctype/` contains only:
- `bulk_fee_generator`
- `bulk_fee_generator_student`
- `fee_category`
- `fee_refund`
- `fee_refund_deduction`
- `scholarship_type`
- `student_scholarship`

Production `university_finance/report/`:
- `fee_collection_summary`
- `fee_defaulters`
- `program_wise_fee_report`

Local has **~125 DocTypes and ~40 reports** in `university_finance` (the fork). Local also has:
- `university_finance/_archived/` — 60+ archived ERPNext-fork DocTypes
- `university_finance/_archived_reports/` — 17 archived reports
- Forked accounting DocTypes (the post-fork-backend-audit-fix work)

### Production-only finance workspace
The prod `University Finance` workspace has different cards and shortcuts. It uses **Fee Payment**, **Fee Category**, **Fee Refund**, **Razorpay Settings** as shortcuts and 4 cards: Fees, Scholarships, Payments, Reports.

### Other small diff
- Local has 1 extra subdir: `university_obe/report/co_attainment_report/co_attainment_report/co_attainment_report.json` (nested duplicate). Prod doesn't. Cosmetic.

---

## 3. Bugs / risks visible from static analysis

These are issues I can flag from code inspection alone, before you do any UI testing:

### 🔴 BUG-1 — `Fee Payment` shortcut on Finance workspace points to a non-existent DocType
The prod `University Finance` workspace has a top shortcut `Fee Payment` (and a Card link `Fee Payment` under "Fees"), but **no `Fee Payment` DocType exists in any installed app** (frappe / erpnext / hrms / education / university_erp).
- **Effect:** Clicking the shortcut/link opens a "DocType Fee Payment not found" page.
- **Likely fix:** Either (a) rename it to `Fees` (the education app's DocType) — but that's already on University Home; or (b) wire to `Payment Entry` (ERPNext); or (c) remove the shortcut.
- **Decide before demo:** what should "Fee Payment" actually mean for this client?

### 🟠 BUG-2 — Two `Fee Refund` DocTypes with the same name across modules
- `university_erp/university_finance/doctype/fee_refund/fee_refund.json` (module: `University Finance`)
- `university_erp/university_payments/doctype/fee_refund/fee_refund.json` (module: `University Payments`)

DocType `name` is `Fee Refund` in both. Frappe's DocType name is the primary key — only one can be "live" in DB. The other one's JSON metadata gets ignored on `bench migrate`.
- **Effect:** Whichever one wins becomes the schema; fields in the other module's version are silently dropped.
- **Action:** Confirm which one is the live schema in DB (`bench --site … console` → `frappe.get_meta('Fee Refund').module`). Delete the loser's `.py`/`.json` so future `bench migrate` is deterministic.

### 🟠 BUG-3 — `Accounts Settings` on Finance workspace links to `University Accounts Settings`
The Finance workspace card `Payments` has a link labeled `Accounts Settings` → `link_to: "University Accounts Settings"`. That's confusing because ERPNext also has a real DocType called `Accounts Settings` (a Single).
- **Effect:** UX confusion — clients see two "Accounts Settings" links resolving to different things.
- **Fix:** Rename label on the workspace JSON to `University Accounts Settings` for clarity.

### 🟡 ISSUE-4 — Empty card on `University Integrations` workspace
The `SMS Gateway` card has no links inside it.
- **Effect:** Empty card visible in UI.
- **Fix:** Either remove the card or add `SMS Settings` / `SMS Template` links (note: SMS Template DocType exists at `university_integrations/doctype/sms_template/`).

### 🟡 ISSUE-5 — `Assessment Rubric` placed under "Reports" card on OBE workspace
Looking at the link order, `Assessment Rubric` is sandwiched between Survey Analysis Report and the Accreditation Card Break. It's a DocType, not a report.
- **Effect:** Item appears in the wrong card.
- **Fix:** Move it under `Outcome Definitions` or its own card.

### 🟡 ISSUE-6 — `university_portals` has no workspace
DocTypes (Alumni, Job Posting, Announcement, Placement Profile, etc.) aren't reachable from any sidebar entry. They're presumably used by website portals — but there's no desk-side admin UI grouping for them.
- **Effect:** Admin has to type `/app/alumni` etc. manually.
- **Decide:** acceptable for the demo, or add a "Portals Admin" workspace?

### 🟡 ISSUE-7 — Duplicate-named DocTypes across modules
Same as BUG-2 pattern in other places (only `Fee Refund` has the actual collision; these are just for awareness):
- `Teaching Assignment` in **both** `faculty_management` and `university_academics` (both define module field correctly to one — verify in DB which wins)
- `Placement Application` and `Placement Drive` in **both** `university_placement` and `university_portals`

### 🟡 ISSUE-8 — Site name vs config drift
`backup` filenames say `university_local`; current site is `ems.hanumatrix.com`. If anything in code (cron, scheduler events, hardcoded URLs) references the old name, it'll silently fail on prod.
- **Action:** grep app for `university_local`, see if any tasks/links break.

---

## 4. Data wipe options (when you're ready)

When you say go, I can prepare a script to wipe ONLY the transactional data on prod while keeping masters. Suggested order (safe-first):

**Phase A — Transactions (always-safe to wipe):**
- Fee Refund, Bulk Fee Generator (+ child), Student Scholarship
- Hostel Attendance, Hostel Bulk Attendance, Hostel Visitor, Hostel Maintenance Request, Hostel Allocation, Mess Menu (records)
- Library Transaction, Book Reservation, Library Fine
- Transport Allocation, Transport Trip Log
- Course Registration, Internal Assessment, Practical Examination, Hall Ticket, Answer Sheet, Student Exam Attempt, Online Examination, Generated Question Paper, Revaluation Request, Student Transcript
- Placement Application, Placement Drive
- LMS Assignment Submission, Quiz Attempt, LMS Content Progress, LMS Discussion
- Feedback Response, Grievance, OBE Survey, CO Attainment, PO Attainment
- All ERPNext transactions: Sales Invoice, Payment Entry, Journal Entry, GL Entry, Stock Entry, etc.

**Phase B — Configurable masters (decide):**
- Programs, Courses, Departments, Academic Year — keep or wipe?
- Students, Student Applicants, Faculty Profiles, Employees — keep or wipe?
- Hostel Buildings/Rooms, Library Articles, Transport Routes — keep or wipe?

**Phase C — Hard reset (nuclear):** drop site + reinstall apps + restore demo seed.

Tell me which phase you want and I'll write the wipe script. I will NOT execute it without your explicit confirmation.

---

## 5. Demo workspace ordering

For demo flow, suggested workspace tour order (matches how a campus actually operates):

1. **University Home** — overview
2. **University Academics** — Programs, Admissions cycle, Course Registration
3. **Faculty Management** — assignments, leave
4. **University Examinations** — schedule, hall tickets, results
5. **University OBE** — CO/PO mapping, attainment dashboards
6. **University Hostel** — allocations, attendance
7. **University Library** — circulation, overdues
8. **University Transport** — routes, trips
9. **University Placement** — drives, statistics
10. **University LMS** — courses, quizzes
11. **University Research** — publications, grants
12. **University Inventory** — assets, lab equipment
13. **University Communication** — notices, grievances, feedback
14. **University Integrations** — payment gateway, biometric, DigiLocker
15. **University Finance** — fee category, refunds, scholarships
16. **University Analytics** — dashboards, KPIs, scheduled reports

Plan the seed data so the **first 5 in this list look polished** — those are the demo opener.
