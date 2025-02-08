#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Configuration
BACKUP_DIR="backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/hellozenno_development_${TIMESTAMP}.sql"

# Create backups directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if database exists
if ! psql -lqt | cut -d \| -f 1 | grep -qw "hellozenno_development"; then
    echo -e "${RED}Database 'hellozenno_development' does not exist!${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating backup of local development database...${NC}"
pg_dump hellozenno_development > "${BACKUP_FILE}"
echo -e "${GREEN}Backup created at: ${BACKUP_FILE}${NC}" 