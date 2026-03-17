# University ERP - Cloud Infrastructure for Custom Frontend Architecture

## Overview

This document outlines the cloud infrastructure required to deploy the **University ERP system with Custom Vue/React Frontend**, based on the architecture defined in Phase 21. The system separates the frontend (Vue/React) from the Frappe backend, requiring specific infrastructure considerations.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    INTERNET                                              │
│                                                                                          │
│    ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│    │                              USERS                                                │ │
│    │                                                                                   │ │
│    │   Students (2,000)  │  Faculty (70)  │  Staff (50)  │  Parents (2,000)           │ │
│    │                                                                                   │ │
│    │   Desktop  │  Tablet  │  Mobile  │  PWA (Installed)                              │ │
│    └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                         │                                                │
│                                         ▼                                                │
│    ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│    │                          CLOUDFLARE (FREE/PRO)                                    │ │
│    │                                                                                   │ │
│    │   • CDN for static assets                                                        │ │
│    │   • DDoS protection                                                              │ │
│    │   • SSL/TLS termination                                                          │ │
│    │   • WAF (Web Application Firewall)                                               │ │
│    │   • Caching                                                                       │ │
│    └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                         │                                                │
└─────────────────────────────────────────┼────────────────────────────────────────────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          │                               │
                          ▼                               ▼
