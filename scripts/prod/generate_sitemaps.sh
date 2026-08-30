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

# Note: sitemap.xml is deliberately NOT deleted here. It is moved aside below
# and restored if the run fails, so a failed run never leaves the repo without
# a sitemap index.

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

# Move the existing index aside so that "the generator wrote an index" can be
# tested by simple existence rather than by comparing timestamps. (A timestamp
# marker is not reliable: bash's -nt compares whole seconds, so a fast run
# would look stale and block the deploy for no reason.) update_sitemap_index()
# wraps its write in try/except, so without this a swallowed write error leaves
# the previous run's index sitting there looking perfectly valid.
INDEX="${FRONTEND_STATIC_DIR}/sitemap.xml"
INDEX_BACKUP="$(mktemp -t hz_sitemap_index)"
HAD_INDEX=false
if [ -f "${INDEX}" ]; then
    HAD_INDEX=true
    mv "${INDEX}" "${INDEX_BACKUP}"
fi

# On any failure, put the old index back rather than leaving the repo with no
# sitemap index at all. Note the generated per-language files have already been
# deleted above, so a restored index references files that are no longer on
# disk - but the deploy is aborted, so nothing ships, and the next successful
# run rewrites both.
restore_index_on_failure() {
    if [ "${HAD_INDEX}" = true ] && [ ! -f "${INDEX}" ]; then
        mv "${INDEX_BACKUP}" "${INDEX}"
        echo_warning "Restored the previous sitemap.xml (it is now stale - rerun before deploying)"
    fi
    rm -f "${INDEX_BACKUP}"
}
trap restore_index_on_failure EXIT

# Run the sitemap generator
echo "Running sitemap generator..."
python -c "from utils.sitemap_generator import generate_sitemaps; generate_sitemaps()"

# ---------------------------------------------------------------------------
# Output gate.
#
# generate_sitemaps() catches and logs almost every failure and still exits 0
# (per-language query errors return "" and are filtered out; even the index
# write is wrapped in try/except). So a zero exit status proves nothing, and
# these files are uploaded verbatim by `vercel deploy`. Checking only that an
# index exists and lacks a localhost URL is not enough: a run that generated
# nothing leaves the previous index in place, and a run whose queries all
# failed writes a valid-looking index listing only the static sitemap. Both
# passed the old gate. Verify the run actually produced what it should.
# ---------------------------------------------------------------------------
# 1+2. The index exists AND was written by this run. Because the previous one
#      was moved aside above, its mere presence proves the generator wrote it.
if [ ! -f "${INDEX}" ]; then
    echo_error "sitemap.xml was not written by this run - refusing to deploy"
    exit 1
fi

# 3. At least one generated per-language sitemap exists on disk. A run whose
#    content queries all failed produces none, having deleted the old ones.
GENERATED_COUNT=$(find "${SITEMAPS_DIR}" -name "sitemap-generated-*.xml" -type f | wc -l | tr -d ' ')
MIN_GENERATED="${SITEMAP_MIN_GENERATED_FILES:-1}"
if [ "${GENERATED_COUNT}" -lt "${MIN_GENERATED}" ]; then
    echo_error "Only ${GENERATED_COUNT} generated sitemap file(s), expected at least ${MIN_GENERATED} - refusing to deploy"
    echo_error "This usually means the content queries failed - check the generator output above."
    exit 1
fi

# 4. Every file the index points at actually exists on disk, and the index
#    references at least one generated sitemap (not just the static one).
INDEXED_GENERATED=0
MISSING=0
while IFS= read -r loc; do
    # <loc> holds an absolute URL; strip scheme+host to get a path under frontend/static/
    rel_path=$(echo "$loc" | sed -E 's|^https?://[^/]+/||')
    if [ ! -f "${FRONTEND_STATIC_DIR}/${rel_path}" ]; then
        echo_error "sitemap.xml references a file that does not exist: ${rel_path}"
        MISSING=$((MISSING + 1))
    fi
    case "$rel_path" in
        *sitemap-generated-*) INDEXED_GENERATED=$((INDEXED_GENERATED + 1)) ;;
    esac
done < <(grep -o '<loc>[^<]*</loc>' "${INDEX}" | sed -e 's|<loc>||' -e 's|</loc>||')

if [ "${MISSING}" -gt 0 ]; then
    echo_error "sitemap.xml references ${MISSING} missing file(s) - refusing to deploy"
    exit 1
fi
if [ "${INDEXED_GENERATED}" -lt 1 ]; then
    echo_error "sitemap.xml lists no generated sitemaps (static-only index) - refusing to deploy"
    exit 1
fi

# 5. Each generated sitemap actually contains URLs - catches a truncated write.
#    The generator skips writing a file entirely when a query returns nothing,
#    so an empty file on disk means a partial write, not an empty language.
while IFS= read -r f; do
    if ! grep -q '<loc>' "$f"; then
        echo_error "Generated sitemap contains no URLs: $f - refusing to deploy"
        exit 1
    fi
done < <(find "${SITEMAPS_DIR}" -name "sitemap-generated-*.xml" -type f)

# 6. No dev URLs leaked into the output.
if grep -rqE "localhost|127\.0\.0\.1|0\.0\.0\.0" "${INDEX}" "${SITEMAPS_DIR}"; then
    echo_error "Generated sitemaps still contain a local URL - refusing to deploy"
    exit 1
fi

echo_success "Sitemaps generated successfully (${GENERATED_COUNT} generated files, ${INDEXED_GENERATED} indexed)"
