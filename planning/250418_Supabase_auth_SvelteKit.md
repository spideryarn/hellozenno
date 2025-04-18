# Supabase Authentication Integration for SvelteKit + Flask API

## Goal & Context

Integrate Supabase Authentication into the Hello Zenno application, enabling user signup, login, logout, and profile management within the current SvelteKit frontend and Flask API architecture.

**Current Stack:**
- Backend: Flask API (on Vercel)
- Database: Supabase (PostgreSQL) with existing `Profile` table
- Frontend: SvelteKit (on Vercel)
- Authentication: None currently implemented in this stack. Previous implementation existed for Flask/Jinja.

## Principles & Key Decisions

- Leverage Supabase Auth for core authentication (`@supabase/supabase-js` on frontend).
- Use JWTs (`Authorization: Bearer <token>` header) for authenticating API requests from SvelteKit to Flask.
- Avoid backend session cookies; rely on frontend token management.
- Reuse Flask backend JWT verification logic (`utils/auth_utils.py`).
- Auto-create user `Profile` in backend upon first verified API request from a new user.
- Implement dedicated `/auth` page in SvelteKit for login/signup UI, handling `?next=` redirect.
- Keep the integration aligned with SvelteKit and Flask best practices, prioritizing simplicity (`rules/CODING-PRINCIPLES.md`).
- Follow a staged approach, starting simple.

## Useful References

