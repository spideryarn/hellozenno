## Goal, context

Build a separate, non-invasive “Learn from Sourcefile” flow that:
- Shows the most important/difficult words from a given sourcefile with their etymologies
- Then runs a session of dynamically generated audio sentence flashcards that deliberately use multiple of those words, starting easier and getting harder

Constraints and preferences for v1:
- Do not alter existing flashcard routes/behavior; this lives on its own page/route
- Low latency once the flashcards start (ok to pay an upfront cost to prepare)
- Persistence now enabled: reuse persisted sentences and audio for the same sourcefile
- Generate lemma metadata if missing (allowed to write to DB for lemma metadata)
- Reuse existing machinery wherever possible


## References

- `backend/docs/FLASHCARDS.md` — Current flashcard behavior, keyboard shortcuts, filtering, endpoints (HTML and API) and CORS notes
- `backend/db_models.py` — Models: `Lemma` (has `etymology`, `commonality`, `guessability`, `language_level`, etc), `Wordform`, `Sentence`
- `backend/utils/store_utils.py` — `load_or_generate_lemma_metadata(…, generate_if_incomplete=True)` for backgroundable lemma metadata generation
- `backend/prompt_templates/metadata_for_lemma.jinja` — LLM prompt for full lemma metadata, including etymology, commonality, guessability
- `backend/prompt_templates/extract_tricky_wordforms.jinja` — LLM prompt for tricky/priority words extraction from text (optional seed for ranking)
- `backend/prompt_templates/generate_sentence_flashcards.jinja` — LLM prompt to generate multiple example sentences using provided lemmas
- `backend/utils/sentence_utils.py` — Utilities for generating/saving sentences, random selection; we’ll reuse patterns but not persist in v1
- `backend/utils/audio_utils.py` — `ensure_audio_data(text)` returns MP3 bytes; we’ll base64 → data URL for v1 (no persistence)
- Frontend components to reuse:
  - `frontend/src/lib/components/LemmaContent.svelte`, `LemmaDetails.svelte`, `LemmaCard.svelte` — to render lemma metadata incl. etymology
  - Existing flashcard Svelte UI patterns under `frontend/src/routes/language/[target_language_code]/flashcards/…` for big-button controls & shortcuts
  - Entry point location for Learn button: `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte`


## Principles, key decisions

- Keep existing flashcards untouched; introduce a new route (single page) under the sourcefile
- Always-on persistence of generated sentences/audio with provenance `learn`
- Allow generating lemma metadata if missing (writes `Lemma` rows), and prefer warming this upfront/background so the flashcard flow is snappy
- Batch-generate all sentences before starting the session using a “thinking mode” prompt that:
  - Maximizes coverage of the selected lemmas across the set
  - Allows the same word to reappear (ideally in varied forms)
  - Orders sentences from easier to harder (based on CEFR or heuristic)
- Serve audio as data URLs in v1 for simplicity
- Take guidance from existing flashcards implementation if appropriate (e.g. re authentication)


## Stages & actions

### Stage: MVP separate page, no persistence
- [x] Backend: Add ephemeral summary endpoint to rank lemmas for a sourcefile
  - Path: `GET /api/lang/learn/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/summary?top=K`
  - Behavior:
    - Collect candidate lemmas via `get_sourcefile_lemmas(target_language_code, sourcedir_slug, sourcefile_slug)`
    - For each lemma, fetch metadata with `load_or_generate_lemma_metadata(lemma, target_language_code, generate_if_incomplete=True)`; missing fields are generated on-demand
    - Ranking in v1: use a numeric heuristic: `difficulty_score = (1 - guessability) + (1 - commonality)` (LLM ranking deferred)
    - Response (ephemeral): a JSON summary only; no sentences or audio are created here. Fields per lemma: `lemma`, `translations[]`, `etymology?`, `commonality?`, `guessability?`, `part_of_speech?`. Also returns meta durations.
    - Defaults: Not included in v1 response; the client can pass `language_level` explicitly if needed
  - Acceptance:
    - Returns within a reasonable time (upfront wait is acceptable); handles missing metadata by generating it
    - 200 response includes at least `lemmas[]`, each with `lemma`, `translations`, `etymology` (possibly empty), `commonality`, `guessability`

