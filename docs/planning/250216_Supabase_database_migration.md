# Supabase Postgres database migration (from Fly.io)

see `docs/PROJECT_MANAGEMENT.md`

## Goal & Context
Migrate the database from Fly.io Postgres to Supabase Postgres while keeping Fly.io for webservers.

### Desired Behavior
1. All database operations should use a single DATABASE_URL connection string
2. Database connections should use Supabase's transaction pooling (port 6543)
3. Local development should be able to connect directly to production for debugging
4. Environment variables should be simplified and standardized
5. All existing data and functionality should be preserved

### Background
- Currently using Fly.io for both web servers and Postgres database
- Moving database to Supabase for better management and scalability
- Need to maintain compatibility with existing application code
- Have a working backup of production data from Feb 9th

## Principles
- Keep changes minimal and focused to one area at a time
- Test thoroughly at each stage with automated tests
- Maintain ability to rollback if needed
- Don't lose any data during migration
- Keep deployment process simple and documented
- No direct database changes outside of migrations
- No destructive operations without explicit user approval

## Actions

DONE: Initial Setup
- [x] Create and switch to `250216_Supabase_database_migration` branch
- [x] Commit initial changes with migration plan
- [x] Document rollback procedures in DATABASE.md

DONE: Environment Variable Restructuring
- [x] Rename `.env.fly_cloud` to `.env.prod` for broader scope
- [x] Update `.env.example` to use DATABASE_URL
- [x] Remove old POSTGRES_* variables from all .env files
- [x] Update `.env.testing` with new structure
- [x] Update `.env.local` template
- [x] Create `.env.local_to_prod` template for debugging
- [x] Update .gitignore to handle .env.* files correctly
- [x] Create sanitized .env.local_to_prod.example template
- [x] Document new environment structure in DATABASE.md

DONE: Database Connection Updates
- [x] Update db_connection.py to use DATABASE_URL
- [x] Configure transaction pooling (port 6543)
- [x] Remove proxy-related code
- [x] Add local-to-prod mode detection
- [x] Update env_config.py to use USE_LOCAL_TO_PROD instead of USE_FLY_POSTGRES_FROM_LOCAL_PROXY
- [x] Fix environment variable handling with gjdutils
- [x] Update all ENV_FLY_CLOUD references to ENV_PROD
- [x] Rename test_db_connection.py to verify_db_connection.py
- [x] Update connection pool settings
- [x] Update health check code
- [x] Add tests for new connection logic
- [x] Add safety checks for local-to-prod mode

DONE: Connection Verification
- [x] Move verify_db_connection.py to utils/
- [x] Test connection to Supabase - ✓ Connection successful!
- [x] Verify connection pooling works - ✓ Pool configured with max 20 connections
- [x] Confirm we can connect from local machine - ✓ Local to prod connection working

DONE: Database Migration
- [x] Create backup of Fly.io database
- [x] Import to Supabase

DONE: Deployment Process Updates
- [x] Update deploy.sh to remove proxy-related code and simplify for Supabase
- [x] Update set_secrets script for new DATABASE_URL
- [x] Remove connection pooling configuration (will use Supabase defaults)
- [x] Test deployment process end-to-end
- [x] Document new deployment steps in DEVOPS.md
- [x] Figure out how migrations will work, uncomment from deploy script

DONE: Cleanup
- [x] Remove obsolete Fly.io database code
- [x] Update database scripts to use direct Supabase connection (i.e. no proxy needed):
  - [x] Update backup_proxy_production_db.sh to backup_db.sh, now using direct Supabase connection
  - [x] Remove connect_to_fly_postgres_via_proxy.sh, migrate_fly_production_db_from_local_proxy.sh (already addressed by oneoff.reorganise_scripts.sh)
- [x] Update documentation to remove proxy references:
  - [x] DATABASE.md - updated backup commands and connection examples
  - [x] MIGRATIONS.md - removed Fly.io references, updated environment variables
  - [x] Updated all references to USE_FLY_POSTGRES_FROM_LOCAL_PROXY to USE_LOCAL_TO_PROD
- [x] Archive old configuration files if they exist

DONE: Document Script Reorganization
- [x] Move and rename scripts according to reorganise_scripts.sh:
  - [x] Production scripts to scripts/prod/
  - [x] Local development scripts to scripts/local/
  - [x] Utility scripts to scripts/utils/
- [x] Update documentation with new script paths:
  - [x] DEVOPS.md
  - [x] DATABASE.md
  - [x] MIGRATIONS.md
  - [x] Verified no script path updates needed in other docs

DONE: Final Testing & Documentation
- [x] Run full test suite
  - Updated test configuration to use DATABASE_URL instead of individual Postgres variables
  - Fixed environment variable conflicts between test and local-to-prod modes
  - All 123 tests passing, 4 skipped (frontend tests)
- [x] Update all database-related documentation
  - Verified no sensitive credentials in Git history
  - Old API keys and Fly.io credentials are obsolete
  - Supabase migration was done safely with no credential exposure
- [x] Document lessons learned and improvements made
  - Successfully migrated from individual POSTGRES_* variables to single DATABASE_URL
  - Improved environment separation (test/prod/local) with clear variable handling
  - Better security practices with credential management

DONE: Git Completion
- [x] Review all changes
- [x] Create final commit with summary of changes
- [x] Merge `250216_Supabase_database_migration` into `main`

