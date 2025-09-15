# API Integration

SvelteKit components communicate with the Flask backend through API calls. The backend provides a set of RESTful endpoints that are consumed by the frontend.

## Type-Safe API Structure

Flask API endpoints follow the pattern `/api/[resource]/[action]`. All API endpoints are automatically mapped to TypeScript types through a generated routes file, providing type-safety and refactoring protection.

## Authenticated API Calls

The frontend uses the `apiFetch` utility function from `$lib/api.ts` to make API calls. This function:

1. Accepts a Supabase client instance (`supabaseClient`)
2. Automatically extracts the JWT token from the session
3. Adds the `Authorization: Bearer <token>` header to requests if authenticated
4. Handles API-specific error responses, including authentication errors

For detailed information about authentication and passing tokens via `apiFetch`, see [Authentication](./AUTHENTICATION_AUTHORISATION.md).

```typescript
// Example of authenticated API call in a server load function
export const load: PageServerLoad = async ({ locals }) => {
  const { supabase } = locals;
  
  const data = await apiFetch({
    supabaseClient: supabase,
    routeName: RouteName.SOME_API_ENDPOINT,
    params: { /* params */ },
    options: { method: 'GET' }
  });
  
  return { data };
};
```

## Example Usage

Here's how to fetch data from the API in a SvelteKit component:

```typescript
// In a SvelteKit component or page
import { getApiUrl, apiFetch } from '$lib/api';
import { RouteName } from '$lib/generated/routes';

// Fetch languages from the API (type-safe)
async function fetchLanguages(supabaseClient: SupabaseClient | null) {
    return apiFetch({
        supabaseClient,
        routeName: RouteName.LANGUAGES_API_GET_LANGUAGES_API,
        params: {}
    });
}

// Fetch a specific source directory (with parameters)
async function fetchSourceDir(supabaseClient: SupabaseClient | null, target_language_code: string, sourcedir_slug: string) {
    return apiFetch({
        supabaseClient,
        routeName: RouteName.SOURCEDIR_API_SOURCEFILES_FOR_SOURCEDIR_API, 
        params: { target_language_code, sourcedir_slug }
    });
}
```

## Protected API Endpoints

See [Authentication](./AUTHENTICATION_AUTHORISATION.md) for endpoint decorator semantics (`@api_auth_required`, `@api_auth_optional`) and UI behavior on auth errors.
## Common Endpoints

All API endpoints are available as enum values in `RouteName` from the generated routes file.

## Parameter Naming

The backend API uses `target_language_code` as the parameter name, while SvelteKit routes may use `target_language_code`. When calling APIs, always map the SvelteKit route parameter to `target_language_code`.

## Flask development server

The Flask development server (`scripts/local/run_backend.sh`):
- Is being run by the user separately, on port 3000, and generates logs in `logs/backend.log`
- It generates type definitions for routes in `frontend/src/lib/generated/routes.ts`

## SvelteKit 

For more information on SvelteKit, see `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`

## Database Models

The Flask API is built around a set of core database models in PostgreSQL using the Peewee ORM:

- See [MODELS.md](../../backend/docs/MODELS.md) for a comprehensive overview of all database models
- Understanding these models is essential for working with the API endpoints