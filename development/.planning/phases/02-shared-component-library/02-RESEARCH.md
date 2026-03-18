# Phase 2: Shared Component Library - Research

**Researched:** 2026-03-18
**Domain:** Vue 3 component library (KPI cards, charts, data tables, filters, export, report viewer, notifications)
**Confidence:** HIGH

## Summary

Phase 2 builds 8 reusable Vue 3 SFC components inside `portal-vue/src/components/` that every portal module (Phases 3-6) composes from. The component library is purely presentational -- props-down, events-up -- with zero internal data fetching. Parents use the existing `useFrappe` composable to fetch data and pass it as props.

The tech stack is locked: ApexCharts for charts, TanStack Table (headless) for data tables, jsPDF + jspdf-autotable for PDF export, ExcelJS for Excel export. All styling uses the project's existing CSS custom properties from `variables.css` and `components.css`. Dark mode is mandatory from day one via `[data-theme="dark"]` semantic token swaps on `<html>`.

The existing codebase already provides a strong foundation: `.stat-card`, `.table-wrapper`, `.form-input`, `.skeleton`, `.alert-*`, and `.btn-*` CSS classes are all defined in `components.css`. The components.css skeleton animation keyframes (1.5s infinite pulse) are ready to use. The `useFrappe` composable from `student-portal-vue` needs to be copied and adapted for the unified portal.

**Primary recommendation:** Build components bottom-up -- CSS token additions first (dark mode semantic tokens), then atomic components (KPI card, skeleton loaders), then composed components (chart wrapper, data table with export), then orchestrating components (filter bar, report viewer, notification panel).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Props-only (dumb) components -- parents fetch data, pass as props. Charts/tables have no internal API calls.
- ApexCharts for Line, Bar, Heatmap charts. Pie/donut deferred (not must-have).
- TanStack Table for data tables with server-side pagination.
- jsPDF + jspdf-autotable for PDF export, ExcelJS for Excel export.
- Export scope: current page only (what user sees).
- Skeleton loaders (not spinners) for all loading states.
- Dark mode from day one via CSS custom properties.
- Filter bar emits `filter-change` event -- no global filter store.
- Report viewer embedded per module (not standalone page).
- Academic year options populated from Frappe `Academic Year` doctype.
- Read-only tables -- editing via navigation to Frappe form, no inline editing.
- Multi-select checkboxes on tables, emitting `selection-change` event.
- Charts emit `drill-down` event with clicked data point; parent handles navigation.
- Custom design system using project's own CSS variables -- no external UI framework.
- Material Symbols Outlined for icons (already used in Sidebar.vue).
- Inter font via `var(--font-family)` token -- fix Lexend reference in PortalLayout.vue.

### Claude's Discretion
- Exact spacing, border-radius, and typography scale (UI-SPEC provides specifics)
- Error state design for charts and tables
- Loading skeleton exact shape/animation
- Component prop naming conventions
- CSS custom property naming scheme for dark/light themes
- Notification panel layout, read/unread state, dismiss behavior
- Pie/donut chart (can include if trivial)

