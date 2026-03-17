# Stack Research

**Domain:** University ERP Dashboards, Analytics & Role-Based Portals
**Researched:** 2026-03-17
**Confidence:** HIGH

## Existing Stack (Locked In)

These are already in production and not up for debate:

| Technology | Version | Purpose | Status |
|------------|---------|---------|--------|
| Frappe Framework | v15+ | Backend framework, ORM, API layer, auth | Production |
| ERPNext / HRMS / Education | v15+ | Core ERP modules (275+ doctypes) | Production |
| Vue 3 | ^3.5.24 | Frontend SPA framework | Production (student portal) |
| Vue Router | ^4.6.4 | Client-side routing | Production |
| Tailwind CSS | ^3.4.17 | Utility-first CSS | Production |
| Vite | ^7.2.4 | Build tool / dev server | Production |
| MariaDB | — | Primary database | Production |
| Redis | — | Cache, queue, realtime pub/sub | Production |

## Recommended New Stack

### Charting & Visualization

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| ApexCharts | ^5.10.4 | Chart rendering engine | Best balance of aesthetics, interactivity, and DX for management dashboards. SVG-based rendering produces crisp charts at any resolution. Built-in zoom, pan, tooltip, and annotation support. The university dashboard will have at most hundreds of data points (departments, semesters, programs) — never the 10K+ threshold where Canvas-based libs matter. | HIGH |
| vue3-apexcharts | ^1.11.1 | Vue 3 wrapper for ApexCharts | Official Vue 3 component, actively maintained (last published March 2026), reactive prop updates. Declarative `<apexchart>` component integrates cleanly with Vue's reactivity. | HIGH |

**Why NOT ECharts:** ECharts wins on raw Canvas performance with massive datasets (10K+ points), but a university ERP dashboard never hits those numbers. ECharts has a steeper learning curve, heavier bundle size (~800KB vs ~130KB for ApexCharts), and its option-object configuration is more verbose than ApexCharts' declarative API. The extra power is wasted complexity here.

**Why NOT Chart.js:** Limited chart types (8 total). No built-in heatmaps, treemaps, or radar variants needed for department comparisons and KPI matrices. ApexCharts covers all Chart.js types plus mixed charts, annotations, and synchronized multi-chart dashboards out of the box.

### Data Tables

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| @tanstack/vue-table | ^8.21.3 | Headless data table logic | Headless approach means full control over markup and Tailwind styling — no fighting a component library's CSS. Built-in sorting, filtering, pagination, column visibility, row selection, and grouping. Matches the project's "Tailwind-first" design philosophy. | HIGH |

**Why NOT AG Grid / PrimeVue DataTable:** AG Grid's free tier is limited and its styling clashes with Tailwind. PrimeVue brings in an entire component system when we only need tables. TanStack Table is headless — zero style opinions, total Tailwind compatibility.

### Export & Reporting

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| jsPDF | ^4.2.1 | Client-side PDF generation | Mature, actively maintained, major v4.0 security overhaul (Jan 2026). Programmatic PDF creation works well for structured reports. | HIGH |
| jspdf-autotable | ^5.0.7 | PDF table generation | Plugin for jsPDF that renders tabular data as formatted PDF tables — perfect for department reports, fee summaries, student lists. | HIGH |
| ExcelJS | ^4.4.0 | Excel (.xlsx) generation | Proper npm package (unlike SheetJS which stopped publishing to npm). Full formatting support: bold headers, column widths, number formats, multiple sheets, cell styling. Handles the "export to Excel" use case completely. | HIGH |

**Why NOT SheetJS (xlsx):** The npm registry version (0.18.5) is 4 years stale and has known security vulnerabilities. New versions require installing from their custom CDN (`cdn.sheetjs.com`), which breaks standard `npm install` workflows, complicates CI/CD, and is fragile. ExcelJS does everything needed and installs normally.

**Why NOT html2pdf.js / vue3-html2pdf:** Converting rendered HTML to PDF produces inconsistent results across browsers, poor print layouts, and unpredictable pagination. jsPDF + autotable gives deterministic output by constructing the PDF programmatically.