- **Previous Flask/Jinja Implementation:** `planning/250316_Supabase_Authentication_Integration.md` - Provides context on how Supabase Auth was used before. (MEDIUM priority)
- **Previous Auth Views (Flask/Jinja):** `backend/views/auth_views.py` - Shows old routes for auth pages, profile, and protection decorator usage. (MEDIUM priority)
- **SvelteKit Frontend Docs:** `frontend/README.md` and linked docs (`docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`, `docs/BACKEND_FLASK_API_INTEGRATION.md`) - Essential for understanding the frontend structure and API interaction. (HIGH priority)
- **Flask API Structure:** `backend/docs/DEVOPS.md` - Overview of backend setup. (LOW priority)
- **Database Models:** `backend/docs/MODELS.md` - Details the `Profile` table structure. (MEDIUM priority)
- **Supabase Auth Docs:** [https://supabase.com/docs/guides/auth](https://supabase.com/docs/guides/auth) - Official documentation for Supabase Auth features. (HIGH priority)
- **Supabase Svelte Auth Helpers:** [https://supabase.com/docs/guides/getting-started/tutorials/with-svelte#auth-helpers](https://supabase.com/docs/guides/getting-started/tutorials/with-svelte#auth-helpers) - Might be useful for SvelteKit integration. (HIGH priority)

## Actions

**Stage 1: Frontend Setup & Basic Auth Page**
- [x] **Install Supabase Client:** Add `@supabase/supabase-js` to `frontend/package.json` and run `npm install` in `frontend/`.
- [x] **Configure Supabase Client:**
    - [x] Create `frontend/src/lib/supabaseClient.ts` to initialize Supabase.
    - [x] Use SvelteKit's public environment variables (`$env/static/public`) for Supabase URL/anon key (e.g., `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY`). Ensure these are added to `.env.local` / Vercel environment.
- [x] **Create Basic Auth Page Route:**
    - [x] Create route files for `/auth` (e.g., `frontend/src/routes/auth/+page.svelte`, `frontend/src/routes/auth/+page.ts`).
    - [x] Add basic placeholders for Login/Signup forms (no logic yet).
    - [x] Read optional `next` query parameter from the URL (e.g., using SvelteKit's `load` function and `url.searchParams.get('next')`).

**Stage 2: Frontend Login/Signup Implementation (Client-Side)**
- [x] Implement UI forms (in `+page.svelte`).
- [x] Call Supabase client methods for login/signup (in `+page.svelte`).
- [x] Handle Supabase auth state changes globally (e.g., using a store - needed for Stage 4).
- [x] Implement logout.
- [x] Manage redirect using `next` parameter (in `+page.svelte` on success).

**Stage 3: Backend API Authentication**
- [x] Adapt/verify JWT verification in `utils/auth_utils.py`.
- [x] Adapt `@api_auth_required` decorator.
- [ ] Implement auto-creation of `Profile` record within the decorator.
- [ ] Protect relevant API endpoints.
- [x] Remove unused cookie logic from `auth_api.py`.
- [x] Remove unused Jinja auth views (`auth_views.py`).

**Stage 4: Connecting Frontend and Backend**
- [x] Add JWT to API requests from SvelteKit (Implicit via Supabase client, needs verification for custom fetch calls).
- [x] Update frontend UI based on auth state (e.g., show user menu).
- [ ] Implement profile viewing/editing page (`/auth/profile`).
  - [x] Create backend API endpoint (GET/PUT `/api/profile`) protected by `@api_auth_required`.
  - [ ] Endpoint should handle fetching/creating `Profile`.
  - [ ] PUT endpoint should validate `target_language_code` using `lang_utils`.
  - [x] Create SvelteKit route `/profile` (`+page.svelte`, `+page.ts`).
  - [ ] Move SvelteKit route to `/auth/profile`.
  - [ ] Fix profile data loading (CORS/fetch error).
  - [ ] Fetch profile data and available languages from backend.
  - [ ] Implement form to update `target_language_code`.
  - [ ] Call backend API to save changes.
- [x] Improve header UI:
  - [x] Make profile display more compact (dropdown menu).
  - [x] Include email, link to `/profile`, and logout button in dropdown.
  - [x] Make "Login / Sign Up" link include `?next=CURRENT_PAGE`.

**Stage 5: Protecting Costly Operations**
- **Adopt Hybrid Approach:**
  - **Backend:** Identify API endpoints triggering LLM/TTS/Transcription calls and protect them either directly (`@api_auth_required`) or conditionally (checking `g.user` before generation).
  - **Frontend:** Use the `$session` store (or `$user` store) in relevant Svelte components to conditionally display/enable controls. Show disabled state or "Login required" prompt for logged-out users.
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
    - [ ] Define custom exception `AuthenticationRequiredForGenerationError` (e.g., in `utils/exceptions.py` or `utils/auth_utils.py`).
    - [ ] Modify `utils/store_utils.py -> load_or_generate_lemma_metadata`: Check `g.user` before calling `_generate_and_save_metadata`. If generation needed and no user, raise `AuthenticationRequiredForGenerationError`.
    - [ ] Modify `lemma_api.py -> get_lemma_metadata_api`: Add `try...except AuthenticationRequiredForGenerationError` around the call to `load_or_generate_lemma_metadata`. In `except`, return `jsonify({"error": "Authentication required to generate full lemma details"}), 401` (or 403).
  - **Stage 5.3: Backend - Conditional Gating (Flashcard Sentence Audio):**
    - [ ] Modify `utils/audio_utils.py -> get_or_create_sentence_audio`: Check `g.user` before calling `generate_and_save_audio`. If generation needed and no user, raise `AuthenticationRequiredForGenerationError`.
    - [ ] Modify `utils/flashcard_utils.py -> prepare_flashcard_sentence_data`: Add `try...except AuthenticationRequiredForGenerationError` around the call to `get_or_create_sentence_audio`. If caught, proceed but include a flag indicating audio generation was skipped due to auth (e.g., add `audio_requires_login=True` to the returned data dictionary).
    - [ ] Modify `flashcard_api.py -> flashcard_sentence_api`: Ensure the response structure accommodates the potential `audio_requires_login` flag from the util function.
  - **Stage 5.4: Frontend - Handle Conditional Lemma Error:**
    - [ ] Search frontend (`*.svelte`, `*.ts`) for usage of `RouteName.LEMMA_API_GET_LEMMA_METADATA_API`.
    - [ ] Update API client calls or component logic (likely in lemma detail page) to specifically catch the 401/403 error *from this endpoint*. Display a user-friendly message (e.g., "Login to generate full details") instead of a generic fetch error, while still showing any existing partial data.
  - **Stage 5.5: Frontend - Handle Conditional Flashcard Audio:**
    - [ ] Search frontend for usage of `RouteName.FLASHCARD_API_FLASHCARD_SENTENCE_API`.
    - [ ] Update component logic (likely flashcard view) to check for the `audio_requires_login` flag in the API response. If true, disable the audio player or show a "Login to hear audio" message.
  - **Stage 5.6: Frontend - UI for Directly Gated Actions:**
    - [ ] Identify components triggering APIs gated in Stage 5.1 (Audio generation, YouTube add, Uploads, Text creation).
    - [ ] Use `$user` store checks in these components to hide/disable UI elements (buttons, forms) for logged-out users. Show appropriate "Login required" prompts/links (`/auth?next=...`).

**Testing:**
- [ ] Add tests alongside feature implementation in each stage.

## Future actions that need to be discussed - how to restrict access

Thoughts that need discussion further down the line:
- Hello Zenno is a 'generative dictionary', i.e. it uses LLMs to generate the dictionary entries for words when they're first searched for. This takes a little bit of time, and costs a small amount of money.
- Right now, I want the app to be freely available, at least at small scale. I put it up online a short while ago, and then received a surprisingly large bill soon after for AI tokens. My best guess is that aggressive AI crawler bots were triggering lots of expensive AI-generation.
- My plan for now, is to annotate most of the actions that will incur meaningful costs as being logged-in-users only, hoping that will be enough of a barrier. So we're going to need a simple way to annotate these API functions (e.g. for generating lemma metadata).
- OR Alternatively, we could swap out the buttons on the frontend somehow for non-logged-in users. I want the user interface to be clear to users.
[] Please 

## Appendix

*(To be filled if needed)*
