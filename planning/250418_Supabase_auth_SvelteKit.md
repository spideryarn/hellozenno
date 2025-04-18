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
- [ ] Handle Supabase auth state changes globally (e.g., using a store - needed for Stage 4).
- [ ] Implement logout.
- [x] Manage redirect using `next` parameter (in `+page.svelte` on success).

**Stage 3: Backend API Authentication**
*(Details to be added)*
- Adapt/verify JWT verification in `utils/auth_utils.py`.
- Adapt `@api_auth_required` decorator.
- Implement auto-creation of `Profile` record within the decorator.
- Protect relevant API endpoints.
- Remove unused cookie logic from `auth_api.py`.

**Stage 4: Connecting Frontend and Backend**
*(Details to be added)*
- Add JWT to API requests from SvelteKit.
- Implement profile viewing/editing page (potentially `/profile`).
- Update frontend UI based on auth state (e.g., show user menu).

**Stage 5: Protecting Costly Operations**
*(Details to be added based on future discussion)*
- Decide strategy (backend decorator vs. frontend UI changes).
- Implement protection for endpoints like AI generation.

**Testing:**
- [ ] Add tests alongside feature implementation in each stage.

## Future actions that need to be discussed

Thoughts that need discussion further down the line:
- Hello Zenno is a 'generative dictionary', i.e. it uses LLMs to generate the dictionary entries for words when they're first searched for. This takes a little bit of time, and costs a small amount of money.
- Right now, I want the app to be freely available, at least at small scale. I put it up online a short while ago, and then received a surprisingly large bill soon after for AI tokens. My best guess is that aggressive AI crawler bots were triggering lots of expensive AI-generation.
- My plan for now, is to annotate most of the actions that will incur meaningful costs as being logged-in-users only, hoping that will be enough of a barrier. So we're going to need a simple way to annotate these API functions (e.g. for generating lemma metadata).
- OR Alternatively, we could swap out the buttons on the frontend somehow for non-logged-in users. I want the user interface to be clear to users.
[] Please 

## Appendix

*(To be filled if needed)*
