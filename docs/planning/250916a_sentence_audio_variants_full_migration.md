## Goal, context

We are migrating sentence audio from a single-blob-per-sentence to a variants model (multiple speakers per sentence), mirroring and unifying with lemma audio. This is a full migration with no backward compatibility: remove `Sentence.audio_data`, add `SentenceAudio` variants, and update all read/write paths to use variants. We will also add a `metadata` JSON on both sentence and lemma variants, removing the dedicated `voice_name` column.

Key outcomes:
- Multiple cached speaker variants per sentence and lemma (default 3), providing diversity for listening and comprehension.
- Remove single `Sentence.audio_data` field and all code paths depending on it.
- Random selection for playback; no API for addressing specific variants.
- Lazy generation where practical (on-click), but Learn/Flashcards can pre-generate during deck preparation.
- Reuse a single `ELEVENLABS_VOICE_POOL` (no language-specific pools).
- Safe to delete all generated audio; code will regenerate lazily as needed.


## References

- Models
  - `backend/db_models.py`
    - `Sentence` (single audio blob to remove): lines 542–567
    - `LemmaAudio` (to modify: add `metadata`, remove `voice_name`): lines 798–811
    - `SentenceLemma` (unchanged): lines 645–653
  - `backend/docs/MODELS.md` – concise overview of models; update sections for `Sentence`, `LemmaAudio`, and add `SentenceAudio`

- Audio generation and limits
  - `backend/utils/audio_utils.py`
    - `ensure_audio_data` – TTS core: lines 141–207
    - `get_or_create_sentence_audio` – remove: lines 209–258
    - `ensure_model_audio_data` – remove sentence branch: lines 261–334
  - `backend/config.py`
    - `MAX_AUDIO_SIZE_FOR_STORAGE`: lines 87–91
    - `ELEVENLABS_VOICE_POOL` and defaults: lines 135–172 (keep pool; do not use per-lang overrides for selection)
    - `LEMMA_AUDIO_SAMPLES`: line 171 (add matching `SENTENCE_AUDIO_SAMPLES` = 3)

- Sentence API
  - `backend/views/sentence_api.py`
    - Stream endpoint: `GET /api/lang/sentence/<lang>/<id>/audio` – change to stream random variant: lines 66–101
    - Generation endpoint: currently `POST /<lang>/<slug>/generate_audio` – replace with ensure-variants: lines 149–176

- Sentence utilities
  - `backend/utils/sentence_utils.py`
    - `generate_sentence` – currently writes `audio_data`; must refactor to variants: lines 18–119 (writes at 47–55, 71–78)
    - `get_random_sentence` – currently may generate audio inline; remove that: lines 138–221 (generation at 202–211)
    - `get_detailed_sentence_data` – computes `has_audio` using `audio_data`; change to variants count: lines 268–356 (uses `has_audio` at 347)

- Learn flow
  - `frontend/docs/FRONTEND_LEARN_FROM_SOURCEFILE.md` – uses sentence streaming URLs and pre-generation: lines 25, 69–72

- Audio doc
  - `docs/reference/AUDIO.md` – update to reflect sentence variants, endpoints, and policies; unify with lemma plan


## Principles, key decisions

- Full migration (no backward compatibility): remove `Sentence.audio_data` and all code that reads/writes it.
- Add `metadata: JSONField` to both `SentenceAudio` and `LemmaAudio`, containing how the audio was generated: `provider`, `voice_name`, `model`, and optional `settings`. Remove `voice_name` column entirely from `LemmaAudio`.
- Default 3 variants per sentence/lemma. Selection is random at playback time.
- Lazy generation:
  - Lemma/Sentence pages: generate on first press of audio.
  - Learn/Flashcards: pre-generate variants during deck preparation.
- API simplification: no need to address specific variants; support “ensure up to N” and “stream random variant” (+ optional `variants` listing for observability).
- No language-specific pools or default voices; only use `ELEVENLABS_VOICE_POOL`.
- OK to delete all generated audio at any time; code path must regenerate lazily when needed.


## Stages & actions

