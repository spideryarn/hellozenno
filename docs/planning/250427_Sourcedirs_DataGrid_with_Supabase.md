# Sourcedir DataGrid with Direct Supabase Queries

## Goal and Context

Evaluate whether we can rewrite the sourcedir page (`/language/[target_language_code]/source/[sourcedir_slug]/`) to use direct Supabase queries instead of the current Flask API approach (`get_sourcefiles_for_sourcedir()`). We want to understand what would be lost or gained by this change.

Currently, the page loads data through the sourcedir API, which handles database access, metadata formatting, and various calculations on the backend. We're considering replacing this with direct Supabase queries from the SvelteKit server components.

## Key Decisions

- **Approach**: After evaluation, we recommend keeping the API approach with some optimizations rather than fully replacing it with direct Supabase queries.
- **Performance improvement**: If performance is a concern, optimize the existing backend API function rather than replacing it entirely.
- **Security**: The backend API provides a consistent security layer that should be maintained.

## Useful References

- **[frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte](../frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte)** - Main SvelteKit component for the sourcedir page. HIGH
- **[frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.server.ts](../frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.server.ts)** - Server load function that fetches data. HIGH
- **[backend/utils/sourcedir_utils.py](../backend/utils/sourcedir_utils.py)** - Contains the `get_sourcefiles_for_sourcedir()` function. HIGH
- **[backend/views/sourcedir_api.py](../backend/views/sourcedir_api.py)** - API endpoints for source directories. MEDIUM
- **[frontend/src/lib/database.types.ts](../frontend/src/lib/database.types.ts)** - TypeScript definitions for Supabase tables. MEDIUM
- **[frontend/src/lib/supabaseClient.ts](../frontend/src/lib/supabaseClient.ts)** - Supabase client initialization. LOW

## Analysis: API vs. Direct Supabase Query

### What we would lose by switching to direct Supabase queries

1. **Backend data processing**:
   - Wordform and phrase counts calculated per sourcefile
   - Metadata enrichment and standardization
   - Vocabulary existence checks
   - Language handling and supported language lists

2. **Error handling**:
   - Consistent error responses
   - Database error abstraction
   - Proper HTTP status codes

3. **Architectural benefits**:
   - Separation of concerns (business logic in backend)
   - API reusability across different clients
   - Centralized security and access controls

### What we would gain by switching

1. **Performance**:
   - Potentially reduced latency (one less HTTP request)
   - Less data serialization/deserialization
   - Direct control over query optimization

2. **Development**:
   - Full control of queries in the frontend
   - More flexibility in data selection
   - Potential for real-time updates with Supabase subscriptions

## Actions

- [ ] **Prototype a direct Supabase implementation**
  - [ ] Create a temporary branch for experimentation
  - [ ] Modify `+page.server.ts` to use Supabase queries
  - [ ] Implement the required data transformations
  - [ ] Compare performance metrics with the current implementation

- [ ] **Optimize the existing backend API**
  - [ ] Profile the current implementation to identify bottlenecks
  - [ ] Consider adding database indexes if needed
  - [ ] Optimize the `get_sourcefiles_for_sourcedir()` function
  - [ ] Reduce data transformations where possible

- [ ] **Address DataGrid consistency issues**
  - [ ] Make sure count fields are consistently named
  - [ ] Ensure consistent date formatting
  - [ ] Standardize metadata fields

- [ ] **Consider hybrid approach**
  - [ ] Use Supabase for direct queries when appropriate
  - [ ] Keep complex operations behind API endpoints
  - [ ] Document the decision criteria for when to use each approach

## Implementation Example (Direct Supabase Query)

Here's a simplified example of how the direct Supabase approach might look:

```typescript
// In +page.server.ts
export const load: PageServerLoad = async ({ params, locals }) => {
  const { target_language_code, sourcedir_slug } = params;
  const { supabase } = locals;

  try {
    // Get the sourcedir entry
    const { data: sourcedir, error: sourcedirError } = await supabase
      .from('sourcedir')
      .select('*')
      .eq('slug', sourcedir_slug)
      .eq('target_language_code', target_language_code)
      .single();

    if (sourcedirError) throw sourcedirError;

    // Get sourcefiles for this sourcedir
    const { data: rawSourcefiles, error: sourcefilesError } = await supabase
      .from('sourcefile')
      .select(`
        id, 
        slug, 
        filename, 
        sourcefile_type, 
        metadata, 
        created_at, 
        updated_at,
        sourcefilewordform:sourcefilewordform(count),
        sourcefilephrase:sourcefilephrase(count)
      `)
      .eq('sourcedir_id', sourcedir.id);

    if (sourcefilesError) throw sourcefilesError;

    // Process sourcefiles to add metadata
    const sourcefiles = rawSourcefiles.map(file => ({
      filename: file.filename,
      slug: file.slug,
      sourcefile_type: file.sourcefile_type,
      created_at: file.created_at,
      updated_at: file.updated_at,
      metadata: {
        ...file.metadata,
        wordform_count: file.sourcefilewordform.length,
        phrase_count: file.sourcefilephrase.length,
        has_audio: file.metadata?.has_audio || false
      }
    }));

    // Check if any sourcefile has vocabulary
    const has_vocabulary = sourcefiles.some(sf => sf.metadata.wordform_count > 0);

    // Get language data
    const language_name = await getLanguageName(target_language_code);
    const supported_languages = await getAllLanguages();

    return {
      sourcedir,
      sourcefiles,
      target_language_code,
      language_name,
      has_vocabulary,
      supported_languages,
      metadata: {
        created_at: sourcedir.created_at,
        updated_at: sourcedir.updated_at
      }
    };
  } catch (err) {
    console.error("Error loading sourcedir:", err);
    throw error(404, {
      message: `Failed to load sourcedir: ${err instanceof Error ? err.message : "Unknown error"}`,
    });
  }
};
```

## Recommendation

We recommend keeping the API approach for the following reasons:

1. **Separation of concerns**: Backend logic should remain in the backend
2. **Code reusability**: The API can be reused in multiple contexts
3. **Security**: Access controls and validation are centralized
4. **Maintainability**: Changes to database structure can be handled in one place

Rather than a full replacement, we suggest optimizing the existing API function if performance is a concern.