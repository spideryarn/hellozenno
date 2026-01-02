# Learn MVP Timeout Robustness Improvements

**Date**: 2026-01-02
**Status**: In Progress
**Goal**: Make Learn from Sourcefile flow robust against timeouts while maintaining good UX

## Problem Statement

The Learn MVP `/generate` endpoint frequently times out (60s Vercel limit) when generating new sentences with audio:
- LLM call (Claude): ~5-15s
- TTS calls (ElevenLabs): ~3-8s **per sentence** × 5-10 sentences = 15-80s total

First-time visitors to a sourcefile experience long waits or timeout errors.

## Success Criteria

1. First visit: User can start practicing within ~15s (summary + first cards ready)
2. Audio: First card has audio ready; subsequent cards preload
3. Subsequent visits: Near-instant (all content cached)
4. No timeout errors under normal operation
5. Graceful degradation if external services are slow

## Architecture Decision

**Approach**: Lazy audio generation with progressive enhancement

Instead of generating all audio upfront (which causes timeouts), we:
1. Generate sentences via LLM first (~5-15s)
2. Return sentences immediately without audio
3. Generate audio on-demand when needed (per-card, ~3-8s each)
4. Prefetch audio for upcoming cards while user is on current card

This keeps each request under 20s while providing good UX.

---

## Stage 1: Backend - Separate Sentence Generation from Audio

**Goal**: Allow `/generate` to return sentences without audio, with a flag indicating audio status.

### Changes

#### 1.1 Add `skip_audio` parameter to `/generate` endpoint

**File**: `backend/views/learn_api.py`

Modify `learn_sourcefile_generate_api` to accept `skip_audio: bool = False` in request body.

When `skip_audio=True`:
- Generate/reuse sentences as normal
- Skip `ensure_sentence_audio_variants()` calls for BOTH reused AND new sentences
- For reused sentences: Still check if audio already exists and return URL if so (cheap DB lookup)
- For new sentences: Return `audio_data_url: null` and `audio_status: "pending"`
- Much faster response (~5-15s for new, ~1-3s for reused)

When `skip_audio=False` (default, backward compatible):
- Current behavior for compatibility

**Important**: `skip_audio` means "don't GENERATE audio", not "don't INCLUDE existing audio".

#### 1.2 Add dedicated audio generation endpoint

**File**: `backend/views/learn_api.py`

New endpoint: `POST /api/lang/learn/sentence/<sentence_id>/ensure-audio`

```python
@learn_api_bp.route("/sentence/<int:sentence_id>/ensure-audio", methods=["POST"])
@api_auth_optional
def ensure_sentence_audio_api(sentence_id: int):
    """Ensure audio exists for a sentence, generating if needed."""
```

Response:
```json
{
  "audio_data_url": "/api/lang/sentence/{lang}/{id}/audio?variant_id=...",
  "generated": true/false,
  "duration_s": 3.5
}
```

This endpoint:
- Checks if audio variants exist
- Generates if missing (requires auth)
- Returns audio URL
- Single sentence = single TTS call = ~3-8s (safe timeout margin)

### Testing

- Verify `/generate?skip_audio=true` returns quickly (~5-15s)
- Verify `/ensure-audio` generates audio correctly
- Verify backward compatibility (`skip_audio` defaults to false)

### Implementation Notes (Stage 1)

**Completed**: 2026-01-02

**Changes made**:
1. Added `skip_audio: bool = False` parameter to request body parsing in `learn_sourcefile_generate_api`
2. Modified reused sentence handling:
   - When `skip_audio=True`: Only does cheap DB lookup for existing audio variants (`.limit(1)`)
   - Sets `audio_status: "ready"` if audio exists, `"pending"` otherwise
   - Always includes `sentence_id` in response for frontend ensure-audio calls
3. Modified new sentence handling:
   - When `skip_audio=True`: Skips all `ensure_sentence_audio_variants()` calls
   - Returns `audio_status: "pending"` for all new sentences
   - Always includes `sentence_id` in response
4. Added new endpoint `POST /api/lang/learn/sentence/<int:sentence_id>/ensure-audio`:
   - Uses `@api_auth_optional` decorator for anonymous access to cached audio
   - Returns existing audio immediately if found (~0.01s)
   - Generates audio on-demand if missing (requires auth, ~3-8s)
   - Returns 401 with `authentication_required_for_generation: true` for anonymous users needing generation
   - Includes `duration_s` in all responses for observability
   - Proper error handling for 404, 401, 500 cases

**Design decisions**:
- `audio_status` field only included when `skip_audio=True` to avoid breaking existing consumers
- Used same response shape conventions as other API endpoints
- Used `.limit(1)` on audio lookup for efficiency since we only need one variant

**Verification**:
- Ruff check passes (no linting errors)
- Black formatting applied
- Routes correctly registered (verified via Flask app inspection)
- Module imports successfully