- [x] Backend: Add ephemeral batch generation endpoint for sentences + audio
  - Path: `POST /api/lang/learn/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/generate`
  - Request body: `{ "lemmas": string[], "num_sentences": 10, "language_level": null | "A1"|… }`
  - Behavior:
    - Use a single LLM call via `generate_sentence_flashcards.jinja` with instructions to:
      - Cover as many of the provided lemmas as possible across the set
      - Reuse some lemmas in varied forms
      - Order sentences from easier to harder
    - For each resulting sentence, generate audio with `ensure_audio_data(sentence)`; base64-encode as `data:audio/mpeg;base64,…`
    - Return array: `{ sentence, translation, used_lemmas, language_level?, audio_data_url }[]`
    - Defaults: If `language_level` is not provided, default to the sourcefile’s `language_level` if present; otherwise omit
  - Acceptance:
    - 200 response with N sentences (default 10), each playable via returned data URL
    - End-to-end time for 10 sentences is acceptable for v1 (logged; we can optimize later)

- [x] Frontend: New single page route adjacent to sourcefile, leaves existing routes untouched
  - Path: `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`
  - Sections:
    - “Priority words” — shows ranked list with etymology (reuse `LemmaContent`/`LemmaDetails`/`LemmaCard`)
    - “Start practice” — button triggers `POST /generate`; after response, shows big flashcard UI
  - Entry point:
    - Add a “Learn (MVP)” button next to “Practice Flashcards” in `SourcefileHeader.svelte`, linking to the above route
  - Flashcard UI:
    - 3 stages (audio only → show sentence → show translation) with left/right/enter keys
    - Preload returned audio data URLs; render large buttons for mobile
  - Acceptance:
    - Page loads, displays top K words with etymologies if present
    - Clicking “Start practice” shows the first generated card and is responsive between cards

- [x] Minimal logging and error handling
  - Log durations for lemma warmup, LLM call, audio generation
  - Graceful UI errors when zero lemmas or zero sentences are produced

- [x] Light checks
  - Backend type/lint as per project norms
  - Frontend `npm run check`


### Stage: Background warming for lemma metadata (optional enhancement)
- [ ] Warm lemma metadata in background to reduce initial wait next time
  - Implementation: spawn an in-process background thread after `summary` request returns that iterates through lemmas calling `load_or_generate_lemma_metadata(..., generate_if_incomplete=True)`
  - Minimal status tracking (log-only) for v1 to stay simple
  - Acceptance: Subsequent visits to the same sourcefile have noticeably less metadata delay

  Notes/Suggestion (frontend-initiated warming):
  - Instead of spawning from the backend, trigger warming from the client after the `summary` load completes when the user is authenticated.
  - Mechanism: fire-and-forget requests to `POST /api/lang/lemma/{target_language_code}/{lemma}/complete_metadata` (or `GET /metadata` which auto-generates) with Supabase auth token.
  - Concurrency: limit to 2–3 concurrent requests and simple backoff; do not block UI.
  - Safety: silently skip on 401; log durations only. This reduces server-side thread complexity and keeps the page responsive.


- ### Stage: Persistence & reuse for Learn (added)
- [x] Add `Sentence.provenance` (default `manual`) and `Sentence.generation_metadata` (JSON)
- [x] Persist Learn-generated sentences and audio; provenance set to `learn`
- [x] Record `generation_metadata` including `{ used_lemmas, used_wordforms, order_index, prompt_version, tts_voice, source_context }`
- [x] Update Learn generate endpoint to first reuse existing persisted sentences for the same sourcefile, then top up by generating new ones; return streaming audio URLs
- [ ] (Later) Integrate with existing `/languages/{code}/flashcards` flow so Learn sentences appear in normal practice
  - Acceptance: User can revisit generated material via existing flashcards; no duplication issues

