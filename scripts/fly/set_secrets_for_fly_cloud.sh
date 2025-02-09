#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/common.sh

echo "Setting Fly.io secrets from .env.fly_cloud..."

# Check if .env.fly_cloud exists
if [ ! -f .env.fly_cloud ]; then
    echo_error ".env.fly_cloud file not found"
    exit 1
fi

# Read .env.fly_cloud and set each secret
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ $line =~ ^#.*$ ]] && continue
    [[ -z $line ]] && continue
    
    # Extract key and value
    key=$(echo "$line" | cut -d'=' -f1)
    value=$(echo "$line" | cut -d'=' -f2-)
    
    echo "Setting $key..."
    # https://www.perplexity.ai/search/with-fly-secrets-do-i-need-to-EECazzUIS4Ky9UXUAfXTQg
    # --stage avoids a restart, and only sets the secret for machines started later
    fly secrets set --stage "$key=$value"    
done < .env.fly_cloud

echo_success "Secrets set successfully!" 