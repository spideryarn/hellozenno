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
    # Use export to ensure variables are available to subprocesses
    export $(grep -v '^#' "$PROJECT_ROOT/.env.prod" | xargs)
else
    echo_error "Missing .env.prod file"
    exit 1
fi

echo "Running migrations on Vercel database..."

# Always run from the backend directory where utils/migrate.py is located
cd "$PROJECT_ROOT/backend"

# Run migrations with environment variables properly set
VERCEL=1 python -m utils.migrate migrate

echo_success "Migrations completed successfully!" 