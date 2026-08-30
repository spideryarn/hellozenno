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

# Sitemap generation (production only) happens inside deploy_backend.sh, not
# here. It is pinned between two ordering constraints - after the migrations,
# before anything ships - and that window only exists inside that script. See
# the call site there for the full reasoning. We just route the flags:
# --with-sitemaps tells the backend script to generate them, --skip-sitemaps
# stops the frontend script from redoing the work.
#
# These are arguments rather than exported env vars so that a stray value in
# the caller's shell can never change what a standalone run of either script
# does - in particular it can never bypass the production sitemap gate.
BACKEND_ARGS=()
FRONTEND_ARGS=()
if [[ "$PREVIEW" == "true" ]]; then
    BACKEND_ARGS+=(--preview)
    FRONTEND_ARGS+=(--preview)
else
    BACKEND_ARGS+=(--with-sitemaps)
    FRONTEND_ARGS+=(--skip-sitemaps)
fi

# 1. Deploy the API (and, for production, generate the sitemaps en route)
echo "Deploying API to Vercel..."
./scripts/prod/deploy_backend.sh "${BACKEND_ARGS[@]}"

# 2. Deploy the Frontend
echo "Deploying Frontend to Vercel..."
./scripts/prod/deploy_frontend.sh "${FRONTEND_ARGS[@]}"

if [[ "$PREVIEW" == "true" ]]; then
    echo_success "Preview deployments completed successfully!"
else
    echo_success "Production deployments completed successfully!"
fi