### Deferred Ideas (OUT OF SCOPE)
- None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| COMP-01 | KPI counter card (value, label, trend indicator, status color) | Existing `.stat-card` CSS pattern in components.css provides base styling. Vue SFC wraps this with props for value, label, trend, status. Status colors from `--success`/`--warning`/`--error` tokens. |
| COMP-02 | Chart wrapper (line, bar, heatmap) using ApexCharts | `vue3-apexcharts` v1.11.1 provides `<apexchart>` component. Wrap in card container with loading/error/empty states. Pass chart series palette from CSS variables. |
| COMP-03 | Data table with sorting, pagination, search using TanStack Table | `@tanstack/vue-table` v8.21.3 is headless -- provides logic only. Combine with existing `.table-wrapper`/`.table` CSS from components.css. Server-side pagination via `page_length`/`start` Frappe params. |
| COMP-04 | Filter bar (date range, academic year, department, program) | Uses existing `.form-input`/`.form-select` CSS classes. Emits `filter-change` event. Academic year from `frappe.db.get_list('Academic Year')`. |
| COMP-05 | PDF export using jsPDF | `jspdf` v4.2.1 + `jspdf-autotable` v5.0.7. Client-side generation from current table page data. Styled header row with primary color. |
| COMP-06 | Excel export using ExcelJS | `exceljs` v4.4.0. Client-side `.xlsx` generation from current table page data. Auto-width columns, styled header. |
| COMP-07 | Report viewer for 54+ backend reports | Calls `frappe.desk.query_report.run` API. Reads filter definitions via `frappe.desk.query_report.get_script`. Renders results in COMP-03 DataTable. |
| COMP-08 | Notification/alert panel | Reads from Frappe notification system + university_erp custom `User Notification` doctype. Card-based layout with read/unread states. |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| vue | ^3.4.0 | Component framework | Already installed in portal-vue |
| pinia | ^2.1.7 | State management | Already installed; session store in use |
| vue-router | ^4.3.0 | Client routing | Already installed |
| apexcharts | 5.10.4 | Chart rendering engine | Specified in COMP-02 requirement |
| vue3-apexcharts | 1.11.1 | Vue 3 wrapper for ApexCharts | Official Vue 3 integration |
| @tanstack/vue-table | 8.21.3 | Headless table logic (sort, paginate, filter) | Specified in COMP-03 requirement |
| jspdf | 4.2.1 | PDF generation client-side | Specified in COMP-05 requirement |
| jspdf-autotable | 5.0.7 | Table formatting plugin for jsPDF | Standard companion to jsPDF for table exports |
| exceljs | 4.4.0 | Excel (.xlsx) generation client-side | Specified in COMP-06 requirement |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none) | - | - | All supporting needs covered by existing CSS design system and Frappe APIs |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ApexCharts | Chart.js | Chart.js lighter but ApexCharts has better heatmap support and is locked in requirements |
| TanStack Table | AG Grid | AG Grid is batteries-included but heavy; TanStack is headless and fits the custom CSS approach |
| jsPDF | pdfmake | pdfmake has declarative API but jsPDF + autotable is more mature for table exports |
| ExcelJS | SheetJS | SheetJS community edition has limitations; ExcelJS is fully open source with styling support |

**Installation:**
```bash
cd /workspace/development/portal-vue
npm install apexcharts@^5.10.4 vue3-apexcharts@^1.11.1 @tanstack/vue-table@^8.21.3 jspdf@^4.2.1 jspdf-autotable@^5.0.7 exceljs@^4.4.0
```

**Version verification:** All versions verified against npm registry on 2026-03-18.

## Architecture Patterns

### Recommended Project Structure
```
portal-vue/src/
├── components/
│   ├── shared/              # Phase 2 shared components
│   │   ├── KpiCard.vue      # COMP-01
│   │   ├── ChartWrapper.vue # COMP-02
│   │   ├── DataTable.vue    # COMP-03
│   │   ├── FilterBar.vue    # COMP-04
│   │   ├── ReportViewer.vue # COMP-07
│   │   ├── NotificationPanel.vue  # COMP-08
│   │   ├── SkeletonLoader.vue     # Shared skeleton primitive
│   │   ├── ToastNotification.vue  # Export feedback toast
│   │   └── index.js         # Barrel export
│   └── Sidebar.vue          # Phase 1 (existing)
├── composables/
│   ├── useFrappe.js         # Copied + adapted from student-portal-vue
│   ├── useExportPdf.js      # COMP-05 logic
│   ├── useExportExcel.js    # COMP-06 logic
│   └── useReportRunner.js   # COMP-07 Frappe report API wrapper
├── config/
│   └── navigation.js        # Existing
├── layouts/
│   └── PortalLayout.vue     # Existing
├── stores/
│   └── session.js           # Existing
└── router/
    └── index.js             # Existing
```

