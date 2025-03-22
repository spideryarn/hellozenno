# URL Structure Standardization Proposal

## Current Issues

Our current URL structure has some inconsistencies that can be confusing:

1. Inconsistent use of singular/plural in resource paths:
   - `/lang/{target_language_code}/lemmas` (plural for list)
   - `/lang/{target_language_code}/lemma/{lemma}` (singular for item)

2. Inconsistent resource hierarchy:
   - Language is sometimes the top category, sometimes a parameter
   - Some routes mix language and resource type in different orders

3. Nested resources are handled inconsistently:
   - `/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/phrases` (phrases as a subcategory)
   - `/lang/{target_language_code}/phrases` (phrases as a top-level resource)

## Proposed URL Structure

I propose moving to a **resource-first URL structure** that is more intuitive and consistent:

### For lemmas:
- `/lemmas/{target_language_code}/{lemma}` (singular resource)
- `/lemmas/{target_language_code}` (list view)

### For phrases:
- `/phrases/{target_language_code}/{phrase_slug}` (singular resource)
- `/phrases/{target_language_code}` (all phrases in language)
- `/phrases/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}` (phrases in a sourcefile)

### For wordforms:
- `/wordforms/{target_language_code}/{wordform}` (singular resource)
- `/wordforms/{target_language_code}` (list view)

### For sentences:
- `/sentences/{target_language_code}/{sentence_slug}` (singular resource)
- `/sentences/{target_language_code}` (list view)

### For source files and directories:
- `/sources/{target_language_code}` (list of sources)
- `/sources/{target_language_code}/{sourcedir_slug}` (specific source directory)
- `/sources/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}` (specific source file)

### For API endpoints:
- `/api/lemmas/{target_language_code}/{lemma}/data`
- `/api/wordforms/{target_language_code}/{wordform}/preview`
- `/api/sentences/{target_language_code}/{slug}/audio`
- `/api/sources/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/generate_audio`

## Benefits

1. **Intuitive resource hierarchy:**
   - Resource type comes first, making it instantly clear what the URL is about
   - Consistent pattern across all resource types is easier to remember
   - Follows standard web conventions that users expect

2. **Logical organization:**
   - Puts the most important identifier (resource type) first
   - Follows a natural narrowing pattern: resource ’ language ’ specific item
   - Makes URLs more predictable - all phrase URLs start with "/phrases"

3. **Better URL readability:**
   - URLs read like English sentences: "phrases in Greek from this source"
   - Easier to understand what a URL does without seeing the page
   - More intuitive for new users to navigate

4. **Improved consistency:**
   - Eliminates the mixing of singular/plural forms (lemma/lemmas)
   - Creates a uniform pattern across the entire application
   - URLs become more self-documenting

5. **Better alignment with REST principles:**
   - Treats resources as the primary organizing principle
   - Follows the collection/item pattern that's standard in RESTful APIs
   - Makes public-facing URLs match common API conventions

## Implementation Strategy

To minimize disruption while implementing this change:

1. Define the new URL structure in a central registry
2. Create redirects from old URLs to new URLs
3. Update templates and JavaScript to use new URL patterns
4. Implement new routes in parallel with old ones
5. Once everything is working with the new routes, deprecate the old ones

This approach allows for a gradual transition without breaking existing links and bookmarks.

## Examples from Popular Websites

Many modern web applications use resource-first URL designs:

- GitHub: `/repos/{owner}/{repo}`
- Twitter: `/users/{username}`
- Stack Overflow: `/questions/{id}`

This approach feels more natural to users and aligns with their mental model of navigating by resource type.

## Additional Considerations

- We should also standardize query parameter naming conventions
- Add proper HTTP status codes for all API responses
- Consider adding versioning for API endpoints (`/api/v1/...`)

## Next Steps

1. Review and approve this proposal
2. Create a detailed implementation plan
3. Prioritize blueprint and view modifications
4. Update URL generation and templates
5. Add redirects from old to new URLs
6. Update documentation