# Accessibility Audit Report - Portal Vue Components

**Date:** 2026-03-18
**Standard:** WCAG 2.1 Level AA
**Tool:** axe-core via vitest-axe
**Components Scanned:** 16 (8 shared + 8 faculty)

## Executive Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Serious  | 0 |
| Moderate | 0 |
| Minor    | 0 |

**Total violations found:** 2 axe-core violations (both critical), plus 10 CSS contrast failures.

The shared component library is largely accessible. The primary issues are:
1. **FilterBar**: Missing form labels on date inputs and missing accessible names on select elements (critical)
2. **CSS Contrast**: 10 color pairs fail WCAG AA 4.5:1 contrast ratio requirements, primarily status colors on white backgrounds and muted text

## Component Violations Table

| Component | Critical | Serious | Moderate | Minor | Top Issue |
|-----------|----------|---------|----------|-------|-----------|
| KpiCard | 0 | 0 | 0 | 0 | None |
| DataTable | 0 | 0 | 0 | 0 | None |
| ChartWrapper | 0 | 0 | 0 | 0 | None |
| FilterBar | 2 | 0 | 0 | 0 | Missing form labels |
| NotificationPanel | 0 | 0 | 0 | 0 | None |
| ReportViewer | 0 | 0 | 0 | 0 | None |
| SkeletonLoader | 0 | 0 | 0 | 0 | None |
| ToastNotification | 0 | 0 | 0 | 0 | None |
| FacultyDashboard | 0 | 0 | 0 | 0 | None |
| TimetableToday | 0 | 0 | 0 | 0 | None |
| FacultyNotices | 0 | 0 | 0 | 0 | None |
| AttendanceMarker | 0 | 0 | 0 | 0 | None |
| TimetableGrid | 0 | 0 | 0 | 0 | None |
| LeaveBalanceCards | 0 | 0 | 0 | 0 | None |
| StudentLeaveQueue | 0 | 0 | 0 | 0 | None |
| WorkloadSummary | 0 | 0 | 0 | 0 | None |

## Violation Details by Type

| Rule ID | Impact | Components Affected | Description | WCAG Criteria |
|---------|--------|---------------------|-------------|---------------|
| label | Critical | FilterBar | Form `<input>` elements must have associated labels | 1.3.1, 4.1.2 |
| select-name | Critical | FilterBar | `<select>` elements must have an accessible name | 1.3.1, 4.1.2 |

### FilterBar Label Issues Detail

The FilterBar component has `<label>` elements with class `filter-label`, but the `<input type="date">` elements use `v-model` binding without `id` attributes, so the `<label>` elements are not programmatically associated with their inputs via `for`/`id` pairs. The `<select>` elements similarly lack explicit label association.

**Fix required:** Add unique `id` attributes to all `<input>` and `<select>` elements in FilterBar, and corresponding `for` attributes on their `<label>` elements.

## CSS Contrast Issues

Audited using `scripts/audit_accessibility.py` against WCAG 2.1 AA requirements (4.5:1 for normal text, 3:1 for large text).

