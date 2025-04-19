# Frontend Authentication with Supabase and @supabase/ssr

This document outlines the authentication flow implemented in the SvelteKit frontend using Supabase, leveraging the `@supabase/ssr` library for server-side rendering compatibility.

## Core Concepts

- **Library:** We use `@supabase/ssr` which is the recommended library for handling Supabase authentication in SvelteKit applications, ensuring session management works correctly across server and client contexts.
- **SSR Aware:** The setup is designed to handle Server-Side Rendering (SSR). Authentication state is initialized on the server and passed to the client, which then takes over.
- **Single Client Instance (per context):** The goal is to use a single Supabase client instance within each context (one server-side per request, one client-side for the browser) to avoid warnings and undefined behavior. Client instances are created and managed via SvelteKit's `load` functions and hooks, not through a global singleton import like `$lib/supabaseClient` for general use.

## Implementation Details

1.  **Server Hooks (`src/hooks.server.ts`):**
    - Creates a server-side Supabase client instance (`event.locals.supabase`) for every incoming request using `createServerClient` from `@supabase/ssr`.
    - Configures the client to use SvelteKit's `event.cookies` for reading and writing session information.
    - Provides a `safeGetSession` helper on `event.locals` which retrieves the session from cookies *and* validates the JWT against the Supabase API (`auth.getUser`) for security.
    - Populates `event.locals.session` and `event.locals.user` with the validated session/user data, making it available to server `load` functions.

2.  **Root Layout Data Flow (`src/routes/+layout.server.ts` & `src/routes/+layout.ts`):**
    - `+layout.server.ts`: Takes `session` and `user` from `event.locals` and returns them in its `load` function's result.
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
    - UI elements (like header profile dropdown/login link) reactively use the `session` prop from `data`.

4.  **Authenticated API Calls (`src/lib/api.ts`):**
    - The central `apiFetch` helper function accepts an optional `supabaseClient` argument.
    - **Crucially:** It uses the *passed* client instance (`locals.supabase` from server `load`, `data.supabase` from client `load` or components) to retrieve the current session token.
    - It automatically adds the `Authorization: Bearer <token>` header to outgoing API requests if a session token exists.
    - Helper functions wrapping `apiFetch` (e.g., `getLemmaMetadata`, `getWordformWithSearch`) also accept the `supabaseClient` instance and pass it down.

5.  **Data Loading & Auth Checks (`+page.server.ts`):**
    - Server `load` functions that need to fetch protected data or perform actions based on auth state:
        - Access the server Supabase client via `locals.supabase`.
        - Access the validated session/user via `locals.session` / `locals.user`.
        - Perform redirects (`throw redirect(...)`) if the user is not authenticated but tries to access a protected page.
        - Call API helper functions from `src/lib/api.ts`, passing the `locals.supabase` instance.

6.  **Client-Side Auth Operations (`src/routes/auth/+page.svelte`, etc.):**
    - Pages/components that perform direct auth actions (e.g., login form, signup form):
        - Access the browser Supabase client instance from the `data` prop (passed down from `+layout.ts`).
        - Use this `data.supabase` instance to call Supabase methods like `auth.signInWithPassword()`, `auth.signUp()`, etc.

7.  **Removed Files:**
    - `src/lib/stores/authStore.ts`: Removed as it duplicated state management now handled by the layout data flow and `onAuthStateChange`.
    - `src/lib/apiClient.ts`: Removed as `fetchAuthenticated` was superseded by the updated `apiFetch`.

8.  **Other Considerations (`src/lib/processing-queue.ts`):**
    - Classes or utilities needing the Supabase client (like `SourcefileProcessingQueue`) have been refactored to accept the client instance in their constructor rather than importing a global instance. This ensures they use the correct, context-aware client.

## Backend API Interaction

It's important to note how this frontend authentication flow interacts with the Flask backend API:

- **JWT Verification:** The Flask backend uses utilities in `backend/utils/auth_utils.py` to handle incoming requests.
- **Token Extraction:** It extracts the JWT sent by the frontend in the `Authorization: Bearer <token>` header.
- **Verification:** The `verify_jwt_token` function validates the token's signature against the `SUPABASE_JWT_SECRET`, checks its expiry, and verifies the audience claim (`authenticated`).
- **Decorators:** API endpoints in Flask are protected using decorators from `auth_utils.py`:
    - `@api_auth_required`: Ensures a valid, verified JWT is present. Returns 401 Unauthorized if not.
    - `@api_auth_optional`: Attempts to verify a JWT if present (populating `g.user` and `g.profile` on success) but allows the request to proceed regardless. This is used for endpoints that have different behavior for logged-in vs anonymous users (e.g., allowing anonymous reads but requiring login for generation/writes).
- **User Context:** If authentication is successful (either required or optional), the decorators populate `flask.g.user` with the decoded JWT payload and `flask.g.profile` with the corresponding user profile from the database (creating it if it's the first time seeing this user).

This backend verification ensures that API endpoints are appropriately secured and have access to the authenticated user's context when needed.

## Summary Flow

1.  Request hits the server.
2.  `hooks.server.ts` creates a server client, validates session from cookies, populates `locals`.
3.  `+layout.server.ts` passes session/user from `locals` to client.
4.  `+layout.ts` receives initial session/user, creates browser client, sets up `depends`.
5.  Page `load` functions (server or client) access the appropriate client (`locals.supabase` or `data.supabase`) and session (`locals.session` or `data.session`).
6.  Server `load` functions make authenticated API calls using helpers that pass `locals.supabase` to `apiFetch`.
7.  `+layout.svelte` receives `data` (including browser client and session) and subscribes to auth changes.
8.  UI renders based on initial `data.session`.
9.  Client-side auth actions (e.g., login) use `data.supabase`.
10. `onAuthStateChange` in `+layout.svelte` detects changes, calls `invalidateAll()`, re-runs `load` functions, updates `data` prop, UI updates reactively.
