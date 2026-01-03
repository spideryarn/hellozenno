# Plan: Learn Audio Reliability Fixes

**Date:** 2026-01-03
**Status:** Draft

## Overview

Fix audio generation reliability issues on the Learn from Sourcefile page (`/language/[code]/source/[dir]/[file]/learn`). The current implementation has three critical problems:
1. **500 errors** from voice_settings type mismatch with ElevenLabs SDK 2.15.0
2. **DB connection exhaustion** from too many parallel requests overwhelming the 14-connection pool
3. **Request timeouts** from cascading slow operations exceeding 60s limits

## Context

### Root Causes Identified

**Bug 1: voice_settings type mismatch (causes 500 errors)**
- Location: `gjdutils/src/gjdutils/outloud_text_to_speech.py` line ~263
- Code passes `{"stability": 0.92}` (plain dict) to ElevenLabs SDK's `convert()`
- SDK 2.15.0 expects a `VoiceSettings` object from `elevenlabs.types`
- Error: `outloud_elevenlabs() got an unexpected keyword argument 'voice_settings'`

**Bug 2: Frontend fires too many parallel requests (causes DB exhaustion)**
- Current behavior in `frontend/src/routes/.../learn/+page.svelte`:
  - Fetches summary (60s timeout)
  - Fires metadata requests for multiple lemmas in parallel
  - Uses p-queue with `concurrency: 2` for warming, but...
  - Prefetches audio for current + next 2 cards simultaneously (3 parallel requests)
  - Warms top 5 lemmas immediately on summary load
- This creates DB contention with the 14-connection pool

**Bug 3: No request deduplication (amplifies DB pressure)**
- Same metadata/audio requests can be fired multiple times
- User navigating quickly triggers duplicate prefetch requests
- No circuit breaker for failing endpoints

### Architecture Context
- Backend: Flask on Vercel (serverless, each instance has own connection pool)
- DB: Supabase Pro with transaction pooler on port 6543
- Pool config: `max_connections=14, stale_timeout=600, timeout=30`
- Frontend: SvelteKit calling backend APIs
- Auth: Page now requires authentication (server-side redirect)

### Previous Work
The `260102_learn_mvp_timeout_robustness.md` plan introduced lazy audio loading:
- Stage 1 (completed): Added `skip_audio=true` to `/generate` endpoint
- Stage 2 (completed): Added prefetch with p-queue for audio
- But prefetch strategy fires too many concurrent requests (concurrency=2)

### Persistence (Reuse on Subsequent Visits)
The `/generate` endpoint already persists sentences and audio for reuse:
- **Sentences**: Stored in `Sentence` table with `provenance="learn"` and FK to sourcefile
- **Audio**: Stored in `SentenceAudio` table (multiple voice variants per sentence)
- **Reuse flow**: On subsequent visits, `/generate` queries for existing sentences first (`reused_count` in response), only generates new ones if needed
- **Result**: Second visit to same sourcefile is much faster (DB lookup vs LLM+TTS generation)

## Success Criteria

1. Zero 500 errors from voice_settings type mismatch
2. No DB pool exhaustion under normal use (1-2 concurrent users)
3. Audio reliably loads within 15s for current card
4. Smooth user experience with audio ready for next card

---

## Stages

### Stage 1: Fix VoiceSettings Type Mismatch (Critical - Fixes 500s)

**Goal:** Convert voice_settings dict to proper `VoiceSettings` object for ElevenLabs SDK 2.15.0

**Files:**
- `gjdutils/src/gjdutils/outloud_text_to_speech.py`

**Steps:**

1. Add import for VoiceSettings type at MODULE level (not inside function):
   ```python
   # Near top of file, after other imports
   try:
       from elevenlabs.types import VoiceSettings
   except ImportError:
       VoiceSettings = None  # Fallback for older SDK versions
   ```

2. Modify `outloud_elevenlabs()` to convert dict to VoiceSettings with proper guarding:
   ```python
   # Around line 263, in the convert_kwargs building section
   if voice_settings is not None:
       # Convert dict to VoiceSettings object for SDK 2.15.0+
       if VoiceSettings is not None and isinstance(voice_settings, dict):
           convert_kwargs["voice_settings"] = VoiceSettings(**voice_settings)
       elif VoiceSettings is not None:
           # Already a VoiceSettings object
           convert_kwargs["voice_settings"] = voice_settings
       else:
           # Fallback: SDK too old, pass dict anyway (may fail)
           convert_kwargs["voice_settings"] = voice_settings
   ```

