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
- [ ] Update tests that assert literal route substrings (e.g., `/lang/`) to either use `build_url_with_query` or adjust to `/language/`.
  - Acceptance: `test_phrase_url_generation` uses helper; no literal mismatch.
- [ ] Ensure templates use API endpoints for destructive actions (phrases too), mirroring lemmas/wordforms.
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
- [ ] Exclude lookup keys from updates in `utils/store_utils.save_lemma_metadata` when calling `Lemma.update_or_create` to avoid duplicate kwargs (e.g., `lemma`).
- [ ] Align `utils.vocab_llm_utils.quick_search_for_wordform` output shape with `utils.word_utils.find_or_create_wordform` expectations (enhanced results structure) or adapt the consumer to the flat schema.
- [ ] Fix `get_or_create_wordform_metadata` to pass the correct target language code (not language name) to `save_wordform_metadata`.
- [ ] Update `views/auth_views.profile_page_vw` / `templates/profile.jinja` so the template iterates a mapping (or adapt to current `SUPPORTED_LANGUAGES` type) instead of calling `.items()` on a set.
- [ ] Enforce sourcedir slug max length (<= 100) in `sourcedir_api.create_sourcedir_api` and truncate when necessary to satisfy tests and UX constraints.
- [ ] Re-expose or relocate `process_sourcefile_content` (currently not in `views.sourcefile_views`) so tests can patch it, or update tests to patch the new location.
- [ ] Ensure create-from-text returns a slugified filename (e.g., `test-title.txt`) to match route expectations.
- [ ] Accept or redirect `GET /favicon.ico/` with trailing slash to avoid false negatives in edge-case tests.
- [ ] Clarify `ensure_model_audio_data` / `get_or_create_sentence_audio` behavior when auth/request context is missing; optionally offer an explicit test bypass.
- [ ] Audit and normalize naming like `VALID_target_language_codeS` for consistency.

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

### Remaining failure clusters (high-level)

- Metadata save path: `update_or_create` called with overlapping keys (lookup + updates) causing Peewee errors.
- Search contract mismatch: `find_or_create_wordform` expects enhanced results; current quick-search returns flat schema.
- Sourcefile flow gaps: missing `process_sourcefile_content` symbol in `views.sourcefile_views`; slugification/slug-length behavior and 204 vs 200 expectations.
- Template/data mismatch: `SUPPORTED_LANGUAGES` consumed as mapping in `profile.jinja`.
- Minor routing edge case: `/favicon.ico/` with trailing slash returns 404.

### Next steps (shortlist)

1) Fix `save_lemma_metadata` update-or-create usage; re-run suite.
2) Normalize quick-search response vs consumer; re-run suite.
3) Re-expose/move `process_sourcefile_content` and update tests to new path; ensure create-from-text slugifies filename and enforce sourcedir slug length.
4) Update profile template or data shape for languages list.
5) Decide on favicon trailing-slash policy (accept or redirect) and align test.
