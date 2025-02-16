Supabase Postgres database migration (from Fly.io)

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

TODO: Stage 0 - Git Setup
- [ ] Create and switch to `250216_Supabase_database_migration` branch
- [ ] Commit initial changes with message describing the migration plan

DONE: Stage 1 - Environment Variable Restructuring
- [x] Rename `.env.fly_cloud` to `.env.prod` to reflect its broader scope
- [x] Update `.env.example` to use DATABASE_URL
- [x] Remove old POSTGRES_* variables from all .env files
- [x] Update `.env.testing` with new structure
- [x] Update `.env.local` template
- [x] Document new environment structure in DATABASE.md
- [ ] Ask user to update `.env.prod` with real credentials
- [ ] Create `.env.local_to_prod` template for debugging production

TODO: Stage 2 - Database Connection Updates
- [ ] Update db_connection.py to use DATABASE_URL
- [ ] Configure transaction pooling (port 6543)
- [ ] Remove proxy-related code
- [ ] Add local-to-prod mode detection
- [ ] Update connection pool settings
- [ ] Update health check code
- [ ] Add tests for new connection logic
- [ ] Add safety checks for local-to-prod mode (e.g. read-only by default)

TODO: Stage 3 - Migration Process
- [ ] Create backup of Fly.io database
- [ ] Export schema and data
- [ ] Import to Supabase
- [ ] Verify data integrity
- [ ] Update migration scripts to use new connection
- [ ] Test migrations on Supabase

TODO: Stage 4 - Deployment Updates
- [ ] Update deploy.sh for new environment structure
- [ ] Update set_secrets script for new variables
- [ ] Test deployment process
- [ ] Document rollback procedure

TODO: Stage 5 - Testing & Verification
- [ ] Run full test suite
- [ ] Verify all database operations
- [ ] Test connection pooling under load
- [ ] Verify backup/restore procedures
- [ ] Document new database administration procedures
- [ ] Test local-to-prod debugging workflow

TODO: Stage 6 - Cleanup
- [ ] Remove obsolete Fly.io database code
- [ ] Remove proxy-related scripts
- [ ] Update documentation
- [ ] Archive old configuration files

TODO: Stage 7 - Git Completion
- [ ] Review all changes
- [ ] Ensure all tests pass
- [ ] Update CHANGELOG.md
- [ ] Create final commit with summary of all changes
- [ ] Merge `250216_Supabase_database_migration` into `main`
- [ ] Tag release (if appropriate)