**Verification:**
- Quick verification: `python3 -c "from elevenlabs.types import VoiceSettings; vs = VoiceSettings(stability=0.92); print(vs)"`
- Run backend tests: `pytest backend/tests/backend/test_audio_utils.py -v`
- Manually test via CLI: `python scripts/local/learn_cli.py generate el 251013 1000015419-word-matching-jpg --lemmas βιβλίο --num 1 --level A1`
- Verify no 500 errors in `/logs/backend.log` when generating audio

**Estimated time:** 30 minutes

---

### Stage 1b: Scope DB Connections in ensure_sentence_audio_api (Fixes Pool Exhaustion)

**Goal:** Release DB connection before slow TTS generation

**Files:**
- `backend/views/learn_api.py` (ensure_sentence_audio_api endpoint)

**Problem identified by reviewer:**
The current `ensure_sentence_audio_api` does `Sentence.get_by_id()` and `SentenceAudio.select()` outside of `connection_context()`. With Flask's `before_request/teardown_request` hooks, a connection opened by those queries remains checked out for the ENTIRE request duration (including 3-8s TTS generation).

**Steps:**

1. Wrap DB reads in short-lived connection contexts:
   ```python
   @learn_api_bp.route("/sentence/<int:sentence_id>/ensure-audio", methods=["POST"])
   @api_auth_required
   def ensure_sentence_audio_api(sentence_id: int):
       t0 = time.time()
       try:
           # Scope DB reads to release connection before TTS
           with database.connection_context():
               try:
                   sentence = Sentence.get_by_id(sentence_id)
               except Sentence.DoesNotExist:
                   return jsonify({...}), 404
               
               target_language_code = sentence.target_language_code
               sentence_text = sentence.sentence  # Cache needed fields
               
               existing_variants = list(
                   SentenceAudio.select()
                   .where(SentenceAudio.sentence == sentence)
                   .order_by(SentenceAudio.created_at)
                   .limit(1)
               )
           
           # Connection released here - now TTS can run without holding pool slot
           if existing_variants:
               # Return cached audio
               ...
           
           # Generate audio (ensure_sentence_audio_variants has its own connection scoping)
           variants, created_count = ensure_sentence_audio_variants(sentence, n=1)
           ...
   ```

**Verification:**
- Verify test suite passes: `pytest backend/tests/backend/test_learn_api.py -v`
- Load test: open 3 browser tabs on Learn page simultaneously, verify no pool errors

**Estimated time:** 20 minutes

---

### Stage 2: Reduce Frontend Parallelism (Fixes DB Exhaustion)

**Goal:** Limit concurrent backend requests to prevent connection pool exhaustion while still buffering ahead

**Strategy:** Keep prefetching multiple cards ahead (so user spending time on one card allows buffering), but reduce queue concurrency to 1. This gives the "best of both worlds": eager prefetch without overwhelming the DB.

