# University ERP - Frappe Docker & DevContainer Setup Guide

## Document Overview

| Item | Details |
|------|---------|
| **Document Version** | 1.0 |
| **Last Updated** | December 2025 |
| **Purpose** | Complete setup guide for Frappe/ERPNext development environment |
| **Target Audience** | Developers implementing University ERP |

---

## Part 1: Prerequisites & System Requirements

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Storage | 50 GB SSD | 100+ GB SSD |
| Network | Stable internet | High-speed broadband |

### Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 24.0+ | Containerization |
| Docker Compose | 2.20+ | Multi-container orchestration |
| VS Code | Latest | IDE with DevContainer support |
| Git | 2.40+ | Version control |
| Node.js | 18 LTS | Frontend tooling (local) |
| Python | 3.11+ | Backend development (local) |

---

## Part 2: Docker Environment Setup

### Step 2.1: Install Docker

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

### Step 2.2: Create Project Directory Structure

```bash
# Create main project directory
mkdir -p ~/university-erp
cd ~/university-erp

# Create subdirectories
mkdir -p {apps,sites,logs,config,backups,scripts}

# Create directory structure
# university-erp/
# ├── apps/                    # Custom Frappe apps
# │   └── university_ems/      # Main University ERP app
# ├── sites/                   # Frappe sites
# ├── logs/                    # Application logs
# ├── config/                  # Configuration files
# ├── backups/                 # Database backups
# ├── scripts/                 # Utility scripts
# ├── docker-compose.yml       # Docker compose configuration
# ├── .env                     # Environment variables
# └── .devcontainer/           # VS Code DevContainer config
```

### Step 2.3: Create Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  # MariaDB Database
  mariadb:
    image: mariadb:10.6
    container_name: university_erp_db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-admin123}
      MYSQL_DATABASE: ${DB_NAME:-university_erp}
      MYSQL_USER: ${DB_USER:-erpnext}
      MYSQL_PASSWORD: ${DB_PASSWORD:-erpnext123}
    volumes:
      - mariadb_data:/var/lib/mysql
      - ./config/mariadb.cnf:/etc/mysql/conf.d/frappe.cnf:ro
    ports:
      - "3307:3306"
    networks:
      - university_erp_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${DB_ROOT_PASSWORD:-admin123}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis-cache:
    image: redis:7-alpine
    container_name: university_erp_redis_cache
    restart: unless-stopped
    volumes:
      - redis_cache_data:/data
    networks:
      - university_erp_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Queue
  redis-queue:
    image: redis:7-alpine
    container_name: university_erp_redis_queue
    restart: unless-stopped
    volumes:
      - redis_queue_data:/data
    networks:
      - university_erp_network

  # Redis Socketio
  redis-socketio:
    image: redis:7-alpine
    container_name: university_erp_redis_socketio
    restart: unless-stopped
    volumes:
      - redis_socketio_data:/data
    networks:
      - university_erp_network

  # Frappe/ERPNext Backend
  frappe:
    build:
      context: .
      dockerfile: Dockerfile.frappe
    container_name: university_erp_frappe
    restart: unless-stopped
    depends_on:
      mariadb:
        condition: service_healthy
      redis-cache:
        condition: service_healthy
    environment:
      - FRAPPE_SITE=${FRAPPE_SITE:-university.localhost}
      - DB_HOST=mariadb
      - DB_PORT=3306
      - REDIS_CACHE=redis://redis-cache:6379
      - REDIS_QUEUE=redis://redis-queue:6379
      - REDIS_SOCKETIO=redis://redis-socketio:6379
      - DEVELOPER_MODE=1
    volumes:
      - frappe_sites:/home/frappe/frappe-bench/sites
      - frappe_logs:/home/frappe/frappe-bench/logs
      - ./apps:/home/frappe/frappe-bench/apps/custom_apps
    ports:
      - "8000:8000"
      - "9000:9000"
      - "6787:6787"
    networks:
      - university_erp_network
    tty: true
    stdin_open: true

  # Frappe Worker - Short
  frappe-worker-short:
    build:
      context: .
      dockerfile: Dockerfile.frappe
    container_name: university_erp_worker_short
    restart: unless-stopped
    depends_on:
      - frappe
    command: bench worker --queue short
    volumes:
      - frappe_sites:/home/frappe/frappe-bench/sites
      - frappe_logs:/home/frappe/frappe-bench/logs
      - ./apps:/home/frappe/frappe-bench/apps/custom_apps
    networks:
      - university_erp_network

  # Frappe Worker - Long
  frappe-worker-long:
    build:
      context: .
      dockerfile: Dockerfile.frappe
    container_name: university_erp_worker_long
    restart: unless-stopped
    depends_on:
      - frappe
    command: bench worker --queue long
    volumes:
      - frappe_sites:/home/frappe/frappe-bench/sites
      - frappe_logs:/home/frappe/frappe-bench/logs
      - ./apps:/home/frappe/frappe-bench/apps/custom_apps
    networks:
      - university_erp_network

  # Frappe Scheduler
  frappe-scheduler:
    build:
      context: .
      dockerfile: Dockerfile.frappe
    container_name: university_erp_scheduler
    restart: unless-stopped
    depends_on:
      - frappe
    command: bench schedule
    volumes:
      - frappe_sites:/home/frappe/frappe-bench/sites
      - frappe_logs:/home/frappe/frappe-bench/logs
    networks:
      - university_erp_network

  # Nginx Proxy (Optional - for production-like setup)
  nginx:
    image: nginx:alpine
    container_name: university_erp_nginx
    restart: unless-stopped
    depends_on:
      - frappe
    volumes:
      - ./config/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - frappe_sites:/var/www/sites:ro
    ports:
      - "80:80"
      - "443:443"
    networks:
      - university_erp_network

