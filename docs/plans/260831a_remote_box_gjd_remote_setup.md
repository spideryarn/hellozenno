# Running Hello Zenno on the shared remote box

Status: **done — it ran on the box 2026-09-03**, see "Outcome, 2026-09-03" at the bottom. The
files themselves landed 2026-09-02, under "What landed". Written 2026-08-31 from the Spideryarn
side, for whoever picks this up here.

Greg has an always-on Hetzner box (CX53, Ubuntu 24.04) where many autonomous Claude Code sessions run
in parallel in tmux, driven from his laptop by a CLI called `gjd-remote`. It has only ever served one
repo. He wants Hello Zenno on the same box, alongside Spideryarn, with sessions running at the same
time.

**The design lives in the other repo**, because that is where `gjd-remote` and the box's Terraform
live:

That repo now lives at `/Users/greg/dev/spideryarn/reading2` (it moved out of Dropbox), and the
files have been renamed since this doc was written:

- `docs/plans/260902h-gjd-remote-works-from-whichever-repo-you-are-in.md` — **the live plan**, and
  Hello Zenno is its Stage 5. It supersedes `260831ad-multi-repo-support-for-gjd-remote-box.md`,
  which was written the day before this doc and never built.
- `docs/project/hetzner-remote-server-box.md` — what the box is and how `gjd-remote` drives it. The
  contract for `.gjd-remote/` is its section "Which repo, and where on the box".

This doc holds only the part that is **Hello Zenno's own work**.

## The shape of the answer, in one paragraph

`gjd-remote` will not learn anything about Hello Zenno. Per-repo variation is absorbed by committed
files in this repo, run explicitly, never because a checkout happened to arrive:

```
.gjd-remote/config.toml    # what this repo asks for; `check` is the only key it sets
.gjd-remote/setup          # executable, idempotent, non-destructive; the default when it exists
.gjd-remote/check          # read-only; the tool runs it itself after setup
```

**Corrected since 2026-08-31**: Greg decided in favour of a small TOML config alongside the
executable, rather than one `.gjd-remote/run` dispatcher and no config at all. Every key is
optional, and an unknown key is an error naming the key. The reasoning is in the Spideryarn plan
`260902h`, section "The per-repo config".

The scripts may do whatever this repo likes — a venv, the submodule, `npm ci --prefix frontend`.
Anything that decides *what leaves Greg's laptop* (credentials, destinations, repo identity) stays
on the laptop side and is not something this repo can declare.

## Five things here that need fixing, with the reasons

These are Hello Zenno's bugs, not `gjd-remote`'s. They are listed roughly by how much they matter on
a **shared** machine.

### 1. `run_backend.sh` kills whatever owns the port — FIXED 2026-09-02

`scripts/local/run_backend.sh:30` and its Vite sibling:

```bash
lsof -ti:$FLASK_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:5173        | xargs kill -9 2>/dev/null || true
```

On a shared box, whatever owns 5173 is very likely Spideryarn's dev server and a colleague agent's
work. **Refuse an occupied port and say who holds it**, rather than killing the owner. This is the
one item that can damage someone else's work, so it is first.

Both are now one `require_free_port` that prints `lsof -nP -iTCP:$port -sTCP:LISTEN` and exits 1.
It also moved *above* the pip installs, so the refusal costs nothing. The `kill -9` tips in
`README.md` and `AGENTS.md` were reworded to "find out who holds it first". Made to go red: a
`python3 -m http.server` on 3111, then `FLASK_PORT=3111 ./scripts/local/run_backend.sh` — refused
by name, and the listener was still alive afterwards.

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

### 3. The submodule URL is ssh, and the box has no GitHub ssh key — FIXED 2026-09-02

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

Done, with the reasoning kept as a comment in `.gitmodules`, and `git submodule sync` run so the
laptop's `.git/config` and the submodule's own `origin` follow. Checked from the laptop:
`git -C gjdutils ls-remote origin refs/heads/main` over https returns exactly the commit this
checkout records. The submodule's *push* URL is still ssh, which is right — the box never pushes it.

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

> **Overtaken by events, 2026-09-03.** `push-env` no longer refuses, and it has been run — see
> "Outcome, 2026-09-03" at the bottom for what went and what was withheld. The reasoning below
> is kept because half of it still holds.

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

Steps 2 and 3 are now `.gjd-remote/setup`, and `.gjd-remote/check` answers "does Hello Zenno still
work here?" by looking rather than by trusting exit codes. Steps 4 and 5 — `.env.local`, the
Supabase stack, the migrations — are deliberately **not** in setup: the box runs one repo's app
stack at a time, so standing Hello Zenno's up stays a decision a person makes. The database-schema
half of the check waits for that.

## What landed, 2026-09-02

Written from the Spideryarn side, as Stage 5 of that repo's `260902h` plan. Nothing has been run on
the box yet.

| file | what |
|---|---|
| `.gjd-remote/config.toml` | points `check` at the script below; no `setup =` key, because an executable `.gjd-remote/setup` is the default |
| `.gjd-remote/setup` | submodule, `.venv` + `backend/requirements-dev.txt`, `npm ci --prefix frontend` |
| `.gjd-remote/check` | read-only: imports flask/peewee/loguru/gjdutils out of `.venv`, `git submodule status`, `npm ls --prefix frontend --depth=0` |
| `.gitmodules` | ssh → https (item 3) |
| `.gitignore` | ignore `.venv/`, which setup creates |
| `scripts/local/run_backend.sh` | `require_free_port` (item 1) |
| `README.md`, `AGENTS.md` | the `kill -9` port tips reworded |