**Files:**
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`

**Steps:**

1. **Add named constants at top of script section** (for maintainability):
   ```typescript
   // Parallelism settings - tuned for DB pool pressure
   // Keep generous lookahead so spending time on a card allows buffering ahead
   // But use concurrency=1 to avoid overwhelming the connection pool
   const AUDIO_PREFETCH_LOOKAHEAD = 3;  // Current + next N cards (buffer ahead)
   const LEMMA_WARM_INITIAL = 5;        // Initial lemmas to warm on load (unchanged)
   const LEMMA_WARM_LOOKAHEAD = 3;      // Lemmas to warm on navigation (unchanged)
   const WARMING_QUEUE_CONCURRENCY = 1; // Max concurrent backend requests (KEY CHANGE)
   ```

2. **Update audio prefetch to use constant (keep current behavior of 3 ahead):**
   ```typescript
   // Keep generous lookahead but process through queue with concurrency=1
   const indicesToPrefetch = Array.from(
     {length: AUDIO_PREFETCH_LOOKAHEAD + 1}, 
     (_, i) => currentIndex + i
   ).filter(i => i < cards.length && cards[i]?.sentence_id);
   ```

3. **Update lemma warming to use constants (values unchanged, just named):**
   ```typescript
   // In warmTopLemmasInBackground call after summary loads:
   warmTopLemmasInBackground(visibleLemmas.slice(0, LEMMA_WARM_INITIAL).map((l) => l.lemma));
   
   // In reactive lemma warming:
   const lookahead = LEMMA_WARM_LOOKAHEAD;
   ```

4. **Reduce p-queue concurrency from 2 to 1** (THE KEY CHANGE):
   ```typescript
   // In ensureWarmingQueue():
   // Change from:
   warmingQueue = new PQueue({ concurrency: 2 });
   // To:
   warmingQueue = new PQueue({ concurrency: WARMING_QUEUE_CONCURRENCY });
   ```

**Why this approach works:**
- User spends 10+ seconds per card reviewing → queue processes 2-3 cards ahead
- Only 1 backend request at a time → no DB pool exhaustion
- If user clicks through quickly → they may see loading spinners, but system recovers

**Verification:**
- Run frontend type check: `cd frontend && npm run check`
- Test manually: stay on card 1 for 30s, verify cards 2-4 have audio ready
- Test: click through quickly, verify no pool errors (may see spinners)
- Check `/logs/backend.log` for connection pool errors

**Estimated time:** 30 minutes

---

### Stage 3: Improve Audio Error Handling and Retry

**Goal:** Allow retry for failed audio loads (currently permanently blocked after error)

**Problem identified by reviewer:**
When audio prefetch times out (15s) or fails, `audioRequestState` is set to `'error'` and the reactive prefetch block permanently skips that sentence (`state === 'error'`). The user has no way to retry, even if the server succeeded after the client abort.

**Files:**
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`

**Steps:**

1. **Update reactive prefetch to skip ALL errors** (retry is triggered manually):
   ```typescript
   $: if (cards.length > 0 && currentIndex >= 0) {
     // Use AUDIO_PREFETCH_LOOKAHEAD constant from Stage 2
     const indicesToPrefetch = Array.from(
       {length: AUDIO_PREFETCH_LOOKAHEAD + 1}, 
       (_, i) => currentIndex + i
     ).filter(i => i < cards.length && cards[i]?.sentence_id);

     for (const idx of indicesToPrefetch) {
       const sentenceId = cards[idx].sentence_id!;
       const state = audioRequestState.get(sentenceId);
       
       // Skip loading/done/error states - errors are only retried via manual button
       // This prevents infinite retry loops when server persistently fails
       if (state === 'loading' || state === 'done' || state === 'error') continue;
       
       // Skip if already has audio
       if (cards[idx].audio_data_url && cards[idx].audio_status === 'ready') continue;
       
       // Mark as loading BEFORE queueing
       audioRequestState.set(sentenceId, 'loading');
       
       if (idx === currentIndex) {
         // Current card - blocking
         audioLoadingForSentenceId = sentenceId;
         prefetchAudioForCard(idx, sentenceId).finally(() => {
           if (audioLoadingForSentenceId === sentenceId) {
             audioLoadingForSentenceId = null;
           }
         });
       } else {
         // Future cards - queue in background with error handling
         ensureWarmingQueue().then((queue) => {
           if (queue) {
             queue.add(() => prefetchAudioForCard(idx, sentenceId), { priority: 0 });
           } else {
             // Queue init failed - revert state to allow retry later
             audioRequestState.set(sentenceId, 'pending');
           }
         }).catch(() => {
           audioRequestState.set(sentenceId, 'pending');
         });
       }
     }
   }
   ```

2. **Add manual retry function:**
   ```typescript
   function retryCurrentCardAudio() {
     const card = cards[currentIndex];
     if (!card?.sentence_id) return;
     // Reset state to allow retry
     audioRequestState.set(card.sentence_id, 'pending');
     cards[currentIndex].audio_status = 'pending';
     cards = [...cards];  // Trigger reactive update
   }
   ```

3. **Add retry button in UI for failed audio:**
   ```svelte
   {#if cards[currentIndex]?.audio_status === 'error'}
     <button class="btn btn-sm btn-outline-warning" on:click={retryCurrentCardAudio}>
       Retry audio
     </button>
   {/if}
   ```

