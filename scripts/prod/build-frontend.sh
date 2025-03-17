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
cd ..

# Copy the Vite manifest to a more accessible location for Vercel
if [ -f "static/build/.vite/manifest.json" ]; then
  echo "Copying Vite manifest to static/build/ for better Vercel compatibility..."
  cp static/build/.vite/manifest.json static/build/manifest.json
else
  echo "Warning: Vite manifest not found at static/build/.vite/manifest.json"
fi

echo "Frontend build complete. Assets are in static/build/" 