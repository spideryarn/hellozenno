#!/bin/bash
# Generate sitemaps as part of the deployment process

set -e

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils/common.sh"

print_header "Generating sitemaps"

# Move to backend directory to ensure imports work correctly
cd "${PROJECT_ROOT}/backend"

# Run the sitemap generator
echo "Running sitemap generator..."
python -c "from utils.sitemap_generator import generate_sitemaps; generate_sitemaps()"

echo "✅ Sitemaps generated successfully"