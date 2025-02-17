# Supabase Postgres database migration (from Fly.io)

see `docs/PROJECT_MANAGEMENT.md`

## Goal & Context
Migrate the database from Fly.io Postgres to Supabase Postgres while keeping Fly.io for webservers.

Key changes:
- Switch to single DATABASE_URL connection string
- Use Supabase's transaction pooling (port 6543)
- Remove proxy-related code (not needed with Supabase)
- Simplify environment variable structure
- Add direct local-to-prod connection mode for debugging

## Principles
- Keep changes minimal and focused
- Test thoroughly at each stage
- Maintain ability to rollback if needed
- Don't lose any data during migration
- Keep deployment process simple

## Actions

DONE: Git Setup
- [x] Create and switch to `250216_Supabase_database_migration` branch
- [x] Commit initial changes with message describing the migration plan

DONE: Environment Variable Restructuring
- [x] Rename `.env.fly_cloud` to `.env.prod` to reflect its broader scope
- [x] Update `.env.example` to use DATABASE_URL
- [x] Remove old POSTGRES_* variables from all .env files
- [x] Update `.env.testing` with new structure
- [x] Update `.env.local` template
- [x] Document new environment structure in DATABASE.md
- [x] Create `.env.local_to_prod` template for debugging production
- [x] Update .gitignore to handle .env.* files correctly (only track `.env.example`)
- [x] Create sanitized .env.local_to_prod.example template

DONE: Database Connection Updates
- [x] Update db_connection.py to use DATABASE_URL
- [x] Configure transaction pooling (port 6543)
- [x] Remove proxy-related code
- [x] Add local-to-prod mode detection
- [x] Update env_config.py to use USE_LOCAL_TO_PROD instead of USE_FLY_POSTGRES_FROM_LOCAL_PROXY
- [x] Fix environment variable handling with gjdutils
- [x] All references to ENV_FLY_CLOUD should be ENV_PROD
- [x] Rename test_db_connection.py to verify_db_connection.py
- [x] Update database connection test to use prod database (i.e. USE_LOCAL_TO_PROD)
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
- [ ] Create backup of Fly.io database
  - [ ] Use `backup_proxy_production_db.sh` to dump current production data
  - [ ] Verify backup integrity
  - [ ] Store backup in secure location
- [ ] Import to Supabase
  - [ ] Create tables in Supabase using migration scripts
  - [ ] Import data from Fly.io backup
  - [ ] Verify data integrity (row counts, sample records)
  - [ ] Test all database operations
- [ ] Document rollback procedure
  - [ ] Create rollback scripts
  - [ ] Test rollback process
  - [ ] Document in DATABASE.md

TODO: Deployment Updates
- [ ] Update deploy.sh for new environment structure
- [ ] Update set_secrets script for new variables
- [ ] Test deployment process
- [ ] Document rollback procedure

TODO: Testing & Verification
- [ ] Run full test suite
- [ ] Verify all database operations
- [ ] Test connection pooling under load
- [ ] Verify backup/restore procedures
- [ ] Document new database administration procedures
- [ ] Test local-to-prod debugging workflow

TODO: Cleanup
- [ ] Remove obsolete Fly.io database code
- [ ] Remove proxy-related scripts
  - [ ] Update backup_proxy_production_db.sh to use direct Supabase connection
  - [ ] Remove connect_to_fly_postgres_via_proxy.sh
  - [ ] Remove migrate_fly_production_db_from_local_proxy.sh
  - [ ] Update documentation to remove proxy references
- [ ] Update documentation
- [ ] Archive old configuration files

TODO: Git Completion
- [ ] Review all changes
- [ ] Ensure all tests pass
- [ ] Update CHANGELOG.md
- [ ] Create final commit with summary of all changes
- [ ] Merge `250216_Supabase_database_migration` into `main`
- [ ] Tag release (if appropriate)

## Current Issues to Address
1. Need to dump and import existing production data from Fly.io to Supabase
2. Need to verify data integrity after import
3. Need to test all database operations with imported data
4. Need to document and test rollback procedures

