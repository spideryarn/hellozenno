### Configuration overview

Backend and frontend read configuration from code defaults, with optional environment overrides. This keeps local = production by default and avoids hard dependence on platform env setup.

### See also
- `backend/config.py` — code defaults for segmentation and known‑word search; DB pool and limits
- `backend/utils/segmentation.py` — selects engine using config defaults; optional env overrides
- `backend/utils/vocab_llm_utils.py` — known‑word fast path uses config default; env override optional
- `frontend/src/lib/config.ts` — requires `VITE_API_URL` in production; uses localhost in dev
- `backend/vercel.json` — Serverless function config and excluded files
- `scripts/prod/deploy.sh` — orchestration for API and frontend deploys; health checks
- Planning: `docs/planning/250914c_multilingual_word_segmentation_for_hover_links.md`
- Conversation: `docs/conversations/250914b_multilingual_segmentation_strategy_icu_only.md`

### Principles, key decisions
- Prefer to use config.py and config.ts rather than environment variables for feature flags
- Maintain parity: the same `backend/requirements.txt` and defaults run locally and in prod.

### Defaults and overrides
- Segmentation defaults (backend):
  - Global: `SEGMENTATION_DEFAULT = "naive"`
  - Per‑language: `SEGMENTATION_PER_LANG_DEFAULTS = { "th": "pythainlp" }`
  - Thai engine: `PYTHAINLP_ENGINE_DEFAULT = "newmm"`
  - Override via env: `SEGMENTATION_TH`, `SEGMENTATION_DEFAULT`, `PYTHAINLP_ENGINE`
- Known‑word search (backend):
  - Default: `RECOGNITION_KNOWN_WORD_SEARCH_DEFAULT = True`
  - Override via env: `RECOGNITION_KNOWN_WORD_SEARCH=0|1`
- Frontend API base URL:
  - Dev: `http://localhost:3000`
  - Prod: must set `VITE_API_URL` (in Vercel project settings)

### Troubleshooting
- If Thai links don’t appear in prod: confirm backend logs show `[segmentation]` counts; engine should be `pythainlp` when ICU is absent. Known‑word fast path can be toggled via env if needed.

