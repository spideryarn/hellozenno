## Slug Migration Plan for Sourcefile

### Goals
1. Add slug field to Sourcefile model as groundwork for future URL improvements
2. Keep filename as primary identifier, add slug for URL display only
3. Auto-generate slugs from filename using python-slugify
4. Maintain uniqueness per sourcedir_id
5. Keep changes minimal and focused
6. Don't change current URL behavior yet

### Progress
- [x] Define SOURCEFILE_SLUG_MAX_LENGTH in `config.py`
- [x] Add slug column to Sourcefile model with auto-generation in `db_models.py`
- [x] Create migration similar to `migrations/008_add_sourcedir_slug.py`
- [x] Add tests to verify slug generation
- [x] Clean up helper functions (removed duplicate _get_sourcefile_entry_from_slug)
- [x] Update delete endpoint to use slug in URL but filename for operations
- [x] Update rename endpoint to use slug in URL and update slug on rename
- [x] Update view functions to handle slug-based URLs (using `delete_sourcefile` as a template):
  - [x] `view_sourcefile` function in `sourcedir_views.py`
  - [x] `inspect_sourcefile` function in `sourcedir_views.py`
  - [x] `sourcefiles_for_sourcedir` function in `sourcedir_views.py`
  - [x] `process_sourcefile` function in `sourcedir_views.py`
  - [x] `_navigate_sourcefile` function in `sourcedir_utils.py`
  - [x] `play_sourcefile_audio` function in `sourcedir_views.py`
  - [x] `sourcefile_sentences` function in `sourcedir_views.py`
- [x] Update templates to use slug-based URLs:
  - [x] `templates/sourcefile.jinja`: Update all URL generation
  - [x] Fix failing tests:
    - [x] `test_auto_linking_wordforms`: Updated to use slug-based URLs
    - [x] `test_auto_linking_case_insensitive`: Fixed template class name mismatch
    - [x] `test_sourcefile_phrase_metadata`: Updated to use slug-based URLs

### Next Steps
1. Update remaining templates:
   - [ ] `templates/sourcefiles.jinja`: Update file listing URLs
   - [ ] `templates/inspect_sourcefile.jinja`: Update navigation links

2. Update JavaScript functions to use slug-based URLs:
   - [ ] `static/js/sourcefile.js`: Update API endpoints for rename/delete
   - [ ] `static/js/navigation.js`: Update prev/next navigation

### Implementation Details
1. In `config.py`:
   ```python
   SOURCEFILE_SLUG_MAX_LENGTH = 100  # Same as SOURCEDIR_SLUG_MAX_LENGTH
   ```

2. In `db_models.py`, added to Sourcefile model:
   ```python
   class Sourcefile(BaseModel):
       # ... existing fields ...
       slug = CharField(max_length=SOURCEFILE_SLUG_MAX_LENGTH)

       def save(self, *args, **kwargs):
           if not self.slug:
               self.slug = slugify(str(self.filename))
           return super().save(*args, **kwargs)

       class Meta:
           indexes = (
               (("sourcedir", "filename"), True),  # Composite unique index
               (("sourcedir", "slug"), True),  # Unique slug per sourcedir
           )
   ```

3. Created `migrations/009_add_sourcefile_slug.py`:
   - Adds nullable slug column
   - Generates slugs for existing records using slugify
   - Makes column required
   - Adds unique index on (slug, sourcedir_id)

### Design Decisions
- Slug uniqueness: Enforced at database level per sourcedir_id
- Slug generation: Simple slugify of filename, no manual override
- Collisions: Return 409 Conflict (keeping it simple for now)
- URL structure: Use slugs for URLs only (/<language_code>/<sourcedir_slug>/<sourcefile_slug>)
- Display: Use path/filename for display and identification
- Naming: Use explicit suffixes (_path, _filename, _slug) to clarify purpose
- Renaming: Update slug when filename changes
- No redirects or transition period needed at this stage

### Files Modified
1. `config.py` - Added SOURCEFILE_SLUG_MAX_LENGTH constant
2. `db_models.py` - Added slug field to Sourcefile model with auto-generation
3. `migrations/009_add_sourcefile_slug.py` - New migration file
4. `test_sourcedir_views.py` - Added slug generation tests
5. `sourcedir_utils.py` - Updated navigation functions to use slugs
6. `sourcedir_views.py` - Updated view functions to use slugs

### Potential Steps to Discuss in Future
1. Add collision handling if needed (numeric suffixes)
2. Consider slug validation improvements
3. Update API documentation 

## Progress Update (Jan 11)

### Fixed Issues
- Restored component words display in phrases section that was accidentally removed in commit `b63c75b3871867b7a8afe3e0f70655e36408febb`
- Fixed section ordering in `templates/sourcefile.jinja`:
  1. Words section (first)
  2. Phrases section (second)
  3. Text section (third)
  4. Translation section (last)
- Restored proper translation section with collapsible details and paragraph handling
- Made phrases section always visible with "No phrases found" message when empty

### Git History Investigation
- Found that commit `b63c75b3871867b7a8afe3e0f70655e36408febb` ("All the other Sourcefile slug changes") had unintentionally removed several template features while implementing slug-based URLs
- The commit was primarily focused on URL structure changes but included template restructuring that removed:
  - Component words display in phrases
  - Proper translation section with paragraph handling
  - Correct section ordering

### Next Steps
1. Run full test suite to verify all template changes work correctly
2. Consider adding visual separation between sections (e.g., consistent spacing or dividers)
3. Review other files changed in `b63c75b` to ensure no other unintended changes
