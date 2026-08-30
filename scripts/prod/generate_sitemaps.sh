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

# Note: sitemap.xml is overwritten by the generator, so don't delete it up front -
# a failed run would otherwise leave the repo with no sitemap index at all.

# Move to backend directory to ensure imports work correctly
cd "${PROJECT_ROOT}/backend"

# Load production environment variables. `.env.prod` uses bare assignments, so
# `set -a` is required: without it they stay shell-local, the Python child never
# sees them, and env_config falls back to .env.local - localhost URLs AND the
# local database.
set -a
source "${PROJECT_ROOT}/.env.prod"
# .env.prod pins USE_LOCAL_TO_PROD=0, which would make env_config load .env.local
# anyway. Override it after sourcing so decide_environment_file() picks .env.prod
# and the DB connection requires SSL.
USE_LOCAL_TO_PROD=1
set +a

# Never let a local opt-out leak into the production path
unset SITEMAP_ALLOW_LOCAL_URL

# Run the sitemap generator
echo "Running sitemap generator..."
python -c "from utils.sitemap_generator import generate_sitemaps; generate_sitemaps()"

# Belt-and-braces: generate_sitemaps() logs-and-swallows most failures, so a stale
# sitemap.xml left behind by scripts/local/ could otherwise get uploaded to Vercel.
if [ ! -f "${FRONTEND_STATIC_DIR}/sitemap.xml" ]; then
    echo_error "sitemap.xml was not generated - refusing to deploy"
    exit 1
fi
if grep -rqE "localhost|127\.0\.0\.1|0\.0\.0\.0" "${FRONTEND_STATIC_DIR}/sitemap.xml" "${SITEMAPS_DIR}"; then
    echo_error "Generated sitemaps still contain a local URL - refusing to deploy"
    exit 1
fi

echo_success "Sitemaps generated successfully"