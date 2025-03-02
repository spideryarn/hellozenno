#!/usr/bin/env bash

# Check if FLASK_PORT is set
if [ -z "$FLASK_PORT" ]; then
    echo "Error: FLASK_PORT environment variable is not set"
    exit 1
fi

# Run Flask in debug and development mode
FLASK_DEBUG=1 FLASK_ENV=development FLASK_APP=app.py flask run --host=localhost --port $FLASK_PORT
