# Migrate from _secrets.py to .env

## Goal Statement
Migrate secrets management from `_secrets.py` to environment variables using `.env.local` for development and proper environment variables in production. This will:
- Follow security best practices by using environment variables
- Make it easier to manage different environments (dev/prod)
- Prepare for migration from Fly.io to Supabase/Render
- Keep non-secret configuration in Python files for better maintainability

## Progress/next steps

DONE: Setup Infrastructure
- [x] Add python-dotenv to requirements.txt
- [x] Create .env.local and .env.example files
- [x] Add .env.* to .gitignore and .cursorignore
- [x] Create central environment loading module (env_config.py)

TODO: Database Secrets Migration
- [x] Move database credentials to .env.local
- [ ] Update db_connection.py to use environment variables
- [ ] Update database initialization script
- [ ] Update database backup script (backup_proxy_production_db.sh)
- [ ] Update Fly.io database connection script (connect_to_fly_postgres_via_proxy.sh)
- [ ] Update conftest.py database test configuration
- [ ] Test database connectivity

TODO: API Keys Migration
- [x] Move API keys (Claude, OpenAI, ElevenLabs) to .env.local
- [ ] Update vocab_llm_utils.py to use environment variables
- [ ] Update audio_utils.py to use environment variables (ELEVENLABS_API_KEY, OPENAI_API_KEY)
- [ ] Update sourcefile_views.py to use environment variables (ELEVENLABS_API_KEY)
- [ ] Test API connectivity

TODO: Flask Configuration
- [x] Move Flask secret key to .env.local
- [ ] Update config.py to use environment variables
- [ ] Test Flask configuration

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
POSTGRES_DB_NAME=hellozenno_development  # Changes per environment
POSTGRES_DB_USER=postgres
POSTGRES_DB_PASSWORD=your_password_here
POSTGRES_HOST=localhost  # Changes per environment
POSTGRES_PORT=5432

# API Keys
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Flask
FLASK_SECRET_KEY=your_secret_key_here
```

### Key Decisions
1. Using `.env.local` instead of `.env` to be explicit about local development
2. Using same variable names across environments (e.g. POSTGRES_* instead of LOCAL_POSTGRES_*)
3. Keeping non-secret configuration in Python files
4. Using .env.example as schema for validation
5. Maintaining backwards compatibility during migration

### Testing Strategy
1. Test each group of secrets independently
2. Run database initialization script with new configuration
3. Test API endpoints that use external services
4. Run full test suite after each major change

### Rollback Plan
Since _secrets.py is in version control and the app has no active users, we'll keep _secrets.py until end of migration, then move it to to `obsolete/`

