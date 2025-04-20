# Frontend Authentication with Supabase and @supabase/ssr

This document outlines the authentication flow implemented in the SvelteKit frontend using Supabase, leveraging the `@supabase/ssr` library for server-side rendering compatibility.

## Core Concepts

- **Library:** We use `@supabase/ssr` which is the recommended library for handling Supabase authentication in SvelteKit applications, ensuring session management works correctly across server and client contexts.
- **SSR Aware:** The setup is designed to handle Server-Side Rendering (SSR). Authentication state is initialized on the server and passed to the client, which then takes over.
- **Single Client Instance (per context):** The goal is to use a single Supabase client instance within each context (one server-side per request, one client-side for the browser) to avoid warnings and undefined behavior. Client instances are created and managed via SvelteKit's `load` functions and hooks, not through a global singleton import like `$lib/supabaseClient` for general use.
- **Auth Strategy:** Authentication is primarily handled at the API level. Most frontend SvelteKit pages don't explicitly require authentication to view, but data-modifying actions and certain AI-powered features do.
- **Profile Management:** Each authenticated user has a corresponding Profile record in the database to store preferences like target language.

## Implementation Details

1.  **Server Hooks (`src/hooks.server.ts`):**
    - Creates a server-side Supabase client instance (`event.locals.supabase`) for every incoming request using `createServerClient` from `@supabase/ssr`.
    - Configures the client to use SvelteKit's `event.cookies` for reading and writing session information.
    - Provides a `safeGetSession` helper on `event.locals` which retrieves the session from cookies *and* validates the JWT against the Supabase API (`auth.getUser`) for security.
    - Populates `event.locals.session` and `event.locals.user` with the validated session/user data, making it available to server `load` functions.

2.  **Root Layout Data Flow (`src/routes/+layout.server.ts` & `src/routes/+layout.ts`):**
    - `+layout.server.ts`: Takes `session` and `user` from `event.locals` and returns them in its `load` function's result.
    - `+layout.server.ts` also fetches the user's profile if they're logged in, making it available to all routes.
    - `+layout.ts`: 
        - Receives `session` and `user` from the server load via the `data` prop.
        - Creates the *browser-side* Supabase client instance using `createBrowserClient` (only when running in the browser).
        - Uses `depends('supabase:auth')` to mark this load function as dependent on authentication state changes.
        - Returns the `supabase` browser client instance, `session`, and `user` in its result, making them available to all child layouts and pages via the `data` prop.

3.  **Client-Side Synchronization (`src/routes/+layout.svelte`):**
    - Accesses the `supabase` client instance and the initial `session` from the `data` prop.
    - Uses `onMount` to subscribe to `supabase.auth.onAuthStateChange`.
    - When the auth state changes client-side (e.g., login, logout, token refresh) and the new session is different from the one received via `data`, it calls `invalidateAll()`.
    - `invalidateAll()` triggers a re-run of all `load` functions that depend on `'supabase:auth'` (including the root `+layout.ts`), ensuring the application state is updated consistently.
    - UI elements (like header profile dropdown/login link) reactively use the `session` prop from `data`. The header includes either a profile dropdown (if logged in) or a login link (if not).
    - The login link includes a `next` query parameter to return the user to their previous page after login.

4.  **Authenticated API Calls (`src/lib/api.ts`):**
    - The central `apiFetch` helper function accepts an optional `supabaseClient` argument.
    - **Crucially:** It uses the *passed* client instance (`locals.supabase` from server `load`, `data.supabase` from client `load` or components) to retrieve the current session token.
    - It automatically adds the `Authorization: Bearer <token>` header to outgoing API requests if a session token exists.
    - Helper functions wrapping `apiFetch` (e.g., `getLemmaMetadata`, `getWordformWithSearch`, `unifiedSearch`) also accept the `supabaseClient` instance and pass it down.
    - Error handling includes special cases for 401 responses with authentication-related flags.

5.  **Data Loading & Auth Checks:**
    - Protected routes (like `/auth/profile`) use server `load` functions that:
        - Access the server Supabase client via `locals.supabase`.
        - Check `locals.session` / `locals.user` to verify authentication.
        - Perform redirects (`throw redirect(...)`) if the user is not authenticated but tries to access a protected page.
        - Pass the `locals.supabase` client to API helper functions from `src/lib/api.ts`.
    - Regular content pages (like sourcefile pages) typically don't require authentication and still work for anonymous users. API calls from these pages will conditionally include auth tokens if available.

6.  **Client-Side Auth Operations (`src/routes/auth/+page.svelte`):**
    - The main auth page handles both login and signup.
    - It reads the `next` query parameter to redirect users back to their previous page after authentication.
    - It accesses the browser Supabase client instance from the `data` prop (passed down from `+layout.ts`).
    - Uses this `data.supabase` instance to call Supabase methods like `auth.signInWithPassword()`, `auth.signUp()`.
    - It implements proper error handling for various error types (invalid credentials, already exists, etc.).
    - After successful authentication, it uses the `redirectBasedOnProfile` utility from `$lib/navigation` to redirect the user to their preferred language or profile settings.

