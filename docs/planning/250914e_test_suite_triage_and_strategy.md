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

## Critique (strengthen the plan)

- **Strengths**: Focuses on integration-first value, targets real failure modes (missing blueprint, auth, external services), and proposes low-effort, high-impact harness fixes.
- **Concerns**:
  - Some tests import `backend.views.*` which breaks when `pythonpath=.`; this isn’t noted. Standardize imports to `views.*` in tests.
  - The auth bypass sets a minimal `g.profile`; ensure it matches code paths that expect fields like `id` to avoid None-related errors.
  - Pruning guidance is good but lacks explicit de-duplication targets (e.g., multiple delete/rename tests across resources doing the same assertion).
  - CI env assumptions (ICU dictionaries) should be explicitly handled with skips to avoid flaky failures.
- **Alternatives**:
  - Instead of bypassing auth globally, parametrize an auth fixture to allow opt-in auth tests where needed; default remains bypassed.
  - Consider a minimal API smoke matrix using `pytest.mark.parametrize` to reduce repetitive endpoint tests.
- **Recommendations**:
  - Replace remaining `from backend.views.*` imports in tests with `from views.*` (and `from backend.views.*` for API should become `from views.*_api`).
  - Keep the autouse auth bypass but document an opt-out marker (e.g., `@pytest.mark.require_auth`) for dedicated auth tests that monkeypatch differently.
  - Add explicit `@pytest.mark.skipif` guards around zh/ja segmentation when ICU dicts are unavailable.
  - As part of pruning, retain: 1 list, 1 detail, 1 write-action, 1 API happy path, 1 failure path per resource; drop duplicates.
- **Questions**:
  - Do we need any end-to-end test with actual token validation, or is route-level behavior sufficient for now?
  - Which exact endpoints benefit most from negative-path tests beyond 401 (e.g., 404/422 bodies)?

## References

- `backend/docs/TESTING.md` – integration-first section and harness snippets (blueprint registration, auth bypass, TTS mocking).


