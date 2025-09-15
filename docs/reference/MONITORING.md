# Monitoring and Performance

Status: draft • Last updated: 2025-09-15

This guide covers runtime observability, common bottlenecks, and resource limits for HelloZenno in development and production.

## Dashboards

- Backend API (Vercel project: hz_backend)
  - Deployment status, function logs, cold starts, and invocations
- Frontend (Vercel project: hz_frontend)
  - Build size, asset timings, errors
- Supabase
  - Project metrics (connections, query performance, egress)

## Logs

- Local development
  - Backend: `logs/backend.log` (Loguru format, ~200-line truncation)
  - Frontend: `logs/frontend.log`
- Production
  - Vercel function logs via dashboard or CLI
  - Note: `vercel logs --json` can be noisy/limited; prefer dashboard for filtering

## Database performance

- Pooling
  - Use Supabase transaction pooler (port 6543) in production
  - Prefer short-lived transactions; avoid long-held connections in serverless
- ORM
  - Peewee: index frequently-filtered columns; avoid N+1 queries by prefetching
- Egress
  - Monitor egress on Supabase and avoid transferring large JSON blobs unnecessarily
  - See planning: `docs/planning/250420_data_egress_issue.md`

## Common bottlenecks

- LLM generation timeouts (Vercel ~30s)
  - Pre-warm content where possible; trigger background warming after initial loads
- Audio processing (TTS)
  - External TTS providers can have cold starts; cache audio and throttle requests
- Large sourcefile processing
  - Chunk operations and stream results; avoid single long-running requests
- Frontend bundle size
  - Keep an eye on `npm run build` output; split routes and defer heavy libs

## Resource limits

- Vercel function timeout ~30s (plan-dependent)
- Supabase free tier limits (connections, egress)
- Rate limiting where applicable on external services

## Quick checks

- Check Vercel deploys for error spikes and cold starts
- Tail `logs/backend.log` locally when reproducing backend issues
- Confirm Supabase connection counts and slow query logs for DB issues


