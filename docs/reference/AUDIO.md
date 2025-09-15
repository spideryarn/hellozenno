## Audio in HelloZenno

This document explains how audio works across the app today (sentences) and the planned lemma-level audio feature. It covers data models, generation and playback flows, API surfaces, UI patterns, and migration/operational notes.

### See also
- `../../backend/docs/FLASHCARDS.md` – Flashcard UX and keyboard conventions used for sentence audio
- `../../backend/utils/audio_utils.py` – Core TTS utilities and helpers (generation, size limits, delays)
- `../../backend/views/sentence_api.py` – Sentence audio streaming and generation endpoints
- `../instructions/WRITE_EVERGREEN_DOC.md` – Guidelines for evergreen documentation
- `../../backend/docs/MIGRATIONS.md` – How to write and apply Peewee migrations
- `../../frontend/docs/AudioPlayer.md` – `AudioPlayer` component usage and events

### Principles and policies
- **Auth**: Generation requires login; playback can be public once audio exists (same policy for sentences and lemmas).
- **Caching**: Persist binary MP3 data in the database to avoid repeat TTS calls; respect `MAX_AUDIO_SIZE_FOR_STORAGE`.
- **Performance**: Keep blobs small (single-word audio is tiny). Stream directly from DB for simplicity.
- **Simplicity first**: Start with ElevenLabs voices and a curated pool; extend to other providers later.

---

## Current state (Sentences)

- Model: `Sentence.audio_data: BlobField` holds a single MP3 for the sentence.
- Generation: `ensure_audio_data(text, should_add_delays=True)` in `audio_utils.py` uses ElevenLabs, randomly selects a voice from a curated list, and inserts short SSML-style breaks for natural pacing.
- Storage: `ensure_model_audio_data`/`get_or_create_sentence_audio` generate and save to `Sentence.audio_data` if missing.
- Endpoints:
  - `GET /api/sentence/<lang>/<id>/audio` – streams MP3 from `Sentence.audio_data`.
  - `POST /api/sentence/<lang>/<slug>/generate_audio` – generates and stores audio (auth required).
- Flashcards: Follow `FLASHCARDS.md` for playback states, keyboard shortcuts, and general audio UX.

## Target state (Lemmas)

### Data model
Add a dedicated table to support multiple voices per lemma without inflating `Lemma`:

- `LemmaAudio` (new)
  - `id`
  - `lemma` (FK → `Lemma`, cascade delete)
  - `provider` (e.g., `elevenlabs`)
  - `voice_name` (e.g., `Alice`)
  - `audio_data` (BlobField, MP3)
  - `created_by` (nullable FK → `AuthUser`)
  - `created_at`, `updated_at`
  - Unique index: `(lemma_id, provider, voice_name)`

Rationale: allows 2–3+ stable voice variants per lemma; clean lifecycle; flexible provider expansion.

### Voice pool and selection
- Maintain a curated pool of 6–10 high-quality voices per language/provider.
- On first click for a lemma, randomly select 3 distinct voices from the pool; generate and persist each as a `LemmaAudio` row.
- Subsequent clicks reuse the same 3 variants. Optionally randomize playback order client-side.

### Endpoints (proposed)
- `GET /api/lemma/<lang>/<lemma_id_or_slug>/audio/variants` → `[{ provider, voice_name, url }]`
- `GET /api/lemma/<lang>/<lemma_id_or_slug>/audio/<provider>/<voice_name>` → streams MP3
- `POST /api/lemma/<lang>/<lemma_id_or_slug>/audio/ensure?n=3` → create any missing variants up to N (auth required)

Notes:
- Playback endpoints are public; `ensure` requires auth.
- Slug or id may be supported based on existing lemma routes.
- Use the same CORS posture as flashcard/sentence endpoints.

### UI pattern (80–20)
- Single audio icon next to each lemma token/card.
- On click:
  1) Fetch variants; if fewer than 3, call `ensure` (show spinner) and refetch.
  2) Play the 3 clips sequentially. Subsequent clicks reuse the same set; optionally shuffle order.
- Micro-UX:
  - Spinner only on the lemma icon during generation.
  - Progress badge during playback (e.g., 1/3 → 2/3 → 3/3).
  - Keyboard: `P` to play, `Enter` to replay sequence; mobile uses large tap target.

### Backend implementation notes
- Migration: add `LemmaAudio` with unique `(lemma_id, provider, voice_name)` and indexes on `lemma_id` and `(lemma_id, created_at)`.
- Business logic:
  - Ensure-generation selects from the curated pool and avoids duplicates.
  - Honor `MAX_AUDIO_SIZE_FOR_STORAGE`.
  - Use the existing `ensure_audio_data` with `should_add_delays=False` for single-word pronunciation (or keep true for minimal pacing; subject to UX preference).
  - Enforce auth for generation via `@api_auth_required`.
- Streaming: `send_file(io.BytesIO(row.audio_data), mimetype="audio/mpeg")` like sentence audio.

### Frontend integration notes
- Minimal client: a single handler to call `ensure?n=3` if needed, then sequentially play `variants[0..2]` via `<audio>`/Web Audio.
- Order randomization is trivial client-side.
- Persist nothing client-side beyond caching URLs; the chosen 3 are fixed in DB.

## Testing
- Unit: mock TTS, test `ensure` idempotency (no duplicate voice rows), size checks, and auth gating.
- API: happy paths (streaming existing audio), 404s, and `ensure` behavior (0→3, 1→3, 3→3).
- E2E: clicking the lemma icon triggers generation on first run and reuses thereafter; verify sequential playback.

## Troubleshooting and ops
- Missing provider key → clear 500 with actionable message; surface friendly error in UI.
- Oversize audio → reject and log; for single words this should be rare.
- Cleanup: cascade deletes when lemma is removed.

## Future extensions
- Per-lemma “refresh voices” admin action to reselect/regenerate the 3 variants.
- User preference: default voice per language; optional speed control for playback.
- Sentence-level multi-voice variants using a similar table if needed.







