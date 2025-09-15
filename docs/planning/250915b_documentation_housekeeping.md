### Goal, context

Comprehensive documentation housekeeping to improve developer experience and maintainability. The documentation has accumulated technical debt with outdated references, missing critical information, and fragmented planning documents. This work will update key documentation, consolidate planning docs into proper reference docs, and ensure all documentation accurately reflects the current implementation.

Priority issues identified:
- ENHANCED_TEXT.md marked as outdated but still actively referenced
- Missing comprehensive CONFIGURATION.md for environment setup
- TESTING.md references non-existent FRONTEND_TESTING.md
- 38+ planning documents with unclear status
- Outdated Fly.io references in DATABASE.md

### References

- `docs/DOCUMENTATION_ORGANISATION.md` - Navigation guide for all documentation
- `frontend/docs/ENHANCED_TEXT.md` - Core interactive text feature (marked outdated)
- `docs/reference/CONFIGURATION.md` - Brief config overview (needs expansion)
- `backend/docs/TESTING.md` - Testing documentation (references missing files)
- `backend/docs/DATABASE.md` - Database setup (contains outdated Fly.io references)
- `docs/planning/250412_enhanced_text_transition.md` - Enhanced text refactoring plan
- `docs/planning/250914e_test_suite_triage_and_strategy.md` - Test consolidation strategy
- `docs/planning/250914c_multilingual_word_segmentation_for_hover_links.md` - Recent segmentation work
- `gjdutils/docs/instructions/UPDATE_HOUSEKEEPING_DOCUMENTATION.md` - Housekeeping process guide
- `gjdutils/docs/instructions/WRITE_EVERGREEN_DOC.md` - Evergreen documentation guidelines

### Principles, key decisions

- Fix critical documentation first (ENHANCED_TEXT.md, CONFIGURATION.md) before nice-to-haves
- Preserve all useful information while removing redundancy
- Consolidate ephemeral planning docs into proper evergreen reference docs where appropriate
- Maintain clear separation between reference (evergreen) and planning (ephemeral) documentation
- Update cross-references to ensure consistency
- Remove or update all outdated information (Fly.io, obsolete approaches)
- Keep changes minimal and focused - don't rewrite working documentation unnecessarily

**Decisions for this effort**
- Prioritize critical fixes first: update `frontend/docs/ENHANCED_TEXT.md`, split testing docs, and clean up `backend/docs/DATABASE.md`.
- Create `frontend/docs/FRONTEND_TESTING.md`; rename `backend/docs/TESTING.md` → `backend/docs/BACKEND_TESTING.md`; add `docs/reference/TESTING.md` as a signpost.
- Align database documentation to Supabase's transaction pooler (port 6543) across all docs; remove Fly.io references (keep migration history only where useful).
- Keep legacy Enhanced Text HTML mode documented but clearly marked as deprecated; structured data mode is the default.
- Update cross-references now to avoid drift; avoid broad rewrites beyond these scoped changes.

### Stages & actions

### Stage: Critical documentation fixes

- [x] Update ENHANCED_TEXT.md to reflect current implementation
  - [x] Review `docs/planning/250412_enhanced_text_transition.md` for transition details
  - [x] Document new `create_interactive_word_data()` approach with clear examples
    - [x] Show how backend returns structured data instead of HTML
    - [x] Include the recognizedWords array format with start/end positions
  - [x] Keep legacy HTML mode documentation but clearly mark as deprecated
  - [x] Update code examples to use structured data mode
    - [x] Replace HTML examples with structured data examples
    - [x] Show both backend API response format and frontend component usage
  - [x] Verify all code references are current (check file paths and function names)

- [x] Fix TESTING.md, rename it, and create FRONTEND_TESTING.md
  - [x] Update backend testing doc content and rename `backend/docs/TESTING.md` → `backend/docs/BACKEND_TESTING.md`
  - [x] Create `frontend/docs/FRONTEND_TESTING.md` with Playwright + Vitest guidance and commands
  - [x] Add `docs/reference/TESTING.md` stub that signposts to both
  - [x] Document integration-first testing strategy
  - [x] Add clear testing workflow and commands
  - [x] Include common test failure patterns and fixes

- Acceptance:
  - `frontend/docs/ENHANCED_TEXT.md` has no "out of date" banner, structured mode is default, legacy mode is marked deprecated.
  - `frontend/docs/FRONTEND_TESTING.md` exists; `backend/docs/BACKEND_TESTING.md` exists; `docs/reference/TESTING.md` exists.
  - All internal links to testing docs resolve and reflect final filenames.
  - Examples compile conceptually against current code paths (`EnhancedText.svelte`, API routes).


