#!/bin/bash

# Exit on error
set -e

# Check if we're in the project root
if [ ! -f "app.py" ]; then
  echo "Error: This script must be run from the project root directory"
  exit 1
fi

# Check if FLASK_PORT is set
if [ -z "$FLASK_PORT" ]; then
  echo "Error: FLASK_PORT environment variable is not set"
  exit 1
fi

# Create static/build directory if it doesn't exist
mkdir -p static/build

# Check if npm is installed
if ! command -v npm &> /dev/null; then
  echo "Error: npm is not installed. Please install Node.js and npm."
  exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
  echo "Installing frontend dependencies..."
  cd frontend && npm install && cd ..
fi

# Start Vite in parallel
echo "Starting development server..."

# Function to kill background processes on exit
cleanup() {
  echo "Shutting down server..."
  kill $VITE_PID 2>/dev/null
}

# Register the cleanup function on script exit
trap cleanup EXIT

# Start Vite in the background, passing FLASK_PORT
echo "Starting Vite server..."
cd frontend && FLASK_PORT=$FLASK_PORT npm run dev &
VITE_PID=$!

# Wait for process
wait $VITE_PID 