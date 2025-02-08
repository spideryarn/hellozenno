#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/common.sh

# Parse arguments
DRY_RUN=0
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=1 ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Check if proxy is running
if ! nc -z localhost 15432 2>/dev/null; then
    echo_error "Proxy not running on port 15432"
    echo
    echo "Please start the proxy first with:"
    echo "    ./scripts/database/connect_to_fly_postgres_via_proxy.sh"
    exit 1
fi

# Set environment variable for db_connection.py
export USE_FLY_POSTGRES_FROM_LOCAL_PROXY=1

echo "Running migrations on production database via proxy..."
echo "Database: hz_app_web"
echo "Host: localhost:15432"
echo "User: hz_app_web"

if [ "$DRY_RUN" = "1" ]; then
    echo
    echo "DRY RUN - Would execute:"
    echo "    ./migrate.py migrate"
    echo
    echo "This would apply these migrations:"
    ./migrate.py list
else
    echo
    echo "Applying migrations..."
    ./migrate.py migrate
fi

# Clean up
unset USE_FLY_POSTGRES_FROM_LOCAL_PROXY 