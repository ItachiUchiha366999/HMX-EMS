# Cloud Architecture & Hosting Plan
## Frappe/ERPNext — Student Portal + Desk UI

**Date:** March 2026
**Users:** 2,000 Students (Portal) + 100 Faculty/Management (Desk)

---

## 1. Application Architecture Overview

### Current Stack

```
┌─────────────────────────────────────────────────┐
│                  Frappe Stack                     │
│                                                   │
│  Student Portal (Vue 3 SPA)                       │
│  ├── Built with Vite → ~92KB static assets        │
│  ├── Served at /assets/university_erp/            │
│  ├── Routes via /student_portal/                  │
│  └── API: /api/method/university_erp...portal_api │
│                                                   │
│  Desk UI (Frappe built-in)                        │
│  ├── Full CRUD for faculty/management             │
│  └── Reports, bulk operations                     │
│                                                   │
│  Backend: Python/Gunicorn + Node.js WebSocket     │
│  Database: MariaDB                                │
│  Cache/Queue: Redis                               │
└─────────────────────────────────────────────────┘
```

**Key Insight:** The student portal is a lightweight Vue 3 SPA (92KB gzipped) served as static files from the Frappe application server. **No separate frontend server is needed.** The entire deployment is a single Frappe Docker stack.

### Student Portal Features (API Endpoints)

| Feature | API Method | Load Type |
|---------|-----------|-----------|
| Dashboard | `get_student_dashboard()` | Read |
| Academics | `get_student_academics()` | Read |
| Fees / Payments | `get_student_fees()`, `create_payment_request()` | Read + Write |
| Attendance | `get_student_attendance_details()` | Read |
| Library | `get_student_library()` | Read |
| Notifications | `get_student_notifications()` | Read |
| Profile | `get_student_profile()` | Read |
| Grievances | `get_student_grievances()` | Read + Write |
| Hostel | `get_student_hostel()` | Read |
| Transport | `get_student_transport()` | Read |

---

## 2. User Load Analysis

| User Type | Count | Interface | Peak Concurrency | Load Profile |
|-----------|-------|-----------|-----------------|--------------|
| Students | 2,000 | Vue SPA (read-heavy) | ~200–400 (10–20%) | View grades, attendance, timetable, fees |
| Faculty/Management | 100 | Desk UI (read+write) | ~50–80 (50–80%) | CRUD, reports, bulk operations |
| **Total** | **2,100** | | **~300–500 concurrent** | |

### Peak Load Scenarios

| Scenario | Expected Concurrent Users | Duration |
|----------|--------------------------|----------|
| Normal day | 100–200 | All day |
| Morning rush (attendance check) | 300–400 | 8:00–10:00 AM |
| Exam results release | 800–1,200 | 2–4 hours |
| Fee payment deadline | 400–600 | 1–2 days |
| Registration period | 500–800 | 1–2 weeks |

---

## 3. Recommended Cloud Architecture

### Production Architecture (Single Server)

```
                    ┌──────────────────┐
                    │    Cloudflare    │  Free Plan
                    │  CDN + DNS + WAF │  Cache static assets
                    │  DDoS Protection │  SSL termination (optional)
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │   Single VM      │
                    │  6–8 vCPU        │
                    │  16 GB RAM       │
                    │  150–200 GB SSD  │
                    │                  │
                    │ ┌──────────────┐ │
                    │ │   Traefik    │ │ SSL (Let's Encrypt)
                    │ │   Reverse    │ │ compose.traefik-ssl.yaml
                    │ │   Proxy      │ │
                    │ └──────┬───────┘ │
                    │        │         │
                    │ ┌──────┴───────┐ │
                    │ │    Nginx     │ │ Static assets (Vue SPA)
                    │ │   Frontend   │ │ Proxy to backend
                    │ │   (:8080)    │ │
                    │ └──────┬───────┘ │
                    │        │         │
                    │   ┌────┴────┐    │
                    │   │        │    │
                    │ ┌─┴──────┐ ┌┴─────────┐ │
                    │ │Gunicorn│ │ WebSocket │ │
                    │ │Backend │ │  Node.js  │ │
                    │ │(:8000) │ │  (:9000)  │ │
                    │ │8w × 4t │ │           │ │
                    │ └────────┘ └───────────┘ │
                    │                  │
                    │ ┌──────────────┐ │
                    │ │   Workers    │ │
                    │ │ queue-short  │ │ Emails, notifications
                    │ │ queue-long   │ │ Reports, bulk ops
                    │ │ scheduler    │ │ Cron jobs
                    │ └──────┬───────┘ │
                    │        │         │
                    │ ┌──────┴───────┐ │
                    │ │   MariaDB    │ │ innodb_buffer_pool=4G
                    │ │   11.x      │ │ max_connections=200
                    │ └──────────────┘ │
                    │ ┌──────────────┐ │
                    │ │    Redis     │ │ Cache: 1GB
                    │ │ Cache+Queue  │ │ Queue: 512MB
                    │ └──────────────┘ │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Object Storage  │ Daily backups
                    │  (S3 compatible) │ via compose.backup-cron.yaml
                    └──────────────────┘
```

