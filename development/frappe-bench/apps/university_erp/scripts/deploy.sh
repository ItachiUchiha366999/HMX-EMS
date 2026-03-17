#!/bin/bash
# University ERP Production Deployment Script
# Usage: ./deploy.sh [environment]
#
# NOTE: This script is for PRODUCTION deployment only.
# For development, use the devcontainer setup with VS Code.
#
# Prerequisites:
# - Docker and Docker Compose installed
# - .env file configured (copy from .env.example)

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-production}"
BACKUP_DIR="/var/backups/university_erp"
LOG_FILE="/var/log/university_erp/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message=$@
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "${GREEN}$@${NC}"; }
warn() { log "WARN" "${YELLOW}$@${NC}"; }
error() { log "ERROR" "${RED}$@${NC}"; exit 1; }

# Create necessary directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

info "Starting deployment for environment: $ENVIRONMENT"

# Load environment-specific config
if [ -f "$PROJECT_DIR/.env.$ENVIRONMENT" ]; then
    source "$PROJECT_DIR/.env.$ENVIRONMENT"
    info "Loaded environment config: .env.$ENVIRONMENT"
else
    warn "No environment config found, using defaults"
fi

# Pre-deployment checks
info "Running pre-deployment checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed"
fi

# Check disk space (need at least 5GB)
AVAILABLE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')
if [ "$AVAILABLE_SPACE" -lt 5 ]; then
    error "Insufficient disk space. Need at least 5GB, have ${AVAILABLE_SPACE}GB"
fi

info "Pre-deployment checks passed"

# Backup current state
info "Creating backup..."
BACKUP_NAME="backup_$(date '+%Y%m%d_%H%M%S')"

if docker-compose -f "$PROJECT_DIR/docker-compose.yml" ps | grep -q "university_erp"; then
    # Backup database
    docker-compose -f "$PROJECT_DIR/docker-compose.yml" exec -T mariadb \
        mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" "${MYSQL_DATABASE}" \
        > "$BACKUP_DIR/${BACKUP_NAME}_db.sql" 2>/dev/null || warn "Database backup failed"

    # Backup sites
    docker-compose -f "$PROJECT_DIR/docker-compose.yml" exec -T backend \
        tar -czf - /home/frappe/frappe-bench/sites \
        > "$BACKUP_DIR/${BACKUP_NAME}_sites.tar.gz" 2>/dev/null || warn "Sites backup failed"

    info "Backup created: $BACKUP_NAME"
fi

# Pull latest code (if git repo)
if [ -d "$PROJECT_DIR/.git" ]; then
    info "Pulling latest code..."
    cd "$PROJECT_DIR"
    git fetch origin
    git checkout "${GIT_BRANCH:-main}"
    git pull origin "${GIT_BRANCH:-main}"
fi

# Build Docker images
info "Building Docker images..."
cd "$PROJECT_DIR"
docker-compose build --no-cache

# Stop existing containers
info "Stopping existing containers..."
docker-compose down --remove-orphans

# Start services
info "Starting services..."
docker-compose up -d

# Wait for services to be healthy
info "Waiting for services to be ready..."
sleep 30

# Check service health
if ! docker-compose ps | grep -q "Up"; then
    error "Services failed to start"
fi

# Run migrations
info "Running database migrations..."
docker-compose exec -T backend bench --site "${SITE_NAME:-university.local}" migrate

# Build assets
info "Building assets..."
docker-compose exec -T backend bench build --app university_erp

# Clear cache
info "Clearing cache..."
docker-compose exec -T backend bench --site "${SITE_NAME:-university.local}" clear-cache

# Restart workers
info "Restarting workers..."
docker-compose restart scheduler worker-short worker-long

# Health check
info "Running health checks..."
sleep 10

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${HTTP_PORT:-80}/api/method/frappe.ping")
if [ "$HEALTH_CHECK" != "200" ]; then
    warn "Health check returned $HEALTH_CHECK, but deployment continues"
fi

# Cleanup old backups (keep last 7)
info "Cleaning up old backups..."
ls -t "$BACKUP_DIR"/backup_*.sql 2>/dev/null | tail -n +8 | xargs -r rm
ls -t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm

# Deployment complete
info "=========================================="
info "Deployment completed successfully!"
info "Environment: $ENVIRONMENT"
info "Site: ${SITE_NAME:-university.local}"
info "URL: https://${SITE_NAME:-localhost}"
info "=========================================="

# Post-deployment notification (if configured)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"University ERP deployed to $ENVIRONMENT\"}" \
        "$SLACK_WEBHOOK_URL" 2>/dev/null || true
fi

exit 0
