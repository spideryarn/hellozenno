#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

echo "Setting Vercel environment variables for Frontend project from .env.prod..."

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo_error ".env.prod file not found"
    exit 1
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

# Get Frontend project ID from .env.prod
FRONTEND_PROJECT_ID=$(grep "VERCEL_PROD_FRONTEND_DEPLOYMENT_ID" .env.prod | cut -d'=' -f2)
if [ -z "$FRONTEND_PROJECT_ID" ]; then
    echo_error "VERCEL_PROD_FRONTEND_DEPLOYMENT_ID not found in .env.prod"
    exit 1
fi

echo "Using Frontend Project ID: $FRONTEND_PROJECT_ID"

# Change to SvelteKit directory
cd frontend

# Add VERCEL=1 environment variable
echo "Setting VERCEL=1 for Frontend project..."
echo "1" | vercel env add VERCEL production --force
echo "1" | vercel env add VERCEL preview --force

# Read .env.prod and set each secret for Frontend project
# Only set the variables that are needed for the Frontend
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ $line =~ ^#.*$ ]] && continue
    [[ -z $line ]] && continue
    
    # Extract key and value
    key=$(echo "$line" | cut -d'=' -f1)
    value=$(echo "$line" | cut -d'=' -f2-)
    
    # Skip API-specific variables and only include frontend variables
    # For SvelteKit, we mainly care about VITE_* variables
    if [[ $key != VITE_* ]] && [[ $key != "VERCEL_PROD_FRONTEND_DEPLOYMENT_ID" ]]; then
        continue
    fi
    
    echo "Setting Frontend environment variable: $key..."
    
    # Set as sensitive for any secrets
    if [[ $key == *"SECRET"* ]]; then
        echo "$value" | vercel env add "$key" production --sensitive --force
        echo "$value" | vercel env add "$key" preview --sensitive --force
    else
        echo "$value" | vercel env add "$key" production --force
        echo "$value" | vercel env add "$key" preview --force
    fi
done < ../.env.prod

# Explicitly set the API URL for production deployment
echo "https://api.hellozenno.com" | vercel env add VITE_API_URL production --force
echo "https://api.hellozenno.com" | vercel env add VITE_API_URL preview --force

echo_success "Environment variables set successfully for Frontend project!" 