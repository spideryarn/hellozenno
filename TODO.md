# Hello Zenno — TODO

## Open issues (non-incident)

- [ ] **`/admin/users` shows "No data"** on https://www.hellozenno.com/admin/users
  after the JWT rotation (2026-05-25). Production. Auth otherwise works
  (profile loads). Triage: check backend `/api/admin/users` (or whatever
  the route is) — likely either a missing-permission issue against
  `auth.users` from the Postgres user the API uses (the legacy anon role
  may have lost something on rotation), or an unrelated frontend regression.
- [ ] **Local backend `/api/profile/current` → 401** with
  `verify_jwt_token: Invalid token signature or structure: Signature
  verification failed`. Production login works fine; this is local-only.
  Likely a stale frontend cookie/token from a different Supabase secret
  (e.g. previously logged in against the prod project, then switched the
  frontend to the local backend). First triage step: clear cookies/local
  storage on the local frontend and log in fresh against local Supabase.
  Defer until the security incident work is done.

## SECURITY INCIDENT — Hello Zenno DONE, Spideryarn + hardening remain (2026-05-03 → )

Hello Zenno credentials rotated end-to-end on 2026-05-25. Attacker's stolen
HS256 secret is permanently revoked. Full session log:
[`docs/conversations/260525a_supabase_pat_compromise_remediation.md`](docs/conversations/260525a_supabase_pat_compromise_remediation.md).
Master external runbook: `~/security-investigations/260503-supabase-vercel/`.

### Done (Hello Zenno)
- [x] Containment: PAT removed from `.cursor/mcp.json`, gitignored, untracked
- [x] PAT revoked + new one generated (`Droid Greg 260504`, in `.env.security`)
- [x] DB backups in two locations (450 MB / 612 entries)
- [x] Edge Function inventory: 0 functions on both projects (proxy already gone)
- [x] DB password reset + propagated via deploy
- [x] Dual-mode JWT verification deployed (`1f6034a`, HS256 + JWKS)
- [x] peewee pinned `<4` (`a764ccc`) — Vercel uv was resolving 4.0.6
- [x] JWT signing keys rotated: ECC P-256 now current
- [x] Frontend migrated to new publishable key (legacy anon JWT replaced)
- [x] Legacy JWT-based API keys disabled
- [x] Legacy HS256 signing key revoked

### Next up (highest ease × value — pick from here first)
1. [ ] **Enable Vercel spend cap** (5 min, dashboard) — caps damage from any
   future incident (DDoS, cost amplification, runaway function). On both
   `hz_backend` and `hz_frontend` projects. https://vercel.com/greg-detre/~/settings/billing
2. [ ] **Drop `SUPABASE_JWT_SECRET` + HS256 branch** (15 min code) — now-dead
   code path since legacy HS256 is revoked. Remove HS256 branch in
   `backend/utils/auth_utils.verify_jwt_token`, remove the env var from
   `backend/utils/env_config.py`, `.env.example`, `.env.local`, `.env.prod`,
   `.env.testing`, and Vercel project settings.
3. [ ] **Fix `deploy_frontend.sh` build-env handling** (15 min code) — pass
   `--build-env` for `PUBLIC_*` vars or drop the `-e` injection entirely and
   rely on Vercel project env vars. Bit us mid-rotation today.
4. [ ] **Apply RLS migration to Hello Zenno** (30–60 min) — 17 public tables
   currently have no row-level security (Supabase advisor flagged all of
   them). SQL ready at
   `~/security-investigations/260503-supabase-vercel/scripts/enable_rls_hellozenno.sql`.
   Real defense-in-depth: without RLS, anyone with a publishable key can read
   all the public tables. **Test locally first** so production isn't blindsided.

### Outstanding rotation work (Spideryarn + post-rotation cleanup)
- [ ] **Spideryarn rotation** — handed off to a separate session. Runbook at
  `/Users/greg/dev/spideryarn/reading/SECURITY_REMEDIATION_TODO.md`.
- [ ] **Rotate third-party API keys** flagged by Trufflehog as historical
  exposures (separate from the PAT incident, still worth doing): OpenAI,
  Anthropic, ElevenLabs (in `.env.testing` @ HZ commit `6069c65`), Gemini
  and Anthropic again (in `.env.test` @ Spideryarn commit `cb08236a`).
  Update local `.env.*` and Vercel. **Best done after Spideryarn rotation
  is complete** so the third-party rotation covers both projects in one pass.
- [ ] **Reply to Supabase Security** with the consolidated timeline +
  remediation summary. Draft at
  `~/security-investigations/260503-supabase-vercel/SUPABASE_REPLY_DRAFT.md`.
  Wait until Spideryarn is also rotated so we send one complete reply.

### Hardening + decisions (lower urgency)
- [ ] **Vercel firewall / IP allow / rate-limit rules**. Decide whether to
  enable. Higher effort than spend cap; depends on traffic patterns.
- [ ] **Reconnect Vercel ↔ GitHub for `hz_backend`/`hz_frontend`.** Currently
  manual deploys only — pushing to `main` does nothing. Consider whether to
  re-link for auto-deploys, or keep manual deploys for safety with a GitHub
  Action that just runs `vercel deploy`.
- [ ] **Failing GitHub Action: Security audit (frontend npm audit, prod
  deps).** Started failing some time before this incident; investigate
  separately from rotation work.
- [ ] **Decision: rewrite git history** to scrub the leaked PAT and the
  historical API keys from `.env.testing`/`.env.test`. Force-push impact
  needs weighing against the fact that all those secrets are now invalidated,
  so the marginal value of history rewrite is mostly reputational.
- [ ] **Decision: notify Hello Zenno users.** ~27 external real users in
  `auth.users`. Profile data is minimal; no storage buckets exposed; no
  evidence the attacker exfiltrated user data (only the proxy Edge Function).
  Consult the runbook for the disclosure decision matrix.

### Housekeeping (lower urgency)
- [ ] **Destroy abandoned Fly.io app `hello-zenno`** (placeholder from the
  blocked-Sentry attempt; local files already deleted 2026-05-25).
  `flyctl auth login && fly apps destroy hello-zenno --yes`.
- [ ] *(Optional)* Move tracked `pip-audit-backend-{before,after}.json`
  and `security-audit-{before,after}.json` under
  `~/security-investigations/...` or `.gitignore` them. They're artifacts
  from the 2025-09-14 vulnerability remediation; harmless to keep in repo.

### Reference
- Session log: [`docs/conversations/260525a_supabase_pat_compromise_remediation.md`](docs/conversations/260525a_supabase_pat_compromise_remediation.md)
- Master runbook: `~/security-investigations/260503-supabase-vercel/REMEDIATION_RUNBOOK.md`
- Hello Zenno backups (612 entries / 450 MB):
  `~/security-investigations/260503-supabase-vercel/db-backups/` and
  `~/Dropbox/backups/supabase-incident-2026/`
- New Supabase PAT (`Droid Greg 260504`): `.env.security` (gitignored)

---

## Pre-existing TODOs

- forgot password
- A vs B search
- broken links to synonyms and doesn't include translations in lemma page
- login required to generate audio
