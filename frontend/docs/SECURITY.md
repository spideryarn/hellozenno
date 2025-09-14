# Frontend Security

## Scope
- SvelteKit app (Vite) with Supabase client

## Practices
- Keep `@sveltejs/kit`, `vite`, `jsdom` current
- Avoid exposing dev servers; do not run with `--host` on untrusted networks
- Use `npm ci` for reproducible installs

## Scanning
- Prod-only audit locally: `npm audit --omit=dev`

## CI Gate
- GitHub Actions job runs `npm audit --omit=dev --audit-level=high`
- Build fails if high/critical vulns detected in prod deps

## Local Commands
```bash
cd frontend
npm ci --ignore-scripts
npm audit --omit=dev
```

## Incident/Updates
- Fix critical within 48h; high within 7 days
- Commit `package.json`/`package-lock.json`; re-run CI
