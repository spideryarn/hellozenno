# Migrate from _secrets.py to .env

## Goal Statement
Migrate secrets management from `_secrets.py` to environment variables using `.env.local` for development and proper environment variables in production. This will:
- Follow security best practices by using environment variables
- Make it easier to manage different environments (dev/prod)
- Prepare for migration from Fly.io to Supabase/Render
- Keep non-secret configuration in Python files for better maintainability
- Fail fast on missing environment variables using explicit validation

## Progress/next steps

DONE: Setup Infrastructure
- [x] Add python-dotenv to requirements.txt
- [x] Create .env.local and .env.example files
- [x] Add .env.* to .gitignore and .cursorignore
- [x] Create central environment loading module (env_config.py)

DONE: Refactor env_config.py
- [x] Implement explicit getenv() function with Pydantic type validation
  - [x] Use StrictStr as default type
  - [x] Use PositiveInt for port numbers
  - [x] Use SecretStr for sensitive values
- [x] Define all environment variables as module-level constants
- [x] Add validation to ensure all .env.example variables are processed
- [x] Implement environment detection functions
  - [x] is_testing() for test environment
  - [x] is_fly_cloud() for Fly.io production
  - [x] is_local_to_fly_proxy() for local development with proxy
- [x] Implement environment file selection
  - [x] choose_environment_file() to select correct .env file
  - [x] load_env_file() to load selected file
  - [x] Support for .env.testing, .env.local, .env.local_with_fly_proxy
- [x] Move database pool settings to env_config.py

DONE: API Keys Migration
- [x] Move API keys (Claude, OpenAI, ElevenLabs) to .env.local
- [x] Update vocab_llm_utils.py to use env_config
- [x] Update audio_utils.py to use env_config
- [x] Update sourcefile_views.py to use env_config
- [ ] Test API connectivity

DONE: Flask Configuration
- [x] Move Flask secret key to .env.local
- [x] Update config.py to use env_config
- [x] Test Flask configuration

DONE: Database Migration
- [x] Move database credentials to .env.local
- [x] Implement test database configuration
  - [x] Use .env.testing with safe defaults
  - [x] Add safety checks to ensure test database name
  - [x] Use env_config.getenv() for validation
- [x] Implement database connection configuration
  - [x] Move environment detection to env_config.py
  - [x] Use unified POSTGRES_* names across environments
  - [x] Move pool settings to env_config.py
  - [x] Remove redundant DB config from config.py
- [x] Discuss approach for bash scripts
  - [x] Update scripts to use appropriate .env files
  - [x] Rename set_secrets.sh to set_secrets_for_fly_cloud.sh
  - [x] Update deploy.sh to use new script name
  - [x] Update initialise_or_wipe_local_postgres.sh to use .env.local
  - [x] Update connect_to_fly_postgres_via_proxy.sh to use .env.local_with_fly_proxy
  - [x] Update backup_proxy_production_db.sh to use .env.local_with_fly_proxy

DONE: Documentation Updates
- [x] Update DATABASE.md to reflect new environment variable setup
- [x] Update DEVOPS.md to remove references to _secrets.py
- [x] Create documentation for setting up .env.local
- [x] Update deployment documentation for Supabase/Render

DONE: Tidying
- [x] Fix the linter errors in `env_config.py` (suppressed)
- [ ] Is there a way to tidy up `conftest.test_db` and how we feed it into `db_connection.init_db()`?

DONE: Create .env Files Structure
- [x] Create `.env.fly_cloud` (with 'xxx' placeholders, for user to fill in)
- [x] Update .env.example with all required variables
- [x] Check .env.local_with_fly_proxy is correct

DONE: Testing & API
- [x] Test API connectivity
- [x] Test all functionality end-to-end

DONE: Final Stages
- [x] Move AWS/Tigris credentials to environment variables (removed instead)
- [x] Remove _secrets.py (moved to obsolete/)

COMPLETED: Migration to .env
✓ All tasks completed except for optional tidying of test database configuration
✓ _secrets.py has been moved to obsolete/
✓ Documentation has been updated
✓ All environment files are in place
✓ AWS/Tigris configuration has been removed

The migration is now complete! 🎉

## Environment Files Structure

see .env.example (version controlled)

### .env.testing (version controlled)
Safe defaults for testing environment with test database name enforced.

### .env.local (not version controlled)
Local development configuration with actual API keys and local database credentials.

### .env.local_with_fly_proxy (not version controlled)
Local development configuration that connects to Fly.io database via proxy.

### .env.fly_cloud (not version controlled)
Production configuration template for Fly.io deployment.

## Key Decisions
1. Using `.env.local` instead of `.env` to be explicit about local development
2. Using same variable names across environments (e.g. POSTGRES_* instead of LOCAL_POSTGRES_*)
3. Keeping non-secret configuration in Python files
4. Using .env.example as schema for validation
5. Using explicit getenv() function that fails loudly on missing variables
6. No optional environment variables - all must be specified
7. Using Pydantic types for robust validation
8. Using .env.testing for test configuration with safe defaults
9. Using env_config.getenv() consistently across all environments
10. Setting Fly.io secrets during deployment using set_secrets.sh

## Deployment Process
1. Maintain `.env.fly_cloud` with production values
2. Use `scripts/fly/set_secrets.sh` to set Fly.io secrets during deployment
3. Script reads `.env.fly_cloud` and sets each secret using `fly secrets set`
4. Secrets are set before each deployment via deploy.sh

## Testing Strategy
1. Test each group of secrets independently
2. Run database initialization script with new configuration
3. Test API endpoints that use external services
4. Run full test suite after each major change

## Rollback Plan
Since _secrets.py is in version control and the app has no active users, we'll keep _secrets.py for now only as reference, then move it to `obsolete/`
