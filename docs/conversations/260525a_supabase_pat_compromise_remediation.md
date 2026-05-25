# Supabase PAT compromise — remediation log

**Date**: 2026-05-25 (active remediation session) • Incident date: 2026-03-21
**Status**: Hello Zenno rotation complete. Spideryarn Reading rotation + Vercel hardening + history cleanup outstanding.

External master runbook (with backups, scripts, draft replies) lives outside the repo at:
`~/security-investigations/260503-supabase-vercel/`

## TL;DR

A Supabase Personal Access Token committed to `.cursor/mcp.json` in the **public** `spideryarn/hellozenno` repo on 2025-04-11 (commit `2b36530`) was harvested by an attacker. On 2026-03-21 the attacker used it to deploy a malicious Edge Function proxy to both projects in the `GD personal` Supabase org (Hello Zenno and Spideryarn Reading). Supabase Security flagged the unusual deploy and disabled the PAT.

Remediation walked through containment → backups → inventory → key rotation across Supabase + Vercel + GitHub. Hello Zenno is now on the new asymmetric (ES256) JWT signing scheme + new publishable key; the legacy HS256 secret and legacy anon/service_role keys are revoked. The attacker's stolen credentials are now permanently worthless for Hello Zenno.

## Why this incident is interesting

The token leak isn't unusual; what's worth remembering is the rotation path:

- **Supabase has removed in-place HS256 JWT secret rotation.** The only path is to migrate to JWT Signing Keys (asymmetric ES256/RS256/EdDSA), promote a standby key to current, then revoke the legacy HS256.
- **The legacy anon/service_role keys are themselves HS256-signed JWTs.** Revoking the HS256 secret would invalidate them mid-flight, so Supabase forces you to first disable the legacy API keys (after migrating to publishable/secret keys), THEN revoke the HS256 secret.
- **Hello Zenno's backend was HS256-only.** A small code change was needed to verify both HS256 (legacy) and asymmetric (JWKS) JWTs during the rollover.
- **`PUBLIC_*` env vars in SvelteKit are inlined at BUILD time, not runtime.** `deploy_frontend.sh` injects env vars via `vercel -e` (runtime only), so the only way to actually update what's baked into the client bundle is to update Vercel's project-level env vars BEFORE redeploying. Hit this as a footgun mid-rotation.

## Timeline (this session)

