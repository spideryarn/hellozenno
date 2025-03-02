#!/usr/bin/env bash

# Exit on error
set -e

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Source common variables and functions
source scripts/utils/common.sh

# Colors for output
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print warning messages (not in common.sh)
echo_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Function to print info messages (not in common.sh)
echo_info() {
    echo -e "$1"
}

echo_warning "WARNING: This script will run migrations from your LOCAL code against the PRODUCTION database!"
echo_warning "This should only be used for emergency fixes when you can't wait for a full deployment."
echo_warning "Make sure you have tested your migration changes locally first."
echo ""
echo "This will use the connection details from .env.local_to_prod to connect directly to the production database."
echo ""

# Check if .env.local_to_prod exists
if [ ! -f .env.local_to_prod ]; then
    echo_error "File .env.local_to_prod does not exist!"
    echo "Please create it with the production database connection details."
    exit 1
fi

# Load environment variables using gjdutils-export-envs
source gjdutils-export-envs .env.local_to_prod

# Verify we have the required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo_error "DATABASE_URL is not set in .env.local_to_prod!"
    exit 1
fi

# Set PYTHONPATH to include the current directory
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Run migrations in dry-run mode first
echo_info "Running migrations in dry-run mode..."
python -m utils.migrate migrate --dry-run

# Ask for confirmation
echo_warning "Would you like to proceed with the actual migration against the PRODUCTION database? [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    # Run the migrations
    echo_info "Running migrations on production database..."
    python -m utils.migrate migrate
    
    echo_success "Migrations completed successfully!"
    
    # Verify database state
    echo_info "Verifying database state..."
    if psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM lemma;" > /dev/null 2>&1; then
        echo_success "Database verification passed."
    else
        echo_error "Database verification failed!"
        exit 1
    fi
else
    echo_info "Migration cancelled."
    exit 0
fi 