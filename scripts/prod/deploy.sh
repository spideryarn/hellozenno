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
    echo_success "Starting Vercel preview deployment process..."
else
    echo_success "Starting Vercel production deployment process..."
fi

# Skip Git checks for preview deployments
if [[ "$PREVIEW" == "false" ]]; then
    # Check Git repository status
    ./scripts/git/check_git_status.sh

    # 1. Run pre-deployment checks
    echo "Running pre-deployment checks..."

    # Check if we can import the application
    if ! python -c "from api.index import app"; then
        echo_error "Application import test failed"
        exit 1
    fi
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

# Build frontend assets for production (only for production deployment)
echo "Building frontend assets..."
./scripts/prod/build-frontend.sh

# Set environment variables from .env.prod
echo "Setting Vercel environment variables..."
# ./scripts/prod/set_secrets.sh

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

# Deploy to Vercel
if [[ "$PREVIEW" == "true" ]]; then
    echo "Deploying to Vercel preview environment with environment variables..."
    # don't display because it has secret variables in it
    # echo "Command: vercel $ENV_ARGS"
    DEPLOY_CMD="vercel $ENV_ARGS"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    # echo "$DEPLOY_OUTPUT"
else
    echo "Deploying to Vercel production..."
    DEPLOY_CMD="vercel --prod $ENV_ARGS"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    echo "$DEPLOY_OUTPUT"
    
    # Run health checks for production deployment
    echo "Waiting for deployment to complete..."
    sleep 30  # Initial wait for deployment to start
    
    # Extract the deployment URL from the output
    DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)
    
    # Run health checks
    echo "Running health checks on $DEPLOYMENT_URL..."
    if curl -s "$DEPLOYMENT_URL/sys/health-check" | grep -q "healthy"; then
        echo_success "Health check passed!"
    else
        echo_error "Health check failed!"
        exit 1
    fi
    
    # Run database migrations for production deployment
    echo "Running database migrations..."
    ./scripts/prod/migrate.sh
fi

# Extract the deployment URL from the output
DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)

if [[ "$PREVIEW" == "true" ]]; then
    echo_success "Preview deployment completed successfully!"
else
    echo_success "Production deployment completed successfully!"
fi

echo "You can now access the application at: $DEPLOYMENT_URL"
if [[ "$PREVIEW" == "true" ]]; then
    echo "Run the following commands to test the deployment:"
    echo "  curl $DEPLOYMENT_URL/vercel-test"
fi 