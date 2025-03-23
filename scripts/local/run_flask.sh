#!/usr/bin/env bash

# Set defaults
PROD_FRONTEND=false
DEBUG_MODE=1
FLASK_MODE="development"

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

# Setup environment variables based on mode
if [ "$PROD_FRONTEND" = true ]; then
    echo "Starting Flask in production frontend mode (for local testing)"
    # The new, more explicit environment variable name
    export LOCAL_CHECK_OF_PROD_FRONTEND=true
else
    echo "Starting Flask in development mode"
    unset LOCAL_CHECK_OF_PROD_FRONTEND
fi

# Run Flask with the appropriate settings
FLASK_DEBUG=$DEBUG_MODE FLASK_ENV=$FLASK_MODE FLASK_APP=api/index.py flask run --host=localhost --port $FLASK_PORT
