#!/bin/bash
# Generate sitemaps for local development

set -e

# Define project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils/common.sh"

print_header "Generating sitemaps locally"

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

# Run the sitemap generator. The localhost URLs this produces must never reach
# production - scripts/prod/generate_sitemaps.sh re-checks before deploying.
echo "Running sitemap generator..."
SITEMAP_ALLOW_LOCAL_URL=1 python -c "from utils.sitemap_generator import generate_sitemaps; generate_sitemaps()"

echo_success "Sitemaps generated successfully"