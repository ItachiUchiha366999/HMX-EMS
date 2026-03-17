# Phase 22: Deployment & Infrastructure

## Overview

This phase covers production deployment strategies, infrastructure setup, CI/CD pipelines, monitoring, backup strategies, security hardening, performance optimization, and scalability configurations for the University ERP system.

**Duration:** 4 Weeks
**Priority:** Critical
**Dependencies:** All previous phases

## Gap Analysis Reference

From IMPLEMENTATION_GAP_ANALYSIS.md:
- Production Deployment: 0% (Missing)
- CI/CD Pipeline: 0% (Missing)
- Monitoring & Logging: 0% (Missing)
- Backup Strategy: 0% (Missing)
- Security Hardening: 0% (Missing)
- Performance Optimization: 0% (Missing)
- High Availability: 0% (Missing)

---

## 1. Docker Production Setup

### 1.1 Production Docker Compose

```yaml
# docker-compose.prod.yml

version: "3.8"

services:
  # Frappe/ERPNext Backend
  backend:
    image: university-erp:${VERSION:-latest}
    build:
      context: .
      dockerfile: images/production/Containerfile
      args:
        - FRAPPE_VERSION=version-15
        - ERPNEXT_VERSION=version-15
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - FRAPPE_SITE_NAME_HEADER=university.local
      - WORKER_CLASS=gthread
      - GUNICORN_WORKERS=4
      - GUNICORN_THREADS=4
    volumes:
      - sites:/home/frappe/frappe-bench/sites
      - logs:/home/frappe/frappe-bench/logs
    networks:
      - university-network
    depends_on:
      - db
      - redis-cache
      - redis-queue

  # Background Workers
  worker-default:
    image: university-erp:${VERSION:-latest}
    command: bench worker --queue default
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 2G
    volumes:
      - sites:/home/frappe/frappe-bench/sites
      - logs:/home/frappe/frappe-bench/logs
    networks:
      - university-network
    depends_on:
      - backend

  worker-short:
    image: university-erp:${VERSION:-latest}
    command: bench worker --queue short
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    networks:
      - university-network
    depends_on:
      - backend

  worker-long:
    image: university-erp:${VERSION:-latest}
    command: bench worker --queue long
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '1'
          memory: 2G
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    networks:
      - university-network
    depends_on:
      - backend

  # Scheduler
  scheduler:
    image: university-erp:${VERSION:-latest}
    command: bench schedule
    deploy:
      replicas: 1
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    networks:
      - university-network
    depends_on:
      - backend

  # MariaDB Database
  db:
    image: mariadb:10.11
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --skip-character-set-client-handshake
      - --innodb-buffer-pool-size=2G
      - --innodb-log-file-size=512M
      - --innodb-flush-log-at-trx-commit=2
      - --max-connections=500
      - --query-cache-size=128M
      - --tmp-table-size=256M
      - --max-heap-table-size=256M
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
      MYSQL_DATABASE: university_erp
      MYSQL_USER: frappe
      MYSQL_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - db-data:/var/lib/mysql
      - ./mariadb/conf.d:/etc/mysql/conf.d:ro
    networks:
      - university-network
    secrets:
      - db_root_password
      - db_password
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Redis Cache
  redis-cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
    volumes:
      - redis-cache-data:/data
    networks:
      - university-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  # Redis Queue
  redis-queue:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    volumes:
      - redis-queue-data:/data
    networks:
      - university-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - sites:/var/www/sites:ro
      - ssl-certs:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    networks:
      - university-network
    depends_on:
      - backend
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  # Backup Service
  backup:
    image: university-erp:${VERSION:-latest}
    command: /backup-cron.sh
    volumes:
      - sites:/home/frappe/frappe-bench/sites
      - backups:/backups
      - ./scripts/backup-cron.sh:/backup-cron.sh:ro
    networks:
      - university-network
    depends_on:
      - db

volumes:
  sites:
  logs:
  db-data:
  redis-cache-data:
  redis-queue-data:
  backups:
  ssl-certs:

networks:
  university-network:
    driver: overlay
    attachable: true

secrets:
  db_root_password:
    external: true
  db_password:
    external: true
```

