# API URL Structure Standardization

## Background

We've identified inconsistencies in our API URL structure, particularly around language-specific endpoints. Some endpoints use `/api/resource/<language_code>/...` while others use `/api/lang/<language_code>/resource/...` or other patterns. This creates confusion during development and potential bugs in frontend code.

This issue was discovered when the "New Source Directory" button failed with a 404 error when using `/api/sourcedir/el` instead of the newer pattern `/api/lang/sourcedir/el`.

## Goals

1. Standardize API URL structure across the application
2. Make API routes more discoverable and consistent
3. Minimize disruption to existing functionality
4. Make tests more reliable with a clear API convention
5. Enable easier expansion of the API in the future
6. No need to worry about backwards compatibility

see `@.cursor/rules/coding.mdc`

## Previous Work

We've recently restructured much of our application to use top-level prefixes:
- `/lang/` for language-specific views
- `/auth/` for authentication-related views
- `/sys/` for system management views

This standardization needs to extend to the API layer as well.

## Approach

We will implement the domain-specific API files approach:

1. Create separate API files for each domain (`sourcedir_api.py`, `sourcefile_api.py`, etc.), but only if there are any API views for that domain
2. Register these as blueprints with consistent prefixes
3. Follow a standard URL pattern: `/api/lang/<resource>/...`
4. Keep domain logic in existing view files and import as needed. If it will help with code re-use, pull out sub-functions that can be referenced from multiple places
5. Update frontend code to use the new standardized URLs
6. Ensure tests work with the new URL structure
7. Be cautious though - don't make mistakes or change more than is necessary

## Implementation Plan

1. Store the API views alongside the non-API views, e.g.
   ```
   /views/
     __init__.py
     sourcedir_views.py
     sourcedir_api.py
     sourcefile_api.py
     sourcefile_api.py
     etc.
   ```

2. Implement a consistent blueprint registration pattern in each API file:
   ```python
   # In /views/api/sourcedir_api.py
   sourcedir_api_bp = Blueprint("sourcedir_api", __name__, url_prefix="/api/lang/sourcedir")
   
   @sourcedir_api_bp.route("/<target_language_code>", methods=["POST"])
   def create_sourcedir(target_language_code):
       # Import and use domain logic from sourcedir_views.py
       from views.sourcedir_views import create_sourcedir as sourcedir_view_create
       return sourcedir_view_create(target_language_code)
   ```

3. Register all API blueprints in app creation:
   ```python
   # In app.py or api/index.py
   from views import (
       sourcedir_api_bp,
       sourcefile_api_bp,
       # etc.
   )
   
   app.register_blueprint(sourcedir_api_bp)
   app.register_blueprint(sourcefile_api_bp)
   # etc.
   ```

4. Update frontend code to use the new standard URLs

5. Update tests to reflect the new URL structure


## Advantages

- Clear separation of concerns between web UI and API
- Consistent URL structure makes API usage more intuitive
- Easier to document the API
- Better organization as the codebase grows
- Domain-specific API files can be versioned independently
- Makes it easier to trace API usage in logs and monitoring

## Risks and Mitigations

- **Risk**: Breaking existing frontend code 
  **Mitigation**: Implement and test one domain at a time, prioritizing the most critical functionality

- **Risk**: Duplicating logic between view files and API files
  **Mitigation**: API files should import and reuse domain logic from view files instead of reimplementing

- **Risk**: Test failures due to URL changes
  **Mitigation**: Update tests to match new URL patterns; consider helper functions for test routes

## Next Steps

1. ✅ Implement the new structure for sourcedir-related APIs first
2. ✅ Update corresponding frontend code 
3. ✅ Roll out the approach to other domains (core, wordform, lemma, phrase, sourcefile)
4. Update tests to reflect the new URL **patterns**
   - Tests currently use the old URL structure (e.g., `/api/sourcedir/...`)
   - Tests need to be updated to use the new URL structure (e.g., `/api/lang/sourcedir/...`)
   - Test failures are expected until these updates are made
5. Document the new API structure for developers
   - Add API documentation to explain the standardized URL structure
   - Update any internal documentation referencing the API endpoints

## Implementation Status

### Completed
- ✅ Created domain-specific API files with standardized URL patterns
- ✅ Set up proper imports and registrations in Flask application
- ✅ Updated frontend code to use the new URL patterns
- ✅ Move API endpoints from sourcedir_views.py to sourcedir_api.py
- ✅ Move API endpoints from sentence_views.py to sentence_api.py
- ✅ Create new handlers in sourcefile_api.py for all API endpoints
- ✅ Fixed sourcedirs.js to consistently use /api/lang/sourcedir/... pattern
- ✅ Fixed sentence.js to consistently use /api/lang/sentence/... pattern
- ✅ Fixed sourcefile.js to consistently use /api/lang/sourcefile/... pattern
- ✅ Fixed sourcefiles.js to consistently use the new API URL patterns
- ✅ Updated URL paths in client-side redirects to use /lang/ prefix

### In Progress
- ⏳ Testing the new API structure with real-world usage
- ⏳ Identifying any remaining endpoints that need conversion 
- ✅ Added key endpoints to the core_api.bp urls list for documentation

### To Do
- [✅] Update sentence test files to use the new URL structure
- [ ] Update remaining test files to use the new URL structure
- [ ] Complete API documentation
- [ ] Perform a thorough audit of all API endpoints to ensure consistency
- [ ] Check all other view files for API endpoints that should be moved
- [✅] Run the sentence tests
- [ ] Run the full test suite
- [ ] Test the whole user workflow with the new API structure