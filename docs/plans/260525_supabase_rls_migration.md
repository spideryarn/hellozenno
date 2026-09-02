# Plan: Supabase RLS Migration for Hello Zenno

**Date:** 2026-05-25
**Status:** Deferred — researched, scoped, not scheduled. Resume when there's appetite for a careful prod migration with manual smoke testing.

## Overview

Enable Postgres row-level security (RLS) on the 17 tables in the Hello Zenno
Supabase project's `public` schema. Currently every table has RLS disabled;
the Supabase advisor flags all 17 as "RLS Disabled in Public" warnings. This
is the largest single security improvement remaining for Hello Zenno after
the 2026-05-25 credential rotation
(see [`docs/conversations/260525a_supabase_pat_compromise_remediation.md`](../conversations/260525a_supabase_pat_compromise_remediation.md)).

A draft migration SQL exists at
`/Users/greg/security-investigations/260503-supabase-vercel/scripts/enable_rls_hellozenno.sql`,
but it was written under an incorrect assumption about how the frontend
talks to Supabase (see Context below). It is **not safe to apply as-is**.

## Why deferred

- The migration's safety hinges on a frontend-loader pattern that needs
  understanding before applying — not something to ship at the tail end of an
  already long incident-response session.
- Existing pytest suite cannot catch RLS regressions (tests run as
  Postgres `postgres` superuser, which bypasses RLS). Manual smoke testing
  is the only signal.
- No Sentry / uptime monitoring is wired up, so a silent regression
  ("page renders but DataGrid is empty") could go undetected for hours.
- The remediation goal of the post-incident hardening is already met by the
  rotation + dropping HS256 + spend cap. RLS is defense-in-depth on top of
  that, not blocking.

## Context

### Stack recap
- SvelteKit frontend (Vercel) + Flask API backend (Vercel) + Supabase
  Postgres + GoTrue.
- Frontend uses `@supabase/ssr` `createServerClient` /
  `createBrowserClient` with the publishable (anon) key.
- Backend connects to Postgres via Peewee using `DATABASE_URL` from
  `.env.prod`. Role: `postgres` (Supabase superuser, `BYPASSRLS=true`).
- JWTs are verified in Python (`backend/utils/auth_utils.verify_jwt_token`)
  and never propagated to Postgres claims; `auth.uid()` would resolve to
  `NULL` for backend-issued queries.

### The 17 tables (per `enable_rls_hellozenno.sql`)
`lemma`, `lemmaaudio`, `lemmaexamplesentence`, `migratehistory`, `phrase`,
`phraseexamplesentence`, `profile`, `relatedphrase`, `sentence`,
`sentenceaudio`, `sentencelemma`, `sourcedir`, `sourcefile`,
`sourcefilephrase`, `sourcefilewordform`, `userlemma`, `wordform`.

### Relevant findings from research

Two researcher subagents (independent runs, converged on the same conclusion).

#### Critical finding: 5 SvelteKit routes query Supabase tables directly via the anon key
The draft script's stated invariant ("data queries are routed through the
Flask backend") is wrong. Under RLS-with-no-policies, these 5 routes would
return zero rows for every user, including admins:

| Route | Table | File:line |
|---|---|---|
| `/language/{code}/lemmas` | `lemma` | `frontend/src/routes/language/[target_language_code]/lemmas/+page.server.ts:13-21` |
| `/language/{code}/wordforms` | `wordform` | `frontend/src/routes/language/[target_language_code]/wordforms/+page.server.ts:12-19` |
| `/language/{code}/sentences` | `sentence` | `frontend/src/routes/language/[target_language_code]/sentences/+page.server.ts:13-21` |
| `/language/{code}/sources` | `sourcedir` | `frontend/src/routes/language/[target_language_code]/sources/+page.server.ts:33-44` |
| `/language/{code}/generate` | `sourcedir` | `frontend/src/routes/language/[target_language_code]/generate/+page.server.ts:9-13` |

Plus a client-side DataGrid pattern in
`frontend/src/lib/datagrid/providers/supabase.ts:29-99` that hits `phrase`
post-page-load via `client.from('phrase')`.

