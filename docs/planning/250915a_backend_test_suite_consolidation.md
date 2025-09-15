# Backend Test Suite Consolidation

## Goal, context

We want a small number of high-value, robust backend tests that catch regressions. Prioritize integration (blueprints, templates, DB) over extensive unit tests and external service mocks. Remove or consolidate low-signal tests. Stabilize CI by avoiding external calls and brittle expectations.

Recent work: fixed collection blockers, registered missing blueprints in tests, added auth bypass and global TTS mock, aligned delete endpoints to API (204), updated docs and triage notes. Current suite: many pass; remaining failures tied to (1) residual external LLM calls, (2) URL expectation drift, (3) request/app context dependencies, (4) a few template endpoints still pointing to view deletes.

## References

- backend/docs/TESTING.md: Integration-first strategy + common failure modes.
- docs/planning/250914e_test_suite_triage_and_strategy.md: Triage table and keep/drop guidance.
- backend/tests/backend/conftest.py: Test app setup, auth bypass, TTS mock, test DB bootstrap.
- utils/vocab_llm_utils.py, utils/audio_utils.py: External service touchpoints and contexts.
- views/*_views.py, *_api.py: View/API endpoint pairs and URL shapes.

## Principles, key decisions

- Favor a lean integration suite hitting real blueprints/routes; minimal mocking for non-deterministic/external services only.
- Align tests with current API semantics (e.g., delete -> 204 No Content).
- Don’t assert literal substrings of URLs when `build_url_with_query` can be used; avoid brittle path fragments.
- Never hit Anthropic/OpenAI/ElevenLabs in tests; rely on autouse mocks.
- Keep 1–2 happy-paths per resource and 1 failure case; remove duplicates.

## Stages & actions

### Stabilize external service calls
- [x] Extend autouse GPT mock to patch both `utils.vocab_llm_utils.generate_gpt_from_template` and `gjdutils.llm_utils.generate_gpt_from_template` reliably across all tests.
  - Acceptance: No Anthropic/OpenAI requests in test logs; related failures disappear.
- [~] Add a focused fixture for tests that call `ensure_model_audio_data` without HTTP to push `app_context()` where needed (or refactor those tests to use the client to trigger within request context).
  - Acceptance: `test_ensure_model_audio_data` passes without context errors.

### Align URLs and templates
- [x] Update tests that assert literal route substrings (e.g., `/lang/`) to either use `build_url_with_query` or adjust to `/language/`.
  - Acceptance: `test_phrase_url_generation` uses helper; no literal mismatch.
- [x] Ensure templates use API endpoints for destructive actions (phrases too), mirroring lemmas/wordforms.
  - Acceptance: Phrase template builds `phrase_api.delete_phrase_api` URL; no BuildError.

### Adjust expectations to current behavior
- [ ] Update tests expecting redirects after deletes to expect 204 (wordform, lemma, phrase) consistently where APIs return 204.
  - Acceptance: All delete tests pass with 204.
- [ ] Loosen assertions tied to specific 404 messages to status-only where appropriate (e.g., flashcards random when empty).
  - Acceptance: Tests pass regardless of wording.

### Prune and consolidate low-signal tests
- [ ] Identify and remove redundant unit tests duplicating integration coverage (wordform/lemma search variations, multiple sort variants) while keeping one representative per category.
  - Acceptance: Net reduction in test count with maintained coverage; CI stable.
- [ ] Keep URL registry tests minimal (endpoint_for, one or two build checks) and avoid brittle TS-vs-Flask strictness unless needed.
  - Acceptance: Registry tests validate basics without frequent churn.

### Code adjustments to stabilize tests
- [x] Exclude lookup keys from updates in `utils/store_utils.save_lemma_metadata` when calling `Lemma.update_or_create` to avoid duplicate kwargs (e.g., `lemma`).
  - Detail: `BaseModel.update_or_create` merges `lookup` and `updates` on create. If `updates` contains `lemma`/`target_language_code`, Peewee receives duplicate keywords and can error. Filter `metadata` to remove lookup fields before passing as `updates`.
- [x] Align `utils.vocab_llm_utils.quick_search_for_wordform` output shape with `utils.word_utils.find_or_create_wordform` expectations (enhanced results structure) or adapt the consumer to the flat schema.
  - Decision: Standardize on the enhanced structure: `{ target_language_results: { matches: [...] , possible_misspellings }, english_results: { matches: [...], possible_misspellings } }`. Tests already mock this shape, which is why they pass despite the current flat implementation.
- [x] Fix `get_or_create_wordform_metadata` to pass the correct target language code (not language name) to `save_wordform_metadata`.
  - Detail: Replace erroneous saves using `target_language_name` with `target_language_code` when persisting lemma/wordform metadata.
- [x] Update `views/auth_views.profile_page_vw` / `templates/profile.jinja` so the template iterates a mapping (or adapt to current `SUPPORTED_LANGUAGES` type) instead of calling `.items()` on a set.
  - Decision: Build and pass `{code: name}` via `get_all_languages()`; keep `SUPPORTED_LANGUAGES` as a set in config.
- [x] Enforce sourcedir slug max length (<= 100) in `sourcedir_api.create_sourcedir_api` and truncate when necessary to satisfy tests and UX constraints.
  - Decision: Set `SOURCEDIR_SLUG_MAX_LENGTH = 100`; use `slugify(path)[:SOURCEDIR_SLUG_MAX_LENGTH]` consistently for duplicate checks and creation. Collisions remain 409 for now; suffix mechanism deferred (see Later-stage improvements).
- [x] Re-expose or relocate `process_sourcefile_content` (currently not in `views.sourcefile_views`) so tests can patch it, or update tests to patch the new location.
  - Decision: Update tests to patch `utils.sourcefile_utils.process_sourcefile` directly; avoid reintroducing a view alias.
- [x] Ensure create-from-text returns a slugified filename (e.g., `test-title.txt`) to match route expectations.
- [ ] Clarify `ensure_model_audio_data` / `get_or_create_sentence_audio` behavior when auth/request context is missing; optionally offer an explicit test bypass.
  - Decision: Add a test fixture to push `test_request_context` and set `g.user` for non-Sentence audio generation paths.
- [ ] Audit and normalize naming like `VALID_target_language_codeS` for consistency.

### Tests to remove/adjust
- [x] Remove the edge-case favicon trailing-slash test (`GET /favicon.ico/`).
  - Rationale: We don’t support trailing slash for files; keep only `/favicon.ico`. Eliminates a brittle edge-case assertion.

### Health checks and documentation
- [ ] Re-run full backend tests locally; iterate until green or a small, well-understood set remains.
  - Acceptance: Majority green; any remaining failures documented with rationale.
- [ ] Update backend/docs/TESTING.md with any fixture changes (GPT mock extension, context fixture for audio) and template endpoint conventions.
  - Acceptance: Doc reflects the final approach succinctly.
- [ ] Move this doc to `planning/finished/` when done and summarize key deltas.
  - Acceptance: Summary exists and doc is archived.

## Progress

- Failures reduced from ~30 to 14 (157 passing, 9 skipped), with most external LLM call failures eliminated by autouse mocks.
- Implemented global LLM mock across both `utils.vocab_llm_utils` and `gjdutils.llm_utils`; global TTS mock extended to also patch `utils.audio_utils.outloud_elevenlabs`.
- Fixed endpoint drift in tests (`endpoint_for` expectation) and template references (`user_views.*` → `auth_views.*`).
- Updated several tests to patch `quick_search_for_wordform` at the correct import path and to assert against current behavior (render 200 instead of redirect for single-match flows).
- Adjusted some smoke tests to be less brittle on status codes where redirects/content differ in test app vs prod.
- Removed favicon trailing-slash test from the suite.
- Captured decisions for lemma save filtering, quick_search schema standardization, sourcedir slug length enforcement, profile languages mapping, and an audio context fixture.

### Remaining failure clusters (high-level)

- Metadata save path: `update_or_create` called with overlapping keys (lookup + updates) causing Peewee errors.
- Sourcefile flow gaps: ensure image/text extraction is mocked or provided so `text_target` is set before word extraction; status codes for invalid/oversize uploads.
- Lemma delete cascade check: verify cascade is effective or adjust test to account for wordform existence criteria post-delete.

### Next steps (shortlist)

1) Fix `save_lemma_metadata` update-or-create usage; re-run suite.
2) Normalize quick-search response vs consumer; re-run suite.
3) Re-expose/move `process_sourcefile_content` and update tests to new path; ensure create-from-text slugifies filename and enforce sourcedir slug length.
4) Update profile template or data shape for languages list.

## Later-stage improvements

- Implement a general slug collision suffix mechanism across models with slug fields (`Sourcedir`, `Sourcefile`, `Sentence`, `Phrase`).
  - Approach: Add a reusable helper `ensure_unique_slug(model_cls, base_slug, *, scope_filters: dict | None = None, max_length: int)` that:
    1. Truncates base slug to `max_length`.
    2. Checks uniqueness under optional scoping (e.g., per `target_language_code` or `sourcedir`).
    3. If taken, appends `-2`, `-3`, ... truncating the base to leave room for the suffix, and retries until unique.
  - Integration: Call from each model’s `save()` when generating slugs, and from create APIs prior to insert to reduce DB constraint churn.
  - Tests: Parametrized cases for collisions (simple, truncated base, scoped uniqueness).
