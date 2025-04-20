#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

echo "Setting Vercel environment variables for API project from .env.prod..."

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

# Change to API directory
cd backend

# # UNNECESSARY: Add VERCEL=1 environment variable
# echo "Setting VERCEL=1 for API project..."
# echo "1" | vercel env add VERCEL production --token $VERCEL_TOKEN --force
# echo "1" | vercel env add VERCEL preview --token $VERCEL_TOKEN --force

# Read .env.prod and set each secret for API project
# Only set the variables that are needed for the API
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ $line =~ ^#.*$ ]] && continue
    [[ -z $line ]] && continue
    
    # Extract key and value
    key=$(echo "$line" | cut -d'=' -f1)
    value=$(echo "$line" | cut -d'=' -f2-)
    
    # Skip frontend-specific variables
    [[ $key == VITE_* ]] && continue
    
    echo "Setting API environment variable: $key..."
    
    # Set as sensitive for API keys and secrets
    if [[ $key == *"API_KEY"* ]] || [[ $key == *"SECRET"* ]] || [[ $key == "DATABASE_URL" ]]; then
        echo "$value" | vercel env add "$key" production --sensitive --force
        echo "$value" | vercel env add "$key" preview --sensitive --force
    else
        echo "$value" | vercel env add "$key" production --force
        echo "$value" | vercel env add "$key" preview --force
    fi
done < ../.env.prod

echo_success "Environment variables set successfully for API project!" 