### 1.2 Nginx Configuration

```nginx
# nginx/conf.d/university.conf

upstream backend {
    ip_hash;
    server backend:8000 weight=5;
    server backend:8000 weight=5;
    keepalive 32;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

# Cache zones
proxy_cache_path /var/cache/nginx/static levels=1:2 keys_zone=static_cache:10m max_size=1g inactive=60m;
proxy_cache_path /var/cache/nginx/api levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=10m;

server {
    listen 80;
    server_name university.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name university.example.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' wss:; frame-ancestors 'self';" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml application/xml+rss text/javascript application/x-javascript;

    # Client settings
    client_max_body_size 50M;
    client_body_buffer_size 128k;

    # Connection limits
    limit_conn conn_limit 20;

    # Static files with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/sites;
        expires 1y;
        add_header Cache-Control "public, immutable";
        proxy_cache static_cache;
        proxy_cache_valid 200 1d;
        access_log off;
    }

    # API rate limiting
    location /api/ {
        limit_req zone=api_limit burst=50 nodelay;

        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        # API response caching for GET requests
        proxy_cache api_cache;
        proxy_cache_methods GET HEAD;
        proxy_cache_valid 200 5m;
        proxy_cache_bypass $http_cache_control;
        add_header X-Cache-Status $upstream_cache_status;
    }

    # Login rate limiting
    location /api/method/login {
        limit_req zone=login_limit burst=3;

        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /socket.io/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # Main application
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Status page for monitoring
    location /nginx_status {
        stub_status on;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

---

## 2. CI/CD Pipeline

### 2.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml

name: Build and Deploy University ERP

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mariadb:
        image: mariadb:10.11
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_university
        ports:
          - 3306:3306
        options: --health-cmd="healthcheck.sh --connect --innodb_initialized" --health-interval=10s --health-timeout=5s --health-retries=3

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install frappe-bench
          bench init --skip-redis-config-generation frappe-bench
          cd frappe-bench
          bench get-app university_erp ${{ github.workspace }}/apps/university_erp

      - name: Run tests
        run: |
          cd frappe-bench
          bench --site test_site run-tests --app university_erp --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frappe-bench/sites/coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install linters
        run: |
          pip install ruff black isort mypy

      - name: Run Ruff
        run: ruff check apps/university_erp

      - name: Run Black
        run: black --check apps/university_erp

      - name: Run isort
        run: isort --check-only apps/university_erp

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'

      - name: Run Bandit security linter
        run: |
          pip install bandit
          bandit -r apps/university_erp -ll

  build:
    needs: [test, lint, security-scan]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./images/production/Containerfile
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
      - name: Deploy to Staging
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/university-erp
            docker-compose -f docker-compose.staging.yml pull
            docker-compose -f docker-compose.staging.yml up -d
            docker-compose exec -T backend bench --site staging.university.local migrate
            docker-compose exec -T backend bench --site staging.university.local clear-cache

      - name: Run smoke tests
        run: |
          sleep 30
          curl -f https://staging.university.example.com/health || exit 1

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Staging deployment completed'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production

    steps:
      - name: Deploy to Production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/university-erp

            # Create backup before deployment
            ./scripts/backup.sh

            # Pull new images
            docker-compose -f docker-compose.prod.yml pull

            # Rolling update
            docker-compose -f docker-compose.prod.yml up -d --no-deps --scale backend=3 backend
            sleep 30
            docker-compose -f docker-compose.prod.yml up -d --no-deps --scale backend=2 backend

            # Run migrations
            docker-compose exec -T backend bench --site university.local migrate

            # Clear cache
            docker-compose exec -T backend bench --site university.local clear-cache

      - name: Health check
        run: |
          for i in {1..5}; do
            curl -f https://university.example.com/health && exit 0
            sleep 10
          done
          exit 1

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
```

---

## 3. Monitoring & Logging

