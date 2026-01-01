---
Date: 2026-January-01
Type: Exploratory / Problem-solving
Topic: Learn from Sourcefile feature improvements
---

# Learn from Sourcefile: Improvements Sounding Board

## Context

Reviewing the Learn from Sourcefile MVP to identify opportunities for making the feature more effective, friendly, usable, and valuable to learners.

### Current State

The Learn flow:
1. **Priority Words**: Surfaces top-K lemmas ranked by difficulty (`1-guessability + 1-commonality`), showing etymology
2. **Practice**: Generates audio sentence flashcards using those lemmas, 3-stage reveal (audio → sentence → translation)
3. **Persistence**: Sentences and audio are saved with `provenance="learn"` and reused on subsequent visits
4. **Local Analytics**: Tracks replays, shows end-of-session stats

### Key References

- `docs/reference/LEARN_FROM_SOURCEFILE_MVP.md` - Feature overview
- `docs/planning/250915a_sourcefile_learn_flow_mvp.md` - Planning doc with stages and future work
- `docs/plans/260101_learn_mvp_bugfixes.md` - 8 identified bugs to fix
- `frontend/docs/FRONTEND_LEARN_FROM_SOURCEFILE.md` - Frontend documentation
- `backend/views/learn_api.py` - API endpoints (summary + generate)
- `backend/prompt_templates/generate_sentence_flashcards.jinja` - Sentence generation prompt


## Questions Raised

### 1. The Fundamental Learning Loop

> Is passive listening + reading sufficient for vocabulary acquisition, or is there a gap?

**Observation**: Research on language learning suggests **active recall** (being forced to produce or recognize) beats passive review. The current flow has the learner mostly as a passive consumer.

**Existing roadmap item**: The "micro-drill" idea (quick "which translation?" quizzes between cards) addresses this but is marked as future work.

**Open question**: Is the current "reveal-and-move-on" pattern valuable enough as a warm-up/exposure tool, or does it need more active engagement to be effective?


### 2. Multi-Lemma Sentence Coverage

User question:
> "Could we generate sentences that try to use multiple lemmas that we're trying to learn?"

**Finding**: The system already does this by design. From planning doc:
> Batch-generate all sentences before starting the session using a "thinking mode" prompt that:
> - Maximizes coverage of the selected lemmas across the set
> - Allows the same word to reappear (ideally in varied forms)

The `generate_sentence_flashcards.jinja` prompt instructs the LLM to use multiple target lemmas per sentence where natural.

**Follow-up questions**:
1. Is the multi-lemma coverage actually happening in generated sentences?
2. Would **highlighting target lemmas** in revealed sentences reinforce the learning connection?
3. Is the `used_lemmas` field being surfaced to users? (e.g., "This sentence practices: βιβλίο, μουσική, διαβάζω")


### 3. Persistent Lemma Ignore Feature

User comment:
> "I think we have a lemma-level ignore feature"

**Confirmed**: Yes, fully implemented.

| Aspect | Details |
|--------|---------|
| **Storage** | PostgreSQL `userlemma` table |
| **Scope** | Per-user, per-language (not per-sourcefile) |
| **Auth Required** | Yes |
| **Model** | `UserLemma` with `user_id`, `lemma` FK, `ignored_dt` timestamp |
| **API Endpoints** | `POST /ignore`, `POST /unignore`, `GET /ignored` |

**Integration in Learn flow**:
- Fetches ignored lemmas on page load
- Filters them from visible Priority Words list
- Excludes them when generating sentences (client-side filtering before API call)
- `get_random_sentence()` can also filter server-side if Profile is passed

**Question raised**: Is the ignore feature discoverable enough in the UI?


### 4. Audio Variant Selection

**Current**: 3 audio variants per sentence with different ElevenLabs voices, selected randomly on playback.

**Open questions**:
- What's the pedagogical intent? Variety for engagement? Different accents?
- **Opportunity**: If voices represent different characteristics (speed, clarity, gender), learners could choose or progressively encounter "harder to understand" variants.


### 5. Analytics Signal Quality

**Current**: Time-to-translation is tracked as a difficulty indicator (slower = harder).

**Concern**: This conflates "struggling to understand" with "taking time to actively process." A learner deliberately delaying reveal for engagement might appear to be struggling.

**Recommendation**: Number of audio replays is likely a cleaner difficulty signal.


## Recommendations

### High-Value Improvements

1. **Highlight target lemmas in revealed sentences**
   - When sentence text is revealed, highlight words that match the `used_lemmas` for that sentence
   - Reinforces which vocabulary the sentence was designed to practice
   - Low effort, high pedagogical value

2. **Surface multi-lemma coverage to user**
   - Show "Practicing: βιβλίο, μουσική" somewhere on the card
   - Helps learners understand why certain sentences were generated
   - Makes the learning intent explicit

3. **Improve difficulty signal**
   - Weight replay count more heavily than time-to-translation
   - Or track both separately for richer analytics

4. **Make ignore feature more discoverable**
   - The feature exists and works well
   - Consider adding visual indicator for "X lemmas ignored" in options panel
   - Could offer "Review ignored lemmas" functionality

### Medium-Priority Improvements (from existing roadmap)

5. **Micro-drills between cards**
   - Quick "Which translation?" or "Which word means X?" before full reveal
   - Introduces active recall into the passive flow
   - Should be optional/skippable

6. **"Generate more" based on performance**
   - Already in roadmap
   - Use replay counts to identify struggling lemmas
   - Request new sentences focused on those lemmas

7. **Spaced exposure within session**
   - Revisit high-replay items after 2-3 intervening cards
   - Lightweight loop without persistence in v1

### Lower-Priority / Future

8. **Audio variant progression**
   - Start with clearest voice, optionally progress to faster/harder variants
   - Requires voice characterization metadata

9. **Pronunciation mimic step**
   - "Record & compare" after reveal
   - Significant implementation effort


## Open Questions (for user)

1. **Who is the target learner?** A beginner encountering a text for the first time, or an intermediate learner reinforcing known material? This affects breadth vs depth priority.

2. **What's the stickiest part of the current experience?** When actually using it, what works well and what feels frustrating or pointless?

3. **Is multi-lemma coverage working in practice?** Are generated sentences actually using multiple target lemmas, or mostly one per sentence?


## Next Steps

- [ ] Address the 8 bugs identified in `docs/plans/260101_learn_mvp_bugfixes.md`
- [ ] Consider implementing "highlight target lemmas" as quick win
- [ ] Decide on active recall approach (micro-drills vs other)
- [ ] Review actual sentence output to verify multi-lemma coverage is working