Investigation notes (models + persistence proposal):
- Current models are mostly fit: `Sentence`, `SentenceLemma`, `Lemma` already cover core needs; audio can use `Sentence.audio_data` initially.
- Recommended additions (see Very late stages below):
  - `Sentence.provenance` enum (`manual`, `imported`, `learn`, `llm_generated`) with default `manual`
  - `Sentence.generation_batch_id` nullable FK to new `GenerationBatch`
  - `Sentence.generation_metadata` JSON to store `{ used_lemmas, order_index, difficulty_score, prompt_version }`
  - `GenerationBatch` model capturing request context (language, source context, requested lemmas, prompt/template version, counts, created_by)
- Write migrations to add these fields and backfill `provenance = 'manual'` for existing data. Keep endpoints backward compatible; feature-flag writes initially.


### Stage: Observability and UX refinements
- [ ] Progress indicators for warmup and generation steps
- [ ] Stats: coverage of lemmas across session, CEFR ramp
- [ ] Allow user-adjustable K (top words), number of sentences, and difficulty range

- [x] Priority Words UI improvements
  - Each lemma title links to its main page in a new tab
  - Show a short context quote from the source text
  - List the wordform(s) present in this sourcefile for the lemma (as links)
  - Display part of speech inline after translations for compactness
  - Preview up to 2 example sentences and up to 2 mnemonics when available
  - Add an "Ignore" button (auth required) that marks the lemma ignored via API and removes it from the list
  - Filter ignored lemmas out of the set passed to the sentence generation endpoint
  - Remove hover/gradient effect that thickened dividers within Priority Words


### Stage: Replay-tracking and simple repeat prioritization
- [ ] Track per-card audio replays (left-button presses)
  - Frontend: increment a counter per displayed sentence ID/slug on each left press
  - Storage (v1-late): use `localStorage` under a session key (e.g., `hz_learn_progress:{sourcefile_slug}`)
  - Data captured: `{ sentence_id|hash, left_replay_count, revealed_sentence_dt, revealed_translation_dt }`
- [ ] Simple prioritization heuristic for continuing sessions
  - If user clicks “Continue practice”, build the next queue by weighting items with higher `left_replay_count` and slower progression to translation
  - Acceptance: User who continues sees more practice for the items they struggled with first


### Stage: Basic analytics (local only)
- [ ] Surface session stats to the user
  - Totals: number of flashcards practiced, average replays per card, distribution of replays
  - Hardest flashcards: top N by `left_replay_count` and longest time-to-translation
  - Hardest lemmas: aggregate per lemma across shown sentences (approximate via backend `recognized_words` or returned `used_lemmas`)
- [ ] Implementation
  - Compute client-side from the session data in `localStorage`
  - Optional: POST summary to backend for future global analytics (feature-flagged, off by default)
  - Acceptance: A simple readout card appears at end-of-session with actionable numbers


### Stage: “Generate more words” based on performance
- [ ] Add a button to extend the session with targeted content
  - Use analytics to select lemmas that appear hardest (highest replay counts, poor progression)
  - Call the existing generate endpoint with a focused lemma subset; optionally request slightly easier/harder CEFR per user performance
  - Acceptance: Clicking the button yields a new batch biased toward difficult items and nearby support vocabulary


### Very late stages: Persistence model proposals and migrations
- [ ] Add provenance fields to generated content
  - `Sentence`: add `provenance` (enum: `manual`, `imported`, `learn`, `llm_generated`), `generation_batch_id` (nullable FK)
  - `SentenceLemma`: no change required functionally; ensure indexes remain valid
  - Migration: backfill `provenance = 'manual'` for existing sentences; set defaults
  - Acceptance: New sentences created by the Learn flow are labeled and queryable by provenance/batch

- [ ] Introduce `GenerationBatch` model for grouping and auditing
  - Fields: `id`, `target_language_code`, `source_context_type` (`sourcefile`|`sourcedir`|`ad_hoc`), `source_context_slug`, `requested_lemmas` (JSON), `prompt_version`, `num_requested`, `num_created`, `notes`, `created_by`
  - Link `Sentence.generation_batch_id` to `GenerationBatch`
  - Acceptance: We can review batches, regenerate, and compare prompt versions

- [x] Store per-sentence coverage and scoring metadata
  - `Sentence`: `generation_metadata` with `{ used_lemmas, used_wordforms, order_index, prompt_version, tts_voice, source_context }`
  - Acceptance: Enables reuse and future analytics

