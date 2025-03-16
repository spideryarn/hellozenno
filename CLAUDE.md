# HelloZenno Project Reference

To understand more about the purpose of the app, see `./README.md`

## Coding

- Make sure you read `.cursor/rules/gjdutils_rules/coding.mdc`

- **Backend (Flask + PostgreSQL)**
  - `index.py` - Main Flask application
  - `views/` - Route handlers and view functions
  - `utils/` - Helper functions
  - `db_models.py` - Database models (using Peewee ORM)
  - `migrations/` - Database migration scripts

- **Frontend (Svelte + TypeScript + Vite)**
  - Read `FRONTEND_INFRASTRUCTURE.md` before creating new frontend components
  - Use the `cursor-tools browser` commands for browser automation, testing, and debugging
  - folder structure:
    - `frontend/src/components/` - Svelte components
    - `frontend/src/entries/` - Entry points for different pages
    - `frontend/src/lib/` - Shared utilities
    - `templates/` - Jinja templates
    - `static/` - Static assets

## Development Guidelines

### Database
- see `DATABASE.md`, and also use the Supabase MCP (read-only)
- see `MIGRATIONS.md` before creating or running migrations

### Logging
- **Backend logs**: `/logs/flask_app.log` (managed by Loguru via LimitingFileWriter)
- **Frontend logs**: `/logs/vite_dev.log` (captured from Vite development server)
- Use the `loguru` library for Python logging: `from loguru import logger`
- Configuration in `utils/logging_utils.py` (backend) and `scripts/local/run_frontend_dev.sh` (frontend)
- Look at logs for debugging both Flask backend and Vite/Svelte frontend issues

### Frontend Components

### Browser Testing and Web Search with cursor-tools

The `cursor-tools` command provides powerful browser automation and web search capabilities:

#### Browser Automation
```bash
# Open a URL and capture page content, console logs, and network activity
cursor-tools browser open "https://example.com" --html

# Execute actions on a webpage using natural language instructions
cursor-tools browser act "Click Login" --url=https://example.com

# Observe interactive elements on a webpage and suggest actions
cursor-tools browser observe "interactive elements" --url=https://example.com

# Extract data from a webpage based on natural language instructions
cursor-tools browser extract "product names" --url=https://example.com/products

# Multi-step actions with state using the pipe separator
cursor-tools browser act "Click Login | Type 'user@example.com' into email | Click Submit" --url=https://example.com

# Connect to an existing Chrome instance
cursor-tools browser act "Click Submit" --connect-to=current  # Use existing page without reloading
cursor-tools browser act "Click Submit" --connect-to=reload-current  # Use existing page and refresh

# Take screenshots
cursor-tools browser open "https://example.com" --screenshot=screenshots/example.png

# Capture video of interactions
cursor-tools browser act "Fill form" --url=https://example.com --video=recordings/
```

**Important Notes on Browser Commands:**
- All browser commands are stateless by default - each starts with a fresh browser
- Do not use "wait" in browser act commands as it's currently disabled
- Use `--no-headless` to show browser UI for debugging

#### Web Search
```bash
# Get answers from the web using Perplexity AI
cursor-tools web "latest TypeScript features"

# For complex queries, save output to a local research file
cursor-tools web "Svelte component lifecycle" --save-to=local-research/svelte-lifecycle.md
```

#### Repository Context and Documentation
```bash
# Get context-aware answers about this repository
cursor-tools repo "explain authentication flow"

# Generate comprehensive documentation
cursor-tools doc --output docs/generated-docs.md

# For remote repositories
cursor-tools doc --from-github=username/repo --output local-docs/repo-name.md
```

#### GitHub Information
```bash
# Get the last 10 PRs or a specific PR
cursor-tools github pr
cursor-tools github pr 123

# Get the last 10 issues or a specific issue
cursor-tools github issue
cursor-tools github issue 456
```

#### Common Options for All Commands
```bash
# Save command output to a file
--save-to=<file path>

# Specify an alternative AI model
--model=<model name>

# Control response length
--max-tokens=<number>

# View all available options
--help
```

### Testing

see `.cursor/rules/gjdutils_rules/testing.mdc` and `docs/TESTING.md`

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/backend/test_file.py
pytest -k test_name
pytest -x --lf # Stop on first failure, then run last failed

# Run with verbose output
pytest -v
```

### Database
```bash
# Connect to local database with nice formatting
psql -d hellozenno_development -P pager=off -x auto

# One-off queries
psql -d hellozenno_development -P pager=off -A -t -c "SELECT * FROM table;"

# Backup local database
./scripts/local/backup_db.sh
```


## Common Commands

### Development
```bash
# Run Flask server - the user will always have this running in another terminal
source .env.local && ./scripts/local/run_flask.sh

# Run frontend development server (Vite) - the user will always have this running in another terminal
source .env.local && ./scripts/local/run_frontend_dev.sh

# Database migrations
./scripts/local/migrations_list.sh # List available migrations
./scripts/local/migrate.sh
```

### Deployment

see `scripts/`

```bash
# Deploy to production
./scripts/prod/deploy.sh

# Backup production database
./scripts/prod/backup_db.sh
```