| Context | Foreground | Background | Ratio | Required | Status |
|---------|------------|------------|-------|----------|--------|
| Card text on card bg | #0F172A | #FFFFFF | 17.85:1 | 4.5:1 | PASS |
| Primary text on surface | #0F172A | #F8FAFC | 17.06:1 | 4.5:1 | PASS |
| Secondary text on card | #64748B | #FFFFFF | 4.76:1 | 4.5:1 | PASS |
| Secondary text on surface | #64748B | #F8FAFC | 4.55:1 | 4.5:1 | PASS |
| Muted text on card | #94A3B8 | #FFFFFF | 2.56:1 | 4.5:1 | **FAIL** |
| Muted text on surface | #94A3B8 | #F8FAFC | 2.45:1 | 4.5:1 | **FAIL** |
| Success text on white | #10B981 | #FFFFFF | 2.54:1 | 4.5:1 | **FAIL** |
| Warning text on white | #F59E0B | #FFFFFF | 2.15:1 | 4.5:1 | **FAIL** |
| Error text on white | #EF4444 | #FFFFFF | 3.76:1 | 4.5:1 | **FAIL** |
| Info text on white | #3B82F6 | #FFFFFF | 3.68:1 | 4.5:1 | **FAIL** |
| Primary brand on white | #4F46E5 | #FFFFFF | 6.29:1 | 4.5:1 | PASS |
| Secondary brand on white | #9333EA | #FFFFFF | 5.38:1 | 4.5:1 | PASS |
| White text on primary | #FFFFFF | #4F46E5 | 6.29:1 | 4.5:1 | PASS |
| White text on success bg | #FFFFFF | #10B981 | 2.54:1 | 4.5:1 | **FAIL** |
| White text on error bg | #FFFFFF | #EF4444 | 3.76:1 | 4.5:1 | **FAIL** |
| White text on warning bg | #FFFFFF | #F59E0B | 2.15:1 | 4.5:1 | **FAIL** |
| Dark success on light success | #065F46 | #D1FAE5 | 6.78:1 | 4.5:1 | PASS |
| Dark error on light error | #991B1B | #FEE2E2 | 6.8:1 | 4.5:1 | PASS |
| Dark warning on light warning | #92400E | #FEF3C7 | 6.37:1 | 4.5:1 | PASS |
| Dark info on light info | #1E40AF | #DBEAFE | 7.15:1 | 4.5:1 | PASS |
| Gray-500 text on white | #64748B | #FFFFFF | 4.76:1 | 4.5:1 | PASS |
| Gray-400 text on white | #94A3B8 | #FFFFFF | 2.56:1 | 4.5:1 | **FAIL** |
| Gray-700 on gray-50 | #334155 | #F8FAFC | 9.9:1 | 4.5:1 | PASS |

### CSS Contrast Analysis

**Status color pattern:** The status colors (success, warning, error, info) used directly as text on white or as backgrounds with white text all fail WCAG AA. However, the `-dark` on `-light` variant pairs (used in ToastNotification) all pass with excellent ratios (6.37-7.15:1). This is the correct accessible pattern.

**Muted text:** `--text-muted` (gray-400, #94A3B8) fails on both white and gray-50 backgrounds. This is used for timestamps, secondary labels, and helper text. Needs to be darkened to at least gray-500 (#64748B) which passes at 4.76:1.

**Status badges in portal.css:** The `.status-badge.warning` uses `color: #856404` which passes on white at 5.7:1. However, `.status-badge.success` uses `var(--portal-success)` (#28A745) on white which fails at 3.68:1.

## Issues Fixed

*(To be populated after Task 2 fixes)*

## Issues Deferred

### Minor (non-blocking, documented for future)

1. **Dark mode contrast audit:** Dark mode (`[data-theme="dark"]`) variables not audited. Recommend a separate dark mode contrast pass.
2. **Portal.css legacy variables:** `--portal-*` variables define a separate color system from the design system `variables.css`. These should be consolidated in a future refactor.
3. **Dynamic content announcements:** Components that load data asynchronously (FacultyDashboard, TimetableGrid) should add `aria-live="polite"` regions to announce when content loads. Currently, screen readers may not be notified of dynamic updates.
4. **Focus visible styles:** Components inherit browser default focus styles. Custom `:focus-visible` styles matching the design system would improve keyboard navigation visual feedback.
5. **Table row selection announcement:** DataTable row selection via checkboxes does not announce selection count to screen readers.

## Structural Accessibility (PortalLayout)

The PortalLayout currently uses:
- `<main>` element for content area (correct)
- Sidebar component (not yet audited for `<nav>` landmark)
- Missing: skip-to-content link for keyboard users

**Required fixes (Task 2):**
- Add skip-to-content link
- Verify Sidebar renders within `<nav>` landmark
- Add `id="main-content"` to main content area
