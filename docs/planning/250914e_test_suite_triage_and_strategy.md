# Test Suite Triage and Strategy (Backend)

Author: Greg • Date: 2025-09-14

Goal: small, high-value, robust tests that catch regressions; prioritize integration flows; avoid excessive mocking.

## Triage Table (most important first)

| Category / examples | Priority | Why breaking | Keep? | Ease | Notes |
|---|---|---|---|---|---|
| Template BuildError in views (e.g., views_smoke, wordform/phrase/sentence views) | High | Test app missed `languages_views_bp`; `base.jinja` uses `url_for('languages_views.languages_list_vw')` | Keep 1–2 smoke tests per blueprint | Easy | Register `languages_views_bp` in `tests/backend/conftest.py` |
| 401 on API endpoints (delete/rename/generate across sentence/wordform/sourcefile) | High | `@api_auth_required` with no test auth | Keep a couple per resource; drop duplicates | Easy (bypass) | Add autouse fixture to bypass `_attempt_authentication_and_set_g` |
| External TTS during tests (e.g., ElevenLabs voice not found) | Medium | Network call in tests | Keep | Easy | Autouse mock for `outloud_elevenlabs` to write dummy MP3 |
| URL registry checks | Medium | Registry built from test app missing some blueprints | Keep minimal | Easy | Resolves when all blueprints are registered |
| Segmentation zh/ja recognition | Low | ICU dictionaries may be unavailable; or earlier 401 | Keep | Easy | Skips in that case; auth bypass resolves 401 earlier |
| Low-value edges (e.g., favicon with trailing slash) | Low | Minor routing/linking | Consider drop | Easy | Low product signal |

## Guidance (from requirements and current state)

- Prefer integration tests that exercise real blueprints/routes and templates, not internal template structure or ORM internals.
- Keep a lean set of representative cases per resource (languages/search/wordform/lemma/phrase/sourcedir/sourcefile/sentence/flashcard). Remove redundant parametric copies.
- Avoid network/third-party calls in tests. Use local mocks for TTS/Whisper/YouTube only when behavior is essential to the test; otherwise, rely on route-level behavior and DB state.

## Concrete Changes Applied (test harness)

- Registered `languages_views_bp` in `tests/backend/conftest.py` to remove template `url_for` BuildErrors.
- Added autouse fixture to bypass API auth: sets a dummy user/profile so `@api_auth_required` passes.
- Added autouse fixture to mock ElevenLabs TTS globally: any code path that tries to generate audio will write `b"test audio data"`.

These bring the suite closer to an integration-first baseline and turn many environment-dependent failures into passes.

## Next Pass: Prune and Consolidate

- Identify duplicate tests per resource and keep only a small set covering: list view, detail view, one write action (delete or rename), one API happy path, and one failure path.
- Remove tests that re-assert ORM-level validations already enforced by models unless regression-prone.
- Keep URL registry smoke checks but avoid brittle string assertions beyond presence of key endpoints.

## References

- `backend/docs/TESTING.md` – now includes an integration-first section and snippets for common fixes (blueprint registration, auth bypass, TTS mocking).