- [ ] Normalize audio storage and streaming
  - Option A: Keep `audio_data` BLOB with length-limits and move to streaming-only endpoints
  - Option B: External object storage (e.g., Supabase storage) and store `audio_url` on Sentence
  - Migration plan: Feature-flagged rollout; dual-read during transition

- [ ] Add lightweight user progress tracking (optional)
  - `UserSentenceProgress`: per user x sentence x session stats (seen count, last_seen, ease)
  - Acceptance: Enables spaced repetition later without coupling v1

- [ ] Backfill and deduplication strategy
  - Deduplicate new sentences by normalized text per language; keep multiple translations only when materially different
  - Add unique index: (`target_language_code`, normalized(`sentence`)) if practical
  - Acceptance: No explosive growth from LLM re-generation

- [ ] Data retention and cleanup
  - Batch-level deletion (cascade to sentences) for test/dev noise
  - Scheduled cleanup for orphaned audio if we move to external storage

- [ ] Documentation and migrations
  - Write migrations: add `provenance`, `generation_batch_id`, `generation_metadata`; create `GenerationBatch`
  - Update `backend/docs/MODELS.md` and `backend/docs/DATABASE.md`
  - Provide rollback guidance

## Appendix: High-value re-architecture proposals

- Consolidate flashcards to SvelteKit + API-first
  - Deprecate legacy template/JS (`sentence_flashcards.jinja`, legacy static JS) and keep a single Svelte code path fed by JSON APIs
  - Benefits: one UI, consistent behaviors, simpler testing and maintenance

- Audio pipeline decoupling
  - Introduce job layer (threaded queue now; task queue later) for TTS generation + caching
  - Switch from `Sentence.audio_data` BLOB to external storage + `audio_url` when scale is a concern

- Prompt/version governance
  - Track prompt/template version, model, temperature in `GenerationBatch` and `Sentence.generation_metadata`
  - Enables reproducibility and A/B comparisons

- Recognition/segmentation facade
  - Stabilize outputs from `create_interactive_word_data` behind a thin service; reduce coupling to UI details

- Unified error shape and handling
  - Standard JSON error schema across views/APIs; map to friendly UI messages

## Further improvements for efficacy and engagement

- Gentle scaffolding in generated sentences
  - Start with high-frequency patterns and short clauses; gradually introduce complexity and new inflections
  - Include minimal distractors targeting common confusions (from lemma `easily_confused_with`)

- Micro-drills between cards
  - One-tap “Which translation?” or “Pick the lemma used here” before revealing translation; optional and skippable

- Spaced exposure within the session
  - Revisit hard items after 2–3 intervening cards; lightweight loop without persistence in v1

- Light gamification
  - Streak for no replay on a card; session summary with badges (local only at first)

- Pronunciation mimic step
  - After reveal, show a “Record & compare” button (later stage) to capture a short user recording and provide a coarse similarity score

## Risks, mitigations
- LLM variability or slow responses → Mitigate with prompt constraints, lower temperature, and parallel audio generation where feasible
- Audio generation time for 10 sentences → Acceptable in v1; mitigate with caching in next stage
- Memory bloat from data URLs → OK for v1 scale; move to streaming endpoint in persistence stage
- Missing lemma metadata → We generate on demand; background warming reduces future delays


## Acceptance criteria (v1)
- A user can visit the new “Learn” page for a sourcefile, see a list of priority words with etymologies, and start a flashcard session
- The flashcard session has audio, sentence, translation stages with keyboard shortcuts and large buttons; navigating between cards is snappy
- No changes to existing flashcard routes/behavior
- Generated sentences and audio are persisted and reused for the same sourcefile
- Basic logging of step durations is present


## Notes on implementation details
- Difficulty ranking heuristic: `difficulty_score = (1 - guessability) + (1 - commonality)` with defaults to `0.5` if missing; can be tuned later
- “Thinking mode” generation: a single prompt request that returns an ordered set (easy → hard), with guidance to cover provided lemmas and reuse some with varied inflections
- Audio: persisted as `Sentence.audio_data`; served via `/api/lang/sentence/{code}/{id}/audio`
- Background warming: in-process thread for simplicity; no new infra needed in v1


