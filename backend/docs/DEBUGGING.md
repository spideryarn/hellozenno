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

### Frontend debugging

see `frontend/docs/FRONTEND_DEBUGGING.md`


## Running Flask dev server

(The user will run this for you in a separate terminal)

```bash
./scripts/local/run_backend.sh
```

## Vercel Logs

Annoyingly, there doesn't seem to be a good way to access production logs programmatically.

The `vercel logs` command will trap you in a shell that updates live, but you can't exit it. So the best approach for now is to `cd frontend_OR_backend && vercel ls | tail`  ask the user to run it for you.

```bash
cd backend
vercel ls | tail
# pick the most recent deployment, `xxx_latest_backend_deployment_id`
vercel logs xxx_latest_backend_deployment_id --json
```

```bash
cd frontend
# pick the most recent deployment, `xxx_latest_frontend_deployment_id`
vercel logs xxx_latest_frontend_deployment_id --json
```

You can filter them with e.g. `--json | jq 'select(.level == "warning")'`