---

## Stage 2: Frontend - Progressive Audio Loading

**Goal**: Update frontend to use lazy audio loading with prefetch.

### Changes

#### 2.1 Update BOTH preparation paths to skip audio

**File**: `frontend/src/routes/.../learn/+page.svelte`

Modify BOTH `preparePracticeInBackground` AND `startPractice` to use `skip_audio: true`:
- Get sentences faster in all paths
- Cards initially have `audio_status: "pending"` (or "ready" if cached)
- Eliminates timeout risk from both foreground and background flows

**Critical**: Both paths must use `skip_audio: true` to fully eliminate timeout risk.

#### 2.2 Add audio prefetch logic

**File**: `frontend/src/routes/.../learn/+page.svelte`

New function: `prefetchAudioForCard(index: number)`

Using p-queue with concurrency 1:
```typescript
const audioQueue = new PQueue({ concurrency: 1 });

async function prefetchAudioForCard(index: number) {
  const card = cards[index];
  if (!card || card.audio_data_url) return; // Already has audio
  
  // Call ensure-audio endpoint
  const result = await apiFetch({
    routeName: RouteName.LEARN_API_ENSURE_SENTENCE_AUDIO_API,
    params: { sentence_id: card.sentence_id },
    options: { method: 'POST' },
    timeoutMs: 15000,
  });
  
  // Update card with audio URL
  cards[index].audio_data_url = result.audio_data_url;
  cards = [...cards]; // Trigger reactivity
}
```

#### 2.3 Prefetch strategy

When practice starts or card changes:
1. Ensure current card has audio (blocking if needed, show spinner)
2. Queue prefetch for next 2 cards (non-blocking)

```typescript
// Track which sentences have audio requests in-flight or done
const audioRequested = new Set<number>();

$: if (cards.length > 0) {
  const card = cards[currentIndex];
  if (card?.sentence_id && !audioRequested.has(card.sentence_id)) {
    audioRequested.add(card.sentence_id);
    // Current card - must have audio (blocking)
    prefetchAudioForCard(currentIndex);
  }
  // Prefetch ahead (non-blocking, deduped)
  [currentIndex + 1, currentIndex + 2].forEach(idx => {
    const c = cards[idx];
    if (c?.sentence_id && !audioRequested.has(c.sentence_id)) {
      audioRequested.add(c.sentence_id);
      audioQueue.add(() => prefetchAudioForCard(idx));
    }
  });
}
```

#### 2.4 UI updates

- Show loading spinner on AudioPlayer while audio is pending
- Update "Practice ready" chip to show card count even without audio
- Add "Audio loading..." indicator
- Handle auth: Skip audio prefetch for anonymous users (they can only use cached audio)

#### 2.5 Card type updates

**File**: `frontend/src/routes/.../learn/+page.svelte`

Update card type to support audio status:
```typescript
type Card = {
  sentence: string;
  translation: string;
  used_lemmas: string[];
  language_level?: string;
  audio_data_url: string | null;  // Changed from string
  audio_status?: 'pending' | 'loading' | 'ready' | 'error';
  sentence_id?: number;  // Needed for ensure-audio calls
};
```

### Testing

- Verify cards load quickly without audio
- Verify audio loads on-demand
- Verify prefetch works (next cards have audio ready)
- Verify spinner shows while loading

### Implementation Notes (Stage 2)

**Completed**: 2026-01-02

**Changes made**:
1. Updated card type to support audio status:
   - `audio_data_url: string | null` (null when audio not yet loaded)
   - `audio_status?: 'pending' | 'loading' | 'ready' | 'error'`
   - `sentence_id?: number` (needed for ensure-audio calls)

2. Updated both `startPractice` and `preparePracticeInBackground` functions:
   - Added `skip_audio: true` to request body in both paths
   - Eliminates timeout risk from audio generation in all flows

3. Added audio prefetch tracking state:
   - `audioRequested: Set<number>` - tracks which sentence IDs have been requested
   - `audioLoadingForCurrentCard: boolean` - tracks blocking audio load for current card

4. Added `prefetchAudioForCard(cardIndex)` function:
   - Checks if card has sentence_id and doesn't already have audio
   - Updates card.audio_status to 'loading' for UI feedback
   - Handles unauthenticated users gracefully (can only use cached audio)
   - Manually constructs ensure-audio URL (route not yet in generated routes)
   - Fetches with auth token if available
   - Updates card with audio URL on success, marks 'error' on failure

5. Added reactive prefetch trigger:
   - Triggers when cards array changes or currentIndex changes
   - Prefetches current card (blocking, shows spinner)
   - Queues next 2 cards via warmingQueue with low priority
   - Uses Set to deduplicate requests