7.  **Profile Management (`src/routes/auth/profile/`):**
    - Protected route that requires authentication.
    - Fetches the user's profile and available languages.
    - Allows users to set their preferred target language.
    - Updates are sent to the backend API which validates and stores changes.

8.  **Error Handling for Auth-Required Generation:**
    - The frontend handles special error cases from the backend:
    - For lemma metadata: Checks `error.body?.authentication_required_for_generation` flag and displays appropriate UI.
    - For audio generation: Handles `audio_requires_login` flag to show login prompts instead of audio controls.
    - These flags indicate that an operation requires authentication specifically for AI resource usage.

## Backend API Interaction

It's important to note how this frontend authentication flow interacts with the Flask backend API:

- **JWT Verification:** The Flask backend uses utilities in `backend/utils/auth_utils.py` to handle incoming requests.
- **Token Extraction:** It extracts the JWT sent by the frontend in the `Authorization: Bearer <token>` header.
- **Verification:** The `verify_jwt_token` function validates the token's signature against the `SUPABASE_JWT_SECRET`, checks its expiry, and verifies the audience claim (`authenticated`).
- **Decorators:** API endpoints in Flask are protected using decorators from `auth_utils.py`:
    - `@api_auth_required`: Ensures a valid, verified JWT is present. Returns 401 Unauthorized if not.
    - `@api_auth_optional`: Attempts to verify a JWT if present (populating `g.user` and `g.profile` on success) but allows the request to proceed regardless. This is used for endpoints that have different behavior for logged-in vs anonymous users (e.g., allowing anonymous reads but requiring login for generation/writes).
      - **Conditional Generation:** Specific endpoints using `@api_auth_optional` (like those fetching lemma metadata, wordform metadata, or flashcard sentences) might still require authentication *if* the requested data doesn't exist and needs to be generated using costly AI resources (LLMs, TTS). In these cases, if generation is needed and the user is not authenticated (`g.user` is None), the underlying utility functions will raise an `AuthenticationRequiredForGenerationError`. The API endpoint catches this and returns a 401 Unauthorized response, often including a flag like `"authentication_required_for_generation": true` or `"audio_requires_login": true` in the JSON body to inform the frontend.
- **User Context:** If authentication is successful (either required or optional), the decorators populate `flask.g.user` with the decoded JWT payload and `flask.g.profile` with the corresponding user profile from the database (creating it if it's the first time seeing this user). This `g.user` object is then accessible by downstream utility functions (like those performing AI generation) to check if the requesting user is authenticated.
- **Profile Auto-Creation:** When a new user authenticates with the API for the first time, a Profile record is automatically created for them in the `_attempt_authentication_and_set_g` function.

This backend verification ensures that API endpoints are appropriately secured and have access to the authenticated user's context when needed.

## Protected Features

The following features require authentication:

- **AI Generation Operations:**
  - Generating audio for sentences or sourcefiles
  - Processing YouTube audio sources
  - Completing lemma metadata via LLM
  - Extracting text from images
  - Translating sourcefile text
  - Extracting wordforms and phrases

- **Content Creation:**
  - Uploading new sourcefiles
  - Creating sourcefiles from text

- **User Preferences:**
  - Setting target language preferences
  - Managing user profile

Anonymous users can still browse and read all content, but cannot trigger resource-intensive operations or modify data.

## Authentication Flow - Summary

1.  Request hits the server.
2.  `hooks.server.ts` creates a server client, validates session from cookies, populates `locals`.
3.  `+layout.server.ts` passes session/user from `locals` to client and fetches user profile if logged in.
4.  `+layout.ts` receives initial session/user, creates browser client, sets up `depends`.
5.  Page `load` functions (server or client) access the appropriate client (`locals.supabase` or `data.supabase`) and session (`locals.session` or `data.session`).
6.  Server `load` functions make authenticated API calls using helpers that pass `locals.supabase` to `apiFetch`.
7.  `+layout.svelte` receives `data` (including browser client and session) and subscribes to auth changes.
8.  UI renders based on initial `data.session`.
9.  Client-side auth actions (e.g., login) use `data.supabase`.
10. `onAuthStateChange` in `+layout.svelte` detects changes, calls `invalidateAll()`, re-runs `load` functions, updates `data` prop, UI updates reactively.

## Debugging Authentication Issues

When troubleshooting authentication problems:

1. Check browser console for any auth-related errors or warnings
2. Verify that cookies are being set correctly (inspect Application tab in DevTools)
3. Look for 401 errors in network requests to the API
4. Inspect the JWT token using a tool like jwt.io to validate claims
5. Check the backend logs (logs/backend.log) for JWT verification errors
6. Verify that environment variables for Supabase are set correctly
