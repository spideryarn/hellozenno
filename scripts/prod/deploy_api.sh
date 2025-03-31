#!/usr/bin/env bash

# Exit on error
set -e

# Source common variables and functions
source scripts/utils/common.sh
# Set environment variables for API deployment
echo "Setting API environment variables..."
# ./scripts/prod/set_secrets_api.sh

# Change to api directory
cd api

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
FLASK_APP=index flask generate-routes-ts

# Run pre-deployment checks for production
if [[ "$PREVIEW" == "false" ]]; then
    echo "Running API pre-deployment checks..."
    
    # Check if we can import the application
    if ! python -c "from index import app"; then
        echo_error "API application import test failed"
        exit 1
    fi
fi

# Deploy to Vercel - set the root option to the current directory
if [[ "$PREVIEW" == "true" ]]; then
    echo "Deploying API to Vercel preview environment..."
    DEPLOY_CMD="vercel --cwd ."
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
else
    # Return to project root for migrations, then back to api for deployment
    cd ..
    
    # Run database migrations for production deployment
    echo "Running database migrations..."
    ./scripts/prod/migrate.sh
    
    # Return to API directory for deployment
    cd api

    echo "Deploying API to Vercel production..."
    DEPLOY_CMD="vercel --prod --cwd ."
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