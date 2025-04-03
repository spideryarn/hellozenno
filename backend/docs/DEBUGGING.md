# Debugging

see `docs/DATABASE.md` for info on how to inspect the database

see `docs/FRONTEND_DEBUGGING.md`

see `.cursor/rules/cursor-tools.mdc` for browser automation (i.e. `cursor-tools browser ...`)

## Local Development Logs

### Flask Logs
Flask application logs are stored in `logs/flask_app.log` when running the app with `scripts/local/run_backend.sh`.

```bash
# View latest Flask logs
tail -f logs/flask_app.log

# Search for errors
grep -i error logs/flask_app.log
```

### Frontend Logs
Vite development server logs are saved to `logs/vite_dev.log` when running frontend with `scripts/local/run_frontend_dev.sh`.

```bash
# View latest Vite logs
tail -f logs/vite_dev.log

# Both logs are limited to 200 lines by default
```

## Running in Different Modes

(uses Flask port 3000)

```bash
# Development mode (default)
./scripts/local/run_backend.sh

# Production frontend testing locally
./scripts/local/run_backend.sh --prod-frontend
```

## Vercel Logs

Access production logs programmatically using the `VERCEL_PROD_DEPLOYMENT_ID` from `.env.prod`:

```
vercel logs $VERCEL_PROD_DEPLOYMENT_ID
```

You can filter them with `--json | jq 'select(.level == "warning")'`

Experiment with ways to avoid getting trapped in a shell.