---
phase: 03
slug: faculty-portal
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest 3.2.4 + @vue/test-utils 2.4.6 |
| **Config file** | `portal-vue/vitest.config.js` |
| **Quick run command** | `cd portal-vue && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd portal-vue && npx vitest run` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd portal-vue && npx vitest run --reporter=verbose`
- **After every plan wave:** Run `cd portal-vue && npx vitest run`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | FCTY-01 | unit | `npx vitest run src/components/faculty/__tests__/TimetableToday.test.js` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | FCTY-02 | unit | `npx vitest run src/components/faculty/__tests__/AttendanceMarker.test.js` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | FCTY-05 | unit | `npx vitest run src/components/faculty/__tests__/FacultyDashboard.test.js` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | FCTY-03 | unit | `npx vitest run src/components/faculty/__tests__/FacultyGradeGrid.test.js` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 2 | FCTY-04 | unit | `npx vitest run src/components/faculty/__tests__/StudentListView.test.js` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 2 | FCTY-07 | unit | `npx vitest run src/components/faculty/__tests__/PerformanceAnalytics.test.js` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 3 | FCTY-08 | unit | `npx vitest run src/components/faculty/__tests__/StudentLeaveQueue.test.js` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 3 | FCTY-11 | unit | `npx vitest run src/components/faculty/__tests__/LeaveBalanceCards.test.js` | ❌ W0 | ⬜ pending |
| 03-03-03 | 03 | 3 | FCTY-09 | unit | `npx vitest run src/components/faculty/__tests__/LmsContentManager.test.js` | ❌ W0 | ⬜ pending |
| 03-03-04 | 03 | 3 | FCTY-10 | unit | `npx vitest run src/components/faculty/__tests__/ObeAttainment.test.js` | ❌ W0 | ⬜ pending |
| 03-03-05 | 03 | 3 | FCTY-06 | unit | `npx vitest run src/components/faculty/__tests__/FacultyNotices.test.js` | ❌ W0 | ⬜ pending |
| 03-03-06 | 03 | 3 | FCTY-12 | unit | `npx vitest run src/components/faculty/__tests__/WorkloadSummary.test.js` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `portal-vue/src/components/faculty/__tests__/` — directory and all 12 test stub files
- [ ] `portal-vue/src/components/faculty/__tests__/faculty-setup.js` — shared fixtures (mock faculty data, timetable, attendance, grades)
- [ ] Framework install: none needed — vitest already configured with 37 passing tests from Phase 2

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Grade grid Tab/Enter navigation UX | FCTY-03 | Keyboard interaction requires real DOM + focus management | Open grade grid, press Tab/Enter between cells, verify cursor movement |
| Attendance bulk-select performance with 60+ rows | FCTY-02 | Performance test with realistic data volume | Load attendance page for a class with 60+ students, select-all, toggle 5 absents, submit — should complete in <2 minutes |
| LMS content CRUD against live Frappe backend | FCTY-09 | Full-stack integration | Create a lesson, edit it, delete it, verify changes in Frappe desk |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
