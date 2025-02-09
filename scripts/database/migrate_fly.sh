#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/common.sh

echo "Running migrations on Fly.io database..."

# Run migrations using fly ssh console with new CLI
fly ssh console -C "./utils/migrate.py migrate"

echo_success "Migrations completed successfully!" 