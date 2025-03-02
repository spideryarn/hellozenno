#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

echo "Running migrations on Fly.io database..."

# Run migrations using fly ssh console with new CLI
# Using bash -c to ensure we have a proper shell environment
fly ssh console -C "bash -c 'cd /app && python -m utils.migrate migrate'"

echo_success "Migrations completed successfully!" 