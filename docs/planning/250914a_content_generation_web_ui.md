### Goal, context

Build a simple, logged-in web UI to generate AI Sourcefile content, mirroring the CLI’s behavior but scoped to the current sourcedir. Keep it synchronous for now and add complexity later.

- Any logged-in user can trigger generation
- Location: Sourcedir page `/language/{target_language_code}/source/{sourcedir_slug}` → Add Files → “Generate AI Content…” (modal)
- Inputs: title (optional), language_level (auto or specific)
- On success: redirect to new Sourcefile’s Text view
- Later: add “Import from URL” (existing API) and optional “search the web” mode


### References

- `backend/docs/CONTENT_GENERATION.md`: overview and CLI usage
- `backend/utils/generate_sourcefiles.py`: core generation functions (topic, content, level choice, sourcedir create)
- `backend/views/sourcefile_api.py`: existing Sourcefile APIs; patterns, auth decorator, and “create_from_url” endpoint
- `backend/utils/sourcefile_utils.py` → `_create_text_sourcefile`, processing helpers
- `backend/utils/lang_utils.py` → `validate_language_level`, `get_language_name`
- `backend/utils/auth_utils.py` → `api_auth_required` decorator; `g.user` and `g.profile`
- `backend/api/index.py` → TS route generation `utils/url_registry.generate_typescript_routes`
- `frontend/src/lib/api.ts` → `apiFetch`, `getApiUrl` and auth header injection via Supabase session
- `frontend/src/lib/generated/routes.ts` → `RouteName` enums (auto-generated from Flask)
- `frontend/src/routes/language/[target_language_code]/sources/+page.svelte` → language nav pattern and actions bar
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte` → Add Files dropdown & new Generate modal
- `frontend/src/routes/+layout.server.ts` and `frontend/src/hooks.server.ts` → session plumbing for auth
- `frontend/src/lib/navigation.ts` → typed page URLs and profile redirect helpers
- `backend/utils/url_registry.py` → `endpoint_for`, route registry and TS generation


### Principles, key decisions

- Start minimal; ship value early, layer features later
- Synchronous end-to-end (no background queue) within timeout budget
- Mirror CLI defaults and auto-selection logic where sensible
- Scope by language route (no cross-language auto selection)
- Any logged-in user may generate content
- Include all CEFR levels in manual selection; default to Auto
- UX: keep forms short; show redirect on success
- Reuse existing backend helpers where possible (import functions from `generate_sourcefiles.py`)
- Type-safe API calls via generated route constants


### Stages & actions

#### Backend: generation API endpoint
- [x] Add `POST /api/lang/sourcefile/<target_language_code>/generate` in `backend/views/sourcefile_api.py`
  - [x] Auth: `@api_auth_required`
  - [x] Request body: `{ title?: string, language_level?: 'A1'|'A2'|'B1'|'B2'|'C1'|'C2', sourcedir_path?: string }`
  - [x] Behavior:
    - Resolve `target_language_code` from path
    - If `language_level` missing → `choose_language_level(code)`
    - If `title` missing → `generate_topic(code, sourcedir_path, language_level)`
    - Ensure sourcedir via `get_or_create_ai_sourcedir(code, sourcedir_path || DEFAULT)`
    - Generate content via `generate_content(code, title, language_level)`
    - Create Sourcefile via `_create_text_sourcefile` with metadata (model, tags, ai_generated=True)
    - Handle filename collision by appending a timestamp
  - [x] Response (200): `{ sourcedir_slug, sourcefile_slug, url_text_tab }` (via `url_for(endpoint_for(inspect_sourcefile_text_vw))`)
  - [x] Errors: 400 for invalid `language_level` via `validate_language_level`; 500 with message
- [x] Update URL registry (auto) and TS route constants in dev
  - Route constant: `RouteName.SOURCEFILE_API_GENERATE_SOURCEFILE_API`
- [ ] Add backend tests: `tests/backend/test_generate_sourcefile_api.py`
  - [ ] Happy path creates file and returns slugs/url
  - [ ] Validates language level and auth required


#### Frontend: sourcedir modal
- [x] Add “Generate AI Content…” to Add Files dropdown in `source/[sourcedir_slug]/+page.svelte`
  - [x] Auth-gated (only visible when logged in)
  - [x] Modal fields:
    - Title (optional)
    - Language Level: select → default “Auto (recommended)”; options A1–C2
  - [x] Submit: call API via `apiFetch(RouteName.SOURCEFILE_API_GENERATE_SOURCEFILE_API, { target_language_code }, body)` including `sourcedir_path = sourcedir.path`; pass Supabase client for auth
  - [x] On success: redirect to returned `url_text_tab`
  - [x] Show structured errors inline
- [x] Removed “Generate” pill from `sources/+page.svelte`


#### Frontend: navigation
- [x] No separate nav pill; entry point is the sourcedir’s Add Files dropdown


#### Validation and tests
- [x] Light Playwright flow (if feasible with test creds): login → generate → redirect visible (smoke test added)
- [x] Backend tests for generate API: auth required, happy path, level validation
- [ ] Smoke test manually in browser


#### Docs and logging
- [x] Update `backend/docs/CONTENT_GENERATION.md` with web UI usage snippet (Sourcedir → Add Files → Generate)
- [ ] Note new endpoint in `backend/docs/URL_REGISTRY.md` examples if helpful
- [x] Add minimal log lines around generation start/finish and parameters


#### Later stage: “Search the web” option
- [ ] Backend: extend generate API (or add `/generate_from_search`) with `{ use_web_search: boolean, query?: string }`
  - [ ] May require minimal prompt modifications
  - [ ] Persist origin metadata: search terms and chosen URL(s)
- [ ] Frontend: add checkbox and optional query field under Advanced


### Acceptance criteria

- [ ] Logged-in user can open a sourcedir and use Add Files → “Generate AI Content…”
- [ ] Submitting with only Level=Auto generates content and redirects to the new file’s Text tab
- [ ] Manual level selection A1–C2 is respected; stored on Sourcefile
- [ ] Generation occurs inside the currently viewed sourcedir
- [ ] API enforces auth and returns expected JSON (slugs + redirect URL)
- [ ] Type checks pass; no new linter errors; smoke test OK
- [ ] Later: Advanced “Import from URL” surfaced on the same page and works end-to-end


### Risks and mitigations

- Synchronous generation timeout → keep prompts concise; consider increasing server timeout; defer long tasks
- Rate limits / API keys → guardrails and friendly errors; logs in `/logs/backend.log`
- Filename collisions → `_create_text_sourcefile` handles collisions or we append timestamp
- Internationalized titles/slugs → rely on existing slugify and DB constraints


### Open questions

- Label for nav: “Generate” vs “AI Generate”? (defaulting to “Generate”)


### Progress log

- 2025-09-14
  - Backend: Implemented `POST /api/lang/sourcefile/<code>/generate` in `backend/views/sourcefile_api.py` with auth, validation, collision handling, and logging. Builds redirect via `url_for(endpoint_for(inspect_sourcefile_text_vw))`.
  - Frontend (initial): Added `language/[code]/generate` page (`+page.svelte`, `+page.server.ts`) with form and auth gate; uses `apiFetch` and `RouteName.SOURCEFILE_API_GENERATE_SOURCEFILE_API`.
  - Change: Moved UX to sourcedir page. Added “Generate AI Content…” to Add Files dropdown in `source/[sourcedir_slug]/+page.svelte` (modal). Removed Sources page “Generate” pill. Fixed auth header (use `data.supabase`) to resolve 401. On success, redirect to `url_text_tab`.
  - Tests: Added backend tests for generate API (auth required, happy path, level validation). Added minimal Playwright smoke test for the generate flow.
  - Docs: Updated `backend/docs/CONTENT_GENERATION.md` with new Sourcedir-based UI.

