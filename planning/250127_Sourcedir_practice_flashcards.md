# Sourcedir-level Flashcard Practice

## Goal
Add ability to practice flashcards for all lemmas in a sourcedir (directory of sourcefiles). This will allow users to practice vocabulary from multiple related files in one session.

### Desired Behavior
1. User visits sourcedir page (e.g. `/el/my-textbook-ch1/`)
2. Clicks "Practice with Flashcards" button
3. Redirected to flashcards view filtered by sourcedir (e.g. `/el/flashcards?sourcedir=my-textbook-ch1`)
4. System shows flashcards for sentences containing any lemma from any sourcefile in that sourcedir
5. Random selection from qualifying sentences, same UI/interaction as existing flashcards

## Implementation Tasks

### Backend Changes (Priority 1)
- [ ] Add sourcedir parameter support to `flashcard_views.py`
  ```python:flashcard_views.py
  # ... existing imports ...
  from models import Sourcedir, Sourcefile, SourcefileWordform  # Add these if missing
  
  def get_sourcedir_lemmas(language_code: str, sourcedir_slug: str) -> list[str]:
      """Get unique lemmas from all sourcefiles in a sourcedir"""
      try:
          sourcedir_entry = Sourcedir.get(
              slug=sourcedir_slug,
              language_code=language_code
          )
          query = (SourcefileWordform
                  .select(fn.DISTINCT(Wordform.lemma))
                  .join(Sourcefile)
                  .join(Wordform)
                  .where(Sourcefile.sourcedir == sourcedir_entry))
          return [w.wordform.lemma for w in query]
      except DoesNotExist:
          abort(404, "Directory not found")
  
  # In flashcard_landing route:
  if sourcedir:
      lemmas = get_sourcedir_lemmas(language_code, sourcedir)
      if not lemmas:  # Add this error check
          abort(404, "Directory contains no practice vocabulary")
  # ... rest of existing logic ...
  ```

### Frontend Changes (Priority 2)
- [ ] Update button in `sourcefiles.jinja` to match sourcefile practice button:
  ```jinja:templates/sourcefiles.jinja
  {# ... existing code ... #}
  <div class="practice-button">
      <a href="{{ url_for('flashcard_views.flashcard_landing', 
                        language_code=target_language_code, 
                        sourcedir=sourcedir_slug) }}" 
         class="button"
         {% if not has_vocabulary %}disabled title="No vocabulary found"{% endif %}>
          Practice with Flashcards
      </a>
  </div>
  {# ... existing code ... #}
  ```
  - Requires adding `has_vocabulary` context variable in sourcedir view:
    ```python:sourcefile_views.py
    # In sourcedir view function:
    has_vocabulary = any(sf.wordform_entries.count() > 0 for sf in sourcefiles)
    return render_template(..., has_vocabulary=has_vocabulary)
    ```

### Testing Strategy (Priority 3)
- [ ] Add multi-sourcefile test to `test_flashcard_views.py`:
  ```python:tests/test_flashcard_views.py
  def test_sourcedir_multiple_files(client, test_sourcedir_with_files):
      """Test sourcedir with multiple sourcefiles returns combined lemmas"""
      # Add second sourcefile with different lemma
      sf2 = create_sourcefile(
          sourcedir=test_sourcedir_with_files,
          slug='test-file-2',
          wordforms=[create_wordform(lemma_entry=create_lemma(lemma='lemma3'))]
      )
      
      response = client.get(
          f"/{TEST_LANGUAGE_CODE}/flashcards?sourcedir={test_sourcedir_with_files.slug}"
      )
      assert response.status_code == 200
      assert b"lemma1" in response.data
      assert b"lemma2" in response.data 
      assert b"lemma3" in response.data
  ```

### Documentation Updates (Priority 4)
- [ ] Add error case documentation to `FLASHCARDS.md`:
  ```markdown:docs/FLASHCARDS.md
  ## Sourcedir Practice Notes
  
  - Practice button will be disabled if:
    - Directory contains no sourcefiles
    - Sourcefiles have no processed vocabulary
  - Error messages:
    - "Directory not found": Invalid sourcedir slug
    - "No vocabulary found": Valid directory but no words extracted
  ```

### Implementation Checklist
1. Backend first:
   - [ ] Add `get_sourcedir_lemmas` helper function
   - [ ] Update flashcard view error handling
   - [ ] Run `pytest tests/test_flashcard_views.py -k sourcedir`
2. Frontend second:
   - [ ] Update button styling and logic
   - [ ] Add `has_vocabulary` context variable
   - [ ] Manual test with empty/non-empty dirs
3. Documentation last:
   - [ ] Update FLASHCARDS.md
   - [ ] Verify disabled button tooltip appears

## QA Steps
1. Test with sourcedir containing:
   - [ ] Single sourcefile with words
   - [ ] Multiple sourcefiles with words
   - [ ] Sourcefiles with no words
   - [ ] Non-existent sourcedir slug
2. Verify button states:
   - [ ] Enabled with tooltip on hover when active
   - [ ] Disabled with "No vocabulary" tooltip
3. Check error pages:
   - [ ] 404 for invalid slug
   - [ ] 404 for valid slug but no words

## Future Enhancements (Not Now)
- Prioritize sentences with multiple lemmas from sourcedir
- Show progress/stats specific to sourcedir words
- Allow switching between all/sourcedir sentences during practice
