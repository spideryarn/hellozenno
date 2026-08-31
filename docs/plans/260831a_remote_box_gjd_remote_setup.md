# Running Hello Zenno on the shared remote box

Status: proposal, nothing built. Written 2026-08-31 from the Spideryarn side, for whoever picks this
up here.

Greg has an always-on Hetzner box (CX53, Ubuntu 24.04) where many autonomous Claude Code sessions run
in parallel in tmux, driven from his laptop by a CLI called `gjd-remote`. It has only ever served one
repo. He wants Hello Zenno on the same box, alongside Spideryarn, with sessions running at the same
time.

**The design lives in the other repo**, because that is where `gjd-remote` and the box's Terraform
live:

- `/Users/greg/Dropbox/dev/experim/spideryarn2/docs/plans/260831ad-multi-repo-support-for-gjd-remote-box.md`
  — the plan, the seam, and what is deliberately not being built.
- `/Users/greg/Dropbox/dev/experim/spideryarn2/docs/project/remote-box.md` — what the box is and how
  `gjd-remote` drives it.

This doc holds only the part that is **Hello Zenno's own work**.

## The shape of the answer, in one paragraph

`gjd-remote` will not learn anything about Hello Zenno. Per-repo variation is absorbed by **one
committed executable per repo**, invoked explicitly, never automatically:

```
.gjd-remote/run setup      # explicit, idempotent, non-destructive
.gjd-remote/run check      # read-only; the tool runs it itself after setup
```

It may dispatch however this repo likes — a venv, the submodule, `npm ci --prefix frontend`, the
local database. No config file, no lifecycle hooks, no overrides. Anything that decides *what leaves
Greg's laptop* (credentials, destinations, repo identity) stays on the laptop side and is not
something this repo can declare.

## Five things here that need fixing, with the reasons

These are Hello Zenno's bugs, not `gjd-remote`'s. They are listed roughly by how much they matter on
a **shared** machine.

### 1. `run_backend.sh` kills whatever owns the port

`scripts/local/run_backend.sh:30` and its Vite sibling:

```bash
lsof -ti:$FLASK_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:5173        | xargs kill -9 2>/dev/null || true
```

On a shared box, whatever owns 5173 is very likely Spideryarn's dev server and a colleague agent's
work. **Refuse an occupied port and say who holds it**, rather than killing the owner. This is the
one item that can damage someone else's work, so it is first.

### 2. `migrate.sh` exits 0 when you cancel the migration

`scripts/local/migrate.sh`, the `else` branch near line 70:

```bash
echo -e "${YELLOW}Migration cancelled.${NC}"
exit 0
```

A cancelled migration is indistinguishable from a successful one to any caller. That matters more
here than usual, because an adapter's `check` would be built on exactly this kind of exit code.
**Verify the resulting schema, not the exit status.** (Spideryarn has a doc about this class:
`docs/reusable/silent-success.md` in that repo.)

### 3. The submodule URL is ssh, and the box has no GitHub ssh key

`.gitmodules`:

```
url = git@github.com:gregdetre/gjdutils.git
```

The box authenticates to GitHub over **https**, through a credential helper that reads the owner out
of the request path and looks up a per-owner fine-grained PAT. An ssh URL never reaches it. Both
`gregdetre.token` and `spideryarn.token` already exist on the box, so the token side is fine.

**Change `.gitmodules` to the https URL.** That was considered against a global `url.insteadOf`
rewrite on the box, and rejected: https works on both machines, whereas a global rewrite is hidden
machine magic that every later `git submodule update` silently depends on.

Until it is changed, a one-command rewrite on the box gets you moving.

### 4. Playwright expects a browser the box does not have

`frontend/playwright.config.ts` builds and previews on port 4173 and expects Playwright's own
bundled Chromium. The box's provisioning deliberately installs system Chrome and **no** bundled
browser. Either point the tests at system Chrome or install the lockfile-matched browser explicitly.
Until then, skip Playwright on the box.

### 5. `supabase/config.toml` collides with Spideryarn on port 8083

Both repos set `edge_runtime.enabled = true` and `inspector_port = 8083` (here, line 264).

**This is currently latent, not live**: neither repo has a `supabase/functions` directory and nothing
is bound to 8083 on the box. It bites the day someone adds an edge function. It can also be fixed on
the Spideryarn side, so it needs nothing here unless you would rather own it.

