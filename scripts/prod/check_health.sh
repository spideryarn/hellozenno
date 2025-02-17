#!/usr/bin/env bash

# Exit on error
set -e

# Source common variables and functions
source "$(dirname "$0")/../common.sh"

echo "Running health checks against https://hz-app-web.fly.dev"
echo "Testing health check endpoint..."

# Try health check endpoint
curl -f "https://hz-app-web.fly.dev/health-check" || {
    echo_error "Health check failed"
    exit 1
}

echo_success "Health check passed!" 