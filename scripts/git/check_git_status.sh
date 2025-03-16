#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

# Function to ask for confirmation
ask_confirmation() {
    local message=$1
    echo -e "${RED}$message${NC}"
    read -p "Do you want to proceed anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_error "Operation aborted by user"
        exit 1
    fi
    echo_success "Proceeding despite Git status issues"
}

git_dirty=false

# Check for unstaged changes
if ! git diff --quiet; then
    echo_error "Unstaged changes present"
    git --no-pager diff --stat
    git_dirty=true
fi

# Check for staged but uncommitted changes
if ! git diff --cached --quiet; then
    echo_error "Uncommitted staged changes present"
    git --no-pager diff --cached --stat
    git_dirty=true
fi

# Check for untracked files
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED" ]; then
    echo_error "Untracked files present:"
    echo "$UNTRACKED"
    git_dirty=true
fi

# If git is dirty, ask for confirmation
if [ "$git_dirty" = true ]; then
    ask_confirmation "Git status is dirty. This might cause issues."
else
    echo_success "Git: clean"
fi 