volumes:
  mariadb_data:
  redis_cache_data:
  redis_queue_data:
  redis_socketio_data:
  frappe_sites:
  frappe_logs:

networks:
  university_erp_network:
    driver: bridge
```

### Step 2.4: Create Dockerfile for Frappe

Create `Dockerfile.frappe`:

```dockerfile
FROM python:3.11-slim-bookworm

LABEL maintainer="University ERP Team"
LABEL description="Frappe Framework with ERPNext for University ERP"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FRAPPE_USER=frappe
ENV FRAPPE_BRANCH=version-15
ENV ERPNEXT_BRANCH=version-15
ENV BENCH_BRANCH=develop

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    sudo \
    mariadb-client \
    libmariadb-dev \
    libffi-dev \
    liblcms2-dev \
    libldap2-dev \
    libsasl2-dev \
    libtiff5-dev \
    libwebp-dev \
    redis-tools \
    rlwrap \
    tk8.6-dev \
    cron \
    xvfb \
    libfontconfig \
    wkhtmltopdf \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18.x
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn

# Create frappe user
RUN useradd -ms /bin/bash ${FRAPPE_USER} \
    && echo "${FRAPPE_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to frappe user
USER ${FRAPPE_USER}
WORKDIR /home/${FRAPPE_USER}

# Install bench
RUN pip install --user frappe-bench

# Add local bin to PATH
ENV PATH="/home/${FRAPPE_USER}/.local/bin:${PATH}"

# Initialize bench
RUN bench init frappe-bench \
    --frappe-branch ${FRAPPE_BRANCH} \
    --skip-redis-config-generation \
    --verbose

WORKDIR /home/${FRAPPE_USER}/frappe-bench

# Get ERPNext
RUN bench get-app erpnext --branch ${ERPNEXT_BRANCH}

# Get Education module (if separate)
RUN bench get-app education --branch ${ERPNEXT_BRANCH} || true

# Get HRMS module
RUN bench get-app hrms --branch ${ERPNEXT_BRANCH} || true

# Expose ports
EXPOSE 8000 9000 6787

# Default command
CMD ["bench", "start"]
```

### Step 2.5: Create MariaDB Configuration

Create `config/mariadb.cnf`:

```ini
[mysqld]
# Character Set
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# InnoDB Settings
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_log_buffer_size = 64M
innodb_file_per_table = 1
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT

# Connection Settings
max_connections = 500
max_allowed_packet = 256M
wait_timeout = 28800
interactive_timeout = 28800

# Query Cache (disabled for MariaDB 10.2+)
query_cache_type = 0

# Logging
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# Performance
tmp_table_size = 64M
max_heap_table_size = 64M
table_open_cache = 4000
sort_buffer_size = 4M
join_buffer_size = 4M
read_buffer_size = 2M
read_rnd_buffer_size = 8M

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
```

### Step 2.6: Create Environment File

Create `.env`:

```bash
# Database Configuration
DB_ROOT_PASSWORD=admin_secure_password_123
DB_NAME=university_erp
DB_USER=erpnext
DB_PASSWORD=erpnext_secure_password_123

# Frappe Configuration
FRAPPE_SITE=university.localhost
DEVELOPER_MODE=1
ADMIN_PASSWORD=admin123

# Redis Configuration
REDIS_CACHE_HOST=redis-cache
REDIS_QUEUE_HOST=redis-queue
REDIS_SOCKETIO_HOST=redis-socketio