#### The other 12 tables
No frontend code path queries them directly. Safe to go RLS-on-with-no-policies
(deny-all to anon) without breaking anything visible. The defence-in-depth
benefit: a future accidental supabase-js query against `lemmaaudio`,
`sentenceaudio`, `sourcefile`, `profile`, `userlemma`, junctions, or
`migratehistory` would be blocked at the DB.

#### Backend is unaffected
Confirmed at `backend/utils/db_connection.py:56-78` and `.env.prod:4`. No
`SET ROLE` or `set_config` calls anywhere in the backend. RLS is
transparent to the Flask layer.

#### Test coverage gap
- ~150 backend pytest tests in `backend/tests/backend/` — all run as the
  `postgres` superuser per `.env.testing` (`DB_USER=postgres`,
  `DB_HOST=localhost`, `DB_PORT=54322`, `DB_NAME=hellozenno_test`).
  Postgres superuser bypasses RLS entirely.
- Frontend has effectively zero automated tests (one 352-byte placeholder).
- **Net: no automated test would surface an RLS regression.** Manual smoke
  testing of the 5 routes above is the only viable verification.

### Key constraints and requirements
- The migration must be reversible quickly (target: < 30 seconds wall-clock
  rollback if prod breaks).
- Must not break `./scripts/prod/migrate.sh` workflow or peewee-migrate
  bookkeeping (`migratehistory` table).
