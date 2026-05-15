---
slug: education-fork-duplicate-audit
status: complete
created: 2026-05-15
completed: 2026-05-15
phase_context: post-03.3.1 audit
---

# Education Fork — Duplicate DocType Audit (Findings + Actions)

## Triggering observation

User flagged `Course Enrollment` vs `Course Registration` as a likely
duplicate after the phase 03.3.1 Education-app fork landed 71 doctypes
into university_erp.

## Method

1. Inventoried all university_erp doctypes (active + archived) across
   17 modules — JSON `name`, `module`, `istable` per doctype.
2. Cross-referenced 71 forked doctype names against pre-existing
   university_erp counterparts.
3. For each suspect pair: compared field schemas, traced incoming
   references via grep across `*.py` and `*.json`, checked DB row
   counts, and inspected git blame for provenance.
4. Classified into HIGH / MEDIUM / LOW confidence.
5. Confirmed removal scope with user before deleting.

## HIGH-confidence findings

| # | Doctype | Verdict | Action | Commit |
|---|---|---|---|---|
| 1 | `Student Siblings` (3-field child) | Duplicate of `Student Sibling` (8-field child). Zero functional consumers — only its own JSON + fork test scaffold referenced it. The actively-used sibling child everywhere (Student, Student Applicant, web form) is `Student Sibling`. DB row count = 0. | **REMOVED**: dir, DocType row, `tabStudent Siblings` table, fork-test scaffold reference | `chore(03.3.1): remove Student Siblings duplicate child doctype` |
| 2 | `university_academics/doctype/teaching_assignment/` (orphan skeleton) | Same DocType `name='Teaching Assignment'` as the production version in `faculty_management/`. Frappe's loader picked one (Faculty Management's, 19 fields with workflow + schedule child + Employee linkage); the academics 9-field skeleton was silently ignored on every migrate. Zero Python imports. Created in same early commit (33eec628) as the faculty version — pre-dates phase 03.3.1, so it was an early scaffolding leftover, not a fork artifact. | **REMOVED**: orphan directory only. No DB change needed (DB row pointed at faculty version). | `chore: remove dead Teaching Assignment skeleton from university_academics` |
| 3 | `Course Enrollment` (forked) — initially flagged | **REVERSED**: NOT a duplicate. Course Registration is the student-submitted form with workflow; Course Enrollment is the system-generated record (one row per student×course) materialized by `course_registration.py:38-81` when the workflow hits Approved. Course Enrollment is consumed by 30+ files: examinations (hall_ticket, transcript, internal_assessment, practical_examination, result_entry), portals (faculty_api, portal_api), student.py, program_enrollment.py, course_activity.py, feedback, KPIs, accreditation/naac_data_collector, scheduled_tasks, dashboards, attendance, demo seed scripts. Removing it would break the system. | **KEPT** | n/a |

## MEDIUM-confidence findings (kept after inspection)

| Pair | Why they look like duplicates | Why they aren't |
|---|---|---|
| `Student Guardian` ↔ `Guardian Student` (both forked children) | Symmetric naming | Intentional inverse children of a many-to-many: Student → Guardians (via Student Guardian), Guardian → Students (via Guardian Student). Both parent doctypes embed the relevant side. |
| `Topic` ↔ `Course Topic` | Similar names | Topic is a master DocType; Course Topic is a child table inside Topic listing per-course assignments. Parent + child of the same hierarchy. |
| `Room` (in `university_student_info/`) ↔ `Hostel Room` (in `university_hostel/`) | Both about "rooms" | Different domains. `Room` = generic classroom (3 fields). `Hostel Room` = dorm room (8 fields, building/floor/beds/occupancy). Future cleanup: rename `Room` → `Classroom`. |
| `Program Enrollment` ↔ `Course Registration` | Both "registrations" | Different granularity & lifecycle. Program Enrollment = student–program–year (long-lived). Course Registration = per-term course list with workflow. |
| `Program Enrollment Fee` ↔ `Program Fee` | Both child fee tables | Different parents (Program Enrollment vs Program). Different rollup contexts. |

## LOW-confidence findings (flagged for awareness, no action)

- `Fees` (forked Education) vs `Sales Invoice` (ERPNext) — workspace already routes "Fee Invoice" shortcut to Sales Invoice. Consolidation would be a large migration; defer.
- `Student Batch Name` — no native counterpart found, kept.
- `Education Settings` (relabeled "Academics Settings") — no native counterpart, kept.

## Verification after cleanup

- `python3 university_erp/scripts/verify_education_removable.py` → 0 violations (unchanged).
- `tabStudent Siblings` → dropped from DB.
- `Teaching Assignment` → still resolves to `Faculty Management` module (production version intact).
- `Student Sibling` (kept) → still owned by `University Student Info`.

## Future cleanup candidates (not actioned this session)

1. Rename `university_student_info/doctype/room/` → `classroom/` to disambiguate from `Hostel Room`. Requires DB rename + grep across portals/exam scheduling.
2. Evaluate `Fees` vs `Sales Invoice` consolidation as part of a future finance migration phase.
3. Audit ARCHIVE_DOCTYPES (the 7 quiz/article entries still owned by Education in DB) for whether to formally drop after Education app uninstall.

## Files changed

```
D  frappe-bench/apps/university_erp/university_erp/university_student_info/doctype/student_siblings/__init__.py
D  frappe-bench/apps/university_erp/university_erp/university_student_info/doctype/student_siblings/student_siblings.json
D  frappe-bench/apps/university_erp/university_erp/university_student_info/doctype/student_siblings/student_siblings.py
M  frappe-bench/apps/university_erp/university_erp/university_student_info/tests/test_education_fork.py
D  frappe-bench/apps/university_erp/university_erp/university_academics/doctype/teaching_assignment/__init__.py
D  frappe-bench/apps/university_erp/university_erp/university_academics/doctype/teaching_assignment/teaching_assignment.json
D  frappe-bench/apps/university_erp/university_erp/university_academics/doctype/teaching_assignment/teaching_assignment.py
```

## Lesson captured

When auditing a "duplicate-looking" pair, **trace incoming references
in controllers**, not just static-text grep. Course Enrollment looked
redundant by name + field overlap, but its controller integration with
Course Registration revealed it as the materialized output side of a
form-submission pipeline. Static name + field comparison alone would
have caused a system-breaking deletion.
