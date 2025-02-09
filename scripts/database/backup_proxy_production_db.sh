#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/common.sh

# Load environment variables
source .env.local_with_fly_proxy
echo "Using Fly.io database via proxy"

# Configuration
BACKUP_DIR="backup"
TIMESTAMP=$(python3 -c "from gdutils.dt import dt_str; print(dt_str())")
BACKUP_FILE="${BACKUP_DIR}/production_backup_${TIMESTAMP}.sql"

# Create backups directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if proxy is running
if ! nc -z $POSTGRES_HOST $POSTGRES_PORT >/dev/null 2>&1; then
    echo_error "No PostgreSQL connection detected on port $POSTGRES_PORT"
    echo
    echo "Please run the proxy connection first:"
    echo "    ./scripts/database/connect_to_fly_postgres_via_proxy.sh"
    echo
    echo "Keep that running in a separate terminal, then run this backup script again."
    exit 1
fi

echo "Will create backup of production database at: ${BACKUP_FILE}"

# Get password from environment
PGPASSWORD=$POSTGRES_DB_PASSWORD \
    pg_dump -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_DB_USER $POSTGRES_DB_NAME > "${BACKUP_FILE}"

echo_success "Backup created at: ${BACKUP_FILE}" 