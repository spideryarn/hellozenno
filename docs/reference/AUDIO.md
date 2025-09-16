## Audio in HelloZenno

HelloZenno now stores multiple text-to-speech variants for both sentences and lemmas. Each variant keeps a short metadata payload describing how the audio was produced so that we can regenerate, audit, or experiment with different providers safely.

### See also
- `../../backend/utils/audio_utils.py` – generation helpers (`ensure_sentence_audio_variants`, `ensure_lemma_audio_variants`)
- `../../backend/views/sentence_api.py` / `../../backend/views/lemma_api.py` – streaming & ensure endpoints
- `../../backend/docs/MODELS.md` – model reference for `SentenceAudio` and `LemmaAudio`
- `../../frontend/docs/FRONTEND_LEARN_FROM_SOURCEFILE.md` – Learn flow pre-generation notes
- `../../backend/docs/MIGRATIONS.md` – context for recent audio migrations

### Core principles
- **Auth**: streaming endpoints remain public; generation (`POST /audio/ensure`) requires authentication.
- **Variants-first**: both sentences and lemmas keep up to three cached variants chosen from a shared ElevenLabs pool; deleting rows is safe as variants regenerate lazily.
- **Metadata over columns**: provider details (`voice_name`, `model`, tuning) live inside a JSONB `metadata` field rather than dedicated columns.
- **Unified playback**: front-end components fetch the variant list, ensure the desired count exists, then play the stored URLs sequentially (shuffled each press).

---

## Data model

### `sentenceaudio`
- `sentence_id` (FK → `sentence`, cascade delete)
- `provider` (default `elevenlabs`)
- `audio_data` (MP3 blob)
- `metadata` (JSONB, e.g. `{ "provider": "elevenlabs", "voice_name": "Brian", "model": "elevenlabs-tts-v1", "settings": {...} }`)
- `created_by` (nullable FK → `auth.users`)
- `created_at`, `updated_at`
- Indexes: `(sentence_id)`, `(sentence_id, created_at)`

### `lemmaaudio`
- Same shape as `sentenceaudio` but keyed by `lemma_id`
- Unique-per-voice enforcement happens in application logic by checking `metadata.voice_name`

### Legacy fields
- `Sentence.audio_data` has been dropped; all consumers should pivot to `SentenceAudio`.
- `LemmaAudio.voice_name` has been replaced by the `metadata` JSON payload.

---

## Generation helpers

Located in `backend/utils/audio_utils.py`:

```python
ensure_sentence_audio_variants(sentence, n=3)
ensure_lemma_audio_variants(lemma, n=3)
```

Both helpers:
- Inspect existing variants and build a set of distinct `voice_name`s from metadata.
- Choose additional voices from `ELEVENLABS_VOICE_POOL` until the min(`n`, pool size) target is met.
- Call `ensure_audio_data(...)` for each missing voice, storing metadata with provider, model, and any settings used.
- Return `(variants, created_count)` for convenience. They raise `AuthenticationRequiredForGenerationError` when new audio is needed and the Flask `g.user` is missing (scripts can disable the check via `enforce_auth=False`).

Sentences add SSML pauses (`should_add_delays=True`); lemmas keep delays off and pass a stable ElevenLabs setting (`{"stability": 0.92}`).

---

## API surface

| Method & Path | Description | Notes |
| --- | --- | --- |
| `GET /api/lang/sentence/{lang}/{id}/audio` | Streams a random sentence variant. Optional `?variant_id=123` pins a specific row. | Response headers: `X-Voice-Name`, `X-Voice-Variant-Id`, `X-Audio-Provider` |
| `GET /api/lang/sentence/{lang}/{id}/audio/variants` | Lists variants `[{ id, provider, metadata, created_at, url }]`. | `url` already points to `?variant_id=` to simplify clients. |
| `POST /api/lang/sentence/{lang}/{slug}/audio/ensure?n=3` | Ensures up to N variants exist. | Returns `{ "created": int, "total": int }`. Requires auth. |
| `GET /api/lang/lemma/{lang}/{lemma}/audio` | Same as sentence streaming (supports `?variant_id=`). | Headers mirror the sentence endpoint. |
| `GET /api/lang/lemma/{lang}/{lemma}/audio/variants` | Lists lemma variants with URLs. | Public, useful for admin/debug. |
| `POST /api/lang/lemma/{lang}/{lemma}/audio/ensure?n=3` | Ensures lemma variants exist. | Auth required; returns counts. |

Streaming endpoints cache-friendly: clients append `?variant_id=` for deterministic playback. Without the parameter, playback is random each request.

---

## Front-end behaviour

- Both the lemma and sentence audio buttons follow the same flow:
  1. Fetch `/audio/variants` to inspect the current variant count.
  2. If fewer than three are available, call `/audio/ensure?n=3` (shows a spinner); unauthenticated users see a login prompt.
  3. Shuffle the returned URLs and play them sequentially, displaying a progress badge (`1/3 → 3/3`).
- Flashcards and Learn flow pre-generate variants server-side by invoking the ensure helpers during deck preparation, minimising latency while reviewing cards.
- Clients rely on the streaming headers to display the active voice (e.g., analytics, debug overlays) but do not expose per-voice controls in the UI.

---

## Operational notes

- **Regeneration**: deleting all rows from `sentenceaudio` or `lemmaaudio` is safe; variants will regenerate lazily via `ensure_*` helpers.
- **Logging**: back-end code logs ensure attempts with sentence/lemma IDs and the voice names chosen. Consider adding light metrics for per-voice usage.
- **Size limits**: `ensure_audio_data` enforces `MAX_AUDIO_SIZE_FOR_STORAGE`. For the ElevenLabs voices we use, single sentences remain well below the limit.
- **One-off scripts**: see `backend/oneoff/250120_generate_missing_audio_for_sentences.py` for a template that ensures variants in bulk (uses a Flask request context and `enforce_auth=False`).

---

## Checklist when touching audio

- Update both `SentenceAudio` and `LemmaAudio` tables if schema changes are required.
- Keep the metadata payload shaped like `{ provider, voice_name, model, settings }` so downstream tooling can reason about audio provenance.
- When adding a new voice/provider, extend `ELEVENLABS_VOICE_POOL` (or future pools) and adjust helper logic if provider-specific settings are needed.
- Remember to adapt the front-end constants in `frontend/src/lib/config.ts` (`LEMMA_AUDIO_SAMPLES`, `SENTENCE_AUDIO_SAMPLES`) if default counts change.






