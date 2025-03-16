#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

echo "Running migrations on Vercel database..."

# Run migrations directly with VERCEL=1 environment variable set only for this command
VERCEL=1 python -m utils.migrate migrate

echo_success "Migrations completed successfully!" 