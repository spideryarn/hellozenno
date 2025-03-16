#!/usr/bin/env bash

# Exit on error
set -e

# Source common variables and functions
source "$(dirname "$0")/../utils/common.sh"

echo "Running health checks against https://hellozenno.vercel.app"
echo "Testing health check endpoint..."

# Try health check endpoint
curl -f "https://hellozenno.vercel.app/sys/health-check" || {
    echo_error "Health check failed"
    exit 1
}

echo_success "Health check passed!" 