### Pattern 1: Props-Down, Events-Up
**What:** Every shared component is a pure display primitive. It receives data via props and emits events for user actions. No component fetches its own data.
**When to use:** All 8 components in this phase.
**Example:**
```vue
<!-- Parent view (Phase 3+) -->
<template>
  <KpiCard
    label="Attendance Rate"
    :value="attendanceRate"
    :trend="attendanceTrend"
    status="good"
    icon="groups"
    :loading="loading"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFrappe } from '@/composables/useFrappe.js'
import KpiCard from '@/components/shared/KpiCard.vue'

const { callMethod, loading } = useFrappe()
const attendanceRate = ref(null)
const attendanceTrend = ref(null)

onMounted(async () => {
  const data = await callMethod('university_erp.university_erp.analytics.api.get_kpi_value', {
    kpi_name: 'Attendance Rate'
  })
  attendanceRate.value = data.value
  attendanceTrend.value = data.trend
})
</script>
```

### Pattern 2: Headless Table with Custom Rendering
**What:** TanStack Table provides sorting/pagination/filtering logic. The Vue component renders the table HTML using the project's `.table-wrapper`/`.table` CSS classes.
**When to use:** COMP-03 DataTable and COMP-07 ReportViewer.
**Example:**
```vue
<script setup>
import {
  useVueTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
} from '@tanstack/vue-table'

const props = defineProps({
  columns: Array,
  data: Array,
  pageSize: { type: Number, default: 20 },
  totalRows: Number,
  loading: Boolean,
})

const emit = defineEmits(['page-change', 'sort-change', 'selection-change'])

// For server-side pagination, use manualPagination: true
const table = useVueTable({
  get data() { return props.data },
  get columns() { return props.columns },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  manualPagination: true,
  get pageCount() { return Math.ceil(props.totalRows / props.pageSize) },
})
</script>
```

### Pattern 3: Composable for Export Logic
**What:** Export logic lives in composables (not inside components) so it can be reused by DataTable and ReportViewer independently.
**When to use:** COMP-05 (PDF) and COMP-06 (Excel).
**Example:**
```javascript
// composables/useExportPdf.js
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

export function useExportPdf() {
  function exportToPdf({ title, columns, rows }) {
    const doc = new jsPDF()
    doc.setFontSize(16)
    doc.text(title, 14, 20)

    autoTable(doc, {
      startY: 30,
      head: [columns.map(c => c.header)],
      body: rows.map(row => columns.map(c => row[c.accessorKey])),
      headStyles: { fillColor: [79, 70, 229] }, // --primary
      alternateRowStyles: { fillColor: [248, 250, 252] }, // --gray-50
    })

    doc.save(`${title}.pdf`)
  }

  return { exportToPdf }
}
```

### Pattern 4: Frappe Report Runner Integration
**What:** The report viewer calls two Frappe APIs: `get_script` to discover filter definitions, and `run` to execute the report with user-supplied filters.
**When to use:** COMP-07 ReportViewer.
**Example:**
```javascript
// composables/useReportRunner.js
import { ref } from 'vue'
import { useFrappe } from './useFrappe.js'

export function useReportRunner() {
  const { callMethod, loading, error } = useFrappe()
  const columns = ref([])
  const rows = ref([])
  const filters = ref([])

  async function loadReportMeta(reportName) {
    // get_script returns filter definitions and report JS
    const script = await callMethod('frappe.desk.query_report.get_script', {
      report_name: reportName
    })
    // Parse filter definitions from script result
    // script.filters contains the filter field definitions
    filters.value = script.filters || []
  }

  async function runReport(reportName, reportFilters) {
    const result = await callMethod('frappe.desk.query_report.run', {
      report_name: reportName,
      filters: JSON.stringify(reportFilters)
    })
    columns.value = result.columns || []
    rows.value = result.result || []
  }

  return { loadReportMeta, runReport, columns, rows, filters, loading, error }
}
```

