# External Integrations

**Analysis Date:** 2026-03-17

## APIs & External Services

**Payment Processing:**
- Razorpay - Indian payment gateway and invoicing platform
  - SDK/Client: `razorpay` (v1.4.0)
  - Implementation: `university_erp.university_integrations.payment_gateway.RazorpayGateway`
  - Auth: Environment vars: `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`
  - Features: Order creation, payment verification, refund processing
  - Currency: INR

- PayU - Indian payment gateway (optional)
  - Auth: Environment vars: `PAYU_MERCHANT_KEY`, `PAYU_SALT`
  - Implementation: `university_erp.university_integrations.payment_gateway.PayUGateway` (framework present)

- Paytm, CCAvenue, Stripe - Supported (framework available in payment_gateway module)
  - Implementation: `university_erp.university_integrations.payment_gateway`

**Communication & Messaging:**
- WhatsApp Business API - Multi-provider WhatsApp integration
  - Implementation: `university_erp.university_integrations.whatsapp_gateway.WhatsAppGateway`
  - Supported providers: Meta Business API, Twilio WhatsApp, Gupshup, WATI
  - Auth: Provider-specific credentials via `WhatsApp Settings` doctype
  - Features: Template messages, bulk messaging, rate limiting, message logging
  - Config: `/workspace/development/frappe-bench/apps/university_erp/university_erp/university_integrations/whatsapp_gateway.py`

- SMS Gateway - Generic SMS provider
  - Implementation: `university_erp.university_integrations.sms_gateway.py`
  - Supports multiple providers

- Firebase Cloud Messaging (FCM) - Push notifications
  - SDK/Client: `firebase-admin` (conditionally imported)
  - Implementation: `university_erp.university_integrations.firebase_admin.FirebaseAdmin`
  - Auth: Service account JSON via `Firebase Settings` doctype
  - API Version: FCM HTTP v1
  - Features: Push notification delivery to mobile apps, topic subscriptions
  - Singleton pattern initialization
  - Config: `/workspace/development/frappe-bench/apps/university_erp/university_erp/university_integrations/firebase_admin.py`

**Document & Certificate Management:**
- DigiLocker - India's National Digital Locker System
  - Implementation: `university_erp.university_integrations.digilocker_integration.DigiLockerClient`
  - Auth: `client_id`, `client_secret`, `hmac_key` via `DigiLocker Settings` doctype
  - Environments: Production (api.digitallocker.gov.in) and Staging (apisetu.gov.in)
  - Features: Document issuance, retrieval, HMAC-SHA256 signed requests
  - Config: `/workspace/development/frappe-bench/apps/university_erp/university_erp/university_integrations/digilocker_integration.py`

- Certificate Generator - Internal certificate generation engine
  - Implementation: `university_erp.university_integrations.certificate_generator.py`
  - Generates academic certificates, hall tickets, transcripts

**Biometric & Attendance:**
- Biometric Device Integration
  - Implementation: `university_erp.university_integrations.biometric_integration.py`
  - Supports multiple biometric device types

**Cloud Storage & Backups:**
- AWS S3 - Cloud file storage
  - SDK: boto3 (v1.34.143)
  - Config env var: `S3_BUCKET`
  - Features: Backup storage, file uploads

- Dropbox - Alternative cloud storage
  - SDK: dropbox (v11.36.2)

## Data Storage

**Databases:**
- MariaDB (Primary)
  - Client: PyMySQL 1.1.1 (strict version pinning)
  - Connection: Configured in `site_config.json`
  - Current setup: `db_name: _df4394075d9a924d` (university.local site)
  - Auth: Via `MYSQL_USER` and `MYSQL_PASSWORD` environment variables

- PostgreSQL (Secondary option)
  - Client: psycopg2-binary (v2.9.1)
  - Support optional, not actively used in current deployment

**File Storage:**
- Local filesystem - Primary storage location
  - Public files: `/workspace/development/frappe-bench/sites/university.local/public`
  - Private files: `/workspace/development/frappe-bench/sites/university.local/private`
  - Logs: `/workspace/development/frappe-bench/sites/university.local/logs`

- AWS S3 - Optional backup/archive destination
  - Backup retention: 30 days (configurable via `RETENTION_DAYS`)
  - Backup directory: `/var/backups/university_erp` (default)

