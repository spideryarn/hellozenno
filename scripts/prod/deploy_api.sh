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
    echo "Starting API preview deployment..."
else
    echo "Starting API production deployment..."
fi

# Generate TypeScript route definitions for the frontend to use
echo "Generating TypeScript route definitions..."
FLASK_APP=api.index flask generate-routes-ts

# Run pre-deployment checks for production
if [[ "$PREVIEW" == "false" ]]; then
    echo "Running API pre-deployment checks..."
    
    # Check if we can import the application
    if ! python -c "from api.index import app"; then
        echo_error "API application import test failed"
        exit 1
    fi
fi

# Set environment variables for API deployment
echo "Setting API environment variables..."
./scripts/prod/set_secrets_api.sh

# Change to API directory
cd api

# Deploy to Vercel
if [[ "$PREVIEW" == "true" ]]; then
    echo "Deploying API to Vercel preview environment..."
    DEPLOY_CMD="vercel"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
else
    # Run database migrations for production deployment
    echo "Running database migrations..."
    ./scripts/prod/migrate.sh

    echo "Deploying API to Vercel production..."
    DEPLOY_CMD="vercel --prod"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    
    # Run health checks for production deployment
    echo "Waiting for API deployment to complete..."
    sleep 30  # Initial wait for deployment to start
    
    # Extract the deployment URL from the output
    DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)
    
    # Run health checks
    echo "Running API health checks on $DEPLOYMENT_URL..."
    if curl -s "$DEPLOYMENT_URL/sys/health-check" | grep -q "healthy"; then
        echo_success "API health check passed!"
    else
        echo_error "API health check failed!"
        exit 1
    fi
fi

# Extract the deployment URL from the output
DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)

if [[ "$PREVIEW" == "true" ]]; then
    echo_success "API preview deployment completed at: $DEPLOYMENT_URL"
else
    echo_success "API production deployment completed at: $DEPLOYMENT_URL"
fi 