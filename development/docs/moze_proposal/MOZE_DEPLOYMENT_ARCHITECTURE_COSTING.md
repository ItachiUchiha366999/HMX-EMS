# G.S. MOZE Educational Trust — Deployment Architecture & Costing Document

**Client:** G.S. MOZE Educational Trust
**Institutes:** 19 colleges under single Frappe site, 19-company isolation
**Users:** 25,000 students + ~2,000 staff = ~27,000 total (growing to 50,000 by Year 10)
**Platform:** Frappe v16 + ERPNext + HRMS + Education + university_erp (custom app)
**Frontend:** portal-vue (Vue 3 SPA) for students/staff + Frappe Desk (admin only)
**Prepared By:** Infrastructure Architecture Team
**Date:** March 2026
**Classification:** Internal Reference — Infrastructure Planning

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Two-Tier Frontend Architecture](#2-two-tier-frontend-architecture)
3. [Load Profile & Sizing Rationale](#3-load-profile--sizing-rationale)
4. [Section A: On-Premise Deployment](#4-section-a-on-premise-deployment)
5. [Section B: Cloud Deployment](#5-section-b-cloud-deployment)
   - [B.1 AWS Architecture](#b1-aws-architecture)
   - [B.2 E2E Networks Architecture (Recommended)](#b2-e2e-networks-architecture-recommended)
6. [Section C: Cost Breakdown — Detailed INR](#6-section-c-cost-breakdown--detailed-inr)
   - [C.1 On-Premise 5-Year and 10-Year Costs](#c1-on-premise-5-year-and-10-year-costs)
   - [C.2 AWS 5-Year and 10-Year Costs](#c2-aws-5-year-and-10-year-costs)
   - [C.3 E2E Networks 5-Year and 10-Year Costs](#c3-e2e-networks-5-year-and-10-year-costs)
   - [C.4 Master Comparison Table](#c4-master-comparison-table)
7. [CI/CD Build Pipeline](#7-cicd-build-pipeline)
8. [Assumptions & Pricing Basis](#8-assumptions--pricing-basis)
9. [Risk Assessment & Recommendations](#9-risk-assessment--recommendations)

---

## 1. Executive Summary

G.S. MOZE Educational Trust operates 19 institutes under a single Frappe deployment with company-based data isolation. At 27,000 users (25,000 students + 2,000 staff) growing to 50,000 by Year 10, this is a large-scale production workload.

**Critical architectural insight:** The university_erp custom app ships a **portal-vue Vue 3 SPA** that serves as the primary interface for all 27,000 students and staff. Frappe Desk is used exclusively by ~5–10 system administrators. This two-tier frontend architecture fundamentally changes the server load profile: portal users receive a single ~250 KB JS bundle from Nginx/CDN and thereafter make only lightweight JSON API calls. Gunicorn never renders HTML pages for portal users. This reduces Gunicorn worker requirements by approximately 40% compared to a traditional Frappe-Desk-for-everyone deployment.

**Key sizing facts:**

| Metric | Value |
|--------|-------|
| Registered users | 27,000 (Year 1) → 53,000 (Year 10) |
| Normal concurrent users | 500–800 |
| Peak concurrent users | 1,500–2,500 (exam results, fee deadlines, admissions) |
| Peak API RPS (Gunicorn) | 80–180 (JSON only — SPA architecture) |
| Static asset requests | Served by Nginx/CDN, never reach Gunicorn |
| DB size progression | 10 GB (Y1) → 25 GB (Y3) → 50 GB (Y5) → 120 GB (Y10) |
| File storage growth | ~50 GB/year (documents, photos, assignments) |
| Institutes | 19 companies in one Frappe site |
| Peak seasons | June–July (admissions), Nov/Apr (exams), March (fees) |

**Deployment Options Compared:**

| Option | 5-Year TCO | 10-Year TCO | Risk Profile |
|--------|-----------|------------|-------------|
| On-Premise (self-managed) | ₹2.14 Cr | ₹4.18 Cr | Medium-High |
| AWS (Mumbai, managed) | ₹1.05–1.10 Cr | ₹2.35–2.50 Cr | Low |
| E2E Networks (India) | ₹40–44 Lakh | ₹98 Lakh–1.05 Cr | Low-Medium |

**Recommendation:** E2E Networks for Years 1–5 (SPA architecture makes lighter app servers viable), with AWS migration path at Year 5+ if concurrent users exceed 2,500 regularly.

---

## 2. Two-Tier Frontend Architecture

### 2.1 Architecture Overview

The university_erp app deploys a **two-tier frontend**:

```
TIER 1 — portal-vue (Vue 3 SPA)
  Used by: 25,000 students + 2,000 staff (99.9% of all users)
  Served by: Nginx (static files) + Cloudflare CDN (cached globally)
  Backend contact: JSON API calls only (/api/method/..., /api/resource/...)
  Build output: university_erp/public/portal/ (Vite manifest for cache busting)

TIER 2 — Frappe Desk (traditional server-rendered)
  Used by: 5–10 system administrators only
  Served by: Nginx → Gunicorn (full page renders)
  Backend contact: Full Frappe page rendering + API calls
```

### 2.2 Build Pipeline

portal-vue is a standalone Vite project that compiles to Frappe's public directory:

```bash
# Build sequence (runs during deployment)
cd frappe-bench/apps/university_erp/portal-vue
npm install --production=false
npm run build
# Output: ../university_erp/public/portal/
#         ../university_erp/public/portal/.vite/manifest.json  (cache-bust hashes)

# Then standard Frappe deployment
cd frappe-bench
bench migrate
bench build --app university_erp   # copies public/ to sites/assets/
bench restart
```

The Vite manifest enables Nginx to serve assets with long-lived `Cache-Control: max-age=31536000, immutable` headers. A new deploy invalidates only changed chunk hashes.

### 2.3 How Nginx Serves the SPA

```nginx
# Nginx configuration for portal-vue SPA
location /portal {
    # Serve the SPA entry point for all sub-routes (Vue Router history mode)
    try_files $uri $uri/ /portal/index.html;
}

location /portal/assets/ {
    # Vite-hashed assets — cache forever at browser and CDN level
    expires max;
    add_header Cache-Control "public, max-age=31536000, immutable";
    add_header Vary "Accept-Encoding";
    gzip_static on;
}

# API calls pass through to Gunicorn as normal
location /api/ {
    proxy_pass http://frappe_app;
    proxy_set_header Host $host;
    # No caching — JSON responses are dynamic
}
```

Cloudflare (or CloudFront) caches `/portal/assets/*` at edge PoPs. First visit downloads ~250 KB gzipped; every subsequent page navigation in the SPA is client-side with zero full-page reloads.

### 2.4 Impact on Server Load

This is the most significant infrastructure implication of the SPA architecture:

| Request Type | Traditional Frappe Desk | portal-vue SPA |
|-------------|------------------------|----------------|
| Page load | Gunicorn renders full HTML → ~500ms | Nginx serves cached HTML → ~5ms |
| Navigation | New full-page HTTP round trip | Client-side Vue Router → 0ms server |
| Data fetch | Gunicorn context + template render | JSON API only → ~50–150ms |
| Static assets | Gunicorn served or Nginx cached | Nginx/CDN only, never hits Gunicorn |
| Gunicorn RPS at 1,500 concurrent | ~200–400 RPS | ~80–180 RPS |
| Gunicorn workers required (peak) | 28–32 | 16–20 |

**Conclusion:** The SPA architecture reduces Gunicorn worker requirements by ~35–40%. App servers can be sized one tier smaller, directly reducing cloud cost.

### 2.5 CDN Strategy for SPA Assets

```
Cloudflare Cache Rules (Free/Pro plan):
  /portal/assets/*   → Cache Everything, Edge TTL: 1 year
                        (Vite hash in filename = natural cache busting on deploy)
  /portal/index.html → Cache TTL: 5 minutes (triggers SPA re-bootstrap after deploy)
  /api/*             → Bypass cache (always origin)
  /files/*           → Cache: 1 hour (Frappe file attachments)

On deploy:
  bench restart automatically invalidates index.html at CDN
  Asset files with new hashes are fetched on next user visit
  Old hash URLs remain cached — no broken references during rolling deploys
```

### 2.6 S3 / Object Storage for File Uploads

The SPA uploads student documents (certificates, photos, assignments) via the Frappe file API directly to object storage:

```
Upload flow:
  Student browser → POST /api/method/upload_file
    → Gunicorn (validates auth, file type)
    → Streams to E2E EOS / AWS S3
    → Returns file URL

Download flow:
  Student browser → GET /files/private/{token}/{filename}
    → Nginx checks Frappe token (lightweight)
    → Streams from object storage
    → OR: pre-signed URL redirect (bypasses app server entirely)
```

Pre-signed URL redirects are preferred for large files — they bypass Gunicorn entirely, reducing app server load during submission periods.

---

## 3. Load Profile & Sizing Rationale

### 3.1 Concurrent User Model (SPA-Adjusted)

With portal-vue SPA, the server-side load profile changes materially. Static asset requests (HTML, JS, CSS) are absorbed by Nginx and CDN. Only API calls reach Gunicorn.

```
SPA API call pattern per active user:
  Dashboard page load:   3–5 API calls (parallel, sub-100ms each)
  Attendance view:       1–2 API calls
  Timetable view:        1 API call (cached in Vue store for session)
  Exam result:           1 API call
  Fee payment initiation: 2–3 API calls

Average API calls per user per minute (normal browsing): 2–4
Average API calls per user per minute (peak — exam results): 6–10

Peak RPS estimate (SPA model):
  1,500 users × 6 API calls/min ÷ 60 = 150 API RPS peak

Required Gunicorn capacity:
  150 RPS × 0.15s avg JSON response time = 22.5 simultaneous threads
  22.5 threads ÷ 4 threads/worker = 6 workers minimum at peak
  Safety margin 2.5× = 16 workers (vs 30 workers needed for Desk-for-all)
  Production config: 16–20 workers across 2 app servers (8–10 per server)

MariaDB connections:
  20 workers × 2 connections = 40 DB connections
  Background workers = 20 connections
  Total: ~60–80 max_connections required
```

### 3.2 Memory Sizing (SPA-Adjusted)

```
Frappe worker memory (gunicorn): ~250 MB per worker
  20 workers × 250 MB = 5 GB (vs 8 GB for 30 workers)

MariaDB innodb_buffer_pool: 70–80% of DB size in RAM
  Year 1 (10 GB DB) → 8 GB buffer pool
  Year 5 (50 GB DB) → 16–32 GB (separate DB server from Year 3)

Redis cache: 4–6 GB (more beneficial in SPA — API response caching)
Redis session store: 1–2 GB (JWT/session tokens for 27K users)
Redis queue: 1 GB

Node.js (socketio for real-time notifications): 512 MB

System + OS overhead: 2 GB

Year 1 application server RAM need: 5+4+1+0.5+2 = ~13 GB per node
  → 16 GB RAM app server is sufficient (vs 32 GB needed for Desk-for-all)
  → 32 GB app server gives comfortable headroom and supports Redis co-location

Year 5 RAM need: ~28–32 GB app server (DB separated from Year 3)
```

### 3.3 Peak Traffic Scenarios (SPA Model)

| Scenario | Concurrent Users | API RPS (Gunicorn) | Static RPS (Nginx/CDN) | Duration |
|----------|-----------------|-------------------|----------------------|----------|
| Normal weekday | 500–800 | 20–50 | 500–2,000 (cached) | 9 AM–6 PM |
| Morning attendance | 800–1,200 | 50–100 | cached | 8:30–10:00 AM |
| Exam result release | 1,500–2,500 | 80–180 | CDN absorbs | 2–4 hours |
| Fee deadline | 1,000–1,500 | 60–120 | CDN absorbs | 2 days |
| Admission season | 800–1,500 | 50–120 | CDN absorbs | 6–8 weeks |

The "static RPS" column (HTML/JS/CSS) never reaches Gunicorn. Cloudflare serves the SPA bundle from its edge cache. This is why the Gunicorn RPS figures are dramatically lower than a traditional Frappe Desk deployment serving the same user count.

### 3.4 Redis Caching Strategy for SPA

The SPA's API-only pattern makes Redis caching highly effective:

```python
# Frappe API response caching (configured in hooks.py)
# Cacheable endpoints (same data for all users in same role):
#   /api/method/university_erp.api.get_timetable      → TTL 1 hour
#   /api/method/university_erp.api.get_academic_calendar → TTL 24 hours
#   /api/method/university_erp.api.get_notice_board    → TTL 15 minutes

# Non-cacheable (user-specific):
#   /api/method/university_erp.api.get_student_dashboard
#   /api/method/university_erp.api.get_fee_status
#   /api/resource/Student/{id}
```

With timetable and calendar responses cached in Redis, repeated API calls during peak attendance time (8:30–10 AM) hit Redis rather than MariaDB. This further reduces DB load during the most critical daily window.

---

## 4. Section A: On-Premise Deployment

### A.1 Architecture Overview

```
ON-PREMISE ARCHITECTURE — G.S. MOZE Educational Trust
═══════════════════════════════════════════════════════

  Internet
  ─────────────────────────────────────────────────────
  Cloudflare (Free/Pro) — DNS, CDN for SPA assets, DDoS, SSL
    portal-vue assets cached at Cloudflare edge globally
    API calls bypass cache, forwarded to origin
  ─────────────────────────────────────────────────────
          |
  ┌───────────────────────────────────────────────────────┐
  │  MOZE Data Centre / Server Room  (College Campus)     │
  │                                                       │
  │  ┌─────────────────┐    ┌─────────────────────────┐   │
  │  │   UTM Firewall   │    │   UPS (Online, 20 KVA)  │   │
  │  │   (FortiGate 80F)│    │   + Generator Backup    │   │
  │  └────────┬────────┘    └─────────────────────────┘   │
  │           │                                            │
  │   ┌───────┴──────────────────────────────────────┐    │
  │   │       Managed Switch (24-port Gigabit)        │    │
  │   └──┬────────────────────────────────────┬───────┘    │
  │      │                                    │             │
  │  ┌───┴────────────────┐   ┌───────────────┴──────┐     │
  │  │  APP SERVER (Prim) │   │  DB SERVER (Primary) │     │
  │  │  Dell PowerEdge    │   │  Dell PowerEdge      │     │
  │  │  R650 or equiv.    │   │  R750 or equiv.      │     │
  │  │                    │   │                      │     │
  │  │  2× Intel Xeon     │   │  2× Intel Xeon       │     │
  │  │  Silver 4314       │   │  Gold 5318Y          │     │
  │  │  (16C/32T, 2.4GHz) │   │  (24C/48T, 2.1GHz)  │     │
  │  │  64 GB DDR4 ECC    │   │  256 GB DDR4 ECC     │     │
  │  │  (SPA: 16GB enough │   │  4× 1.92 TB SSD      │     │
  │  │   but 64 for head- │   │  (RAID-10 Data)      │     │
  │  │   room + growth)   │   │                      │     │
  │  │  2× 960 GB SSD     │   │  Software:           │     │
  │  │  (RAID-1 OS+bench) │   │  Ubuntu 22.04 LTS    │     │
  │  │                    │   │  MariaDB 11.x        │     │
  │  │  Software:         │   │  (innodb_buffer=     │     │
  │  │  Ubuntu 22.04 LTS  │   │   200 GB)            │     │
  │  │  Nginx             │   │  Percona XtraBackup  │     │
  │  │  Frappe/Bench      │   │                      │     │
  │  │  Gunicorn (20 w)   │   │                      │     │
  │  │  Redis Cache (6GB) │   │                      │     │
  │  │  Redis Queue (1GB) │   │                      │     │
  │  │  Node.js SocketIO  │   │                      │     │
  │  │  portal-vue assets │   │                      │     │
  │  │  (served by Nginx) │   │                      │     │
  │  └────────────────────┘   └──────────────────────┘     │
  │                                                         │
  │  ┌────────────────────┐   ┌──────────────────────┐     │
  │  │  APP STANDBY       │   │  DB STANDBY / REPLICA│     │
  │  │  (Hot Standby)     │   │  (MariaDB Replication│     │
  │  │  Same specs        │   │   Semisync + Failover│     │
  │  │  Rsync hourly      │   │  Read replica + DR   │     │
  │  └────────────────────┘   └──────────────────────┘     │
  │                                                         │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  NAS / Backup Server                            │   │
  │  │  Synology RS2423+ — 8× 8 TB RAID-6 = 40 TB     │   │
  │  │  Daily Frappe backup, 90-day retention          │   │
  │  └─────────────────────────────────────────────────┘   │
  └───────────────────────────────────────────────────────┘

  NOTE ON SPA ASSETS (portal-vue):
  ┌─────────────────────────────────────────────────────────┐
  │  portal-vue builds to: sites/assets/university_erp/     │
  │  Nginx serves /portal/* directly from disk              │
  │  Cloudflare caches /portal/assets/* at edge             │
  │  On-premise Nginx never sees repeat static asset hits   │
  │  from returning users — Cloudflare absorbs them         │
  └─────────────────────────────────────────────────────────┘
```

### A.2 Server Hardware Specifications

#### Primary Application Server (SPA-Optimized Sizing)

| Component | Specification | Rationale |
|-----------|--------------|-----------|
| Model | Dell PowerEdge R650 (or HPE DL360 Gen10 Plus) | 1U, suitable for SPA-reduced load |
| CPU | 2× Intel Xeon Silver 4314 (16C/32T each, 2.4 GHz) | SPA needs fewer Gunicorn workers; 32 physical cores ample for 20 workers + OS |
| RAM | 64 GB DDR4-3200 ECC (4× 16 GB DIMMs) | Gunicorn 20 workers (5 GB) + Redis 8 GB + Node.js (0.5 GB) + OS (2 GB) + headroom |
| Storage (OS) | 2× 480 GB SATA SSD in RAID-1 | OS + Frappe bench + logs |
| Storage (Data) | 2× 1.92 TB NVMe SSD in RAID-1 | Frappe sites directory, portal-vue built assets |
| NIC | 2× 10 GbE (bonded/LACP) | High-speed LAN |
| iDRAC | iDRAC9 Enterprise | Remote management |
| PSU | 2× 800W redundant | Reliability |
| Warranty | 5-year ProSupport (NBD on-site) | Production SLA |

> **SPA sizing note:** A traditional Frappe Desk deployment serving 25,000 users would require the larger R750 with 128 GB RAM and 30 Gunicorn workers. Because portal-vue handles all student/staff UI client-side, the R650 with 64 GB RAM and 20 workers is sufficient with headroom for Year 1–3.

#### Primary Database Server

| Component | Specification | Rationale |
|-----------|--------------|-----------|
| Model | Dell PowerEdge R750 | DB is memory-bound regardless of frontend architecture |
| CPU | 2× Intel Xeon Gold 5318Y (24C/48T, 2.1 GHz) | DB CPU bound on complex report queries |
| RAM | 256 GB DDR4-3200 ECC | innodb_buffer_pool = 180–200 GB (Year 5: 50 GB DB) |
| Storage (OS) | 2× 480 GB SSD RAID-1 | OS + MariaDB binaries |
| Storage (Data) | 4× 1.92 TB NVMe SSD RAID-10 | MariaDB data files, 3.8 TB usable |
| NIC | 2× 25 GbE | DB traffic, replication |
| Warranty | 5-year ProSupport (NBD on-site) | Production SLA |

#### Standby Servers, NAS, Networking, Power

Unchanged from database-tier requirements — see original specifications. App standby mirrors the R650 primary (not R750). Database standby mirrors the R750.

| Item | Specification |
|------|--------------|
| NAS | Synology RS2423+ — 8× 8 TB IronWolf RAID-6 → 40 TB usable |
| Core Switch | Cisco SG350-28MP 28-port PoE+ Managed |
| UTM Firewall | Fortinet FortiGate 80F |
| ISP-1 | 100 Mbps symmetric leased line |
| ISP-2 | 50 Mbps broadband (failover) |
| UPS | APC Smart-UPS SRT 20 KVA (online double-conversion) |
| Generator | 15 KVA diesel (auto-start) |
| Precision AC | 2× Stulz CWC 2000 (N+1) |

### A.3 Software Stack

| Layer | Software | Version | Notes |
|-------|---------|---------|-------|
| OS | Ubuntu Server 22.04.4 LTS | 22.04 | LTS until 2027 |
| Database | MariaDB | 11.4 LTS | Frappe-native |
| Cache/Queue | Redis | 7.x | Cache + queue + session store |
| Web Server | Nginx | 1.24+ | Static files, SPA entry, reverse proxy |
| WSGI | Gunicorn (gthread) | 21+ | 20 workers × 4 threads (SPA-sized) |
| WebSocket | Node.js 18 LTS | 18.x | SocketIO for real-time notifications |
| SPA Frontend | portal-vue (Vue 3 + Vite) | latest | Built to public/portal/, served by Nginx |
| Framework | Frappe | v16 | Open source |
| ERP | ERPNext | v16 | Open source |
| HR | Frappe HRMS | v16 | Open source |
| Academic | Frappe Education | v16 | Open source |
| Custom | university_erp | 1.x | Includes portal-vue SPA |
| Error Tracking | Sentry (self-hosted or cloud) | latest | Vue SPA frontend errors + backend |
| Backup | Percona XtraBackup | 8.x | Hot MariaDB backup |
| Monitoring | Netdata + Grafana + Prometheus | latest | Server + API metrics |
| Log Mgmt | Loki + Grafana | latest | Centralized logs |
| VPN | WireGuard | latest | Admin remote access |

### A.4 Gunicorn Configuration (SPA-Adjusted)

```
gunicorn \
  --workers=20 \
  --threads=4 \
  --worker-class=gthread \
  --timeout=120 \
  --keepalive=10 \
  --max-requests=1000 \
  --max-requests-jitter=50 \
  --bind=0.0.0.0:8000

# SPA justification: 20 workers (vs 30 for Desk-for-all) because:
#   - No HTML page rendering for portal users (pure JSON responses)
#   - Average API response time: ~100–150ms (vs ~300–500ms for Desk page renders)
#   - At 150 peak API RPS × 0.15s = 22.5 concurrent threads → 6 workers needed
#   - 20 workers at 4 threads = 80 concurrent threads → 3.5× safety margin
#   - Memory saving: 10 fewer workers × 250 MB = 2.5 GB freed for Redis
```

### A.5 MariaDB Configuration (Production Tuning)

```ini
[mysqld]
innodb_buffer_pool_size       = 180G
innodb_buffer_pool_instances  = 16
innodb_log_file_size          = 4G
innodb_log_buffer_size        = 256M
innodb_flush_log_at_trx_commit = 1
innodb_flush_method           = O_DIRECT
max_connections               = 300
# SPA reduces concurrent DB connections: 20 workers × 2 = 40 + 20 workers = 60 total
thread_cache_size             = 64
table_open_cache              = 4096
table_definition_cache        = 2048
query_cache_type              = 0
log_bin                       = /var/lib/mysql/binlog
binlog_format                 = ROW
expire_logs_days              = 7
sync_binlog                   = 1
character-set-server          = utf8mb4
collation-server              = utf8mb4_unicode_ci
slow_query_log                = 1
long_query_time               = 1
slow_query_log_file           = /var/log/mysql/slow.log
```

### A.6 Security Hardening

#### Firewall Rules

| Direction | Port | Protocol | Source | Action |
|-----------|------|----------|--------|--------|
| Inbound | 443 | TCP | 0.0.0.0/0 | Allow (HTTPS) |
| Inbound | 80 | TCP | 0.0.0.0/0 | Allow (redirect to 443) |
| Inbound | 22 | TCP | Admin IPs only | Allow (SSH) |
| Inbound | 51820 | UDP | Admin IPs | Allow (WireGuard VPN) |
| DB Server | 3306 | TCP | App server LAN IP only | Allow |
| All other | * | * | * | Deny |

#### SSL / TLS

- Cloudflare Full Strict mode (external SSL termination)
- Let's Encrypt Origin Certificate on Nginx (auto-renew)
- TLS 1.2 minimum, TLS 1.3 preferred
- HSTS: `max-age=31536000; includeSubDomains`
- SPA assets served with `Content-Security-Policy` header restricting script sources

### A.7 Monitoring — On-Premise

| Component | Tool | What to Monitor |
|-----------|------|----------------|
| Server metrics | Netdata | CPU, RAM, disk I/O, network |
| Application errors | Sentry (self-hosted) | Vue SPA JS errors, Python exceptions |
| API response times | Netdata + Frappe logs | Portal endpoints p50/p95/p99 |
| DB slow queries | MariaDB slow query log → Grafana | Queries >1s |
| Uptime | UptimeRobot (free) | External check every 5 min |
| CDN hit rate | Cloudflare Analytics | Portal asset cache hit ratio |
| Background jobs | Frappe Scheduler | Queue depth, failed jobs |

---

## 5. Section B: Cloud Deployment

### B.1 AWS Architecture

#### Architecture Philosophy

AWS Mumbai (ap-south-1) with the SPA architecture: CloudFront caches the portal-vue bundle at India edge PoPs (Mumbai, Chennai, Hyderabad, Delhi). First-visit users get ~250 KB JS from the nearest CloudFront PoP in milliseconds. API calls route through ALB to smaller EC2 instances — because Gunicorn only handles JSON, not HTML renders, the r6i.2xlarge used previously can be replaced by c6i.2xlarge (compute-optimized, half the cost).

```
AWS ARCHITECTURE — G.S. MOZE Educational Trust (SPA-Optimized)
ap-south-1 (Mumbai) | Multi-AZ Production
═══════════════════════════════════════════════════════════════════

  USERS (27,000 registered, 1,500–2,500 peak concurrent)
  ┌──────────────────────────────────────────────────────────┐
  │  Students/Staff → portal-vue SPA (99.9% of users)       │
  │  System Admins → Frappe Desk (5–10 users only)          │
  └──────────────────────────┬───────────────────────────────┘
                             │ HTTPS
                             ▼
  ┌──────────────────────────────────────────────────────────┐
  │  CLOUDFLARE (DNS + DDoS + WAF) — Free/Pro               │
  │  Rate limiting, bot protection, SSL offload             │
  └──────────────────────────┬───────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────┐
  │  AWS CLOUDFRONT (CDN)                                   │
  │  • /portal/assets/* → Cache: 1 year, immutable          │
  │    (Vite hash filenames = safe aggressive caching)       │
  │  • /portal/index.html → Cache: 5 minutes                │
  │  • /api/* /files/* → No cache, origin ALB               │
  │  • India PoPs: Mumbai, Chennai, Hyderabad, Delhi         │
  │  • Portal JS bundle ~250 KB gzip — one CDN fetch/user   │
  └──────────────────────────┬───────────────────────────────┘
                             │ (API calls only reach here)
  ┌──────────────────────────▼───────────────────────────────┐
  │  AWS VPC: 10.0.0.0/16 (ap-south-1)                     │
  │                                                         │
  │  PUBLIC SUBNET                                          │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  Application Load Balancer (ALB)                │   │
  │  │  • HTTPS termination (ACM cert)                 │   │
  │  │  • Health check: /api/method/ping               │   │
  │  │  • Multi-AZ (ap-south-1a, 1b)                  │   │
  │  └──────────────────┬──────────────────────────────┘   │
  │                     │                                   │
  │  PRIVATE SUBNET — App Tier                              │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  Auto Scaling Group: Frappe App Servers          │   │
  │  │  ┌─────────────────┐  ┌─────────────────┐       │   │
  │  │  │ EC2: c6i.2xlarge│  │ EC2: c6i.2xlarge│       │   │
  │  │  │ (8vCPU / 16 GB) │  │ (8vCPU / 16 GB) │  ... │   │
  │  │  │ Ubuntu 22.04    │  │ Ubuntu 22.04    │       │   │
  │  │  │ Frappe v16      │  │ Frappe v16      │       │   │
  │  │  │ Gunicorn 10w    │  │ Gunicorn 10w    │       │   │
  │  │  │ Nginx (SPA+API) │  │ Nginx (SPA+API) │       │   │
  │  │  │ Redis Cache 4GB │  │ Redis Cache 4GB │       │   │
  │  │  └─────────────────┘  └─────────────────┘       │   │
  │  │  Min: 2 nodes | Normal: 2 | Peak scale: 4       │   │
  │  │                                                 │   │
  │  │  NOTE: c6i.2xlarge chosen over r6i.2xlarge      │   │
  │  │  SPA = JSON only. 16 GB RAM sufficient for      │   │
  │  │  10 Gunicorn workers (2.5 GB) + Redis (4 GB)    │   │
  │  │  + Nginx + OS. Saves ~40% on compute cost.      │   │
  │  │                                                 │   │
  │  │  ┌──────────────────────────────────────────┐   │   │
  │  │  │  Background Worker: c6i.xlarge            │   │   │
  │  │  │  (4vCPU / 8 GB) — Queue, Scheduler       │   │   │
  │  │  │  Report generation, bulk operations      │   │   │
  │  │  └──────────────────────────────────────────┘   │   │
  │  └─────────────────────────────────────────────────┘   │
  │                     │                                   │
  │  PRIVATE SUBNET — Data Tier                             │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  Amazon RDS MariaDB 11.4                        │   │
  │  │  db.r6g.large (2 vCPU, 16 GB) Multi-AZ         │   │
  │  │  200 GB gp3 SSD | 35-day backup retention       │   │
  │  │  Read Replica: db.r6g.large (reports)           │   │
  │  │  SPA note: fewer concurrent DB connections       │   │
  │  │  (60–80 vs 120+ for Desk-for-all)               │   │
  │  │                                                 │   │
  │  │  Amazon ElastiCache Redis 7.x                   │   │
  │  │  cache.r6g.large (2 vCPU, 13 GB) Multi-AZ      │   │
  │  │  API response caching + session store            │   │
  │  │  (More Redis beneficial in SPA — cache JSON     │   │
  │  │   responses shared across all portal users)     │   │
  │  └─────────────────────────────────────────────────┘   │
  │                                                         │
  │  STORAGE TIER                                           │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  Amazon S3 (ap-south-1):                        │   │
  │  │  moze-erp-files — student docs, photos, assigns │   │
  │  │  Intelligent Tiering + Glacier lifecycle         │   │
  │  │  Pre-signed URLs for student downloads          │   │
  │  │  (bypasses Gunicorn for large file downloads)   │   │
  │  │                                                 │   │
  │  │  S3 DR copy → ap-southeast-1 (Singapore)        │   │
  │  └─────────────────────────────────────────────────┘   │
  │                                                         │
  │  MONITORING & OBSERVABILITY                             │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  CloudWatch: EC2, RDS, ElastiCache, ALB metrics │   │
  │  │  Sentry: Vue SPA JS errors + Python exceptions  │   │
  │  │  CloudFront analytics: CDN hit rate monitoring  │   │
  │  │  Custom CloudWatch metrics: portal API p95/p99  │   │
  │  └─────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────┘

  DISASTER RECOVERY (ap-southeast-1, Singapore):
  RTO: 4 hours | RPO: 1 hour
  S3 cross-region replication + RDS backup copy
```

#### EC2 Instance Selection (SPA-Optimized)

**Application Servers — c6i.2xlarge (Compute-Optimized, not Memory-Optimized)**

| Attribute | Value |
|-----------|-------|
| Instance type | c6i.2xlarge |
| vCPU | 8 |
| RAM | 16 GB |
| Purpose | Gunicorn (10 workers × 250 MB = 2.5 GB) + Redis Cache (4 GB) + Nginx + OS |
| Pricing (1-yr Reserved, no upfront) | ~$0.183/hr (~₹15/hr) |
| Pricing (3-yr Reserved, partial upfront) | ~$0.130/hr (~₹11/hr) |

> **Why c6i over r6i (SPA justification):** The original design used r6i.2xlarge (64 GB, $0.302/hr) because Frappe Desk HTML renders are memory-intensive and required 16+ Gunicorn workers per node. With portal-vue SPA, each app node runs only 10 Gunicorn workers serving JSON. 16 GB RAM is sufficient (2.5 GB workers + 4 GB Redis + 2 GB overhead + 4 GB headroom). Switching from r6i.2xlarge to c6i.2xlarge saves **~₹12,000/month per node** on 1-yr Reserved pricing.

**Background Worker Server — c6i.xlarge (downsized)**

| Attribute | Value |
|-----------|-------|
| Instance type | c6i.xlarge |
| vCPU | 4 |
| RAM | 8 GB |
| Purpose | Queue workers, scheduler, background reports |
| Pricing (1-yr Reserved) | ~$0.091/hr (~₹7.6/hr) |

**RDS — db.r6g.large (downsized from xlarge)**

| Parameter | Value |
|-----------|-------|
| Engine | MariaDB 11.4 |
| Instance class | db.r6g.large (2 vCPU, 16 GB RAM) |
| Multi-AZ | Yes |
| Storage | 200 GB gp3 SSD |
| Rationale | SPA = 60–80 concurrent DB connections (vs 120+ for Desk). db.r6g.large handles this easily. Upgrade to xlarge at Year 3 when DB grows to 25 GB and report query load increases. |

**Auto-Scaling Policy (SPA-Tuned)**

```
Normal: 2 × c6i.2xlarge app servers
         1 × c6i.xlarge worker server (always on)

Scale-Out Trigger (API-focused, not page-render focused):
  • ALB RequestCountPerTarget > 250 req/min sustained 3 min → add 1 instance
  • Average CPU > 70% for 5 minutes → add 1 instance
  • Scale-out cooldown: 5 minutes

Scale-In Trigger:
  • ALB RequestCountPerTarget < 100 req/min for 15 minutes → remove 1
  • Average CPU < 35% for 10 minutes → remove 1
  • Minimum: 2 instances always

Peak Pre-warming (calendar-based — same as before):
  Exam results day: scale to 4 at 8 AM
  Fee deadline: scale to 3 two days before
  Admission results: manual scale to 4
```

#### CloudWatch Monitoring & Alarms (SPA-Specific Additions)

| Alarm | Threshold | Action |
|-------|-----------|--------|
| EC2 CPU > 75% for 5 min | High | SNS → Email + SMS |
| RDS CPU > 70% for 10 min | High | SNS → Alert |
| ALB 5XX error rate > 0.5% | High | SNS → Alert (lower threshold — SPA errors are user-visible immediately) |
| ALB Latency p99 > 2s (API) | High | SNS → Alert |
| CloudFront cache hit rate < 80% | Warning | SNS → Review CDN config |
| ElastiCache Evictions > 500/min | Warning | SNS → Alert |
| Sentry error rate spike (Vue) | High | SNS → Dev team Slack |
| Billing > ₹55,000/month | Alert | SNS → Email CFO |

---

### B.2 E2E Networks Architecture (Recommended)

#### Why E2E Networks for MOZE (with SPA)?

The SPA architecture makes E2E Networks even more attractive than before. Without the SPA:
- E2E's lack of auto-scaling was a moderate risk because Gunicorn under full HTML rendering load could saturate quickly.
- With SPA: peak Gunicorn API RPS is ~150–180, easily handled by 2 app servers with 10 workers each. The headroom before saturation is significantly larger, giving more time for manual pre-provisioning before peaks.

| Factor | E2E Networks | AWS |
|--------|-------------|-----|
| Pricing | 50–60% cheaper | Full commercial pricing |
| Billing | INR, no forex risk | USD (₹84 assumption) |
| GST | 18% (ITC reclaimable) | 18% GST on AWS India |
| Compliance | MEITY empaneled, ISO 27001 | SOC2, ISO 27001 |
| SLA | 99.95% | 99.99% (Multi-AZ RDS) |
| SPA peak risk | LOW — SPA reduces peak API RPS dramatically | LOW — auto-scales |
| Support | IST business hours | 24×7 (paid plans) |

#### E2E Networks Architecture Diagram (SPA-Optimized)

```
E2E NETWORKS ARCHITECTURE — G.S. MOZE (SPA-Optimized)
Mumbai Data Centre
═══════════════════════════════════════════════════════════════════

  USERS (27,000 registered)
  ┌──────────────────────────────────────────────────────────┐
  │  Students/Staff → portal-vue SPA                        │
  │  Admins → Frappe Desk (5–10 users, negligible load)     │
  └──────────────────────────┬───────────────────────────────┘
                             │ HTTPS
                             ▼
  ┌──────────────────────────────────────────────────────────┐
  │  CLOUDFLARE Pro — DNS + DDoS + CDN + WAF                │
  │                                                         │
  │  Cache rules:                                           │
  │    /portal/assets/*  → Edge cache 1 year (immutable)    │
  │    /portal/index.html → Edge cache 5 min                │
  │    /api/*            → Bypass (origin always)           │
  │                                                         │
  │  At peak exam result: ~1,500 users hit Cloudflare       │
  │  Cloudflare serves JS/CSS from edge to all users        │
  │  Only JSON API calls (~150 RPS) reach E2E origin        │
  └──────────────────────────┬───────────────────────────────┘
                             │ (API + uncached requests)
  ┌──────────────────────────▼───────────────────────────────┐
  │  E2E NETWORKS — Mumbai DC                               │
  │                                                         │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  LOAD BALANCER (E2E Managed LB)                  │   │
  │  │  L7 HTTPS | sticky sessions | health checks      │   │
  │  │  SSL termination (Let's Encrypt)                │   │
  │  └──────────────────┬──────────────────────────────┘   │
  │                     │                                   │
  │  ┌──────────────────▼──────────────────────────────┐   │
  │  │  APPLICATION SERVERS (SPA-Optimized)             │   │
  │  │                                                 │   │
  │  │  ┌─────────────────┐  ┌─────────────────┐       │   │
  │  │  │  App Server 1   │  │  App Server 2   │       │   │
  │  │  │  8 vCPU/32 GB   │  │  8 vCPU/32 GB   │       │   │
  │  │  │  100 GB SSD     │  │  100 GB SSD     │       │   │
  │  │  │                 │  │                 │       │   │
  │  │  │  Ubuntu 22.04   │  │  Ubuntu 22.04   │       │   │
  │  │  │  Frappe v16     │  │  Frappe v16     │       │   │
  │  │  │  Gunicorn 10w   │  │  Gunicorn 10w   │       │   │
  │  │  │  Nginx          │  │  Nginx          │       │   │
  │  │  │  Redis Cache 6GB│  │  Redis Cache 6GB│       │   │
  │  │  │  portal-vue     │  │  portal-vue     │       │   │
  │  │  │  assets on disk │  │  assets on disk │       │   │
  │  │  └─────────────────┘  └─────────────────┘       │   │
  │  │                                                 │   │
  │  │  SPA note: 32 GB RAM is ample for 10 Gunicorn   │   │
  │  │  workers (2.5 GB) + Redis (6 GB) + OS (2 GB)    │   │
  │  │  + 20 GB headroom for Year 1→3 growth           │   │
  │  │                                                 │   │
  │  │  ┌─────────────────────────────────────────┐    │   │
  │  │  │  Worker Server: 4 vCPU, 16 GB RAM        │    │   │
  │  │  │  Queue workers, Scheduler, Reports       │    │   │
  │  │  │  Sentry DSN relay (self-hosted optional) │    │   │
  │  │  └─────────────────────────────────────────┘    │   │
  │  └─────────────────────────────────────────────────┘   │
  │                                                         │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  DATABASE TIER                                   │   │
  │  │  E2E Managed MariaDB DBaaS                       │   │
  │  │  8 vCPU, 32 GB RAM, 300 GB SSD                  │   │
  │  │  Daily backup (7-day retention)                  │   │
  │  │  Private network access only                    │   │
  │  │                                                 │   │
  │  │  SPA note: DB connection count is lower (60–80  │   │
  │  │  vs 120+ for Desk). 32 GB RAM handles innodb    │   │
  │  │  buffer pool for Year 1–4 comfortably.          │   │
  │  └─────────────────────────────────────────────────┘   │
  │                                                         │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  STORAGE TIER                                   │   │
  │  │  E2E Object Storage (EOS — S3 Compatible)       │   │
  │  │  Student documents, photos, assignments         │   │
  │  │  Frappe file attachments                        │   │
  │  │  Frappe bench backups (30-day retention)        │   │
  │  │                                                 │   │
  │  │  Block Storage: 100 GB SSD per app server       │   │
  │  │  (sites directory + portal-vue built assets)    │   │
  │  └─────────────────────────────────────────────────┘   │
  │                                                         │
  │  ┌─────────────────────────────────────────────────┐   │
  │  │  MONITORING & OBSERVABILITY                      │   │
  │  │  • Netdata: server CPU/RAM/disk/network          │   │
  │  │  • UptimeRobot: external uptime (5-min checks)  │   │
  │  │  • Grafana + Prometheus: API response times      │   │
  │  │  • Sentry (cloud): Vue SPA JS errors            │   │
  │  │  • Cloudflare Analytics: CDN hit rate           │   │
  │  │  • Frappe bench logs → Loki → Grafana           │   │
  │  └─────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────┘

  DISASTER RECOVERY:
  RTO: 8–12 hours | RPO: 24 hours
  Daily EOS backups + weekly full backup to Delhi NCR DC
```

#### E2E vs AWS: SPA-Impact Comparison

| Feature | E2E Networks (SPA) | AWS (SPA) |
|---------|-------------------|-----------|
| App server type | C4.8xlarge (8 vCPU/32 GB) | c6i.2xlarge (8 vCPU/16 GB) |
| Gunicorn workers per node | 10 | 10 |
| Peak Gunicorn headroom | 2 nodes × 10w × 4t = 80 threads vs ~150 RPS needed | Same + auto-scale |
| Database | Managed MariaDB 8 vCPU/32 GB | RDS db.r6g.large 2 vCPU/16 GB |
| Redis | Self-managed 6 GB (on app servers) | ElastiCache cache.r6g.large (13 GB) |
| CDN for SPA assets | Cloudflare Pro (₹1,680/mo) | CloudFront (~₹2,000/mo) |
| SPA peak crash risk | LOW — 150 API RPS is well within 2-server capacity | Very Low — auto-scales |
| Auto-scaling | Manual pre-provision (predictable peaks) | Automatic (ASG) |
| Monthly infra cost (Y1) | ~₹38,000–44,000 (incl. GST) | ~₹85,000–95,000 (incl. GST) |

---

## 6. Section C: Cost Breakdown — Detailed INR

### Pricing Basis (March 2026)

- USD/INR: 1 USD = ₹84
- AWS Reserved Instances: 1-Year No-Upfront for Year 1–2, 3-Year Partial Upfront from Year 3
- E2E Networks: Published INR pricing, March 2026
- GST: 18% applied to all cloud services
- On-premise: Mumbai/Pune market pricing, March 2026
- SPA impact: app server instance type downsized (AWS: r6i → c6i; on-prem: R750 → R650 for app servers)

### C.1 On-Premise: Year-by-Year Cost Breakdown

#### One-Time Capital Expenditure (Year 0 — SPA-Adjusted Hardware)

| Item | Qty | Unit Cost (₹) | Total (₹) |
|------|-----|--------------|----------|
| **Compute Hardware** | | | |
| Dell PowerEdge R650 (App Server Primary — SPA-sized) | 1 | ₹8,00,000 | ₹8,00,000 |
| Dell PowerEdge R750 (DB Server Primary) | 1 | ₹15,00,000 | ₹15,00,000 |
| Dell PowerEdge R650 (App Standby) | 1 | ₹8,00,000 | ₹8,00,000 |
| Dell PowerEdge R750 (DB Standby/Replica) | 1 | ₹15,00,000 | ₹15,00,000 |
| **Storage** | | | |
| Synology RS2423+ NAS (rackmount) | 1 | ₹1,50,000 | ₹1,50,000 |
| Seagate IronWolf 8 TB NAS HDD | 8 | ₹18,000 | ₹1,44,000 |
| Additional NVMe SSD 1.92 TB (spare) | 4 | ₹22,000 | ₹88,000 |
| **Networking** | | | |
| Cisco SG350-28MP Managed Switch | 1 | ₹55,000 | ₹55,000 |
| Fortinet FortiGate 80F UTM Firewall | 1 | ₹85,000 | ₹85,000 |
| Cat6 cabling, patch panels, rack | 1 lot | ₹40,000 | ₹40,000 |
| 42U Server Rack | 1 | ₹60,000 | ₹60,000 |
| **Power & Cooling** | | | |
| APC Smart-UPS SRT 20 KVA | 1 | ₹4,50,000 | ₹4,50,000 |
| APC Rack PDUs (metered) | 4 | ₹12,000 | ₹48,000 |
| 15 KVA Diesel Generator (auto-start) | 1 | ₹2,50,000 | ₹2,50,000 |
| Stulz Precision AC 3.5 KW | 2 | ₹1,20,000 | ₹2,40,000 |
| **Miscellaneous** | | | |
| Server room civil work (raised floor, fire suppression) | 1 | ₹5,00,000 | ₹5,00,000 |
| Installation & commissioning | 1 | ₹1,50,000 | ₹1,50,000 |
| Cables, KVM, misc consumables | 1 | ₹30,000 | ₹30,000 |
| **Total Hardware CapEx** | | | **₹67,40,000** |

> **SPA savings on hardware:** Switching from two R750 app servers to two R650 app servers (SPA load profile) saves ₹8 Lakh CapEx (₹4 Lakh × 2 nodes) compared to the Desk-for-all R750 sizing. Database servers remain R750 (DB sizing is independent of frontend architecture).

#### Annual Operating Expenditure (On-Premise)

| Item | Y1 | Y2 | Y3 | Y4 | Y5 |
|------|----|----|----|----|-----|
| **Internet** | | | | | |
| 100 Mbps Leased Line | ₹2,40,000 | ₹2,40,000 | ₹2,64,000 | ₹2,64,000 | ₹2,88,000 |
| 50 Mbps Backup ISP | ₹60,000 | ₹60,000 | ₹66,000 | ₹66,000 | ₹72,000 |
| **Software & Subscriptions** | | | | | |
| Cloudflare Pro ($20/mo) | ₹17,500 | ₹17,500 | ₹17,500 | ₹21,000 | ₹21,000 |
| Sentry error tracking (Team plan ~$26/mo) | ₹26,200 | ₹26,200 | ₹26,200 | ₹26,200 | ₹26,200 |
| Domain (.edu.in) | ₹1,000 | ₹1,000 | ₹1,000 | ₹1,000 | ₹1,000 |
| FortiGate UTM subscription renewal | ₹30,000 | ₹30,000 | ₹30,000 | ₹30,000 | ₹30,000 |
| **Power & Maintenance** | | | | | |
| Electricity (13 KW avg × 24×365 × ₹8/unit) | ₹9,10,560 | ₹9,10,560 | ₹9,56,088 | ₹9,56,088 | ₹10,01,616 |
| Diesel for generator (testing) | ₹24,000 | ₹24,000 | ₹24,000 | ₹24,000 | ₹24,000 |
| UPS battery replacement (every 4 years) | ₹0 | ₹0 | ₹0 | ₹1,20,000 | ₹0 |
| AC maintenance (annual AMC) | ₹24,000 | ₹24,000 | ₹24,000 | ₹24,000 | ₹24,000 |
| **Hardware Maintenance** | | | | | |
| Dell ProSupport 5-year (amortized) | ₹4,00,000 | ₹4,00,000 | ₹4,00,000 | ₹4,00,000 | ₹4,00,000 |
| Spare parts fund | ₹30,000 | ₹30,000 | ₹50,000 | ₹50,000 | ₹50,000 |
| **Staffing** | | | | | |
| Linux/Network Admin (0.5 FTE) | ₹3,00,000 | ₹3,15,000 | ₹3,30,750 | ₹3,47,288 | ₹3,64,652 |
| DBA support (0.25 FTE or retainer) | ₹1,50,000 | ₹1,57,500 | ₹1,65,375 | ₹1,73,644 | ₹1,82,326 |
| **ERP Vendor AMC** | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 |
| **Total Annual OpEx** | **₹25,13,260** | **₹25,35,760** | **₹26,54,913** | **₹27,02,220** | **₹26,84,794** |

> Electricity reduced from original (15 KW → 13 KW) because two R650 app servers draw ~300W each vs ~450W for R750, saving ~300W × 2 = 600W across the pair. Sentry added as new line item for Vue SPA error monitoring.

#### On-Premise Years 6–10 (Hardware Refresh)

At Year 5–6, primary servers need refresh. Assuming 25% cost reduction due to hardware advancement:

| Item | Y6 | Y7 | Y8 | Y9 | Y10 |
|------|----|----|----|----|-----|
| Hardware Refresh CapEx | ₹30,00,000 | ₹0 | ₹0 | ₹0 | ₹0 |
| Annual OpEx (5% growth) | ₹28,19,034 | ₹29,59,986 | ₹31,07,985 | ₹32,63,384 | ₹34,26,554 |
| **Total** | **₹58,19,034** | **₹29,59,986** | **₹31,07,985** | **₹32,63,384** | **₹34,26,554** |

#### On-Premise Total Cost Summary

| Period | CapEx | OpEx | Total |
|--------|-------|------|-------|
| Year 0 (Hardware) | ₹67,40,000 | — | ₹67,40,000 |
| Year 1 | — | ₹25,13,260 | ₹25,13,260 |
| Year 2 | — | ₹25,35,760 | ₹25,35,760 |
| Year 3 | — | ₹26,54,913 | ₹26,54,913 |
| Year 4 | — | ₹27,02,220 | ₹27,02,220 |
| Year 5 | — | ₹26,84,794 | ₹26,84,794 |
| **5-Year Total** | **₹67,40,000** | **₹1,30,90,947** | **₹1,98,30,947** |
| Year 6 (Refresh) | ₹30,00,000 | ₹28,19,034 | ₹58,19,034 |
| Year 7 | — | ₹29,59,986 | ₹29,59,986 |
| Year 8 | — | ₹31,07,985 | ₹31,07,985 |
| Year 9 | — | ₹32,63,384 | ₹32,63,384 |
| Year 10 | — | ₹34,26,554 | ₹34,26,554 |
| **10-Year Total** | **₹97,40,000** | **₹2,86,67,890** | **₹3,84,07,890** |

---

### C.2 AWS (ap-south-1): Detailed Year-by-Year Costs

#### AWS Year 1 Monthly Cost Breakdown (SPA-Optimized)

| Service | Specification | Monthly (₹ incl. GST) |
|---------|--------------|----------------------|
| **Compute** | | |
| EC2 c6i.2xlarge × 2 (app servers, 1-yr RI) | 8vCPU/16GB, $0.183/hr × 2 × 730 = $267/mo | ₹26,470 |
| EC2 c6i.xlarge × 1 (worker, 1-yr RI) | 4vCPU/8GB, $0.091/hr × 730 = $66/mo | ₹6,548 |
| EC2 t3.micro × 1 (bastion) | 1vCPU/1GB, $0.0104/hr × 730 = $7.6/mo | ₹754 |
| **Database** | | |
| RDS MariaDB db.r6g.large Multi-AZ (1-yr RI) | 2vCPU/16GB, $0.175/hr × 730 = $128/mo | ₹12,691 |
| RDS Storage gp3 200 GB | $0.138/GB × 200 = $27.6/mo | ₹2,318 |
| RDS Read Replica db.r6g.medium | 1vCPU/8GB, $0.071/hr × 730 = $52/mo | ₹5,154 |
| **Cache** | | |
| ElastiCache Redis cache.r6g.large (1-yr RI) | 2vCPU/13GB, Multi-AZ, $0.114/hr × 730 = $83/mo | ₹8,232 |
| **Storage** | | |
| EBS gp3 100 GB × 3 instances | $0.096/GB × 300 = $28.8/mo | ₹2,854 |
| S3 Standard (Year 1: 50 GB) | $0.023/GB × 50 = $1.15/mo | ₹114 |
| S3 Cross-region replication (Singapore) | ~$5/mo | ₹496 |
| S3 PUT/GET requests | ~500K ops/mo | ₹297 |
| **Networking** | | |
| Application Load Balancer | ~$30/mo | ₹2,973 |
| CloudFront CDN (SPA assets + API) | 500 GB/mo India, $0.0085/GB + requests | ₹1,027 |
| Data Transfer Out (EC2, reduced — SPA shifts load to CloudFront) | 50 GB/mo | ₹413 |
| NAT Gateway | ~$6/mo | ₹595 |
| **Backup & DR** | | |
| RDS automated snapshots (35-day) | Included in RDS | ₹0 |
| RDS snapshot export + Glacier | ~$2.3/mo | ₹228 |
| EC2 AMIs (weekly) | ~$3/mo | ₹297 |
| **Monitoring & Observability** | | |
| CloudWatch metrics + alarms + logs | ~$10/mo | ₹1,180 |
| Sentry Team plan ($26/mo) | Vue SPA + Python errors | ₹2,575 |
| CloudFront cache analytics | Included in CloudFront | ₹0 |
| **Security** | | |
| AWS WAF on ALB | 1 WebACL + 10 rules = $15/mo | ₹1,485 |
| ACM SSL (with ALB) | Free | ₹0 |
| **Domain & DNS** | | |
| Route 53 + domain (.edu.in) | ~$1/mo | ₹99 |
| Cloudflare Pro (optional, ₹1,680 excl. GST) | Replaces part of CloudFront WAF | ₹1,982 |
| **ERP Vendor AMC** | ₹25,000/mo | ₹25,000 |
| **Total Monthly (AWS, Year 1 incl. GST)** | | **₹95,776** |

> **SPA compute savings vs original design:** Original used 2× r6i.2xlarge ($0.302/hr each = $441/mo total). SPA design uses 2× c6i.2xlarge ($0.183/hr each = $267/mo total). Monthly saving: ~₹14,600 on compute alone. RDS also downsized from xlarge to large, saving ~₹8,700/mo. Total monthly infrastructure saving from SPA architecture: **~₹23,000/month (~₹2.76 Lakh/year)**.

#### AWS Annual Cost Progression (5 Years — SPA-Optimized)

Growth: students 25K→37K, DB storage 200→600 GB, app servers 2→2→3→3→3, RDS upgrade to xlarge at Y3.

| Cost Category | Y1 (₹) | Y2 (₹) | Y3 (₹) | Y4 (₹) | Y5 (₹) |
|--------------|---------|---------|---------|---------|---------|
| **Compute (incl. GST)** | | | | | |
| App Servers (c6i.2xl × 2→2→3→3→3) | ₹3,71,718 | ₹3,71,718 | ₹5,57,577 | ₹5,57,577 | ₹5,57,577 |
| Worker Server (c6i.xlarge) | ₹92,856 | ₹92,856 | ₹92,856 | ₹92,856 | ₹92,856 |
| Bastion | ₹10,656 | ₹10,656 | ₹10,656 | ₹10,656 | ₹10,656 |
| **Database (incl. GST)** | | | | | |
| RDS (large Y1-Y2, upgrade to xlarge Y3+) | ₹1,78,000 | ₹1,78,000 | ₹2,97,000 | ₹2,97,000 | ₹2,97,000 |
| RDS Storage (200→250→350→450→600 GB) | ₹32,789 | ₹40,987 | ₹57,382 | ₹73,776 | ₹98,369 |
| RDS Read Replica | ₹72,756 | ₹72,756 | ₹91,498 | ₹91,498 | ₹91,498 |
| **Cache (incl. GST)** | | | | | |
| ElastiCache Redis Multi-AZ | ₹98,596 | ₹98,596 | ₹98,596 | ₹98,596 | ₹98,596 |
| **Storage (incl. GST)** | | | | | |
| EBS volumes | ₹34,203 | ₹34,203 | ₹40,392 | ₹40,392 | ₹40,392 |
| S3 storage + replication | ₹11,326 | ₹15,099 | ₹18,872 | ₹22,645 | ₹26,418 |
| S3 requests | ₹4,246 | ₹4,954 | ₹5,663 | ₹6,372 | ₹7,080 |
| **Networking (incl. GST)** | | | | | |
| ALB | ₹35,618 | ₹37,399 | ₹39,268 | ₹41,231 | ₹43,293 |
| CloudFront (SPA assets cached aggressively) | ₹14,604 | ₹15,312 | ₹16,020 | ₹16,728 | ₹17,436 |
| Data Transfer Out (reduced — CDN handles SPA) | ₹5,904 | ₹6,844 | ₹7,550 | ₹8,260 | ₹9,204 |
| NAT Gateway | ₹7,126 | ₹7,481 | ₹7,856 | ₹8,248 | ₹8,660 |
| **Backup & DR (incl. GST)** | | | | | |
| EC2 AMIs + Snapshots | ₹3,540 | ₹3,540 | ₹4,248 | ₹4,248 | ₹5,664 |
| RDS export + Glacier | ₹3,210 | ₹4,012 | ₹5,618 | ₹7,224 | ₹8,028 |
| **Monitoring & Observability (incl. GST)** | | | | | |
| CloudWatch | ₹14,160 | ₹14,160 | ₹15,516 | ₹15,516 | ₹15,516 |
| Sentry Team plan (Vue SPA + API errors) | ₹30,900 | ₹30,900 | ₹30,900 | ₹30,900 | ₹30,900 |
| **Security (incl. GST)** | | | | | |
| AWS WAF | ₹21,240 | ₹21,240 | ₹21,240 | ₹21,240 | ₹21,240 |
| **Domain & SSL** | ₹1,500 | ₹1,500 | ₹1,500 | ₹1,500 | ₹1,500 |
| **ERP Vendor AMC** | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 |
| **Total Annual Cost (AWS, SPA)** | **₹19,24,748** | **₹19,52,213** | **₹22,20,208** | **₹22,46,463** | **₹22,81,882** |

#### AWS Years 6–10 (SPA, continued growth)

Students 40K→52K, DB grows to 1.2 TB, 4 app servers from Y7.

| Cost Category | Y6 (₹) | Y7 (₹) | Y8 (₹) | Y9 (₹) | Y10 (₹) |
|--------------|---------|---------|---------|---------|---------|
| Compute (4 app servers from Y7) | ₹9,12,433 | ₹11,56,151 | ₹11,56,151 | ₹11,56,151 | ₹12,68,965 |
| Database (RDS xlarge, larger storage) | ₹4,18,432 | ₹4,59,225 | ₹4,96,624 | ₹5,34,022 | ₹5,93,220 |
| Cache | ₹1,18,315 | ₹1,18,315 | ₹1,18,315 | ₹1,18,315 | ₹1,18,315 |
| Storage (S3, EBS, growing) | ₹84,744 | ₹96,070 | ₹1,07,396 | ₹1,18,722 | ₹1,30,048 |
| Networking (CDN savings persist) | ₹75,604 | ₹82,308 | ₹87,896 | ₹93,484 | ₹99,072 |
| Backup & DR | ₹17,025 | ₹18,912 | ₹21,240 | ₹23,568 | ₹26,544 |
| Monitoring (CloudWatch + Sentry) | ₹55,428 | ₹55,428 | ₹55,428 | ₹55,428 | ₹55,428 |
| Security (WAF) | ₹25,488 | ₹25,488 | ₹25,488 | ₹25,488 | ₹25,488 |
| Domain | ₹1,500 | ₹1,500 | ₹1,500 | ₹1,500 | ₹1,500 |
| ERP Vendor AMC | ₹3,00,000 | ₹3,00,000 | ₹3,50,000 | ₹3,50,000 | ₹3,50,000 |
| **Annual Total** | **₹24,08,969** | **₹25,13,397** | **₹27,20,038** | **₹27,76,678** | **₹29,68,580** |

#### AWS 5-Year and 10-Year Summary (SPA-Optimized)

| Year | Annual Cost (₹) | Cumulative (₹) |
|------|-----------------|----------------|
| Y1 | ₹19,24,748 | ₹19,24,748 |
| Y2 | ₹19,52,213 | ₹38,76,961 |
| Y3 | ₹22,20,208 | ₹60,97,169 |
| Y4 | ₹22,46,463 | ₹83,43,632 |
| Y5 | ₹22,81,882 | ₹1,06,25,514 |
| **5-Year Total** | | **₹1,06,25,514** |
| Y6 | ₹24,08,969 | ₹1,30,34,483 |
| Y7 | ₹25,13,397 | ₹1,55,47,880 |
| Y8 | ₹27,20,038 | ₹1,82,67,918 |
| Y9 | ₹27,76,678 | ₹2,10,44,596 |
| Y10 | ₹29,68,580 | ₹2,40,13,176 |
| **10-Year Total** | | **₹2,40,13,176** |

---

### C.3 E2E Networks: Detailed Year-by-Year Costs

#### E2E Networks Year 1 Monthly Cost Breakdown

All prices from E2E Networks published pricing (INR, March 2026, excl. GST unless noted)

| Service | Specification | Monthly (₹ excl. GST) | Monthly (₹ incl. 18% GST) |
|---------|--------------|----------------------|--------------------------|
| **Compute** | | | |
| App Server 1: E2E C4.8xlarge | 8 vCPU, 32 GB RAM, 100 GB SSD | ₹7,200 | ₹8,496 |
| App Server 2: E2E C4.8xlarge | 8 vCPU, 32 GB RAM, 100 GB SSD | ₹7,200 | ₹8,496 |
| Worker Server: E2E C4.4xlarge | 4 vCPU, 16 GB RAM, 50 GB SSD | ₹3,600 | ₹4,248 |
| **Database** | | | |
| E2E Managed MariaDB (DBaaS) | 8 vCPU, 32 GB RAM, 300 GB SSD | ₹12,000 | ₹14,160 |
| **Load Balancer** | | | |
| E2E Managed Load Balancer | 1 LB, 1 TB traffic included | ₹1,500 | ₹1,770 |
| **Storage** | | | |
| Block Storage (additional 200 GB per app server) | 400 GB total | ₹2,000 | ₹2,360 |
| E2E Object Storage (EOS) — 100 GB | Files, documents, SPA build cache | ₹1,000 | ₹1,180 |
| **Network** | | | |
| Static Public IPs (3 servers + LB) | 4 IPs | ₹400 | ₹472 |
| Inbound Bandwidth | Included (5 TB/month) | ₹0 | ₹0 |
| Outbound Bandwidth | Included (500 GB) + ~50 GB excess | ₹40 | ₹47 |
| **Monitoring** | | | |
| Netdata Cloud (free tier, up to 5 nodes) | Server metrics | ₹0 | ₹0 |
| UptimeRobot (free tier, 5-min checks) | External uptime | ₹0 | ₹0 |
| Sentry Team plan ($26/mo = ₹2,184) | Vue SPA JS errors + Python | ₹2,184 | ₹2,577 |
| **CDN & Security** | | | |
| Cloudflare Pro ($20/mo = ₹1,680) | DNS, SPA CDN, DDoS, WAF | ₹1,680 | ₹1,982 |
| **Domain** | .edu.in (annual ₹1,000 ÷ 12) | ₹83 | ₹98 |
| **Backup** | EOS backup (50 GB/month, 30-day) | ₹500 | ₹590 |
| **ERP Vendor AMC** | ₹25,000/month (same across all options) | ₹25,000 | ₹25,000 |
| **Monthly Total (E2E, Year 1)** | | **₹62,387** | **₹71,476** |

#### Infrastructure-Only (Excl. ERP AMC)

| Monthly Infra Cost (excl. AMC) | ₹37,387 excl. GST | ₹46,476 incl. GST |
|--------------------------------|-------------------|-------------------|

#### E2E Annual Cost Progression (5 Years — SPA)

| Cost Category | Y1 (₹) | Y2 (₹) | Y3 (₹) | Y4 (₹) | Y5 (₹) |
|--------------|---------|---------|---------|---------|---------|
| **Compute (incl. 18% GST)** | | | | | |
| App Servers (2×8vCPU/32GB) | ₹2,03,904 | ₹2,03,904 | ₹2,40,864 | ₹2,40,864 | ₹2,40,864 |
| Worker Server (4vCPU/16GB) | ₹50,976 | ₹50,976 | ₹60,264 | ₹60,264 | ₹60,264 |
| **Database (incl. GST)** | | | | | |
| Managed MariaDB (8vCPU/32GB) | ₹1,69,920 | ₹1,69,920 | ₹1,91,160 | ₹1,91,160 | ₹2,12,400 |
| DB storage growth | ₹0 | ₹0 | ₹14,160 | ₹14,160 | ₹28,320 |
| **Load Balancer (incl. GST)** | ₹21,240 | ₹21,240 | ₹21,240 | ₹21,240 | ₹21,240 |
| **Storage (incl. GST)** | | | | | |
| Block Storage | ₹28,320 | ₹28,320 | ₹33,040 | ₹33,040 | ₹37,760 |
| EOS object storage (growing) | ₹14,160 | ₹16,520 | ₹18,880 | ₹21,240 | ₹23,600 |
| **Network (incl. GST)** | | | | | |
| Static IPs | ₹5,664 | ₹5,664 | ₹5,664 | ₹5,664 | ₹5,664 |
| Excess bandwidth (reduced — CDN absorbs SPA) | ₹564 | ₹564 | ₹705 | ₹846 | ₹987 |
| **Monitoring (incl. GST)** | | | | | |
| Sentry Team plan | ₹30,924 | ₹30,924 | ₹30,924 | ₹30,924 | ₹30,924 |
| **CDN — Cloudflare Pro (incl. GST)** | ₹23,784 | ₹23,784 | ₹23,784 | ₹23,784 | ₹23,784 |
| **Domain (incl. GST)** | ₹1,176 | ₹1,176 | ₹1,176 | ₹1,176 | ₹1,176 |
| **Backup (EOS)** | ₹7,080 | ₹8,260 | ₹9,440 | ₹10,620 | ₹11,800 |
| **ERP Vendor AMC** | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 | ₹3,00,000 |
| **Annual Total (E2E, SPA)** | **₹8,57,712** | **₹8,61,252** | **₹9,51,301** | **₹9,54,982** | **₹9,98,783** |

#### E2E Networks Years 6–10

Year 5→6: Add 3rd app server (students approach 40,000). Upgrade DB node to 64 GB RAM.

| Cost Category | Y6 (₹) | Y7 (₹) | Y8 (₹) | Y9 (₹) | Y10 (₹) |
|--------------|---------|---------|---------|---------|---------|
| App Servers (3 from Y6) | ₹3,61,296 | ₹3,61,296 | ₹3,61,296 | ₹3,61,296 | ₹3,61,296 |
| Worker Server | ₹60,264 | ₹60,264 | ₹60,264 | ₹60,264 | ₹60,264 |
| Managed MariaDB (upgrade to 64 GB) | ₹3,54,000 | ₹3,54,000 | ₹3,54,000 | ₹3,54,000 | ₹3,54,000 |
| Storage (growing) | ₹72,480 | ₹84,960 | ₹97,440 | ₹1,09,920 | ₹1,22,400 |
| LB + Network + CDN + Domain | ₹51,246 | ₹51,246 | ₹51,246 | ₹51,246 | ₹51,246 |
| Monitoring (Sentry) | ₹30,924 | ₹30,924 | ₹30,924 | ₹30,924 | ₹30,924 |
| Backup | ₹14,160 | ₹16,520 | ₹18,880 | ₹21,240 | ₹23,600 |
| ERP Vendor AMC | ₹3,50,000 | ₹3,50,000 | ₹3,50,000 | ₹3,50,000 | ₹3,50,000 |
| **Annual Total** | **₹12,94,370** | **₹13,09,210** | **₹13,24,050** | **₹13,38,890** | **₹13,53,730** |

#### E2E Networks 5-Year and 10-Year Summary

| Year | Annual Cost (₹) | Cumulative (₹) |
|------|-----------------|----------------|
| Y1 | ₹8,57,712 | ₹8,57,712 |
| Y2 | ₹8,61,252 | ₹17,18,964 |
| Y3 | ₹9,51,301 | ₹26,70,265 |
| Y4 | ₹9,54,982 | ₹36,25,247 |
| Y5 | ₹9,98,783 | ₹46,24,030 |
| **5-Year Total** | | **₹46,24,030** |
| Y6 | ₹12,94,370 | ₹59,18,400 |
| Y7 | ₹13,09,210 | ₹72,27,610 |
| Y8 | ₹13,24,050 | ₹85,51,660 |
| Y9 | ₹13,38,890 | ₹98,90,550 |
| Y10 | ₹13,53,730 | ₹1,12,44,280 |
| **10-Year Total** | | **₹1,12,44,280** |

---

### C.4 Master Comparison Table

#### 5-Year Total Cost Comparison (All-In, Including ERP AMC)

| Cost Element | On-Premise | AWS Mumbai (SPA) | E2E Networks (SPA) |
|-------------|-----------|-----------------|-------------------|
| Year 0 CapEx | ₹67,40,000 | — | — |
| Year 1 | ₹25,13,260 | ₹19,24,748 | ₹8,57,712 |
| Year 2 | ₹25,35,760 | ₹19,52,213 | ₹8,61,252 |
| Year 3 | ₹26,54,913 | ₹22,20,208 | ₹9,51,301 |
| Year 4 | ₹27,02,220 | ₹22,46,463 | ₹9,54,982 |
| Year 5 | ₹26,84,794 | ₹22,81,882 | ₹9,98,783 |
| **5-Year TCO** | **₹1,98,30,947** | **₹1,06,25,514** | **₹46,24,030** |

#### 10-Year Total Cost Comparison

| Cost Element | On-Premise | AWS Mumbai (SPA) | E2E Networks (SPA) |
|-------------|-----------|-----------------|-------------------|
| 5-Year Subtotal | ₹1,98,30,947 | ₹1,06,25,514 | ₹46,24,030 |
| Y6 | ₹58,19,034 | ₹24,08,969 | ₹12,94,370 |
| Y7 | ₹29,59,986 | ₹25,13,397 | ₹13,09,210 |
| Y8 | ₹31,07,985 | ₹27,20,038 | ₹13,24,050 |
| Y9 | ₹32,63,384 | ₹27,76,678 | ₹13,38,890 |
| Y10 | ₹34,26,554 | ₹29,68,580 | ₹13,53,730 |
| **10-Year TCO** | **₹3,84,07,890** | **₹2,40,13,176** | **₹1,12,44,280** |

#### Year-by-Year Comparison

| Year | On-Premise (₹) | AWS SPA (₹) | E2E SPA (₹) | E2E Savings vs AWS |
|------|--------------|------------|------------|-------------------|
| 0 (CapEx) | ₹67,40,000 | ₹0 | ₹0 | — |
| 1 | ₹25,13,260 | ₹19,24,748 | ₹8,57,712 | ₹10,67,036 |
| 2 | ₹25,35,760 | ₹19,52,213 | ₹8,61,252 | ₹10,90,961 |
| 3 | ₹26,54,913 | ₹22,20,208 | ₹9,51,301 | ₹12,68,907 |
| 4 | ₹27,02,220 | ₹22,46,463 | ₹9,54,982 | ₹12,91,481 |
| 5 | ₹26,84,794 | ₹22,81,882 | ₹9,98,783 | ₹12,83,099 |
| 6 | ₹58,19,034 | ₹24,08,969 | ₹12,94,370 | ₹11,14,599 |
| 7 | ₹29,59,986 | ₹25,13,397 | ₹13,09,210 | ₹12,04,187 |
| 8 | ₹31,07,985 | ₹27,20,038 | ₹13,24,050 | ₹13,95,988 |
| 9 | ₹32,63,384 | ₹27,76,678 | ₹13,38,890 | ₹14,37,788 |
| 10 | ₹34,26,554 | ₹29,68,580 | ₹13,53,730 | ₹16,14,850 |

#### Feature / Capability Comparison (SPA Context)

| Feature | On-Premise | AWS (SPA) | E2E Networks (SPA) |
|---------|-----------|----------|-------------------|
| **Frontend Architecture** | | | |
| SPA served by | Nginx on-premises + Cloudflare CDN | CloudFront + Nginx (EC2) | Cloudflare CDN + Nginx (E2E) |
| API-only Gunicorn | Yes (20 workers) | Yes (10w/node × 2 nodes) | Yes (10w/node × 2 nodes) |
| Build pipeline | CI/CD on-prem or GitHub Actions | GitHub Actions + CodeDeploy | GitHub Actions + deploy script |
| **Reliability** | | | |
| Database HA | Manual failover (~30–60 min) | Multi-AZ automatic (<90 sec) | Manual (~2–4 hrs) |
| App HA | Manual standby | Auto Scaling Group | Manual (add server) |
| SPA availability | Cloudflare edge (very high) | CloudFront edge (very high) | Cloudflare edge (very high) |
| Uptime SLA | Self-managed | 99.99% (RDS Multi-AZ) | 99.95% |
| **Scalability** | | | |
| Peak capacity (SPA) | Fixed 20 workers on 2 servers | Auto-scale 2→4 nodes | Manual pre-provision |
| SPA peak headroom | 80 threads vs ~150 RPS → sufficient | Elastic | 80 threads vs ~150 RPS → sufficient |
| **Monitoring** | | | |
| Vue SPA error tracking | Sentry (self-hosted) | Sentry Team plan | Sentry Team plan |
| API response monitoring | Netdata + Grafana | CloudWatch custom metrics | Grafana + Prometheus |
| CDN hit rate | Cloudflare Analytics | CloudFront metrics | Cloudflare Analytics |
| **Cost** | | | |
| 5-Year TCO | ₹1.98 Cr | ₹1.06 Cr | ₹46.2 Lakh |
| 10-Year TCO | ₹3.84 Cr | ₹2.40 Cr | ₹1.12 Cr |
| Monthly infra (Y1, excl. AMC) | ~₹1.70 Lakh | ~₹58,000 | ~₹46,476 |
| CapEx | ₹67.4 Lakh | ₹0 | ₹0 |

---

## 7. CI/CD Build Pipeline

The portal-vue SPA introduces a frontend build step to the deployment pipeline. The full production deploy sequence is:

```yaml
# GitHub Actions workflow (deploy.yml) — simplified
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-22.04

    steps:
      # 1. Build portal-vue SPA
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: portal-vue/package-lock.json

      - name: Install frontend dependencies
        run: |
          cd frappe-bench/apps/university_erp/portal-vue
          npm ci --prefer-offline

      - name: Build portal-vue SPA
        run: |
          cd frappe-bench/apps/university_erp/portal-vue
          npm run build
          # Output: ../university_erp/public/portal/
          # Vite manifest: ../university_erp/public/portal/.vite/manifest.json
        env:
          VITE_API_BASE: https://moze.edu.in
          VITE_SENTRY_DSN: ${{ secrets.SENTRY_DSN_FRONTEND }}

      # 2. Deploy to app servers via SSH
      - name: Sync built assets to app servers
        run: |
          rsync -avz --delete \
            frappe-bench/apps/university_erp/university_erp/public/portal/ \
            deploy@app-server-1:/home/frappe/frappe-bench/apps/university_erp/university_erp/public/portal/

      # 3. Frappe backend deployment
      - name: Run bench commands on app server
        run: |
          ssh deploy@app-server-1 '
            cd /home/frappe/frappe-bench
            git -C apps/university_erp pull origin main
            bench migrate --skip-failing
            bench build --app university_erp
            bench restart
          '

      # 4. Invalidate CDN cache for index.html only
      # (Asset files have new Vite hashes — old URLs remain cached safely)
      - name: Cloudflare cache purge (index.html)
        run: |
          curl -X POST \
            "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            --data '{"files":["https://moze.edu.in/portal/index.html"]}'
        env:
          CF_ZONE_ID: ${{ secrets.CF_ZONE_ID }}
          CF_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
```

**Deploy timing breakdown:**

| Step | Duration | Notes |
|------|----------|-------|
| npm ci (cached deps) | ~45 sec | Node modules cached in GitHub Actions |
| npm run build (Vite) | ~60–90 sec | Production bundle with tree-shaking |
| rsync built assets | ~15 sec | ~1–3 MB delta on typical deploy |
| bench migrate | ~30–120 sec | Varies if schema changes present |
| bench build (assets copy) | ~30 sec | Copies public/ to Frappe assets |
| bench restart (graceful) | ~15 sec | Gunicorn graceful reload, zero downtime |
| Cloudflare purge | ~5 sec | Only index.html purged |
| **Total deploy time** | **~4–7 minutes** | Zero downtime for active SPA users |

---

## 8. Assumptions & Pricing Basis

### Student & User Growth Model

| Year | Students | Staff | Total | Concurrent Normal | Concurrent Peak |
|------|---------|-------|-------|-------------------|-----------------|
| 1 | 25,000 | 2,000 | 27,000 | 500–800 | 1,500–2,000 |
| 2 | 28,000 | 2,200 | 30,200 | 600–900 | 1,600–2,200 |
| 3 | 31,000 | 2,400 | 33,400 | 700–1,000 | 1,800–2,400 |
| 4 | 34,000 | 2,600 | 36,600 | 800–1,100 | 1,900–2,500 |
| 5 | 37,000 | 2,800 | 39,800 | 900–1,200 | 2,000–2,700 |
| 6 | 40,000 | 3,000 | 43,000 | 1,000–1,400 | 2,200–3,000 |
| 7 | 43,000 | 3,100 | 46,100 | 1,100–1,500 | 2,400–3,200 |
| 8 | 46,000 | 3,200 | 49,200 | 1,200–1,600 | 2,600–3,400 |
| 9 | 49,000 | 3,350 | 52,350 | 1,300–1,700 | 2,800–3,600 |
| 10 | 52,000 | 3,500 | 55,500 | 1,400–1,800 | 3,000–4,000 |

### SPA Load Assumptions

| Assumption | Value | Basis |
|-----------|-------|-------|
| API calls per user per minute (normal) | 2–4 | SPA client-side navigation, cached Vue store |
| API calls per user per minute (peak) | 6–10 | Exam result page burst |
| Average JSON API response time | 100–150 ms | Frappe + Redis cache hit rate ~60% |
| Gunicorn thread utilisation at peak | ~30% | 150 RPS × 0.15s = 22.5 threads / 80 available |
| Cloudflare/CDN cache hit rate (SPA assets) | >95% | Vite-hashed assets, 1-year TTL |
| Portal JS bundle size (gzipped) | ~250 KB | Vue 3 + vue-router + pinia + app code |
| Admin Desk users (Frappe Desk) | 5–10 | Negligible load; not sized for |

### Database Growth Model

| Year | DB Size (GB) | RDS/Managed DB Allocated | File Storage (S3/EOS) |
|------|-------------|------------------------|-----------------------|
| 1 | 10 | 200 GB | 50 GB |
| 2 | 15 | 250 GB | 100 GB |
| 3 | 25 | 350 GB | 150 GB |
| 4 | 35 | 450 GB | 200 GB |
| 5 | 50 | 600 GB | 250 GB |
| 6 | 65 | 700 GB | 300 GB |
| 7 | 80 | 800 GB | 350 GB |
| 8 | 95 | 900 GB | 400 GB |
| 9 | 110 | 1 TB | 450 GB |
| 10 | 120 | 1.2 TB | 500 GB |

### Pricing Sources (March 2026)

| Service | Source | Rate Used |
|---------|--------|----------|
| EC2 c6i.2xlarge (1-yr RI, no-upfront) | AWS Mumbai | $0.183/hr |
| EC2 c6i.xlarge (1-yr RI) | AWS Mumbai | $0.091/hr |
| RDS MariaDB db.r6g.large Multi-AZ (1-yr RI) | AWS Mumbai | $0.175/hr |
| RDS MariaDB db.r6g.xlarge Multi-AZ (1-yr RI) | AWS Mumbai | $0.344/hr |
| ElastiCache cache.r6g.large Multi-AZ (1-yr RI) | AWS Mumbai | $0.114/hr |
| RDS gp3 storage | AWS Mumbai | $0.138/GB/month |
| S3 Standard | AWS Mumbai | $0.023/GB/month |
| CloudFront India | AWS | $0.0085/GB |
| USD/INR | Conservative | ₹84 |
| E2E compute 8vCPU/32GB | E2E Networks published | ₹7,200/month |
| E2E Managed MariaDB 8vCPU/32GB/300GB | E2E Networks published | ₹12,000/month |
| E2E Object Storage | E2E Networks published | ₹1/GB/month |
| GST on cloud services | Indian GST law | 18% |
| Dell PowerEdge R650 (configured) | Dell India commercial | ₹8 Lakh |
| Dell PowerEdge R750 (configured) | Dell India commercial | ₹15 Lakh |
| Electricity | Maharashtra commercial tariff | ₹8/kWh |
| 100 Mbps Leased Line | TATA/Airtel Maharashtra | ₹20,000/month |
| Sentry Team plan | Sentry.io | $26/month |
| Cloudflare Pro | Cloudflare | $20/month |

---

## 9. Risk Assessment & Recommendations

### Risk Matrix

| Risk | On-Premise | AWS (SPA) | E2E Networks (SPA) |
|------|-----------|----------|--------------------|
| Hardware failure | HIGH | LOW | LOW |
| Power failure | MEDIUM (UPS + gen) | LOW | LOW |
| Network outage | MEDIUM | LOW | MEDIUM |
| Exam results peak crash | HIGH (fixed capacity) | LOW (auto-scales) | LOW-MEDIUM (SPA reduces RPS 50%) |
| Data loss | HIGH (campus only) | LOW (multi-region) | MEDIUM |
| Security breach | MEDIUM | LOW | MEDIUM |
| SPA JS error undetected | MEDIUM (no monitoring) | LOW (Sentry) | LOW (Sentry) |
| Deploy breaks SPA | MEDIUM | LOW (blue/green) | MEDIUM (test pre-prod) |
| Staff dependency | HIGH (1.5 FTE) | LOW (0.25 FTE) | MEDIUM (0.5 FTE) |
| Forex risk (USD billing) | None | MEDIUM | None (INR billing) |
| Capex risk | HIGH (₹67L upfront) | None | None |

### SPA-Specific Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Vite build breaks on deploy | Low | CI pipeline fails before deploy; old version stays live |
| Vue runtime error affects all users | Medium | Sentry real-time alerts; rollback via git revert + redeploy in ~5 min |
| CDN serves stale index.html | Low | Cloudflare purge on deploy (automated in CI/CD) |
| API CORS error after config change | Low | Frappe CORS settings tested in staging before production push |
| Large file upload saturates Gunicorn | Medium | Pre-signed URL upload to EOS/S3 (bypasses Gunicorn) |
| SocketIO real-time disconnects under load | Medium | Graceful degradation — portal works without realtime; reconnects automatically |

### Phased Recommendation for MOZE

#### Phase 1 (Year 1–3): E2E Networks — SPA Amplifies Value

**Monthly infrastructure cost: ~₹46,000–52,000 (incl. GST, excl. ERP AMC)**

- Deploy 2 app servers + 1 worker + managed MariaDB on E2E Networks Mumbai
- Build portal-vue SPA in CI/CD, deploy to Nginx on app servers
- Use Cloudflare Pro for SPA CDN (portal assets cached at edge), DDoS protection, WAF
- Self-hosted monitoring (Netdata) + Sentry Team plan for Vue SPA error tracking
- Automated daily Frappe backup to EOS with 30-day retention
- Pre-provision 3rd app server 48 hours before known peaks
- **SPA advantage:** At peak (1,500 users), Cloudflare absorbs static asset requests; Gunicorn sees only ~150 API RPS — well within 2 servers × 10 workers × 4 threads = 80 concurrent threads. Peak crash risk is dramatically lower than a Desk-for-all deployment.
- **Savings vs AWS:** ₹10–13 Lakh/year

#### Phase 2 (Year 3–5): Evaluate Migration Triggers

**Migrate to AWS if any of these conditions are met:**

| Trigger | Action |
|---------|--------|
| Sustained concurrent users > 2,500 for more than 2 weeks | AWS Auto Scaling becomes essential even with SPA |
| Gunicorn queue depth consistently > 40 threads (>50% utilisation) | Scale out needed; E2E manual pre-provision becomes risky |
| E2E uptime falls below 99.8% (>17 hrs/year downtime) | AWS Multi-AZ eliminates DB failover risk |
| MOZE requires SOC2/ISO 27001 Type II audit evidence | AWS provides compliance artifacts |
| DB exceeds 300 GB and needs seamless read replicas | AWS RDS Read Replica is seamless |

#### Phase 3 (Year 5+): AWS or E2E Scale-Up

If staying on E2E: upgrade DB to 64 GB RAM node, add 3rd app server (students at 37K+).
If migrating to AWS: 3-year Reserved Instances for c6i.2xlarge; SPA load profile means 3 nodes (not 4) handle up to 3,000 concurrent users.

### Why On-Premise is Not Recommended

1. **₹67.4 Lakh upfront CapEx** — a 2-year cloud spend at E2E, for hardware that depreciates
2. **₹9–10 Lakh/year electricity** — sole largest recurring cost, exceeds E2E's entire annual cloud bill
3. **No auto-scaling** — even with SPA reducing peak API RPS, hardware is fixed; a surprise peak (e.g., Maharashtra board result announcement same day as MOZE results) will saturate
4. **Disaster recovery is impossible** — fire, flood, or power failure at campus = total data loss
5. **Staff burden** — 1.5 FTE sysadmin/DBA, difficult to retain in Pune market
6. **5-year TCO ₹1.98 Cr** vs E2E's ₹46.2 Lakh — **4.3× more expensive**

### Final Recommendation

**Recommended: E2E Networks (Years 1–5) → evaluate AWS (Years 5+)**

| Year | Platform | Monthly Cost (Infra + GST, excl. AMC) | Reason |
|------|---------|--------------------------------------|--------|
| 1–2 | E2E Networks | ₹46,000–50,000 | Lowest cost; SPA reduces peak risk to acceptable level |
| 3–5 | E2E Networks | ₹50,000–65,000 | Adequate for 31–37K students with 3rd server pre-provision |
| 5+ | AWS Mumbai | ₹1,00,000–1,35,000 | Auto-scaling essential at 37K+ students; SPA means c6i not r6i |

**10-Year TCO (excl. ERP AMC):**
- E2E Networks (SPA): **~₹82.5 Lakh**
- AWS (SPA): **~₹2.10 Cr**
- On-Premise (SPA): **~₹3.54 Cr**

The SPA architecture (portal-vue) reduces required compute by ~35–40% across all three deployment options. On E2E Networks, the already-low cost drops further because the SPA's reduced Gunicorn load means the standard C4.8xlarge nodes carry much more headroom than they would for a Desk-for-all deployment. The combination of E2E Networks pricing and SPA architecture efficiency delivers the best value for MOZE's 10-year outlook while keeping data in Indian data centres throughout.

---

*Document Version 2.0 — March 2026*
*Revision: Incorporates portal-vue Vue 3 SPA two-tier frontend architecture*
*All prices in Indian Rupees (₹). GST at 18% applied to cloud services.*
*Prices based on published tariffs, March 2026. Subject to revision per actual vendor quotes.*
*USD/INR assumed at ₹84. AWS billing varies with forex rates.*
*On-premise power at Maharashtra commercial tariff ₹8/kWh.*
*SPA load assumptions based on portal-vue API call patterns; actual RPS will vary.*
