#!/usr/bin/env bash

# Exit on error
set -e

source ./scripts/utils/common.sh
# echo "Setting API environment variables..."
echo_warning "Skipping API environment variables..."
# ./scripts/prod/set_secrets_backend.sh

# Change to api directory
cd backend

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
# Change back to root directory before generating routes
cd ..
FLASK_APP=backend/api/index.py flask generate-routes-ts
# Go back to backend directory
cd backend

# Run pre-deployment checks for production
if [[ "$PREVIEW" == "false" ]]; then
    echo "Running API pre-deployment checks..."
    
    # Check if we can import the application
    if ! python -c "from api.index import app"; then
        echo_error "API application import test failed"
        exit 1
    fi
fi

# Build the environment variables command line arguments
echo "Building environment variables for deployment..."
ENV_ARGS=""
if [ -f .env.prod ]; then
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ $line =~ ^#.*$ ]] && continue
        [[ -z $line ]] && continue
        
        # Extract key and value
        key=$(echo "$line" | cut -d'=' -f1)
        value=$(echo "$line" | cut -d'=' -f2-)
        
        # Add to environment arguments
        ENV_ARGS="$ENV_ARGS -e $key=\"$value\""
    done < .env.prod
    
    # Add VERCEL=1
    ENV_ARGS="$ENV_ARGS -e VERCEL=1"
fi

# Deploy to Vercel - set the root option to the current directory
if [[ "$PREVIEW" == "true" ]]; then
    echo "Deploying API to Vercel preview environment..."
    DEPLOY_CMD="vercel $ENV_ARGS"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    
    # Extract the deployment URL from the output
    DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)
    echo_success "API preview deployment completed at: $DEPLOYMENT_URL"
    echo "Note: Skipping health check for preview deployment"
else
    # Run database migrations for production deployment
    echo "Skipping database migrations..."
    # echo "Running database migrations..."
    # ../scripts/prod/migrate.sh

    echo "Deploying API to Vercel production..."
    DEPLOY_CMD="vercel --prod $ENV_ARGS"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    
    # Extract the deployment URL from the output for logging
    DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)
    
    # Use production URL for health check
    HEALTH_CHECK_URL="https://api.hellozenno.com"
    
    # Run health checks
    echo "Waiting 10s to allow Vercel to deploy..."
    sleep 10

    echo "Running API health checks on $HEALTH_CHECK_URL..."
    if curl -s "$HEALTH_CHECK_URL/sys/health-check" | grep -q "healthy"; then
        echo_success "API health check passed!"
    else
        echo_error "API health check failed!"
        exit 1
    fi

    echo_success "API production deployment completed!"
fi 