#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

echo_success "Starting Vercel preview deployment process..."

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

# Set environment variables from .env.prod
echo "Setting Vercel environment variables..."
./scripts/prod/set_secrets.sh

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

# Deploy to Vercel preview with environment variables
echo "Deploying to Vercel preview environment with environment variables..."
# don't display because it has secret variables in it
# echo "Command: vercel $ENV_ARGS"
DEPLOY_CMD="vercel $ENV_ARGS"
DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
# echo "$DEPLOY_OUTPUT"

# Extract the deployment URL from the output
DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)

echo_success "Preview deployment completed successfully!"
echo "You can now access the preview application at: $DEPLOYMENT_URL"
echo "Run the following commands to test the deployment:"
echo "  curl $DEPLOYMENT_URL/vercel-test"
echo "  curl $DEPLOYMENT_URL/debug-env" 