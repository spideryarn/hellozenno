#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

echo_success "Starting Vercel deployment process..."

# Check Git repository status
./scripts/git/check_git_status.sh

# 1. Run pre-deployment checks
echo "Running pre-deployment checks..."

# Check if we can import the application
if ! python -c "from api.index import app"; then
    echo_error "Application import test failed"
    exit 1
fi

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo_error "Vercel CLI not found. Please install it with: npm i -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo_error "Not logged in to Vercel. Please run 'vercel login' first."
    exit 1
fi

# Build frontend assets for production
echo "Building frontend assets..."
./scripts/prod/build-frontend.sh

# Set environment variables from .env.prod
echo "Setting Vercel environment variables..."
./scripts/prod/set_secrets.sh

# Deploy to Vercel
echo "Deploying to Vercel..."
DEPLOY_OUTPUT=$(vercel --prod)
echo "$DEPLOY_OUTPUT"

# Extract the deployment URL from the output
DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)

# Run health checks
echo "Waiting for deployment to complete..."
sleep 30  # Initial wait for deployment to start

# Run health checks
echo "Running health checks on $DEPLOYMENT_URL..."
if curl -s "$DEPLOYMENT_URL/health" | grep -q "ok"; then
    echo_success "Health check passed!"
else
    echo_error "Health check failed!"
    exit 1
fi

echo_success "Deployment completed successfully!"
echo "You can now access the application at: $DEPLOYMENT_URL" 