#!/usr/bin/env bash

# Set defaults
PROD_FRONTEND=false
DEBUG_MODE=1
FLASK_MODE="development"

# should be run from PROJECT_ROOT, and *not* from backend/
if [ ! -f "backend/api/index.py" ]; then
    echo "Error: Not in project root"
    exit 1
fi

# Function to display usage information
function show_usage {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --prod-frontend   Run Flask with production frontend (built assets)"
    echo "  --help            Display this help message"
    echo ""
    echo "Environment variables:"
    echo "  FLASK_PORT        Required - Port for Flask to listen on"
    echo ""
    echo "Examples:"
    echo "  $0                      # Run in normal development mode"
    echo "  $0 --prod-frontend      # Run with production frontend for testing"
}

# Function to kill existing Flask servers
function kill_flask_servers {
    echo "Killing any existing Flask servers on port $FLASK_PORT..."
    lsof -ti:$FLASK_PORT | xargs kill -9 2>/dev/null || true
}

# Function to kill Vite dev server
function kill_vite_server {
    echo "Killing any running Vite development server..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prod-frontend)
            PROD_FRONTEND=true
            DEBUG_MODE=0
            FLASK_MODE="production"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if FLASK_PORT is set
if [ -z "$FLASK_PORT" ]; then
    echo "Error: FLASK_PORT environment variable is not set"
    echo ""
    show_usage
    exit 1
fi

# Install API requirements if Flask is not installed
if ! pip show flask > /dev/null 2>&1; then
    echo "Installing API requirements..."
    pip install -r api/requirements.txt
fi

# Install gjdutils in development mode if not already installed
if ! pip show gjdutils > /dev/null 2>&1; then
    echo "Installing gjdutils in development mode..."
    pip install -e api/gjdutils
fi

# Always kill existing Flask servers
kill_flask_servers

# Setup environment variables based on mode
if [ "$PROD_FRONTEND" = true ]; then
    echo "Starting Flask in production frontend mode (for local testing)"
    
    # Kill Vite dev server if running
    kill_vite_server
    
    # The new, more explicit environment variable name
    export LOCAL_CHECK_OF_PROD_FRONTEND=true
    
    # Ensure NODE_ENV is set to production
    export NODE_ENV=production
    
    echo "Building frontend assets..."
    # Run the build-frontend script
    ./scripts/prod/build-frontend.sh
    
    # Verify the build succeeded by checking for key files
    if [ ! -f "static/build/js/hz-components.es.js" ]; then
        echo "Error: Built assets not found. Frontend build may have failed."
        echo "Check static/build/ directory for missing files."
        exit 1
    fi
    
    echo "Frontend build successful. Running Flask with production assets..."
else
    echo "Starting Flask in development mode"
    unset LOCAL_CHECK_OF_PROD_FRONTEND
    export NODE_ENV=development
fi

# Ensure logs directory exists
mkdir -p logs

# Clear the log file
> logs/backend.log

# Run Flask with the appropriate settings and log to both file and screen using tee
FLASK_DEBUG=$DEBUG_MODE FLASK_ENV=$FLASK_MODE FLASK_APP=backend/api/index.py flask run --host=localhost --port $FLASK_PORT 2>&1 | tee logs/backend.log
