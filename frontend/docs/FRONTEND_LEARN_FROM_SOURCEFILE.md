# Learn from Sourcefile

## Introduction

The Learn page provides an end-to-end practice flow for a single sourcefile. It surfaces priority words (with etymologies) and then runs an audio sentence flashcard session. Generation now persists sentences and audio for reuse on subsequent visits.

## See also

- `SOURCEFILE_PAGES.md` — Sourcefile tabs structure and navigation
- `../../backend/views/learn_api.py` — Backend endpoints for summary and generation
- `../../backend/docs/DATABASE.md` — Data model reference (Lemma, Sentence, etc.)
- `../../backend/prompt_templates/generate_sentence_flashcards.jinja` — Prompt used to generate sentences
- `../../backend/prompt_templates/metadata_for_lemma.jinja` — Prompt used to fill lemma metadata
- `ENHANCED_TEXT.md` — How interactive text/word links work elsewhere
- `KEYBOARD_SHORTCUTS.md` — Keyboard shortcuts reference for Learn and flashcards
- `../../docs/planning/250915a_sourcefile_learn_flow_mvp.md` — Planning notes and future stages
 - `../../docs/reference/libraries/p-queue.md` — Queue-based concurrency used for background warming

## Principles and key decisions

- Separate, non-invasive flow: lives under the sourcefile route; existing flashcards unchanged
- Always-on persistence: sentences and audio are saved on generation with provenance `learn`, and reused on subsequent visits for the same sourcefile
- Warm missing lemma metadata as needed to keep the flow snappy
- Batch-generate all sentences up-front; then practice with low latency between cards
- Serve persisted audio via `/api/lang/sentence/{code}/{id}/audio` URLs (no base64 in responses)
- Shuffle the practice deck at session start for varied repetition (generation orders easy→hard; shuffle trades sequence for variety)

## Current state, target state, migration status

- Current State: Page at `/language/{code}/source/{dir}/{file}/learn` with persistence and reuse
- Target State: Possible future batch/session tracking; integration into main flashcards flow (deferred)
- Migration Status: Persistence enabled; batch/session object explicitly deferred

## Architecture and data flow (high level)

- Frontend route: `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`
- On load:
  - Calls `GET /api/lang/learn/sourcefile/{code}/{dir}/{file}/summary?top=K` to fetch priority lemmas. Missing metadata fields may be generated on-demand server-side
  - Fetches source text for showing short context next to lemmas
  - Optionally warms lemma metadata in the background (limited concurrency)
  - Optionally begins preparing a practice deck in the background (calls `POST /generate` once)
- On “Start practice”:
  - Uses a pre-prepared deck if available; otherwise calls `POST /generate`
  - Backend first reuses persisted sentences for this sourcefile, then tops up generation and persists
  - Deck is shuffled client-side for each session start
  - Audio is preloaded; navigation between stages/cards is instant

## UI behavior

- Priority Words panel:
  - Compact list of top-K lemmas with translations and one-at-a-time detail view
  - Shows etymology and wordforms present in the sourcefile when available
  - “Ignore” removes a lemma from this session (auth required)
  - Arrow keys browse words before practice starts
- Practice panel:
  - Three-stage card: 1) audio only → 2) show sentence → 3) show translation
  - Controls: large buttons for mobile; keyboard shortcuts: Left = previous stage/play, Right = next stage, Enter = next card
  - Deck order is shuffled per session start

## API endpoints (backend)

- Summary
  - `GET /api/lang/learn/sourcefile/{code}/{dir}/{file}/summary?top=K`
  - Returns: `{ lemmas: [{ lemma, translations[], etymology?, commonality?, guessability?, part_of_speech? }], meta: { durations } }`
  - Ranking heuristic (MVP): `difficulty_score = (1 - guessability) + (1 - commonality)`
- Generate sentences + audio (persist + reuse)
  - `POST /api/lang/learn/sourcefile/{code}/{dir}/{file}/generate`
  - Body: `{ lemmas: string[], num_sentences: number, language_level: null | "A1"|… }`
  - Returns: `{ sentences: [{ sentence, translation, used_lemmas[], language_level?, audio_data_url }], meta: { durations } }` where `audio_data_url` is a streaming URL

## Performance and warming

- Lemma metadata warming: client fires low-priority, concurrent requests to fill missing metadata
- Background deck preparation: the page may pre-generate a deck while the user reviews words
- Audio preloading: streaming URLs are preloaded to minimize delays during practice
 - Concurrency is managed with p-queue; see `../../docs/reference/libraries/p-queue.md`

## Error handling

- Summary and generation errors render a visible alert in the UI
- Not logged-in behavior: warming/ignore gracefully no-op if auth is missing

## Defaults and configuration (MVP)

- Summary: `top = 20`
- Generate: `num_sentences = 10`, `language_level = null` (server may choose defaults)
- Deck: shuffled on start; repeat visits re-generate and re-shuffle

## Limitations

- Batch/session object is deferred; we do not support exact replay of a prior Learn run yet

## Planned future work

- Background warming improvements (client-initiated vs server-initiated)
- Batch tracking for exact session replay and cleanup
- External storage for audio if DB size becomes a concern
- Progress tracking and adaptive session continuation

## Implementation references

- Frontend page: `../src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`
- Header link: `../src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte`
- Backend view: `../../backend/views/learn_api.py`
- Audio generation: `../../backend/utils/audio_utils.py`
- Lemma metadata utilities: `../../backend/utils/store_utils.py`

Note: We intentionally defer a dedicated batch/session model for now. If added later, this doc should be updated with retrieval and cleanup semantics.
