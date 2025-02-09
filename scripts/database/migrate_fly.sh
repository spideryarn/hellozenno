#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/common.sh

echo "Running migrations on Fly.io database..."

# Run migrations using fly ssh console with new CLI, ensuring PYTHONPATH includes project root
fly ssh console -C "PYTHONPATH=/app python /app/utils/migrate.py migrate"

echo_success "Migrations completed successfully!" 