### Stage: Schema changes and migrations
- [x] Create `SentenceAudio` model in `backend/db_models.py` parallel to `LemmaAudio`:
  - Fields: `sentence: FK(Sentence)`, `provider: CharField(default="elevenlabs")`, `audio_data: BlobField`, `metadata: JSONField`, `created_by: FK(AuthUser, null=True)`, timestamps via `BaseModel`.
  - Indexes: add non-unique index on `(sentence)`, and `(sentence, created_at)` for ordering; enforce distinct `voice_name` per `sentence` via app logic using `metadata.voice_name`.
- [x] Add `metadata: JSONField` to `LemmaAudio` and remove `voice_name` column.
- [x] Remove `Sentence.audio_data` column entirely.
- [x] Create Peewee migrations in `backend/migrations/`:
  1. Add `metadata` to `lemma_audio`; backfill: `metadata = {"provider": provider, "voice_name": voice_name}`; then drop `voice_name`.
  2. Create `sentence_audio` table per above.
  3. Drop `sentence.audio_data`.
- [x] Update `backend/docs/MIGRATIONS.md` with these steps and rollback notes (best-effort downgrade may retain columns without data).

Acceptance criteria:
- New `sentence_audio` exists; `lemma_audio` has `metadata` and no `voice_name`; `sentence.audio_data` removed; app starts with migrations applied.


### Stage: Backend utilities refactor
- [x] In `backend/config.py`, add `SENTENCE_AUDIO_SAMPLES: int = 3`.
- [x] In `backend/utils/audio_utils.py` add:
  - `select_random_voices(n: int, exclude: set[str]) -> list[str]` that samples from `ELEVENLABS_VOICE_POOL` without replacement and excluding `exclude`.
  - `ensure_sentence_audio_variants(sentence: Sentence, n: int = SENTENCE_AUDIO_SAMPLES) -> list[SentenceAudio]`:
    - Load existing variants; compute missing count based on distinct `metadata.voice_name`.
    - For each missing, call `ensure_audio_data(text=sentence.sentence, should_add_delays=True, voice_name=chosen)`; create `SentenceAudio` row with `metadata`:
      `{ "provider": "elevenlabs", "voice_name": chosen, "model": "elevenlabs-tts-v1", "settings": {} }`.
    - Enforce `MAX_AUDIO_SIZE_FOR_STORAGE` and return created/total.
  - `ensure_lemma_audio_variants(lemma: Lemma, n: int = LEMMA_AUDIO_SAMPLES) -> list[LemmaAudio]` (mirror of the above using lemma word text).
  - `stream_random_sentence_audio(sentence_id: int) -> bytes` selecting a random variant (DB random or Python choice).
- [x] Remove `get_or_create_sentence_audio` and the Sentence branch from `ensure_model_audio_data`. Update imports/callers.

Acceptance criteria:
- Helpers are idempotent; never duplicate a `voice_name` for the same sentence/lemma. Exceptions and size limits handled cleanly.


### Stage: Sentence API updates
- [x] Replace `GET /api/lang/sentence/<lang>/<id>/audio` to stream a random variant; 404 if none exist.
- [x] Replace `POST /api/lang/sentence/<lang>/<slug>/generate_audio` with `POST /api/lang/sentence/<lang>/<slug>/audio/ensure?n=3` (auth required) to generate up to N missing variants.
- [x] Add optional `GET /api/lang/sentence/<lang>/<id>/audio/variants` returning minimal metadata for observability: `[{ id, provider, metadata: { voice_name }, created_at }]`.

Acceptance criteria:
- Ensure endpoint behaves correctly for 0→3, 1→3, 3→3. Stream endpoint serves a random variant.


### Stage: Lemma API updates
- [x] Add `POST /api/lemma/<lang>/<lemma_id_or_slug>/audio/ensure?n=3` (auth) using the lemma ensure helper.
- [x] Add `GET /api/lemma/<lang>/<lemma_id_or_slug>/audio` to stream a random variant, plus optional `/variants` list.
- [x] Update any existing lemma endpoints and docs accordingly.

Acceptance criteria:
- Lemma audio flows match sentence flows; both support ensure and random stream.


- [x] Update `utils/sentence_utils.generate_sentence`:
  - Stop writing `audio_data`. Create or update `Sentence` row only.
  - Do not generate variants here by default. Return metadata as before.
- [x] Update `get_random_sentence` to stop inline audio generation (remove lines 202–211). Return sentence data only.
- [x] Update `get_detailed_sentence_data`:
  - Replace `has_audio` with `has_variants = (count of SentenceAudio for sentence) > 0`.
