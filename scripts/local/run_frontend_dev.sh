#!/bin/bash

# Exit on error, undefined variables, and ensure pipefail
set -euo pipefail

# Check if we're in the project root
if [ ! -f "api/index.py" ]; then
  echo "Error: This script must be run from the project root directory"
  exit 1
fi

# Check if FLASK_PORT is set
if [ -z "${FLASK_PORT:-}" ]; then
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

# Function to kill background processes on exit
cleanup() {
  echo "Shutting down server..."
  if [ -n "${VITE_PID:-}" ]; then
    kill $VITE_PID 2>/dev/null || true
  fi
}

# Register the cleanup function on script exit
trap cleanup EXIT INT TERM

# Set NODE_ENV to development explicitly
export NODE_ENV=development

# Define log file location and max lines
MAX_LINES=200
LOG_FILE="../logs/vite_dev.log"

# Function to limit log file size
limit_log_file() {
  if [ -f "$LOG_FILE" ]; then
    echo "Limiting $LOG_FILE to $MAX_LINES lines..."
    tail -n $MAX_LINES "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
  fi
}

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Limit log file size before starting
limit_log_file

# Start Vite in the background with error handling and log capturing
echo "Starting Vite development server (logs in $LOG_FILE)..."
cd frontend
npm run dev >> "$LOG_FILE" 2>&1 &
VITE_PID=$!

# Monitor the Vite process
while true; do
  if ! kill -0 $VITE_PID 2>/dev/null; then
    echo "Vite server crashed or failed to start"
    exit 1
  fi
  sleep 1
done 