### Composables & Utilities

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| @vueuse/core | ^14.2.1 | Vue composition utilities | 200+ composables covering intervals (useIntervalFn for auto-refresh), localStorage (useStorage for filter persistence), browser visibility (useDocumentVisibility to pause polling), network status (useNetwork), and dark mode. Eliminates boilerplate for dashboard features like auto-refresh, responsive breakpoints, and state persistence. | HIGH |

### Realtime Updates

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Frappe Realtime (socket.io) | Built-in | Server-push events | Already built into Frappe v15. Python `frappe.publish_realtime()` pushes events through Redis pub/sub to a Node socket.io server. No additional package needed — just subscribe from the Vue app via the site's socket.io endpoint. Use for KPI counters (fee collection today, enrollment changes). | HIGH |
| Polling fallback (useIntervalFn) | via @vueuse | Periodic data refresh | For dashboards where socket.io is overkill or unreliable (e.g., Docker dev), poll the Frappe API every 30-60 seconds using VueUse's `useIntervalFn`. Simpler, more debuggable, sufficient for most management dashboards. | HIGH |

**Recommended pattern:** Use polling as the primary refresh mechanism (simple, reliable, works everywhere). Reserve socket.io push for high-value live counters (today's fee collection, active student count) where immediate updates matter.

### Role-Based Routing

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Vue Router meta + guards | Built-in (^4.6.4) | Route-level access control | Declare allowed roles in route `meta: { roles: ['Faculty', 'HOD'] }`, enforce via global `beforeEach` guard that checks against Frappe session roles. No additional library needed — Vue Router's built-in meta and navigation guards are the standard pattern. | HIGH |

**Pattern:**
```typescript
// Route definition
{ path: '/faculty/attendance', meta: { roles: ['Faculty', 'HOD'] } }

// Global guard
router.beforeEach((to) => {
  const requiredRoles = to.meta.roles
  if (requiredRoles && !requiredRoles.some(r => userRoles.includes(r)))
    return '/unauthorized'
})
```

### Backend API Layer

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Frappe @whitelist() APIs | Built-in v15 | Backend endpoints | Already the pattern used by the existing portal_api.py. Dashboard data served via `frappe.call()` from Vue to whitelisted Python methods. The existing `executive_dashboard.py` already follows this pattern. | HIGH |
| Frappe Report API | Built-in v15 | Report data access | Frappe's built-in report system (Query Report, Script Report) already powers 54+ custom reports. Expose report data to Vue via `frappe.call('frappe.client.get_report_data', ...)`. | MEDIUM |

## Installation

```bash
# Charting
npm install apexcharts vue3-apexcharts

# Data tables
npm install @tanstack/vue-table

# Export / Reporting
npm install jspdf jspdf-autotable exceljs

# Utilities
npm install @vueuse/core
```

No dev dependencies needed beyond the existing Vite + Tailwind setup.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| ApexCharts | ECharts (vue-echarts ^8.0.1) | If dashboards ever need 10K+ data points, geographic maps, or 3D visualizations. Unlikely for this university ERP. |
| ApexCharts | Chart.js (vue-chartjs ^5.x) | If you only need basic bar/line/pie and want the smallest bundle (~60KB). Too limited for management dashboards. |
| @tanstack/vue-table | PrimeVue DataTable | If you adopt PrimeVue as a full component library. Not recommended — conflicts with Tailwind-first approach. |
| ExcelJS | SheetJS (xlsx) | Never for this project. npm version is stale and insecure. CDN install is fragile. |
| jsPDF + autotable | pdfmake | If you need highly complex PDF layouts with columns, watermarks, and rich formatting. jsPDF is simpler and sufficient for tabular reports. |
| Polling | Full WebSocket | If the university grows to need sub-second updates across many concurrent dashboards. Current scale doesn't warrant the complexity. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| SheetJS (xlsx) from npm | v0.18.5 on npm is 4 years old with known vulnerabilities. New versions only on custom CDN. | ExcelJS ^4.4.0 |
| Frappe Charts (frappe-charts) | Frappe's own charting lib is basic, limited chart types, minimal interactivity, and primarily designed for Frappe Desk, not standalone SPAs. | ApexCharts |
| D3.js directly | Too low-level for dashboard charts. You'd spend weeks building what ApexCharts provides out of the box. D3 is for custom, novel visualizations. | ApexCharts |
| Vuetify / Quasar / PrimeVue | Full component libraries that bring their own design system. Conflicts with existing Tailwind CSS approach and bloats bundle. | Headless libs (TanStack) + Tailwind |
| html2pdf.js | Renders HTML to canvas to PDF — inconsistent results, poor pagination control, browser-dependent output. | jsPDF (programmatic PDF) |
| Axios | Unnecessary when Frappe provides its own `frappe.call()` HTTP client that handles CSRF, sessions, and error formatting. | frappe.call() / fetch with Frappe session |

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| vue3-apexcharts ^1.11.1 | Vue ^3.5, apexcharts ^5.x | Must install both apexcharts AND vue3-apexcharts |
| @vueuse/core ^14.2.1 | Vue ^3.5+ | v14.0+ dropped Vue 3.4 and earlier support |
| @tanstack/vue-table ^8.21.3 | Vue ^3.3+ | Headless — no CSS dependencies |
| jspdf-autotable ^5.0.7 | jsPDF ^4.x | Plugin — requires jsPDF as peer dependency |
| ExcelJS ^4.4.0 | Node 16+ / Browser | Works client-side via Vite bundling |

## Bundle Size Impact

| Package | Gzipped Size | Notes |
|---------|-------------|-------|
| apexcharts | ~130KB | Loaded once, cached. Tree-shakeable chart types in v5. |
| @vueuse/core | ~15KB (typical) | Tree-shakeable — only imported composables are bundled |
| @tanstack/vue-table | ~14KB | Headless, minimal footprint |
| jspdf + autotable | ~280KB | Only loaded on export action (dynamic import recommended) |
| exceljs | ~320KB | Only loaded on export action (dynamic import recommended) |

**Total always-loaded addition:** ~160KB gzipped (ApexCharts + VueUse composables + TanStack Table).
**Lazy-loaded on demand:** ~600KB (PDF + Excel export — loaded only when user clicks "Export").

## Sources

- [vue3-apexcharts npm](https://www.npmjs.com/package/vue3-apexcharts) — version 1.11.1 verified
- [apexcharts npm](https://www.npmjs.com/package/apexcharts) — version 5.10.4 verified
- [@tanstack/vue-table npm](https://www.npmjs.com/package/@tanstack/vue-table) — version 8.21.3 verified
- [jsPDF npm](https://www.npmjs.com/package/jspdf) — version 4.2.1 verified, v4.0 security overhaul noted
- [jspdf-autotable npm](https://www.npmjs.com/package/jspdf-autotable) — version 5.0.7 verified
- [ExcelJS npm](https://www.npmjs.com/package/exceljs) — version 4.4.0 verified
- [@vueuse/core npm](https://www.npmjs.com/package/@vueuse/core) — version 14.2.1 verified
- [Luzmo Vue Chart Library Guide](https://www.luzmo.com/blog/vue-chart-libraries) — charting library comparison
- [ECharts vs ApexCharts StackShare](https://stackshare.io/stackups/apexcharts-vs-echarts) — performance comparison
- [SheetJS npm warning](https://git.sheetjs.com/sheetjs/sheetjs/issues/3098) — stale npm version, security vulnerabilities
- [Frappe Realtime API docs](https://docs.frappe.io/framework/user/en/api/realtime) — publish_realtime, socket.io architecture
- [Frappe v15 Database API](https://docs.frappe.io/framework/v15/user/en/api/database) — get_list, sql methods
- [Vue Router Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html) — meta-based role routing pattern
- [Frappe v15 Reports docs](https://docs.frappe.io/framework/v15/user/en/desk/reports) — report types and API

---
*Stack research for: University ERP Dashboards, Analytics & Role-Based Portals*
*Researched: 2026-03-17*