- [x] Update any other backend views/utilities that reference `audio_data` to use variants logic.
  - Search for `audio_data` usages across repo and update accordingly.

Acceptance criteria:
- Learn page can pre-generate variants server-side for its deck, and streaming uses random variant endpoints.


### Stage: Frontend updates
- [x] Update Learn flow to pre-generate sentence variants during deck preparation via `POST /audio/ensure?n=3` for each sentence in the deck.
- [x] Streaming URLs should call `GET /api/lang/sentence/<lang>/<id>/audio` (random variant).
- [x] Playback behavior: when pressing the audio button on a sentence card, play 3 variants sequentially (shuffle order); show 1/3 → 3/3 progress.
- [x] Lemma pages: on first click, call ensure if needed, then play 3 variants sequentially; subsequent clicks reuse.

Acceptance criteria:
- Audio button results in three distinct voices. Initial spinner/delay only on first generation.


### Stage: Documentation and ops
- [x] Update `docs/reference/AUDIO.md` to:
  - Document `SentenceAudio` model and `metadata` for both variants.
  - Document endpoints: ensure + random stream; lazy generation; 3-variant playback pattern.
  - Remove references to `Sentence.audio_data`.
- [x] Update `backend/docs/MODELS.md` to:
  - Add `SentenceAudio` section; remove sentence `audio_data` and lemma `voice_name`; add lemma `metadata`.
- [x] Update `frontend/docs/FRONTEND_LEARN_FROM_SOURCEFILE.md` to reflect pre-generation and random stream.
- [x] Add operational note: deleting audio is supported; system regenerates lazily.

Acceptance criteria:
- Docs accurately reflect shipped behavior.


### Stage: Cleanup and validation
- [ ] Optional one-off scripts to clear all audio blobs for a clean test:
  - Delete all rows from `sentence_audio` and `lemma_audio` (or set `audio_data = NULL` if schema demands).
- [ ] Verify app behavior with zero preexisting audio; learn flow and on-click generation replenish variants as expected.

Acceptance criteria:
- Application operates from a blank-audio state without errors.


### Current status
- Code and documentation updates completed; variant storage is now the only audio pathway in the repo.
- Outstanding: run migrations `045`–`047` and the backend/frontend test suites once the local Postgres instance is reachable (current `./scripts/local/migrate.sh` attempts fail because the database service is offline).
- Cleanup/validation items remain pending until migrations apply and we can verify behaviour against a reset datastore.


## Appendix

### Exact code references to change

- Remove single sentence audio field usages:
  - `backend/db_models.py`
    - `Sentence.audio_data` definition: lines 546 (delete field) and any related code in `get_all_sentences_for` that computes `has_audio` (lines 631–633) – update to variants count.
  - `backend/utils/sentence_utils.py`
    - `generate_sentence`: lines 47–55 (ensure_audio_data call) and 71–78 (writing `audio_data`) – remove and refactor to variants handled elsewhere.
    - `get_random_sentence`: lines 202–211 – remove inline generation block.
    - `get_detailed_sentence_data`: line 347 – replace `has_audio` with variants check.
  - `backend/views/sentence_api.py`
    - `get_sentence_audio_api` (lines 79–90): replace `sentence.audio_data` streaming with random variant selection from `SentenceAudio`.
    - `generate_sentence_audio_api` (lines 167–169): replace entire endpoint with `POST /audio/ensure` behavior.
  - `backend/utils/audio_utils.py`
    - Remove `get_or_create_sentence_audio` (lines 209–258) and remove sentence branch from `ensure_model_audio_data` (lines 279–305). Add new helpers listed in plan.

- Add/modify models:
  - `backend/db_models.py`
    - Add `class SentenceAudio(BaseModel)` near `LemmaAudio`.
    - Modify `class LemmaAudio(BaseModel)` to add `metadata = JSONField()` and remove `voice_name`.

- Config changes:
  - `backend/config.py`
    - Add `SENTENCE_AUDIO_SAMPLES: int = 3`.
    - Keep `ELEVENLABS_VOICE_POOL` and ignore per-language overrides in selection functions.