### 3.1 Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Frappe/ERPNext metrics
  - job_name: 'frappe'
    static_configs:
      - targets: ['backend:9100']
    metrics_path: /api/method/frappe.monitor.get_metrics

  # Nginx metrics
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  # MariaDB metrics
  - job_name: 'mariadb'
    static_configs:
      - targets: ['mysqld-exporter:9104']

  # Redis metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Node metrics (system)
  - job_name: 'node'
    static_configs:
      - targets:
        - 'node-exporter:9100'
```

### 3.2 Alert Rules

```yaml
# monitoring/prometheus/rules/alerts.yml

groups:
  - name: university_erp_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(frappe_request_errors_total[5m])) /
          sum(rate(frappe_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} over the last 5 minutes"

      # Slow response time
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95, rate(frappe_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times"
          description: "95th percentile response time is {{ $value }}s"

      # Worker queue backup
      - alert: WorkerQueueBackup
        expr: frappe_background_jobs_pending > 1000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Background job queue backing up"
          description: "{{ $value }} jobs pending in queue"

      # Database connections
      - alert: HighDatabaseConnections
        expr: mysql_global_status_threads_connected > 400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connection count"
          description: "{{ $value }} active database connections"

      # Memory usage
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) /
          node_memory_MemTotal_bytes > 0.9
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      # Disk space
      - alert: LowDiskSpace
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} /
          node_filesystem_size_bytes{mountpoint="/"}) < 0.15
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Only {{ $value | humanizePercentage }} disk space remaining"

      # SSL certificate expiry
      - alert: SSLCertificateExpiringSoon
        expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 30
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "SSL certificate expiring soon"
          description: "Certificate expires in {{ $value | humanizeDuration }}"

      # Backup failure
      - alert: BackupFailed
        expr: time() - backup_last_success_timestamp > 86400 * 2
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "Backup not completed"
          description: "Last successful backup was {{ $value | humanizeDuration }} ago"
```

### 3.3 Grafana Dashboard

```json
{
  "dashboard": {
    "title": "University ERP Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "sum(rate(frappe_requests_total[5m]))",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(frappe_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "frappe_active_users",
            "legendFormat": "Users"
          }
        ]
      },
      {
        "title": "Background Jobs",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 8},
        "targets": [
          {
            "expr": "frappe_background_jobs_pending",
            "legendFormat": "Pending"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "gauge",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8},
        "targets": [
          {
            "expr": "mysql_global_status_threads_connected"
          }
        ],
        "options": {
          "maxValue": 500
        }
      },
      {
        "title": "Memory Usage",
        "type": "gauge",
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 8},
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
          }
        ]
      }
    ]
  }
}
```

### 3.4 Centralized Logging with Loki

```yaml
# monitoring/loki/loki-config.yml

auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s
  max_transfer_retries: 0

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h
```

---

## 4. Backup Strategy

### 4.1 Automated Backup Script

```bash
#!/bin/bash
# scripts/backup.sh

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
SITE_NAME="university.local"
RETENTION_DAYS=30
S3_BUCKET="university-erp-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_${SITE_NAME}_${TIMESTAMP}"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    log "ERROR: $1"
    exit 1
}

# Create backup directory
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

log "Starting backup for ${SITE_NAME}"

# 1. Database backup
log "Backing up database..."
docker exec university-erp-db-1 mysqldump \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --quick \
    --lock-tables=false \
    -u root \
    -p"${MYSQL_ROOT_PASSWORD}" \
    "${SITE_NAME//./_}" | gzip > "${BACKUP_DIR}/${BACKUP_NAME}/database.sql.gz"

if [ $? -ne 0 ]; then
    error "Database backup failed"
fi

# 2. Files backup
log "Backing up site files..."
docker exec university-erp-backend-1 tar czf - \
    -C /home/frappe/frappe-bench/sites/${SITE_NAME} \
    private public > "${BACKUP_DIR}/${BACKUP_NAME}/files.tar.gz"

# 3. Configuration backup
log "Backing up configuration..."
cp -r /opt/university-erp/nginx "${BACKUP_DIR}/${BACKUP_NAME}/"
cp /opt/university-erp/docker-compose.prod.yml "${BACKUP_DIR}/${BACKUP_NAME}/"

