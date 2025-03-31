#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

# Check if preview flag is provided
PREVIEW=false
if [[ "$1" == "--preview" ]]; then
    PREVIEW=true
    echo "Starting Frontend preview deployment..."
else
    echo "Starting Frontend production deployment..."
fi

# Set environment variables for Frontend deployment
echo "Setting Frontend environment variables..."
./scripts/prod/set_secrets_frontend.sh

# Change to SvelteKit directory
cd sveltekit_hz

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing SvelteKit dependencies..."
    npm install
fi

# Build is handled by Vercel automatically, no need to build locally

# Deploy to Vercel
if [[ "$PREVIEW" == "true" ]]; then
    echo "Deploying Frontend to Vercel preview environment..."
    DEPLOY_CMD="vercel"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
else
    echo "Deploying Frontend to Vercel production..."
    DEPLOY_CMD="vercel --prod"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    
    # Run health checks for production deployment
    echo "Waiting for Frontend deployment to complete..."
    sleep 30  # Initial wait for deployment to start
    
    # Extract the deployment URL from the output
    DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)
    
    # Run health checks
    echo "Running Frontend health checks on $DEPLOYMENT_URL..."
    if curl -s "$DEPLOYMENT_URL" -I | grep -q "200 OK"; then
        echo_success "Frontend health check passed!"
    else
        echo_error "Frontend health check failed!"
        exit 1
    fi
fi

# Extract the deployment URL from the output
DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)

if [[ "$PREVIEW" == "true" ]]; then
    echo_success "Frontend preview deployment completed at: $DEPLOYMENT_URL"
else
    echo_success "Frontend production deployment completed at: $DEPLOYMENT_URL"
fi 