### Stage: Database and reference cleanup

- [x] Remove Fly.io references from DATABASE.md
  - [x] Search for all Fly.io mentions
  - [x] Update to reflect Supabase-only architecture
  - [x] Verify all connection instructions are current

- [x] Review and update cross-references
  - [x] Check all "See also" sections for accuracy
  - [x] Ensure referenced files exist
  - [x] Update paths if files have moved
  - [x] Add missing cross-references where helpful

- Acceptance:
  - `backend/docs/DATABASE.md` consistently specifies Supabase transaction pooler (6543) in production and is free of Fly.io update TODOs.
  - No broken or stale references remain in touched docs.

### Stage: Planning document consolidation

- [x] Review and organize planning documents
  - [x] Use Task tool with subagents to review all docs in `docs/planning/`
  - [x] Identify which planning docs represent completed work
  - [x] Move completed docs to `docs/planning/finished/`
- [ ] Consolidate authentication documentation
  - [ ] Merge relevant planning details into AUTH.md
  - [ ] Remove redundant auth information from other docs
  - [ ] Ensure single source of truth for auth patterns

- Acceptance:
  - Completed planning docs are archived; this doc lists what moved.
  - `frontend/docs/AUTH.md` reflects consolidated auth patterns; redundant references removed.

- [ ] Extract deployment architecture into proper reference doc
  - [ ] Consider creating docs/reference/ARCHITECTURE.md for high-level decisions
  - [ ] Document Flask + SvelteKit hybrid approach rationale
  - [ ] Include deployment architecture overview

- [ ] Move any .md docs in `docs/` into `docs/reference/`

### Stage: Documentation organization improvements

- [ ] Update DOCUMENTATION_ORGANISATION.md
  - [ ] Add status indicators for doc completeness
  - [ ] Include last-updated dates where helpful
  - [ ] Reorganize categories based on current structure
  - [ ] Mark critical starter docs more clearly

- [ ] Create missing high-value documentation
  - [ ] API documentation - improve existing URL_REGISTRY.md documentation
    - Note: We use a custom URL registry system, not OpenAPI
    - Document the Flask → TypeScript type generation system better
    - Add examples of request/response formats for major endpoint categories
    - Include authentication requirements per endpoint type (@api_auth_required vs @api_auth_optional)
    - Consider adding endpoint documentation tables to URL_REGISTRY.md
  - [ ] Performance/monitoring documentation (create docs/reference/MONITORING.md)
    - Document production monitoring tools:
      - Vercel dashboard for backend API (hz_backend project)
      - Vercel dashboard for frontend (hz_frontend project)
      - Supabase dashboard for database metrics and egress
    - Log analysis guidance:
      - Backend: `/logs/backend.log` (Loguru format, 200-line limit)
      - Frontend: `/logs/frontend.log`
      - Production logs via Vercel CLI (note issues with `vercel logs --json`)
    - Database performance:
      - Connection pooling settings (session vs transaction pooler)
      - Query optimization tips for Peewee ORM
      - Supabase egress monitoring (see `docs/planning/250420_data_egress_issue.md`)
    - Common bottlenecks:
      - LLM generation timeouts (30s Vercel limit)
      - Audio processing with ElevenLabs
      - Large sourcefile processing
      - Frontend bundle size (check with `npm run build`)
    - Resource limits:
      - Vercel function timeout (30s default)
      - Supabase free tier limits
      - Rate limiting considerations

- Acceptance:
  - `docs/DOCUMENTATION_ORGANISATION.md` includes updated links and status notes for modified docs.
  - If created, `docs/reference/MONITORING.md` and API endpoint enhancements are linked from the organisation doc.

### Stage: Final validation and cleanup

- [ ] Run comprehensive documentation review
  - [ ] Use Task tool to check for broken links
  - [ ] Verify all code examples still work
  - [ ] Ensure no contradictions between documents
  - [ ] Check that all TODOs have been addressed

- [ ] Update housekeeping tracking
  - [ ] Update DOCUMENTATION_ORGANISATION.md with all changes
  - [ ] Commit with clear documentation of improvements
  - [ ] Move this planning doc to finished/

- Acceptance:
  - Automated link check passes; no broken internal references in updated docs.
  - Repository contains the updated/created docs; version control commit documents the changes.
