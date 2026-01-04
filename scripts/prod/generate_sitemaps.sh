#!/bin/bash
# Generate sitemaps as part of the deployment process

set -e

# Define project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils/common.sh"

print_header "Generating sitemaps"

# Define paths
FRONTEND_STATIC_DIR="${PROJECT_ROOT}/frontend/static"
SITEMAPS_DIR="${FRONTEND_STATIC_DIR}/sitemaps"

# Create sitemaps directory if it doesn't exist
mkdir -p "${SITEMAPS_DIR}"

# Remove existing generated sitemap files (but keep static ones)
echo "Removing existing generated sitemap files..."
find "${FRONTEND_STATIC_DIR}" -name "sitemap-generated-*.xml" -type f -delete

# Also remove the main sitemap index (will be regenerated)
if [ -f "${FRONTEND_STATIC_DIR}/sitemap.xml" ]; then
    rm "${FRONTEND_STATIC_DIR}/sitemap.xml"
fi

# Move to backend directory to ensure imports work correctly
cd "${PROJECT_ROOT}/backend"

# Load production environment variables
source "${PROJECT_ROOT}/.env.prod"

# Run the sitemap generator
echo "Running sitemap generator..."
python -c "from utils.sitemap_generator import generate_sitemaps; generate_sitemaps()"

echo_success "Sitemaps generated successfully"