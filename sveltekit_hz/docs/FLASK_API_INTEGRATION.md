# API Integration

SvelteKit components communicate with the Flask backend through API calls. The backend provides a set of RESTful endpoints that are consumed by the frontend.


## API Structure

Flask API endpoints follow the pattern `/api/[resource]/[action]`, with all API endpoints defined in corresponding `*_api.py` files in the Flask backend.

## Example Usage

Here's how to fetch data from the API in a SvelteKit component:

```typescript
// In a SvelteKit component or page
import { get_api_url } from '$lib/utils';

// Fetch languages from the API
async function fetchLanguages() {
    const response = await fetch(get_api_url('lang/languages'));
    return await response.json();
}
```

## Common Endpoints

- `/api/lang/languages` - Get all available languages
- `/api/lang/language/<code>` - Get details for a specific language
- `/api/sentence/<slug>` - Get a specific sentence by slug
- `/api/sources/<language_code>` - Get sources for a specific language

## Data Types

When working with the API, ensure your TypeScript definitions match the data structures returned by the API. Define types for all data exchanged with the backend to maintain type safety. 


## Flask development server

The Flask development server (`scripts/local/run_flask.sh`):
- Is being run by the user separately, on port 3000, and generates logs in `logs/flask_app.log`
- It generates a description of the API routes in `static/js/generated/routes.ts`


## SvelteKit 

For more information on SvelteKit, see `sveltekit_hz/docs/SVELTEKIT_ARCHITECTURE.md`