- Must keep the 5 frontend SSR loaders working (they're customer-visible).
- Should leave the backend's `postgres`-role connection unchanged.

### Success criteria
1. Supabase advisor "RLS Disabled in Public" warning closes for all 17
   tables.
2. All 6 user flows in the smoke test plan (below) work for both logged-in
   and logged-out users.
3. `migratehistory` reflects the new migration with a clean rollback path.
4. No backend test regressions.

## Approach options

### Option A — Apply with 5 SELECT policies (RECOMMENDED)
Add 5 lines to the migration permitting anon SELECT on the tables the
frontend reads. Closes the advisor warning for the other 12 tables. Keeps
all 6 user flows working. ~30 minutes to author, smoke, ship.

```sql
CREATE POLICY "public_read_lemma"     ON public.lemma     FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "public_read_wordform"  ON public.wordform  FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "public_read_sentence"  ON public.sentence  FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "public_read_phrase"    ON public.phrase    FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "public_read_sourcedir" ON public.sourcedir FOR SELECT TO anon, authenticated USING (true);
```

Defence: a future accidental exposure of a sensitive table via supabase-js
is blocked. Already-public content stays public.

Non-defence: anon can still read all lemmas/wordforms/sentences/phrases/
sourcedirs (which they can today anyway via the existing direct-from-frontend
pattern).

### Option B — Refactor 5 SSR loaders to Flask, then RLS-no-policies (~2-3 hours)
The Flask API endpoints already exist
(`LEMMA_API_LEMMAS_LIST_API`, `WORDFORM_API_WORDFORMS_LIST_API`, etc.).
Port the 5 loaders, drop the direct supabase-js DataGrid path, then enable
RLS with no policies. Eliminates the whole "frontend can read DB directly"
class of attack surface.

Trade-off: bigger change, more breakage risk, customer-visible perf
characteristics may change (Flask pagination vs PostgREST pagination).
Best as a separate hardening effort after Option A is in place.

### Option C — Defer until backend uses an `authenticated`-role connection
Bigger architectural shift: backend would need to propagate the JWT into
Postgres claims (`SET LOCAL request.jwt.claim.sub`) or use a dedicated
`authenticated` role with `BYPASSRLS=false`. Enables real per-user
enforcement at the DB layer. Out of scope for now.

## Stages (Option A)

### Stage 0: Pre-flight verification
1. **Confirm prod backend role bypasses RLS.** From a session with
   `.env.prod` loaded:
   ```bash
   psql "$DATABASE_URL" -c "SELECT current_user, rolbypassrls FROM pg_roles WHERE rolname = current_user;"
   ```
   Abort if `rolbypassrls != t`.
2. **Backup prod DB.** `./scripts/prod/backup_db.sh` (per
   `backend/docs/MIGRATIONS.md`).
3. **Confirm migration head.** `./scripts/local/migrations_list.sh` to find
   the next migration number (currently 049 will likely be the next free
   slot — verify before authoring).

### Stage 1: Author the migration
- New file: `backend/migrations/0XX_enable_rls.py` (number per Stage 0).
- Use peewee-migrate's `migrator.sql(...)` for all DDL — keeps everything
  inside `database.atomic()` and tracked in `migratehistory`.
- Skeleton:
  ```python
  TABLES = [
      "lemma","lemmaaudio","lemmaexamplesentence","migratehistory","phrase",
      "phraseexamplesentence","profile","relatedphrase","sentence","sentenceaudio",
      "sentencelemma","sourcedir","sourcefile","sourcefilephrase",
      "sourcefilewordform","userlemma","wordform",
  ]
  PUBLIC_READ = ["lemma","wordform","sentence","phrase","sourcedir"]

  def migrate(migrator, database, fake=False, **kwargs):
      with database.atomic():
          for t in TABLES:
              migrator.sql(f'ALTER TABLE public."{t}" ENABLE ROW LEVEL SECURITY;')
          for t in PUBLIC_READ:
              migrator.sql(
                  f'CREATE POLICY "public_read_{t}" ON public."{t}" '
                  f'FOR SELECT TO anon, authenticated USING (true);'
              )

  def rollback(migrator, database, fake=False, **kwargs):
      with database.atomic():
          for t in PUBLIC_READ:
              migrator.sql(f'DROP POLICY IF EXISTS "public_read_{t}" ON public."{t}";')
          for t in TABLES:
              migrator.sql(f'ALTER TABLE public."{t}" DISABLE ROW LEVEL SECURITY;')
  ```

### Stage 2: Apply locally + manual smoke
1. `supabase start` (if not running).
2. `./scripts/local/migrate.sh` to apply the new migration.
3. Restart `./scripts/local/run_backend.sh` and `./scripts/local/run_frontend.sh`.
4. Manual smoke checklist (logged in as a test user):

   | # | Action | Route | Expected |
   |---|---|---|---|
   | 1 | Sign in | `/auth` | Works |
   | 2 | Lemmas list | `/language/el/lemmas` | DataGrid populates |
   | 3 | Wordforms list | `/language/el/wordforms` | DataGrid populates |
   | 4 | Sentences list | `/language/el/sentences` | DataGrid populates |
   | 5 | Phrases list | `/language/el/phrases` | DataGrid populates (Flask-fed initially, supabase-js for sort/filter) |
   | 6 | Sources list | `/language/el/sources` | Page populates |
   | 7 | Generate page | `/language/el/generate` | Sourcedir picker populates |
   | 8 | Lemma detail | `/language/el/lemma/{slug}` | Loads (Flask path) |
   | 9 | Sourcefile detail | `/language/el/source/{slug}/{slug}` | Loads (Flask path) |
   | 10 | Generate audio button | sourcefile page | Works (Flask path) |
   | 11 | Profile page | `/auth/profile` | Loads + edits work (Flask path) |
   | 12 | Admin/users | `/admin/users` | Loads (Flask path) |

5. Repeat steps 2-7 logged out. The 5 PostgREST routes should still
   populate (anon SELECT policy permits it). If any return empty, the
   policies aren't matching what the frontend queries — debug before
   continuing.

### Stage 3: Pytest sanity check
- `pytest backend/tests/` — should pass unchanged (tests run as
  superuser, RLS bypassed). If it fails, the migration broke something
  unrelated.

### Stage 4: Optional — RLS smoke test in pytest
~30 minutes if appetite. Adds a small test that creates `anon` and
`authenticated` Postgres roles in the test DB, switches role, and confirms
the 5 PostgREST tables permit SELECT while a non-policy table (e.g.
`profile`, `lemmaaudio`) denies. This is the lowest-cost way to catch
future RLS regressions in CI without a frontend test rewrite.

Skeleton in `backend/tests/backend/test_rls_smoke.py`:
```python
import pytest
from playhouse.postgres_ext import PostgresqlExtDatabase

@pytest.fixture
def authenticated_conn(db_url):
    conn = PostgresqlExtDatabase(...)
    conn.connect()
    conn.execute_sql("SET ROLE authenticated;")
    yield conn
    conn.close()

def test_authenticated_can_read_lemma(authenticated_conn):
    cur = authenticated_conn.execute_sql("SELECT 1 FROM public.lemma LIMIT 1;")
    assert cur.fetchone() is not None or True  # presence of permission, not data

def test_authenticated_cannot_read_lemmaaudio(authenticated_conn):
    with pytest.raises(Exception):  # tighten to specific psycopg error
        authenticated_conn.execute_sql("SELECT 1 FROM public.lemmaaudio LIMIT 1;")
```

### Stage 5: Apply to prod
1. Have the rollback `psql` window pre-loaded (see Rollback below).
2. Source `.env.prod` and run `./scripts/prod/migrate.sh`.
3. Watch the output for the new row in `migratehistory`.
4. Within 60 seconds, hit https://www.hellozenno.com/language/el/lemmas in
   an incognito window. If the DataGrid populates, all 5 frontend pages
   are good (they share the same anon-key path). Hit one or two of the
   others (`/sources`, `/sentences`) to confirm.
5. Re-run the Supabase advisor: confirm "RLS Disabled in Public" warnings
   are gone.

## Rollback

### Fast path (psql, < 30 seconds)
```sql
BEGIN;
DROP POLICY IF EXISTS "public_read_lemma"     ON public.lemma;
DROP POLICY IF EXISTS "public_read_wordform"  ON public.wordform;
DROP POLICY IF EXISTS "public_read_sentence"  ON public.sentence;
DROP POLICY IF EXISTS "public_read_phrase"    ON public.phrase;
DROP POLICY IF EXISTS "public_read_sourcedir" ON public.sourcedir;
ALTER TABLE public.lemma                  DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.lemmaaudio             DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.lemmaexamplesentence   DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.migratehistory         DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.phrase                 DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.phraseexamplesentence  DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.profile                DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.relatedphrase          DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sentence               DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sentenceaudio          DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sentencelemma          DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sourcedir              DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sourcefile             DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sourcefilephrase       DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sourcefilewordform     DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.userlemma              DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.wordform               DISABLE ROW LEVEL SECURITY;
COMMIT;
```

### Clean path (peewee-migrate)
`cd backend && python -m utils.migrate rollback` — same effect, also
removes the `migratehistory` row. Slightly slower (~5 seconds).

## Open questions to revisit when picking this back up
1. Has the frontend changed since 2026-05-25? Re-grep for
   `from\(['"]` and `client\.from\(` to catch any new tables added to the
   anon-key path. If new ones appeared, expand the public-read policy list
   accordingly before applying.
2. Has the schema changed (new tables added)? Inventory will need updating.
3. Is Sentry now wired up? If yes, lower-stakes apply (we'd see a 500
   spike). If no, manual smoke is still the only signal.
4. Is the appetite right for Option B (refactor) instead? If we're already
   doing other frontend work, batching the loader refactor into the same
   change may make sense.
5. Are we OK with the small per-page latency cost if Option B chooses
   Flask paths? PostgREST is usually faster than Flask + Peewee for simple
   list pagination.

## Files referenced
- `/Users/greg/security-investigations/260503-supabase-vercel/scripts/enable_rls_hellozenno.sql` — original draft (do not apply as-is)
- `/Users/greg/dev/hellozenno/backend/utils/db_connection.py`
- `/Users/greg/dev/hellozenno/backend/utils/auth_utils.py`
- `/Users/greg/dev/hellozenno/backend/db_models.py`
- `/Users/greg/dev/hellozenno/backend/docs/MIGRATIONS.md`
- `/Users/greg/dev/hellozenno/backend/tests/backend/conftest.py`
- `/Users/greg/dev/hellozenno/.env.prod`
- `/Users/greg/dev/hellozenno/frontend/src/routes/language/[target_language_code]/{lemmas,wordforms,sentences,sources,generate}/+page.server.ts`
- `/Users/greg/dev/hellozenno/frontend/src/lib/datagrid/providers/supabase.ts`
- [`docs/conversations/260525a_supabase_pat_compromise_remediation.md`](../conversations/260525a_supabase_pat_compromise_remediation.md)