- Views (lemmas):
  - Add `POST /api/lemma/<lang>/<lemma_id_or_slug>/audio/ensure?n=3` and `GET /api/lemma/<lang>/<lemma_id_or_slug>/audio` (random variant), mirroring sentence.

- Docs to update:
  - `docs/reference/AUDIO.md`
  - `backend/docs/MODELS.md`
  - `frontend/docs/FRONTEND_LEARN_FROM_SOURCEFILE.md`


### Data migration steps

1) `lemma_audio` – add JSON metadata and drop voice_name
- Forward:
  - Add `metadata JSONB` column (nullable); for each row, set `metadata = {"provider": provider, "voice_name": voice_name}`.
  - Drop `voice_name` column.
- Backward (best-effort):
  - Re-add `voice_name` and backfill from `metadata.voice_name` if present; keep `metadata`.

2) `sentence_audio` – create new table
- Columns: `id`, `sentence_id`, `provider`, `audio_data`, `metadata`, `created_by`, `created_at`, `updated_at`.
- Indexes: `sentence_id`, `(sentence_id, created_at)`.

3) `sentence` – drop `audio_data`
- Forward: drop column.
- Backward: re-add column `audio_data BYTEA NULL` (data loss acceptable).


### API shapes

- Sentences
  - `POST /api/lang/sentence/<lang>/<slug>/audio/ensure?n=3` → `{ created: number, total: number }`
  - `GET /api/lang/sentence/<lang>/<id>/audio` → streams MP3 for a random variant (HTTP 404 if none)
  - `GET /api/lang/sentence/<lang>/<id>/audio/variants` → `[{ id, provider, metadata: { voice_name }, created_at }]` (optional)

- Lemmas
  - `POST /api/lemma/<lang>/<lemma_id_or_slug>/audio/ensure?n=3` → `{ created: number, total: number }`
  - `GET /api/lemma/<lang>/<lemma_id_or_slug>/audio` → streams MP3 for a random variant
  - `GET /api/lemma/<lang>/<lemma_id_or_slug>/audio/variants` → `[{ id, provider, metadata: { voice_name }, created_at }]` (optional)


### Metadata JSON schema

Stored in `metadata` JSON for each variant:

```json
{
  "provider": "elevenlabs",
  "voice_name": "Brian",
  "model": "elevenlabs-tts-v1",
  "settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}
```

Notes:
- `voice_name` moves into `metadata` for both lemma and sentence variants.
- Additional keys can be included as needed (e.g., `speed`, `style`).


### Playback behavior specifics

- Sentence cards (Flashcards/Learn): When the user presses the audio button, play three different variants back-to-back. If fewer than 3 exist, call ensure to create the missing ones (show spinner), then play. Shuffle order per press.
- Lemma audio: identical to sentence behavior.
- Keyboard behavior (per existing docs): pressing the left button on an audio-sentence-flashcard should play with a different voice each time; for a three-press sequence, all three distinct voices are heard.


### Error handling and limits

- If `ELEVENLABS_VOICE_POOL` has fewer unique voices than requested `n`, generate up to the pool size and return the actual `created` count.
- Enforce `MAX_AUDIO_SIZE_FOR_STORAGE` for generated blobs.
- Auth required for ensure endpoints; streaming endpoints are public (consistent with current policy noted in `docs/reference/AUDIO.md`).
- Return 404 on stream when no variants exist.


### Testing checklist

- Unit tests (backend):
  - ensure idempotency: 0→3, 1→3, 3→3 for both sentence and lemma helpers.
  - ensure distinct `voice_name` per sentence/lemma.
  - handle pool smaller than `n` gracefully.
  - size limit and error propagation.

- API tests:
  - `POST /audio/ensure` happy paths and 400/401/500 edges.
  - `GET /audio` streams MP3 when variants exist; 404 when not.

- E2E (frontend):
  - Learn page pre-generation during deck prep; first session has low latency between cards.
  - Audio button plays 3 distinct voices with progress 1/3 → 3/3.
  - On-click generation on Lemma page: first press generates and plays; subsequent presses reuse.


### Operational notes

- It is safe to delete all generated audio at any time; system will regenerate lazily.
- DB growth: limited by 3 variants per sentence/lemma; monitor `sentence_audio` and `lemma_audio` counts.
- Logging: log ensure events with sentence/lemma IDs and selected voices; consider lightweight metrics on generation volume and stream counts per voice.