# App Configuration
APP_NAME=university_ems
APP_TITLE="University ERP System"
```

---

## Part 3: VS Code DevContainer Setup

### Step 3.1: Create DevContainer Configuration

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "University ERP Development",
  "dockerComposeFile": ["../docker-compose.yml", "docker-compose.devcontainer.yml"],
  "service": "frappe",
  "workspaceFolder": "/home/frappe/frappe-bench",
  
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": "/home/frappe/frappe-bench/env/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
        "editor.tabSize": 4,
        "files.trimTrailingWhitespace": true,
        "files.insertFinalNewline": true,
        "[python]": {
          "editor.defaultFormatter": "ms-python.black-formatter"
        },
        "[javascript]": {
          "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "terminal.integrated.defaultProfile.linux": "bash"
      },
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint",
        "eamodio.gitlens",
        "ms-azuretools.vscode-docker",
        "humao.rest-client",
        "gruntfuggly.todo-tree",
        "streetsidesoftware.code-spell-checker",
        "yzhang.markdown-all-in-one",
        "redhat.vscode-yaml",
        "ms-python.isort",
        "tamasfe.even-better-toml",
        "mechatroner.rainbow-csv"
      ]
    }
  },
  
  "forwardPorts": [8000, 9000, 3306, 6379],
  
  "postCreateCommand": "bash .devcontainer/post-create.sh",
  
  "postStartCommand": "bash .devcontainer/post-start.sh",
  
  "remoteUser": "frappe",
  
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  
  "mounts": [
    "source=${localWorkspaceFolder}/apps,target=/home/frappe/frappe-bench/apps/custom_apps,type=bind,consistency=cached"
  ],
  
  "containerEnv": {
    "FRAPPE_SITE": "university.localhost",
    "DEVELOPER_MODE": "1"
  }
}
```

### Step 3.2: Create DevContainer Docker Compose Override

Create `.devcontainer/docker-compose.devcontainer.yml`:

```yaml
version: "3.8"

services:
  frappe:
    build:
      context: ..
      dockerfile: Dockerfile.frappe
    volumes:
      - ..:/workspace:cached
      - frappe-bench-env:/home/frappe/frappe-bench/env
      - frappe-node-modules:/home/frappe/frappe-bench/node_modules
    environment:
      - DEVELOPER_MODE=1
      - FRAPPE_SITE=university.localhost
    command: sleep infinity

volumes:
  frappe-bench-env:
  frappe-node-modules:
```

### Step 3.3: Create Post-Create Script

Create `.devcontainer/post-create.sh`:

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "University ERP - Post Create Setup"
echo "=========================================="

cd /home/frappe/frappe-bench

# Wait for database to be ready
echo "Waiting for database connection..."
while ! mariadb -h mariadb -u root -p${DB_ROOT_PASSWORD:-admin123} -e "SELECT 1" > /dev/null 2>&1; do
    echo "Waiting for MariaDB..."
    sleep 2
done
echo "Database is ready!"

# Configure bench to use Docker services
echo "Configuring bench..."
bench set-config -g db_host mariadb
bench set-config -g redis_cache "redis://redis-cache:6379"
bench set-config -g redis_queue "redis://redis-queue:6379"
bench set-config -g redis_socketio "redis://redis-socketio:6379"

# Create new site if it doesn't exist
SITE_NAME=${FRAPPE_SITE:-university.localhost}
if [ ! -d "sites/${SITE_NAME}" ]; then
    echo "Creating new site: ${SITE_NAME}"
    bench new-site ${SITE_NAME} \
        --db-host mariadb \
        --db-root-password ${DB_ROOT_PASSWORD:-admin123} \
        --admin-password ${ADMIN_PASSWORD:-admin123} \
        --no-mariadb-socket
    
    # Set as default site
    bench use ${SITE_NAME}
    
    # Install ERPNext
    echo "Installing ERPNext..."
    bench --site ${SITE_NAME} install-app erpnext
    
    # Install Education module
    echo "Installing Education module..."
    bench --site ${SITE_NAME} install-app education || true
    
    # Install HRMS module
    echo "Installing HRMS module..."
    bench --site ${SITE_NAME} install-app hrms || true
    
    # Enable developer mode
    bench --site ${SITE_NAME} set-config developer_mode 1
else
    echo "Site ${SITE_NAME} already exists"
    bench use ${SITE_NAME}
fi

# Build assets
echo "Building assets..."
bench build

# Setup Python virtual environment for IDE
if [ ! -f "env/bin/python" ]; then
    python -m venv env
fi

echo "=========================================="
echo "Setup Complete!"
echo "Access your site at: http://localhost:8000"
echo "=========================================="
```

### Step 3.4: Create Post-Start Script

Create `.devcontainer/post-start.sh`:

```bash
#!/bin/bash
set -e

