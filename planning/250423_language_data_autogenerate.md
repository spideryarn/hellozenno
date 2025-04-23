# Auto-generate Language Data TypeScript File

## Goal

Eliminate API calls to `LANGUAGES_API_GET_LANGUAGES_API` and `LANGUAGES_API_GET_LANGUAGE_NAME_API` by auto-generating a TypeScript file with hardcoded language data, improving frontend performance and reducing backend load.

## Context

Currently, the frontend makes API calls to fetch:
1. The list of all supported languages via `LANGUAGES_API_GET_LANGUAGES_API`  
2. Individual language names via `LANGUAGES_API_GET_LANGUAGE_NAME_API`

These calls add latency and server load. Since language data rarely changes, we can generate this data during build/deployment and eliminate these API calls entirely.

## Key Decisions

- Generate a TypeScript file with language data automatically when Flask starts (similar to routes.ts generation)
- Include methods to replace the current API helper functions
- Keep the language API endpoints available for backward compatibility, but update frontend code to use the generated data

## Useful References

- `/backend/views/languages_api.py` - Current language API endpoints implementation (HIGH)
- `/backend/utils/lang_utils.py` - Contains the functions that retrieve language data (HIGH)
- `/backend/config.py` - Contains SUPPORTED_LANGUAGES and LANGUAGE_NAME_OVERRIDES (HIGH)
- `/frontend/src/lib/utils.ts` - Contains client-side `get_language_name` helper that makes API calls (HIGH)
- `/frontend/src/lib/api.ts` - Contains `getLanguages` helper that makes API calls (HIGH)
- `/backend/docs/URL_REGISTRY.md` - Explains current code generation pattern for routes.ts (MEDIUM)

## Actions

- [x] Create code generator in Flask
  - [x] Create new file `backend/utils/language_data_generator.py` 
  - [x] Add functions to generate TypeScript code from language data in `config.py` and `lang_utils.py`
  - [x] Include TypeScript types for language objects
  - [x] Include helper functions that mimic the API behavior

- [x] Integrate code generator with Flask startup
  - [x] Add commands to generate the language data TypeScript file:
    - `flask generate-language-data` - Only generate language data
    - `flask generate-all-ts` - Generate both routes and language data
  - [x] Hook into the same mechanism that generates routes.ts
  - [x] Generate the file at `frontend/src/lib/generated/languages.ts`
  - [x] Auto-regenerate on Flask development server restart 
  - [x] Ensure language data is generated during production deployment

- [x] Update frontend to use generated data
  - [x] Create TypeScript wrapper functions in `frontend/src/lib/language-utils.ts` 
  - [x] Implement `getLanguages()` and `getLanguageName()` using the generated data
  - [x] Add fallback to API calls if the generated data doesn't have what's needed

- [x] Update frontend components
  - [x] Update `/frontend/src/routes/languages/+page.server.ts` to use new helper
  - [x] Update `/frontend/src/routes/language/[target_language_code]/+layout.server.ts` to use new helper
  - [x] Update `/frontend/src/lib/api.ts` to use static data instead of API calls
  - [x] Update `/frontend/src/lib/utils.ts` to redirect to language-utils.ts

- [ ] Add unit tests (future enhancement)
  - [ ] Test the TypeScript generation in Python
  - [ ] Test the TypeScript helpers with sample data
  - [ ] Verify page layouts still work with the new approach

- [ ] Deploy and verify improvements
  - [ ] Check network tab for absence of language API calls
  - [ ] Verify correct language names appear on all relevant pages
  - [ ] Measure performance improvement

## Generated Code Structure

The generated `languages.ts` looks like:

```typescript
// Auto-generated from Flask language configuration

/**
 * Interface for a language definition
 */
export interface Language {
  /** Two-letter language code (ISO 639-1) */
  code: string;
  /** Human-readable language name */
  name: string;
}

/**
 * All supported languages in the application.
 * This is auto-generated from backend configuration.
 */
export const LANGUAGES: Language[] = [
  { code: "zh", name: "Chinese" },
  { code: "hi", name: "Hindi" },
  { code: "es", name: "Spanish" },
  // ...all supported languages
  { code: "el", name: "Greek (modern)" },
];

/**
 * Map of language codes to language names for quick lookups.
 */
export const LANGUAGE_NAMES: Record<string, string> = {
  "zh": "Chinese",
  "hi": "Hindi",
  "es": "Spanish",
  // ...all supported languages
  "el": "Greek (modern)",
};

/**
 * Get a language name from a language code.
 * 
 * @param target_language_code Two-letter language code
 * @returns The language name, or the code if not found
 */
export function getLanguageName(target_language_code: string): string {
  return LANGUAGE_NAMES[target_language_code] || target_language_code;
}

/**
 * Find a language by its code.
 * 
 * @param target_language_code Two-letter language code
 * @returns The language object, or undefined if not found
 */
export function findLanguageByCode(target_language_code: string): Language | undefined {
  return LANGUAGES.find(lang => lang.code === target_language_code);
}
```

## Implementation Details

1. The TypeScript code is automatically generated during Flask development server startup
2. It's also generated during production deployment through the same mechanism
3. The following CLI commands are available:
   - `flask generate-language-data` - Generate only language data
   - `flask generate-routes-ts` - Generate only routes (existing)
   - `flask generate-all-ts` - Generate both routes and language data
4. The existing API endpoints remain for backward compatibility
5. TypeScript helper functions emulate the API behavior using the static data
6. The system gracefully falls back to API calls if needed (e.g., for an unknown language code)

## Migration Strategy

1. Add the generated code without removing the API endpoints
2. Update frontend code to use the generated helpers first
3. Retain fallback to API calls to ensure robustness
4. Eventually, mark the API endpoints as deprecated once all code is migrated