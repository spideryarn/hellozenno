#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}This script will migrate your local development database.${NC}"

# Check if database exists
if ! psql -lqt | cut -d \| -f 1 | grep -qw "hellozenno_development"; then
    echo -e "${RED}Database 'hellozenno_development' does not exist!${NC}"
    exit 1
fi

# Backup the database first
./scripts/local/backup_db.sh

# Run migrations in dry-run mode first
echo -e "${YELLOW}Running migrations in dry-run mode...${NC}"
POSTGRES_DB_NAME="hellozenno_development" python utils/migrate.py migrate --dry-run

# Ask for confirmation
echo -e "${YELLOW}Would you like to proceed with the actual migration? [y/N]${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo -e "${YELLOW}Running migrations...${NC}"
    POSTGRES_DB_NAME="hellozenno_development" python utils/migrate.py migrate
    echo -e "${GREEN}Migrations completed successfully.${NC}"
    
    echo -e "${YELLOW}Verifying database state...${NC}"
    # Add basic checks here - e.g. can we connect and query the database?
    if psql -d hellozenno_development -c "SELECT COUNT(*) FROM lemma;" > /dev/null 2>&1; then
        echo -e "${GREEN}Database verification passed.${NC}"
    else
        echo -e "${RED}Database verification failed!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Migration cancelled.${NC}"
    exit 0
fi 