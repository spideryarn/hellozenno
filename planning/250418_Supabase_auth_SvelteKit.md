# Supabase Authentication Integration for SvelteKit + Flask API

## Goal & Context

Integrate Supabase Authentication into the Hello Zenno application, enabling user signup, login, logout, and profile management within the current SvelteKit frontend and Flask API architecture.

**Current Stack:**
- Backend: Flask API (on Vercel)
- Database: Supabase (PostgreSQL) with existing `Profile` table
- Frontend: SvelteKit (on Vercel) with `@supabase/ssr` for auth handling
- Authentication: Supabase Auth via `@supabase/ssr`

## Principles & Key Decisions

- Leverage Supabase Auth for core authentication (`@supabase/ssr` on frontend).
- Use JWTs (`Authorization: Bearer <token>` header) for authenticating API requests from SvelteKit to Flask.
- Avoid backend session cookies; rely on frontend token management.
- Reuse Flask backend JWT verification logic (`utils/auth_utils.py`).
- Auto-create user `Profile` in backend upon first verified API request from a new user (handled in `_attempt_authentication_and_set_g`).
- Implement dedicated `/auth` page in SvelteKit for login/signup UI, handling `?next=` redirect.
- Keep the integration aligned with SvelteKit and Flask best practices, prioritizing simplicity (`rules/CODING-PRINCIPLES.md`).
- Follow a staged approach, starting simple.

## Useful References

