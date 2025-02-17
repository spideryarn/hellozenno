#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

# Load environment variables
source .env.local_to_prod
echo "Using direct Supabase connection"

# Configuration
BACKUP_DIR="backup"
TIMESTAMP=$(python3 -c "from gjdutils.dt import dt_str; print(dt_str())")
BACKUP_FILE="${BACKUP_DIR}/production_backup_${TIMESTAMP}.sql"

# Create backups directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "Will create backup of production database at: ${BACKUP_FILE}"

# Use DATABASE_URL for pg_dump
pg_dump "$DATABASE_URL" > "${BACKUP_FILE}"

echo_success "Backup created at: ${BACKUP_FILE}" 