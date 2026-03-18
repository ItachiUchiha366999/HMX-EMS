# Phase 2: Shared Component Library - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Build reusable UI components inside `portal-vue/src/components/` — KPI cards, chart wrappers, data tables, filter bars, PDF/Excel export, report viewer, and notification panel. These are pure display primitives that every portal module (Faculty, Management, HOD, Parent in Phases 3–6) composes from. No portal-specific views are built here.

</domain>

<decisions>
## Implementation Decisions

### Visual Style
- **Design approach**: Production-ready custom design system using the project's own CSS variables and design tokens (already in `portal.css`). No external UI framework dependency.
- **Color palette**: Clean and professional base (white/light grey backgrounds, blue/indigo primary) with colorful accents per status and module — not monochrome.
- **KPI card status**: Color + icon signaling — cards change border and background tint based on value vs threshold (red = critical, amber = warning, green = good). Includes trend arrow icon (up/down/flat).
- **Dark mode**: Required from day one. Implement via CSS custom properties (`--bg-color`, `--text-color`, etc.) so both themes share the same component markup.
- **Density**: Data-dense but not cramped — enough whitespace to read, compact enough for dashboard grids.

### Chart Types & Data Binding
- **Data binding pattern**: Props-only (dumb components). Parent view fetches data from Frappe API and passes it as props. Charts are pure display — no internal API calls.
- **Required chart types**: Line, Bar/Column, Heatmap. (Pie/donut deferred — not selected as must-have.)
- **Library**: ApexCharts (specified in COMP-02 requirement).
- **Drill-down**: Charts emit a `drill-down` event with the clicked data point. Parent view handles navigation via Vue Router. Chart component stays decoupled.
- **Loading state**: Skeleton placeholder — animated grey shape matching the chart dimensions while parent fetches data. Not a spinner.
- **Error state**: Claude's discretion (empty chart + error message).

### Data Table Behavior
- **Editing**: Read-only. Editing happens by navigating to the Frappe form — no inline cell editing.
- **Pagination**: Server-side pagination via Frappe API (`page_length`, `start` params). Supports datasets of any size.
- **Library**: TanStack Table (specified in COMP-03 requirement).
- **Row selection**: Multi-select checkboxes supported. Table emits `selection-change` event with selected rows. Parent handles bulk actions (used in Phase 3 for bulk attendance, etc.).
- **Export scope**: Current page only — exports exactly what the user sees (respects active filters and pagination).
- **Export formats**: PDF via jsPDF (COMP-05), Excel via ExcelJS (COMP-06). Export buttons live inside the table component header.

### Filter Bar
- **Filters included**: Date range, academic year, department, program selectors (COMP-04).
- **State management**: Filter bar emits a `filter-change` event with the current filter state. Parent view passes filter state to data-fetching composables. No global filter store in Phase 2.
- **Academic year options**: Populated from Frappe `Academic Year` doctype via `useFrappe` composable.

### Report Viewer
- **Presentation**: Embedded per portal module — no standalone report viewer page. Each portal section includes only its relevant reports inline.
- **Render location**: Inline in the portal page content area below the report's filter bar.
- **Filters**: Dynamic — component reads the report's filter field definitions from Frappe and renders appropriate inputs automatically (same approach as Frappe desk report runner).
- **Export**: Report results render in the DataTable component, so PDF/Excel export comes for free via the table's export buttons.

### Notification/Alert Panel (COMP-08)
- **Scope**: Reusable panel component showing user notifications from Frappe's notification system + university_erp custom notifications.
- **Claude's Discretion**: Exact panel layout, read/unread state, dismiss behavior.

### Claude's Discretion
- Exact spacing, border-radius, and typography scale
- Error state design for charts and tables
- Loading skeleton exact shape/animation
- Component prop naming conventions
- CSS custom property naming scheme for dark/light themes
- Pie/donut chart (not selected as Phase 2 must-have — can include if trivial)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — COMP-01 through COMP-08 (all 8 component requirements)

### Existing portal foundation (Phase 1 output)
- `portal-vue/src/main.js` — App bootstrap; Pinia + Vue Router initialization pattern
- `portal-vue/src/stores/session.js` — Pinia session store; `roles[]` and `allowed_modules[]` available to all components
- `portal-vue/src/composables/useFrappe.js` — (if exists in student-portal-vue, copy/reference) Frappe API wrapper for data fetching
- `portal-vue/src/config/navigation.js` — Route definitions; future phases add nav items here
- `portal-vue/src/layouts/PortalLayout.vue` — Shell layout; components slot into `<main>` area
- `portal-vue/vite.config.js` — Build config; output path for new component assets
- `frappe-bench/apps/university_erp/university_erp/www/portal/index.py` — SPA entry point

### Existing CSS/design tokens
- `frappe-bench/apps/university_erp/university_erp/public/css/theme/variables.css` — CSS custom properties (colors, spacing, typography)
- `frappe-bench/apps/university_erp/university_erp/public/css/theme/components.css` — Existing component styles to align with
- `frappe-bench/apps/university_erp/university_erp/public/css/university_desk.css` — Desk-level overrides

### Backend report patterns
- `frappe-bench/apps/university_erp/university_erp/university_analytics/report/` — Existing report definitions; report viewer must call these
- `frappe-bench/apps/university_erp/university_erp/university_erp/analytics/api.py` — Analytics API endpoints (now permission-guarded); chart data sources

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `student-portal-vue/src/composables/useFrappe.js` — Frappe API wrapper (fetch, error handling, loading state); copy into `portal-vue/src/composables/` as the data-fetching primitive all components depend on
- `portal-vue/src/stores/session.js` — Pinia session store already has `roles[]`; components can read user context from here
- `frappe-bench/apps/university_erp/university_erp/public/css/theme/variables.css` — CSS custom properties already defined; component styles should use these variables, not hardcoded hex values

### Established Patterns
- **Data fetching**: `useFrappe` composable wraps `frappe.call()` — components receive data via props, parents use composables to fetch
- **Props-down, events-up**: Phase 1 sidebar follows this pattern; all Phase 2 components follow the same
- **CSS variables for theming**: `portal.css` and `variables.css` already use `var(--bg-color)` etc.; dark mode = swap the variable values via `[data-theme="dark"]` selector on `<html>`

### Integration Points
- Components slot into `PortalLayout.vue`'s `<main>` content area
- Chart data comes from `university_erp.university_erp.analytics.api.*` endpoints (all now permission-guarded)
- Report viewer calls `frappe.call('frappe.desk.query_report.run', {report_name, filters})` — standard Frappe report runner API
- Export components write files client-side (jsPDF / ExcelJS) — no server involvement
- Filter bar's academic year selector fetches from `frappe.db.get_list('Academic Year')`

</code_context>

<specifics>
## Specific Ideas

- "Production-ready, modern university ERP" — components should not look like prototypes. Clean typography, consistent spacing, polished states (loading, empty, error).
- "Clean and professional as well as colorful" — use a neutral base (white/light grey) with purposeful color: status colors on KPI cards, chart series colors, module accent colors. Not pastel, not garish.
- Dark mode from day one — implement with CSS custom properties so toggling is a single attribute change on `<html>`.
- Report viewer is embedded per module, not a standalone page — faculty portal shows faculty reports, management shows analytics reports, etc.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-shared-component-library*
*Context gathered: 2026-03-18*
