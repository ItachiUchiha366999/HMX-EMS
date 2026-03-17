#!/bin/bash
# University ERP Backup Script
# Usage: ./backup.sh [backup_type]
# backup_type: full, db, files (default: full)

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_TYPE="${1:-full}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/university_erp}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $@"; }
info() { log "${GREEN}INFO: $@${NC}"; }
error() { log "${RED}ERROR: $@${NC}"; exit 1; }

# Create backup directory
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_NAME="university_erp_${BACKUP_TYPE}_${TIMESTAMP}"

info "Starting $BACKUP_TYPE backup: $BACKUP_NAME"

cd "$PROJECT_DIR"

# Database backup
backup_database() {
    info "Backing up database..."

    docker-compose exec -T mariadb mysqldump \
        -u root \
        -p"${MYSQL_ROOT_PASSWORD}" \
        --single-transaction \
        --routines \
        --triggers \
        "${MYSQL_DATABASE}" \
        > "$BACKUP_DIR/${BACKUP_NAME}_db.sql"

    gzip "$BACKUP_DIR/${BACKUP_NAME}_db.sql"
    info "Database backup: ${BACKUP_NAME}_db.sql.gz"
}

# Files backup
backup_files() {
    info "Backing up files..."

    docker-compose exec -T backend tar -czf - \
        /home/frappe/frappe-bench/sites/${SITE_NAME:-university.local}/private \
        /home/frappe/frappe-bench/sites/${SITE_NAME:-university.local}/public \
        > "$BACKUP_DIR/${BACKUP_NAME}_files.tar.gz"

    info "Files backup: ${BACKUP_NAME}_files.tar.gz"
}

# Full backup
backup_full() {
    backup_database
    backup_files

    # Create combined archive
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" \
        "${BACKUP_NAME}_db.sql.gz" \
        "${BACKUP_NAME}_files.tar.gz"

    # Remove individual files
    rm -f "${BACKUP_NAME}_db.sql.gz" "${BACKUP_NAME}_files.tar.gz"

    info "Full backup: ${BACKUP_NAME}.tar.gz"
}

# Execute backup based on type
case "$BACKUP_TYPE" in
    full)
        backup_full
        ;;
    db|database)
        backup_database
        ;;
    files)
        backup_files
        ;;
    *)
        error "Unknown backup type: $BACKUP_TYPE"
        ;;
esac

# Upload to S3 (if configured)
if [ -n "$S3_BUCKET" ]; then
    info "Uploading to S3..."
    aws s3 cp "$BACKUP_DIR/${BACKUP_NAME}"* "s3://${S3_BUCKET}/backups/" || warn "S3 upload failed"
fi

# Cleanup old backups
info "Cleaning up old backups..."
find "$BACKUP_DIR" -name "university_erp_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "university_erp_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/${BACKUP_NAME}"* 2>/dev/null | head -1 | cut -f1)

info "=========================================="
info "Backup completed successfully!"
info "Type: $BACKUP_TYPE"
info "Size: $BACKUP_SIZE"
info "Location: $BACKUP_DIR"
info "=========================================="

exit 0
