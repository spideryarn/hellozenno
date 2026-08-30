#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

# Parse arguments.
#
# --skip-sitemaps is internal: on a full deploy the sitemaps have already been
# generated and validated inside deploy_backend.sh (after the migrations,
# before anything ships - see the call site there). It is deliberately an
# argument rather than an environment variable so that a stray exported value
# in the caller's shell cannot silently bypass the production sitemap gate.
PREVIEW=false
SKIP_SITEMAPS=false
for arg in "$@"; do
    case "$arg" in
        --preview) PREVIEW=true ;;
        --skip-sitemaps) SKIP_SITEMAPS=true ;;
        *)
            echo_error "Unknown argument: $arg (expected --preview and/or --skip-sitemaps)"
            exit 1
            ;;
    esac
done

if [[ "$PREVIEW" == "true" ]]; then
    echo "Starting Frontend preview deployment..."
else
    echo "Starting Frontend production deployment..."
fi

# Build the environment variables command line arguments.
#
# We pass each var via BOTH -e (runtime) AND -b (build-env, alias for
# --build-env) because SvelteKit inlines `$env/static/public` (any PUBLIC_*
# var) at build time. If a var is only passed as -e, the built bundle ships
# with the OLD value from Vercel's project-level env vars, even though SSR
# uses the new value. This bit us during the 2026-05-25 publishable-key
# rotation: see docs/conversations/260525a_supabase_pat_compromise_remediation.md
echo "Building environment variables for deployment..."
ENV_ARGS=""
if [ -f .env.prod ]; then
    echo "Loading environment variables from .env.prod..."
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ $line =~ ^#.*$ ]] && continue
        [[ -z $line ]] && continue

        # Extract key and value
        key=$(echo "$line" | cut -d'=' -f1)
        value=$(echo "$line" | cut -d'=' -f2-)

        # Add to environment arguments (both runtime and build)
        ENV_ARGS="$ENV_ARGS -e $key=\"$value\" -b $key=\"$value\""

        # Print environment variables being set
        echo "Setting environment variable: $key"
    done < .env.prod
else
    echo_error ".env.prod file not found"
    exit 1
fi

# Verify VITE_API_URL is included
if ! echo "$ENV_ARGS" | grep -q "VITE_API_URL"; then
    echo_error "VITE_API_URL not found in .env.prod"
    exit 1
fi

# Change to SvelteKit directory
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing SvelteKit dependencies..."
    npm install
fi

# echo "ENV_ARGS: $ENV_ARGS"
# exit 1


# Generate sitemaps before deployment for production only.
#
# On a full deploy these were already generated and validated by
# deploy_backend.sh, before anything shipped, and deploy.sh passes
# --skip-sitemaps so we don't repeat the work. Run standalone (no such
# argument) this script still generates and validates them itself.
if [[ "$PREVIEW" == "false" ]]; then
    cd .. # Return to project root
    if [[ "$SKIP_SITEMAPS" == "true" ]]; then
        echo "Sitemaps already generated and validated by deploy_backend.sh - skipping regeneration"
    else
        echo "Generating sitemaps for production deployment..."
        ./scripts/prod/generate_sitemaps.sh
    fi
    cd frontend # Go back to frontend directory
fi

# Deploy to Vercel with environment variables
if [[ "$PREVIEW" == "true" ]]; then
    echo "Deploying Frontend to Vercel preview environment..."
    DEPLOY_CMD="vercel $ENV_ARGS"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    
    # Extract the deployment URL from the output
    DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*\.vercel\.app' | head -1)
    echo_success "Frontend preview deployment completed at: $DEPLOYMENT_URL"
    echo "Note: Skipping health check for preview deployment"
else
    echo "Deploying Frontend to Vercel production..."
    DEPLOY_CMD="vercel --prod $ENV_ARGS"
    DEPLOY_OUTPUT=$(eval $DEPLOY_CMD)
    
    # Run health checks for production deployment
    echo "Waiting for Frontend deployment to complete..."
    sleep 30  # Initial wait for deployment to start
    
    # Use production URL for health check
    HEALTH_CHECK_URL="https://www.hellozenno.com"
    
    # Run health checks
    echo "Running Frontend health checks on $HEALTH_CHECK_URL..."
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_CHECK_URL")
    HTTP_HEADERS=$(curl -s -I "$HEALTH_CHECK_URL")
    
    if [[ $HTTP_STATUS -ge 200 && $HTTP_STATUS -lt 400 ]]; then
        echo_success "Frontend health check passed with status code $HTTP_STATUS!"
    else
        echo_error "Frontend health check failed! Status code: $HTTP_STATUS"
        echo "Response headers:"
        echo "$HTTP_HEADERS"
        exit 1
    fi
    
    echo_success "Frontend production deployment completed!"
fi 