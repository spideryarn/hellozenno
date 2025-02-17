#!/bin/bash
set -euo pipefail

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Create new directories if they don't exist
mkdir -p scripts/prod scripts/local scripts/utils

# Production scripts
mv scripts/fly/deploy.sh scripts/prod/
mv scripts/fly/set_secrets_for_fly_cloud.sh scripts/prod/set_secrets.sh
mv scripts/database/backup_proxy_production_db.sh scripts/prod/backup_db.sh
mv scripts/database/migrate_fly.sh scripts/prod/migrate.sh

# Local development scripts
mv scripts/database/migrate_local.sh scripts/local/migrate.sh
mv scripts/database/migrations_list.sh scripts/local/migrations_list.sh
mv scripts/database/initialise_or_wipe_local_postgres.sh scripts/local/init_db.sh
mv scripts/database/backup_local_db.sh scripts/local/backup_db.sh
mv scripts/run_local_flask_server.sh scripts/local/run_flask.sh

# Utility scripts
mv scripts/export_envs.sh scripts/utils/
mv scripts/count_lines.sh scripts/utils/
mv scripts/play_gong.sh scripts/utils/
mv scripts/common.sh scripts/utils/

# Remove obsolete scripts (they used the old Fly.io proxy approach)
rm -f scripts/database/migrate_fly_production_db_from_local_proxy.sh
rm -f scripts/database/connect_to_fly_postgres_via_proxy.sh

# Remove empty directories
rmdir scripts/fly 2>/dev/null || true
rmdir scripts/database 2>/dev/null || true

# Update references in deploy.sh
sed -i '' 's|scripts/fly/set_secrets_for_fly_cloud.sh|scripts/prod/set_secrets.sh|g' scripts/prod/deploy.sh
sed -i '' 's|scripts/database/migrate_fly.sh|scripts/prod/migrate.sh|g' scripts/prod/deploy.sh

# Update references in DEVOPS.md
sed -i '' 's|scripts/fly/deploy.sh|scripts/prod/deploy.sh|g' docs/DEVOPS.md
sed -i '' 's|scripts/database/initialise_or_wipe_local_postgres.sh|scripts/local/init_db.sh|g' docs/DEVOPS.md
sed -i '' 's|scripts/database/migrate_local.sh|scripts/local/migrate.sh|g' docs/DEVOPS.md
sed -i '' 's|scripts/database/migrations_list.sh|scripts/local/migrations_list.sh|g' docs/DEVOPS.md
sed -i '' 's|scripts/database/migrate_fly.sh|scripts/prod/migrate.sh|g' docs/DEVOPS.md

echo "Script reorganization complete!" 