**Caching & Session Storage:**
- Redis (Cache)
  - Connection: Environment var `REDIS_CACHE` (default: redis://redis-cache:6379)
  - Purpose: Application cache, session store, real-time data
  - Client: redis (v4.5.5) + hiredis (v2.2.3)

- Redis (Job Queue)
  - Connection: Environment var `REDIS_QUEUE` (default: redis://redis-queue:6379)
  - Purpose: Background job scheduling and execution
  - Framework: rq (RQ - Redis Queue v1.15.1)
  - Worker: `bench worker 1` process (configured in Procfile)

## Authentication & Identity

**Auth Provider:**
- Custom (Frappe built-in)
  - Implementation: Frappe's user/role system with JWT tokens
  - Token generation: PyJWT (v2.8.0)
  - Approach:
    - Database-backed user credentials (hashed via passlib v1.7.4)
    - Session-based auth via cookies
    - JWT tokens for API requests
    - Role-based access control (RBAC) with custom roles (University roles)

- OAuth2 Integration (Optional)
  - Library: oauthlib (v3.2.2), requests-oauthlib (v1.3.1)
  - Supported: Google OAuth, generic OAuth2 providers
  - Credentials: google-auth (v2.40.3), google-auth-oauthlib (v1.2.2)

- LDAP (Optional)
  - Library: ldap3 (v2.9)
  - Purpose: Enterprise directory integration

## Monitoring & Observability

**Error Tracking:**
- Sentry - Error tracking and monitoring
  - SDK: sentry-sdk (v1.45.1)
  - Config env var: `SENTRY_DSN`
  - Captures: Exceptions, performance metrics, session replays

**Logs:**
- Approach: File-based logging
  - Location: `/workspace/development/frappe-bench/sites/university.local/logs/`
  - Access via Frappe UI: Admin > System > System Console
  - Worker logs: `/workspace/development/frappe-bench/logs/worker.log` and `.error.log`

**Analytics & Product Insights:**
- PostHog - Product analytics
  - SDK: posthog (v3.21.0)
  - Features: Event tracking, feature flags, user analytics

**Notifications:**
- Slack - Team notifications (optional)
  - Config env var: `SLACK_WEBHOOK_URL`
  - Used for system alerts and summary messages

## CI/CD & Deployment

**Hosting:**
- Docker containerization (development and production)
  - Base image: frappe/bench:version-15
  - Dockerfile: `/workspace/development/frappe-bench/apps/university_erp/Dockerfile`
  - Docker Compose: `/workspace/development/frappe-bench/apps/university_erp/docker-compose.yml`
  - Health check: API ping to `/api/method/frappe.ping`

- Bench CLI - Local development deployment
  - Commands: `bench serve`, `bench watch`, `bench schedule`, `bench worker`
  - Configuration: `/workspace/development/frappe-bench/Procfile`

**CI Pipeline:**
- Not detected (no GitHub Actions or CI config visible in current analysis)
- Git integration: GitPython support available

**Deployment Tools:**
- Bench (frappe/bench) - Development and production deployment
- Docker & Docker Compose for containerized deployments

## Environment Configuration

**Required env vars:**
- Site & Network:
  - `SITE_NAME` - Site identifier
  - `HTTP_PORT` - HTTP server port (default: 8000)
  - `HTTPS_PORT` - HTTPS port (default: 443)

- Database:
  - `MYSQL_ROOT_PASSWORD` - Database root password
  - `MYSQL_DATABASE` - Database name
  - `MYSQL_USER` - Database user
  - `MYSQL_PASSWORD` - Database password

- Cache & Queue:
  - `REDIS_CACHE` - Redis cache connection string
  - `REDIS_QUEUE` - Redis queue connection string

- Email:
  - `MAIL_SERVER` - SMTP server hostname
  - `MAIL_PORT` - SMTP port
  - `MAIL_USE_TLS` - Enable TLS (boolean)
  - `MAIL_LOGIN` - SMTP username
  - `MAIL_PASSWORD` - SMTP password

- Payment Gateways:
  - `RAZORPAY_KEY_ID` - Razorpay key ID
  - `RAZORPAY_KEY_SECRET` - Razorpay secret key
  - `RAZORPAY_WEBHOOK_SECRET` - Razorpay webhook secret

- Firebase:
  - Service account JSON (base64 encoded or JSON string)
  - Required for FCM push notifications

- DigiLocker:
  - `DIGILOCKER_CLIENT_ID` - DigiLocker OAuth client ID
  - `DIGILOCKER_CLIENT_SECRET` - DigiLocker OAuth client secret

- Push Notifications:
  - `VAPID_PUBLIC_KEY` - Web push VAPID public key
  - `VAPID_PRIVATE_KEY` - Web push VAPID private key
  - `PUSH_EMAIL` - Admin email for push service

- Backup:
  - `BACKUP_DIR` - Backup destination directory
  - `RETENTION_DAYS` - Backup retention period
  - `S3_BUCKET` - AWS S3 bucket name

- Monitoring:
  - `SENTRY_DSN` - Sentry error tracking DSN
  - `SLACK_WEBHOOK_URL` - Slack webhook for alerts

- Deployment:
  - `GIT_BRANCH` - Git branch to deploy
  - `ENVIRONMENT` - Environment name (production/staging/development)

**Secrets location:**
- `.env` file in `/workspace/development/frappe-bench/apps/university_erp/` (not committed)
- `.env.example` provided as template
- Frappe also stores encrypted passwords in database `single` doctypes:
  - `Payment Gateway Settings` (razorpay, payu credentials)
  - `Firebase Settings` (service account JSON)
  - `DigiLocker Settings` (client secret, hmac key)
  - `WhatsApp Settings` (provider credentials)
  - `Email Account Settings` (SMTP credentials)

## Webhooks & Callbacks

**Incoming:**
- Razorpay payment callbacks
  - Endpoint: Auto-handled by `payment_gateway` module
  - Signature validation: HMAC-SHA256
  - Triggers: Payment success, failure, refund notifications

- Webhook events from payment gateway
  - DigiLocker callbacks (document issued/revoked)
  - WhatsApp message delivery/read receipts

**Outgoing:**
- Scheduled notifications:
  - Fee reminders (daily via `send_fee_reminders`)
  - Overdue notices (daily)
  - Library overdue notices (daily)
  - Attendance warnings (weekly)
  - Placement updates (weekly)
  - Report generation (weekly, monthly)

- Real-time events via Socket.IO:
  - User notifications (connected to Frappe socketio.js)
  - Live dashboard updates
  - Real-time notifications center

---

*Integration audit: 2026-03-17*
