---
Date: 2026-January-01
Type: Research Review
Participants: User (Greg), Droid (Claude), Triple-review subagents (GPT-5.2, Gemini-3-Pro, Claude Opus)
---

# Architecture Improvement Analysis - Triple Review

## Context

User requested a system architecture review using the Chief Engineer workflow's triple-review mode, with multiple subagents analyzing the codebase for improvements prioritized by **Ease × Value**.

## Methodology

Four subagents ran in parallel:
1. **@researcher** - Gathered comprehensive codebase context
2. **@reviewer-gpt5.2-high** (82% confidence) - Thorough analysis with high reasoning
3. **@reviewer-gemini** (85% confidence) - Alternative perspective
4. **@reviewer-opus** (82% confidence) - Deep nuanced analysis

All reviewers exceeded the 80% confidence threshold.

---

## Critical Issues (Consensus from all reviewers)

### 1. Exception Details Leaked to Clients in Production

**Files**: `backend/api/index.py` (lines 165-180), various `*_api.py` files

**Problem**: The 500 error handler includes `"message": str(original_error)` even in production. Multiple endpoints also catch exceptions and return `str(e)` directly, bypassing the central handler.

**Evidence**:
```python
# backend/api/index.py - always includes error message
response["message"] = str(original_error)

# Various views - manual exception string exposure
except Exception as e:
    return jsonify({"error": str(e)}), 500
```

**Recommendation**: In production, return generic messages only; log details server-side with request IDs.

**Rating**: Ease 4/5, Value 5/5, Score: 20

---

### 2. Synchronous LLM/TTS in Request Path (Timeout Risk)

**Files**: `backend/views/learn_api.py`, `backend/utils/vocab_llm_utils.py`

**Problem**: LLM generation (Claude calls) and TTS happen synchronously within HTTP request handlers. Functions like `learn_sourcefile_generate_api` can run 30+ seconds. Vercel has 30s function timeout.

**Recommendation**: 
- Return `202 Accepted` with `job_id`
- Persist job status in DB
- Frontend polls for completion
- Consider Supabase Edge Functions or background queue

**Rating**: Ease 2/5, Value 5/5, Score: 10

---

### 3. Audio Blobs Stored in Postgres

**Files**: `backend/db_models.py` (LemmaAudio, SentenceAudio models)

**Problem**: MP3 audio bytes stored directly in database and streamed via Flask. This inflates DB size, worsens backups/migrations, and scales poorly.

**Recommendation**: Store audio in Supabase Storage (or S3), keep DB rows as metadata + object keys.

**Rating**: Ease 2/5, Value 5/5, Score: 10

---

## High-Value Improvements (Prioritized by Ease × Value)

### Standardize API Response/Error Envelope
- **Score**: 20 (Ease 4, Value 5)
- **Problem**: Responses vary between `{"error": ...}`, `{"success": false, ...}`, manual status codes
- **Recommendation**: Single shape like `{"data": ..., "meta": {...}, "error": null}`

### Add CI for Tests/Lint/Typecheck
- **Score**: 16 (Ease 4, Value 4)
- **Current**: Only `security-audit.yml` exists
- **Recommendation**: Add workflows for pytest, ruff/black, npm run check

### Split Monolithic db_models.py
- **Score**: 12 (Ease 3, Value 4)
- **File**: `backend/db_models.py` (~1000+ lines, 17 models)
- **Recommendation**: Split into `backend/models/` package by domain

### Rate Limiting on Generation Endpoints
- **Score**: 12 (Ease 3, Value 4)
- **Problem**: No visible rate limiting on expensive LLM/TTS endpoints
- **Recommendation**: Per-user limits using Redis or Supabase metadata

### Frontend Caching for Tooltip/Lemma Data
- **Score**: 12 (Ease 3, Value 4)
- **File**: `frontend/src/lib/components/EnhancedText.svelte`
- **Problem**: Refetches tooltip data on every hover; no cache
- **Recommendation**: In-memory cache per page/session

### Database N+1 Query Optimization
- **Score**: 12 (Ease 3, Value 4)
- **Location**: `backend/db_models.py` lines 216-218 in `Lemma.to_dict()`
- **Problem**:
  ```python
  "example_usage": [
      {...}
      for es in self.example_sentences  # N+1 query per lemma
  ],
  "example_wordforms": [wf.wordform for wf in self.wordforms],  # N+1 again
  ```
- **Impact**: When serializing multiple lemmas, each triggers separate queries for relationships
- **Recommendation**: Use Peewee's `prefetch()` before calling `to_dict()` on collections

### Introduce Service Layer
- **Score**: 10 (Ease 2, Value 5)
- **Problem**: View functions contain business logic, making testing harder
- **Recommendation**: Extract to `backend/services/` with views as thin controllers

### Remove Flask `g` Coupling from BaseModel
- **Score**: 8 (Ease 2, Value 4)
- **File**: `backend/db_models.py` BaseModel.save()
- **Problem**: Reads `flask.g.user_id` to populate `created_by`, breaks scripts/background jobs
- **Recommendation**: Set `created_by` explicitly in service layer

---

## Tactical Improvements (Nice-to-Have)

| Suggestion | Ease | Value | Score |
|------------|------|-------|-------|
| Add database indexes for common queries | 5 | 3 | 15 |
| Remove `print()` statements, use structured logging | 4 | 3 | 12 |
| Use AbortController for fetch timeouts | 4 | 3 | 12 |
| Deprecate legacy `*_views.py` files | 3 | 3 | 9 |
| Add mypy strict type checking | 3 | 3 | 9 |
| Add Svelte stores for global state | 3 | 3 | 9 |
| Pydantic request/response validation | 2 | 4 | 8 |

---

## What's Already Good (Consensus)

- **Type-safe API boundary**: Flask routes auto-generate TypeScript enums/types in `frontend/src/lib/generated/routes.ts`
- **Clean auth decorator pattern**: `@api_auth_required`, `@api_auth_optional`, `@api_admin_required`
- **Good documentation culture**: CLAUDE.md, AGENTS.md, extensive docs folder
- **Modern frontend stack**: SvelteKit 5 with runes, proper SSR patterns
- **48 incremental migrations**: Shows mature database evolution practices
- **Security awareness**: JWT verification with `aud` claim checking

---

## Long-Term Considerations

1. **Async job queue** is prerequisite for scaling LLM-heavy features
2. **Multi-tenancy** would require significant schema refactoring if B2B pivot
3. **Mobile apps** would need API versioning strategy
4. **Content moderation** needed before scaling user-generated content

---

## Recommended Priority Order

**Quick Wins** (do first):
1. Fix error response leakage in production
2. Standardize API response envelope
3. Add CI workflow for tests

**Strategic Investments** (plan for):
1. Async job queue for LLM/TTS generation
2. Move audio to object storage
3. Service layer refactor

---

## References

- Chief Engineer workflow: `docs/generic/CHIEF_ENGINEER.md`
- Architecture docs: `docs/reference/ARCHITECTURE.md`
- Database models: `backend/db_models.py`
- N+1 location: `backend/db_models.py:216-218` (Lemma.to_dict)
- Error handler: `backend/api/index.py:165-180`