echo "Starting University ERP Development Environment..."

cd /home/frappe/frappe-bench

# Ensure site is set
bench use ${FRAPPE_SITE:-university.localhost}

# Check for pending migrations
echo "Checking for pending migrations..."
bench --site ${FRAPPE_SITE:-university.localhost} migrate || true

# Start bench in background (optional - can also use bench start manually)
# bench start &

echo "=========================================="
echo "Development Environment Ready!"
echo ""
echo "Commands:"
echo "  bench start              - Start development server"
echo "  bench new-app <name>     - Create new Frappe app"
echo "  bench --site <site> migrate - Run migrations"
echo "  bench build              - Build frontend assets"
echo "  bench console            - Start Python console"
echo "=========================================="
```

Make scripts executable:
```bash
chmod +x .devcontainer/post-create.sh
chmod +x .devcontainer/post-start.sh
```

---

## Part 4: Initial Setup Checklist

### Pre-Setup Checklist

- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] VS Code installed with Remote Containers extension
- [ ] Git configured with user name and email
- [ ] Minimum 8GB RAM available
- [ ] 50GB+ free disk space
- [ ] Stable internet connection

### Setup Execution Checklist

```bash
# Step 1: Clone/Create project
cd ~/university-erp

# Step 2: Create all configuration files (as shown above)
# - docker-compose.yml
# - Dockerfile.frappe
# - config/mariadb.cnf
# - .env
# - .devcontainer/devcontainer.json
# - .devcontainer/docker-compose.devcontainer.yml
# - .devcontainer/post-create.sh
# - .devcontainer/post-start.sh

# Step 3: Build and start containers
docker compose build
docker compose up -d

# Step 4: Verify all containers are running
docker compose ps

# Step 5: Check logs for any errors
docker compose logs -f frappe

# Step 6: Access the application
# Open browser: http://localhost:8000
# Login: Administrator / admin123
```

### Post-Setup Verification Checklist

- [ ] All Docker containers running (check with `docker compose ps`)
- [ ] MariaDB accepting connections
- [ ] Redis services responding
- [ ] Frappe site accessible at http://localhost:8000
- [ ] Can login with admin credentials
- [ ] ERPNext modules visible in setup wizard
- [ ] Education module installed
- [ ] HRMS module installed
- [ ] Developer mode enabled
- [ ] Bench commands working inside container

---

## Part 5: Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Database Connection Failed
```bash
# Check MariaDB container status
docker compose logs mariadb

# Verify database credentials
docker exec -it university_erp_db mariadb -u root -p

# Reset database password if needed
docker compose down -v
docker compose up -d
```

#### Issue 2: Redis Connection Error
```bash
# Check Redis containers
docker compose logs redis-cache redis-queue redis-socketio

# Test Redis connection
docker exec -it university_erp_redis_cache redis-cli ping
```

#### Issue 3: Site Creation Failed
```bash
# Enter Frappe container
docker exec -it university_erp_frappe bash

# Check site status
cd /home/frappe/frappe-bench
bench --site university.localhost status

# Recreate site
bench drop-site university.localhost --force
bench new-site university.localhost --db-host mariadb --admin-password admin123
```

#### Issue 4: Build/Asset Errors
```bash
# Clear cache and rebuild
bench clear-cache
bench clear-website-cache
yarn install
bench build --force
```

#### Issue 5: Permission Errors
```bash
# Fix ownership
sudo chown -R frappe:frappe /home/frappe/frappe-bench

# Fix permissions
chmod -R 755 /home/frappe/frappe-bench/sites
```

---

## Part 6: Development Workflow

### Daily Development Commands

```bash
# Start development server
bench start

# Create a new custom app
bench new-app university_ems

# Install app on site
bench --site university.localhost install-app university_ems

# After code changes - rebuild
bench build

# After DocType changes - migrate
bench --site university.localhost migrate

# Clear cache
bench clear-cache

# Run tests
bench --site university.localhost run-tests --app university_ems

# Export fixtures
bench --site university.localhost export-fixtures

# Console for debugging
bench console
```

### Git Workflow for Custom Apps

```bash
cd apps/university_ems

# Initialize git (if new app)
git init
git remote add origin <repository-url>

# Development branch
git checkout -b feature/module-name

# Commit changes
git add .
git commit -m "feat: add hostel management module"

# Push changes
git push origin feature/module-name
```

---

## Next Steps

After completing this setup:

1. **Proceed to Document 02**: University ERP App Architecture & Module Integration
2. **Create the University EMS App**: Using `bench new-app university_ems`
3. **Configure Module Structure**: Set up app directory structure
4. **Begin Module Development**: Start with Priority 1 modules

---

**Document End**