### Pattern 5: Dark Mode via Semantic Tokens
**What:** Add semantic CSS custom properties (--bg-surface, --bg-card, --text-primary, etc.) that swap values under `[data-theme="dark"]`. Components reference only semantic tokens.
**When to use:** Every component. This is the first task in the phase.
**Example:**
```css
/* Added to variables.css */
:root {
  --bg-surface: var(--gray-50);
  --bg-card: var(--white);
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-500);
  --text-muted: var(--gray-400);
  --border-default: var(--gray-200);
  --border-subtle: var(--gray-100);
  --skeleton-base: var(--gray-200);
  --skeleton-shine: var(--gray-100);
}

[data-theme="dark"] {
  --bg-surface: var(--gray-900);
  --bg-card: var(--gray-800);
  --text-primary: var(--gray-50);
  --text-secondary: var(--gray-400);
  --text-muted: var(--gray-500);
  --border-default: var(--gray-700);
  --border-subtle: var(--gray-800);
  --skeleton-base: var(--gray-700);
  --skeleton-shine: var(--gray-600);
}
```

### Anti-Patterns to Avoid
- **Hardcoded hex values in component styles:** Always use CSS variables. The Sidebar.vue currently uses hardcoded colors (#0f172a, #e2e8f0, etc.) -- Phase 2 components must NOT follow this pattern.
- **Data fetching inside shared components:** Components must be pure display. If a component needs data, it declares a prop. Parent fetches.
- **Global filter store in Phase 2:** The filter bar emits events. No Pinia store for filters until a later phase demonstrates the need.
- **Using `--font-bold` (700) weight:** UI-SPEC restricts to `--font-normal` (400) and `--font-semibold` (600) only. The existing `.stat-value` in components.css uses `--font-bold` -- KpiCard should use `--font-semibold` instead per UI-SPEC.
- **Importing ApexCharts globally:** Register `vue3-apexcharts` locally in ChartWrapper.vue only, not in main.js. Keeps bundle efficient.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Table sorting/pagination/selection | Custom sort/paginate logic | `@tanstack/vue-table` | Edge cases in multi-column sort, selection state, page boundary math |
| Chart rendering | Canvas/SVG drawing | `apexcharts` + `vue3-apexcharts` | Responsive resize, tooltips, animations, accessibility |
| PDF table layout | Manual coordinate math | `jspdf-autotable` | Column width calculation, page breaks, header repetition |
| Excel cell styling | Raw XML manipulation | `exceljs` | Cell formats, column widths, sheet naming, .xlsx spec compliance |
| Skeleton animation | Custom CSS animation | Existing `.skeleton` class from components.css | Already defined with proper pulse animation keyframes |
| Form input styling | Custom input CSS | Existing `.form-input`/`.form-select` classes | Consistent with rest of portal, focus states already handled |

**Key insight:** The project already has a comprehensive CSS design system in `components.css` (767 lines). Phase 2 components should use these classes, not reinvent them. The `.stat-card`, `.table-wrapper`, `.table`, `.form-input`, `.form-select`, `.btn-*`, `.skeleton`, and `.alert-*` patterns are all ready.

## Common Pitfalls

### Pitfall 1: ApexCharts Reactivity with Vue 3
**What goes wrong:** ApexCharts does not reactively update when props change in Vue 3 if the chart options object reference stays the same.
**Why it happens:** ApexCharts uses internal diffing that can miss deeply nested changes.
**How to avoid:** Use a computed property for chart options that returns a new object reference when data changes. The `vue3-apexcharts` component watches the `options` and `series` props, but series MUST be a new array reference (not mutated in place).
**Warning signs:** Chart doesn't update when parent passes new data.

### Pitfall 2: TanStack Table Server-Side Pagination Setup
**What goes wrong:** Forgetting `manualPagination: true` causes TanStack to try client-side pagination on the current page's data, showing wrong page counts.
**Why it happens:** TanStack defaults to client-side pagination.
**How to avoid:** Always set `manualPagination: true` and provide `pageCount` computed from `totalRows / pageSize`. Handle `onPaginationChange` to emit events that trigger parent re-fetch.
**Warning signs:** Page count shows "1 of 1" despite hundreds of records, or all records load at once.

### Pitfall 3: ExcelJS Bundle Size
**What goes wrong:** ExcelJS adds ~500KB to the bundle, degrading initial load.
**Why it happens:** ExcelJS includes full xlsx read/write capabilities.
**How to avoid:** Dynamic import ExcelJS only when the user clicks "Export to Excel". Use `const ExcelJS = await import('exceljs')` inside the export composable.
**Warning signs:** Main bundle exceeds 500KB; Lighthouse warns about unused JavaScript.

### Pitfall 4: jsPDF Font Handling
**What goes wrong:** Non-Latin characters (Hindi, regional languages) render as boxes in PDF.
**Why it happens:** jsPDF default fonts only support Latin-1.
**How to avoid:** For Phase 2, document this as a known limitation. If needed later, custom fonts can be embedded via `doc.addFont()`. Keep exports to ASCII/Latin data for now.
**Warning signs:** PDF output contains empty squares instead of text.

### Pitfall 5: Frappe Report API Filter Serialization
**What goes wrong:** Report filters passed as a JavaScript object get rejected by the Frappe `query_report.run` endpoint.
**Why it happens:** The Frappe API expects `filters` as a JSON string, not an object, when called via `frappe.call`.
**How to avoid:** Always `JSON.stringify()` the filters object before passing to the API call. The `useFrappe` composable already JSON-stringifies POST body, but nested objects need explicit serialization.
**Warning signs:** "ValueError: could not convert string to float" or "json.decoder.JSONDecodeError" in server logs.

### Pitfall 6: CSS Variable Fallbacks in ApexCharts
**What goes wrong:** ApexCharts configuration accepts hex color strings, not CSS `var()` references. Passing `var(--primary)` directly to chart options doesn't work.
**Why it happens:** ApexCharts renders to SVG/Canvas and parses color strings internally -- it doesn't go through CSS.
**How to avoid:** Read CSS variable values at chart mount time using `getComputedStyle(document.documentElement).getPropertyValue('--primary').trim()`. Create a composable `useThemeColors()` that returns resolved hex values. Re-resolve on theme change.
**Warning signs:** Charts render with default ApexCharts blue instead of the theme primary indigo.

### Pitfall 7: useFrappe Composable Adaptation
**What goes wrong:** Copying `useFrappe.js` from `student-portal-vue` without updating the base URL causes API calls to hit the student portal endpoint instead of the general Frappe API.
**Why it happens:** The student-portal version hardcodes `PORTAL_API = '/api/method/university_erp.university_portals.api.portal_api'`.
**How to avoid:** The adapted composable for `portal-vue` should use `callMethod(fullPath, params)` as the primary interface (calling `/api/method/{fullPath}` directly). The portal-specific `call()` method should either be removed or re-pointed.
**Warning signs:** 404 errors on API calls; responses that don't match expected format.

## Code Examples

### useFrappe Composable (Adapted for Portal)
```javascript
// portal-vue/src/composables/useFrappe.js
import { ref } from 'vue'

function getCsrfToken() {
  const match = document.cookie.match(/csrf_token=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}

async function handleResponse(res) {
  if (res.status === 403 || res.status === 401) {
    window.location.href = '/login?redirect-to=/portal/'
    throw new Error('Session expired')
  }
  const data = await res.json()
  if (data.exc) {
    const msg = typeof data.exc === 'string' ? data.exc : JSON.stringify(data.exc)
    throw new Error(data._server_messages || msg)
  }
  return data.message
}

export function useFrappe() {
  const loading = ref(false)
  const error = ref(null)

  async function call(method, params = {}, options = {}) {
    loading.value = true
    error.value = null
    try {
      let url = `/api/method/${method}`
      const fetchOptions = {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': getCsrfToken(),
        },
      }
      if (options.method === 'GET') {
        const qs = new URLSearchParams(params).toString()
        if (qs) url += `?${qs}`
        fetchOptions.method = 'GET'
      } else {
        fetchOptions.method = 'POST'
        fetchOptions.body = JSON.stringify(params)
      }
      const res = await fetch(url, fetchOptions)
      return await handleResponse(res)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // Convenience: get a list of documents
  async function getList(doctype, { fields, filters, orderBy, start, pageLength } = {}) {
    return call('frappe.client.get_list', {
      doctype,
      fields: fields || ['name'],
      filters: filters || {},
      order_by: orderBy || 'modified desc',
      start: start || 0,
      page_length: pageLength || 20,
    }, { method: 'GET' })
  }

  return { call, getList, loading, error }
}
```

### useThemeColors Composable (for ApexCharts)
```javascript
// portal-vue/src/composables/useThemeColors.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useThemeColors() {
  const colors = ref(resolveColors())

  function resolveColors() {
    const style = getComputedStyle(document.documentElement)
    return {
      primary: style.getPropertyValue('--primary').trim(),
      success: style.getPropertyValue('--success').trim(),
      warning: style.getPropertyValue('--warning').trim(),
      error: style.getPropertyValue('--error').trim(),
      info: style.getPropertyValue('--info').trim(),
      secondary: style.getPropertyValue('--secondary').trim(),
      textPrimary: style.getPropertyValue('--text-primary').trim() || style.getPropertyValue('--gray-900').trim(),
      textSecondary: style.getPropertyValue('--text-secondary').trim() || style.getPropertyValue('--gray-500').trim(),
      bgCard: style.getPropertyValue('--bg-card').trim() || style.getPropertyValue('--white').trim(),
    }
  }

  // Re-resolve when theme attribute changes
  let observer
  onMounted(() => {
    observer = new MutationObserver(() => {
      colors.value = resolveColors()
    })
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    })
  })
  onUnmounted(() => observer?.disconnect())

  return { colors }
}
```

### Frappe Report Runner API Calls
```javascript
// The two key Frappe API calls for report viewer:

// 1. Get report metadata + filter definitions
// POST /api/method/frappe.desk.query_report.get_script
// Params: { report_name: "Faculty Workload Summary" }
// Returns: { script: "...", filters: [...], columns: [...] }

// 2. Execute report with filters
// POST /api/method/frappe.desk.query_report.run
// Params: { report_name: "Faculty Workload Summary", filters: '{"department": "CS"}' }
// Returns: { columns: [...], result: [[...], [...]], ... }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ApexCharts 3.x | ApexCharts 5.x | 2025 | Major version bump; import paths changed, some option names updated |
| TanStack Table 7 (react-table) | TanStack Table 8 (framework-agnostic) | 2023 | Vue-specific package `@tanstack/vue-table`; uses `useVueTable` instead of `useReactTable` |
| jsPDF 2.x | jsPDF 4.x | 2024-2025 | New plugin architecture; `jspdf-autotable` is now a separate import |
| ExcelJS 4.3 | ExcelJS 4.4 | 2024 | Minor; streaming improvements |

**Deprecated/outdated:**
- `vue-apexcharts` (Vue 2 only) -- use `vue3-apexcharts` instead
- `react-table` -- renamed to `@tanstack/table-core` with framework-specific wrappers
- Direct `autoTable(doc, options)` function call is current pattern for jspdf-autotable 5.x (not `doc.autoTable()`)

## Open Questions

1. **Report filter discovery from JS files**
   - What we know: `frappe.desk.query_report.get_script` returns the report's JavaScript as a string containing `frappe.query_reports[name] = { filters: [...] }`. The filters array is embedded in JS code, not returned as structured JSON.
   - What's unclear: Whether all 54+ reports have their filters defined in the JS file or if some use Python-side `get_filters()`.
   - Recommendation: Parse the JS response to extract the filters array. As a fallback, allow manual filter definition overrides per report in the report viewer config.

2. **Toast notification system**
   - What we know: Export success/failure needs toast feedback (COMP-05/06).
   - What's unclear: Whether a shared toast system should be a Vue plugin (provide/inject) or a simple component composed at layout level.
   - Recommendation: Create a lightweight `ToastNotification.vue` component positioned fixed bottom-right, driven by a simple `useToast()` composable with `show(message, type, duration)`. No plugin needed.

3. **Notification panel data source**
   - What we know: COMP-08 should show Frappe notifications + university_erp custom `User Notification` doctype.
   - What's unclear: Exact Frappe API for fetching notifications for portal users (not desk users).
   - Recommendation: Use `frappe.client.get_list` on the `Notification Log` doctype filtered by `for_user = frappe.session.user`. For university_erp custom notifications, use `frappe.client.get_list` on `User Notification`.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest (to be installed -- no test infrastructure exists yet) |
| Config file | none -- see Wave 0 |
| Quick run command | `npx vitest run --reporter=verbose` |
| Full suite command | `npx vitest run` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COMP-01 | KPI card renders value, label, trend, status color | unit | `npx vitest run src/components/shared/__tests__/KpiCard.test.js` | No -- Wave 0 |
| COMP-02 | Chart wrapper renders with ApexCharts, emits drill-down | unit | `npx vitest run src/components/shared/__tests__/ChartWrapper.test.js` | No -- Wave 0 |
| COMP-03 | DataTable sorts, paginates, searches, supports selection | unit | `npx vitest run src/components/shared/__tests__/DataTable.test.js` | No -- Wave 0 |
| COMP-04 | FilterBar renders selectors, emits filter-change | unit | `npx vitest run src/components/shared/__tests__/FilterBar.test.js` | No -- Wave 0 |
| COMP-05 | PDF export generates downloadable file from table data | unit | `npx vitest run src/composables/__tests__/useExportPdf.test.js` | No -- Wave 0 |
| COMP-06 | Excel export generates downloadable file from table data | unit | `npx vitest run src/composables/__tests__/useExportExcel.test.js` | No -- Wave 0 |
| COMP-07 | ReportViewer loads filters and runs Frappe report | unit | `npx vitest run src/components/shared/__tests__/ReportViewer.test.js` | No -- Wave 0 |
| COMP-08 | NotificationPanel shows items with read/unread state | unit | `npx vitest run src/components/shared/__tests__/NotificationPanel.test.js` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `npx vitest run --reporter=verbose`
- **Per wave merge:** `npx vitest run`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Install `vitest` + `@vue/test-utils` + `jsdom` as dev dependencies
- [ ] Create `portal-vue/vitest.config.js` with Vue plugin and jsdom environment
- [ ] Create `portal-vue/src/components/shared/__tests__/` directory
- [ ] Create `portal-vue/src/composables/__tests__/` directory
- [ ] Mock setup for `document.cookie` (CSRF token) and `fetch` (API calls)

## Sources

### Primary (HIGH confidence)
- `portal-vue/package.json` -- current Vue 3 dependencies verified locally
- `frappe-bench/apps/university_erp/university_erp/public/css/theme/variables.css` -- all CSS tokens verified locally (137 lines)
- `frappe-bench/apps/university_erp/university_erp/public/css/theme/components.css` -- all component CSS patterns verified locally (767 lines, includes .stat-card, .table, .skeleton, .alert, .btn, .form-input)
- `frappe-bench/apps/frappe/frappe/desk/query_report.py` -- Frappe report runner API (`run`, `get_script`) verified from source code
- `student-portal-vue/src/composables/useFrappe.js` -- existing composable pattern verified locally
- npm registry -- all 6 package versions verified via `npm view` on 2026-03-18

### Secondary (MEDIUM confidence)
- ApexCharts Vue 3 integration patterns -- based on `vue3-apexcharts` standard usage; version 1.11.1 confirmed
- TanStack Table Vue integration -- `@tanstack/vue-table` v8 `useVueTable` API based on known patterns; version 8.21.3 confirmed
- jsPDF + autotable integration -- `jspdf-autotable` v5 `autoTable(doc, options)` call pattern

### Tertiary (LOW confidence)
- Report filter discovery method -- exact format of `get_script` response for all 54+ reports may vary; some reports may use Python-only filter definitions

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries are locked decisions, versions verified from npm registry
- Architecture: HIGH -- component patterns follow established project conventions (props-down/events-up, CSS variables, useFrappe composable)
- Pitfalls: HIGH -- most pitfalls verified from local source code analysis (CSS variable handling, Frappe API patterns, existing code patterns)
- Report viewer: MEDIUM -- Frappe `get_script` API verified from source, but filter parsing from JS strings needs runtime validation

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (stable stack, no fast-moving dependencies)
