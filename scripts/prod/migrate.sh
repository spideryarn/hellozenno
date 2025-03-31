#!/usr/bin/env bash

# Exit on error
set -e

# Get the absolute path to the project root, regardless of where the script is called from
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# Source common variables and functions
source "$PROJECT_ROOT/scripts/utils/common.sh"

# Source environment variables from .env.prod
if [ -f "$PROJECT_ROOT/.env.prod" ]; then
    echo "Loading environment variables from .env.prod..."
    source "$PROJECT_ROOT/scripts/utils/export_envs.sh" "$PROJECT_ROOT/.env.prod"
else
    echo_error "Missing .env.prod file"
    exit 1
fi

echo "Running migrations on Vercel database..."

# Run migrations with the proper Python path
# Check if we're in the api directory
if [ "$(basename "$(pwd)")" = "api" ]; then
    # If we're in the api directory, run the module directly
    VERCEL=1 python -m utils.migrate migrate
else
    # If we're in the project root or somewhere else, run it from the api directory
    cd "$PROJECT_ROOT/api"
VERCEL=1 python -m utils.migrate migrate
fi

echo_success "Migrations completed successfully!" 