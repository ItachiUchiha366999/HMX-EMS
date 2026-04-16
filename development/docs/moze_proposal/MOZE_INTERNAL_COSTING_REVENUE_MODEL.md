# MOZE Educational Trust — Internal Costing & Revenue Model

```
╔══════════════════════════════════════════════════════════════════╗
║   INTERNAL / CONFIDENTIAL — HMX EYES ONLY                      ║
║   DO NOT SHARE WITH CLIENT, PARTNERS, OR EXTERNAL PARTIES       ║
║   This document contains actual cost data, margin analysis,     ║
║   and strategic pricing intelligence.                           ║
╚══════════════════════════════════════════════════════════════════╝
```

**Prepared by:** HMX Strategy & Implementation
**Client:** G.S. MOZE Educational Trust
**Document Type:** Internal Revenue & Cost Model
**Date:** March 2026
**Status:** Active — Update after each contract milestone
**Revision:** v2.0 — portal-vue unified frontend incorporated

---

## Executive Summary (Brutally Honest)

| Metric | Figure |
|--------|--------|
| Year 1 revenue from MOZE | ₹27,05,000 |
| Actual cost to deliver Year 1 (revised with portal) | ~₹3,60,000–₹4,00,000 |
| **Year 1 gross margin** | **~85–87%** |
| Year 2+ annual revenue | ~₹9,15,000 |
| Year 2+ actual cost | ~₹1,15,000–₹1,40,000 |
| **Year 2+ gross margin** | **~85–87%** |
| 10-year gross profit (internal estimate) | ~₹1.08–₹1.12 Crore |
| Time to break even | **Day 1 — advance alone exceeds total cost** |

MOZE is a high-margin engagement. The backend product was already built. What is actively being built now is the portal-vue — a Vue 3 SPA frontend that is role-aware, mobile-responsive, and visually superior to anything a competitor using default Frappe Desk can offer. The portal is not a cosmetic addition. It is, from the client's perspective, the entire product. It is what MOZE management will demo to their college principals. It is what 25,000 students will use on their phones. The portal IS the reason ₹12L+ is a justifiable build fee.

The portal adds development cost (est. ₹65,000–₹80,000 incremental). It is worth every rupee because it is the primary reason we win deals and the primary reason clients do not leave.

---

## 1. Development Cost Analysis

### 1.1 Team Composition for MOZE Project

| Role | Person | Monthly Cost | Notes |
|------|--------|-------------|-------|
| Lead Developer / Implementer | 1 developer | ₹5,000 | Salary / self-draw |
| Claude Code Max (AI force multiplier) | Subscription | ₹25,000 | Does the work of 5–8 additional developers |
| **Total team monthly burn** | | **₹30,000** | ₹190/hr effective rate |

**There is no other team.** This is intentional and sustainable. Claude Code Max is not a "tool" — it is the primary development engine. The human developer directs, reviews, and delivers. The AI writes 80–90% of the code. This is why our margins are structurally impossible for a traditional team to match.

**Why 1 dev + Claude Code = team of 5–10:**
- A standard junior-to-mid developer in Pune/Nashik costs ₹25,000–₹60,000/month
- A 5-person team (backend + frontend) costs ₹1.5–₹4 lakh/month — more with Vue 3 specialists
- Claude Code Max produces production-quality Frappe/Python/JavaScript/Vue code, JSON DocType schemas, test cases, and documentation in real-time
- Our build time for the entire backend (17 modules, 155 DocTypes, 13,000+ lines): **1 week, ₹6,930 total**
- The portal-vue frontend, with 23 Faculty components complete and the full SPA architecture established, is being built iteratively — shared component library means each new portal section is faster than the last
- A 5-person traditional team (including a Vue specialist) would have taken 4–8 months and spent ₹8–20 lakh for equivalent output

### 1.2 Base Product Cost — Already Amortized

The backend exists. It cost ₹6,930 to build (1 week in March 2026). For MOZE, the amortized base product cost is effectively ₹0 in any honest accounting. The portal-vue frontend is a live, ongoing build — its amortized cost is slightly higher because the Faculty portal (Phase 1 of the frontend) is complete and reusable for all future clients.

| Amortization scenario | Backend Cost per MOZE | Portal Cost per MOZE |
|-----------------------|----------------------|----------------------|
| MOZE is client #1 | ₹6,930 | Full portal cost (they fund the build) |
| MOZE is client #2 | ₹3,465 | ~50% (shared with client #1) |
| MOZE is client #5 | ₹1,386 | ~20% (five clients share amortized cost) |

For this model, we use ₹6,930 for the backend (worst case, MOZE is first client) and attribute the full portal completion cost to MOZE since the portal is being built with MOZE as the reference deployment. Every future client gets this portal for near-zero marginal cost.

### 1.3 The Portal-Vue Frontend — What It Is and Why It Matters

The portal-vue is a Vue 3 Single Page Application that replaces the default Frappe Desk interface for end users. It is not a theme or a skin. It is a completely separate frontend with:

