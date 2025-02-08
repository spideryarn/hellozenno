#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/common.sh

# Configuration
BACKUP_DIR="backup"
TIMESTAMP=$(python3 -c "from gdutils.dt import dt_str; print(dt_str())")
BACKUP_FILE="${BACKUP_DIR}/production_backup_${TIMESTAMP}.sql"

# Create backups directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if proxy is running
if ! nc -z localhost 15432 >/dev/null 2>&1; then
    echo_error "No PostgreSQL connection detected on port 15432"
    echo
    echo "Please run the proxy connection first:"
    echo "    ./scripts/database/connect_to_fly_postgres_via_proxy.sh"
    echo
    echo "Keep that running in a separate terminal, then run this backup script again."
    exit 1
fi

echo "Will create backup of production database at: ${BACKUP_FILE}"

# Get password from _secrets.py without displaying it
PGPASSWORD="$( grep POSTGRES_DB_PASSWORD _secrets.py | cut -d'"' -f2 )" \
    pg_dump -h localhost -p 15432 -U hz_app_web hz_app_web > "${BACKUP_FILE}"

echo_success "Backup created at: ${BACKUP_FILE}" 