#!/bin/bash

# Exit on error, undefined variables, and ensure pipefail
set -euo pipefail

# Get the script directory for absolute path reference
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Define log file location using absolute path
LOG_FILE="$SCRIPT_DIR/logs/sveltekit_dev.log"
rm -f "$LOG_FILE"
touch "$LOG_FILE"

# Function to kill background processes on exit
cleanup() {
  echo "Shutting down server..."
  if [ -n "${SVELTEKIT_PID:-}" ]; then
    kill $SVELTEKIT_PID 2>/dev/null || true
  fi
}

# Register the cleanup function on script exit
trap cleanup EXIT INT TERM

# Start SvelteKit in the background with error handling and log capturing to both file and stdout
echo "Starting SvelteKit development server (logs in $LOG_FILE and stdout)..."
cd "$SCRIPT_DIR/sveltekit_hz"
npm run dev -- --open 2>&1 | tee -a "$LOG_FILE" &
SVELTEKIT_PID=$!

# Monitor the SvelteKit process
while true; do
  if ! kill -0 $SVELTEKIT_PID 2>/dev/null; then
    echo "SvelteKit server crashed or failed to start"
    exit 1
  fi
  sleep 1
done 