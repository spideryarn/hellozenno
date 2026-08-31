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

Both projects are on Vercel under the `greg-detre` team (`hz_frontend` ->
www.hellozenno.com, `hz_backend` -> api.hellozenno.com). There is no Vercel MCP server
configured; the CLI is the access path, and `vercel whoami` should print `gregdetre`.

**Runtime logs.** `vercel logs <url>` live-tails and never exits on its own, so an agent
must wrap it in `timeout` - that is the whole trick, and it works fine:

```bash
timeout 30 vercel logs https://api.hellozenno.com    # backend
timeout 30 vercel logs https://www.hellozenno.com    # frontend
```

You can pass the production domain directly - no need to look up a deployment id first.
Add `--json` to get structured records for filtering (e.g. `| jq 'select(.level == "warning")'`).

Caveat: this shows *live* logs only. Requests from before you started the command are
mostly not visible, so for a quiet period you may need to trigger traffic yourself, and
for genuine history use the Vercel dashboard's Observability tab.

**Build logs**, by contrast, are complete and historical:

```bash
vercel inspect --logs https://hzbackend-7hpinio7g-greg-detre.vercel.app
```

**Listing deployments.** Name the project explicitly - a bare `vercel ls` filters by the
current git branch and will look empty on a feature branch:

```bash
vercel ls hz_backend
vercel ls hz_frontend
```

Running these from `backend/` prints a spurious `Did you mean to deploy the subdirectory
"logs"?` warning (because `backend/logs/` exists). Harmless.
