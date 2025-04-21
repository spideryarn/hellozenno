#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source environment variables from .env.local if not already set
if [ -z "${DATABASE_URL:-}" ] && [ -f .env.local ]; then
    echo -e "${YELLOW}Loading environment variables from .env.local${NC}"
    source .env.local
elif [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}Error: DATABASE_URL not set and .env.local file not found!${NC}"
    exit 1
fi

# Extract database connection details from DATABASE_URL
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

# Configuration
BACKUP_DIR="backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"

# Create backups directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Use PGPASSWORD to avoid password prompt
export PGPASSWORD="${DB_PASSWORD}"

# Check if database exists
if ! psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
    echo -e "${RED}Database '${DB_NAME}' does not exist!${NC}"
    unset PGPASSWORD
    exit 1
fi

echo -e "${YELLOW}Creating backup of database: ${DB_NAME}...${NC}"
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${DB_NAME}" > "${BACKUP_FILE}"
echo -e "${GREEN}Backup created at: ${BACKUP_FILE}${NC}"

# Clean up
unset PGPASSWORD 