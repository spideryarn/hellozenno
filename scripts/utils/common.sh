#!/usr/bin/env bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print success messages
echo_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
echo_error() {
    echo -e "${RED}✗ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if required commands are available
for cmd in python; do
    if ! command_exists "$cmd"; then
        echo_error "Required command '$cmd' not found"
        exit 1
    fi
done 