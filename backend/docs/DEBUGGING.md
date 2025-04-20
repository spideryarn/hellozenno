# Debugging

see `docs/DATABASE.md` for info on how to inspect the database

see `docs/FRONTEND_DEBUGGING.md`

## Local Development Logs

### Flask Logs
Flask application logs are stored in `logs/backend.log` when running the app with `scripts/local/run_backend.sh`.

```bash
# View latest Flask logs
tail -f logs/backend.log

# Search for errors
grep -i error logs/backend.log
```

### Frontend debugging

see `frontend/docs/FRONTEND_DEBUGGING.md`

There is a corresponding `logs/frontend.log`

But you'll need Playwright MCP to view the browser console errors for a page.


## Running Flask dev server

(The user will run this for you in a separate terminal)

```bash
./scripts/local/run_backend.sh
```

## Vercel Logs for debugging production

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