┌─────────────────────────────────────┐   ┌─────────────────────────────────────┐
│      FRONTEND HOSTING                │   │      BACKEND (E2E Networks)          │
│                                      │   │                                      │
│   Option A: Same E2E Server          │   │   Frappe/ERPNext Application         │
│   Option B: Vercel/Netlify (CDN)     │   │   REST APIs                          │
│   Option C: CloudFlare Pages         │   │   Frappe Desk (Admin)                │
│                                      │   │                                      │
│   • Vue/React Static Files           │   │   • /api/method/*                    │
│   • Service Worker (PWA)             │   │   • /app (Desk UI)                   │
│   • Manifest.json                    │   │   • /socket.io                       │
│                                      │   │                                      │
│   URL: portal.university.edu         │   │   URL: api.university.edu            │
└─────────────────────────────────────┘   └─────────────────────────────────────┘
```

---

## Complete Infrastructure Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    E2E NETWORKS CLOUD                                             │
│                                    (Delhi-NCR / Mumbai)                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                   LOAD BALANCER                                              │ │
│  │                                   (₹500/month)                                               │ │
│  │                                                                                              │ │
│  │   • HTTP/HTTPS load balancing                                                               │ │
│  │   • Health checks                                                                            │ │
│  │   • SSL termination (CloudFlare origin cert)                                                │ │
│  └─────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                            │                                                      │
│                    ┌───────────────────────┼───────────────────────┐                             │
│                    │                       │                       │                              │
│                    ▼                       ▼                       ▼                              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐       │
│  │    APPLICATION SERVER    │  │     WORKER SERVER        │  │    FRONTEND SERVER       │       │
│  │      (C2.Medium)         │  │      (C2.Small)          │  │     (Optional)           │       │
│  │   ₹1,500/month           │  │   ₹750/month             │  │   ₹500/month or CDN      │       │
│  │                          │  │                          │  │                          │       │
│  │  • 2 vCPU, 4GB RAM       │  │  • 1 vCPU, 2GB RAM       │  │  • Static file server    │       │
│  │  • Nginx                 │  │  • Background workers    │  │  • Vue/React build       │       │
│  │  • Frappe Gunicorn       │  │  • Scheduler             │  │  • PWA assets            │       │
│  │  • Redis                 │  │  • Email queue           │  │  • Nginx                 │       │
│  │  • SocketIO              │  │  • Push notifications    │  │                          │       │
│  └──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘       │
│                    │                       │                       │                              │
│                    └───────────────────────┼───────────────────────┘                             │
│                                            │                                                      │
│  ┌─────────────────────────────────────────┴───────────────────────────────────────────────────┐ │
│  │                                   DATA LAYER                                                 │ │
│  │                                                                                              │ │
│  │   ┌─────────────────────────────┐              ┌─────────────────────────────┐              │ │
│  │   │     MANAGED MYSQL           │              │       REDIS                 │              │ │
│  │   │      (DBaaS-2GB)            │              │    (On App Server)          │              │ │
│  │   │      ₹1,200/month           │              │                             │              │ │
│  │   │                             │              │   • Cache: 256MB            │              │ │
│  │   │   • 2GB RAM, 50GB SSD       │              │   • Queue: 256MB            │              │ │
│  │   │   • Daily backups           │              │   • SocketIO: 128MB         │              │ │
│  │   │   • 99.95% SLA              │              │                             │              │ │
│  │   └─────────────────────────────┘              └─────────────────────────────┘              │ │
│  │                                                                                              │ │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                                   STORAGE LAYER                                              │ │
│  │                                                                                              │ │
│  │   ┌─────────────────────────────┐              ┌─────────────────────────────┐              │ │
│  │   │     BLOCK STORAGE           │              │     OBJECT STORAGE (EOS)    │              │ │
│  │   │      100GB SSD              │              │      200GB                  │              │ │
│  │   │      ₹500/month             │              │      ₹200/month             │              │ │
│  │   │                             │              │                             │              │ │
│  │   │   • /data mount             │              │   • LMS content             │              │ │
│  │   │   • Frappe files            │              │   • Backups                 │              │ │
│  │   │   • Logs                    │              │   • Student documents       │              │ │
│  │   │                             │              │   • Report archives         │              │ │
│  │   └─────────────────────────────┘              └─────────────────────────────┘              │ │
│  │                                                                                              │ │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Hosting Options

Since you're building a custom Vue/React frontend, you have three hosting options:

### Option A: Same E2E Server (Simplest)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE SERVER SETUP                           │
│                                                                  │
│   E2E App Server (C2.Medium - 4GB)                              │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │                         NGINX                              │ │
│   │                                                            │ │
│   │   location / {                                             │ │
│   │       # Serve frontend static files                        │ │
│   │       root /var/www/university-frontend/dist;              │ │
│   │   }                                                        │ │
│   │                                                            │ │
│   │   location /api {                                          │ │
│   │       # Proxy to Frappe backend                            │ │
│   │       proxy_pass http://127.0.0.1:8000;                    │ │
│   │   }                                                        │ │
│   │                                                            │ │
│   │   location /app {                                          │ │
│   │       # Frappe Desk for admins                             │ │
│   │       proxy_pass http://127.0.0.1:8000;                    │ │
│   │   }                                                        │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│   Cost: ₹0 additional (uses same server)                        │
└─────────────────────────────────────────────────────────────────┘
```

**Nginx Configuration:**
```nginx
# /etc/nginx/sites-available/university-erp

server {
    listen 80;
    listen 443 ssl http2;
    server_name university.example.com;

    # SSL (CloudFlare Origin Certificate)
    ssl_certificate /etc/ssl/cloudflare/origin.pem;
    ssl_certificate_key /etc/ssl/cloudflare/origin.key;

    # Frontend static files (Vue/React build)
    root /var/www/university-frontend/dist;
    index index.html;

    # Static frontend pages
    location / {
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # PWA manifest and service worker
    location /manifest.json {
        add_header Cache-Control "no-cache";
    }

    location /sw.js {
        add_header Cache-Control "no-cache";
        add_header Service-Worker-Allowed "/";
    }

    # API routes - proxy to Frappe
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;

        # CORS headers for API
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Credentials true always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, X-Frappe-CSRF-Token" always;
    }

    # Frappe Desk (Admin only)
    location /app {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frappe assets
    location /assets {
        proxy_pass http://127.0.0.1:8000;
    }

    # Socket.IO for real-time updates
    location /socket.io {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Option B: CloudFlare Pages (Recommended for Frontend)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         CLOUDFLARE PAGES + E2E BACKEND                                   │
│                                                                                          │
│   ┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐   │
│   │       CLOUDFLARE PAGES              │     │        E2E NETWORKS                 │   │
│   │       (FREE)                        │     │                                     │   │
│   │                                     │     │   App Server (C2.Medium)            │   │
│   │   • Auto-deploy from GitHub         │     │   ┌─────────────────────────────┐   │   │
│   │   • Global CDN (300+ locations)     │     │   │  Frappe Backend            │   │   │
│   │   • Free SSL                        │     │   │  • /api/* endpoints        │   │   │
│   │   • Unlimited bandwidth             │     │   │  • /app (Desk)             │   │   │
│   │   • Preview deployments             │     │   │  • Socket.IO               │   │   │
│   │                                     │     │   └─────────────────────────────┘   │   │
│   │   URL: portal.university.edu        │     │   URL: api.university.edu           │   │
│   │                                     │     │                                     │   │
│   │   Contains:                         │     │   Contains:                         │   │
│   │   • Vue/React build                 │     │   • Frappe/ERPNext                  │   │
│   │   • PWA assets                      │     │   • Education module                │   │
│   │   • Service Worker                  │     │   • HRMS module                     │   │
│   │   • manifest.json                   │     │   • University ERP custom           │   │
│   └─────────────────────────────────────┘     └─────────────────────────────────────┘   │
│                                                                                          │
│   Cost: ₹0 for frontend                       Cost: ₹4,850/month for backend            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**CloudFlare Pages Configuration:**

```toml
# wrangler.toml (in frontend project root)

name = "university-erp-frontend"
compatibility_date = "2024-01-01"

[site]
bucket = "./dist"

[[redirects]]
from = "/api/*"
to = "https://api.university.edu/api/:splat"
status = 200

[[headers]]
for = "/sw.js"
[headers.values]
Cache-Control = "no-cache"
Service-Worker-Allowed = "/"

[[headers]]
for = "/*"
[headers.values]
X-Frame-Options = "SAMEORIGIN"
X-Content-Type-Options = "nosniff"
```

### Option C: Vercel/Netlify (Alternative CDN)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         VERCEL/NETLIFY + E2E BACKEND                                     │
│                                                                                          │
│   Similar to CloudFlare Pages but with:                                                  │
│   • Vercel: Best for React/Next.js                                                      │
│   • Netlify: Great for Vue/Nuxt.js                                                      │
│   • Both have generous free tiers                                                        │
│   • Both support custom domains + SSL                                                    │
│                                                                                          │
│   Vercel Config (vercel.json):                                                          │
│   {                                                                                      │
│     "rewrites": [                                                                        │
│       { "source": "/api/:path*", "destination": "https://api.university.edu/api/:path*" }
│     ]                                                                                    │
│   }                                                                                      │
│                                                                                          │
│   Netlify Config (netlify.toml):                                                        │
│   [[redirects]]                                                                          │
│     from = "/api/*"                                                                      │
│     to = "https://api.university.edu/api/:splat"                                        │
│     status = 200                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Recommended Infrastructure Configuration

### For 2,000 Students (Your Current Size)

| Component | Specification | Provider | Monthly Cost (₹) |
|-----------|---------------|----------|------------------|
| **Frontend Hosting** | CloudFlare Pages | CloudFlare | **FREE** |
| **CDN + DDoS** | CloudFlare Free/Pro | CloudFlare | FREE / ₹1,700 |
| **App Server** | C2.Medium (2 vCPU, 4GB) | E2E Networks | ₹1,500 |
| **Worker Server** | C2.Small (1 vCPU, 2GB) | E2E Networks | ₹750 |
| **Managed MySQL** | DBaaS-2GB (2GB RAM) | E2E Networks | ₹1,200 |
| **Block Storage** | 100GB SSD | E2E Networks | ₹500 |
| **Object Storage** | 200GB EOS | E2E Networks | ₹200 |
| **Static IP** | 1 IP | E2E Networks | ₹100 |
| **Load Balancer** | Basic LB | E2E Networks | ₹500 |
| **Email Service** | AWS SES (10k emails) | AWS | ₹100 |
| **SMS Gateway** | MSG91 (2k SMS) | MSG91 | ₹400 |
| **Push Notifications** | Firebase FCM | Google | **FREE** |
| | | **TOTAL** | **₹5,250/month** |

---

## Detailed Component Specifications

### 1. Application Server (E2E C2.Medium)

```yaml
Server: university-erp-app
Plan: C2.Medium
Specifications:
  vCPU: 2
  RAM: 4 GB
  Storage: 60 GB SSD (included)
  OS: Ubuntu 22.04 LTS

Services Running:
  - Nginx (reverse proxy): 128 MB
  - Frappe/Gunicorn (4 workers): 1.5 GB
  - Redis (cache + queue): 512 MB
  - Supervisor: 64 MB
  - OS overhead: 512 MB
  - Buffer: 1.3 GB

Ports:
  - 22 (SSH): Admin IP only
  - 80 (HTTP): Load Balancer
  - 443 (HTTPS): Load Balancer (if SSL termination here)
  - 8000 (Frappe): Internal only
  - 9000 (SocketIO): Internal only
```

### 2. Worker Server (E2E C2.Small)

```yaml
Server: university-erp-worker
Plan: C2.Small
Specifications:
  vCPU: 1
  RAM: 2 GB
  Storage: 40 GB SSD
  OS: Ubuntu 22.04 LTS

Services Running:
  - Frappe Worker (default): 512 MB
  - Frappe Worker (short): 256 MB
  - Frappe Scheduler: 128 MB
  - Push Notification Service: 256 MB
  - OS overhead: 512 MB
  - Buffer: 384 MB

Purpose:
  - Background job processing
  - Email sending
  - Report generation
  - Push notifications
  - Scheduled tasks (attendance alerts, fee reminders)
```

### 3. Managed MySQL Database

```yaml
Database: university-mysql
Engine: MySQL 8.0
Plan: DBaaS-2GB
Specifications:
  RAM: 2 GB
  Storage: 50 GB SSD
  Backup: Daily (7 days retention)
  High Availability: No (cost saving)

Estimated Size:
  - 2,000 students × 500KB avg = 1 GB
  - 70 faculty × 200KB = 14 MB
  - Transactions (1 year) = 5 GB
  - Reports/Logs = 2 GB
  - Total: ~10 GB (50 GB provides 5x growth)

Connection:
  - Host: <id>.mysql.database.e2enetworks.net
  - Port: 3306
  - Access: App server private IP only
```

### 4. Object Storage (EOS)

```yaml
Bucket: university-erp-files
Storage: 200 GB
Type: S3-compatible

Structure:
  university-erp-files/
  ├── sites/
  │   └── university.example.com/
  │       ├── private/files/
  │       └── public/files/
  ├── lms/
  │   ├── courses/
  │   ├── lectures/
  │   └── assignments/
  ├── documents/
  │   ├── certificates/
  │   ├── transcripts/
  │   └── id-cards/
  └── backups/
      ├── daily/
      ├── weekly/
      └── monthly/

Estimated Usage:
  - LMS content: 50 GB
  - Student documents: 25 GB
  - Backups: 30 GB
  - General files: 20 GB
  - Buffer: 75 GB
```

---

## Network Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              NETWORK TOPOLOGY                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   INTERNET                                                                               │
│       │                                                                                  │
│       ▼                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│   │                           CLOUDFLARE                                              │  │
│   │                                                                                   │  │
│   │   portal.university.edu ────────────► CloudFlare Pages (Frontend)                │  │
│   │                                                                                   │  │
│   │   api.university.edu ──────────────► E2E Load Balancer                           │  │
│   └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                              │                                           │
│                                              ▼                                           │
│   ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│   │                        E2E VPC (10.0.0.0/16)                                      │  │
│   │                                                                                   │  │
│   │   ┌─────────────────────────────────────────────────────────────────────────┐    │  │
│   │   │                    PUBLIC SUBNET (10.0.1.0/24)                           │    │  │
│   │   │                                                                          │    │  │
│   │   │   Load Balancer ──────────────► 10.0.1.10 (Public IP attached)          │    │  │
│   │   │                                                                          │    │  │
│   │   └─────────────────────────────────────────────────────────────────────────┘    │  │
│   │                                       │                                           │  │
│   │                                       ▼                                           │  │
│   │   ┌─────────────────────────────────────────────────────────────────────────┐    │  │
│   │   │                    PRIVATE SUBNET (10.0.10.0/24)                         │    │  │
│   │   │                                                                          │    │  │
│   │   │   App Server ────────────────► 10.0.10.10                               │    │  │
│   │   │   Worker Server ─────────────► 10.0.10.11                               │    │  │
│   │   │   MySQL (Managed) ───────────► 10.0.10.50 (Private endpoint)            │    │  │
│   │   │                                                                          │    │  │
│   │   └─────────────────────────────────────────────────────────────────────────┘    │  │
│   │                                                                                   │  │
│   └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Security Configuration

### Security Groups

```yaml
# Load Balancer Security Group (lb-sg)
Inbound:
  - Port 80 (HTTP): 0.0.0.0/0 (redirects to HTTPS)
  - Port 443 (HTTPS): 0.0.0.0/0

# Application Security Group (app-sg)
Inbound:
  - Port 22 (SSH): Admin VPN IP only
  - Port 8000 (Frappe): lb-sg only
  - Port 9000 (SocketIO): lb-sg only
  - Port 6379 (Redis): worker-sg only

# Worker Security Group (worker-sg)
Inbound:
  - Port 22 (SSH): Admin VPN IP only

# Database Security Group (db-sg)
Inbound:
  - Port 3306 (MySQL): app-sg, worker-sg only
```

### CORS Configuration for Custom Frontend

```python
# site_config.json
{
    "allow_cors": [
        "https://portal.university.edu",
        "https://university.example.com"
    ],
    "allow_websocket_origin": "portal.university.edu"
}
```

```python
# hooks.py - Add CORS headers
def after_request(response):
    origin = frappe.request.headers.get("Origin")
    allowed_origins = ["https://portal.university.edu"]

    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Frappe-CSRF-Token"

    return response
```

---

## Push Notification Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          PUSH NOTIFICATION FLOW                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────┐ │
│   │   Custom Frontend   │          │   Frappe Backend    │          │  Firebase FCM   │ │
│   │   (Vue/React PWA)   │          │   (E2E Server)      │          │  (Google)       │ │
│   └─────────┬───────────┘          └─────────┬───────────┘          └────────┬────────┘ │
│             │                                │                                │          │
│             │  1. User grants permission     │                                │          │
│             │  2. Get FCM token              │                                │          │
│             │  ◄─────────────────────────────┼────────────────────────────────┤          │
│             │                                │                                │          │
│             │  3. Send token to backend      │                                │          │
│             │  POST /api/method/register_device                               │          │
│             ├───────────────────────────────►│                                │          │
│             │                                │                                │          │
│             │                                │  4. Store token in             │          │
│             │                                │     User Device Token DocType  │          │
│             │                                │                                │          │
│             │                                │                                │          │
│             │                                │  5. Event triggers notification│          │
│             │                                │     (fee due, exam result)     │          │
│             │                                │                                │          │
│             │                                │  6. Send to FCM                │          │
│             │                                ├───────────────────────────────►│          │
│             │                                │                                │          │
│             │                                │                                │  7. Push │
│             │  8. Display notification       │                                │◄────────┤ │
│             │◄───────────────────────────────┼────────────────────────────────┤          │
│             │                                │                                │          │
└─────────────┴────────────────────────────────┴────────────────────────────────┴──────────┘
```

**Firebase Configuration:**
```javascript
// firebase-config.js (in frontend)
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "university-erp.firebaseapp.com",
  projectId: "university-erp",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};

// VAPID key for web push
const vapidKey = "YOUR_VAPID_PUBLIC_KEY";
```

---

## Backup Strategy

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              BACKUP STRATEGY                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   TYPE              FREQUENCY        RETENTION       STORAGE                            │
│   ─────────────────────────────────────────────────────────────────                     │
│   Database          Every 6 hours    24 backups      E2E EOS + Local                    │
│   Database          Daily (2 AM)     7 days          E2E EOS                            │
│   Database          Weekly (Sun)     4 weeks         E2E EOS                            │
│   Database          Monthly (1st)    12 months       E2E EOS (Glacier)                  │
│                                                                                          │
│   Files             Real-time        Versioned       E2E EOS (versioning)               │
│   Files             Daily            7 days          E2E EOS                            │
│                                                                                          │
│   Frontend Build    On deploy        5 versions      CloudFlare Pages / Git            │
│                                                                                          │
│   Server Config     Daily            30 days         E2E EOS                            │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Backup Script:**
```bash
#!/bin/bash
# /opt/scripts/full_backup.sh

SITE="university.example.com"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/data/backups"
EOS_BUCKET="university-erp-files"

# Database backup
cd /home/frappe/frappe-bench
sudo -u frappe bench --site $SITE backup --with-files

# Upload to EOS
s3cmd put $BACKUP_DIR/*$DATE* s3://$EOS_BUCKET/backups/daily/

# Frontend backup (if hosted locally)
tar -czf $BACKUP_DIR/frontend_$DATE.tar.gz /var/www/university-frontend/
s3cmd put $BACKUP_DIR/frontend_$DATE.tar.gz s3://$EOS_BUCKET/backups/frontend/

# Cleanup old backups
find $BACKUP_DIR -type f -mtime +7 -delete

# Notify healthcheck
curl -fsS -m 10 --retry 5 https://hc-ping.com/YOUR-UUID
```

---

## Monitoring & Alerting

### Monitoring Stack

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              MONITORING ARCHITECTURE                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                           FREE MONITORING TOOLS                                  │   │
│   │                                                                                  │   │
│   │   UptimeRobot (Free)                 Healthchecks.io (Free)                     │   │
│   │   ┌───────────────────┐              ┌───────────────────┐                      │   │
│   │   │ • HTTP monitoring │              │ • Cron monitoring │                      │   │
│   │   │ • 5 min intervals │              │ • Backup alerts   │                      │   │
│   │   │ • 50 monitors     │              │ • Custom scripts  │                      │   │
│   │   │ • Email alerts    │              │ • Email + Slack   │                      │   │
│   │   └───────────────────┘              └───────────────────┘                      │   │
│   │                                                                                  │   │
│   │   E2E Built-in Monitoring            CloudFlare Analytics                       │   │
│   │   ┌───────────────────┐              ┌───────────────────┐                      │   │
│   │   │ • CPU, RAM, Disk  │              │ • Request metrics │                      │   │
│   │   │ • Network I/O     │              │ • Cache hit rate  │                      │   │
│   │   │ • Database metrics│              │ • Threat blocking │                      │   │
│   │   │ • Email alerts    │              │ • Performance     │                      │   │
│   │   └───────────────────┘              └───────────────────┘                      │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│   ALERT CHANNELS:                                                                        │
│   ─────────────────                                                                      │
│   Critical: SMS + Email + Slack                                                         │
│   Warning: Email + Slack                                                                 │
│   Info: Logged only                                                                      │
│                                                                                          │
│   ALERT CONDITIONS:                                                                      │
│   ─────────────────                                                                      │
│   • Site unreachable > 2 min                    → Critical                              │
│   • Response time > 5s                          → Warning                                │
│   • CPU > 80% for 10 min                        → Warning                                │
│   • Disk > 85%                                  → Warning                                │
│   • Database connections > 100                  → Warning                                │
│   • Backup failed                               → Critical                              │
│   • SSL certificate expiring < 7 days           → Warning                                │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CI/CD PIPELINE                                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   FRONTEND (Vue/React) - GitHub Actions → CloudFlare Pages                              │
│   ─────────────────────────────────────────────────────────                             │
│                                                                                          │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────────────┐  │
│   │  Push   │ ── │  Build  │ ── │  Test   │ ── │ Deploy  │ ── │ CloudFlare Pages    │  │
│   │ (main)  │    │ (Vite)  │    │ (Jest)  │    │         │    │ (Auto-deploy)       │  │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────────────────┘  │
│                                                                                          │
│                                                                                          │
│   BACKEND (Frappe) - GitHub Actions → E2E Server                                        │
│   ──────────────────────────────────────────────                                        │
│                                                                                          │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────────────┐  │
│   │  Push   │ ── │  Test   │ ── │  SSH    │ ── │ Deploy  │ ── │ E2E App Server      │  │
│   │ (main)  │    │(pytest) │    │ Connect │    │ (bench) │    │ (bench deploy)      │  │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────────────────┘  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**GitHub Actions - Frontend:**
```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'university-frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: cd university-frontend && npm ci

      - name: Build
        run: cd university-frontend && npm run build

      - name: Deploy to CloudFlare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: university-erp-frontend
          directory: university-frontend/dist
```

**GitHub Actions - Backend:**
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'frappe-bench/apps/university_erp/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to E2E Server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.E2E_HOST }}
          username: frappe
          key: ${{ secrets.E2E_SSH_KEY }}
          script: |
            cd ~/frappe-bench
            git pull origin main
            bench --site university.example.com migrate
            bench build
            sudo supervisorctl restart all
```

---

## Cost Summary

### Recommended Setup (2,000 Students)

| Component | Provider | Monthly Cost (₹) |
|-----------|----------|------------------|
| **Frontend** | | |
| CloudFlare Pages | CloudFlare | **FREE** |
| CloudFlare CDN + SSL | CloudFlare | **FREE** |
| | | |
| **Backend** | | |
| App Server (C2.Medium) | E2E Networks | ₹1,500 |
| Worker Server (C2.Small) | E2E Networks | ₹750 |
| Managed MySQL (2GB) | E2E Networks | ₹1,200 |
| Block Storage (100GB) | E2E Networks | ₹500 |
| Object Storage (200GB) | E2E Networks | ₹200 |
| Load Balancer | E2E Networks | ₹500 |
| Static IP | E2E Networks | ₹100 |
| | | |
| **External Services** | | |
| AWS SES (10k emails) | AWS | ₹100 |
| MSG91 SMS (2k) | MSG91 | ₹400 |
| Firebase FCM | Google | **FREE** |
| UptimeRobot | UptimeRobot | **FREE** |
| Healthchecks.io | Healthchecks | **FREE** |
| | | |
| **TOTAL** | | **₹5,250/month** |

### Comparison with Original Single App Setup

| Setup | Monthly Cost | Notes |
|-------|--------------|-------|
| Original (Single Frappe app) | ₹4,850 | No separate frontend |
| Proposed (Custom Frontend) | ₹5,250 | +₹400 for worker server |
| Using Vercel/Netlify Free | ₹5,250 | Same as above |
| CloudFlare Pro (optional) | ₹6,950 | +₹1,700 for Pro features |

---

## Scaling Path

### Growth Timeline

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              SCALING ROADMAP                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   PHASE 1: Current (2,000 students)                     Cost: ₹5,250/month              │
│   ─────────────────────────────────                                                      │
│   • 1 App Server (C2.Medium)                                                             │
│   • 1 Worker Server (C2.Small)                                                           │
│   • Managed MySQL 2GB                                                                    │
│   • CloudFlare Pages (frontend)                                                          │
│                                                                                          │
│                                    │                                                     │
│                                    ▼                                                     │
│                                                                                          │
│   PHASE 2: Growth (5,000 students)                      Cost: ₹12,000/month             │
│   ─────────────────────────────────                                                      │
│   • 2 App Servers (C2.Medium)                                                            │
│   • 1 Worker Server (C2.Medium)                                                          │
│   • Managed MySQL 4GB                                                                    │
│   • Load Balancer with health checks                                                     │
│   • Redis cluster (separate node)                                                        │
│                                                                                          │
│                                    │                                                     │
│                                    ▼                                                     │
│                                                                                          │
│   PHASE 3: Scale (10,000+ students)                     Cost: ₹25,000/month             │
│   ──────────────────────────────────                                                     │
│   • 3+ App Servers (auto-scaling)                                                        │
│   • Dedicated Worker cluster                                                             │
│   • Managed MySQL 8GB + Read Replica                                                     │
│   • Managed Redis cluster                                                                │
│   • CDN for API responses                                                                │
│   • Consider Kubernetes                                                                  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start Checklist

### Infrastructure Setup

- [ ] Create E2E Networks account and verify KYC
- [ ] Generate SSH key and add to E2E Dashboard
- [ ] Create VPC with public and private subnets
- [ ] Create App Server (C2.Medium)
- [ ] Create Worker Server (C2.Small)
- [ ] Create Managed MySQL database
- [ ] Create Object Storage bucket
- [ ] Create Block Storage and attach to App Server
- [ ] Configure Security Groups
- [ ] Create Load Balancer

### Frontend Deployment

- [ ] Create GitHub repository for frontend
- [ ] Connect to CloudFlare Pages
- [ ] Configure custom domain (portal.university.edu)
- [ ] Set up environment variables
- [ ] Configure API proxy rewrites

### Backend Deployment

- [ ] Install Frappe/ERPNext on App Server
- [ ] Configure site with E2E MySQL
- [ ] Install university_erp custom app
- [ ] Configure Redis cache and queue
- [ ] Set up Supervisor for workers
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL with CloudFlare Origin cert

### Integration

- [ ] Configure CORS for frontend domain
- [ ] Set up Firebase for push notifications
- [ ] Configure AWS SES for emails
- [ ] Configure MSG91 for SMS
- [ ] Test API authentication from frontend
- [ ] Test file uploads to EOS

### Security & Monitoring

- [ ] Enable UFW firewall
- [ ] Install and configure fail2ban
- [ ] Disable root SSH login
- [ ] Set up UptimeRobot monitoring
- [ ] Set up Healthchecks.io for backups
- [ ] Configure backup scripts and cron
- [ ] Test backup restoration

### Go-Live

- [ ] DNS propagation verified
- [ ] SSL working correctly
- [ ] All API endpoints tested
- [ ] PWA installation tested
- [ ] Push notifications working
- [ ] Backup verified
- [ ] Monitoring alerts tested

---

**Document Version:** 1.0
**Last Updated:** January 2026
**Architecture:** Custom Vue/React Frontend + Frappe Backend
**Target Scale:** 2,000 students (scalable to 10,000+)
