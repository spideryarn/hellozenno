#!/usr/bin/env bash

# Exit on error
set -e

source ./scripts/utils/common.sh

# Resolve project root for reading shared files like .env.prod
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# echo "Setting API environment variables..."
echo_warning "Skipping API environment variables..."
# ./scripts/prod/set_secrets_backend.sh

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo_error "Virtual environment is not activated. Please activate a virtual environment before deploying."
    exit 1
fi
echo_success "Virtual environment is active: $VIRTUAL_ENV"

# Change to api directory
cd backend

# Parse arguments.
#
# --with-sitemaps is internal: deploy.sh passes it so sitemap generation happens
# at the one point in the sequence that satisfies both of its ordering
# constraints (see the call site further down). It has no effect on a preview
# deploy. It is an argument rather than an environment variable so that a stray
# exported value in the caller's shell cannot change what a standalone run does.
PREVIEW=false
WITH_SITEMAPS=false
for arg in "$@"; do
    case "$arg" in
        --preview) PREVIEW=true ;;
        --with-sitemaps) WITH_SITEMAPS=true ;;
        *)
            echo_error "Unknown argument: $arg (expected --preview and/or --with-sitemaps)"
            exit 1
            ;;
    esac
done

if [[ "$PREVIEW" == "true" ]]; then
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
ENV_FILE="$PROJECT_ROOT/.env.prod"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE..."
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ $line =~ ^#.*$ ]] && continue
        [[ -z $line ]] && continue

        # Extract key and value
        key=$(echo "$line" | cut -d'=' -f1)
        value=$(echo "$line" | cut -d'=' -f2-)

        # Add to environment arguments
        ENV_ARGS="$ENV_ARGS -e $key=\"$value\""
    done < "$ENV_FILE"

    # Add VERCEL=1
    ENV_ARGS="$ENV_ARGS -e VERCEL=1"
else
    echo_warning "Missing .env.prod at $ENV_FILE; proceeding without env injection"
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
    echo "Running database migrations..."
    ../scripts/prod/migrate.sh

    # Generate sitemaps HERE - yes, in the *backend* deploy script.
    #
    # By subject matter this belongs in deploy_frontend.sh: it writes files into
    # frontend/static/ that `vercel deploy` uploads with the frontend. It lives
    # here instead because two ordering constraints pin it, and they only
    # overlap at this exact point in the sequence:
    #
    #   * it queries the production database using THIS release's models, so it
    #     must run after the migrations above - which rules out doing it early
    #     in deploy.sh, before this script is even called;
    #   * a failure must abort before any code ships, so it must run before the
    #     `vercel --prod` below - which rules out deploy_frontend.sh, by which
    #     point the backend is already live and the release half-completed.
    #
    # If you are tempted to move this: the migrations are the reason it cannot
    # go earlier, and the backend deploy is the reason it cannot go later.
    # Moving migrations out of this script into deploy.sh would free it up, but
    # that would put the app-import check above after the migrations, letting a
    # broken build migrate the production database. That trade was considered
    # and rejected.
    #
    # deploy.sh passes --with-sitemaps here and --skip-sitemaps to
    # deploy_frontend.sh. A standalone backend deploy passes neither and leaves
    # sitemaps alone; a standalone frontend deploy generates its own.
    if [[ "$WITH_SITEMAPS" == "true" ]]; then
        echo "Generating sitemaps (after migrations, before anything ships)..."
        "${PROJECT_ROOT}/scripts/prod/generate_sitemaps.sh"
    fi

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