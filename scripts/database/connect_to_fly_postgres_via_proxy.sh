#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/common.sh

# Load environment variables
source .env.local_with_fly_proxy
echo "Using Fly.io database via proxy"

# Configuration
LOCAL_PORT=$LOCAL_POSTGRES_PORT
REMOTE_PORT=$REMOTE_POSTGRES_PORT
DB_NAME=$POSTGRES_DB_NAME
DB_USER=$POSTGRES_DB_USER
APP_NAME=$FLY_APP_NAME

echo "Using Fly.io database app: ${APP_NAME}"

# Function to cleanup background processes on exit
cleanup() {
    echo "Cleaning up..."
    # Kill any fly proxy processes for our port
    pkill -f "fly proxy ${LOCAL_PORT}:${REMOTE_PORT}" || true
    exit 0
}

# Register cleanup function to run on script exit
trap cleanup EXIT

# Check if port is already in use
if lsof -i :${LOCAL_PORT} > /dev/null 2>&1; then
    echo_error "Port ${LOCAL_PORT} is already in use"
    echo
    echo "This usually means a previous proxy session didn't clean up properly."
    echo "To fix, run this command:"
    echo "    pkill -f 'fly proxy ${LOCAL_PORT}:${REMOTE_PORT}'"
    echo "Or, if that doesn't work:"
    echo "    pkill -f fly; sudo lsof -i :15432"
    echo
    echo "Then try this script again."
    echo
    echo "If that doesn't work, you can:"
    echo "1. Wait a few moments for the port to be released"
    echo "2. Edit this script to use a different port"
    exit 1
fi

# Start proxy in background
echo "Starting Fly.io database proxy..."
fly proxy ${LOCAL_PORT}:${REMOTE_PORT} -a ${APP_NAME} &
PROXY_PID=$!

# Wait for proxy to be ready
echo "Waiting for proxy connection..."
for i in {1..10}; do
    if nc -z localhost ${LOCAL_PORT} 2>/dev/null; then
        echo "Proxy ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo_error "Proxy failed to start"
        exit 1
    fi
    sleep 1
done

# Show connection details
echo
echo "Connecting to database with:"
echo "  Host     : localhost (proxied to ${APP_NAME})"
echo "  Port     : ${LOCAL_PORT}"
echo "  Database : ${DB_NAME}"
echo "  User     : ${DB_USER}"
echo

# Get password from environment
PGPASSWORD=$POSTGRES_DB_PASSWORD \
    psql -h localhost -p ${LOCAL_PORT} -U ${DB_USER} ${DB_NAME}

# Note: Cleanup happens automatically via trap when you exit psql 