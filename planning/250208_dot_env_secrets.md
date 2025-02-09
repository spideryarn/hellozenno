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

TODO: Documentation Updates
- [ ] Update DATABASE.md to reflect new environment variable setup
- [ ] Update DEVOPS.md to remove references to _secrets.py
- [ ] Create documentation for setting up .env.local
- [ ] Update deployment documentation for Supabase/Render

TODO: Tidying
- [ ] Fix the linter errors in `env_config.py`
- [ ] Is there a way to tidy up `conftest.test_db` and how we feed it into `db_connection.init_db()`?

TODO: Create .env Files Structure
- [ ] Create .env.fly_cloud (with 'xxx' placeholders, for user to fill in)
- [x] Update .env.example with all required variables
- [ ] Check .env.local_with_fly_proxy is correct

TODO: Testing & Cleanup
- [ ] Test all functionality end-to-end
- [ ] Remove _secrets.py
- [ ] Update deployment documentation for Supabase/Render



Accept
⌘Y

Reject
⌘N
dev
- Fail fast on missing environment variables using `os.environ[...]` for maximum explicitness
TODO: Refactor env_config.py (New)
- [ ] Implement new explicit getenv() function with Pydantic type validation
  - [ ] Use StrictStr as default type
  - [ ] Use PositiveInt for port numbers
  - [ ] Use SecretStr for sensitive values
- [ ] Define all environment variables as module-level constants
- [ ] Add validation to ensure all .env.example variables are processed
- [ ] Update existing os.environ/os.getenv usage to use env_config
  - [ ] Update db_connection.py (needs discussion)
  - [ ] Update fly_cloud_utils.py
TODO: API Keys Migration (Phase 1)
- [x] Move API keys (Claude, OpenAI, ElevenLabs) to .env.local
- [x] Update vocab_llm_utils.py to use env_config
- [x] Update audio_utils.py to use env_config
- [x] Update sourcefile_views.py to use env_config
- [ ] Test API connectivity

TODO: Flask Configuration (Phase 1)
- [ ] Update config.py to use os.environ[] (needs discussion)
- [ ] Test Flask configuration
TODO: Database Migration (Needs Discussion)
- [x] Discuss approach for conftest.py (test database configuration)
  - Use .env.testing with safe defaults
  - Simple safety check to ensure test database name
  - Allow environment variables to override if needed
  - Use env_config.getenv() for validation
- [x] Discuss approach for db_connection.py (handling defaults, test vs prod configs)
  - Move environment detection to env_config.py
  - Use unified POSTGRES_* names across environments
  - Move pool settings to config.py
  - Remove redundant DB config from config.py
  - Create .env.local_with_fly_proxy for proxy case
- [ ] Create new .env files structure
  - [ ] Update .env.example with all required variables
  - [ ] Create .env.local_with_fly_proxy template
  - [ ] Create .env.fly template (with 'xxx' placeholders)
- [ ] Implement agreed approach
  - [ ] Update env_config.py with environment detection
  - [ ] Update config.py (remove DB config, add pool settings)
  - [ ] Update db_connection.py to use new structure
- [ ] Test database connectivity
- [ ] Discuss approach for bash scripts

TODO: Documentation Updates
- [ ] Update DATABASE.md to reflect new environment variable setup
- [ ] Update DEVOPS.md to remove references to _secrets.py
- [ ] Create documentation for setting up .env.local
- [ ] Update deployment documentation for Supabase/Render

TODO: Tidying
- [ ] Fix the linter errors in `env_config.py`
- [ ] Is there a way to tidy up `conftest.test_db` and how we feed it into `db_connection.init_db()`?

TODO: Testing & Cleanup
- [ ] Test all functionality end-to-end
- [ ] Remove _secrets.py
- [ ] Update deployment documentation for Supabase/Render

TODO: Final Stages
- [ ] Move AWS/Tigris credentials to environment variables
- [ ] Test all functionality end-to-end
- [ ] Remove _secrets.py
- [ ] Update deployment documentation for Supabase/Render
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
