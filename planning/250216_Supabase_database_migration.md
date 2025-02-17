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

IN PROGRESS: Database Migration
- [x] Create backup of Fly.io database
  - [x] Use `backup_proxy_production_db.sh` to dump current production data
  - [x] Verify backup integrity
  - [x] Store backup in secure location at `/Users/greg/Dropbox/dev/experim/hellozenno/backup/production_backup_250209_0231_22.sql`
- [x] Import to Supabase
  - [x] Create `oneoff/load_supabase_from_prod_backup.py` script
  - [x] Run script to load backup into Supabase
  - [x] Verify data integrity:

TODO: Deployment Process Updates
- [ ] Update deploy.sh for new environment structure
- [ ] Update set_secrets script for new variables
- [ ] Test deployment process end-to-end
- [ ] Document new deployment steps in DEVOPS.md

TODO: Cleanup
- [ ] Remove obsolete Fly.io database code
- [ ] Update database scripts to use direct Supabase connection:
  - [ ] Update backup_proxy_production_db.sh
  - [ ] Remove connect_to_fly_postgres_via_proxy.sh
  - [ ] Remove migrate_fly_production_db_from_local_proxy.sh
- [ ] Update documentation to remove proxy references
- [ ] Archive old configuration files if they exist

TODO: Document Script Reorganization
- [ ] Update README.md with new script locations
- [ ] Update DATABASE.md to reflect new script structure
- [ ] Update MIGRATIONS.md with new paths
- [ ] Review and update any remaining documentation files for script path references
- [ ] Add note about script organization in CONTRIBUTING.md if it exists

TODO: Final Testing & Documentation
- [ ] Run full test suite again
- [ ] Test local-to-prod debugging workflow
- [ ] Update all database-related documentation
- [ ] Document lessons learned and improvements made

TODO: Git Completion (after user approval)
- [ ] Review all changes
- [ ] Create final commit with summary of changes
- [ ] Merge `250216_Supabase_database_migration` into `main`

## Current Status
- Environment and connection changes are complete and tested
- Have production backup from Feb 9th
- Ready to load backup into Supabase
- Need user approval before proceeding with database import

