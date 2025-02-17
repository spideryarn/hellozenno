#!/bin/bash
set -euo pipefail

# Don't ever run this script without explicitly being asked, or on production.

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up local PostgreSQL database for HelloZenno...${NC}"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL client (psql) not found. Please install PostgreSQL first.${NC}"
    exit 1
fi

# Check if PostgreSQL server is running
if ! pg_isready &> /dev/null; then
    echo -e "${RED}PostgreSQL server is not running. Please start it first.${NC}"
    exit 1
fi

# Load environment variables
source .env.local
echo "Using database: $POSTGRES_DB_NAME"

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB_NAME"; then
    echo -e "${RED}Database $POSTGRES_DB_NAME already exists. Skipping creation.${NC}"
    read -p "Do you want to drop and recreate it? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Dropping database $POSTGRES_DB_NAME..."
        dropdb "$POSTGRES_DB_NAME"
        createdb "$POSTGRES_DB_NAME"
        echo -e "${GREEN}Database $POSTGRES_DB_NAME recreated.${NC}"
    fi
else
    createdb "$POSTGRES_DB_NAME"
    echo -e "${GREEN}Database $POSTGRES_DB_NAME created.${NC}"
fi

# Run migrations - migrations/MIGRATIONS.md for instructions
echo -e "\nRunning migrations..."

echo -e "\n${GREEN}Setup complete!${NC}"