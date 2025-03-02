#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

echo_success "Starting deployment process..."

# Check Git repository status
./scripts/git/check_git_status.sh

# 1. Run pre-deployment checks
echo "Running pre-deployment checks..."

# Check if we can import the application
if ! python -c "from app import app"; then
    echo_error "Application import test failed"
    exit 1
fi

# Check if we're deploying to the correct app
CURRENT_APP=$(fly status --json | jq -r .Name)
if [ "$CURRENT_APP" != "hz-app-web" ]; then
    echo_error "Wrong Fly.io app: $CURRENT_APP (expected: hz-app-web)"
    exit 1
fi

# Build frontend assets for production
echo "Building frontend assets..."
./scripts/prod/build-frontend.sh

# Set secrets from .env.prod
echo "Setting Fly.io secrets..."
./scripts/prod/set_secrets.sh

# Deploy to Fly.io using fly.toml configuration
echo "Deploying to Fly.io..."
fly deploy \
    --local-only \
    --config fly.toml \
    --auto-confirm \
    --no-cache

# Wait for deployment to complete and run health checks
echo "Waiting for deployment to complete..."
sleep 60  # Initial wait for deployment to start

# Run migrations
./scripts/prod/migrate.sh

# Run health checks
./scripts/prod/check_health.sh

echo_success "Deployment completed successfully!"
echo "You can now access the application at: https://hz-app-web.fly.dev" 