# 4. Create archive
log "Creating backup archive..."
cd "${BACKUP_DIR}"
tar czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

# 5. Upload to S3
log "Uploading to S3..."
aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
    "s3://${S3_BUCKET}/backups/${BACKUP_NAME}.tar.gz" \
    --storage-class STANDARD_IA

# 6. Cleanup old backups
log "Cleaning up old backups..."
find "${BACKUP_DIR}" -name "backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

# Cleanup S3 (using lifecycle policy is preferred)
aws s3 ls "s3://${S3_BUCKET}/backups/" | while read -r line; do
    createDate=$(echo $line | awk '{print $1}')
    fileName=$(echo $line | awk '{print $4}')
    convertedDate=$(date -d "$createDate" +%s)
    olderThan=$(date -d "-${RETENTION_DAYS} days" +%s)
    if [[ $convertedDate -lt $olderThan ]]; then
        aws s3 rm "s3://${S3_BUCKET}/backups/$fileName"
    fi
done

# 7. Verify backup
log "Verifying backup..."
BACKUP_SIZE=$(stat -f%z "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" 2>/dev/null || stat -c%s "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz")
if [ "$BACKUP_SIZE" -lt 1000 ]; then
    error "Backup file is too small, might be corrupted"
fi

# 8. Update backup status
docker exec university-erp-backend-1 bench --site ${SITE_NAME} execute \
    "frappe.db.set_value('System Settings', None, 'last_backup_time', '$(date -Iseconds)')"

# 9. Send notification
BACKUP_SIZE_HUMAN=$(numfmt --to=iec-i --suffix=B "$BACKUP_SIZE")
curl -X POST "${SLACK_WEBHOOK_URL}" \
    -H 'Content-type: application/json' \
    -d "{\"text\":\"✅ Backup completed successfully\nSite: ${SITE_NAME}\nSize: ${BACKUP_SIZE_HUMAN}\nTime: $(date)\"}"

log "Backup completed successfully: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE_HUMAN})"
```

### 4.2 Restore Script

```bash
#!/bin/bash
# scripts/restore.sh

set -euo pipefail

BACKUP_FILE=$1
SITE_NAME="university.local"
TEMP_DIR="/tmp/restore_$$"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting restore from ${BACKUP_FILE}"

# Create temp directory
mkdir -p "${TEMP_DIR}"

# Extract backup
log "Extracting backup..."
tar xzf "${BACKUP_FILE}" -C "${TEMP_DIR}"
BACKUP_NAME=$(ls "${TEMP_DIR}")

# Put site in maintenance mode
log "Enabling maintenance mode..."
docker exec university-erp-backend-1 bench --site ${SITE_NAME} set-maintenance-mode on

# Stop workers
log "Stopping workers..."
docker-compose -f /opt/university-erp/docker-compose.prod.yml stop worker-default worker-short worker-long scheduler

# Restore database
log "Restoring database..."
gunzip -c "${TEMP_DIR}/${BACKUP_NAME}/database.sql.gz" | \
    docker exec -i university-erp-db-1 mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "${SITE_NAME//./_}"