4. **Clear audioRequestState on deck reset:**
   Verify this is done in `resetMetricsForNewDeck()` or add if missing.

**Verification:**
- Run frontend type check: `cd frontend && npm run check`
- Test: let audio timeout, verify retry button appears
- Test: click retry, verify new request is made
- Test: rapidly navigate, verify no duplicate requests for non-current cards

**Estimated time:** 30 minutes

---

### Stage 4: Consider Pool Size Reduction for Serverless (Optional)

**Goal:** Evaluate if reducing pool size improves reliability on serverless

**Files:**
- `backend/config.py`

**Context:**
Current pool config:
```python
DB_POOL_CONFIG = {
    "max_connections": 14,
    "stale_timeout": 600,
    "timeout": 30,
    "autoconnect": True,
    "thread_safe": True,
}
```

On Vercel serverless:
- Each function instance gets its own pool
- Multiple concurrent invocations = multiple pools
- 14 connections × N instances can exceed Supabase limits

**Analysis Required:**
1. Check Supabase Pro connection limits
2. Review Vercel function concurrency settings
3. Determine if pool size 14 is too aggressive

**Potential Change:**
```python
DB_POOL_CONFIG = {
    "max_connections": 5,  # Reduced for serverless
    # ... rest unchanged
}
```

**Risk:** May increase connection wait times during legitimate bursts.

**Decision:** This stage is optional and should only be implemented if Stages 1-3 don't fully resolve the issue. The audio_utils.py already uses short-lived `database.connection_context()` scopes which should mitigate pool pressure.

**Verification:**
- Monitor Supabase connection metrics after Stages 1-3
- If pool exhaustion still occurs, implement this stage
- Test under load with reduced pool size

**Estimated time:** 15 minutes (if needed)

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| VoiceSettings import fails on older SDK | Low | High | Try/except with fallback to raw dict |
| Reduced prefetch too conservative | Medium | Low | User sees spinner briefly; monitor feedback |
| Reduced concurrency slows warming | Low | Low | Single-threaded queue still fast enough |
| Pool reduction causes wait timeouts | Medium | Medium | Only apply if needed; monitor metrics |

## Implementation Notes

### Completed Stages
<!-- Updated by implementer as stages complete -->

### Stage 1 Notes
- Decisions made:
- Learnings:
- Deviations from plan:

### Stage 2 Notes
- Decisions made:
- Learnings:
- Deviations from plan:

### Stage 3 Notes
- Decisions made:
- Learnings:
- Deviations from plan:

---

## Files Modified Summary

| File | Stage | Change |
|------|-------|--------|
| `gjdutils/src/gjdutils/outloud_text_to_speech.py` | 1 | Fix VoiceSettings type |
| `backend/views/learn_api.py` | 1b | Scope DB connections in ensure-audio |
| `frontend/src/routes/.../learn/+page.svelte` | 2, 3 | Reduce parallelism, add retry |
| `backend/config.py` | 4 (optional) | Reduce pool size |

## Testing Checklist

- [ ] Stage 1: Quick test `python3 -c "from elevenlabs.types import VoiceSettings; vs = VoiceSettings(stability=0.92); print(vs)"`
- [ ] Stage 1: `pytest backend/tests/backend/test_audio_utils.py -v` passes
- [ ] Stage 1: Manual CLI test generates audio without 500 errors
- [ ] Stage 1b: `pytest backend/tests/backend/test_learn_api.py -v` passes
- [ ] Stage 2: `cd frontend && npm run check` passes
- [ ] Stage 2: Network tab shows reduced concurrent requests
- [ ] Stage 3: Retry button appears for failed audio
- [ ] Stage 3: No duplicate requests when navigating quickly
- [ ] All: `/logs/backend.log` shows no connection pool errors
- [ ] All: Audio loads reliably within 15s for current card

## Rollback Plan

All changes are backward compatible:
- Stage 1: Can revert VoiceSettings wrapper if issues arise
- Stage 2-3: Frontend changes are isolated, can revert independently
- Stage 4: Pool size easily reverted if wait times increase

No database migrations required.