- **Previous Flask/Jinja Implementation:** `planning/250316_Supabase_Authentication_Integration.md` - Provides context on how Supabase Auth was used before. (MEDIUM priority)
- **Previous Auth Views (Flask/Jinja):** `backend/views/auth_views.py` - Shows old routes for auth pages, profile, and protection decorator usage. (MEDIUM priority)
- **SvelteKit Frontend Docs:** `frontend/README.md` and linked docs (`docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`, `docs/BACKEND_FLASK_API_INTEGRATION.md`, `docs/AUTH.md`) - Essential for understanding the frontend structure and API interaction. (HIGH priority)
- **Flask API Structure:** `backend/docs/DEVOPS.md` - Overview of backend setup. (LOW priority)
- **Database Models:** `backend/docs/MODELS.md` - Details the `Profile` table structure. (MEDIUM priority)
- **Supabase Auth Docs:** [https://supabase.com/docs/guides/auth](https://supabase.com/docs/guides/auth) - Official documentation for Supabase Auth features. (HIGH priority)
- **Supabase SSR Docs:** [https://supabase.com/docs/guides/auth/server-side-rendering](https://supabase.com/docs/guides/auth/server-side-rendering) - Relevant for the `@supabase/ssr` package. (HIGH priority)

## Actions

**Stage 1: Frontend Setup & Basic Auth Page**
- [x] **Install Supabase Client:** Add `@supabase/supabase-js` to `frontend/package.json`. (Now also using `@supabase/ssr`).
- [x] **Configure Supabase Client:**
    - [x] Use SvelteKit's public environment variables (`$env/static/public`) for Supabase URL/anon key.
    - [x] Setup `@supabase/ssr` with `hooks.server.ts`, `+layout.server.ts`, `+layout.ts`.
- [x] **Create Basic Auth Page Route:**
    - [x] Create route files for `/auth` (`+page.svelte`).
    - [x] Read optional `next` query parameter from the URL.

**Stage 2: Frontend Login/Signup Implementation (Client-Side)**
- [x] Implement UI forms (in `/auth/+page.svelte`).
- [x] Call Supabase client methods for login/signup (using client passed from layout data).
- [x] Handle Supabase auth state changes globally (via `onAuthStateChange` in root `+layout.svelte`, triggering `invalidateAll`).
- [x] Implement logout (in root `+layout.svelte`).
- [x] Manage redirect using `next` parameter (in `+page.svelte` on success).

**Stage 3: Backend API Authentication**
- [x] Adapt/verify JWT verification in `utils/auth_utils.py` (`verify_jwt_token`).
- [x] Adapt `@api_auth_required` decorator.
- [x] Implement auto-creation of `Profile` record (verified in `_attempt_authentication_and_set_g`).
- [ ] Protect *all* relevant API endpoints (review needed).
- [x] Remove unused cookie logic from `auth_api.py` (Assuming done previously or not applicable).
- [x] Remove unused Jinja auth views (`auth_views.py`) (Assuming done previously or not applicable).

**Stage 4: Connecting Frontend and Backend**
- [x] Add JWT to API requests from SvelteKit (Handled automatically by modified `apiFetch` in `$lib/api.ts`).
- [x] Update frontend UI based on auth state (Root layout uses `data.session`).
- [ ] Implement profile viewing/editing page (`/auth/profile`).
  - [ ] **Create backend API endpoints:**
      - [ ] GET `/api/profile` protected by `@api_auth_required`. (Needs implementation).
      - [ ] PUT `/api/profile` protected by `@api_auth_required`. (Needs implementation).
      - [ ] PUT endpoint should validate `target_language_code` using `lang_utils`.
  - [x] Create SvelteKit route `/auth/profile` (`+page.svelte`, `+page.server.ts`).
  - [x] Fetch profile data and available languages from backend (via `+page.server.ts`, using placeholder `getProfile`).
  - [x] Implement form to update `target_language_code` (in `+page.svelte`).
  - [ ] Call backend API to save changes (needs PUT endpoint implementation and potentially `RouteName` update).
- [x] Improve header UI:
  - [x] Make profile display more compact (dropdown menu).
  - [x] Include email, link to `/auth/profile`, and logout button in dropdown.
  - [x] Make "Login / Sign Up" link include `?next=CURRENT_PAGE`.

**Stage 5: Protecting Costly Operations**
- **Adopt Hybrid Approach:**
  - **Backend:** Identify API endpoints triggering LLM/TTS/Transcription calls and protect them either directly (`@api_auth_required`) or conditionally (checking `g.user` before generation).
  - **Frontend:** Use the `session` prop (from layout `data`) in relevant Svelte components to conditionally display/enable controls. Show disabled state or "Login required" prompt for logged-out users.
  - **Error Handling:** Ensure robust frontend handling for potential 401/403 errors from conditionally gated APIs.

- **Detailed Implementation Plan:**
  - **Stage 5.1: Backend - Direct Gating:**
    - [ ] Add `@api_auth_required` to `sourcefile_api.generate_sourcefile_audio_api`.
    - [ ] Add `@api_auth_required` to `sourcedir_api.add_youtube_audio_api`.
    - [ ] Add `@api_auth_required` to `sentence_api.generate_sentence_audio_api`.
    - [ ] Add `@api_auth_required` to `lemma_api.complete_lemma_metadata_api`.
    - [ ] Add `@api_auth_required` to `sourcedir_api.upload_sourcedir_new_sourcefile_api` (file uploads).
    - [ ] Add `@api_auth_required` to `sourcefile_api.create_sourcefile_from_text_api` (text file creation).
    - [x] Verify `@api_auth_required` is present on endpoints in `sourcefile_api_processing.py` (extract_text, translate, process_wordforms, process_phrases).
  - **Stage 5.2: Backend - Conditional Gating (Lemma Generation):**
    - [x] Define custom exception `AuthenticationRequiredForGenerationError`.
    - [x] Modify `utils/store_utils.py -> load_or_generate_lemma_metadata`.
    - [x] Modify `lemma_api.py -> get_lemma_metadata_api`.
  - **Stage 5.3: Backend - Conditional Gating (Flashcard Sentence Audio):**
    - [ ] Modify `utils/audio_utils.py -> get_or_create_sentence_audio`: Check `g.user` before calling `generate_and_save_audio`. If generation needed and no user, raise `AuthenticationRequiredForGenerationError`.
    - [ ] Modify `utils/flashcard_utils.py -> prepare_flashcard_sentence_data`: Add `try...except AuthenticationRequiredForGenerationError` around the call to `get_or_create_sentence_audio`. If caught, proceed but include a flag indicating audio generation was skipped due to auth (e.g., add `audio_requires_login=True` to the returned data dictionary).
    - [ ] Modify `flashcard_api.py -> flashcard_sentence_api`: Ensure the response structure accommodates the potential `audio_requires_login` flag from the util function.
  - **Stage 5.4: Frontend - Handle Conditional Lemma Error:**
    - [x] Search frontend (`*.svelte`, `*.ts`) for usage of `RouteName.LEMMA_API_GET_LEMMA_METADATA_API`.
    - [x] Update API client calls or component logic (Handled in `$lib/api.ts -> getLemmaMetadata` and `lemma/[lemma]/+page.server.ts`).
  - **Stage 5.5: Frontend - Handle Conditional Flashcard Audio:**
    - [ ] Search frontend for usage of `RouteName.FLASHCARD_API_FLASHCARD_SENTENCE_API`.
    - [ ] Update component logic (likely flashcard view) to check for the `audio_requires_login` flag in the API response. If true, disable the audio player or show a "Login to hear audio" message.
  - **Stage 5.6: Frontend - UI for Directly Gated Actions:**
    - [ ] Identify components triggering APIs gated in Stage 5.1 (Audio generation, YouTube add, Uploads, Text creation).
    - [ ] Use `session` prop checks in these components to hide/disable UI elements (buttons, forms) for logged-out users. Show appropriate "Login required" prompts/links (`/auth?next=...`).


**Stage: Avoid initial loading flash where the user interface appears to be for an anonymous user, then realises if you're logged in and updates**
- [ ] Reproduce the problem with Playwright MCP
- [ ] Add actions here...

**Testing:**
- [ ] Add tests alongside feature implementation in each stage.

## Next Steps

1.  **Implement Profile API:** Create the backend API endpoints (`GET` and `PUT /api/profile`) required by the `/auth/profile` page. Ensure the PUT endpoint includes validation.
2.  **Generate Routes:** Update `RouteName` enum and regenerate frontend routes if necessary for the new profile endpoints.
3.  **Review API Protection:** Systematically review all backend API endpoints and apply `@api_auth_required` or `@api_auth_optional` as needed (Stage 3 completion).
4.  **Address Costly Operations:** Proceed with Stage 5 implementation, protecting LLM/TTS/etc. calls.

## Appendix

*(To be filled if needed)*
