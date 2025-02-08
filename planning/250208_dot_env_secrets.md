# Migrate from _secrets.py to .env

## Goal Statement
Migrate secrets management from `_secrets.py` to environment variables using `.env.local` for development and proper environment variables in production. This will:
- Follow security best practices by using environment variables
- Make it easier to manage different environments (dev/prod)
- Prepare for migration from Fly.io to Supabase/Render
- Keep non-secret configuration in Python files for better maintainability
- Fail fast on missing environment variables using `os.environ[...]` for maximum explicitness

## Progress/next steps

DONE: Setup Infrastructure
- [x] Add python-dotenv to requirements.txt
- [x] Create .env.local and .env.example files
- [x] Add .env.* to .gitignore and .cursorignore
- [x] Create central environment loading module (env_config.py)

TODO: Refactor env_config.py (New)
- [ ] Implement new explicit getenv() function with Pydantic type validation
  - [ ] Use StrictStr as default type
  - [ ] Use PositiveInt for port numbers
  - [ ] Use SecretStr for sensitive values
- [ ] Define all environment variables as module-level constants
- [ ] Add validation to ensure all .env.example variables are processed
- [ ] Update existing os.environ/os.getenv usage to use env_config
  - [ ] Update db_connection.py
  - [ ] Update google_cloud_run_utils.py
  - [ ] Update fly_cloud_utils.py

TODO: API Keys Migration (Phase 1)
- [x] Move API keys (Claude, OpenAI, ElevenLabs) to .env.local
- [ ] Update vocab_llm_utils.py to use os.environ[]
- [ ] Update audio_utils.py to use os.environ[]
- [ ] Update sourcefile_views.py to use os.environ[]
- [ ] Test API connectivity

TODO: Flask Configuration (Phase 1)
- [x] Move Flask secret key to .env.local
- [ ] Update config.py to use os.environ[] (needs discussion)
- [ ] Test Flask configuration

TODO: Database Migration (Needs Discussion)
- [x] Move database credentials to .env.local
- [ ] Discuss approach for db_connection.py (handling defaults, test vs prod configs)
- [ ] Discuss approach for conftest.py (test database configuration)
- [ ] Discuss approach for bash scripts
- [ ] Implement agreed approach
- [ ] Test database connectivity

TODO: Documentation Updates
- [ ] Update DATABASE.md to reflect new environment variable setup
- [ ] Update DEVOPS.md to remove references to _secrets.py
- [ ] Create documentation for setting up .env.local
- [ ] Update deployment documentation for Supabase/Render

TODO: Testing & Cleanup
- [ ] Test all functionality end-to-end
- [ ] Remove _secrets.py
- [ ] Update deployment documentation for Supabase/Render

## Implementation Details

### Environment Variables Structure
```
# Database
POSTGRES_DB_NAME=hellozenno_development  # Required
POSTGRES_DB_USER=postgres               # Required
POSTGRES_DB_PASSWORD=your_password_here # Required
POSTGRES_HOST=localhost                 # Required
POSTGRES_PORT=5432                      # Required

# API Keys
CLAUDE_API_KEY=your_claude_api_key      # Required
OPENAI_API_KEY=your_openai_api_key      # Required
ELEVENLABS_API_KEY=your_elevenlabs_api_key  # Required

# Flask
FLASK_SECRET_KEY=your_secret_key_here   # Required
```

### Key Decisions
1. Using `.env.local` instead of `.env` to be explicit about local development
2. Using same variable names across environments (e.g. POSTGRES_* instead of LOCAL_POSTGRES_*)
3. Keeping non-secret configuration in Python files
4. Using .env.example as schema for validation
5. Maintaining backwards compatibility during migration
6. Using explicit getenv() function in env_config.py that fails loudly on missing variables
7. No optional environment variables - all must be specified
8. Exposing environment variables as typed module-level constants for better IDE support and clarity
9. Using Pydantic types for robust validation while keeping implementation simple

### Discussion Points for Database Migration
1. How to handle test vs production database configurations
2. Whether to allow any default values (e.g. localhost, default ports)
3. How to handle Fly.io specific configuration
4. Best approach for database scripts that need different behavior in different environments
5. Whether to keep LOCAL_ prefix for test database configuration

### Testing Strategy
1. Test each group of secrets independently
2. Run database initialization script with new configuration
3. Test API endpoints that use external services
4. Run full test suite after each major change

### Rollback Plan
Since _secrets.py is in version control and the app has no active users, we'll keep _secrets.py until end of migration, then move it to to `obsolete/`

