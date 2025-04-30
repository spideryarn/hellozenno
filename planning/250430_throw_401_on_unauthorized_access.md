# Improving Authentication Response Status Codes

## Problem Statement

Currently, when unauthorized users access resources requiring authentication (like lemma pages that need generation), the application:
1. Returns a 200 OK HTTP status 
2. Includes an error message in the page content
3. Provides a login link to authenticate

This approach works from a user perspective but has drawbacks:
- Search engines and crawlers may index content that shouldn't be accessible
- HTTP status codes don't accurately reflect the true state of the resource
- Tools/scripts interacting with the API don't receive the proper error codes
- Status monitoring may not correctly detect authentication failures

For example, when accessing a lemma page that requires authentication to generate content:
```bash
curl "http://localhost:5173/language/el/lemma/%CF%84%CF%81%CE%B1%CF%84%CE%AC%CF%81%CF%89"
# Returns 200 OK even though the user needs to authenticate
```

## Proposed Solution

Modify the application to properly propagate 401 Unauthorized status codes from the API to the frontend HTTP response when authentication is required.

### Implementation Approach

1. **Modify server-side load functions** to detect authentication errors and throw SvelteKit errors with proper status codes
2. **Maintain the existing error page UX** for a smooth user experience
3. **Standardize the pattern** for reuse across the application

### Detailed Implementation Steps

#### 1. Update the Lemma Page Server Load Function

In `frontend/src/routes/language/[target_language_code]/lemma/[lemma]/+page.server.ts`:

```typescript
export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code, lemma } = params;
    const { supabase, session } = locals;

    try {
        // Call the helper function, passing the server client instance
        const lemmaResult = await getLemmaMetadata(supabase, target_language_code, lemma);

        // Check if authentication is required for generation and propagate the 401 status code
        if (lemmaResult.authentication_required_for_generation) {
            throw error(401, {
                message: lemmaResult.description || 'Authentication required to generate lemma data',
                body: lemmaResult // Include original error data for the error page
            });
        }

        // Only reach here for successful results
        return {
            session: session,
            lemmaResult: lemmaResult,
            target_language_code: target_language_code,
            lemma: lemma,
        };

    } catch (err: any) {
        // If the error already has status and body, pass it through
        if (err.status === 401) {
            // Already handled above, just re-throw
            throw err;
        }
        
        // Handle other errors from getLemmaMetadata
        console.error("Error loading lemma in +page.server.ts:", err);
        // Throw SvelteKit error for unexpected issues
        throw error(
            err.status || 500,
            {
                message: `Failed to load lemma: ${err.message || String(err)}`,
                // If there's a body from the API, include it
                ...(err.body ? { body: err.body } : {})
            }
        );
    }
};
```

This implementation:
1. Detects authentication requirement flags in the API response
2. Converts them to proper SvelteKit errors with 401 status
3. Preserves error context in the error payload for the error page to use

#### 2. Update the Wordform Page Server Load Function

Added the same 401 error handling pattern to `frontend/src/routes/language/[target_language_code]/wordform/[wordform]/+page.server.ts`.

The implementation follows the same approach as the lemma page:
- Detects `authentication_required_for_generation` flag
- Throws 401 SvelteKit error when authentication is required
- Includes session in all successful responses

#### 3. Apply the Pattern to Other Server Load Functions

This same pattern should be applied to other server-side load functions that might encounter authentication requirements:

- Sentence audio generation
- Sourcefile processing endpoints
- Any other feature that uses `authentication_required_for_generation` or similar flags

#### 4. Testing Implementation

Test the implementation with curl to verify proper status codes:

```bash
# Should return 401 when authentication is required
curl -I "http://localhost:5173/language/el/lemma/%CF%84%CF%81%CE%B1%CF%84%CE%AC%CF%81%CF%89"
```

## Benefits of this Approach

1. **Standards compliance**: HTTP status codes accurately reflect the resource state
2. **SEO improvement**: Search engines won't index unauthorized content
3. **API consistency**: Scripts/tools receive proper error codes
4. **Monitoring**: Status monitoring can correctly detect authentication failures
5. **Maintained UX**: The error page still provides a friendly login experience

## Potential Concerns

1. **Implementation effort**: Each server-side load function needs to be updated
2. **Error page customization**: May need tweaks to error display components
3. **Edge cases**: Special handling may be needed for partial data scenarios

## Next Steps

1. ✅ Implement and test for lemma page
2. ✅ Implement and test for wordform page
3. Identify other load functions needing similar treatment
4. Standardize the pattern for reuse
5. Consider creating a utility function to simplify implementation