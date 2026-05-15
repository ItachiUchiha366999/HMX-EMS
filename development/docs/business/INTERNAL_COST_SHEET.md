# University ERP — Internal Cost Sheet

**Purpose:** Internal reference for actual cost to develop and deliver to a client
**Classification:** Internal Only
**Date:** March 2026

---

## Cost Basis

| Component | Monthly | Per Hour (160 hrs/month) |
|-----------|---------|--------------------------|
| Developer Cost | ₹5,000 | ₹31 |
| Claude Code Max | ₹25,000 | ₹156 |
| **Total** | **₹30,000** | **₹187 → rounded to ₹190/hr** |

---

## 1. Base Product Development Cost (Already Built — Amortized)

The entire product (22 phases, 17 modules, 155 DocTypes, 13,000+ lines of code) was built in **1 week** using Claude Code Max as the primary development tool.

| Component | Actual Time | Actual Cost |
|-----------|------------|------------|
| Developer (₹5,000/month ÷ 4.33 weeks) | 1 week | ₹1,155 |
| Claude Code Max (₹25,000/month ÷ 4.33 weeks) | 1 week | ₹5,775 |
| **Total Base Product Cost** | **1 week** | **₹6,930** |

> This is the actual money spent to build the entire University ERP product from scratch.

**Amortization per client (essentially negligible after first client):**

| Clients Served | Cost Per Client |
|---------------|----------------|
| 1 | ₹6,930 |
| 5 | ₹1,386 |
| 10 | ₹693 |
| 20 | ₹347 |

---

## 2. Per-Client Implementation Cost

### 2.1 Requirement Analysis

| Activity | Hours | Cost |
|----------|-------|------|
| Discovery meetings & stakeholder interviews | 16 | ₹3,040 |
| Business process mapping | 20 | ₹3,800 |
| ERP gap analysis | 12 | ₹2,280 |
| Fee structure & data audit | 16 | ₹3,040 |
| Requirement document & implementation plan | 24 | ₹4,560 |
| Proposal and sign-off | 4 | ₹760 |
| **TOTAL** | **92 hrs** | **₹17,480** |

### 2.2 Configuration & Development

| Task | Hours | Cost |
|------|-------|------|
| Client-specific configuration (programs, fee heads, academic year) | 24 | ₹4,560 |
| Custom fields, roles, permissions | 16 | ₹3,040 |
| Payment gateway setup (Razorpay / PayU) | 8 | ₹1,520 |
| SMS / WhatsApp / Email setup | 12 | ₹2,280 |
| Report customization | 16 | ₹3,040 |
| Portal branding | 12 | ₹2,280 |
| DigiLocker / Biometric setup | 8 | ₹1,520 |
| Testing & debugging | 48 | ₹9,120 |
| **TOTAL** | **144 hrs** | **₹27,360** |

### 2.3 Data Migration

| Task | Hours | Cost |
|------|-------|------|
| Data audit & Excel template preparation | 20 | ₹3,800 |
| Student, result, fee history import | 52 | ₹9,880 |
| Employee / faculty / library data import | 28 | ₹5,320 |
| Chart of accounts & opening balances | 12 | ₹2,280 |
| Validation scripts, dry run, corrections | 44 | ₹8,360 |
| **TOTAL** | **156 hrs** | **₹29,640** |

### 2.4 Deployment

| Task | Hours | Cost |
|------|-------|------|
| Server / cloud setup, Frappe install, Nginx, SSL | 16 | ₹3,040 |
| Backup, monitoring, security config | 9 | ₹1,710 |
| Staging environment & performance testing | 8 | ₹1,520 |
| **TOTAL** | **33 hrs** | **₹6,270** |

### 2.5 Training & Go-Live

| Task | Hours | Cost |
|------|-------|------|
| Admin, finance, HR, student affairs training | 22 | ₹4,180 |
| User manuals & documentation | 10 | ₹1,900 |
| UAT support & issue resolution | 28 | ₹5,320 |
| Go-live monitoring (day-of + 2 weeks post) | 24 | ₹4,560 |
| **TOTAL** | **84 hrs** | **₹15,960** |

---

## 3. Total Per-Client Delivery Cost

| Component | Internal Cost | Notes |
|-----------|---------------|-------|
| Base Product (actual cost, amortized @ 10 clients) | ₹693 | Negligible — built in 1 week for ₹6,930 total |
| Requirement Analysis | ₹17,480 | 92 hrs |
| Configuration & Development | ₹27,360 | 144 hrs |
| Data Migration | ₹29,640 | 156 hrs |
| Deployment | ₹6,270 | 33 hrs |
| Training & Go-Live | ₹15,960 | 84 hrs |
| **TOTAL COST TO GO LIVE** | **₹97,403** | **509 hrs of delivery work** |

> **It costs us under ₹1 Lakh in real money to fully go live with one client.**
> The base product cost is effectively zero after the first client — it was built in 1 week for ₹6,930 total.
> Delivery work (509 hrs) at ₹190/hr spread over ~3 months = ~₹30,000/month burn rate.

---

## 4. Recurring Monthly Cost (Post Go-Live, Per Client)

| Component | Monthly Cost |
|-----------|-------------|
| Developer + Claude Code (shared overhead) | ₹30,000 |
| Hosting — Starter VPS (< 500 students) | ₹1,670 |
| Hosting — Standard Cloud (500–2,000 students) | ₹4,650 |
| Hosting — Professional Cloud (2,000–5,000 students) | ₹5,920 |

**AMC Labour Cost Per Tier:**

| AMC Tier | Included Hours/Month | Monthly Labour Cost |
|----------|---------------------|---------------------|
| Basic | 2 hrs | ₹380 |
| Priority | 8 hrs | ₹1,520 |
| Enterprise | 20 hrs | ₹3,800 |

---

## 5. Travel / On-Site Cost (When Required)

| Item | Internal Cost |
|------|--------------|
| Remote support | ₹190/hr |
| On-site support | ₹300/hr |
| Full day on-site | ₹2,400/day |
| Local travel | ₹500 flat/visit |
| Outstation petrol | ₹12/km |
| Daily allowance (DA) | ₹1,500/day |
| Hotel | ₹2,500–₹4,000/night |
| Flight | Actuals |

---

## 6. Quick Reference — Cost vs Charge

| What We Charge Client | What It Costs Us | Gross Margin |
|-----------------------|-----------------|-------------|
| Package A — ₹4,00,000 one-time | ~₹65,000 | ~84% |
| Package B — ₹7,50,000 one-time | ~₹97,000 | ~87% |
| Package C — ₹12,00,000 one-time | ~₹1,40,000 | ~88% |
| AMC Basic — ₹5,000/month | ₹380 labour + ₹1,670 hosting = ₹2,050 | ~59% |
| AMC Priority — ₹12,000/month | ₹1,520 labour + ₹4,650 hosting = ₹6,170 | ~49% |
| AMC Enterprise — ₹25,000/month | ₹3,800 labour + ₹5,920 hosting = ₹9,720 | ~61% |

> **Key fact:** The base product (17 modules, 155 DocTypes) cost only ₹6,930 to build (1 week).
> Every rupee charged above delivery cost is near-pure profit.

---

*All costs in ₹. Internal use only. March 2026.*
