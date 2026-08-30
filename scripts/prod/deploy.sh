#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

# Check if preview flag is provided
PREVIEW=false
TIMESTAMP=$(date +"%y%m%d_%H%M")
if [[ "$1" == "--preview" ]]; then
    PREVIEW=true
    echo_success "Starting Vercel preview deployment process... [$TIMESTAMP]"
else
    echo_success "Starting Vercel production deployment process... [$TIMESTAMP]"
fi

# Check git status once early to give immediate feedback
./scripts/git/check_git_status.sh

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

# deploy_backend.sh checks this too, but the sitemap step below shells out to
# python, so check it here to fail with a useful message rather than an
# ImportError.
if [ -z "$VIRTUAL_ENV" ]; then
    echo_error "Virtual environment is not activated. Please activate a virtual environment before deploying."
    exit 1
fi

# 1. Generate sitemaps (production only) - BEFORE anything ships.
#
# Sitemap generation is purely local: it reads the production DB and writes
# files into frontend/static/. Nothing about it needs the backend deployed
# first. It used to run inside deploy_frontend.sh, which meant any failure
# there - bad env, DB unreachable, localhost VITE_FRONTEND_URL - aborted the
# frontend deploy *after* the backend had already shipped, leaving a
# half-completed release. Running it up front means every sitemap failure mode
# aborts before anything is deployed.
#
# deploy_frontend.sh honours HZ_SITEMAPS_ALREADY_GENERATED and skips its own
# run, so invoking that script standalone still regenerates sitemaps.
if [[ "$PREVIEW" == "false" ]]; then
    echo "Generating sitemaps before deploying..."
    ./scripts/prod/generate_sitemaps.sh
    export HZ_SITEMAPS_ALREADY_GENERATED=1
fi

# 2. Deploy the API
echo "Deploying API to Vercel..."
./scripts/prod/deploy_backend.sh $([[ "$PREVIEW" == "true" ]] && echo "--preview")

# 3. Deploy the Frontend
echo "Deploying Frontend to Vercel..."
./scripts/prod/deploy_frontend.sh $([[ "$PREVIEW" == "true" ]] && echo "--preview")

if [[ "$PREVIEW" == "true" ]]; then
    echo_success "Preview deployments completed successfully!"
else
    echo_success "Production deployments completed successfully!"
fi
