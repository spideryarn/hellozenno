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

# 1. Deploy the API
echo "Deploying API to Vercel..."
./scripts/prod/deploy_backend.sh $([[ "$PREVIEW" == "true" ]] && echo "--preview")

# 2. Deploy the Frontend
echo "Deploying Frontend to Vercel..."
./scripts/prod/deploy_frontend.sh $([[ "$PREVIEW" == "true" ]] && echo "--preview")

if [[ "$PREVIEW" == "true" ]]; then
    echo_success "Preview deployments completed successfully!"
else
    echo_success "Production deployments completed successfully!"
fi 