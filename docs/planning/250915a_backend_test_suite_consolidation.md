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
- [ ] Extend autouse GPT mock to patch both `utils.vocab_llm_utils.generate_gpt_from_template` and `gjdutils.llm_utils.generate_gpt_from_template` reliably across all tests.
  - Acceptance: No Anthropic/OpenAI requests in test logs; related failures disappear.
- [ ] Add a focused fixture for tests that call `ensure_model_audio_data` without HTTP to push `app_context()` where needed (or refactor those tests to use the client to trigger within request context).
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

### Health checks and documentation
- [ ] Re-run full backend tests locally; iterate until green or a small, well-understood set remains.
  - Acceptance: Majority green; any remaining failures documented with rationale.
- [ ] Update backend/docs/TESTING.md with any fixture changes (GPT mock extension, context fixture for audio) and template endpoint conventions.
  - Acceptance: Doc reflects the final approach succinctly.
- [ ] Move this doc to `planning/finished/` when done and summarize key deltas.

## Notes / risks
- Some view tests still trigger generation code paths; ensure autouse GPT mock covers all import paths.
- Request/app context needs care: prefer client-driven routes; otherwise use `app_context()` within tests.
- Keep an eye on unique constraints and FKs requiring a dummy `auth.users` row (created in test DB bootstrap).
