#!/bin/bash

# Exit on error
set -e

# Check if we're in the project root
if [ ! -f "api/index.py" ]; then
  echo "Error: This script must be run from the project root directory"
  exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
  echo "Error: npm is not installed. Please install Node.js and npm."
  exit 1
fi

echo "Building SvelteKit frontend for production..."

# Change to SvelteKit directory
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "Installing SvelteKit dependencies..."
  npm install
fi

# Build the SvelteKit frontend
echo "Running npm build..."
npm run build

echo "SvelteKit frontend build complete."

# Note: With SvelteKit and the Vercel adapter, Vercel will handle the build process
# during deployment. This script is mostly for local testing and verification. 