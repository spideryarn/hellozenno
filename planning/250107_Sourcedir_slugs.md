## Slug Migration Plan

### Goals
1. Replace path-based URLs with slug-based URLs for Sourcedir
2. Keep path as primary identifier, add slug for URL display only
3. Auto-generate slugs from path using python-slugify
4. Maintain uniqueness per language_code
5. Keep changes minimal and focused
6. No transition period or redirects needed
7. Later: Apply same pattern to Sourcefiles

### Progress
- [x] Define SOURCEDIR_SLUG_MAX_LENGTH in config.py
- [x] Add slug column to Sourcedir model with auto-generation
- [x] Create migration to add slug column
- [x] Update view functions to use slug in URLs
- [x] Update templates to use slug in URLs
- [x] Update tests to work with slugs
- [x] Test and verify all changes
- [x] Rename template variables for clarity (sourcedir_path vs sourcedir_slug)
- [x] Fix slug collision handling in create_sourcedir
- [x] Fix filename generation in upload_sourcefile to use path
- [x] Update tests to use slugs in URLs consistently

### Next Steps
1. Add slug collision handling:
   - Add incremental number suffix for collisions
   - Update migration and model save() method
   - Add tests for collision cases
2. Apply same pattern to Sourcefiles:
   - Add slug column to Sourcefile model
   - Create migration
   - Update views and templates
   - Update tests
3. Consider adding slug validation:
   - Maximum length checks
   - Character set restrictions
   - Collision handling improvements
4. Add documentation:
   - Update API documentation
   - Add examples of slug usage
   - Document slug generation rules

### Design Decisions
- Slug uniqueness: Will be enforced at database level per language_code
- Slug generation: Automatic from path, no manual override
- Collisions: Initially handled by returning 409 Conflict
- URL structure: /<language_code>/<slug>/

### Implementation Details
- Added SOURCEDIR_SLUG_MAX_LENGTH = 100 to config.py
- Added slug CharField to Sourcedir model with auto-generation
- Created migration that:
  1. Adds nullable slug column
  2. Generates slugs for existing records
  3. Makes column required
  4. Adds unique index on (slug, language_code)
- Slug generation:
  - Simple slugify of path
  - Basic collision handling (409 response)
  - Max length constraints
