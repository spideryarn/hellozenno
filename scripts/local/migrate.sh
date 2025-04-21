#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Source environment variables from .env.local
if [ -f .env.local ]; then
    echo -e "${YELLOW}Loading environment variables from .env.local${NC}"
    source .env.local
else
    echo -e "${RED}Error: .env.local file not found!${NC}"
    exit 1
fi

# Extract database connection details from DATABASE_URL
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}Error: DATABASE_URL not set in .env.local${NC}"
    exit 1
fi

# Parse DATABASE_URL to get database name
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

echo -e "${YELLOW}This script will migrate your database: ${DB_NAME}${NC}"

# Backup the database first
./scripts/local/backup_db.sh

# Change to backend directory before running migrations
cd backend

# Run migrations in dry-run mode first
echo -e "${YELLOW}Running migrations in dry-run mode...${NC}"
python -m utils.migrate migrate --dry-run

# Ask for confirmation
echo -e "${YELLOW}Would you like to proceed with the actual migration? [y/N]${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo -e "${YELLOW}Running migrations...${NC}"
    python -m utils.migrate migrate
    echo -e "${GREEN}Migrations completed successfully.${NC}"
    
    # Return to project root
    cd ..
    
    echo -e "${YELLOW}Verifying database state...${NC}"
    # Extract connection parameters from DATABASE_URL
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    # Use PGPASSWORD to avoid password prompt
    export PGPASSWORD="${DB_PASSWORD}"
    
    if psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT COUNT(*) FROM lemma;" > /dev/null 2>&1; then
        echo -e "${GREEN}Database verification passed.${NC}"
        unset PGPASSWORD
    else
        echo -e "${RED}Database verification failed!${NC}"
        unset PGPASSWORD
        exit 1
    fi
else
    # Return to project root if migration was cancelled
    cd ..
    echo -e "${YELLOW}Migration cancelled.${NC}"
    exit 0
fi 