Two things setup will not do, both because the box is shared and other agents' sessions are live in
other checkouts: it never re-runs `npm ci` over an existing `frontend/node_modules` (`npm ci`
deletes that directory first), and it never recreates an existing `.venv`. `pip install -r` is
additive, so that one is repeated on every run. `check` is what notices a stale `node_modules`.

Exercised on the laptop: `check` red on the venv by name with no `.venv`; green on all three with a
`.venv` symlinked to Greg's existing backend venv; red on the submodule by name with `gjdutils`
detached to `HEAD~1`, then restored. `setup` was **not** run here — it would create a second venv
and install hundreds of MB on the laptop for no reason — beyond `bash -n` and its
not-a-checkout guard. The Spideryarn config parser was pointed at this repo and resolved
`setup = ./.gjd-remote/setup (source: script)`, `check = ./.gjd-remote/check`, no warnings.

## How to know each guard works

The rule on the Spideryarn side, worth importing: a check you have never seen fail is not evidence.

| Guard | Make it go red | Seen red? |
|---|---|---|
| `check` is not just `setup` again | Have `setup` return immediately with dependencies absent; `check` must fail, by name | yes — `check` fails on a checkout `setup` has never touched |
| venv | Remove `.venv/bin/python`; `check` must fail | yes, 2026-09-02 |
| submodule | Move `gjdutils` off its recorded commit; `check` must fail | yes, 2026-09-02 (`HEAD~1`, then restored) |
| frontend | Remove `frontend/node_modules`, or leave one that no longer satisfies the lockfile | not yet — `npm ls` was only seen green |
| migration verification | Cancel the migration; the schema check must still fail | no — item 2 is still open, and no schema check exists yet |
| port politeness | Bind 5173 from an unrelated process; `run_backend.sh` must refuse and name the holder, not kill it | yes, 2026-09-02 (on 3111, and the holder survived) |

## Outcome, 2026-09-03

**Hello Zenno is on the box.** Run end to end from `/Users/greg/dev/hellozenno` with the multi-repo
`gjd-remote`, as Stage 5 of the Spideryarn plan. The full record — every command, the quoted output,
and what each of GPT Sol's watch points did — is in that repo, at
`/Users/greg/dev/spideryarn/reading2/docs/plans/260902h-gjd-remote-works-from-whichever-repo-you-are-in.md`,
in the Log entry dated 2026-09-03 headed "Stage 5 run end to end against the box".

What is now on the box, at `/home/greg/code/hellozenno`:

- The checkout, cloned over https from `main` at `62e7c54`. Its repo identity to `gjd-remote` is
  **`spideryarn/hellozenno`**, taken from the git origin — so its files on the box and on the laptop
  are named `spideryarn--hellozenno.*`.
- `gjdutils` checked out at the recorded commit, over the https submodule URL, with no credential
  prompt.
- `.venv` on Python 3.12.3, with `backend/requirements-dev.txt` installed.
- `frontend/node_modules` from `npm ci`.
- A `success` setup verdict at `~/gjd-remote/setup/spideryarn--hellozenno.json`, and
  `./.gjd-remote/check` passing all three items when re-run by hand.

Nothing stands the application up: no Supabase stack, no migrations, no Playwright browsers. That is
still a decision for a person, as this doc says above.

### `push-env` was run, and "do not use `push-env`" above needs revisiting

The section headed "Environment variables: do not use `push-env`" is now half out of date, and Greg
should decide what replaces it.

- **Out of date:** it says `push-env` "will **refuse** for this repo, deliberately". It does not any
  more. Every repo that is not Spideryarn now gets a checklist of its own key **names**, proposed by
  a model that never sees a value, and the answers are remembered.
- **Still true, and the reason to be careful:** `backend/utils/env_config.py` requires *every* key,
  so the partial file now on the box would crash the backend at import.

What was actually sent, on 2026-09-03, as key names only: `OPENAI_API_KEY`, `CLAUDE_API_KEY`,
`ELEVENLABS_API_KEY`, `PERPLEXITY_API_KEY`, `GEMINI_API_KEY`, `CODEX_API_KEY`, `USE_LOCAL_TO_PROD`,
`LOGS_DIR`, `FLASK_PORT`, `SUPABASE_PORT`, `SUPABASE_POOL_MODE`, `PUBLIC_SUPABASE_URL`,
`SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY`, `USE_LEGACY_CURSORRULES`, `VITE_FRONTEND_URL`,
`VITE_API_URL`, `SEGMENTATION_DEFAULT`, `SEGMENTATION_TH`, `RECOGNITION_KNOWN_WORD_SEARCH`.

**Withheld**, and recorded as withheld so no later model can re-propose them: `FLASK_SECRET_KEY` —
the production session-signing secret this doc singles out — plus `SUPABASE_PASSWORD`,
`SUPABASE_USER`, `SUPABASE_HOST`, `SUPABASE_DATABASE` and `DATABASE_URL`.

The file on the box is `600 greg:greg` and holds those 20 names and no others. The paragraph above
about the box being one Unix user shared by many agents still stands, unchanged: those provider keys
are now readable by every agent on it.
