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

# Create static/build directory if it doesn't exist
mkdir -p static/build

echo "Building frontend for production..."

# Install dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
  echo "Installing frontend dependencies..."
  cd frontend && npm install && cd ..
fi

# Build the frontend
cd frontend && npm run build

echo "Frontend build complete. Assets are in static/build/" 