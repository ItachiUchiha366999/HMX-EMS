---
phase: 2
slug: shared-component-library
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest (to be installed — no test infrastructure exists yet) |
| **Config file** | none — Wave 0 installs `portal-vue/vitest.config.js` |
| **Quick run command** | `cd portal-vue && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd portal-vue && npx vitest run` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd portal-vue && npx vitest run --reporter=verbose`
- **After every plan wave:** Run `cd portal-vue && npx vitest run`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 0 | COMP-01..08 | infra | `cd portal-vue && npx vitest run` | ❌ W0 | ⬜ pending |
| 2-01-02 | 01 | 1 | COMP-01 | unit | `cd portal-vue && npx vitest run src/components/shared/__tests__/KpiCard.test.js` | ❌ W0 | ⬜ pending |
| 2-01-03 | 01 | 1 | COMP-02 | unit | `cd portal-vue && npx vitest run src/components/shared/__tests__/ChartWrapper.test.js` | ❌ W0 | ⬜ pending |
| 2-01-04 | 01 | 1 | COMP-04 | unit | `cd portal-vue && npx vitest run src/components/shared/__tests__/FilterBar.test.js` | ❌ W0 | ⬜ pending |
| 2-01-05 | 01 | 1 | COMP-08 | unit | `cd portal-vue && npx vitest run src/components/shared/__tests__/NotificationPanel.test.js` | ❌ W0 | ⬜ pending |
| 2-02-01 | 02 | 2 | COMP-03 | unit | `cd portal-vue && npx vitest run src/components/shared/__tests__/DataTable.test.js` | ❌ W0 | ⬜ pending |
| 2-02-02 | 02 | 2 | COMP-05 | unit | `cd portal-vue && npx vitest run src/composables/__tests__/useExportPdf.test.js` | ❌ W0 | ⬜ pending |
| 2-02-03 | 02 | 2 | COMP-06 | unit | `cd portal-vue && npx vitest run src/composables/__tests__/useExportExcel.test.js` | ❌ W0 | ⬜ pending |
| 2-02-04 | 02 | 2 | COMP-07 | unit | `cd portal-vue && npx vitest run src/components/shared/__tests__/ReportViewer.test.js` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `portal-vue/vitest.config.js` — Vitest config with Vue plugin and jsdom environment
- [ ] `portal-vue/src/components/shared/__tests__/KpiCard.test.js` — stubs for COMP-01
- [ ] `portal-vue/src/components/shared/__tests__/ChartWrapper.test.js` — stubs for COMP-02
- [ ] `portal-vue/src/components/shared/__tests__/DataTable.test.js` — stubs for COMP-03
- [ ] `portal-vue/src/components/shared/__tests__/FilterBar.test.js` — stubs for COMP-04
- [ ] `portal-vue/src/composables/__tests__/useExportPdf.test.js` — stubs for COMP-05
- [ ] `portal-vue/src/composables/__tests__/useExportExcel.test.js` — stubs for COMP-06
- [ ] `portal-vue/src/components/shared/__tests__/ReportViewer.test.js` — stubs for COMP-07
- [ ] `portal-vue/src/components/shared/__tests__/NotificationPanel.test.js` — stubs for COMP-08
- [ ] Install `vitest`, `@vue/test-utils`, `jsdom`, `@vitejs/plugin-vue` as dev dependencies
- [ ] Mock setup for `document.cookie` (CSRF token) and `fetch` (Frappe API calls)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dark mode visual toggle | COMP-01..08 | CSS visual — jsdom cannot verify rendered colors | Set `document.documentElement.setAttribute('data-theme','dark')` in browser, verify all 8 components render correctly with dark background |
| Chart drill-down event fires on click | COMP-02 | ApexCharts click events require real DOM/canvas | Mount ChartWrapper in browser, click a data point, verify `drill-down` event emitted with `{series, dataPoint, value}` |
| PDF download produces valid file | COMP-05 | File download requires real browser | Export table to PDF, verify file opens in PDF reader and matches current page rows |
| Excel download produces valid file | COMP-06 | File download requires real browser | Export table to Excel, verify file opens in Excel/Sheets with correct column headers and row data |
| Report viewer loads and runs reports | COMP-07 | Requires live Frappe instance | Select a report from the list, apply filters, verify results render in DataTable below |
| Skeleton loader animation | COMP-01..08 | Visual animation | Set `loading: true` prop, verify animated grey pulse visible matching component dimensions |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