- **Role-based routing:** 7 distinct user types each see a completely different interface
  - Student portal (11 views to build)
  - Faculty portal (COMPLETE — 23 components, 27 backend API endpoints)
  - HOD portal (role-specific dashboard, departmental oversight)
  - Parent portal (ward's attendance, fees, results — read-only)
  - Management portals × 4 sub-roles (VC, Principal, Trust Management, Finance Officer)
  - Finance portal (fee collection, dues, receipts)
  - Admin portal (system configuration, reports)
- **Shared component library:** KpiCard, ChartWrapper, DataTable, FilterBar, NotificationPanel, SidebarNav — built once, used by all portals
- **Mobile-first responsive design:** Students use this on ₹8,000 Android phones — this is non-negotiable
- **PWA-ready architecture:** Service worker, manifest, offline caching already scaffolded
- **Vibrant, modern UI:** Not Frappe's grey institutional look — actual UX design with colors, iconography, and hierarchy that non-technical users find intuitive

**Current build status (March 2026):**

| Portal Section | Status | Components/Views | Backend Endpoints |
|----------------|--------|-----------------|-------------------|
| Faculty portal | COMPLETE | 23 components | 27 endpoints |
| Student portal | TO BUILD | 11 views | ~18 endpoints (est.) |
| Management × 4 roles | TO BUILD | 4 role dashboards | ~12 endpoints (est.) |
| HOD portal | TO BUILD | ~6 views | ~8 endpoints (est.) |
| Parent portal | TO BUILD | ~4 views | ~5 endpoints (est.) |
| Finance portal | TO BUILD | ~5 views | ~7 endpoints (est.) |
| Scheduled reports module | TO BUILD | ~3 views | ~6 endpoints (est.) |
| **Total remaining** | **6 of 10 phases** | **~33 views** | **~56 endpoints (est.)** |

**Key cost dynamic:** The Faculty portal took the longest because it established the architecture, the shared component library, the API conventions, and the authentication patterns. All remaining portals build on this foundation. Each subsequent portal is approximately 40–60% faster to build than the Faculty portal. This is the classic platform effect — the first is the most expensive, the rest are incremental.

### 1.4 Hours Estimate: 19-Institute Setup vs Single-Institute Baseline — Revised with Portal

The single-institute delivery baseline without a custom portal: ~509 hours. MOZE gets the full portal-vue implementation. This adds frontend development hours on top of the standard backend delivery. However, the portal is built ONCE and deployed for all 19 institutes simultaneously — it does not scale with institute count.

**Backend delivery (19-institute MOZE):**

| Phase | Single Institute (hrs) | MOZE 19-Institute (hrs) | Notes |
|-------|----------------------|------------------------|-------|
| Requirement Analysis | 92 | 160 | 19 institutes = more stakeholders, more discovery sessions, more fee structures |
| Configuration & Development (backend) | 144 | 220 | Core config once; replicate institute-level data; custom fields, roles per institute type |
| Data Migration | 156 | 380 | 19 institutes × student/fee/employee data; most expensive phase at scale |
| Deployment | 33 | 50 | Single deployment, multi-institute performance tuning, load testing |
| Training & Go-Live | 84 | 200 | Staggered rollout; super-admin model reduces our hours |
| **Backend subtotal** | **509 hrs** | **~1,010 hrs** | ~2× single due to shared config, not 19× |

**Portal-vue frontend (added for MOZE — built once, shared across all 19):**

| Portal Phase | Estimated Hours | Notes |
|--------------|----------------|-------|
| Student portal (11 views) | 80 hrs | Largest remaining section; attendance, fees, results, timetable, etc. |
| Management portals × 4 roles | 60 hrs | 4 dashboards, each with KPI cards and drill-downs; shared KpiCard component speeds this up |
| HOD portal | 35 hrs | Departmental oversight; simpler than management |
| Parent portal | 25 hrs | Read-only ward summary; simplest portal |
| Finance portal | 35 hrs | Fee collection UI, dues management; moderate complexity |
| Scheduled reports module | 20 hrs | Report scheduler + download interface |
| Integration testing (all portals) | 30 hrs | Cross-role testing, API validation, mobile responsiveness QA |
| Per-institute config (logo, theme, nav) × 19 | 38 hrs | 2 hrs per institute for branding config — this is low because it is config, not code |
| **Portal subtotal** | **~323 hrs** | **Built once; serves all 19 institutes** |

**Grand total hours (MOZE, with portal):**

| Category | Hours |
|----------|-------|
| Backend delivery (19 institutes) | 1,010 hrs |
| Portal-vue completion | 323 hrs |
| **Total** | **~1,333 hrs** |

The 1,333 hours spread over 5–7 months for MOZE = ~190–270 hours/month. At ₹190/hr effective rate, this is ₹36,000–₹51,000/month in labour cost — manageable within our ₹30,000/month team envelope because Claude Code compresses actual clock hours significantly. The AI writes code; we review and integrate. Real calendar hours are ~40–50% of raw hour estimates.

### 1.5 Total Internal Cost to Deliver MOZE Year 1 — Revised with Portal

| Component | Hours | Internal Cost | Notes |
|-----------|-------|--------------|-------|
| Base product (amortized, backend) | — | ₹6,930 | Worst case (client #1) |
| Requirement Analysis | 160 hrs | ₹30,400 | 160 × ₹190 |
| Configuration & Development (backend) | 220 hrs | ₹41,800 | 220 × ₹190 |
| Data Migration (19 institutes) | 380 hrs | ₹72,200 | 380 × ₹190; largest backend cost |
| Deployment & Infrastructure Setup | 50 hrs | ₹9,500 | 50 × ₹190 |
| Training & Go-Live (staggered) | 200 hrs | ₹38,000 | 200 × ₹190 |
| **Portal-vue: Student portal** | 80 hrs | ₹15,200 | 80 × ₹190 |
| **Portal-vue: Management portals (×4)** | 60 hrs | ₹11,400 | 60 × ₹190 |
| **Portal-vue: HOD + Parent + Finance** | 95 hrs | ₹18,050 | 95 × ₹190 |
| **Portal-vue: Scheduled reports** | 20 hrs | ₹3,800 | 20 × ₹190 |
| **Portal-vue: Integration testing + QA** | 30 hrs | ₹5,700 | 30 × ₹190 |
| **Portal-vue: Per-institute theming (×19)** | 38 hrs | ₹7,220 | 38 × ₹190 |
| AMC Year 1 Labour (20 hrs/month × 12) | 240 hrs | ₹45,600 | AMC support during Year 1 |
| Infrastructure (MOZE hosts = ₹0; monitoring tools buffer) | — | ₹12,000 | Third-party monitoring SaaS |
| Miscellaneous / buffer (travel, comms, tools, browser testing) | — | ₹30,000 | Higher than before due to device testing overhead |
| **TOTAL YEAR 1 COST** | **~1,333 hrs** | **~₹3,47,800** | |

**Rounded conservative figure: ₹3,60,000–₹4,00,000** (including 15% scope creep buffer — see Risk section).

**Year 1 revenue charged: ₹27,05,000**

**Year 1 gross profit: ~₹23,05,000–₹23,45,000**

**Year 1 gross margin: ~85–87%**

> Note: Infrastructure cost is ₹0 because MOZE pays their own hosting per the proposal. If MOZE ever asks us to host, recalculate at cost + 40% margin (see Section 2). The portal does not materially change infrastructure cost — it is static-built Vue assets served through Nginx. No additional server resources required.

> Honest note on margin impact: The portal adds ~₹61,370 in direct labour cost over the backend-only estimate. This reduces Year 1 gross margin from ~89.6% to ~85–87%. This is the right trade — the portal is what makes the ₹12L build fee defensible. Without it, a client could fairly ask why they are paying ₹12L for a "configured Frappe instance." With it, they are buying a custom-built multi-role ERP portal that no competitor in the state has deployed at this scale.

---

## 2. Infrastructure Cost vs Client Pricing

### 2.1 What MOZE Hosting Actually Costs Us

MOZE: 19 institutes, 25,000 students — largest scale tier in our model. The portal-vue frontend does not meaningfully change server requirements. Vue apps are compiled to static files (HTML/CSS/JS) — they add ~2–5 MB of assets served via Nginx. No additional compute, no additional database load.

| Component | Monthly Cost (HMX Internal) | Annual |
|-----------|---------------------------|--------|
| Cloud VPS / managed server (8–16 vCPU, 32GB RAM, 500GB SSD) | ₹18,000 | ₹2,16,000 |
| MariaDB managed (or self-hosted) | ₹2,500 | ₹30,000 |
| Redis / cache | ₹800 | ₹9,600 |
| Nginx / SSL / CDN (serves portal static files + API) | ₹350 | ₹4,200 |
| Backup storage (offsite) | ₹800 | ₹9,600 |
| Monitoring (UptimeRobot Pro / similar) | ₹200 | ₹2,400 |
| **Total infrastructure monthly** | **₹22,650–₹23,650** | **₹2,71,800–₹2,83,800** |

The portal has no incremental infrastructure cost. One Nginx instance that already serves Frappe also serves the compiled Vue SPA from a `dist/` folder. This is an important talking point internally: we are selling a significantly more premium product without a corresponding increase in our cost base.

### 2.2 Per the Proposal — MOZE Pays Hosting Directly

The MOZE proposal specifies the client arranges and pays for their own hosting. This is strategically excellent for the same reasons as before, and the portal does not change this calculus.

- Our infrastructure cost for MOZE: ₹0
- Our AMC includes labour + monitoring support, not server bills
- Portal updates (new components, new views) are pushed as code deployments — no infra cost
- This eliminates our single largest recurring cost item entirely

**Verify this is watertight in the contract.** If MOZE decides to outsource hosting to us in Year 2, recalculate at cost + 40% margin.

### 2.3 Infrastructure Margin Summary

| Scenario | Monthly Infra Cost to Us | AMC Revenue (Infra-related portion) | Margin |
|----------|--------------------------|-------------------------------------|--------|
| MOZE pays own hosting | ₹0 | ₹0 (not charged separately) | N/A |
| We host MOZE (if they ask) | ₹23,650 | We would charge ₹35,000–₹40,000/month | ~40–69% |

If we ever take on MOZE hosting: charge minimum ₹33,000/month (₹3,96,000/year). Do not disclose actual infrastructure cost. Note that hosting the portal adds no incremental server cost — the same server price covers everything.

---

## 3. AMC Strategy

### 3.1 What AMC Actually Costs Us to Deliver

Per the proposal, MOZE Year 1 AMC = ₹7,35,000/year (₹61,250/month).

**What MOZE gets under AMC (Enterprise tier):**
- 20 hours/month of labour (bug fixes, minor changes, support queries, portal updates)
- System updates and Frappe version patches
- Portal-vue component updates as new features are requested (within 20hr allocation)
- Monitoring and uptime support
- SLA: 4-hour critical response, 24-hour standard

The portal adds a material dimension to what AMC covers. Portal bugs (a button not working on mobile, a chart rendering incorrectly, a route not loading for a specific role) are part of AMC scope. This is appropriate — portal issues are the most visible to end users and the fastest to produce complaint calls. Budget ~4–6 hrs/month of the 20hr AMC allocation for portal maintenance. This is already within the existing allocation and changes nothing financially.

| Cost Component | Monthly | Annual |
|---------------|---------|--------|
| Labour: 20 hrs/month × ₹190/hr | ₹3,800 | ₹45,600 |
| Infrastructure (if we host) | ₹23,650 | ₹2,83,800 |
| Infrastructure (if MOZE hosts — per proposal) | ₹0 | ₹0 |
| **Total AMC cost (MOZE hosts)** | **₹3,800** | **₹45,600** |
| **Total AMC cost (we host)** | **₹27,450** | **₹3,29,400** |

### 3.2 AMC Revenue vs Cost Analysis

**Scenario A: MOZE hosts (per proposal — most likely)**

| | Monthly | Annual |
|--|---------|--------|
| AMC Revenue | ₹61,250 | ₹7,35,000 |
| AMC Cost (labour only) | ₹3,800 | ₹45,600 |
| **Gross Profit** | **₹57,450** | **₹6,89,400** |
| **Gross Margin** | **93.8%** | **93.8%** |

**Scenario B: We host MOZE (if arrangement changes)**

| | Monthly | Annual |
|--|---------|--------|
| AMC Revenue | ₹61,250 | ₹7,35,000 |
| AMC Cost (labour + infra) | ₹27,450 | ₹3,29,400 |
| **Gross Profit** | **₹33,800** | **₹4,05,600** |
| **Gross Margin** | **55.2%** | **55.2%** |

The AMC model in Scenario A remains extraordinarily profitable. The portal does not degrade AMC margin — it actually gives us more leverage at renewal time because the portal is what clients SEE and what their end-users depend on daily.

### 3.3 Year-over-Year AMC Margin (as student count grows)

| Year | Students | AMC Revenue | Labour Cost | Infra Cost (Scenario A) | Gross Margin |
|------|----------|-------------|-------------|------------------------|-------------|
| Y1 | 25,000 | ₹7,35,000 | ₹45,600 | ₹0 | 93.8% |
| Y2 | 26,000 | ₹7,35,000 | ₹45,600 | ₹0 | 93.8% |
| Y3 | 27,500 | ₹7,35,000 + PPI increase | ₹49,400 | ₹0 | ~93% |
| Y4 | 29,000 | ₹8,08,500 (+10% CPI) | ₹52,000 | ₹0 | ~93.5% |
| Y5 | 31,000 | ₹8,08,500 | ₹55,000 | ₹0 | ~93.2% |

**Key insight:** The portal reinforces this dynamic. As student count grows, portal usage grows. MOZE becomes more dependent on the portal — not less. There is no "the system is stable, why do we need AMC" argument when 25,000+ students are logging into a live Vue SPA every day. The portal creates continuous operational dependency that backends alone do not.

### 3.4 AMC Price Increase Strategy

**CPI Linkage (recommended):**
- Contractual clause: AMC increases by CPI or 10% (whichever is higher) from Year 3 onward
- Current CPI in India: ~5–6% — our 10% floor gives real margin expansion every year
- Frame as "cost of living adjustment" — clients almost never push back on CPI-linked increases
- MOZE's Year 3 AMC target: ₹8,08,500/year

**Feature Addition Upsells (convert portal features into AMC "tier upgrades"):**
- New portal role added (e.g., Alumni portal, Placement company external login) → justify ₹40K–₹60K one-time + ₹25K AMC increase
- New dashboard widget or KPI card on management portal → ₹10K–₹20K per widget set
- Add WhatsApp Business integration with notification panel in portal → justify ₹25K increase in AMC
- PWA full activation (push notifications + offline mode) → justify ₹30K–₹50K one-time + ₹20K AMC increase
- Per-institute custom theme (different brand colors per college) → ₹8K–₹15K per institute one-time

**Volume Add-on:**
- As MOZE adds colleges, charge "multi-institute scaling fee" within AMC: ₹5,000/year per college above base 19 — nominally justified, near-zero cost to deliver since the portal code is already deployed

### 3.5 Floor Price for AMC Negotiation

If MOZE attempts to renegotiate AMC down, know our floor:

| Scenario | Our Floor AMC | Rationale |
|----------|--------------|-----------|
| MOZE hosts (current) | ₹2,50,000/year | Covers 20 hrs/month labour + 40% overhead + profit |
| We host | ₹5,00,000/year | Covers labour + infra + 20% margin minimum |
| Absolute minimum to retain (relationship) | ₹1,80,000/year | Covers direct labour cost only — accept ONLY if strategic |

**Never go below ₹2,50,000/year if MOZE hosts.** Below that level, the account is not worth servicing.

**The portal strengthens our negotiating position.** If MOZE tries to argue they can manage without us, the honest response is: who maintains the Vue SPA? Who deploys portal updates? Who fixes the mobile rendering issue when a new Android version breaks the PWA manifest? Their internal IT team cannot. This is not a threat — it is an accurate description of operational reality.

**Negotiation lever:** If MOZE pushes back on AMC, offer "Basic" tier at ₹4,00,000/year (8 hrs/month response, 24-hour SLA, no portal feature updates — bug fixes only). This feels like a concession but is still 89%+ margin.

---

## 4. Profit Margin Analysis

### 4.1 Year 1 Gross Margin

| Revenue Item | Amount |
|-------------|--------|
| Build Fee | ₹12,10,000 |
| Setup Fee (19 × ₹40,000) | ₹7,60,000 |
| AMC Year 1 | ₹7,35,000 |
| **Total Year 1 Revenue** | **₹27,05,000** |

| Cost Item | Amount |
|----------|--------|
| Base product (amortized, backend) | ₹6,930 |
| Requirement Analysis (160 hrs) | ₹30,400 |
| Configuration & Development — backend (220 hrs) | ₹41,800 |
| Data Migration — 19 institutes (380 hrs) | ₹72,200 |
| Deployment & Setup (50 hrs) | ₹9,500 |
| Training & Go-Live — staggered (200 hrs) | ₹38,000 |
| **Portal-vue — Student portal (80 hrs)** | **₹15,200** |
| **Portal-vue — Management × 4 roles (60 hrs)** | **₹11,400** |
| **Portal-vue — HOD + Parent + Finance (95 hrs)** | **₹18,050** |
| **Portal-vue — Scheduled reports (20 hrs)** | **₹3,800** |
| **Portal-vue — Integration testing + QA (30 hrs)** | **₹5,700** |
| **Portal-vue — Per-institute theming × 19 (38 hrs)** | **₹7,220** |
| AMC Year 1 Labour (20 hrs/month × 12) | ₹45,600 |
| Infrastructure (MOZE hosts = ₹0; monitoring tools) | ₹12,000 |
| Miscellaneous / buffer (travel, comms, browser testing) | ₹30,000 |
| **Total Year 1 Cost** | **~₹3,47,800** |

**Year 1 Gross Profit: ₹27,05,000 − ₹3,47,800 = ₹23,57,200**

**Year 1 Gross Margin: ~87.1%**

> Even if actual hours run 20% over estimate (scope creep buffer), gross margin stays above 84%.

> Context: The previous estimate (without portal) showed ~89.6% gross margin. The portal adds ~₹66,370 in real cost. That reduction in margin from 89.6% to 87.1% is the correct trade: the portal is the primary justification for charging ₹12,10,000 as a build fee rather than ₹6–8L. Without the portal, a MOZE-type client is looking at a configured Frappe Desk instance — there is no rational reason to pay ₹12L for that. The portal earns us the premium.

### 4.2 Year 2+ Gross Margin

| Revenue Item | Amount (Year 2) |
|-------------|----------------|
| AMC (base) | ₹7,35,000 |
| New college setup (2 new @ ₹40K each) | ₹80,000 |
| PPI / Per-student increase | ₹1,00,000 |
| Portal upsell (new widgets / dashboard for management) | ₹30,000 |
| **Total Year 2 Revenue** | **~₹9,45,000** |

| Cost Item | Amount (Year 2) |
|----------|----------------|
| AMC Labour (20 hrs/month × ₹190 × 12) | ₹45,600 |
| New college setup labour (2 × ~₹8,000 per institute incl. portal theming) | ₹16,000 |
| PPI processing / feature work | ₹15,000 |
| Portal upsell delivery (new dashboard widgets) | ₹6,000 |
| Tools and monitoring overhead | ₹12,000 |
| **Total Year 2 Cost** | **~₹94,600** |

**Year 2 Gross Profit: ₹9,45,000 − ₹94,600 = ₹8,50,400**

**Year 2 Gross Margin: ~90.0%**

Year 2 is more profitable in margin terms than Year 1 because all delivery work is done and the portal is fully deployed. We are collecting near-passive income. Portal upsells (new widgets, new role views, theming for new colleges) carry 80–90% margins because the component library is already built.

### 4.3 Net Margin After Overhead

We carry team overhead (₹30,000/month = ₹3,60,000/year) regardless of client activity. If MOZE is the only client:

| | Year 1 | Year 2 |
|-|--------|--------|
| Gross Profit | ₹23,57,200 | ₹8,50,400 |
| Team overhead (not fully MOZE-attributable) | ₹3,60,000 | ₹3,60,000 |
| **Net Profit** | **₹19,97,200** | **₹4,90,400** |
| **Net Margin** | **~73.8%** | **~51.9%** |

If we have 2+ clients sharing team overhead, net margin on MOZE alone rises to 84%+.

### 4.4 Break-Even Analysis

There is no real break-even problem. We are profitable from the first invoice. The portal adds cost, but it does not change the cash-flow-positive day-one reality.

| Milestone | Cumulative Revenue | Cumulative Cost | Running Profit |
|-----------|-------------------|----------------|----------------|
| Proposal signing / advance (30%) | ₹8,11,500 | ₹35,000 (initial work) | ₹7,76,500 |
| Milestone 2 — Phase 1 delivery, incl. portal MVP (30%) | ₹16,23,000 | ₹1,40,000 (ongoing + portal build) | ₹14,83,000 |
| Go-live (30%) | ₹24,34,500 | ₹3,00,000 (full delivery + portal complete) | ₹21,34,500 |
| Final 10% + AMC Year 1 start | ₹27,05,000 | ₹3,47,800 | ₹23,57,200 |

**Cash flow is positive from Day 1.** The advance alone (₹8,11,500) exceeds our total cost to deliver the entire engagement. This is true even with the portal included.

### 4.5 10-Year Cash Flow Projection

| Year | Revenue | Cost | Net Profit | Cumulative |
|------|---------|------|-----------|-----------|
| Y1 | ₹27,05,000 | ₹3,47,800 | ₹23,57,200 | ₹23,57,200 |
| Y2 | ₹9,45,000 | ₹94,600 | ₹8,50,400 | ₹32,07,600 |
| Y3 | ₹9,45,000 | ₹98,000 | ₹8,47,000 | ₹40,54,600 |
| Y4 | ₹10,39,500 (+CPI) | ₹1,01,000 | ₹9,38,500 | ₹49,93,100 |
| Y5 | ₹10,39,500 | ₹1,04,000 | ₹9,35,500 | ₹59,28,600 |
| Y6 | ₹11,43,450 (+CPI) | ₹1,08,000 | ₹10,35,450 | ₹69,64,050 |
| Y7 | ₹11,43,450 | ₹1,11,000 | ₹10,32,450 | ₹79,96,500 |
| Y8 | ₹12,57,795 (+CPI) | ₹1,14,000 | ₹11,43,795 | ₹91,40,295 |
| Y9 | ₹12,57,795 | ₹1,18,000 | ₹11,39,795 | ₹1,02,80,090 |
| Y10 | ₹13,83,575 (+CPI) | ₹1,21,000 | ₹12,62,575 | ₹1,15,42,665 |

**10-year gross cumulative revenue: ~₹1.28 Crore** (portal upsells add incrementally vs prior estimate)
**10-year cumulative net profit: ~₹1.15 Crore**
**10-year overall net margin: ~90%**

---

## 5. The Portal as Competitive Moat — Strategic Analysis

This section is new and critical. It warrants its own analysis separate from pure cost accounting.

### 5.1 Why the Portal Changes Our Competitive Position Completely

Every Frappe/ERPNext implementation firm in India — and there are dozens competing for education sector contracts — sells the same underlying backend. The same DocTypes. The same workflows. The same Python business logic. When MOZE talks to Competitor A and Competitor B, both will demo a Frappe Desk interface with an "Education" module. Both will show the same fields, the same list views, the same grey interface.

We will show something completely different. We will show a custom-built Vue 3 SPA where:
- The student logs in and sees their attendance, fees, upcoming exams, and notices on a clean mobile-responsive dashboard — not a list of DocTypes
- The faculty member sees their teaching assignments, leave balance, publications, and student feedback in a single cohesive view — not a Frappe form
- The Principal sees real-time KPIs for their college — not a Frappe report that takes 45 seconds to load

**The Frappe Desk problem, stated plainly:** Default Frappe Desk was designed by developers, for developers. It is functionally powerful and visually unacceptable to non-technical end users. Students will not use it. Faculty will not love it. Management will ask why they paid ₹12 lakh for something that looks like a 2010 enterprise application. The portal solves this. The portal IS the product.

### 5.2 Head-to-Head: Us vs a Competitor with Default Frappe Desk

| Dimension | HMX (with portal-vue) | Competitor (default Frappe Desk) |
|-----------|----------------------|----------------------------------|
| Student experience | Mobile-first SPA, role-specific dashboard, modern UI | Generic Frappe Desk — confusing, desktop-centric |
| Faculty experience | 23-component portal, all workflows surfaced | Frappe forms — requires training, not intuitive |
| Management dashboards | Live Vue dashboards with chart.js, role-specific KPIs | Frappe Reports — static, slow, hard to navigate |
| Parent access | Dedicated parent portal with ward summary | No standard parent portal — custom work required |
| Mobile usability | PWA-capable, responsive by design | Frappe has a mobile site — barely functional |
| Demo impact | Instant visual differentiation | Looks identical to every other Frappe vendor |
| Client's first impression | "This is what we envisioned" | "This is the software?" |
| Annual renewal motivation | Portal creates daily usage dependency | Backend-only creates less visible dependency |

This is not a marginal difference. In a procurement decision between two vendors at similar price points, a live demo of our portal vs their Frappe Desk will win the deal for us the majority of the time. The portal is a close rate multiplier, not just a quality-of-life improvement.

### 5.3 The Portal as Switching Cost Amplifier

After 2–3 years of MOZE operating with our portal:
- 25,000+ students know this interface
- Faculty use it daily for attendance, feedback, publications
- Management has built workflows around the dashboard views
- The portal is bookmarked, potentially home-screened as PWA, integrated into the college's digital identity

**Switching to another vendor means:**
- Losing all portal customizations (they cannot take our Vue code — IP is ours)
- Retraining 25,000 students on a new interface
- Rebuilding 3+ years of workflow muscle memory across faculty and admin
- Accepting a visually inferior product (unless the competitor also builds a custom portal, which costs them ₹8–15L in dev time)

This is organic, honest lock-in. We are not trapping MOZE. We are genuinely delivering value that is hard to replicate. The switching cost is real and proportional to how good the portal is.

### 5.4 Charging Premium Because of the Portal

The ₹12,10,000 build fee is defensible *only* because of the portal. Without it, honest internal assessment: a 19-institute Frappe backend configuration and setup is worth ₹6–8L maximum against market rates.

**The portal earns us ₹4–6L of the build fee.** That is its direct revenue contribution in Year 1. And it costs us ~₹62,000 in labour to build. The ROI on portal development investment is extraordinary.

For future pricing decisions: always include the portal as a standard deliverable, not an optional add-on. Pricing the portal as optional invites clients to skip it — and then they have a weak product, a weak demo, and a weak renewal argument.

---

## 6. Upsell Opportunities

### 6.1 Upsell Menu — MOZE Specific (Revised with Portal)

#### Portal Customization Upsells — NEW

These did not exist before the portal was built. They are now recurring revenue opportunities unique to our model.

| Upsell Item | Charge | Actual Cost | Margin | Notes |
|-------------|--------|------------|--------|-------|
| New portal role/view (e.g., Alumni portal, Placement company external login) | ₹40,000–₹60,000 | ₹7,000–₹12,000 | ~82–85% | ~30–40 hrs of Vue + backend work |
| New KPI card / dashboard widget for management | ₹10,000–₹20,000 per widget set | ₹1,500–₹3,000 | ~85–90% | KpiCard component already built; mainly data/API work |
| Per-institute custom theme (logo + color scheme beyond default) | ₹8,000–₹15,000 per institute | ₹800–₹1,500 | ~90% | CSS variable overrides; trivial to deliver |
| Portal branding package (19 institutes, unique theme each) | ₹1,00,000–₹1,50,000 | ₹15,000–₹25,000 | ~83–88% | If MOZE wants each college to feel distinct |
| New report view in portal (custom analytics section) | ₹15,000–₹30,000 | ₹2,500–₹4,500 | ~85–87% | ChartWrapper component already built |
| Scheduled report module (auto-email PDF reports) | ₹20,000–₹35,000 | ₹3,800 | ~89% | Already estimated as 20 hrs to build |

#### PWA Upgrade — ₹60,000–₹1,00,000 one-time

The portal is already PWA-capable. Full PWA activation (push notifications, offline caching, home screen install prompt, splash screen) is a natural, fast upsell.

| Item | Detail |
|------|--------|
| Charge range | ₹60,000 (basic PWA activation) to ₹1,00,000 (push notifications + offline mode) |
| Actual build cost | ₹8,000–₹15,000 (service worker + manifest already scaffolded) |
| Gross margin | ~85–90% |
| Recurring | Add ₹15,000–₹20,000/year to AMC for PWA maintenance and push notification management |
| Best pitch timing | Month 3–5 after portal go-live, once student usage patterns are visible |
| Pitch angle | "Your students are already using the portal on mobile. Let them add it to their home screen — no App Store needed, instant fee alerts, exam reminders via push notification." |

#### WhatsApp Business Integration — ₹25,000–₹40,000 one-time

Integrates with the portal notification panel. Notifications that appear in the portal also fire as WhatsApp messages.

| Item | Detail |
|------|--------|
| Charge range | ₹25,000 (basic templates) to ₹40,000 (custom workflows with portal trigger) |
| Actual build cost | ₹5,000–₹8,000 |
| Gross margin | ~80–88% |
| Recurring | Per-message cost passed through; ₹5,000–₹10,000/year for template management in AMC |
| Pitch angle | "25,000 students, instant fee reminders, exam hall ticket alerts, attendance warnings — directly to WhatsApp AND the portal notification panel simultaneously." |

#### Additional Modules

| Module | Charge | Actual Cost | Margin |
|--------|--------|------------|--------|
| Research module enhancement (grant tracking, patent) | ₹40,000 | ₹7,000 | 82.5% |
| Alumni management + donation portal | ₹50,000 | ₹9,000 | 82% |
| Placement company portal (external company access via portal) | ₹50,000 | ₹9,000 | 82% |
| Advanced OBE/NAAC dashboard in management portal | ₹65,000 | ₹11,000 | 83% |
| Online examination with proctoring | ₹1,00,000 | ₹18,000 | 82% |

#### New College Onboarding — ₹40,000 each

| Item | Detail |
|------|--------|
| Charge | ₹40,000 per new institute added |
| Actual cost (labour) | ₹6,000–₹9,000 (data migration + backend config + portal theming for one institute) |
| Gross margin | ~77–85% |
| Notes | Portal theming for a new institute (logo + color theme) adds ~₹800–₹1,500 cost — negligible |

#### Custom Reports and Dashboards — ₹10,000–₹30,000 per report set

| Item | Detail |
|------|--------|
| Charge | ₹10,000 (simple report) to ₹30,000 (multi-dataset executive dashboard in portal) |
| Actual cost | ₹1,500–₹4,000 per report (ChartWrapper component reused; mainly data/query work) |
| Gross margin | ~85–90% |
| Volume potential | MOZE has 19 institutes — expect 3–5 custom report requests annually |

#### Biometric Integration — ₹35,000–₹50,000 one-time

| Item | Detail |
|------|--------|
| Charge | ₹35,000–₹50,000 |
| Actual cost | ₹7,000–₹12,000 (device-specific API work; portal attendance view already exists) |
| Gross margin | ~78–80% |
| Note | Device purchase is client's cost; attendance results surface in the existing student portal view |

#### DigiLocker Integration — ₹30,000–₹50,000 one-time

| Item | Detail |
|------|--------|
| Charge | ₹30,000–₹50,000 |
| Actual cost | ₹6,000–₹10,000 |
| Gross margin | ~80–86% |
| Strategic value | DigiLocker is a UGC/NAAC compliance requirement; certificates issued through DigiLocker can surface as downloadable links in the student portal |

#### Per-Student Price Increase (PPI)

- Year 1 base: ₹7,35,000 AMC for 25,000 students = ₹29.4/student/year
- Every 1,000 additional students: charge ₹4,000–₹5,000 incremental AMC increase
- MOZE grows ~1,000–1,500 students/year organically
- PPI revenue by Year 5: ~₹1,25,000–₹1,50,000/year
- PPI cost to us: zero (portal scales with zero marginal cost; no infra change until >40,000 students)

### 6.2 Annual Upsell Revenue Potential — Revised with Portal

| Year | Likely Upsells | Revenue |
|------|---------------|---------|
| Y2 | PWA upgrade + WhatsApp + 2 new management dashboard widgets | ₹1,45,000 |
| Y3 | 2 new colleges + custom report views × 3 + per-institute themes | ₹1,20,000 |
| Y4 | DigiLocker + Biometric + 1 new college + Alumni portal in SPA | ₹1,55,000 |
| Y5 | Online exam module + Placement portal + new analytics section in portal | ₹1,80,000 |
| Cumulative Y2–Y5 | | **~₹6,00,000** |

**Conservative annual upsell estimate: ₹1,00,000–₹1,80,000/year once relationship matures.** The portal significantly increases the upsell ceiling vs a backend-only product because every new feature request has a natural portal expression — a new view, a new widget, a new role — and each of those is billable.

---

## 7. Risk Factors

### 7.1 Client Dependency Risk — Single Large Client

**Risk:** MOZE represents potentially 100% of revenue in Year 1 if they are our first client.

**Severity:** HIGH

**Analysis:**
- If MOZE delays signing, our cash flow goes to zero
- If MOZE terminates after Year 1 (non-renewal), we lose ₹9.45L+ in annual recurring revenue
- MOZE's trust structure (19 institutes, established HEI) reduces churn risk, but does not eliminate it

**Mitigation:**
- Sign MOZE contract with a 3-year lock-in clause (AMC non-refundable after each year commences)
- Begin pursuing 1–2 additional college trust clients during MOZE delivery phase
- Target: 3 clients by end of Year 1 so no single client > 50% of ARR
- The portal, once deployed, makes non-renewal significantly less likely — daily user dependency is the most powerful retention mechanism we have

### 7.2 Scope Creep During 2–3 Month Build

**Risk:** "19 institutes" is complex. Scope expansion is near-certain, and the portal adds another vector for scope creep.

**Severity:** MEDIUM-HIGH

**Expected scope creep scenarios:**
- Each institute has unique fee structures → more data migration
- Discovery uncovers legacy systems that don't export clean data → extra migration hours
- MOZE management requests mid-project portal customizations ("can the management dashboard also show...?")
- Integration with existing accounting software (Tally?) not in scope
- Staggered rollout: some institutes go live, find portal UI issues → rework cycles

**Portal-specific scope creep risks:**
- "Can we make it look more like X?" — design revision requests after portal is coded
- "Can parents also see the fee payment history?" — new portal views requested mid-build
- Browser compatibility issues on older Android devices used by students/faculty (a real and common problem)
- Each institute's IT team will find edge cases in the portal that need fixing post-go-live

**Mitigation:**
- Define portal scope precisely in contract: list the 7 role portals and their views explicitly. Any additional view = CR at minimum ₹8,000
- Include: "Portal UI is final upon client sign-off at prototype stage — visual design changes after sign-off billed as CR"
- Include: "Browser compatibility guaranteed for Chrome/Firefox/Safari latest 2 major versions. Legacy browser support is out of scope"
- Budget 15–20% scope buffer in internal estimate (already done; ₹30,000 miscellaneous buffer)

### 7.3 19-Institute Rollout Complexity

**Risk:** Staggered rollout across 19 colleges is operationally complex for a 1-person team, and the portal adds a per-institute configuration step.

**Severity:** MEDIUM

**Mitigation:**
- Propose "Super Admin" training model: train 2–3 MOZE IT/admin staff who then cascade to institute-level users
- Portal theming per institute is low-effort (2 hrs each) — build a config panel where logo and color can be changed without code changes
- Create standard training materials (video walkthrough of each portal role) — one-time effort
- Define post-go-live support as 2 weeks per institute wave, not open-ended

### 7.4 AMC Negotiation Pressure

**Risk:** Year 2 AMC renewal is a known negotiation point.

**Severity:** MEDIUM

**Counter-strategy:**
- Ensure AMC has contractual auto-renewal with CPI linkage
- Document all portal updates, bug fixes, and feature additions delivered in Year 1 AMC — present this as tangible value at renewal
- The portal makes the "we can manage without AMC" argument implausible: who will update the Vue SPA when the next version of Chrome breaks something?
- Convert renewal conversation into "what new portal features do you want in Year 2" — make it an upsell meeting, not a cost-cutting meeting

### 7.5 Developer Availability — Single Point of Failure (ELEVATED with Portal)

**Risk:** HMX currently has 1 developer. The portal adds Vue 3 frontend skills to the requirement profile, not just Python/Frappe.

**Severity:** HIGH (elevated from prior assessment)

**Analysis:**
- Any developer who can pick up the backend can learn Frappe in 1–2 weeks
- A developer who can maintain the portal-vue must know Vue 3, the component architecture, Vite build tooling, and the API contract with Frappe
- This raises the skill floor for a replacement/backup developer
- A 1-month illness during portal delivery phase = significant delay; portal has more moving parts than backend config
- If the sole developer exits and a replacement cannot read Vue 3 code, the portal is effectively unmaintainable until someone upskills

**Mitigation:**
- Maintain thorough inline documentation for all Vue components — priority, not optional
- The component architecture (KpiCard, ChartWrapper, etc.) is standardized and readable; any competent Vue developer can navigate it with documentation
- Identify a Vue 3-capable freelancer contact NOW, before a crisis. Not a full-time hire — a vetted contractor who can be activated within 1 week for emergency support. Budget ₹500–₹800/hr for emergency portal work
- Consider: once MOZE + 1 additional client are live, hire a part-time second developer who specifically has Vue 3 skills (₹15,000–₹20,000/month for 10 hrs/week would be sufficient for AMC-level portal maintenance)
- Document the portal build process in an internal "portal-vue architecture guide" — this reduces onboarding time from months to days

### 7.6 Browser and Device Compatibility — NEW RISK (Portal Specific)

**Risk:** The portal must work correctly across the range of devices used by 25,000 students and 1,000+ faculty. This is not a controlled environment.

**Severity:** MEDIUM

**Specific concerns:**
- Students in Tier-2/3 cities often use low-end Android phones with older Chrome versions
- Some faculty may use older Safari on iPhones
- The college admin portal is likely accessed on Windows PCs with various browser configurations
- If the portal renders incorrectly for even 10% of students, the complaint volume will be significant at MOZE scale

**Mitigation:**
- Define supported browsers explicitly in the contract (Chrome 100+, Firefox 100+, Safari 15+, Samsung Internet 20+)
- Test on at least one low-end Android device (2–3GB RAM, Android 11–12) before go-live
- Use Vite/Vue 3's modern build pipeline with appropriate polyfills for target browser range
- Add a browser compatibility warning banner in the portal for unsupported browsers — sets expectation without breaking experience
- Budget 30 hours (already included in estimate) explicitly for cross-device QA

### 7.7 Portal Maintenance as an Ongoing Overhead — NEW RISK

**Risk:** Unlike the backend (which stabilises once configured), the portal needs continuous attention as requirements evolve, new features are requested, and the frontend ecosystem updates.

**Severity:** MEDIUM

**Analysis:**
- Each new module added to the backend should eventually surface in the portal — this is ongoing work
- Frontend dependencies (Vue, Vite, component libraries) require periodic updates for security and compatibility
- MOZE will request portal changes more frequently than backend changes because the portal is visible and personal to end users
- This is a higher maintenance burden than a backend-only product

**Mitigation:**
- The AMC 20hr/month allocation accounts for portal maintenance as part of standard support
- Portal feature requests outside AMC scope are billed as CRs — enforce this discipline consistently
- Annual dependency updates (Vue version bumps, Vite updates) should be planned, not reactive — schedule as quarterly maintenance windows
- The shared component library means updates to KpiCard or ChartWrapper propagate across all portals at once — this is efficient, not fragmented

---

## 8. Strategic Recommendations

### 8.1 Using MOZE as Reference Client for Other Trusts

MOZE is the most valuable asset we will have after Year 1 — the reference, the case study, and the live demo environment.

**What "19 institutes, 25,000 students, custom Vue portal" does for our sales pipeline:**
- No other competitor can credibly claim a custom-built Vue 3 ERP portal deployed at this scale in Maharashtra
- This becomes a case study that opens doors to every mid-to-large educational trust in the state
- When prospects ask "can we see a live demo?" we show them MOZE's portal (with permission) — they do not see a Frappe Desk. This is a deal-closer.
- Target: Maharashtra alone has 100+ educational trusts with 5–25 colleges each

**How to use MOZE as a reference:**
- Get written testimonial and case study permission in Year 1 AMC contract — add this clause now
- Create a demo environment that mirrors MOZE's portal with anonymized data — use this for all future sales demos
- Offer MOZE management a referral incentive: ₹20,000 off their AMC for every trust they refer that signs with us
- Present at Maharashtra higher education events, NAAC workshops — the portal demo is the centrepiece

### 8.2 The Portal as a Scalable Product (Future Clients)

For all future clients, the portal-vue is already built. Deployment cost for the next client's portal is:
- Architecture: ₹0 (already built)
- Role portals: ₹0 (Faculty, Student, Management, etc. already built)
- Configuration for new client: ~15–20 hrs (logo, theme, navigation config, data mapping)
- Cost: ~₹2,850–₹3,800 per new client's portal setup

We will charge ₹6,00,000–₹12,00,000 in build fees for future clients. The portal costs us ₹3,800 to configure for them. The margin on the portal portion of the build fee for future clients is approximately 99.9%. MOZE is funding the creation of a reusable product asset worth ₹6–10L in development value for future clients.

This is the correct frame: MOZE is not just our first client. MOZE is our product R&D funding source. We are building a polished, enterprise-grade portal on their contract budget, and every client thereafter benefits from that investment at near-zero marginal cost to us.

### 8.3 Pricing Strategy for Similar-Scale Trusts (Revised)

| Trust Size | Build Fee | Setup (per institute) | AMC/year | Portal Included? |
|-----------|-----------|----------------------|----------|-----------------|
| 1–5 institutes, <5,000 students | ₹6,00,000 | ₹40,000/institute | ₹3,50,000 | Yes — standard |
| 6–15 institutes, 5,000–15,000 students | ₹9,00,000 | ₹40,000/institute | ₹5,50,000 | Yes — standard |
| 16–25 institutes, 15,000–30,000 students | ₹12,00,000 | ₹40,000/institute | ₹7,50,000 | Yes — MOZE tier |
| 25+ institutes, >30,000 students | ₹15,00,000+ | ₹35,000/institute (volume) | ₹10,00,000+ | Yes — premium |

**Pricing principle:** The portal is included in the build fee — it is not a separate line item. Never let clients negotiate the portal out to reduce cost. The portal IS what justifies the build fee. Without it, you are selling a configured Frappe instance at a premium that cannot be defended.

**Never reveal:** Internal cost data, portal build costs, product amortization logic, or that the backend was built in 1 week for ₹6,930. Never disclose margin data to any client, partner, or external advisor.

### 8.4 When to Hire Additional Developers — Revised with Portal Considerations

| Trigger | Action |
|---------|--------|
| MOZE signed + 1 additional trust in pipeline | Hire 1 part-time developer with Vue 3 skills at ₹15,000–₹20,000/month |
| 3 active implementation clients simultaneously | Hire 1 full-time junior developer (must know Vue + Frappe) at ₹22,000–₹28,000/month |
| ARR > ₹25 lakh from AMC alone | Hire 1 mid-level developer + 1 support/training specialist |
| 10+ clients in AMC pool | Build a proper team: 1 lead dev, 2 junior devs (1 backend, 1 frontend), 1 support, 1 sales/BD |

**The Vue 3 skills requirement changes our hiring calculus.** A Frappe-only developer cannot maintain the portal. When hiring, prioritize candidates with:
1. Vue 3 / React experience (frontend SPA development)
2. Frappe/ERPNext familiarity (secondary — teachable from the codebase)
3. Python for backend API work (tertiary)

**Do not hire a pure Frappe developer** — they cannot independently maintain the portal. The leverage of having a Vue-capable hire is that they can take over frontend work while the lead developer handles backend complexity and client management.

### 8.5 Protecting Margins Long-Term

1. **Product IP is ours.** The university_erp app and the portal-vue SPA are both HMX property. Clients pay for a configured instance. They do not own the source code. On contract termination, we provide a data export — not source code. This is explicit in every contract.

2. **The portal amplifies lock-in.** Clients cannot take the portal to another vendor. A competitor would need to rebuild an equivalent Vue SPA from scratch — that is ₹8–15L and 4–6 months of development. The portal is our most powerful retention asset, and it appreciates over time as more customizations are added.

3. **AMC as the profit engine — protect it absolutely.** Never discount AMC to win a deal. Discount the setup fee for large trusts (volume narrative) if needed. Keep AMC firm. Portal maintenance is now part of what makes AMC indispensable.

4. **Avoid time-and-material commitments on portal work.** Always quote fixed price for defined portal scope. Portal design changes and new view requests after sign-off are CRs, always. Unlimited portal support requests inside AMC will erode margin — enforce the 20hr/month cap strictly.

5. **WhatsApp / SMS / payment gateway pass-through.** Pass per-message and per-transaction costs through to the client at cost + 10%. These can become material at MOZE scale.

6. **Annual Account Review meeting.** Schedule this 60 days before AMC renewal every year. Present value delivered: issues resolved, updates applied, portal improvements made, hours logged. Make the renewal a formality, not a renegotiation. Frame the meeting around "what new portal features do you want next year" — not around cost.

---

## 9. Quick Reference — MOZE Financials at a Glance

| Metric | Figure |
|--------|--------|
| Contract value Year 1 | ₹27,05,000 |
| Our cost to deliver Year 1 (with portal) | ~₹3,47,800 |
| Year 1 gross profit | **~₹23,57,200** |
| Year 1 gross margin | **~87.1%** |
| ARR from Year 2 (base + portal upsells) | ₹9,45,000 |
| Our cost Year 2 | ~₹94,600 |
| Year 2 gross profit | **~₹8,50,400** |
| Year 2 gross margin | **~90.0%** |
| 10-year cumulative revenue | ~₹1.28 Crore |
| 10-year cumulative cost | ~₹13,00,000 |
| 10-year net profit | **~₹1.15 Crore** |
| 10-year net margin | **~90%** |
| Monthly team cost (total) | ₹30,000 |
| Effective hourly rate | ₹190/hr |
| AMC cost per month (MOZE hosts) | ₹3,800 labour |
| AMC revenue per month | ₹61,250 |
| AMC margin (MOZE hosts) | **93.8%** |
| Break-even point | Day 1 (advance alone > total cost) |
| Developer headcount | 1 + Claude Code Max |
| Portal status | Faculty DONE; 6 of 10 phases remaining |
| Portal incremental cost (MOZE) | ~₹62,370 labour |
| Portal incremental revenue justified | ~₹4–6L of the ₹12.1L build fee |
| Portal ROI | **~640–960%** on development cost |

---

## 10. Confidentiality and Handling

This document contains:

- **Actual internal cost structure** — never share externally
- **AMC floor prices** — disclosure gives clients negotiating ammunition
- **Margin data** — 85–94% margins would damage trust if disclosed
- **Strategic pricing intelligence** — competitors would undercut us if aware
- **Product build cost** (backend ₹6,930; portal ~₹62,370 for completion) — extremely sensitive
- **Portal IP assertion** — contractual framing for IP ownership is a strategic asset

**Access:** Founders / directors only. Do not share with interns, contractors, or client-facing staff.

**Version control:** Update this document after MOZE signing, after each major milestone payment, at each portal phase completion, and annually at AMC renewal.

---

*All figures in Indian Rupees (₹). Internal use only. March 2026.*
*Prepared by: HMX Strategy. Classification: INTERNAL / CONFIDENTIAL.*
*v2.0 — Revised to incorporate portal-vue unified frontend strategic and cost analysis.*
