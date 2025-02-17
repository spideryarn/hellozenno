#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

# Check for unstaged changes
if ! git diff --quiet; then
    echo_error "Unstaged changes present"
    git --no-pager diff --stat
    exit 1
fi

# Check for staged but uncommitted changes
if ! git diff --cached --quiet; then
    echo_error "Uncommitted staged changes present"
    git --no-pager diff --cached --stat
    exit 1
fi

# Check for untracked files
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED" ]; then
    echo_error "Untracked files present:"
    echo "$UNTRACKED"
    exit 1
fi

echo_success "Git: clean" 