### Docker Compose Services

| Service | Source | Role | Resources |
|---------|--------|------|-----------|
| Traefik | `compose.traefik-ssl.yaml` | Reverse proxy + SSL | Minimal |
| Frontend (Nginx) | `compose.yaml` | Static assets + proxy | Minimal |
| Backend (Gunicorn) | `compose.yaml` | API server | 8 workers × 4 threads |
| WebSocket | `compose.yaml` | Real-time notifications | Minimal |
| Queue-Short | `compose.yaml` | Quick async tasks | 1 process |
| Queue-Long | `compose.yaml` | Heavy background jobs | 1 process |
| Scheduler | `compose.yaml` | Cron jobs | 1 process |
| MariaDB 11.x | `compose.mariadb.yaml` | Database | 4 GB buffer pool |
| Redis Cache | `compose.redis.yaml` | Sessions + cache | 1 GB |
| Redis Queue | `compose.redis.yaml` | Job queue broker | 512 MB |
| Backup Cron | `compose.backup-cron.yaml` | Automated backups | Minimal |

---

## 4. Hosting Provider Comparison

### Budget Providers (India Datacenter Available)

| Provider | Plan | vCPU | RAM | Storage | Monthly (USD) | India DC | Managed DB |
|----------|------|------|-----|---------|--------------|----------|------------|
| **Contabo** | VPS S | 4 | 8 GB | 75 GB NVMe | **$4.95** | Navi Mumbai | No |
| **Contabo** | VPS M | 6 | 16 GB | 150 GB NVMe | **$8.95** | Navi Mumbai | No |
| **E2E Networks** | Cloud Server | 4 | 12 GB | 100 GB SSD | **~$36–72** (₹3K–6K) | Delhi NCR, Mumbai | PostgreSQL only |

### Mid-Range Providers

| Provider | Plan | vCPU | RAM | Storage | Monthly (USD) | India DC | Managed DB |
|----------|------|------|-----|---------|--------------|----------|------------|
| **Hetzner** | CPX31 | 4 | 8 GB | 160 GB | **~$18** | No (Singapore) | No |
| **Hetzner** | CPX41 | 8 | 16 GB | 240 GB | **~$33** | No (Singapore) | No |
| **Vultr** | Cloud Compute | 4 | 8 GB | 100 GB | **~$48** | Mumbai, Bangalore, Delhi | Yes |
| **DigitalOcean** | General Purpose | 4 | 8 GB | 25 GB | **~$63** | Bangalore | Yes ($15/mo+) |
| **Linode/Akamai** | Dedicated 8GB | 4 | 8 GB | 160 GB | **~$72** | Mumbai | Yes ($15/mo+) |

### Hyperscalers