The rest of the port picture: this repo's Supabase block is 5432x (the CLI defaults), Spideryarn's is
5436x, so those do not clash. Flask 3000, Vite 5173, preview 4173 and Storybook 6006 are all
unqualified defaults, and **5173 is genuinely contested** — Spideryarn's Vite wants it too.

## Environment variables: do not use `push-env`

`gjd-remote push-env` builds a `.env.local` on the box from an allowlist of key names. It will
**refuse** for this repo, deliberately, and you should not try to talk it into working.

Two reasons, both specific to this repo:

- `backend/utils/env_config.py` requires *every* key. An allowlist-trimmed file would either be the
  whole file (no protection at all) or crash the app at import.
- Ten values in `.env.local` are **byte-identical** to values in `.env.prod`, and one of them is
  `FLASK_SECRET_KEY` — a production session-signing secret. The shared provider API keys
  (`OPENAI_API_KEY`, `CLAUDE_API_KEY`, `ELEVENLABS_API_KEY`) are ordinary and not the problem;
  `FLASK_SECRET_KEY` is.

For the record, and correcting a mistake made while investigating this: **`.env.local`'s database
and Supabase URLs are all `127.0.0.1`.** It is `.env.prod` that holds the `*.supabase.co` hosts.

So: build a **box-local** development env by hand, with a freshly generated `FLASK_SECRET_KEY` and
only the provider keys deliberately chosen. `USE_LOCAL_TO_PROD` must be `0`.

The reason this matters more than it would on a laptop: the box is one Unix user with passwordless
sudo, shared by many autonomous agents. **Any credential on that box is available to every agent on
it.** Per-repo files do not create per-repo confidentiality. If Hello Zenno ever needs secrets that
Spideryarn's agents must not hold, the answer is a separate Unix user or a separate box, not a
cleverer allowlist.

## What the box already has, and what it does not

Measured 2026-08-31.

| | |
|---|---|
| node, Docker CE, Supabase CLI (pinned), Chrome, gh, jq, tmux, mosh | present |
| python3 | **3.12.3 present, but no pip, no venv, no uv** — one line of provisioning, on the Spideryarn side |
| `/home` (persistent volume) | 49G, 2.5G used |
| RAM | 30G total, **19G used, 11G available** — with 13 sessions on *one* repo |
| Xvfb `:99` + noVNC on 6080 | one shared display for the whole box |

RAM is nearer the ceiling than disk. There is nothing above CX53 in Hetzner's CX line. So: **run one
repo's application services at a time.** Concurrent Claude *sessions* are fine; concurrent app stacks
(two Supabase Dockers, two dev servers) are deferred until someone shows they fit.

Also worth knowing: `gjd-remote` runs commands over non-interactive ssh, which sources neither
`.bashrc` nor `.bash_profile`. An adapter here must use explicit paths (`.venv/bin/python`) and fail
clearly when something is missing, rather than relying on a login shell.

## The v0 recipe

Deliberately manual. It needs essentially no change to `gjd-remote`, which is the point.

1. `gjd-remote clone spideryarn/hellozenno` — clones the root checkout to `~/code/hellozenno`.
2. `git submodule update --init --recursive`, explicitly (see item 3 above).
3. Create `.venv`, install backend requirements, `npm ci --prefix frontend`.
4. Write `.env.local` on the box by hand — box-local values, fresh Flask secret.
5. Bring up the local Supabase stack and apply migrations.
6. `gjd-remote new-shell -d ~/code/hellozenno` for a session that survives the laptop sleeping.

Skip Playwright. Do not run Spideryarn's app stack at the same time.

Once steps 2-5 are written down as `.gjd-remote/run setup`, with a `check` that verifies venv,
submodule commit, frontend dependencies and database schema **independently** rather than by trusting
exit codes, the box can answer "does Hello Zenno still work here?" after a rebuild without a human
checking five things by hand. That is the whole reason the adapter exists.

## How to know each guard works

The rule on the Spideryarn side, worth importing: a check you have never seen fail is not evidence.

| Guard | Make it go red |
|---|---|
| `check` is not just `setup` again | Have `setup` return immediately with dependencies absent; `check` must fail, by name |
| venv | Remove `.venv/bin/python`; `check` must fail |
| submodule | Move `gjdutils` off its recorded commit; `check` must fail |
| migration verification | Cancel the migration; the schema check must still fail |
| port politeness | Bind 5173 from an unrelated process; `run_backend.sh` must refuse and name the holder, not kill it |