# Restore files
log "Restoring files..."
docker exec university-erp-backend-1 rm -rf /home/frappe/frappe-bench/sites/${SITE_NAME}/private/*
docker exec university-erp-backend-1 rm -rf /home/frappe/frappe-bench/sites/${SITE_NAME}/public/files/*
cat "${TEMP_DIR}/${BACKUP_NAME}/files.tar.gz" | \
    docker exec -i university-erp-backend-1 tar xzf - -C /home/frappe/frappe-bench/sites/${SITE_NAME}/

# Clear cache
log "Clearing cache..."
docker exec university-erp-backend-1 bench --site ${SITE_NAME} clear-cache

# Run migrations (in case of version mismatch)
log "Running migrations..."
docker exec university-erp-backend-1 bench --site ${SITE_NAME} migrate

# Start workers
log "Starting workers..."
docker-compose -f /opt/university-erp/docker-compose.prod.yml up -d worker-default worker-short worker-long scheduler

# Disable maintenance mode
log "Disabling maintenance mode..."
docker exec university-erp-backend-1 bench --site ${SITE_NAME} set-maintenance-mode off

# Cleanup
rm -rf "${TEMP_DIR}"

log "Restore completed successfully"
```

---

## 5. Security Hardening

### 5.1 Security Configuration

```python
# site_config.json security settings

{
  "allow_cors": "https://university.example.com",
  "deny_multiple_sessions": true,
  "disable_session_cache": false,
  "disable_website_cache": false,
  "encryption_key": "{{ vault_encryption_key }}",
  "force_https": true,
  "http_timeout": 120,
  "logging": 1,
  "mail_login": "{{ vault_mail_login }}",
  "mail_password": "{{ vault_mail_password }}",
  "mail_port": 587,
  "mail_server": "smtp.example.com",
  "max_reports_per_user": 50,
  "monitor": 1,
  "rate_limit": {
    "limit": 300,
    "window": 300
  },
  "redis_cache": "redis://redis-cache:6379/0",
  "redis_queue": "redis://redis-queue:6379/0",
  "restrict_to_domain": "university.example.com",
  "robots_txt": "/robots.txt",
  "session_expiry": 480,
  "session_expiry_mobile": 1440,
  "use_ssl": true
}
```

### 5.2 Security Headers Middleware

```python
# university_erp/university_erp/security/middleware.py

import frappe

def add_security_headers(response):
    """Add security headers to all responses"""

    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.google.com https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: blob: https:; "
        "connect-src 'self' wss: https:; "
        "frame-src 'self' https://www.google.com; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'self'"
    )

    headers = {
        'Content-Security-Policy': csp,
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Cache-Control': 'no-store, no-cache, must-revalidate, private',
        'Pragma': 'no-cache'
    }

    for header, value in headers.items():
        response.headers[header] = value

    return response


# hooks.py
# app_include_js/css hooks don't apply here, use
# after_request = ["university_erp.university_erp.security.middleware.add_security_headers"]
```

### 5.3 Input Validation

```python
# university_erp/university_erp/security/validators.py

import frappe
from frappe import _
import re
import bleach
from typing import Any, Optional

class InputValidator:
    """Input validation and sanitization utilities"""

    # Allowed HTML tags for rich text
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 's', 'a', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre', 'code',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img', 'hr'
    ]

    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan']
    }

    @staticmethod
    def sanitize_html(value: str) -> str:
        """Sanitize HTML input to prevent XSS"""
        if not value:
            return value

        return bleach.clean(
            value,
            tags=InputValidator.ALLOWED_TAGS,
            attributes=InputValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove spaces, dashes, and parentheses
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        # Check if it's a valid number (10-15 digits, optionally starting with +)
        pattern = r'^\+?[0-9]{10,15}$'
        return bool(re.match(pattern, clean_phone))

    @staticmethod
    def validate_roll_number(roll: str) -> bool:
        """Validate roll number format (customize as needed)"""
        # Example: 2021CSE001
        pattern = r'^[0-9]{4}[A-Z]{2,5}[0-9]{3,4}$'
        return bool(re.match(pattern, roll.upper()))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize file name to prevent path traversal"""
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        # Remove special characters except dots and underscores
        filename = re.sub(r'[^\w\.\-]', '_', filename)
        # Prevent hidden files
        if filename.startswith('.'):
            filename = '_' + filename[1:]
        return filename

    @staticmethod
    def validate_file_type(filename: str, allowed_types: list) -> bool:
        """Validate file extension"""
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        return ext in allowed_types

    @staticmethod
    def escape_sql_like(value: str) -> str:
        """Escape special characters for LIKE queries"""
        return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


# Decorator for validating API inputs
def validate_api_input(schema: dict):
    """Decorator to validate API input parameters"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for field, rules in schema.items():
                value = kwargs.get(field) or frappe.local.form_dict.get(field)

                if rules.get('required') and not value:
                    frappe.throw(_(f"{field} is required"))

                if value:
                    # Type validation
                    expected_type = rules.get('type')
                    if expected_type == 'email' and not InputValidator.validate_email(value):
                        frappe.throw(_(f"Invalid email format for {field}"))
                    elif expected_type == 'phone' and not InputValidator.validate_phone(value):
                        frappe.throw(_(f"Invalid phone format for {field}"))

                    # Length validation
                    max_length = rules.get('max_length')
                    if max_length and len(str(value)) > max_length:
                        frappe.throw(_(f"{field} exceeds maximum length of {max_length}"))

                    # Pattern validation
                    pattern = rules.get('pattern')
                    if pattern and not re.match(pattern, str(value)):
                        frappe.throw(_(f"Invalid format for {field}"))

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 6. Performance Optimization

### 6.1 Database Optimization

```sql
-- database/optimize.sql

-- Add indexes for common queries
CREATE INDEX idx_student_user ON `tabStudent`(user);
CREATE INDEX idx_student_program ON `tabStudent`(program);
CREATE INDEX idx_student_department ON `tabStudent`(department);
CREATE INDEX idx_student_batch ON `tabStudent`(batch);

CREATE INDEX idx_attendance_student_date ON `tabStudent Attendance`(student, attendance_date);
CREATE INDEX idx_attendance_course_date ON `tabStudent Attendance`(course, attendance_date);

CREATE INDEX idx_fees_student ON `tabFees`(student);
CREATE INDEX idx_fees_status ON `tabFees`(outstanding_amount, due_date);

CREATE INDEX idx_assessment_student ON `tabAssessment Result`(student);
CREATE INDEX idx_assessment_course ON `tabAssessment Result`(course);

-- Optimize table storage
OPTIMIZE TABLE `tabStudent`;
OPTIMIZE TABLE `tabStudent Attendance`;
OPTIMIZE TABLE `tabFees`;
OPTIMIZE TABLE `tabAssessment Result`;

-- Update statistics
ANALYZE TABLE `tabStudent`;
ANALYZE TABLE `tabStudent Attendance`;
ANALYZE TABLE `tabFees`;
ANALYZE TABLE `tabAssessment Result`;
```

### 6.2 Caching Strategy

```python
# university_erp/university_erp/caching/cache_manager.py

import frappe
from frappe.utils import cint
import json
from typing import Any, Optional, Callable
from functools import wraps

class CacheManager:
    """
    Centralized cache management for University ERP
    """

    # Cache key prefixes
    STUDENT_PREFIX = "student_data"
    TIMETABLE_PREFIX = "timetable"
    DASHBOARD_PREFIX = "dashboard"
    REPORT_PREFIX = "report"

    # Default TTL in seconds
    DEFAULT_TTL = 300  # 5 minutes
    LONG_TTL = 3600    # 1 hour
    SHORT_TTL = 60     # 1 minute

    @staticmethod
    def get_cache_key(*args) -> str:
        """Generate cache key from arguments"""
        return ":".join(str(arg) for arg in args)

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        value = frappe.cache().get_value(key)
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        ttl = ttl or CacheManager.DEFAULT_TTL
        try:
            serialized = json.dumps(value)
        except (TypeError, ValueError):
            serialized = value
        frappe.cache().set_value(key, serialized, expires_in_sec=ttl)

    @staticmethod
    def delete(key: str):
        """Delete value from cache"""
        frappe.cache().delete_value(key)

    @staticmethod
    def delete_pattern(pattern: str):
        """Delete all keys matching pattern"""
        frappe.cache().delete_keys(pattern)

    @staticmethod
    def invalidate_student_cache(student: str):
        """Invalidate all cache for a student"""
        patterns = [
            f"{CacheManager.STUDENT_PREFIX}:{student}:*",
            f"{CacheManager.DASHBOARD_PREFIX}:{student}",
            f"{CacheManager.TIMETABLE_PREFIX}:{student}:*"
        ]
        for pattern in patterns:
            CacheManager.delete_pattern(pattern)

    @staticmethod
    def invalidate_course_cache(course: str):
        """Invalidate cache for a course"""
        CacheManager.delete_pattern(f"*:course:{course}:*")


def cached(key_prefix: str, ttl: int = None, key_builder: Callable = None):
    """
    Decorator for caching function results

    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key from args
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: use function name and arguments
                arg_str = "_".join(str(arg) for arg in args)
                kwarg_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{func.__name__}:{arg_str}:{kwarg_str}"

            # Check cache
            cached_value = CacheManager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            CacheManager.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


# Usage example
@cached(key_prefix="student", ttl=300)
def get_student_dashboard_data(student: str):
    """Get dashboard data for a student (cached)"""
    # ... implementation
    pass


# Cache invalidation on document events
def on_student_update(doc, method):
    """Invalidate cache when student is updated"""
    CacheManager.invalidate_student_cache(doc.name)

def on_attendance_insert(doc, method):
    """Invalidate attendance cache"""
    CacheManager.delete_pattern(f"*:{doc.student}:attendance:*")
```

---

## 7. Implementation Checklist

### Week 1: Infrastructure Setup
- [ ] Set up production Docker environment
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure MariaDB optimization
- [ ] Set up Redis caching
- [ ] Configure Docker secrets

### Week 2: CI/CD Pipeline
- [ ] Set up GitHub Actions workflows
- [ ] Configure automated testing
- [ ] Set up security scanning
- [ ] Configure Docker image building
- [ ] Set up staging deployment
- [ ] Configure production deployment

### Week 3: Monitoring & Logging
- [ ] Set up Prometheus metrics
- [ ] Configure Grafana dashboards
- [ ] Set up Loki for logging
- [ ] Configure alert rules
- [ ] Set up PagerDuty/Slack integration
- [ ] Create runbooks

### Week 4: Security & Backup
- [ ] Implement security headers
- [ ] Configure input validation
- [ ] Set up automated backups
- [ ] Configure S3 backup storage
- [ ] Create restore procedures
- [ ] Perform security audit
- [ ] Load testing and optimization

---

## 8. Infrastructure Diagram

```
                                    ┌─────────────┐
                                    │   Internet  │
                                    └──────┬──────┘
                                           │
                                    ┌──────▼──────┐
                                    │ CloudFlare  │
                                    │    (CDN)    │
                                    └──────┬──────┘
                                           │
                              ┌────────────┼────────────┐
                              │            │            │
                        ┌─────▼─────┐┌─────▼─────┐┌─────▼─────┐
                        │  Nginx-1  ││  Nginx-2  ││  Nginx-3  │
                        └─────┬─────┘└─────┬─────┘└─────┬─────┘
                              │            │            │
                              └────────────┼────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
              ┌─────▼─────┐         ┌──────▼──────┐        ┌──────▼──────┐
              │ Backend-1 │         │  Backend-2  │        │  Backend-3  │
              └─────┬─────┘         └──────┬──────┘        └──────┬──────┘
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
       ┌──────▼──────┐             ┌───────▼───────┐             ┌──────▼──────┐
       │ MariaDB     │             │  Redis Cache  │             │ Redis Queue │
       │ (Primary)   │             │   (Cluster)   │             │  (Cluster)  │
       └──────┬──────┘             └───────────────┘             └─────────────┘
              │
       ┌──────▼──────┐
       │  MariaDB    │
       │  (Replica)  │
       └─────────────┘
```

---

## 9. Disaster Recovery Plan

### 9.1 Recovery Time Objective (RTO)
- Critical systems: < 1 hour
- Non-critical systems: < 4 hours

### 9.2 Recovery Point Objective (RPO)
- Database: < 15 minutes (continuous replication)
- Files: < 1 hour (hourly backups)

### 9.3 Failover Procedures

1. **Database Failover**
   - Automatic failover using MariaDB Galera Cluster
   - Manual promotion of replica if needed

2. **Application Failover**
   - Docker Swarm automatic container restart
   - Load balancer health checks remove failed nodes

3. **Complete Site Failover**
   - DNS failover to disaster recovery site
   - Restore from S3 backups if needed