6. Updated UI:
   - Shows "Loading audio..." spinner when `audioLoadingForCurrentCard` or card status is 'loading'
   - Falls back to audio player when ready, or warning when no audio available

**Design decisions**:
- Reused existing `warmingQueue` (p-queue with concurrency 2) for background prefetch
- Manually constructed fetch URL instead of using apiFetch to avoid route generation dependency
- Used finally() instead of try/catch for audioLoadingForCurrentCard to ensure cleanup

**Verification**:
- `npm run check` passes with no errors
- Existing warnings unrelated to changes
- Type annotations correct for nullable audio_data_url

---

## Stage 3: Optimization - Smaller Initial Batches

**Goal**: Generate fewer sentences initially for faster first response.

**Rationale**: Even with skip_audio, the LLM call to generate sentences can take ~5-15s. If we request 10 sentences, that's one long request. By requesting 4 sentences first, we can reduce initial wait time to ~3-8s, then fetch more in background.

### Changes

#### 3.1 Add config constant for initial batch size

**File**: `frontend/src/lib/config.ts`

```typescript
export const LEARN_INITIAL_CARDS = 4;  // First batch (quick ~3-8s)
export const LEARN_DEFAULT_NUM_CARDS = 10;  // Total target
```

#### 3.2 Two-phase generation in preparePracticeInBackground

**File**: `frontend/src/routes/.../learn/+page.svelte`

Modify `preparePracticeInBackground()`:
1. First call: `num_sentences: LEARN_INITIAL_CARDS (4), skip_audio: true`
2. Set `preparedCards` with initial batch, mark as "partial"
3. If user starts practice, they get initial cards immediately
4. Background follow-up call: `num_sentences: LEARN_DEFAULT_NUM_CARDS (10)`
5. Merge new sentences into deck (append, dedupe by sentence_id)

**Key consideration**: The second call may return some of the same sentences (reused). We need to:
- Deduplicate by sentence_id
- Preserve audio status from first batch
- Only add truly new sentences

#### 3.3 Track partial deck state

Add state variable:
```typescript
let preparedDeckIsPartial = false;  // True if more cards coming
```

Update UI to show "More cards loading..." when partial.

#### 3.4 Merge logic

```typescript
function mergeCards(existing: Card[], incoming: Card[]): Card[] {
  const existingIds = new Set(existing.map(c => c.sentence_id));
  const newCards = incoming.filter(c => !existingIds.has(c.sentence_id));
  return [...existing, ...newCards];
}
```

### Risk Mitigation

1. **Race condition**: User starts practice before second batch arrives
   - Solution: Merge into cards array even if practice started, preserving current index
   
2. **Duplicate requests**: Background prep starts while user triggers manual start
   - Solution: Track `preparingMoreCards` flag, skip if already in progress

3. **UI confusion**: User sees card count change mid-session
   - Solution: Show "(N cards, more loading...)" indicator

---

## Stage 4: Future - Async Job Queue (Deferred)

For truly robust handling of very slow operations, implement async job pattern:
- Return 202 Accepted with job_id
- Poll for completion
- Store state in DB

This is architectural and can be implemented later if needed.

---

## Implementation Order

1. **Stage 1** (Backend): ~1-2 hours
   - Add `skip_audio` parameter
   - Add `/ensure-audio` endpoint
   - Test both paths

2. **Stage 2** (Frontend): ~2-3 hours
   - Integrate lazy audio loading
   - Add prefetch with p-queue
   - Update UI for loading states

3. **Stage 3** (Optimization): ~1 hour
   - Smaller initial batches
   - Two-phase generation
   - Test end-to-end flow

---

## Rollback Plan

All changes are backward compatible:
- `skip_audio` defaults to `false`
- Frontend can be reverted independently
- No database migrations required

---

## Files to Modify

### Backend
- `backend/views/learn_api.py` - Add skip_audio param and ensure-audio endpoint
- `backend/api/index.py` - Register new route (if needed)

### Frontend  
- `frontend/src/routes/.../learn/+page.svelte` - Lazy audio loading
- `frontend/src/lib/config.ts` - New constants
- `frontend/src/lib/generated/routes.ts` - New route name (auto-generated)

### Documentation
- `docs/reference/LEARN_FROM_SOURCEFILE_MVP.md` - Update with new flow
- `docs/diagrams/260102a_learn_mvp_detailed_flow.mermaid` - Update diagram

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Audio fails to generate | Low | Medium | Show "audio unavailable" gracefully |
| Prefetch too aggressive | Low | Low | p-queue limits concurrency |
| User advances faster than prefetch | Medium | Low | Show loading spinner, block briefly |
| Backend changes break mobile | N/A | N/A | No mobile client yet |

---

## Metrics to Monitor

- Time to first card ready
- Time to practice start (user clicks play)
- Audio generation success rate
- Timeout error rate (should drop to ~0)