| Provider | Plan | vCPU | RAM | Monthly (USD) | India DC | Managed DB | Startup Credits |
|----------|------|------|-----|--------------|----------|------------|----------------|
| **GCP** | e2-standard-4 | 4 | 16 GB | **~$107** (on-demand) | Mumbai, Delhi | Cloud SQL $50–80/mo | $300 trial + up to $350K |
| **GCP** | e2-standard-4 (1yr) | 4 | 16 GB | **~$62** | Same | Same | Same |
| **AWS** | t3.xlarge | 4 | 16 GB | **~$133** (Mumbai) | Mumbai | RDS MariaDB ~$80/mo | Up to $100K (Activate) |
| **Azure** | B4ms | 4 | 16 GB | **~$133** (on-demand) | Pune, Chennai, Mumbai | MariaDB native ~$50–100/mo | $200 + up to $150K |
| **Azure** | B4ms (1yr) | 4 | 16 GB | **~$82** | Same | Same | Same |

### Fully Managed

| Provider | Plan | Monthly (USD) | Notes |
|----------|------|--------------|-------|
| **Frappe Cloud** | Dedicated Server | **$200–400** | Zero DevOps, backups + updates included |

---

## 5. Provider Deep Dive

### Contabo ($8.95/mo) — Ultra Budget
- **Pros:** Cheapest option by far, India DC (Navi Mumbai), generous specs
- **Cons:** 200 Mbit/s network cap, inconsistent performance under heavy load, no managed DB, slow support, requires 12-month commitment
- **Best for:** Tight budgets with strong sysadmin skills

### E2E Networks (~₹3K–6K/mo) — Best Indian Provider
- **Pros:** Indian company, INR billing, India DCs (Delhi NCR + Mumbai), good support, no foreign exchange overhead
- **Cons:** Only managed PostgreSQL (no MariaDB), smaller ecosystem
- **Best for:** Indian institutions wanting local billing and support

### Vultr (~$48–73/mo) — Best Value with India DC
- **Pros:** 3 India DCs (Mumbai, Bangalore, Delhi), managed MySQL databases, $250 free credit for new accounts
- **Cons:** Mid-range pricing
- **Best for:** Balanced cost + convenience with managed DB

### Hetzner (~$33/mo) — Best Price/Performance
- **Pros:** Exceptional value (8vCPU/16GB for $33), reliable, great community
- **Cons:** No India DC (Singapore nearest, ~60–80ms latency), no managed DB
- **Best for:** Budget-conscious with tolerance for non-India latency

### GCP/Azure ($127–170/mo) — Enterprise with Free Credits
- **Pros:** India DCs, managed databases, auto-scaling, enterprise SLAs, massive startup credits (GCP up to $350K, Azure up to $150K)
- **Cons:** Complex pricing, expensive without credits
- **Best for:** Startups that qualify for credits — potentially **free for 1–2 years**

### Frappe Cloud ($200–400/mo) — Zero Operations
- **Pros:** Purpose-built for Frappe/ERPNext, zero DevOps, backups/updates/monitoring included
- **Cons:** Most expensive option
- **Best for:** No sysadmin on staff, just want it to work

---

## 6. Total Monthly Cost by Tier

### Tier 1: Ultra-Budget — ~$12/mo
| Item | Provider | Cost |
|------|----------|------|
| Server (6vCPU/16GB) | Contabo VPS M (Navi Mumbai) | $8.95 |
| Object Storage (backups) | Contabo | ~$3 |
| CDN + DNS + SSL | Cloudflare Free | $0 |
| **Total** | | **~$12/mo** |

### Tier 2: Best Value (India) — ~$41/mo
| Item | Provider | Cost |
|------|----------|------|
| Server (4vCPU/12GB) | E2E Networks (Mumbai) | ~$36 |
| Object Storage | E2E / S3 compatible | ~$5 |
| CDN + DNS + SSL | Cloudflare Free | $0 |
| **Total** | | **~$41/mo** |

### Tier 3: Balanced (Managed DB) — ~$73/mo
| Item | Provider | Cost |
|------|----------|------|
| Server (4vCPU/8GB) | Vultr (Mumbai) | $48 |
| Managed MySQL DB | Vultr | ~$20 |
| Object Storage | Vultr | ~$5 |
| CDN + DNS + SSL | Cloudflare Free | $0 |
| **Total** | | **~$73/mo** |

