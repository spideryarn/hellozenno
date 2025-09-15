# Converting Raw Fetch to ApiFetch

## Goal, Context

Replace raw `fetch()` calls with the `apiFetch()` wrapper throughout the frontend codebase to standardize API calls, improve authentication handling, and ensure consistent error management. This addresses several issues found in the AUTHENTICATION_AUTHORISATION.md documentation:

> "Using raw fetch without explicit headers can cause SvelteKit to automatically forward headers from the incoming request, potentially including sensitive tokens or malformed values that cause 'Illegal header value' errors in production."

The codebase currently has a mix of approaches (raw fetch, fetch with manual auth, and apiFetch), making it inconsistent and potentially error-prone.

## Principles, Key Decisions

1. **Security First**: Prioritize proper authentication token handling for all API calls
2. **Consistency**: Standardize on `apiFetch` for all API calls unless there's a compelling reason not to
3. **Compatibility**: Ensure `apiFetch` works correctly in both client and server contexts
4. **Progressive**: Migrate files in small batches, starting with high-risk server-side files
5. **Special Cases**: Consider extending `apiFetch` rather than keeping raw fetch for special cases

We'll extend `apiFetch` to support the following features identified in raw fetch calls:
- Cache control options (e.g., `cache: 'no-cache'`)
- SvelteKit's server fetch compatibility
- Non-JSON response handling

## Useful References

- **`frontend/docs/AUTHENTICATION_AUTHORISATION.md`**: Details authentication flow and explicitly recommends using `apiFetch` over raw fetch. HIGH
- **`frontend/src/lib/api.ts`**: Contains the `apiFetch` implementation. HIGH
- **`auth_utils.py`**: Backend authentication decorator implementation. MEDIUM
- **`frontend/src/routes/+layout.server.ts`**: Shows correct server-side auth handling. MEDIUM
- **`frontend/src/lib/processing-queue.ts`**: Contains complex raw fetch usage with custom error handling. MEDIUM
- **`frontend/src/hooks.server.ts`**: Implements server-side auth setup. LOW

## Actions

- [ ] Enhance `apiFetch` with additional capabilities
  - [ ] Add support for cache control options
  - [ ] Add support for non-JSON response types (blob, text)
  - [ ] Add support for custom request options (cors, etc.)
  - [ ] Update type definitions to reflect new options

- [ ] Convert high-priority server-side load functions
  - [ ] Identify +page.server.ts files calling auth-required API endpoints
  - [ ] Update search page server (`/routes/language/[target_language_code]/search/+page.server.ts`)
  - [ ] Update sourcedir page server (`/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.server.ts`)
  - [ ] Update sourcefile page servers (text, audio, image, etc.)
  - [ ] Test each conversion individually

- [ ] Convert client-side components
  - [ ] Update `processing-queue.ts` with new apiFetch capabilities
  - [ ] Update `EnhancedText.svelte`
  - [ ] Update `Sentence.svelte`
  - [ ] Test components after migration

- [ ] Convert remaining raw fetch calls
  - [ ] Scan codebase for any missed fetch calls
  - [ ] Convert or document reasons for keeping as exceptions

- [ ] Security testing
  - [ ] Test authentication with various API endpoints
  - [ ] Verify that error handling works correctly
  - [ ] Check for any auth-required endpoints still called without proper tokens

- [ ] Documentation
  - [ ] Update any relevant documentation on API calls
  - [ ] Document any remaining raw fetch calls and why they were kept

## Special Cases Consideration

Some raw fetch calls may be kept or need special handling:

1. **SvelteKit Server Context**: Server load functions with specialized fetch behaviors
2. **Direct Response Manipulation**: Endpoints needing direct `Response` object access
3. **Binary Data Handling**: Endpoints returning non-JSON data

## Example Migration Pattern

```typescript
// BEFORE: Raw fetch with manual headers
const headers = new Headers();
if (session?.access_token) {
  headers.set('Authorization', `Bearer ${session.access_token}`);
}

const response = await fetch(
  `${API_BASE_URL}/api/lang/${target_language_code}/unified_search?q=${encodeURIComponent(query)}`,
  { headers }
);

// AFTER: Using apiFetch
const result = await apiFetch({
  supabaseClient: locals.supabase, // or data.supabase on client
  routeName: RouteName.SEARCH_API_UNIFIED_SEARCH_API,
  params: { target_language_code },
  options: {
    method: 'GET',
  },
  query: { q: query }
});
```

# Appendix

## Raw Fetch Usage Summary

Current statistics:
- 19 files using raw `fetch`
- 12 server-side load functions with raw `fetch`
- 8 API modules with auth-required endpoints
- Multiple patterns of auth handling

## Authenticated API Endpoints

The following key endpoints require authentication:
- Sourcefile operations (create, delete, rename, process)
- Sourcedir operations (create, delete, rename)
- Search API (unified_search)
- Sentence operations (delete, rename, generate audio)
- Profile operations
