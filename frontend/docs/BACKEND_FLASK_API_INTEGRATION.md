# API Integration

SvelteKit components communicate with the Flask backend through API calls. The backend provides a set of RESTful endpoints that are consumed by the frontend.

## Type-Safe API Structure

Flask API endpoints follow the pattern `/api/[resource]/[action]`. All API endpoints are automatically mapped to TypeScript types through a generated routes file, providing type-safety and refactoring protection.

## Example Usage

Here's how to fetch data from the API in a SvelteKit component:

```typescript
// In a SvelteKit component or page
import { getApiUrl } from '$lib/api';
import { RouteName } from '$lib/generated/routes';

// Fetch languages from the API (type-safe)
async function fetchLanguages() {
    const url = getApiUrl(RouteName.LANGUAGES_API_GET_LANGUAGES_API, {});
    const response = await fetch(url);
    return await response.json();
}

// Fetch a specific source directory (with parameters)
async function fetchSourceDir(target_language_code: string, sourcedir_slug: string) {
    const url = getApiUrl(
        RouteName.SOURCEDIR_API_SOURCEFILES_FOR_SOURCEDIR_API, 
        { target_language_code, sourcedir_slug }
    );
    const response = await fetch(url);
    return await response.json();
}
```

## Common Endpoints

All API endpoints are available as enum values in `RouteName` from the generated routes file.

## Parameter Naming

The backend API uses `target_language_code` as the parameter name, while SvelteKit routes may use `language_code`. When calling APIs, always map the SvelteKit route parameter to `target_language_code`.

## Flask development server

The Flask development server (`scripts/local/run_backend.sh`):
- Is being run by the user separately, on port 3000, and generates logs in `logs/flask_app.log`
- It generates type definitions for routes in `frontend/src/lib/generated/routes.ts`

## SvelteKit 

For more information on SvelteKit, see `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`