### Tier 4: Enterprise — ~$127/mo (or free with credits)
| Item | Provider | Cost |
|------|----------|------|
| VM (4vCPU/16GB, 1yr CUD) | GCP Mumbai | ~$62 |
| Cloud SQL (MariaDB) | GCP | ~$60 |
| Cloud Storage | GCP | ~$5 |
| CDN + DNS + SSL | Cloudflare Free | $0 |
| **Total** | | **~$127/mo** |

> Apply for GCP for Startups ($350K credits) or Azure Founders Hub ($150K) to get this free

### Tier 5: Fully Managed — $200–400/mo
| Item | Provider | Cost |
|------|----------|------|
| Everything | Frappe Cloud Dedicated | $200–400 |
| **Total** | | **$200–400/mo** |

---

## 7. Server Configuration Tuning

### Gunicorn (Backend)
```
--workers=8
--threads=4
--worker-class=gthread
--timeout=120
```

### MariaDB
```ini
[mysqld]
innodb_buffer_pool_size = 4G
innodb_log_file_size = 512M
max_connections = 200
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

### Redis Cache
```
maxmemory 1gb
maxmemory-policy allkeys-lru
```

### Redis Queue
```
maxmemory 512mb
```

### Nginx (Frontend)
```
client_max_body_size 50m;
proxy_read_timeout 120s;
gzip on;
gzip_types text/css application/javascript application/json;
```

---

## 8. Essential Infrastructure

### Backups
- **Frequency:** Every 6 hours via `compose.backup-cron.yaml`
- **Destination:** S3-compatible object storage (separate from server)
- **Retention:** 7 daily + 4 weekly + 3 monthly
- **Test restores:** Monthly

### Monitoring
- **Uptime:** UptimeRobot or BetterStack (free tier)
- **Server:** Netdata (self-hosted, free) or provider's built-in monitoring
- **Alerts:** Email/Slack on CPU > 80%, disk > 85%, memory > 90%

### Security
- Cloudflare WAF (free plan) for DDoS + bot protection
- SSH key-only access (disable password auth)
- Automatic security updates (`unattended-upgrades`)
- Firewall: allow only 80, 443, 22 (restricted IP)
- Regular Docker image updates

### SSL/TLS
- Let's Encrypt via Traefik (`compose.traefik-ssl.yaml`)
- Auto-renewal built into Traefik
- Cloudflare Full (Strict) SSL mode

---

## 9. Scaling Path

| Stage | Trigger | Action | Est. Cost |
|-------|---------|--------|-----------|
| **Start** | < 300 concurrent | Single server (this plan) | $12–73/mo |
| **Scale Up** | CPU > 70% sustained | Upgrade to 8vCPU/32GB | +$10–50/mo |
| **Separate DB** | DB I/O bottleneck | Move MariaDB to dedicated server/managed DB | +$20–80/mo |
| **Scale Out** | > 500 concurrent | 2 app nodes + load balancer | +$50–100/mo |
| **Full HA** | Uptime SLA required | Multi-node + DB replication + failover | +$150–300/mo |

---

## 10. Recommendation

**For an Indian educational institution with 2,000 students + 100 faculty:**

### Primary Recommendation: E2E Networks (~$41/mo)
- Indian company with INR billing (no forex overhead)
- India datacenters (Delhi NCR, Mumbai) for low latency
- Good support with local team
- Self-managed MariaDB + Redis on same server
- Add Cloudflare Free for CDN and DDoS protection

### Alternative: Vultr (~$73/mo)
- If you want managed database (less ops burden)
- 3 India datacenters for flexibility
- $250 free credit to start

### If You Qualify for Startup Credits: GCP (~$127/mo → free)
- Apply for Google for Startups (up to $350K credits)
- Enterprise infrastructure at zero cost for 1–2 years
- Managed everything (Cloud SQL, monitoring, auto-scaling)

### If No Sysadmin Available: Frappe Cloud ($200–400/mo)
- Zero operational overhead
- Purpose-built for Frappe/ERPNext
- Backups, updates, monitoring all included

---

*A single well-configured server handles 2,000 students + 100 faculty comfortably. The student portal is a lightweight 92KB Vue SPA — the real load is API calls to Frappe, which Gunicorn with 8 workers handles well for 300–500 concurrent users.*
