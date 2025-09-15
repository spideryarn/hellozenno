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

### Stages & actions

### Stage: Critical documentation fixes

- [ ] Update ENHANCED_TEXT.md to reflect current implementation
  - [ ] Review `docs/planning/250412_enhanced_text_transition.md` for transition details
  - [ ] Document new `create_interactive_word_data()` approach with clear examples
    - Show how backend returns structured data instead of HTML
    - Include the recognizedWords array format with start/end positions
  - [ ] Keep legacy HTML mode documentation but clearly mark as deprecated
  - [ ] Update code examples to use structured data mode
    - Replace HTML examples with structured data examples
    - Show both backend API response format and frontend component usage
  - [ ] Verify all code references are current (check file paths and function names)

- [ ] Fix TESTING.md, rename it, and create FRONTEND_TESTING.md
  - [ ] Create `frontend/docs/FRONTEND_TESTING.md` if truly needed (or remove reference)
  - [ ] Update TESTING.md with current test suite status from `250914e_test_suite_triage_and_strategy.md`
  - [ ] Rename TESTING.md to BACKEND_TESTING.md
  - [ ] Document integration-first testing strategy
  - [ ] Add clear testing workflow and commands
  - [ ] Include common test failure patterns and fixes
  - [ ] Create a stub docs/reference/TESTING.md that signposts to the other two

### Stage: Database and reference cleanup

- [ ] Remove Fly.io references from DATABASE.md
  - [ ] Search for all Fly.io mentions
  - [ ] Update to reflect Supabase-only architecture
  - [ ] Verify all connection instructions are current

- [ ] Review and update cross-references
  - [ ] Check all "See also" sections for accuracy
  - [ ] Ensure referenced files exist
  - [ ] Update paths if files have moved
  - [ ] Add missing cross-references where helpful

### Stage: Planning document consolidation

- [x] Review and organize planning documents
  - [x] Use Task tool with subagents to review all docs in `docs/planning/`
  - [x] Identify which planning docs represent completed work
  - [x] Move completed docs to `docs/planning/finished/`
  - [x] Update this planning doc with list of moved files
    - Moved 7 completed planning docs to finished/:
      - 250111_pasting_in_Sourcefile_text.md (Phase 3 complete, moving to documentation)
      - 250111_uploading_audio_Sourcefile.md (Implementation with many completed items)
      - 250315_Phrase_literal_translation.md (Complete feature implementation)
      - 250412_frontend_orchestrated_Sourcefile_processing.md (Marked as "implementation completed")
      - 250420_Sourcefile_debugging.md (Debugging session completed)
      - 250420_site_logo_link_profile.md (Completed attempt, marked as failed)
      - 250914a_content_generation_web_ui.md (Most stages marked as completed)
- [ ] Consolidate authentication documentation
  - [ ] Merge relevant planning details into AUTH.md
  - [ ] Remove redundant auth information from other docs
  - [ ] Ensure single source of truth for auth patterns

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

### Open questions for user

1. **Priority**: Should we focus on the high-priority issues first (ENHANCED_TEXT.md, CONFIGURATION.md, TESTING.md) or do a broader sweep?

2. **Planning docs**: How should we handle the 38+ planning documents? Should we:
   - Archive completed ones to finished/
   - Extract key decisions to reference docs
   - Leave as-is for historical context

3. **New documentation**: Should we create:
   - ARCHITECTURE.md for high-level system design?
   - API.md for endpoint documentation?
   - TROUBLESHOOTING.md for common issues?

4. **Frontend testing**: The backend references FRONTEND_TESTING.md but it doesn't exist. Should we:
   - Create it with Playwright/testing guidance
   - Remove the reference
   - Consolidate all testing into one doc

5. **Scope**: Any specific areas you'd like prioritized or deprioritized?

### Appendix

#### Documentation health metrics from review

**Critical issues (blocks development)**
- ENHANCED_TEXT.md outdated but actively used
- CONFIGURATION.md missing key setup information
- TESTING.md broken reference

**Important issues (causes confusion)**
- 38+ unorganized planning documents
- Fly.io outdated references
- Fragmented auth documentation

**Nice to have (improves experience)**
- Missing architecture overview
- No API documentation
- Inconsistent cross-references

#### Affected stakeholders
- New developers: Need accurate setup and architecture docs
- AI assistants: Rely on AGENTS.md and instruction files
- Maintainers: Need clear testing and deployment docs
- Frontend developers: Missing testing documentation

#### Alternative approaches considered
1. **Full rewrite**: Rejected - too risky, would lose valuable context
2. **Minimal fixes only**: Rejected - doesn't address systemic issues
3. **Gradual improvement**: Selected - fix critical issues first, then improve systematically