1. **Containment.** Removed PAT from `.cursor/mcp.json`, gitignored the file, untracked it. Local commit `5f86530`. Did not push until later. User revoked the leaked PAT in the Supabase dashboard and generated a new one (`Droid Greg 260504`), stored in `.env.security` (gitignored).
2. **Backups.** `pg_dump` of both production DBs via session pooler (port 5432; transaction pooler at 6543 doesn't allow dumps). Hello Zenno: 450 MB / 612 entries. Spideryarn: 21 MB / 577 entries. Stored in two locations (Dropbox + local).
3. **Edge Function inventory.** Confirmed via Management API that BOTH projects now have zero Edge Functions — the malicious proxy was cleanly removed by the time we audited.
4. **Edge Function project secrets.** Only Supabase built-ins (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`, `SUPABASE_JWT_SECRET`, `SB_INTEGRATION_AS_TENANT_KEY`, `SUPABASE_AUTH_HEADER_NAME`). No third-party API keys were exfiltrated via the Edge Functions secrets surface.
5. **Trufflehog scan.** Found additional historical exposures unrelated to the PAT but worth rotating later: OpenAI/Anthropic/ElevenLabs in `spideryarn/hellozenno` commit `6069c65` (`.env.testing`, 2025-02-09); Gemini/Anthropic in `spideryarn/reading` commit `cb08236a` (`.env.test`).
6. **GitHub Actions secret update.** Refreshed `SUPABASE_ACCESS_TOKEN` on `spideryarn/reading` to the new PAT.
7. **Auth code change.** Implemented dual-mode JWT verification — `verify_jwt_token` reads the `alg` header and routes HS256 → existing shared secret, ES256/RS256/EdDSA → JWKS lookup via `PyJWKClient` (cached, 1 h TTL). Added `SUPABASE_URL` env var. Bumped requirement to `PyJWT[crypto]>=2.8.0`. Local commit `1f6034a`.
8. **Deploy bug, peewee 4.0.6.** First production deploy failed at runtime with `cannot import name 'PooledPostgresqlExtDatabase' from 'playhouse.pool'`. Root cause: peewee 4.0.6 was released and removed the class; Vercel's uv-based builder resolved `peewee>=3.17.0` to it. Pinned `peewee>=3.17.0,<4` and `peewee-migrate>=1.12.2,<2`. Local commit `a764ccc`.
9. **Database password reset.** User reset DB password in dashboard, updated `DATABASE_URL` in `.env.prod`; deploy script propagated it to Vercel via `-e` flag. Backend health-check confirmed `database.connected: true`.
10. **JWT key rotation (graceful).** User clicked "Rotate keys" in Supabase JWT page → ECC P-256 (kid `dbfef37b-66db-4ab7-9608-fb931fe91927`) promoted to current; HS256 demoted to "Previously used keys". Existing HS256 sessions remained valid; new logins issued ES256. Verified login + profile + DB queries all working post-rotation.
11. **Publishable key migration.** Created new "default" publishable key via the new "Publishable and secret API keys" tab. Updated `PUBLIC_SUPABASE_ANON_KEY` in `.env.prod`. Redeployed.
12. **Disable JWT-based legacy API keys.** User clicked "Disable JWT-based legacy API keys" in API Keys → Legacy tab. Login broke: `Error: Legacy API keys are disabled`. Root cause: SvelteKit `$env/static/public` inlines at build time; the `-e` runtime injection didn't change the bundle. Fixed by updating Vercel's PROJECT-level `PUBLIC_SUPABASE_ANON_KEY` env var to the new publishable, then redeploying so the build picked it up.
13. **Revoke legacy HS256 signing key.** Final dashboard click. Attacker's stolen secret is now permanently invalid.

## Code changes (Hello Zenno repo)

All commits on `main`, all pushed:

| Commit    | Title                                                   | Files |
|-----------|---------------------------------------------------------|-------|
| `5f86530` | security: untrack `.cursor/mcp.json` (contained leaked PAT) | `.cursor/mcp.json`, `.gitignore` |
| `1f6034a` | auth: support both HS256 and asymmetric JWTs via JWKS   | `backend/utils/auth_utils.py`, `backend/utils/env_config.py`, `backend/requirements.txt`, `.env.example` |
| `a764ccc` | fix(deps): pin peewee<4                                 | `backend/requirements.txt` |

Key file: `backend/utils/auth_utils.py:verify_jwt_token` — algorithm-aware verification, HS256 path retained for backwards compatibility (until the legacy secret env var is also removed; not strictly necessary now that HS256 is revoked).

## Dashboard actions taken

Supabase, Hello Zenno project (`itcwqlhvpbtvtgqkumia`):
- Settings → JWT Keys: created standby (ES256) → rotated → revoked legacy HS256
- Settings → API Keys: created new publishable key (`default`) → disabled JWT-based legacy API keys
- Settings → Database: reset DB password
- Settings → Auth: (no changes)

Vercel:
- `hz_backend` env vars: added `SUPABASE_URL`
- `hz_frontend` env vars: replaced `PUBLIC_SUPABASE_ANON_KEY` (legacy JWT → new publishable)

GitHub:
- `spideryarn/reading` Actions secret: replaced `SUPABASE_ACCESS_TOKEN` with new PAT

## Backups

Hello Zenno production DB at the moment of containment, in two locations:
- `~/Dropbox/backups/supabase-incident-2026/` (primary)
- `~/security-investigations/260503-supabase-vercel/db-backups/` (redundant, MD5-verified)

## Footgun: SvelteKit + Vercel build-time env vars

If you ever rotate `PUBLIC_*` env vars again, **update Vercel's project-level env vars first**, then redeploy. The `-e KEY=VALUE` flag in `scripts/prod/deploy_frontend.sh` only sets runtime env, which is invisible to `$env/static/public` imports. The fix from this session was:

```bash
# Read new value from .env.prod, push it to Vercel project settings:
NEW_KEY=$(grep '^PUBLIC_SUPABASE_ANON_KEY=' .env.prod | cut -d'=' -f2-)
vercel env rm PUBLIC_SUPABASE_ANON_KEY production
echo "$NEW_KEY" | vercel env add PUBLIC_SUPABASE_ANON_KEY production
# Then redeploy via ./scripts/prod/deploy.sh
```

A cleaner long-term fix would be to extend `deploy_frontend.sh` to also pass `--build-env` flags, or just remove the `-e` injection and rely on Vercel project env vars exclusively.

## What changed for the dual-mode auth

`backend/utils/auth_utils.py`:

```python
_jwks_client: Optional[PyJWKClient] = None

def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
    return _jwks_client


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    unverified_header = jwt.get_unverified_header(token)
    alg = unverified_header.get("alg", "")
    if alg == "HS256":
        # legacy path
        payload = jwt.decode(token, SUPABASE_JWT_SECRET.get_secret_value().strip(),
                             algorithms=["HS256"], audience="authenticated")
    elif alg in ("ES256", "RS256", "EdDSA"):
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=[alg],
                             audience="authenticated")
    else:
        return None
    return payload
```

The HS256 branch can be removed once `SUPABASE_JWT_SECRET` is also dropped from `.env.prod` (any time now — no in-flight HS256 tokens remain since the legacy secret is revoked).

## Outstanding work

See `TODO.md` (top section) for the live list.
